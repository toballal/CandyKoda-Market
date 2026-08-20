import asyncio
from datetime import datetime
import flet as ft

from app_state import cantidad_productos
from components.theme import BORDE, CARD, FONDO, MORADO, ROSA, TEXTO, TEXTO_2, VERDE, AMARILLO, ROJO
from database.connection import verificar_conexion


def menu_lateral(page: ft.Page, ruta_activa: str):
    colapsado = bool(getattr(page, "sidebar_colapsado", False))
    db_ok = verificar_conexion()
    arduino = getattr(page, "arduino", None)
    arduino_ok = bool(arduino is not None and getattr(arduino, "is_open", False))
    if db_ok and arduino_ok:
        sistema, color_sistema = "Sistema operativo", VERDE
    elif db_ok:
        sistema, color_sistema = "Modo limitado", AMARILLO
    else:
        sistema, color_sistema = "Sin conexión", ROJO

    hora = ft.Text("--:--", size=22, weight=ft.FontWeight.BOLD, color=TEXTO)
    fecha = ft.Text("", size=11, color=TEXTO_2)

    async def reloj():
        while True:
            ahora = datetime.now()
            hora.value, fecha.value = ahora.strftime("%H:%M"), ahora.strftime("%d %b %Y")
            try:
                hora.update(); fecha.update()
            except Exception:
                return
            await asyncio.sleep(30)

    def alternar(e):
        page.sidebar_colapsado = not colapsado
        page.refrescar_vista_actual()

    def alternar_accesibilidad(e):
        page.modo_accesible = not getattr(page, "modo_accesible", False)
        page.refrescar_vista_actual()

    def alternar_movimiento(e):
        page.reducir_movimiento = not getattr(page, "reducir_movimiento", False)
        page.refrescar_vista_actual()

    alto_opcion = 56 if getattr(page, "modo_accesible", False) else 48
    texto_opcion = 15 if getattr(page, "modo_accesible", False) else 13

    def opcion(icono, texto, ruta, contador=0):
        activo = ruta_activa == ruta
        def hover(e):
            if not activo:
                e.control.bgcolor = ft.Colors.with_opacity(0.08, MORADO) if e.data == "true" else ft.Colors.TRANSPARENT
                e.control.update()
        return ft.Container(
            height=alto_opcion, padding=ft.Padding(left=10, right=10, top=6, bottom=6),
            gradient=ft.LinearGradient(colors=[ft.Colors.with_opacity(0.20, MORADO), ft.Colors.with_opacity(0.08, ROSA)]) if activo else None,
            border=ft.Border(left=ft.BorderSide(3, MORADO if activo else ft.Colors.TRANSPARENT)), border_radius=12,
            ink=True, tooltip=texto if colapsado else None, on_hover=hover, on_click=lambda e: page.go(ruta),
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=12, controls=[
                    ft.Container(width=32, height=32, border_radius=9, bgcolor=ft.Colors.with_opacity(0.14, MORADO) if activo else "#1D1D29", alignment=ft.Alignment.CENTER, content=ft.Icon(icono, size=18, color=MORADO if activo else "#B9B9C9")),
                    ft.Text(texto, size=texto_opcion, color=TEXTO if activo else "#C7C7D4", weight=ft.FontWeight.BOLD if activo else ft.FontWeight.W_500) if not colapsado else ft.Container(),
                ]),
                ft.Container(width=24, height=24, border_radius=12, bgcolor=ROSA, alignment=ft.Alignment.CENTER, content=ft.Text(str(contador), size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD)) if contador and not colapsado else ft.Container(),
            ]),
        )

    page.run_task(reloj)
    return ft.Container(
        width=92 if colapsado else 268, animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
        padding=ft.Padding(left=15, right=15, top=18, bottom=16),
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER, colors=["#141421", FONDO]),
        border=ft.Border(right=ft.BorderSide(1, BORDE)),
        content=ft.Column(expand=True, controls=[
            ft.Container(padding=10, bgcolor=CARD, border=ft.Border.all(1, BORDE), border_radius=15, content=ft.Row(spacing=10, controls=[
                ft.Image(src="LogoCandyKodaVerySimple.svg", width=38, height=38),
                ft.Column(spacing=0, controls=[ft.Text("Candy Koda", size=16, color=TEXTO, weight=ft.FontWeight.BOLD), ft.Text("MARKET", size=10, color=ROSA, weight=ft.FontWeight.BOLD)]) if not colapsado else ft.Container(),
            ])),
            ft.Container(alignment=ft.Alignment.CENTER_RIGHT, content=ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT_ROUNDED if colapsado else ft.Icons.CHEVRON_LEFT_ROUNDED, icon_color=MORADO, tooltip="Expandir menú" if colapsado else "Contraer menú", on_click=alternar)),
            opcion(ft.Icons.STOREFRONT_ROUNDED, "Tienda", "/"),
            opcion(ft.Icons.COOKIE_ROUNDED, "Productos", "/productos"),
            opcion(ft.Icons.AUTO_AWESOME_ROUNDED, "Hablar con Koda", "/koda"),
            opcion(ft.Icons.SHOPPING_BAG_ROUNDED, "Mi carrito", "/carrito", cantidad_productos()),
            opcion(ft.Icons.HELP_CENTER_ROUNDED, "Ayuda", "/ayuda"),
            ft.Container(expand=True),
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=3, controls=[
                ft.IconButton(icon=ft.Icons.ACCESSIBILITY_NEW_ROUNDED, icon_color=MORADO if getattr(page, "modo_accesible", False) else TEXTO_2, tooltip="Alternar controles grandes", on_click=alternar_accesibilidad),
                ft.IconButton(icon=ft.Icons.MOTION_PHOTOS_OFF_ROUNDED, icon_color=MORADO if getattr(page, "reducir_movimiento", False) else TEXTO_2, tooltip="Reducir animaciones", on_click=alternar_movimiento),
            ]),
            ft.Container(padding=12, bgcolor=CARD, border=ft.Border.all(1, BORDE), border_radius=14, content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, controls=[
                hora, fecha if not colapsado else ft.Container(), ft.Divider(color=BORDE, height=8),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=7, controls=[ft.Container(width=8, height=8, border_radius=4, bgcolor=color_sistema), ft.Text(sistema, size=10, color=TEXTO_2) if not colapsado else ft.Container()]),
            ])),
        ]),
    )
