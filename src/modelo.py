"""Modelo de datos del autómata y funciones básicas.

Un autómata es un diccionario con estas claves:
  estados       -> lista de nombres, ej. ["q0", "q1"]
  alfabeto      -> lista de símbolos de UN carácter, ej. ["a", "b"]
  inicial       -> nombre del estado inicial
  finales       -> lista de estados finales
  transiciones  -> {(estado, símbolo): [estados destino]}

Nota: los símbolos no pueden ser + * ( ) λ ∅ ε porque se usan en la ER.
La transición vacía se escribe con el símbolo ε (EPS) y no va en el alfabeto.
"""

VACIO = "∅"  # nombre del conjunto vacío (estado pozo)
EPS = "ε"    # símbolo de la transición vacía


def crear_automata(estados, alfabeto, inicial, finales, transiciones):
    """Arma el diccionario del autómata."""
    return {
        "estados": list(estados),
        "alfabeto": list(alfabeto),
        "inicial": inicial,
        "finales": list(finales),
        "transiciones": {k: list(v) for k, v in transiciones.items()},
    }


def nombre_conjunto(conjunto, orden):
    """Convierte un conjunto de estados en texto: {q0,q1} o ∅.

    'orden' es un diccionario {estado: posición} para mostrarlos
    siempre en el mismo orden.
    """
    if not conjunto:
        return VACIO
    ordenados = sorted(conjunto, key=lambda e: orden[e])
    return "{" + ",".join(ordenados) + "}"


def clausura_epsilon(automata, estados):
    """Estados que se alcanzan desde 'estados' usando solo transiciones ε."""
    clausura = set(estados)
    pendientes = list(estados)
    while pendientes:
        estado = pendientes.pop()
        for destino in automata["transiciones"].get((estado, EPS), []):
            if destino not in clausura:
                clausura.add(destino)
                pendientes.append(destino)
    return frozenset(clausura)


def acepta_cadena(automata, cadena):
    """Dice si el autómata (AFND, AFND-ε o AFD) acepta la cadena.

    Va guardando el conjunto de estados donde puede estar.
    """
    actuales = clausura_epsilon(automata, {automata["inicial"]})
    for simbolo in cadena:
        siguientes = set()
        for estado in actuales:
            siguientes.update(automata["transiciones"].get((estado, simbolo), []))
        actuales = clausura_epsilon(automata, siguientes)
    return any(e in automata["finales"] for e in actuales)


def estados_alcanzables(automata):
    """Estados a los que se puede llegar desde el inicial."""
    vistos = {automata["inicial"]}
    pendientes = [automata["inicial"]]
    while pendientes:
        estado = pendientes.pop()
        for simbolo in automata["alfabeto"] + [EPS]:
            for destino in automata["transiciones"].get((estado, simbolo), []):
                if destino not in vistos:
                    vistos.add(destino)
                    pendientes.append(destino)
    return vistos


def estados_que_llegan_a_final(automata):
    """Estados desde los que se puede llegar a algún final."""
    vistos = set(automata["finales"])
    cambio = True
    while cambio:
        cambio = False
        for (origen, _), destinos in automata["transiciones"].items():
            if origen not in vistos and any(d in vistos for d in destinos):
                vistos.add(origen)
                cambio = True
    return vistos
