import asyncio
import flet as ft
from app_state import (
    obtener_carrito,
    calcular_total,
    cantidad_productos,
)

from hardware.lector_nfc import leer_tarjeta
from database.tarjetas import existe_tarjeta
from services.procesar_pago import procesar_pago
from components.formatos import formato_precio as _formato_precio

def formato_precio(valor):
    return _formato_precio(valor)

def crear_productos_resumen():
    productos = []

    for item in obtener_carrito():
        subtotal_producto = item["cantidad"] * item["precio"]

        productos.append(
            producto_resumen(
                nombre=item["producto"],
                cantidad=item["cantidad"],
                precio=subtotal_producto,
            )
        )

    if not productos:
        productos.append(
            ft.Container(
                padding=20,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    "No hay productos en el carrito",
                    color="#999999",
                ),
            )
        )

    return productos


def producto_resumen(nombre, cantidad, precio):
    return ft.Container(
        padding=12,
        border_radius=12,
        bgcolor="#1A1A1A",
        border=ft.Border.all(1, "#2D2D2D"),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=3,
                    controls=[
                        ft.Text(
                            nombre,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            f"Cantidad: {cantidad}",
                            size=13,
                            color="#9E9E9E",
                        ),
                    ],
                ),
                ft.Text(
                    formato_precio(precio),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
            ],
        ),
    )


