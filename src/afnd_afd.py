"""Módulo 1: conversión de AFND a AFD (método de subconjuntos)."""

from .modelo import crear_automata, nombre_conjunto, clausura_epsilon


def mover(afnd, conjunto, simbolo):
    """Unión de los destinos de cada estado del conjunto con ese símbolo,
    más la clausura-ε del resultado."""
    destino = set()
    for estado in conjunto:
        destino.update(afnd["transiciones"].get((estado, simbolo), []))
    return clausura_epsilon(afnd, destino)


def _tiene_final(afnd, conjunto):
    """True si el conjunto contiene algún estado final del AFND."""
    return any(e in afnd["finales"] for e in conjunto)


def _texto_inicial(simple, inicial, orden):
    """Explica cuál es el estado inicial del AFD (con clausura-ε si hace falta)."""
    if simple == inicial:
        return "El estado inicial del AFD es " + nombre_conjunto(inicial, orden)
    return (f"Clausura-ε de {nombre_conjunto(simple, orden)} = "
            f"{nombre_conjunto(inicial, orden)}: es el estado inicial del AFD")


def convertir_afnd_a_afd(afnd):
    """Convierte un AFND en AFD.

    Devuelve (tabla, pasos, afd):
      tabla -> una fila por conjunto: {"conjunto", "final", "destinos"}
      pasos -> lista de pasos (conjunto, símbolo, destino) con texto
      afd   -> autómata en el mismo formato del modelo
    """
    orden = {e: i for i, e in enumerate(afnd["estados"])}
    simple = frozenset([afnd["inicial"]])
    inicial = clausura_epsilon(afnd, simple)       # clausura-ε del inicial
    vistos = [inicial]
    pendientes = [inicial]
    tabla, pasos = [], []
    transiciones = {}

    pasos.append({
        "conjunto": nombre_conjunto(inicial, orden), "simbolo": None,
        "destino": None,
        "descripcion": _texto_inicial(simple, inicial, orden),
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
        tabla.append({"conjunto": nombre, "final": _tiene_final(afnd, actual),
                      "destinos": destinos_fila})

    nombres = [nombre_conjunto(c, orden) for c in vistos]
    finales = [nombre_conjunto(c, orden) for c in vistos if _tiene_final(afnd, c)]
    afd = crear_automata(nombres, afnd["alfabeto"], nombres[0], finales,
                         transiciones)
    return tabla, pasos, afd
