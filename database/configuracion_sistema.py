from database.connection import conectar

CONFIGURACION_PREDETERMINADA = {
    "nombre_sistema": "Candy Koda",
    "stock_minimo": "10",
    "moneda": "CLP",
    "video_fondo": "1",
    "market_mantenimiento": "0",
}


def _es_verdadero(valor):
    return str(valor).strip().casefold() in {"1", "true", "si", "sí", "activo"}


def preparar_configuracion():
    db = conectar()
    if db is None:
        return False
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                clave VARCHAR(80) PRIMARY KEY,
                valor VARCHAR(255) NOT NULL,
                descripcion VARCHAR(255) NULL,
                actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        valores = (
            ("nombre_sistema", "Candy Koda", "Nombre mostrado por el sistema"),
            ("stock_minimo", "10", "Stock mínimo predeterminado"),
            ("moneda", "CLP", "Moneda utilizada por el sistema"),
            ("video_fondo", "1", "Muestra el video decorativo de fondo"),
            ("market_mantenimiento", "0", "Bloquea compras en Candy Koda Market"),
        )
        cursor.executemany(
            "INSERT IGNORE INTO configuracion_sistema (clave, valor, descripcion) VALUES (%s, %s, %s)",
            valores,
        )
        db.commit()
        return True
    except Exception as error:
        db.rollback()
        print("No se pudo preparar la configuración:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        db.close()


def obtener_configuraciones():
    configuracion = CONFIGURACION_PREDETERMINADA.copy()
    db = conectar()
    if db is None:
        return configuracion
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute("SELECT clave, valor FROM configuracion_sistema")
        for clave, valor in cursor.fetchall():
            if clave in configuracion:
                configuracion[clave] = str(valor)
        return configuracion
    except Exception as error:
        print("No se pudo leer la configuración:", error)
        return configuracion
    finally:
        if cursor:
            cursor.close()
        db.close()


def market_en_mantenimiento(configuracion=None):
    configuracion = configuracion or obtener_configuraciones()
    return _es_verdadero(configuracion.get("market_mantenimiento", "0"))
