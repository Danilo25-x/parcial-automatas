"""Convierte el texto del editor en un autómata (con errores claros)."""

from .modelo import crear_automata, EPS

SIMBOLOS_PROHIBIDOS = set("+*()λ∅ε")


def _separar(texto):
    """'q0, q1 q2' -> ['q0', 'q1', 'q2'] sin vacíos ni repetidos."""
    resultado = []
    for palabra in texto.replace(",", " ").split():
        if palabra not in resultado:
            resultado.append(palabra)
    return resultado


def _leer_alfabeto(texto):
    alfabeto = _separar(texto)
    if not alfabeto:
        raise ValueError("El alfabeto está vacío.")
    for simbolo in alfabeto:
        if len(simbolo) != 1:
            raise ValueError(f"El símbolo '{simbolo}' debe tener un solo carácter.")
        if simbolo in SIMBOLOS_PROHIBIDOS:
            raise ValueError(f"El símbolo '{simbolo}' no se puede usar en el alfabeto.")
    return alfabeto


def _leer_transiciones(texto, estados, alfabeto):
    """Cada línea: origen,símbolo,destino  (las líneas con # se ignoran)."""
    transiciones = {}
    for numero, linea in enumerate(texto.splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = linea.replace(",", " ").split()
        if len(partes) != 3:
            raise ValueError(f"Línea {numero}: escriba 'origen,símbolo,destino'.")
        origen, simbolo, destino = partes
        if simbolo in ("eps", "epsilon"):          # alias fácil de escribir
            simbolo = EPS
        for estado in (origen, destino):
            if estado not in estados:
                raise ValueError(f"Línea {numero}: el estado '{estado}' no existe.")
        if simbolo != EPS and simbolo not in alfabeto:
            raise ValueError(f"Línea {numero}: el símbolo '{simbolo}' no está en el alfabeto.")
        destinos = transiciones.setdefault((origen, simbolo), [])
        if destino not in destinos:
            destinos.append(destino)
    return transiciones


def leer_afnd(estados, alfabeto, inicial, finales, transiciones):
    """Valida los textos del editor y devuelve el autómata.

    Lanza ValueError con un mensaje en español si algo está mal.
    """
    lista_estados = _separar(estados)
    if not lista_estados:
        raise ValueError("Escriba al menos un estado.")
    lista_alfabeto = _leer_alfabeto(alfabeto)
    inicial = inicial.strip()
    if inicial not in lista_estados:
        raise ValueError(f"El estado inicial '{inicial}' no está en la lista de estados.")
    lista_finales = _separar(finales)
    for estado in lista_finales:
        if estado not in lista_estados:
            raise ValueError(f"El estado final '{estado}' no existe.")
    tabla = _leer_transiciones(transiciones, lista_estados, lista_alfabeto)
    return crear_automata(lista_estados, lista_alfabeto, inicial,
                          lista_finales, tabla)


def automata_a_textos(automata):
    """Hace lo contrario: automata -> (estados, alfabeto, inicial, finales, transiciones)."""
    lineas = []
    for (origen, simbolo), destinos in automata["transiciones"].items():
        for destino in destinos:
            lineas.append(f"{origen},{simbolo},{destino}")
    return (",".join(automata["estados"]), ",".join(automata["alfabeto"]),
            automata["inicial"], ",".join(automata["finales"]),
            "\n".join(lineas))
