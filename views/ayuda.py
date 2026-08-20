import flet as ft

from components.menu_lateral import menu_lateral
from components.theme import (
    FONDO,
    CARD,
    BORDE,
    MORADO,
    ROSA,
    TEXTO,
    TEXTO_2,
    encabezado,
)


def ayuda_view(page: ft.Page):

    pasos = [
        (
            ft.Icons.TOUCH_APP_ROUNDED,
            "1. Elige tus productos",
            "Explora el catálogo o pídele una recomendación a Koda.",
        ),
        (
            ft.Icons.SHOPPING_BAG_ROUNDED,
            "2. Revisa tu carrito",
            "Confirma las cantidades y el total antes de continuar.",
        ),
        (
            ft.Icons.CONTACTLESS_ROUNDED,
            "3. Acerca tu tarjeta",
            "Mantén tu tarjeta Candy Koda junto al lector NFC.",
        ),
        (
            ft.Icons.LOCK_ROUNDED,
            "4. Confirma el pago",
            "Ingresa tu PIN de cuatro dígitos y espera la aprobación.",
        ),
        (
            ft.Icons.INVENTORY_2_ROUNDED,
            "5. Retira tus dulces",
            "Espera hasta que la pantalla confirme la entrega.",
        ),
    ]

    tarjetas = [
        ft.Container(
            padding=20,
            bgcolor=CARD,
            border=ft.Border.all(1, BORDE),
            border_radius=18,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        border_radius=14,
                        bgcolor=ft.Colors.with_opacity(0.14, MORADO),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icono,
                            color=MORADO,
                            size=25,
                        ),
                    ),
                    ft.Text(
                        titulo,
                        size=17,
                        color=TEXTO,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        detalle,
                        size=13,
                        color=TEXTO_2,
                    ),
                ],
            ),
        )
        for icono, titulo, detalle in pasos
    ]

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=FONDO,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=24,
            controls=[
                encabezado(
                    "¿Cómo comprar?",
                    "Sigue estos pasos para usar el tótem.",
                    ft.Icons.HELP_CENTER_ROUNDED,
                ),

                ft.ResponsiveRow(
                    columns=10,
                    spacing=14,
                    run_spacing=14,
                    controls=[
                        ft.Container(
                            col={
                                "sm": 10,
                                "md": 5,
                                "lg": 2,
                            },
                            content=tarjeta,
                        )
                        for tarjeta in tarjetas
                    ],
                ),

                ft.Container(
                    padding=22,
                    bgcolor="#231D12",
                    border=ft.Border.all(1, "#66501C"),
                    border_radius=18,
                    content=ft.Row(
                        spacing=16,
                        controls=[
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                color="#FFC857",
                                size=32,
                            ),
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Si un producto no es entregado",
                                        color=TEXTO,
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "No vuelvas a pagar. Conserva el número de venta: "
                                        "el sistema devolverá automáticamente el importe "
                                        "del producto no entregado.",
                                        color="#D8CDAA",
                                        size=13,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(
                            "Comenzar compra",
                            icon=ft.Icons.STOREFRONT_ROUNDED,
                            height=52,
                            bgcolor=ROSA,
                            color="#FFFFFF",
                            on_click=lambda e: page.go("/"),
                        )
                    ],
                ),
            ],
        ),
    )

    return ft.View(
        route="/ayuda",
        padding=0,
        spacing=0,
        bgcolor=FONDO,
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    menu_lateral(page, "/ayuda"),
                    contenido,
                ],
            )
        ],
    )