import flet as ft
print("Has ButtonVariant:", hasattr(ft, "ButtonVariant"))
print("Has Button:", hasattr(ft, "Button"))
print("Has ElevatedButton:", hasattr(ft, "ElevatedButton"))
print("Has alignment.center:", hasattr(ft.alignment, "center"))
print("Has alignment.CENTER:", hasattr(ft.alignment, "CENTER"))
print("Has Alignment:", hasattr(ft, "Alignment"))
if hasattr(ft, "Alignment"):
    print("Has Alignment.center:", hasattr(ft.Alignment, "center"))
    print("Has Alignment.CENTER:", hasattr(ft.Alignment, "CENTER"))
