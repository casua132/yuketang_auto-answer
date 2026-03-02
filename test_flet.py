import flet as ft
def main(page: ft.Page):
    header = ft.Row(
        [
            ft.Text("摸鱼课堂 Mobile", size=20, weight=ft.FontWeight.BOLD),
            # NO MORE ft.Container(expand=True) here!
            ft.ElevatedButton("启动"),
            ft.ElevatedButton("登录"),
            ft.ElevatedButton("配置")
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True
    )

    # We also check the Safe Area + Column expands correctly
    # with similar hierarchy from main.py
    page.add(
        ft.SafeArea(
            ft.Container(
                content=ft.Column(
                    [
                        header,
                        ft.Container(
                            content=ft.ListView(expand=True, auto_scroll=True),
                            expand=True,
                            bgcolor=ft.Colors.GREY_100
                        )
                    ],
                    expand=True
                ),
                expand=True
            ),
            expand=True
        )
    )

ft.app(target=main)
