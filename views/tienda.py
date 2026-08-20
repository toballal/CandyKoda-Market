import flet as ft
from components.formatos import formato_precio
from app_state import obtener_carrito
from app_state import agregar_producto
from components.menu_lateral import menu_lateral
from database.productos import obtener_productos
from components.theme import FONDO, CARD, BORDE


def card_producto(producto, agregar_al_carrito):
    return ft.Container(
        height=320,
        padding=16,
        bgcolor=CARD,
        border_radius=20,
        border=ft.Border.all(1, BORDE),
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color="#35000000",
            offset=ft.Offset(0, 5),
        ),
        content=ft.Column(
            expand=True,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    height=135,
                    bgcolor="#242027",
                    border_radius=16,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src=producto["imagen"],
                        width=115,
                        height=115,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            producto["nombre"],
                            size=18,
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD,
                            font_family="Segoe UI",
                            expand=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),

                        ft.Container(
                            padding=ft.Padding.symmetric(
                                horizontal=10,
                                vertical=5,
                            ),
                            bgcolor="#352143",
                            border_radius=12,
                            content=ft.Text(
                                formato_precio(producto["precio"]),
                                color="#FF4FA3",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ],
                ),

                ft.Text(
                    producto["descripcion"],
                    size=13,
                    color="#A9A9B2",
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),

                ft.Container(expand=True),

                ft.FilledButton(
                    "Agregar",
                    icon=ft.Icons.ADD_SHOPPING_CART,
                    height=45,
                    bgcolor="#2B1A4A",
                    color="#FFFFFF",
                    on_click=lambda e: agregar_al_carrito(producto),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        side=ft.BorderSide(1, "#9B59FF"),
                        padding=12,
                        icon_size=21,
                        text_style=ft.TextStyle(
                            font_family="Segoe UI",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ),
            ],
        ),
    )

carrito = obtener_carrito()
def card_carrito(page: ft.Page):
    return ft.Container(
        height=320,
        padding=16,
        bgcolor=CARD,
        border_radius=20,
        border=ft.Border.all(1, "#50365C"),
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color="#35000000",
            offset=ft.Offset(0, 5),
        ),
        content=ft.Column(
            expand=True,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Tu carrito",
                                    size=22,
                                    color="#FFFFFF",
                                    font_family="Segoe UI",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"{sum(item['cantidad'] for item in carrito)} productos",
                                    size=13,
                                    color="#99939F",
                                ),
                            ],
                        ),
                        ft.Container(
                            width=42,
                            height=42,
                            bgcolor="#2B1A4A",
                            border_radius=13,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.SHOPPING_CART_OUTLINED,
                                size=24,
                                color="#FF4FA3",
                            ),
                        ),
                    ],
                ),

                ft.Divider(
                    height=1,
                    color="#3C3341",
                ),

                contenido_carrito(),

                ft.FilledButton(
                    "Finalizar compra",
                    icon=ft.Icons.PAYMENT,
                    disabled=len(carrito) == 0,
                    on_click=lambda e: page.go("/pay"),
                    height=45,
                    bgcolor=(
                        "#FF4FA3"
                        if len(carrito) > 0
                        else "#4A4650"
                    ),
                    color=(
                        "#FFFFFF"
                        if len(carrito) > 0
                        else "#A6A2A9"
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        icon_size=20,
                        text_style=ft.TextStyle(
                            font_family="Segoe UI",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ),
            ],
        ),
    )

def crear_item_carrito(item):
    return ft.Container(
        padding=8,
        bgcolor="#232028",
        border_radius=10,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            item["producto"],
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f'{item["cantidad"]} x {formato_precio(item["precio"])}',
                            color="#99939F",
                            size=12,
                        ),
                    ],
                ),
                ft.Text(
                    formato_precio(item["cantidad"] * item["precio"]),
                    color="#FF4FA3",
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
    )

def contenido_carrito():
    if len(carrito) == 0:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=68,
                        height=68,
                        bgcolor="#27202E",
                        border_radius=34,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            ft.Icons.SHOPPING_BASKET_OUTLINED,
                            size=34,
                            color="#9B59FF",
                        ),
                    ),
                    ft.Text(
                        "Carrito vacío",
                        size=16,
                        color="#FFFFFF",
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Agrega un dulce para comenzar",
                        size=12,
                        color="#99939F",
                    ),
                ],
            ),
        )

    return ft.ListView(
        expand=True,
        spacing=8,
        controls=[
            crear_item_carrito(item)
            for item in carrito
        ],
    )


