"""Autómatas de ejemplo (Anexo A del parcial)."""

from .modelo import crear_automata


def caso1():
    """Caso 1 (AFND → AFD): q0-a->q0, q0-a->q1, q1-b->q2, final q2."""
    return crear_automata(
        ["q0", "q1", "q2"], ["a", "b"], "q0", ["q2"],
        {("q0", "a"): ["q0", "q1"], ("q1", "b"): ["q2"]})


def caso2():
    """Caso 2 (AF → ER): q0-x->q1, q1-x->q2, q2-y->q2, q2-y->q1, final q1."""
    return crear_automata(
        ["q0", "q1", "q2"], ["x", "y"], "q0", ["q1"],
        {("q0", "x"): ["q1"], ("q1", "x"): ["q2"],
         ("q2", "y"): ["q2", "q1"]})


# nombre que se muestra en la lista -> función que crea el autómata
EJEMPLOS = {
    "Caso 1 · AFND → AFD": caso1,
    "Caso 2 · AF → ER": caso2,
}
