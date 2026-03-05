import flet as ft
try:
    img = ft.Image(src="data:image/png;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    print("src base64 data URI exists and works!")
except Exception as e:
    print(f"Error: {e}")
