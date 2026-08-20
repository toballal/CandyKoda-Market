import flet as ft
from components.formatos import formato_precio

from app_state import agregar_producto
from components.menu_lateral import menu_lateral
from database.productos import obtener_productos
from components.theme import FONDO, CARD, BORDE


def productos_view(page: ft.Page):
    productos = obtener_productos()
    categoria_actual = "Todos"

    # ---------------------------------------------------------
    # AGREGAR PRODUCTO
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CARD PRODUCTO
    # ---------------------------------------------------------

    def crear_card(producto):

        disponible = producto["stock"] > 0

        return ft.Container(
            width=280,
            padding=16,
            bgcolor=CARD,
            border_radius=20,

            border=ft.Border.all(
                1,
                BORDE,
            ),

            shadow=ft.BoxShadow(
                blur_radius=12,
                color="#35000000",
                offset=ft.Offset(0, 5),
            ),

            content=ft.Column(
                spacing=10,
                controls=[

                    # IMAGEN
                    ft.Container(
                        height=150,
                        bgcolor="#242027",
                        border_radius=15,
                        alignment=ft.Alignment.CENTER,

                        content=ft.Image(
                            src=producto["imagen"],
                            width=130,
                            height=130,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    ),

                    # NOMBRE + PRECIO
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                        controls=[

                            ft.Text(
                                producto["nombre"],
                                size=18,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),

                            ft.Container(
                                bgcolor="#352143",
                                border_radius=10,
                                padding=ft.Padding.symmetric(
                                    horizontal=10,
                                    vertical=5,
                                ),

                                content=ft.Text(
                                    formato_precio(producto["precio"]),
                                    color="#FF4FA3",
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),

                    # CATEGORIA
                    ft.Text(
                        producto["categoria"],
                        size=12,
                        color="#9B59FF",
                        weight=ft.FontWeight.BOLD,
                    ),

                    # DESCRIPCIÓN
                    ft.Text(
                        producto["descripcion"],
                        size=13,
                        color="#A9A9B2",
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),

                    # DISPONIBILIDAD
                    ft.Row(
                        spacing=6,
                        controls=[

                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE
                                if disponible
                                else ft.Icons.CANCEL,

                                size=16,

                                color=(
                                    "#65D892"
                                    if disponible
                                    else "#FF5C5C"
                                ),
                            ),

                            ft.Text(
                                "Disponible"
                                if disponible
                                else "Agotado",

                                size=12,

                                color=(
                                    "#65D892"
                                    if disponible
                                    else "#FF5C5C"
                                ),
                            ),
                        ],
                    ),

                    ft.Text(
                        "Últimas unidades" if producto["cantidad_disponible"] <= producto["stock_minimo"] else f'{producto["cantidad_disponible"]} disponibles',
                        size=12,
                        color="#FFC857" if producto["cantidad_disponible"] <= producto["stock_minimo"] else "#A9A9B2",
                        weight=ft.FontWeight.BOLD,
                    ),


                    # BOTÓN
                    ft.FilledButton(
                        "Agregar al carrito",
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        disabled=not disponible,
                        height=45,

                        bgcolor=(
                            "#2B1A4A"
                            if disponible
                            else "#333333"
                        ),

                        color="#FFFFFF",

                        on_click=lambda e, p=producto:
                            agregar_al_carrito(p),

                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(
                                radius=12
                            ),

                            side=ft.BorderSide(
                                1,
                                "#9B59FF"
                                if disponible
                                else "#555555",
                            ),
                        ),
                    ),
                ],
            ),
        )

    # ---------------------------------------------------------
    # GRID
    # ---------------------------------------------------------

    grid_productos = ft.GridView(
        expand=True,
        max_extent=330,
        child_aspect_ratio=0.85,
        spacing=20,
        run_spacing=20,
    )
    # ---------------------------------------------------------
    # CONTADOR
    # ---------------------------------------------------------

    contador = ft.Text(
        "0 productos encontrados",
        size=14,
        color="#A9A9B2",
    )

    # ---------------------------------------------------------
    # BUSCADOR
    # ---------------------------------------------------------

    buscador = ft.TextField(
        hint_text="Buscar productos...",
        prefix_icon=ft.Icons.SEARCH,
        height=52,
        expand=True,

        bgcolor="#19191D",

        border_radius=15,
        border_color="#37323D",
        focused_border_color="#9B59FF",

        cursor_color="#FF4FA3",
    )

    # ---------------------------------------------------------
    # ORDENAR
    # ---------------------------------------------------------

    ordenar = ft.Dropdown(
        width=220,
        value="Recomendados",

        bgcolor="#19191D",

        border_color="#37323D",
        focused_border_color="#9B59FF",

        options=[
            ft.dropdown.Option("Recomendados"),
            ft.dropdown.Option("Precio menor"),
            ft.dropdown.Option("Precio mayor"),
            ft.dropdown.Option("Nombre A-Z"),
            ft.dropdown.Option("Nombre Z-A"),
        ],
    )

    # ---------------------------------------------------------
    # FILTRAR PRODUCTOS
    # ---------------------------------------------------------

    def filtrar(e=None):

        texto = buscador.value.lower().strip()

        lista_filtrada = []

        for producto in productos:

            coincide_nombre = (
                texto in producto["nombre"].lower()
            )

            coincide_categoria = (
                categoria_actual == "Todos"
                or producto["categoria"] == categoria_actual
            )

            if coincide_nombre and coincide_categoria:
                lista_filtrada.append(producto)

        # ORDENAMIENTO

        if ordenar.value == "Precio menor":

            lista_filtrada.sort(
                key=lambda producto: producto["precio"]
            )

        elif ordenar.value == "Precio mayor":

            lista_filtrada.sort(
                key=lambda producto: producto["precio"],
                reverse=True,
            )

        elif ordenar.value == "Nombre A-Z":

            lista_filtrada.sort(
                key=lambda producto:
                    producto["nombre"].lower()
            )

        elif ordenar.value == "Nombre Z-A":

            lista_filtrada.sort(
                key=lambda producto:
                    producto["nombre"].lower(),
                reverse=True,
            )

        mostrar_productos(lista_filtrada)

    # ---------------------------------------------------------
    # MOSTRAR PRODUCTOS
    # ---------------------------------------------------------

    def mostrar_productos(lista):

        grid_productos.controls.clear()

        for producto in lista:

            grid_productos.controls.append(
                crear_card(producto)
            )

        cantidad = len(lista)

        contador.value = (
            f"{cantidad} producto encontrado"
            if cantidad == 1
            else f"{cantidad} productos encontrados"
        )

        page.update()

    # ---------------------------------------------------------
    # CAMBIAR CATEGORÍA
    # ---------------------------------------------------------

    botones_categoria = {}

    def seleccionar_categoria(nombre):

        nonlocal categoria_actual

        categoria_actual = nombre

        for categoria, boton in botones_categoria.items():

            if categoria == categoria_actual:

                boton.bgcolor = "#2B1A4A"
                boton.color = "#FF4FA3"

            else:

                boton.bgcolor = "#202024"
                boton.color = "#A9A9B2"

        filtrar()

    # ---------------------------------------------------------
    # BOTONES CATEGORÍA
    # ---------------------------------------------------------

    categorias = [
        "Todos",
        "Frutales",
        "Chicles",
        "Masticables",
    ]

    fila_categorias = ft.Row(
        spacing=10,
    )

    for categoria in categorias:

        boton = ft.FilledButton(
            categoria,

            bgcolor=(
                "#2B1A4A"
                if categoria == "Todos"
                else "#202024"
            ),

            color=(
                "#FF4FA3"
                if categoria == "Todos"
                else "#A9A9B2"
            ),

            on_click=lambda e, c=categoria:
                seleccionar_categoria(c),

            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(
                    radius=20
                ),
            ),
        )

        botones_categoria[categoria] = boton
        fila_categorias.controls.append(boton)

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    buscador.on_change = filtrar
    ordenar.on_select = filtrar

    # ---------------------------------------------------------
    # CONTENIDO PRINCIPAL
    # ---------------------------------------------------------

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=FONDO,

        content=ft.Column(
            expand=True,
            spacing=20,

            controls=[

                # ENCABEZADO
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    controls=[

                        ft.Column(
                            spacing=5,

                            controls=[
                                ft.Text(
                                    "Todos los productos",
                                    size=34,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "Encuentra tus dulces favoritos",
                                    size=15,
                                    color="#A5A1AA",
                                ),
                            ],
                        ),

                        ft.IconButton(
                            icon=ft.Icons.SHOPPING_CART_OUTLINED,
                            icon_size=30,
                            icon_color="#FF4FA3",

                            on_click=lambda e:
                                page.go("/carrito"),
                        ),
                    ],
                ),

                # BUSCAR + ORDENAR
                ft.Row(
                    spacing=15,

                    controls=[
                        buscador,
                        ordenar,
                    ],
                ),

                # FILTROS
                ft.Column(
                    spacing=10,

                    controls=[

                        ft.Text(
                            "Categorías",
                            color="#FFFFFF",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),

                        fila_categorias,
                    ],
                ),

                ft.Divider(
                    color="#37323D",
                    height=1,
                ),

                contador,

                # PRODUCTOS
                grid_productos,
            ],
        ),
    )

    # ---------------------------------------------------------
    # CARGAR PRODUCTOS
    # ---------------------------------------------------------

    mostrar_productos(productos)

    # ---------------------------------------------------------
    # VIEW
    # ---------------------------------------------------------

    return ft.View(
        route="/productos",
        padding=0,
        spacing=0,

        controls=[

            ft.Row(
                expand=True,
                spacing=0,

                vertical_alignment=
                    ft.CrossAxisAlignment.STRETCH,

                controls=[
                    menu_lateral(page, "/productos"),
                    contenido,
                ],
            )
        ],
    )
