import flet as ft
import asyncio

from IA.assistent import hablarConKoda
from IA.voz import hablar
from app_state import (
    agregar_producto,
    cambiar_cantidad,
    vaciar_carrito
)
from database.productos import obtener_productos
from components.menu_lateral import menu_lateral


def koda_view(page: ft.Page):

    # Historial de mensajes
    lista_mensajes = ft.ListView(
        expand=True,
        spacing=15,
        padding=20,
        auto_scroll=True,
    )

    # Campo donde escribe el usuario
    input_mensaje = ft.TextField(
        hint_text="Escribe tu pedido...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=3,
        bgcolor="#1B1B1F",
        border_color="#37323D",
        focused_border_color="#9B59FF",
        cursor_color="#FF4FA3",
        border_radius=15,
        text_size=16,
        content_padding=15,
    )

    def crear_burbuja(texto, es_usuario=False):

        color_fondo = "#5D32A8" if es_usuario else "#1F1F24"
        color_borde = "#9B59FF" if es_usuario else "#37323D"

        burbuja = ft.Container(
            width=550,
            padding=15,
            bgcolor=color_fondo,
            border=ft.Border.all(1, color_borde),
            border_radius=16,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(
                        "Tú" if es_usuario else "Koda",
                        size=12,
                        color="#FFFFFF" if es_usuario else "#FF4FA3",
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        texto,
                        size=15,
                        color="#FFFFFF",
                        selectable=True,
                    ),
                ],
            ),
        )

        return ft.Row(
            alignment=(
                ft.MainAxisAlignment.END
                if es_usuario
                else ft.MainAxisAlignment.START
            ),
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[

                # Avatar de Koda
                ft.Container(
                    visible=not es_usuario,
                    width=40,
                    height=40,
                    bgcolor="#2B1A4A",
                    border_radius=12,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src="assets/LogoCandyKodaVerySimple.svg",
                        width=25,
                    ),
                ),

                burbuja,
            ],
        )

    def agregar_respuesta_koda(texto):

        lista_mensajes.controls.append(
            crear_burbuja(
                texto,
                es_usuario=False,
            )
        )

        page.update()

    async def enviar_mensaje(e=None):

        texto = input_mensaje.value.strip()

        if texto == "":
            return

        lista_mensajes.controls.append(
            crear_burbuja(
                texto,
                es_usuario=True,
            )
        )

        input_mensaje.value = ""
        input_mensaje.disabled = True

        page.update()

        try:

            resultado = await asyncio.to_thread(
                hablarConKoda,
                texto
            )

            mensaje_koda = resultado["mensaje"]
            pedido_detectado = resultado["pedido"]
            accion = resultado.get("accion")

            lista_mensajes.controls.append(
                crear_burbuja(
                    mensaje_koda,
                    es_usuario=False,
                )
            )

            page.update()

            page.run_task(
                hablar,
                mensaje_koda
            )

            if accion == "vaciar":
                vaciar_carrito()

            if pedido_detectado:

                for producto in pedido_detectado:

                    nombre = producto["producto"]
                    cantidad = producto["cantidad"]
                    precio = producto["precio"]

                    producto_bd = next(
                        (
                            p
                            for p in obtener_productos()
                            if p["nombre"].lower() == nombre.lower()
                        ),
                        None
                    )

                    if producto_bd is None:
                        continue

                    id_producto = producto_bd["id_producto"]
                    imagen = producto_bd["imagen"]

                    if accion == "agregar":

                        agregar_producto(
                            id_producto,
                            nombre,
                            cantidad,
                            precio,
                            imagen,
                            producto_bd["id_dispensador"],
                            producto_bd.get("cantidad_disponible"),
                        )

                    elif accion == "actualizar":

                        cambiar_cantidad(
                            id_producto,
                            cantidad
                        )

                    elif accion == "eliminar":

                        cambiar_cantidad(
                            id_producto,
                            0
                        )

        except Exception as error:

            detalle = str(error)

            mensaje_error = (
                "Koda todavía no tiene configurada su conexión con la IA. "
                "Solicita al administrador que configure GROQ_API_KEY."
                if "GROQ_API_KEY" in detalle or "clave de IA" in detalle
                else "No pude conectarme en este momento. Intenta nuevamente."
            )

            lista_mensajes.controls.append(
                crear_burbuja(
                    mensaje_error,
                    es_usuario=False,
                )
            )

            print(f"Error al hablar con Koda: {error}")

        finally:

            input_mensaje.disabled = False

            page.update()

            await input_mensaje.focus()

    async def colocar_sugerencia(texto):

        input_mensaje.value = texto

        page.update()

        await input_mensaje.focus()

    # Mensaje inicial
    lista_mensajes.controls.append(
        crear_burbuja(
            "¡Hola! Soy Koda, la asistente de Candy Koda.\n"
            "Puedo ayudarte a elegir dulces, revisar promociones "
            "y preparar tu pedido.",
            es_usuario=False,
        )
    )

    encabezado = ft.Container(
        padding=20,
        bgcolor="#151518",
        border=ft.Border.only(
            bottom=ft.BorderSide(1, "#303036"),
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[

                ft.Row(
                    spacing=12,
                    controls=[

                        ft.Container(
                            width=52,
                            height=52,
                            bgcolor="#2B1A4A",
                            border_radius=16,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Image(
                                src="assets/LogoCandyKodaVerySimple.svg",
                                width=30,
                            ),
                        ),

                        ft.Column(
                            spacing=3,
                            controls=[

                                ft.Text(
                                    "Koda IA",
                                    size=23,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Row(
                                    spacing=6,
                                    controls=[

                                        ft.Container(
                                            width=8,
                                            height=8,
                                            bgcolor="#43D17A",
                                            border_radius=4,
                                        ),

                                        ft.Text(
                                            "Disponible",
                                            size=13,
                                            color="#A0A0A8",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color="#A0A0A8",
                    tooltip="Volver a la tienda",
                    on_click=lambda e: page.go("/"),
                ),
            ],
        ),
    )

    sugerencias = ft.Row(
        spacing=10,
        wrap=True,
        controls=[

            ft.OutlinedButton(
                "Quiero 2 Frugelé",
                icon=ft.Icons.ADD_SHOPPING_CART,
                on_click=lambda e: page.run_task(
                    colocar_sugerencia,
                    "Quiero 2 Frugelé"
                ),
                style=ft.ButtonStyle(
                    color="#FF4FA3",
                    side=ft.BorderSide(1, "#51365F"),
                    shape=ft.RoundedRectangleBorder(radius=14),
                ),
            ),

            ft.OutlinedButton(
                "Recomiéndame algo",
                icon=ft.Icons.AUTO_AWESOME,
                on_click=lambda e: page.run_task(
                    colocar_sugerencia,
                    "¿Qué dulce me recomiendas?"
                ),
                style=ft.ButtonStyle(
                    color="#9B59FF",
                    side=ft.BorderSide(1, "#51365F"),
                    shape=ft.RoundedRectangleBorder(radius=14),
                ),
            ),

            ft.OutlinedButton(
                "Ver promociones",
                icon=ft.Icons.LOCAL_OFFER_OUTLINED,
                on_click=lambda e: page.run_task(
                    colocar_sugerencia,
                    "Muéstrame las promociones disponibles"
                ),
                style=ft.ButtonStyle(
                    color="#FFC107",
                    side=ft.BorderSide(1, "#5A4B28"),
                    shape=ft.RoundedRectangleBorder(radius=14),
                ),
            ),
        ],
    )

    barra_entrada = ft.Container(
        padding=20,
        bgcolor="#151518",
        border=ft.Border.only(
            top=ft.BorderSide(1, "#303036"),
        ),
        content=ft.Column(
            spacing=12,
            controls=[

                sugerencias,

                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[

                        input_mensaje,

                        ft.Container(
                            width=52,
                            height=52,
                            border_radius=16,
                            bgcolor="#FF4FA3",
                            content=ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                icon_color="#FFFFFF",
                                tooltip="Enviar",
                                on_click=enviar_mensaje,
                            ),
                        ),
                    ],
                ),

                ft.Text(
                    "Revisa tu pedido antes de finalizar la compra.",
                    size=11,
                    color="#74747D",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    contenido = ft.Container(
        expand=True,
        bgcolor="#101012",
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[

                encabezado,

                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(
                        horizontal=35,
                        vertical=10,
                    ),
                    content=lista_mensajes,
                ),

                barra_entrada,
            ],
        ),
    )

    return ft.View(
        route="/koda",
        padding=0,
        spacing=0,
        bgcolor="#101012",
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    menu_lateral(page, "/koda"),

                    ft.Container(
                        expand=True,
                        content=contenido,
                    ),
                ],
            )
        ],
    )