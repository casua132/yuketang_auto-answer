import flet as ft
import threading
import json
import time
import os
import websocket
import requests
from context import AppContext
from Scripts.Utils import get_config_path, get_config_dir, get_initial_data, get_user_info, dict_result
from Scripts.Monitor import monitor

def main(page: ft.Page):
    page.title = "Rain Classroom Assistant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 400
    page.window_height = 800
    
    # Context setup
    ctx = AppContext(page)
    
    # State
    course_data_rows = []
    log_messages = []
    
    # UI Elements
    log_list_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    
    course_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("课程名")),
            ft.DataColumn(ft.Text("标题")),
            ft.DataColumn(ft.Text("教师")),
            ft.DataColumn(ft.Text("时间")),
        ],
        rows=[]
    )
    
    # Login Dialog Elements
    qr_image = ft.Image(src_base64=None, width=200, height=200)
    login_status_text = ft.Text("")
    
    # Config Dialog Elements
    # (Simplified for now)
    
    def add_log(message, type=0):
        # type is used for audio in original code, ignoring for now or just log it
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        log_messages.append(f"{timestamp}{message}")
        log_list_view.controls.append(ft.Text(f"{timestamp}{message}", size=12, selectable=True))
        page.update()

    def add_course(row, index):
        # row: [lessonname, title, teacher, time_str, lessonid]
        # We store the full row data including ID
        course_data_rows.append(row)
        
        # Display only first 4 columns
        display_row = row[:4]
        
        course_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(r))) for r in display_row
                ],
                data=row[4] if len(row) > 4 else None # Store lessonid in DataRow.data
            )
        )
        ctx.course_count = len(course_table.rows)
        page.update()
        
    def del_course(lessonid):
        # Remove by lessonid
        to_remove_idx = -1
        for i, r in enumerate(course_table.rows):
            if r.data == lessonid:
                to_remove_idx = i
                break
        
        if to_remove_idx != -1:
            course_table.rows.pop(to_remove_idx)
            # Also remove from data rows if we want to keep them synced
            # Finding the data row might be tricky without ID, but we only use it for display
            # We can just ignore course_data_rows sync if it's not used elsewhere.
            # But let's try to keep it clean.
            for i, d in enumerate(course_data_rows):
                 if len(d) > 4 and d[4] == lessonid:
                     course_data_rows.pop(i)
                     break

            ctx.course_count = len(course_table.rows)
            page.update()

    # Wire up context
    ctx.on_message = add_log
    ctx.on_add_course = add_course
    ctx.on_del_course = del_course
    
    # Helper to load config
    def load_config():
        # Try loading from client_storage (Persistent on Android)
        try:
            if page.client_storage.contains_key("config"):
                data = page.client_storage.get("config")
                add_log("配置已从本地存储加载")
                # Merge with default in case of new fields
                default_data = get_initial_data()
                default_data.update(data)
                return default_data
        except Exception as e:
            add_log(f"本地存储读取失败: {e}")

        # Fallback to file-based config (Legacy or Desktop)
        dir_route = get_config_dir()
        config_route = get_config_path()
        
        if not os.path.exists(dir_route):
            try:
                os.makedirs(dir_route)
            except:
                pass
            
        if os.path.exists(config_route):
            try:
                with open(config_route, "r") as f:
                    data = json.load(f)
                add_log("配置文件已读取 (File)")
                return data
            except:
                pass
        
        data = get_initial_data()
        add_log("使用默认配置")
        return data

    def save_config_data(config):
        # Save to client_storage
        try:
            page.client_storage.set("config", config)
        except Exception as e:
            add_log(f"保存配置到本地存储失败: {e}")
            
        # Also save to file as backup
        try:
            dir_route = get_config_dir()
            config_route = get_config_path()
            if not os.path.exists(dir_route):
                os.makedirs(dir_route)
            with open(config_route, "w+") as f:
                json.dump(config, f)
        except Exception:
            pass

    ctx.config = load_config()
    
    # Init env var from config
    if "doubao_api_key" in ctx.config and ctx.config["doubao_api_key"]:
        os.environ["DOUBAO_API_KEY"] = ctx.config["doubao_api_key"]
    
    # Monitor Thread
    monitor_thread = None
    
    # Video control for Wakelock (Keep Screen On)
    # We play a dummy video when monitoring is active to prevent screen sleep
    wakelock_video = ft.Video(
        playlist=[ft.VideoMedia("keep_alive.mp4")],
        playlist_mode=ft.PlaylistMode.LOOP,
        fill_color=ft.Colors.TRANSPARENT,
        aspect_ratio=1,
        volume=0,
        autoplay=False,
        filter_quality=ft.FilterQuality.NONE,
        muted=True,
        wakelock=True,
        pause_upon_entering_background_mode=False,
        width=1,
        height=1,
        visible=False # Initially invisible, though visibility might affect playing on some platforms
    )
    # Note: Flet Video might need to be visible to play? 
    # Usually visibility=False stops rendering.
    # We'll set opacity to 0 instead of visible=False if needed, but let's try visible first.
    # Actually, let's keep it visible but tiny.
    wakelock_video.visible = True
    wakelock_video.opacity = 0.01 # Non-zero opacity to ensure it's "visible" to the system

    # Audio control for better backgrounding support
    wakelock_audio = ft.Audio(
        src="keep_alive.mp4", # Reuse the video file as audio source if it contains audio track, or just as a placeholder
        autoplay=False,
        volume=0,
        balance=0,
        release_mode=ft.AudioReleaseMode.LOOP,
    )
    page.overlay.append(wakelock_audio)

    def toggle_active(e):
        if ctx.is_active:
            # Stop
            ctx.is_active = False
            active_btn.text = "启动"
            active_btn.disabled = False # In original it disables then enables. 
            wakelock_video.pause()
            wakelock_audio.pause()
            add_log("停止监听")
        else:
            # Start
            ctx.is_active = True
            active_btn.text = "停止监听"
            monitor_thread = threading.Thread(target=monitor, args=(ctx,), daemon=True)
            monitor_thread.start()
            wakelock_video.play()
            wakelock_audio.play()
            add_log("启动监听 (已启用屏幕常亮)")
        page.update()

    active_btn = ft.ElevatedButton("启动", on_click=toggle_active)
    
    # Login Logic
    def show_login_dialog(e=None):
        qr_image.src_base64 = ""
        login_status_text.value = "正在获取二维码..."
        
        def close_login(e):
            login_dialog.open = False
            page.update()
            # Stop any running login threads if needed
            
        login_dialog = ft.AlertDialog(
            title=ft.Text("微信扫码登录"),
            content=ft.Column([
                qr_image,
                login_status_text
            ], tight=True, alignment=ft.MainAxisAlignment.CENTER),
            actions=[
                ft.TextButton("取消", on_click=close_login)
            ]
        )
        page.overlay.append(login_dialog)
        login_dialog.open = True
        page.update()
        
        # Start Login Thread
        threading.Thread(target=login_process, args=(login_dialog,), daemon=True).start()

    def login_process(dialog):
        # Websocket for Login
        login_wss_url = "wss://www.yuketang.cn/wsapp/"
        ws_app = None
        
        def on_open(ws):
            data={"op":"requestlogin","role":"web","version":1.4,"type":"qrcode","from":"web"}
            ws.send(json.dumps(data))
            
        def on_message(ws, message):
            data = dict_result(message)
            if data["op"] == "requestlogin":
                # Get QR Code image
                try:
                    import base64
                    img_resp = requests.get(url=data["ticket"], proxies={"http": None,"https":None})
                    b64_img = base64.b64encode(img_resp.content).decode('utf-8')
                    qr_image.src_base64 = b64_img
                    login_status_text.value = "请扫码"
                    page.update()
                except Exception as ex:
                    print(ex)
            elif data["op"] == "loginsuccess":
                # Login Success
                login_status_text.value = "扫码成功，正在登录..."
                page.update()
                
                web_login_url = "https://www.yuketang.cn/pc/web_login"
                login_data = {
                    "UserID":data["UserID"],
                    "Auth":data["Auth"]
                }
                headers = {
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
                }
                try:
                    r = requests.post(url=web_login_url, data=json.dumps(login_data), headers=headers, proxies={"http": None,"https":None})
                    sessionid = dict(r.cookies)["sessionid"]
                    ctx.config["sessionid"] = sessionid
                    
                    # Save config
                    save_config_data(ctx.config)
                        
                    login_status_text.value = "登录成功！"
                    page.update()
                    time.sleep(1)
                    dialog.open = False
                    page.update()
                    ws.close()
                    
                    # Refresh User Info
                    check_login_status()
                    
                except Exception as e:
                    login_status_text.value = f"登录失败: {e}"
                    page.update()

        ws_app = websocket.WebSocketApp(url=login_wss_url, on_open=on_open, on_message=on_message)
        ws_app.run_forever()

    def check_login_status():
        if "sessionid" in ctx.config and ctx.config["sessionid"]:
            code, user_info = get_user_info(ctx.config["sessionid"])
            if code == 0:
                login_btn.text = f"已登录: {user_info['name']}"
                add_log(f"登录成功，当前用户: {user_info['name']}")
                return True
            else:
                login_btn.text = "登录"
                return False
        else:
            login_btn.text = "登录"
            return False

    login_btn = ft.ElevatedButton("登录", on_click=show_login_dialog)
    
    # Config Dialog
    def show_config_dialog(e):
        
        def save_config(e):
            ctx.config["auto_danmu"] = cb_auto_danmu.value
            ctx.config["auto_answer"] = cb_auto_answer.value
            ctx.config["audio_on"] = cb_audio_on.value
            ctx.config["doubao_api_key"] = tb_api_key.value
            
            # Update env var for immediate use
            if tb_api_key.value:
                os.environ["DOUBAO_API_KEY"] = tb_api_key.value
            
            save_config_data(ctx.config)
            
            config_dialog.open = False
            page.update()
            add_log("配置已保存")

        def close_config(e):
            config_dialog.open = False
            page.update()

        cb_auto_danmu = ft.Checkbox(label="自动发弹幕", value=ctx.config.get("auto_danmu", True))
        cb_auto_answer = ft.Checkbox(label="自动答题", value=ctx.config.get("auto_answer", True))
        cb_audio_on = ft.Checkbox(label="语音提醒 (暂不可用)", value=ctx.config.get("audio_on", True))
        
        tb_api_key = ft.TextField(label="Doubao API Key", value=ctx.config.get("doubao_api_key", ""), password=True, can_reveal_password=True)
        
        config_dialog = ft.AlertDialog(
            title=ft.Text("配置"),
            content=ft.Column([
                cb_auto_danmu,
                cb_auto_answer,
                cb_audio_on,
                tb_api_key,
                ft.Text("更多配置请直接修改 config.json", size=10, color=ft.Colors.GREY)
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=close_config),
                ft.TextButton("保存", on_click=save_config)
            ]
        )
        page.overlay.append(config_dialog)
        config_dialog.open = True
        page.update()

    config_btn = ft.ElevatedButton("配置", on_click=show_config_dialog)

    # Layout
    header = ft.Row(
        [
            ft.Text("摸鱼课堂 Mobile", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            active_btn,
            login_btn,
            config_btn
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Text("⚠️ 注意：本应用将在运行时保持屏幕常亮。", size=12, color=ft.Colors.BLUE),
                    ft.Text("监听列表:", size=16),
                    ft.Container(
                        content=course_table,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        height=200,
                        # scroll=ft.ScrollMode.ADAPTIVE
                    ),
                    ft.Text("信息:", size=16),
                    ft.Container(
                        content=log_list_view,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        expand=True,
                        padding=5,
                        bgcolor=ft.Colors.GREY_100
                    ),
                    wakelock_video
                ]
            ),
            padding=10,
            expand=True
        )
    )

    # Check login on start
    try:
        check_login_status()
    except Exception as e:
        add_log(f"登录状态检查失败: {e}")
        
    add_log("初始化完成")

ft.app(target=main, assets_dir="assets")
