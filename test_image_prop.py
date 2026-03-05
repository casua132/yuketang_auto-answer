import flet as ft
try:
    img = ft.Image(src_base64="R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    print("src_base64 exists and works!")
except Exception as e:
    print(f"Error: {e}")
