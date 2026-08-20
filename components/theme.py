import flet as ft

FONDO = "#09090F"
SUPERFICIE = "#11111B"
CARD = "#161622"
CARD_ELEVADA = "#1B1B29"
BORDE = "#2A2A3A"
MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#57D68D"
AMARILLO = "#FFC857"
ROJO = "#FF647C"
TEXTO = "#F7F7FB"
TEXTO_2 = "#A7A7B8"

def encabezado(titulo, subtitulo, icono, acciones=None):
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        ft.Row(spacing=15, controls=[
            ft.Container(width=52, height=52, border_radius=15, gradient=ft.LinearGradient(colors=[MORADO, ROSA]), alignment=ft.Alignment.CENTER, content=ft.Icon(icono, color="#FFFFFF", size=27), shadow=ft.BoxShadow(blur_radius=18, color="#449B59FF")),
            ft.Column(spacing=2, controls=[ft.Text(titulo, size=30, weight=ft.FontWeight.BOLD, color=TEXTO), ft.Text(subtitulo, size=13, color=TEXTO_2)]),
        ]),
        ft.Row(spacing=10, controls=acciones or []),
    ])

def badge(texto, color=MORADO, icono=None):
    controles = ([ft.Icon(icono, size=14, color=color)] if icono else []) + [ft.Text(texto, size=11, color=color, weight=ft.FontWeight.BOLD)]
    return ft.Container(padding=ft.Padding.symmetric(horizontal=10, vertical=6), bgcolor=ft.Colors.with_opacity(0.12, color), border=ft.Border.all(1, ft.Colors.with_opacity(0.35, color)), border_radius=20, content=ft.Row(tight=True, spacing=6, controls=controles))

def panel(content, padding=20, expand=False):
    return ft.Container(expand=expand, padding=padding, bgcolor=CARD, border=ft.Border.all(1, BORDE), border_radius=18, shadow=ft.BoxShadow(blur_radius=20, color="#26000000", offset=ft.Offset(0, 7)), content=content)
