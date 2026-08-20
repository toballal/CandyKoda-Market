import flet as ft

from components.menu_lateral import menu_lateral
from components.theme import FONDO, CARD, BORDE
from components.formatos import formato_precio

from app_state import (
    obtener_carrito,
    calcular_total,
    cantidad_productos,
    eliminar_producto,
    cambiar_cantidad,
)


def carrito_view(page: ft.Page):

    nombre_sistema = page.configuracion_sistema.get("nombre_sistema", "Candy Koda")
    page.title = f"{nombre_sistema} Market"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True

    carrito = obtener_carrito()

    # Controles que se actualizarán
    lista_productos = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )

    texto_cantidad = ft.Text(
        color="#A5A1AA",
        size=15,
    )

    texto_subtotal = ft.Text(
        color="#FFFFFF",
        size=16,
    )

    texto_total = ft.Text(
        color="#FF4FA3",
        size=28,
        weight=ft.FontWeight.BOLD,
    )

    boton_pagar = ft.FilledButton(
        "Finalizar compra",
        icon=ft.Icons.PAYMENT,
        height=52,
        bgcolor="#FF4FA3",
        color="#FFFFFF",
        on_click=lambda e: page.go("/pay"),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            icon_size=22,
            text_style=ft.TextStyle(
                font_family="Segoe UI",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
        ),
    )

    def actualizar_carrito():

        carrito_actual = obtener_carrito()

        lista_productos.controls.clear()

        if len(carrito_actual) == 0:

            lista_productos.controls.append(
                ft.Container(
                    expand=True,
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=90,
                                height=90,
                                border_radius=45,
                                bgcolor="#27202E",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.SHOPPING_BASKET_OUTLINED,
                                    size=45,
                                    color="#9B59FF",
                                ),
                            ),

                            ft.Text(
                                "Tu carrito está vacío",
                                size=22,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Text(
                                "Agrega algunos dulces para continuar.",
                                size=15,
                                color="#99939F",
                            ),

                            ft.FilledButton(
                                "Ir a la tienda",
                                icon=ft.Icons.STORE,
                                bgcolor="#2B1A4A",
                                color="#FF4FA3",
                                on_click=lambda e: page.go("/"),
                            ),
                        ],
                    ),
                )
            )

        else:

            for item in carrito_actual:
                lista_productos.controls.append(
                    crear_producto_carrito(item)
                )

        subtotal = calcular_total()
        cantidad = cantidad_productos()

        texto_cantidad.value = (
            f"{cantidad} producto"
            if cantidad == 1
            else f"{cantidad} productos"
        )

        texto_subtotal.value = formato_precio(subtotal)
        texto_total.value = formato_precio(subtotal)

        boton_pagar.disabled = len(carrito_actual) == 0

        boton_pagar.bgcolor = (
            "#FF4FA3"
            if carrito_actual
            else "#4A4650"
        )

        boton_pagar.color = (
            "#FFFFFF"
            if carrito_actual
            else "#A6A2A9"
        )

    def aumentar(item):

        cambiado = cambiar_cantidad(
            item["producto"],
            item["cantidad"] + 1,
        )

        if not cambiado:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Has alcanzado el máximo disponible."
                    ),
                    bgcolor="#6B5722",
                )
            )

        actualizar_carrito()
        page.update()

    def disminuir(item):

        cambiar_cantidad(
            item["producto"],
            item["cantidad"] - 1,
        )

        actualizar_carrito()
        page.update()

    def eliminar(item):

        eliminar_producto(
            item["producto"]
        )

        actualizar_carrito()
        page.update()

    def crear_producto_carrito(item):

        subtotal_producto = (
            item["cantidad"] * item["precio"]
        )

        return ft.Container(
            padding=18,
            border_radius=16,
            bgcolor=CARD,
            border=ft.Border.all(1, BORDE),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[

                    ft.Container(
                        width=75,
                        height=75,
                        border_radius=14,
                        bgcolor="#242027",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Image(
                            src=item["imagen"]
                        ),
                    ),

                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[

                            ft.Text(
                                item["producto"],
                                size=18,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Text(
                                f"Precio unitario: "
                                f"{formato_precio(item['precio'])}",
                                size=13,
                                color="#99939F",
                            ),
                        ],
                    ),

                    ft.Container(
                        padding=6,
                        border_radius=12,
                        bgcolor="#242027",
                        content=ft.Row(
                            spacing=5,
                            controls=[

                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    icon_size=18,
                                    icon_color="#FFFFFF",
                                    on_click=lambda e, producto=item: disminuir(
                                        producto
                                    ),
                                ),

                                ft.Text(
                                    str(item["cantidad"]),
                                    width=30,
                                    text_align=ft.TextAlign.CENTER,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    icon_size=18,
                                    icon_color="#FFFFFF",
                                    on_click=lambda e, producto=item: aumentar(
                                        producto
                                    ),
                                ),
                            ],
                        ),
                    ),

                    ft.Text(
                        formato_precio(subtotal_producto),
                        width=90,
                        size=18,
                        color="#FF4FA3",
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.RIGHT,
                    ),

                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#FF5C77",
                        tooltip="Eliminar producto",
                        on_click=lambda e, producto=item: eliminar(
                            producto
                        ),
                    ),
                ],
            ),
        )

    mainContent = ft.Container(
        expand=True,
        padding=30,
        bgcolor=FONDO,
        content=ft.Column(
            expand=True,
            spacing=25,
            controls=[

                ft.Column(
                    spacing=5,
                    controls=[

                        ft.Text(
                            "Tu carrito",
                            size=38,
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD,
                            font_family="Segoe UI",
                        ),

                        texto_cantidad,
                    ],
                ),

                ft.Row(
                    expand=True,
                    spacing=25,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[

                        ft.Container(
                            expand=2,
                            padding=20,
                            border_radius=20,
                            bgcolor=CARD,
                            border=ft.Border.all(1, BORDE),
                            content=lista_productos,
                        ),

                        ft.Container(
                            width=360,
                            padding=25,
                            border_radius=20,
                            bgcolor="#19161D",
                            border=ft.Border.all(
                                1,
                                "#50365C"
                            ),
                            content=ft.Column(
                                spacing=20,
                                controls=[

                                    ft.Row(
                                        controls=[

                                            ft.Icon(
                                                ft.Icons.RECEIPT_LONG_OUTLINED,
                                                color="#FF4FA3",
                                                size=28,
                                            ),

                                            ft.Text(
                                                "Resumen",
                                                size=24,
                                                color="#FFFFFF",
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                    ),

                                    ft.Divider(
                                        color="#3C3341"
                                    ),

                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[

                                            ft.Text(
                                                "Subtotal",
                                                color="#BDBDBD",
                                            ),

                                            texto_subtotal,
                                        ],
                                    ),

                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[

                                            ft.Text(
                                                "Descuento",
                                                color="#BDBDBD",
                                            ),

                                            ft.Text(
                                                "$0",
                                                color="#57D68D",
                                            ),
                                        ],
                                    ),

                                    ft.Divider(
                                        color="#3C3341"
                                    ),

                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[

                                            ft.Text(
                                                "Total",
                                                size=20,
                                                color="#FFFFFF",
                                                weight=ft.FontWeight.BOLD,
                                            ),

                                            texto_total,
                                        ],
                                    ),

                                    ft.Container(
                                        expand=True
                                    ),

                                    boton_pagar,

                                    ft.Text(
                                        "El pago se realiza únicamente con la "
                                        "tarjeta Candy Koda o con un pase escolar autorizado.",
                                        size=12,
                                        color="#99939F",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    actualizar_carrito()

    return ft.View(
        route="/carrito",
        padding=0,
        spacing=0,
        bgcolor=FONDO,
        controls=[
            ft.Row(
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
                controls=[
                    menu_lateral(page, "/carrito"),
                    mainContent,
                ],
            )
        ],
    )
