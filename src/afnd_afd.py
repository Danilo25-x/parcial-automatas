"""Módulo 1: conversión de AFND a AFD (método de subconjuntos)."""

from .modelo import crear_automata, nombre_conjunto


def mover(afnd, conjunto, simbolo):
    """Unión de los destinos de cada estado del conjunto con ese símbolo."""
    destino = set()
    for estado in conjunto:
        destino.update(afnd["transiciones"].get((estado, simbolo), []))
    return frozenset(destino)


def convertir_afnd_a_afd(afnd):
    """Convierte un AFND en AFD.

    Devuelve (tabla, pasos, afd):
      tabla -> una fila por conjunto: {"conjunto", "final", "destinos"}
      pasos -> lista de pasos (conjunto, símbolo, destino) con texto
      afd   -> autómata en el mismo formato del modelo
    """
    orden = {e: i for i, e in enumerate(afnd["estados"])}
    inicial = frozenset([afnd["inicial"]])
    vistos = [inicial]
    pendientes = [inicial]
    tabla, pasos = [], []
    transiciones = {}

    pasos.append({
        "conjunto": nombre_conjunto(inicial, orden), "simbolo": None,
        "destino": None,
        "descripcion": "El estado inicial del AFD es "
                       + nombre_conjunto(inicial, orden),
    })

    while pendientes:
        actual = pendientes.pop(0)
        nombre = nombre_conjunto(actual, orden)
        destinos_fila = {}
        for simbolo in afnd["alfabeto"]:
            destino = mover(afnd, actual, simbolo)
            nombre_dest = nombre_conjunto(destino, orden)
            es_nuevo = destino not in vistos
            if es_nuevo:
                vistos.append(destino)
                pendientes.append(destino)
            destinos_fila[simbolo] = nombre_dest
            transiciones[(nombre, simbolo)] = [nombre_dest]
            texto = f"{nombre} con '{simbolo}' llega a {nombre_dest}"
            pasos.append({
                "conjunto": nombre, "simbolo": simbolo, "destino": nombre_dest,
                "descripcion": texto + (" (conjunto nuevo)" if es_nuevo else ""),
            })
        es_final = any(e in afnd["finales"] for e in actual)
        tabla.append({"conjunto": nombre, "final": es_final,
                      "destinos": destinos_fila})

    nombres = [nombre_conjunto(c, orden) for c in vistos]
    finales = [nombre_conjunto(c, orden) for c in vistos
               if any(e in afnd["finales"] for e in c)]
    afd = crear_automata(nombres, afnd["alfabeto"], nombres[0], finales,
                         transiciones)
    return tabla, pasos, afd
