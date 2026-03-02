import flet as ft
def main(page: ft.Page):
    # Try it WITHOUT expand=True on SafeArea.
    header = ft.Row(
        [
            ft.Text("摸鱼课堂 Mobile", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("启动"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True
    )

    main_layout = ft.Column(
        [
            header,
            ft.Text("信息:", size=16),
            ft.Container(
                content=ft.ListView(expand=True, auto_scroll=True),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=5,
                expand=True, # Allow container to expand
            )
        ],
        expand=True # Allow column to expand
    )

    # Do not set expand=True on SafeArea, it might be causing the white screen
    # by trying to force infinite layout inside the flutter engine bounds on Android.
    page.add(
        ft.SafeArea(
            ft.Container(
                content=main_layout,
                padding=10,
                expand=True # Allow padding container to expand
            )
        )
    )

ft.app(target=main)
