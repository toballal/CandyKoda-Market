from hardware.servomotores import enviar_entrega
from database.entregas import iniciar_entrega, completar_entrega, marcar_error


def procesar_entrega(arduino, entregas, id_venta, on_progreso=None):

    print("=== PROCESAR ENTREGA ===")
    print("Entregas recibidas:", entregas)

    if not entregas:
        print("ERROR: No hay productos para entregar")
        return False

    total = len(entregas)
    for indice, entrega in enumerate(entregas, start=1):

        id_dispensador = entrega["id_dispensador"]
        cantidad = entrega["cantidad"]
        iniciar_entrega(entrega["id_entrega"], id_venta)
        if on_progreso:
            on_progreso(indice, total, entrega["producto"], "Dispensando")

        print(
            f"Entregando dispensador {id_dispensador}, "
            f"cantidad {cantidad}"
        )

        resultado = enviar_entrega(
            arduino,
            id_dispensador,
            cantidad
        )

        if not resultado:
            print(
                f"Falló dispensador {id_dispensador}"
            )
            marcar_error(
                entrega["id_entrega"], entrega["id_detalle"], id_venta,
                f"El dispensador {id_dispensador} no confirmó la entrega",
            )
            if on_progreso:
                on_progreso(indice, total, entrega["producto"], "Error")
            return False

        completar_entrega(
            entrega["id_entrega"], entrega["id_detalle"], id_dispensador,
            cantidad, id_venta,
        )
        if on_progreso:
            on_progreso(indice, total, entrega["producto"], "Completada")

    print("Todos los productos fueron entregados")
    return True
