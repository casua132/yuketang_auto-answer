import flet as ft
import flet_audio as ft_audio
import flet_video as ft_video

def main(page: ft.Page):
    try:
        page.window_width = 400
        print("window_width OK")
    except Exception as e:
        print("window_width ERROR:", e)

    try:
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Col"))],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("Cell"))], data="hello")]
        )
        print("DataTable OK")
    except Exception as e:
        print("DataTable ERROR:", e)

    try:
        video = ft_video.Video(
            playlist=[ft_video.VideoMedia("keep_alive.mp4")],
            playlist_mode=ft_video.PlaylistMode.LOOP,
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
            visible=True
        )
        print("Video OK")
    except Exception as e:
        print("Video ERROR:", e)

    try:
        dialog = ft.AlertDialog(
            title=ft.Text("Login"),
            content=ft.Column([ft.Text("Hello")], tight=True, alignment=ft.MainAxisAlignment.CENTER),
            actions=[ft.TextButton("Close")]
        )
        print("AlertDialog OK")
    except Exception as e:
        print("AlertDialog ERROR:", e)

ft.app(main)