def pay_view(page: ft.Page):
    page.pago_en_proceso = False

    async def esperar_tarjeta():

        print("Tarea NFC iniciada")

        while page.route == "/pay":

            arduino = getattr(page, "arduino", None)

            uid = leer_tarjeta(arduino)

            if uid is not None:
                registrada = existe_tarjeta(uid)

                if registrada:
                    print("Mostrando pantalla PIN")

                    contenido.content = pantalla_pin(uid)
                    contenido.update()

                    break

                else:
                    print("Tarjeta NO registrada")

                    texto_estado.value = "Tarjeta no registrada"
                    texto_estado.color = "#FF5C5C"

                    texto_instruccion.value = (
                        "Utiliza una tarjeta Candy Koda registrada"
                    )

                    page.update()

            await asyncio.sleep(0.1)

    def pantalla_pin(uid):

        pin = ft.TextField(
            password=True,
            max_length=4,
            width=300,
            text_align=ft.TextAlign.CENTER,
            text_size=22,
            border_color="#39394A",
            focused_border_color="#9B59FF",
            bgcolor="#14141F",
            border_radius=12,
            hint_text="••••",
        )

        def confirmar_pin(e):
            if getattr(page, "pago_en_proceso", False):
                return

            if len(pin.value) != 4:
                error_pin.value = "Ingresa los 4 dígitos"
                page.update()
                return

            if not pin.value.isdigit():
                error_pin.value = "El PIN solo puede contener números"
                page.update()
                return

            page.pago_en_proceso = True
            boton_confirmar.disabled = True
            boton_confirmar.content = "Procesando..."
            pin.disabled = True
            page.update()

            try:
                resultado = procesar_pago(uid, pin.value)
            finally:
                pin.value = ""

            if not resultado["exito"]:
                error_pin.value = resultado["mensaje"]
                error_pin.visible = True
                page.pago_en_proceso = False
                boton_confirmar.disabled = False
                boton_confirmar.content = "Confirmar pago"
                pin.disabled = False
                page.update()
                return

            # PIN CORRECTO
            error_pin.value = ""
            error_pin.visible = False

            page.data = resultado
            page.go("/state")


        error_pin = ft.Text(
            "",
            color="#FF5C5C",
            size=13,
        )

        boton_confirmar = ft.FilledButton(
            "Confirmar pago",
            icon=ft.Icons.PAYMENT,
            width=300,
            height=50,
            bgcolor="#9B59FF",
            color="#FFFFFF",
            on_click=confirmar_pin,
        )

        return ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,

            controls=[

                ft.Container(
                    width=90,
                    height=90,
                    border_radius=45,
                    bgcolor="#211629",
                    alignment=ft.Alignment.CENTER,

                    content=ft.Icon(
                        ft.Icons.LOCK_OUTLINE,
                        size=45,
                        color="#9B59FF",
                    ),
                ),

                ft.Text(
                    "Tarjeta detectada",
                    size=18,
                    color="#65D892",
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Ingresa tu PIN",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),

                ft.Text(
                    "Ingresa los 4 dígitos de tu tarjeta Candy Koda",
                    size=14,
                    color="#A5A5A5",
                ),

                pin,

                error_pin,

                boton_confirmar,

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.go("/carrito")
                ),
            ],
        )

    subtotal = calcular_total()
    descuento = 0
    total = subtotal - descuento
    cantidad = cantidad_productos()

    productos_carrito = crear_productos_resumen()

    texto_estado = ft.Text(
        "Esperando tarjeta...",
        size=16,
        weight=ft.FontWeight.BOLD,
        color="#9B59FF",
    )

    texto_instruccion = ft.Text(
        "Acerca tu tarjeta para continuar",
        size=14,
        color="#AFAFAF",
        text_align=ft.TextAlign.CENTER,
    )

    anillo_espera = ft.Stack(
        width=130,
        height=130,
        controls=[
            ft.ProgressRing(
                width=130,
                height=130,
                stroke_width=7,
                color="#9B59FF",
            ),
            ft.Container(
                width=130,
                height=130,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(
                    width=95,
                    height=95,
                    border_radius=50,
                    bgcolor="#17121F",
                    border=ft.Border.all(1, "#43255F"),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.CONTACTLESS_OUTLINED,
                        size=48,
                        color="#FFFFFF",
                    ),
                ),
            ),
        ],
    )

    contenido = ft.Container(
        expand=2,
        padding=40,
        bgcolor="#0D0D14",
        content=ft.Column(
            spacing=22,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color="#FFFFFF",
                            bgcolor="#1E1E1E",
                            tooltip="Volver al carrito",
                            on_click=lambda e: page.go("/carrito"),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Pago",
                                    size=38,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "Finaliza tu compra con tu tarjeta Candy Koda",
                                    size=15,
                                    color="#A5A5A5",
                                ),
                            ],
                        ),
                    ],
                ),

                ft.Container(
                    padding=20,
                    border_radius=16,
                    bgcolor="#211629",
                    border=ft.Border.all(1, "#5D2F7A"),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=12,
                                bgcolor="#362044",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.INFO_OUTLINE,
                                    size=27,
                                    color="#FF4FA3",
                                ),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Método de pago exclusivo",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        "Paga únicamente con la tarjeta Candy Koda "
                                        "entregada para la exhibición o con el pase "
                                        "escolar autorizado.",
                                        size=14,
                                        color="#C8C8C8",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(
                    expand=True,
                    padding=30,
                    border_radius=22,
                    bgcolor="#151521",
                    border=ft.Border.all(1, "#29293A"),
                    content=ft.Column(
                        spacing=25,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=85,
                                        height=60,
                                        border_radius=12,
                                        gradient=ft.LinearGradient(
                                            colors=[
                                                "#9B59FF",
                                                "#FF4FA3",
                                            ]
                                        ),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(
                                            ft.Icons.CREDIT_CARD,
                                            size=38,
                                            color="#FFFFFF",
                                        ),
                                    ),
                                    ft.Icon(
                                        ft.Icons.ARROW_FORWARD,
                                        size=30,
                                        color="#555555",
                                    ),
                                    ft.Container(
                                        width=85,
                                        height=60,
                                        border_radius=12,
                                        bgcolor="#252525",
                                        border=ft.Border.all(1, "#4D4D4D"),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(
                                            ft.Icons.CONTACTLESS,
                                            size=40,
                                            color="#9B59FF",
                                        ),
                                    ),
                                ],
                            ),

                            ft.Column(
                                spacing=5,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        "Acerca tu tarjeta",
                                        size=27,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        "Colócala sobre la zona NFC del lector",
                                        size=15,
                                        color="#A8A8A8",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                            ),

                            ft.Divider(
                                height=1,
                                color="#303030",
                            ),

                            ft.Container(
                                width=500,
                                padding=24,
                                border_radius=18,
                                bgcolor="#141414",
                                border=ft.Border.all(1, "#2E2E2E"),
                                content=ft.Column(
                                    spacing=18,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text(
                                                    "Estado de la lectura",
                                                    size=15,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#FFFFFF",
                                                ),
                                                ft.Container(
                                                    padding=ft.Padding.symmetric(
                                                        horizontal=12,
                                                        vertical=6,
                                                    ),
                                                    border_radius=20,
                                                    bgcolor="#251834",
                                                    content=texto_estado,
                                                ),
                                            ],
                                        ),

                                        anillo_espera,

                                        texto_instruccion,
                                    ],
                                ),
                            ),

                            ft.TextButton(
                                "Cancelar y volver al carrito",
                                icon=ft.Icons.CLOSE,
                                style=ft.ButtonStyle(
                                    color="#AFAFAF",
                                ),
                                on_click=lambda e: page.go("/carrito"),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ---------------------------------------------------------
    # RESUMEN DE COMPRA
    # ---------------------------------------------------------

    info_pago = ft.Container(
        expand=1,
        padding=30,
        bgcolor="#11111B",
        border=ft.Border(
            left=ft.BorderSide(
                width=1,
                color="#303030",
            )
        ),
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            size=28,
                            color="#FF4FA3",
                        ),
                        ft.Text(
                            "Resumen de compra",
                            size=25,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                    ],
                ),

                ft.Text(
                    f"{cantidad} productos",
                    size=14,
                    color="#999999",
                ),
                ft.Divider(
                    height=1,
                    color="#303030",
                ),

                ft.Column(
                    spacing=12,
                    controls=productos_carrito,
                ),

                ft.Divider(
                    height=1,
                    color="#303030",
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Subtotal",
                            size=15,
                            color="#BDBDBD",
                        ),
                        ft.Text(
                            formato_precio(subtotal),
                            size=15,
                            color="#FFFFFF",
                        ),
                    ],
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Descuento",
                            size=15,
                            color="#BDBDBD",
                        ),
                        ft.Text(
                            f"-{formato_precio(descuento)}",
                            size=15,
                            color="#57D68D",
                        ),
                    ],
                ),

                ft.Divider(
                    height=1,
                    color="#303030",
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Text(
                            "Total a pagar",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            formato_precio(total),
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color="#FF4FA3",
                        ),
                    ],
                ),

                ft.Container(
                    padding=18,
                    border_radius=15,
                    bgcolor="#21182B",
                    border=ft.Border.all(1, "#4D2C65"),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Container(
                                width=45,
                                height=45,
                                border_radius=12,
                                bgcolor="#352245",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.SECURITY_OUTLINED,
                                    size=26,
                                    color="#9B59FF",
                                ),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=5,
                                controls=[
                                    ft.Text(
                                        "Pago 100% seguro",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        "La operación se realiza únicamente con "
                                        "la tarjeta autorizada para Candy Koda.",
                                        size=13,
                                        color="#B8B8B8",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(
                    padding=15,
                    border_radius=14,
                    bgcolor="#201B12",
                    border=ft.Border.all(1, "#5C481B"),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                size=24,
                                color="#FFC107",
                            ),
                            ft.Text(
                                "No retires la tarjeta hasta que el pago "
                                "sea confirmado.",
                                expand=True,
                                size=13,
                                color="#D8CDAA",
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )
    page.run_task(esperar_tarjeta)
    return ft.View(
        route="/pay",
        padding=0,
        spacing=0,
        bgcolor="#121212",
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    contenido,
                    info_pago,
                ],
            )
        ],
    )
