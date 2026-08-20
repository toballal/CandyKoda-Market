import flet as ft
import flet_video as fv
import asyncio
from time import monotonic

from views.tienda import tienda_view
from views.TalkToKoda import koda_view
from views.carrito import carrito_view
from views.pago import pay_view
from views.estado_pago import estado_view
from views.productos import productos_view
from views.ayuda import ayuda_view
from views.mantenimiento import mantenimiento_view
from hardware.arduino import conectar_arduino
from app_state import vaciar_carrito, establecer_configuracion
from database.configuracion_sistema import (
    preparar_configuracion,
    obtener_configuraciones,
    market_en_mantenimiento,
)


def main(page: ft.Page):
    preparar_configuracion()
    page.configuracion_sistema = obtener_configuraciones()
    establecer_configuracion(page.configuracion_sistema)
    page.title = f'{page.configuracion_sistema["nombre_sistema"]} Market'
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed="#9B59FF",
        font_family="Segoe UI",
        visual_density=ft.VisualDensity.COMFORTABLE,
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.FADE_FORWARDS,
            linux=ft.PageTransitionTheme.FADE_FORWARDS,
            macos=ft.PageTransitionTheme.CUPERTINO,
            android=ft.PageTransitionTheme.FADE_UPWARDS,
            ios=ft.PageTransitionTheme.CUPERTINO,
        ),
    )
    page.bgcolor = "#09090F"
    page.window.full_screen = True
    page.padding = 0
    page.spacing = 0
    page.sidebar_colapsado = False
    page.modo_accesible = False
    page.reducir_movimiento = False
    page.ultima_actividad = monotonic()
    page.aviso_inactividad_abierto = False

    page.arduino = conectar_arduino()
    if page.arduino is None:
        print("Arduino no disponible")
    else:
        print("Arduino disponible en toda la aplicación")

    def crear_video_fondo():
        # Se crea una instancia nueva al reconstruir la ruta; Flet destruye
        # los controles multimedia cuando salen del árbol visual.
        return fv.Video(
            playlist=[fv.VideoMedia("Fondo.mp4")],
            autoplay=True,
            muted=True,
            controls=None,
            fit=ft.BoxFit.COVER,
            expand=True,
            playlist_mode=fv.PlaylistMode.LOOP,
        )

    def inicio_con_video():
        vista = tienda_view(page)
        mostrar_video = str(
            page.configuracion_sistema.get("video_fondo", "1")
        ).strip().casefold() in {"1", "true", "si", "sí"}
        if page.reducir_movimiento or not mostrar_video:
            return vista
        contenido = vista.controls[0]
        vista.bgcolor = ft.Colors.TRANSPARENT
        vista.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    crear_video_fondo(),
                    ft.Container(
                        expand=True,
                        bgcolor=ft.Colors.with_opacity(0.48, "#09090F"),
                        content=contenido,
                    ),
                ],
            )
        ]
        return vista

    def registrar_actividad(e=None):
        page.ultima_actividad = monotonic()

    def limpiar_sesion(ir_inicio=True):
        vaciar_carrito()
        page.data = None
        page.pago_en_proceso = False
        page.aviso_inactividad_abierto = False
        page.ultima_actividad = monotonic()
        if ir_inicio:
            page.go("/")

    def proteger_interaccion(vista):
        if not vista.controls:
            return vista
        contenido = vista.controls[0]
        vista.controls = [
            ft.Container(
                expand=True,
                content=ft.GestureDetector(content=contenido, on_tap_down=registrar_actividad),
            )
        ]
        return vista

    def route_change(e):
        page.views.clear()

        page.configuracion_sistema = obtener_configuraciones()
        establecer_configuracion(page.configuracion_sistema)
        nombre_sistema = page.configuracion_sistema["nombre_sistema"]
        page.title = f"{nombre_sistema} Market"
        mantenimiento = market_en_mantenimiento(page.configuracion_sistema)
        if mantenimiento and page.route not in ("/state",):
            page.route = "/mantenimiento"

        if page.route == "/":
            vista = inicio_con_video()

        elif page.route == "/koda":
            vista = koda_view(page)

        elif page.route == "/carrito":
            vista = carrito_view(page)

        elif page.route == "/pay":
            vista = pay_view(page)
        elif page.route == "/state":
            vista = estado_view(page)
        elif page.route == "/productos":
            vista = productos_view(page)

        elif page.route == "/ayuda":
            vista = ayuda_view(page)

        elif page.route == "/mantenimiento":
            vista = mantenimiento_view(page)

        else:
            page.route = "/"
            vista = inicio_con_video()

        page.views.append(proteger_interaccion(vista))

        page.update()


    page.on_route_change = route_change
    page.refrescar_vista_actual = lambda: route_change(None)

    async def controlar_inactividad():
        while True:
            await asyncio.sleep(5)
            if page.route == "/state" or page.aviso_inactividad_abierto:
                continue
            if monotonic() - page.ultima_actividad < 90:
                continue
            if page.route == "/pay":
                page.aviso_inactividad_abierto = True
                def continuar(e):
                    page.pop_dialog()
                    page.aviso_inactividad_abierto = False
                    registrar_actividad()
                def cancelar(e):
                    page.pop_dialog()
                    limpiar_sesion()
                page.show_dialog(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("¿Sigues ahí?"),
                    content=ft.Text("Tu compra está en curso. ¿Deseas continuar?"),
                    actions=[ft.TextButton("Cancelar compra", on_click=cancelar), ft.FilledButton("Continuar", on_click=continuar)],
                    actions_alignment=ft.MainAxisAlignment.END,
                ))
            else:
                limpiar_sesion()

    async def vigilar_mantenimiento():
        configuracion_anterior = None
        while True:
            await asyncio.sleep(3)
            configuracion = await asyncio.to_thread(obtener_configuraciones)
            activo = market_en_mantenimiento(configuracion)
            estado_anterior = (
                market_en_mantenimiento(configuracion_anterior)
                if configuracion_anterior is not None
                else None
            )
            page.configuracion_sistema = configuracion
            establecer_configuracion(configuracion)
            page.title = f'{configuracion["nombre_sistema"]} Market'
            if activo != estado_anterior:
                if activo and page.route not in ("/pay", "/state", "/mantenimiento"):
                    limpiar_sesion(False)
                    page.go("/mantenimiento")
                elif not activo and page.route == "/mantenimiento":
                    page.go("/")
            configuracion_anterior = configuracion

    page.route = "/"
    route_change(None)
    page.run_task(controlar_inactividad)
    page.run_task(vigilar_mantenimiento)



ft.run(
    main,
    assets_dir="assets"
)

"""
=================================
Comprobar db si existe configuracion.
=================================
"""
