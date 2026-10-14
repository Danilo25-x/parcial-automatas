"""Módulo 2: de autómata finito a expresión regular.

Notación de la ER: unión '+', estrella '*', concatenación sin símbolo,
λ = cadena vacía, ∅ = lenguaje vacío.

Cada estado genera una ecuación:  p = r1·q1 + r2·q2 + ... + c
  - ecuación = {"terminos": {estado: coeficiente}, "const": c}
  - c es "λ" si p es final, y None si no (nada).
"""

import re

from .modelo import estados_alcanzables, estados_que_llegan_a_final

LAMBDA = "λ"
VACIO = "∅"


# ---------- Utilidades para armar expresiones regulares ----------

def _tiene_union(r):
    """True si r tiene un '+' fuera de paréntesis."""
    profundidad = 0
    for c in r:
        if c == "(":
            profundidad += 1
        elif c == ")":
            profundidad -= 1
        elif c == "+" and profundidad == 0:
            return True
    return False


def _es_atomico(r):
    """True si r se puede usar con '*' sin paréntesis: a, (ab), a*."""
    if len(r) == 1:
        return True
    if r.endswith("*") and _es_atomico(r[:-1]):
        return True
    if r[0] == "(" and r[-1] == ")":
        profundidad = 0
        for i, c in enumerate(r):
            if c == "(":
                profundidad += 1
            elif c == ")":
                profundidad -= 1
                if profundidad == 0 and i < len(r) - 1:
                    return False
        return True
    return False


def unir(a, b):
    """a + b (None significa 'nada')."""
    if a is None:
        return b
    if b is None:
        return a
    return a if a == b else a + "+" + b


def concatenar(a, b):
    """a seguido de b (λ no cambia nada; None anula)."""
    if a is None or b is None:
        return None
    if a == LAMBDA:
        return b
    if b == LAMBDA:
        return a
    if _tiene_union(a):
        a = "(" + a + ")"
    if _tiene_union(b):
        b = "(" + b + ")"
    return a + b


def estrella(r):
    """r* poniendo paréntesis solo si hace falta."""
    if r == LAMBDA:
        return LAMBDA
    if r.endswith("*") and _es_atomico(r):
        return r
    if _es_atomico(r):
        return r + "*"
    return "(" + r + ")*"


def texto_ecuacion(estado, ecuacion):
    """Escribe la ecuación en texto, ej.  q0 = a·q1 + b·q2 + λ"""
    partes = []
    for variable, coef in ecuacion["terminos"].items():
        if coef == LAMBDA:
            partes.append(variable)
        else:
            c = "(" + coef + ")" if _tiene_union(coef) else coef
            partes.append(c + "·" + variable)
    if ecuacion["const"] is not None:
        partes.append(ecuacion["const"])
    return f"{estado} = " + (" + ".join(partes) if partes else VACIO)


# ---------- Planteo, bucle y sustitución ----------

def _plantear(automata, estados):
    """Crea la ecuación de cada estado a partir de sus transiciones."""
    ecuaciones = {}
    for p in estados:
        terminos = {}
        cuenta = 0
        for simbolo in automata["alfabeto"]:
            for destino in automata["transiciones"].get((p, simbolo), []):
                if destino in estados:
                    terminos[destino] = unir(terminos.get(destino), simbolo)
                    cuenta += 1
        es_final = p in automata["finales"]
        ecuaciones[p] = {"terminos": terminos,
                         "const": LAMBDA if es_final else None}
        ecuaciones[p]["cuenta"] = cuenta
    return ecuaciones


def _regla_de_planteo(ec, estado):
    """Nombre de la regla y explicación para una ecuación recién planteada."""
    cuenta, final = ec["cuenta"], ec["const"] == LAMBDA
    if cuenta == 0 and final:
        return "Estado final (p = λ)", f"{estado} es final y no tiene salidas."
    if cuenta == 1:
        extra = " Además es final: se suma λ." if final else ""
        return "Transición simple (p = aq)", f"{estado} tiene una transición." + extra
    extra = " Además es final: se suma λ." if final else ""
    return ("Varias transiciones (p = aq + br)",
            f"{estado} tiene varias transiciones, se suman." + extra)


def _aplicar_bucle(ecuaciones, p, pasos, activos):
    """Si p = ap + resto, entonces p = a*·resto (regla del bucle)."""
    ec = ecuaciones[p]
    if p not in ec["terminos"]:
        return
    antes = texto_ecuacion(p, ec)
    r = ec["terminos"].pop(p)
    e = estrella(r)
    solo_lambda = not ec["terminos"] and ec["const"] == LAMBDA
    regla = ("Bucle (p = ap → a*)" if solo_lambda
             else "Bucle más salida (p = ap + bq → a*·bq)")
    for variable in ec["terminos"]:
        ec["terminos"][variable] = concatenar(e, ec["terminos"][variable])
    ec["const"] = concatenar(e, ec["const"])
    despues = texto_ecuacion(p, ec)
    pasos.append({
        "regla": regla,
        "descripcion": f"{antes}   ⟹   {despues}",
        "ecuaciones": [texto_ecuacion(q, ecuaciones[q]) for q in activos],
    })


