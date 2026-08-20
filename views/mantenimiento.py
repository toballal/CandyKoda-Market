import flet as ft

from components.theme import FONDO, MORADO, TEXTO, TEXTO_2


def mantenimiento_view(page: ft.Page):

    return ft.View(
        route="/mantenimiento",
        padding=0,
        spacing=0,
        bgcolor=FONDO,
        controls=[
            ft.Container(
                expand=True,
                padding=40,
                bgcolor=FONDO,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Image(
                            src="LogoCandyKodaSimplify.svg",
                            width=260,
                        ),

                        ft.Container(
                            width=130,
                            height=130,
                            border_radius=65,
                            bgcolor="#201B31",
                            border=ft.Border.all(2, MORADO),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.BUILD_CIRCLE_ROUNDED,
                                size=72,
                                color=MORADO,
                            ),
                        ),

                        ft.Text(
                            "Mantenimiento en curso",
                            size=34,
                            color=TEXTO,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Text(
                            "Estamos preparando Candy Koda para atenderte mejor. "
                            "Las compras están temporalmente pausadas.",
                            width=560,
                            size=16,
                            color=TEXTO_2,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Container(height=8),

                        ft.ProgressRing(
                            color=MORADO,
                        ),

                        ft.Text(
                            "La pantalla se habilitará automáticamente.",
                            size=12,
                            color="#777788",
                        ),
                    ],
                ),
            )
        ],
    )