import flet as ft
import time
import threading

def main(page: ft.Page):
    # Base64 for a transparent pixel
    TRANSPARENT_PIXEL_B64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

    # Base64 for a small red dot
    RED_DOT_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

    # We initialize the image with src set, like in main.py
    # qr_image = ft.Image(src=f"data:image/png;base64,{TRANSPARENT_PIXEL_B64}", width=200, height=200)

    # Let's test using only src_base64
    qr_image = ft.Image(src_base64=TRANSPARENT_PIXEL_B64, width=200, height=200)

    page.add(qr_image)

    def background_update():
        time.sleep(2)
        async def _update():
            # If we were using src before, we'd clear it:
            qr_image.src = None
            qr_image.src_base64 = RED_DOT_B64
            qr_image.key = str(time.time())
            qr_image.update()
        page.run_task(_update)

    threading.Thread(target=background_update).start()

ft.app(main)