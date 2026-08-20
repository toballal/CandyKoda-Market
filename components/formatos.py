from decimal import Decimal


SIMBOLOS_MONEDA = {
    "CLP": "$",
    "USD": "US$",
    "EUR": "€",
}


def formato_precio(valor, configuracion=None, decimales=0):
    if configuracion is None:
        from app_state import obtener_configuracion_sistema

        configuracion = obtener_configuracion_sistema()
    moneda = str(configuracion.get("moneda", "CLP")).upper()
    simbolo = SIMBOLOS_MONEDA.get(moneda, f"{moneda} ")
    numero = Decimal(str(valor))
    texto = f"{numero:,.{decimales}f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{simbolo}{texto}"