def _sustituir(ecuaciones, p, pasos, activos):
    """Reemplaza p en las demás ecuaciones por su valor."""
    ec_p = ecuaciones[p]
    cambiadas = []
    for q in activos:
        ec_q = ecuaciones[q]
        if q == p or p not in ec_q["terminos"]:
            continue
        k = ec_q["terminos"].pop(p)
        for variable, coef in ec_p["terminos"].items():
            nuevo = concatenar(k, coef)
            ec_q["terminos"][variable] = unir(ec_q["terminos"].get(variable), nuevo)
        ec_q["const"] = unir(ec_q["const"], concatenar(k, ec_p["const"]))
        cambiadas.append(q)
    activos.remove(p)
    texto = (f"Se reemplaza {p} = {texto_ecuacion(p, ec_p).split(' = ', 1)[1]} "
             f"en: {', '.join(cambiadas) if cambiadas else 'ninguna ecuación'}.")
    pasos.append({
        "regla": "Sustitución",
        "descripcion": texto,
        "ecuaciones": [texto_ecuacion(q, ecuaciones[q]) for q in activos],
    })


# ---------- Función principal ----------

def afd_a_er(automata):
    """Obtiene la ER del lenguaje del autómata (AFD o AFND).

    Devuelve (pasos, er). Cada paso: {"regla", "descripcion", "ecuaciones"}.
    """
    pasos = []
    inicial = automata["inicial"]
    alcanzables = estados_alcanzables(automata)
    con_salida = estados_que_llegan_a_final(automata)

    inalcanzables = [e for e in automata["estados"] if e not in alcanzables]
    if inalcanzables:
        pasos.append({"regla": "Estado inalcanzable (se descarta)",
                      "descripcion": ", ".join(inalcanzables)
                      + " no se alcanza desde el inicial.",
                      "ecuaciones": []})
    if inicial not in con_salida:
        pasos.append({"regla": "Estado sin salida (p = ∅)",
                      "descripcion": "Desde el inicial no se llega a ningún final.",
                      "ecuaciones": [f"{inicial} = ∅"]})
        return pasos, VACIO
    muertos = [e for e in automata["estados"]
               if e in alcanzables and e not in con_salida]
    if muertos:
        pasos.append({"regla": "Estado sin salida (p = ∅)",
                      "descripcion": ", ".join(muertos)
                      + " no llega(n) a un final: vale ∅ y se quita(n) (estado pozo).",
                      "ecuaciones": []})

    activos = [e for e in automata["estados"]
               if e in alcanzables and e in con_salida]
    ecuaciones = _plantear(automata, set(activos))

    # 1) Planteo: una ecuación por estado, con su regla
    for i, p in enumerate(activos):
        regla, explicacion = _regla_de_planteo(ecuaciones[p], p)
        pasos.append({
            "regla": regla, "descripcion": explicacion,
            "ecuaciones": [texto_ecuacion(q, ecuaciones[q]) for q in activos[:i + 1]],
        })

    # 2) Eliminar los estados de atrás hacia adelante (el inicial queda al final)
    for p in [e for e in reversed(activos) if e != inicial]:
        _aplicar_bucle(ecuaciones, p, pasos, activos)
        _sustituir(ecuaciones, p, pasos, activos)

    # 3) Bucle del estado inicial y resultado
    _aplicar_bucle(ecuaciones, inicial, pasos, activos)
    er = ecuaciones[inicial]["const"]
    pasos.append({"regla": "Resultado",
                  "descripcion": f"La ER del lenguaje es: {er}",
                  "ecuaciones": [texto_ecuacion(inicial, ecuaciones[inicial])]})
    return pasos, er


# ---------- Probar cadenas contra una ER ----------

def er_a_regex(er):
    """Traduce nuestra notación a una regex de Python (+ → |, λ → vacío)."""
    if er == VACIO:
        return "(?!)"  # nunca coincide
    salida = []
    for c in er:
        if c == "+":
            salida.append("|")
        elif c == LAMBDA:
            salida.append("(?:)")
        elif c in "()*":
            salida.append(c)
        else:
            salida.append(re.escape(c))
    return "(?:" + "".join(salida) + ")"


def acepta_er(er, cadena):
    """True si la cadena completa pertenece al lenguaje de la ER."""
    return re.fullmatch(er_a_regex(er), cadena) is not None
