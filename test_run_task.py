import flet as ft
import threading
import time
import asyncio

def main(page: ft.Page):
    text = ft.Text("Initial")
    page.add(text)

    def background_thread():
        time.sleep(2)

        async def update_ui():
            text.value = "Updated from background thread!"
            text.update()

        page.run_task(update_ui)

    threading.Thread(target=background_thread).start()

if __name__ == "__main__":
    ft.app(target=main)
