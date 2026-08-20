from database.connection import conectar

def obtener_productos():
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                p.id_producto,
                p.nombre,
                p.descripcion,
                p.precio,
                p.stock,
                p.stock_minimo,
                p.imagen,
                p.estado,
                c.nombre AS categoria,
                d.id_dispensador
                ,LEAST(p.stock, d.cantidad_disponible) AS cantidad_disponible
                ,d.estado AS estado_dispensador
            FROM productos p

            INNER JOIN categorias c
                ON p.id_categoria = c.id_categoria

            LEFT JOIN dispensadores d
                ON d.id_producto = p.id_producto

            WHERE p.estado = 'Disponible'
              AND p.stock > 0
              AND d.estado = 'Disponible'
              AND d.cantidad_disponible > 0

            ORDER BY p.nombre
        """

        cursor.execute(sql)

        productos = cursor.fetchall()

        return productos

    except Exception as e:
        print("Error al obtener productos:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()
"""
    {
        "id_producto": 1,
        "nombre": "Frugelé",
        "descripcion": "Caramelos masticables de sabores frutales.",
        "precio": 300,
        "stock": 20,
        "stock_minimo": 5,
        "imagen": "assets/Frugele.png",
        "estado": "activo",
        "categoria": "Frutales"
    },
"""