def tienda_view(page: ft.Page):
    productos = obtener_productos()

    def buscar(e):
        texto = e.control.value.lower()

        busqueda.content.controls.clear()

        if texto == "":
            busqueda.visible = False
        else:
            for producto in productos:
                if texto in producto["nombre"].lower():
                    busqueda.content.controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="#1F1F1F",
                            border_radius=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(producto["nombre"]),
                                    ft.FilledButton(
                                        "Agregar",
                                        icon=ft.Icons.ADD_SHOPPING_CART,
                                        height=45,
                                        bgcolor="#2B1A4A",
                                        color="#FFFFFF",
                                        on_click=lambda e, p=producto: agregar_al_carrito(p),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                            side=ft.BorderSide(1, "#9B59FF"),
                                            padding=12,
                                            icon_size=21,
                                            text_style=ft.TextStyle(
                                                font_family="Segoe UI",
                                                size=15,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ),
                                    )
                                ]
                            )
                        )
                    )

            busqueda.visible = len(busqueda.content.controls) > 0

        page.update()

    def agregar_al_carrito(producto):

        precio = int(producto["precio"])

        agregado = agregar_producto(
            producto["id_producto"],
            producto["nombre"],
            1,
            precio,
            producto["imagen"],
            producto["id_dispensador"],
            producto.get("cantidad_disponible"),
        )

        snackbar = ft.SnackBar(
            content=ft.Text(
                f'{producto["nombre"]} agregado al carrito' if agregado else f'No hay más unidades disponibles de {producto["nombre"]}',
                color="#FFFFFF"
            ),
            bgcolor="#2B1A4A" if agregado else "#6B5722",
        )

        page.overlay.append(snackbar)
        snackbar.open = True

        page.update()

        if agregado:
            contenedor_carrito.content = card_carrito(page)
            contenedor_carrito.update()

    busqueda = ft.Container(
        visible=False,
        width=500,
        height=200,
        bgcolor="#111111",
        border=ft.Border.all(1, "#535353"),
        border_radius=15,
        padding=10,
        shadow=ft.BoxShadow(
            blur_radius=15,
        ),
        content=ft.Column(
            spacing=5,
            controls=[]
        )
    )

    contenedor_carrito = ft.Container(
        expand=True,
        content=card_carrito(page),
    )

        # CREAR LOS 3 ESPACIOS PARA PRODUCTOS
    productos_mostrar = productos[:3]

    espacios_productos = []

    for i in range(3):
        if i < len(productos_mostrar):
            espacios_productos.append(
                ft.Container(
                    expand=True,
                    content=card_producto(
                        productos_mostrar[i],
                        agregar_al_carrito
                    ),
                )
            )
        else:
            espacios_productos.append(
                ft.Container(
                    expand=True,
                )
            )

    contentMain = ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.with_opacity(0.84, FONDO),
        content=ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[

                        # Título
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "Bienvenido a",
                                    color="#FFFFFF",
                                    font_family="Segoe UI",
                                    size=36,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Candy",
                                    color="#9B59FF",
                                    font_family="Segoe UI",
                                    size=36,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Koda",
                                    color="#FF4FA3",
                                    font_family="Segoe UI",
                                    size=36,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),

                        ft.Text(
                            "Elige tus dulces o pídeselos directamente a Koda",
                            color="#A5A1AA",
                            size=15,
                            font_family="Segoe UI",
                        ),

                        # Botón IA
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=320,
                                    height=72,
                                    padding=2,
                                    border_radius=20,
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(-1, 0),
                                        end=ft.Alignment(1, 0),
                                        colors=[
                                            "#9B59FF",
                                            "#FF4FA3",
                                        ],
                                    ),
                                    content=ft.FilledButton(
                                        "Hablar con Koda",
                                        icon=ft.Icons.AUTO_AWESOME,
                                        on_click=lambda e: page.go("/koda"),
                                        bgcolor="#18151D",
                                        color="#FFFFFF",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=18),
                                            icon_size=25,
                                            text_style=ft.TextStyle(
                                                size=17,
                                                weight=ft.FontWeight.BOLD,
                                                font_family="Segoe UI",

                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        # SOLO EL BUSCADOR
                        ft.Row(
                            margin=ft.Margin(
                                top=40,
                                left=0,
                                bottom=0,
                                right=0
                            ),
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.TextField(
                                    hint_text="Buscar dulces...",
                                    on_change=buscar,
                                    width=520,
                                    height=54,
                                    bgcolor="#19191D",
                                    border_radius=15,
                                    border_color="#37323D",
                                    focused_border_color="#9B59FF",
                                    cursor_color="#FF4FA3",
                                    prefix_icon=ft.Icons.SEARCH,
                                    text_size=15,
                                    content_padding=16,
                                )
                            ]
                        ),
                        # PRODUCTOS
                        ft.Container(
                            expand=True,
                            margin=ft.Margin(
                                top=20,
                                left=0,
                                right=0,
                                bottom=0,
                            ),
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        spacing=20,
                                        controls=[
                                            ft.Container(
                                                expand=3,
                                                content=ft.Row(
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Text(
                                                            "Productos Disponibles",
                                                            color="#FFFFFF",
                                                            size=20,
                                                            font_family="Segoe UI",
                                                        ),
                                                        ft.FilledButton(
                                                            "Ver todo",
                                                            on_click=lambda e: page.go("/productos"),
                                                            bgcolor="#222222",
                                                            color="#FF4FA3",
                                                        ),
                                                    ],
                                                ),
                                            ),

                                            # Espacio reservado para el carrito
                                            ft.Container(
                                                expand=1,
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=20,
                                        expand=True,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Container(
                                                expand=3,
                                                content=ft.Row(
                                                    spacing=20,
                                                    expand=True,
                                                    controls=espacios_productos,
                                                ),
                                            ),

                                            ft.Container(
                                                expand=1,
                                                content=contenedor_carrito,
                                            ),
                                        ],
                                    )
                                ]
                            )
                        ),
                    ]
                ),

                # LISTA FLOTANTE (TIENE QUE ESTAR AL FINAL)
                ft.Container(
                    top=260,
                    left=0,
                    right=0,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=500,
                                content=busqueda
                            )
                        ]
                    ),
                )
            ]
        )
    )

    return ft.View(
        route="/",
        padding=0,
        spacing=0,
        controls=[
            ft.Row(
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
                controls=[
                    menu_lateral(page, "/"),
                    ft.Container(
                        expand=True,
                        content=contentMain,
                    ),
                ],
            )
        ]
    )
