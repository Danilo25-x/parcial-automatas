"""Verificador: compara AFND, AFD y ER con todas las cadenas hasta n."""

from itertools import product

from .modelo import acepta_cadena
from .af_er import acepta_er


def generar_cadenas(alfabeto, n):
    """Todas las cadenas del alfabeto de longitud 0 hasta n."""
    for largo in range(n + 1):
        for letras in product(alfabeto, repeat=largo):
            yield "".join(letras)


def verificar_equivalencia(afnd, afd, er, n=6):
    """Compara los tres reconocedores.

    Devuelve {"total", "equivalentes", "diferencias"}; cada diferencia es
    (cadena, acepta_afnd, acepta_afd, acepta_er).
    """
    if n < 6:
        raise ValueError("n debe ser al menos 6")
    diferencias = []
    total = 0
    for cadena in generar_cadenas(afnd["alfabeto"], n):
        total += 1
        r1 = acepta_cadena(afnd, cadena)
        r2 = acepta_cadena(afd, cadena)
        r3 = acepta_er(er, cadena)
        if not (r1 == r2 == r3):
            diferencias.append((cadena, r1, r2, r3))
    return {"total": total, "equivalentes": not diferencias,
            "diferencias": diferencias}
