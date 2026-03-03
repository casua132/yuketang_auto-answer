import flet as ft
def main(page: ft.Page):
    try:
        page.scroll = ft.ScrollMode.ADAPTIVE
        page.add(
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Text("Hello"), ft.ElevatedButton("Btn")], scroll=ft.ScrollMode.ADAPTIVE),
                            ft.Text("Log:"),
                            ft.Container(
                                content=ft.ListView(spacing=10, auto_scroll=True),
                                height=400,
                                bgcolor=ft.Colors.GREY_100
                            )
                        ]
                    ),
                    padding=10
                )
            )
        )
        print("Success rendering layout")
    except Exception as e:
        page.add(ft.Text(f"CRASH: {e}", color=ft.Colors.RED))
ft.app(main)
