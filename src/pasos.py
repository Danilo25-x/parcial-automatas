"""Ayudas para el paso a paso del Módulo 1 (sin Tkinter)."""

from .modelo import crear_automata


def afd_parcial(afd, pasos, k):
    """AFD construido hasta el paso k (k = 0 es solo el estado inicial).

    Usa la lista 'pasos' que devuelve convertir_afnd_a_afd.
    """
    estados = []
    transiciones = {}
    for paso in pasos[:k + 1]:
        for nombre in (paso["conjunto"], paso["destino"]):
            if nombre is not None and nombre not in estados:
                estados.append(nombre)
        if paso["simbolo"] is not None:
            transiciones[(paso["conjunto"], paso["simbolo"])] = [paso["destino"]]
    finales = [e for e in estados if e in afd["finales"]]
    return crear_automata(estados, afd["alfabeto"], afd["inicial"],
                          finales, transiciones)


def vista_paso(afd, pasos, k):
    """Qué dibujar en el paso k: (autómata parcial, estados resaltados, flecha resaltada)."""
    paso = pasos[k]
    parcial = afd_parcial(afd, pasos, k)
    if paso["simbolo"] is None:
        return parcial, [paso["conjunto"]], None
    return parcial, [paso["conjunto"]], (paso["conjunto"], paso["simbolo"], paso["destino"])
