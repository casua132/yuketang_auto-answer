import flet as ft
try:
    print("Testing border...")
    b = ft.border.all(1, ft.Colors.GREY_300)
    print("Border OK")
except Exception as e:
    print("Border FAIL:", e)

try:
    print("Testing text weight...")
    t = ft.Text("Hello", weight=ft.FontWeight.BOLD)
    print("Text Weight OK")
except Exception as e:
    print("Text FAIL:", e)
