carrito = []
usuario_actual = None
tarjeta_actual = None
koda_hablando = False
configuracion_sistema = {}


def establecer_configuracion(configuracion):
    configuracion_sistema.clear()
    configuracion_sistema.update(configuracion or {})


def obtener_configuracion_sistema():
    return configuracion_sistema.copy()


def agregar_producto(
    id_producto,
    nombre,
    cantidad,
    precio,
    imagen=None,
    id_dispensador=None,
    cantidad_disponible=None,
):
    cantidad = int(cantidad)
    if cantidad <= 0:
        return False

    for item in carrito:
        if item["id_producto"] == id_producto:
            limite = item.get("cantidad_disponible")
            nueva = item["cantidad"] + cantidad
            if limite is not None and nueva > int(limite):
                return False
            item["cantidad"] = nueva

            if imagen is not None:
                item["imagen"] = imagen

            if id_dispensador is not None:
                item["id_dispensador"] = id_dispensador

            return True

    carrito.append({
        "id_producto": id_producto,
        "producto": nombre,
        "cantidad": cantidad,
        "precio": precio,
        "imagen": imagen,
        "id_dispensador": id_dispensador,
        "cantidad_disponible": int(cantidad_disponible) if cantidad_disponible is not None else None,
    })
    return True

def eliminar_producto(nombre):
    for item in carrito:
        if item["producto"] == nombre:
            carrito.remove(item)
            return


def cambiar_cantidad(producto, cantidad):
    for item in carrito:
        if item["producto"] == producto or item["id_producto"] == producto:
            if cantidad <= 0:
                carrito.remove(item)
            else:
                limite = item.get("cantidad_disponible")
                if limite is not None and cantidad > int(limite):
                    return False
                item["cantidad"] = int(cantidad)
            return True
    return False

def obtener_resumen_carrito():
    if not carrito:
        return "El carrito está vacío."

    partes = []

    for item in carrito:
        partes.append(
            f'{item["cantidad"]} {item["producto"]}'
        )

    return ", ".join(partes)

def obtener_carrito():
    return carrito


def calcular_total():
    return sum(
        item["cantidad"] * item["precio"]
        for item in carrito
    )


def cantidad_productos():
    return sum(
        item["cantidad"]
        for item in carrito
    )


def vaciar_carrito():
    carrito.clear()



