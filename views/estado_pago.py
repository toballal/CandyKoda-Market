import asyncio
from queue import Queue, Empty
import flet as ft

from app_state import vaciar_carrito
from components.theme import (
    FONDO,
    CARD,
    BORDE,
    MORADO,
    ROSA,
    VERDE,
    AMARILLO,
    ROJO,
    TEXTO,
    TEXTO_2,
)
from database.devoluciones import devolver_productos_no_entregados
from database.entregas import marcar_error
from services.procesar_entrega import procesar_entrega
from components.formatos import formato_precio


def _precio(valor):
    return formato_precio(valor)


def estado_view(page: ft.Page):

    resultado = page.data if isinstance(page.data, dict) else {}
    pago_aprobado = bool(resultado.get("exito"))
    color = MORADO if pago_aprobado else ROJO

    icono = ft.Icon(
        ft.Icons.SYNC_ROUNDED if pago_aprobado else ft.Icons.CLOSE_ROUNDED,
        size=74,
        color=color,
    )

    titulo = ft.Text(
        "Preparando tu pedido" if pago_aprobado else "Pago rechazado",
        size=34,
        color=TEXTO,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    descripcion = ft.Text(
        "Pago aprobado. Iniciaremos la entrega."
        if pago_aprobado
        else resultado.get(
            "mensaje",
            "No se pudo completar la operación.",
        ),
        size=16,
        color=TEXTO_2,
        text_align=ft.TextAlign.CENTER,
    )

    fase = ft.Text(
        "Procesando pago → Preparando pedido",
        size=14,
        color=MORADO,
        weight=ft.FontWeight.BOLD,
    )

    progreso = ft.ProgressBar(
        value=0.20 if pago_aprobado else 0,
        width=500,
        color=MORADO,
        bgcolor="#292938",
        border_radius=8,
    )

    detalle_entrega = ft.Text(
        "",
        size=13,
        color=TEXTO_2,
        text_align=ft.TextAlign.CENTER,
    )

    devolucion = ft.Container(
        visible=False,
        width=520,
        padding=18,
        border_radius=15,
        bgcolor="#18291F",
        border=ft.Border.all(1, "#315D40"),
    )

    boton = ft.FilledButton(
        "Volver al inicio",
        icon=ft.Icons.HOME_ROUNDED,
        width=500,
        height=54,
        bgcolor=MORADO,
        color="#FFFFFF",
        disabled=pago_aprobado,
        on_click=lambda e: finalizar(),
    )

    cuenta = ft.Text(
        "",
        size=11,
        color="#777788",
    )

    def finalizar():
        page.data = None
        page.pago_en_proceso = False
        page.go("/")

    items = resultado.get("entregas", [])

    resumen_items = ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"{item['cantidad']}× {item['producto']}",
                        color=TEXTO_2,
                        size=13,
                    ),
                    ft.Icon(
                        ft.Icons.SCHEDULE_ROUNDED,
                        color=MORADO,
                        size=17,
                    ),
                ],
            )
            for item in items
        ],
    )

    async def volver_automaticamente(segundos):

        for restante in range(segundos, 0, -1):

            if page.route != "/state":
                return

            cuenta.value = (
                f"La sesión se cerrará en {restante} segundos."
            )

            try:
                page.update()
            except Exception:
                return

            await asyncio.sleep(1)

        if page.route == "/state":
            finalizar()

    async def ejecutar_entrega():

        vaciar_carrito()
        eventos = Queue()

        def reportar(indice, total, producto, estado):
            eventos.put(
                (
                    indice,
                    total,
                    producto,
                    estado,
                )
            )

        if getattr(page, "arduino", None) is None:

            for entrega in items:

                marcar_error(
                    entrega["id_entrega"],
                    entrega["id_detalle"],
                    resultado["id_venta"],
                    "Arduino no conectado",
                )

            exitoso = False

        else:

            tarea = asyncio.create_task(
                asyncio.to_thread(
                    procesar_entrega,
                    page.arduino,
                    items,
                    resultado["id_venta"],
                    reportar,
                )
            )

            while not tarea.done():

                try:

                    while True:

                        indice, total, producto, estado = (
                            eventos.get_nowait()
                        )

                        fase.value = (
                            f"Entregando {indice} de {total}"
                        )

                        detalle_entrega.value = (
                            f"{producto}: {estado}"
                        )

                        progreso.value = (
                            0.35
                            + (
                                0.55
                                * (
                                    (
                                        indice
                                        - (
                                            0
                                            if estado == "Completada"
                                            else 0.5
                                        )
                                    )
                                    / total
                                )
                            )
                        )

                except Empty:
                    pass

                page.update()
                await asyncio.sleep(0.10)

            exitoso = await tarea

        resultado["entrega_enviada"] = True
        resultado["entrega_exitosa"] = bool(exitoso)

        boton.disabled = False

        if exitoso:

            icono.icon = ft.Icons.CHECK_CIRCLE_ROUNDED
            icono.color = VERDE

            titulo.value = "¡Compra completada!"

            descripcion.value = (
                "El pago y la entrega se realizaron correctamente. "
                "Retira tus productos."
            )

            fase.value = (
                "Procesando pago → Preparando pedido → Entregado"
            )

            fase.color = VERDE
            progreso.value = 1
            progreso.color = VERDE

            detalle_entrega.value = (
                "Todos los productos fueron confirmados por el dispensador."
            )

            boton.bgcolor = VERDE

            page.update()

            page.run_task(
                volver_automaticamente,
                15,
            )

            return

        icono.icon = ft.Icons.WARNING_AMBER_ROUNDED
        icono.color = AMARILLO

        titulo.value = "Entrega no completada"

        descripcion.value = (
            "No vuelvas a pagar. Estamos devolviendo el importe "
            "de los productos no entregados."
        )

        fase.value = (
            "Pago aprobado → Entrega fallida → Procesando devolución"
        )

        fase.color = AMARILLO
        progreso.value = 0.85
        progreso.color = AMARILLO

        detalle_entrega.value = (
            f"Incidente registrado en la venta "
            f"#{resultado.get('id_venta', '-')}"
        )

        page.update()

        reembolso = await asyncio.to_thread(
            devolver_productos_no_entregados,
            resultado["id_venta"],
        )

        if reembolso.get("exito"):

            monto = reembolso["monto"]

            resultado["monto_devuelto"] = monto

            resultado["saldo_restante"] = reembolso.get(
                "saldo_nuevo",
                resultado.get("saldo_restante", 0),
            )

            descripcion.value = (
                "La entrega falló, pero el dinero de los productos "
                "no entregados ya fue devuelto a tu tarjeta."
            )

            fase.value = (
                "Pago aprobado → Entrega fallida → "
                "Devolución completada"
            )

            progreso.value = 1
            devolucion.visible = True

            devolucion.content = ft.Row(
                spacing=14,
                controls=[
                    ft.Icon(
                        ft.Icons.REPLAY_CIRCLE_FILLED_ROUNDED,
                        color=VERDE,
                        size=30,
                    ),

                    ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(
                                "Devolución automática completada",
                                color=TEXTO,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Text(
                                f"Monto devuelto: "
                                f"{_precio(monto)} · "
                                f"Saldo actual: "
                                f"{_precio(resultado['saldo_restante'])}",
                                color=VERDE,
                            ),
                        ],
                    ),
                ],
            )

        else:

            descripcion.value = (
                "La entrega falló y la devolución requiere revisión. "
                "Solicita asistencia y conserva el número de venta."
            )

            fase.value = "Atención manual requerida"

            devolucion.visible = True
            devolucion.bgcolor = "#2A171B"
            devolucion.border = ft.Border.all(
                1,
                "#6A303B",
            )

            devolucion.content = ft.Row(
                spacing=14,
                controls=[
                    ft.Icon(
                        ft.Icons.SUPPORT_AGENT_ROUNDED,
                        color=ROJO,
                        size=30,
                    ),

                    ft.Text(
                        "Solicita asistencia. No realices un nuevo pago.",
                        color=TEXTO,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            )

        page.update()

        page.run_task(
            volver_automaticamente,
            30,
        )

    tarjeta = ft.Container(
        width=520,
        padding=22,
        bgcolor=CARD,
        border=ft.Border.all(1, BORDE),
        border_radius=18,
        content=ft.Column(
            spacing=13,
            controls=[

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "N.º de venta",
                            color=TEXTO_2,
                        ),

                        ft.Text(
                            f"#{resultado.get('id_venta', '-')}",
                            color=TEXTO,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),

                resumen_items,

                ft.Divider(
                    color=BORDE,
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Total pagado",
                            color=TEXTO_2,
                        ),

                        ft.Text(
                            _precio(resultado.get("total", 0)),
                            color=ROSA,
                            size=21,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            ],
        ),
    )

    contenido = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=18,
        controls=[

            ft.Image(
                src="LogoCandyKodaSimplify.svg",
                width=230,
            ),

            ft.Container(
                width=130,
                height=130,
                border_radius=65,
                bgcolor=ft.Colors.with_opacity(
                    0.12,
                    color,
                ),
                border=ft.Border.all(
                    3,
                    color,
                ),
                alignment=ft.Alignment.CENTER,
                content=icono,
            ),

            titulo,
            descripcion,
            fase,
            progreso,
            detalle_entrega,

            tarjeta if pago_aprobado else ft.Container(),

            devolucion,
            boton,
            cuenta,
        ],
    )

    if pago_aprobado:

        page.run_task(
            ejecutar_entrega
        )

    else:

        boton.disabled = False

        page.run_task(
            volver_automaticamente,
            15,
        )

    return ft.View(
        route="/state",
        padding=0,
        spacing=0,
        bgcolor=FONDO,
        controls=[
            ft.Container(
                expand=True,
                padding=28,
                bgcolor=FONDO,
                content=contenido,
            )
        ],
    )
