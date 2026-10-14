"""Pruebas de la lógica pura. Ejecutar con:  python -m unittest -v"""

import unittest

from src.modelo import crear_automata, acepta_cadena
from src.afnd_afd import convertir_afnd_a_afd
from src.af_er import afd_a_er, acepta_er
from src.verificador import verificar_equivalencia


def caso1():
    """Anexo A, caso 1: AFND -> AFD."""
    return crear_automata(
        ["q0", "q1", "q2"], ["a", "b"], "q0", ["q2"],
        {("q0", "a"): ["q0", "q1"], ("q1", "b"): ["q2"]})


def caso2():
    """Anexo A, caso 2: AF -> ER (es no determinista en q2 con y)."""
    return crear_automata(
        ["q0", "q1", "q2"], ["x", "y"], "q0", ["q1"],
        {("q0", "x"): ["q1"], ("q1", "x"): ["q2"],
         ("q2", "y"): ["q2", "q1"]})


class TestCaso1(unittest.TestCase):
    def setUp(self):
        self.tabla, self.pasos, self.afd = convertir_afnd_a_afd(caso1())

    def test_estados_del_afd(self):
        esperados = {"{q0}", "{q0,q1}", "{q2}", "∅"}
        self.assertEqual(set(self.afd["estados"]), esperados)
        self.assertEqual(self.afd["inicial"], "{q0}")

    def test_finales(self):
        self.assertEqual(self.afd["finales"], ["{q2}"])

    def test_transiciones(self):
        t = self.afd["transiciones"]
        self.assertEqual(t[("{q0}", "a")], ["{q0,q1}"])
        self.assertEqual(t[("{q0}", "b")], ["∅"])
        self.assertEqual(t[("{q0,q1}", "a")], ["{q0,q1}"])
        self.assertEqual(t[("{q0,q1}", "b")], ["{q2}"])
        self.assertEqual(t[("{q2}", "a")], ["∅"])
        self.assertEqual(t[("{q2}", "b")], ["∅"])
        self.assertEqual(t[("∅", "a")], ["∅"])
        self.assertEqual(t[("∅", "b")], ["∅"])

    def test_tabla_y_pasos(self):
        self.assertEqual(len(self.tabla), 4)
        self.assertEqual(len(self.pasos), 1 + 4 * 2)  # inicio + 4 filas x 2 símbolos

    def test_afd_igual_que_afnd(self):
        for cadena in ["", "a", "ab", "aab", "b", "abb", "aaab"]:
            self.assertEqual(acepta_cadena(caso1(), cadena),
                             acepta_cadena(self.afd, cadena))


class TestCaso2(unittest.TestCase):
    def test_er_esperada(self):
        _, er = afd_a_er(caso2())
        self.assertEqual(er, "x(xy*y)*")

    def test_cada_paso_tiene_regla(self):
        pasos, _ = afd_a_er(caso2())
        self.assertTrue(all(p["regla"] for p in pasos))
        reglas = " ".join(p["regla"] for p in pasos)
        self.assertIn("Bucle más salida", reglas)

    def test_regla_estado_final(self):
        # En el AFD del caso 1, {q2} solo es final: regla p = λ
        _, _, afd = convertir_afnd_a_afd(caso1())
        pasos, _ = afd_a_er(afd)
        reglas = " ".join(p["regla"] for p in pasos)
        self.assertIn("Estado final (p = λ)", reglas)

    def test_cadenas(self):
        _, er = afd_a_er(caso2())
        for cadena in ["x", "xxy", "xxyy", "xxyxy"]:
            self.assertTrue(acepta_er(er, cadena), cadena)
        for cadena in ["", "y", "xx", "xy"]:
            self.assertFalse(acepta_er(er, cadena), cadena)


class TestFlujoCompleto(unittest.TestCase):
    """AFND -> AFD -> ER y verificación."""

    def probar(self, afnd):
        _, _, afd = convertir_afnd_a_afd(afnd)
        _, er = afd_a_er(afd)
        return afd, er, verificar_equivalencia(afnd, afd, er, 6)

    def test_caso1(self):
        _, er, res = self.probar(caso1())
        self.assertEqual(er, "aa*b")
        self.assertTrue(res["equivalentes"])

    def test_caso2(self):
        _, _, res = self.probar(caso2())
        self.assertTrue(res["equivalentes"])
        self.assertEqual(res["total"], 127)  # 2^0 + ... + 2^6

    def test_er_incorrecta_muestra_diferencias(self):
        afnd = caso1()
        _, _, afd = convertir_afnd_a_afd(afnd)
        res = verificar_equivalencia(afnd, afd, "a*b", 6)
        self.assertFalse(res["equivalentes"])
        cadenas = [d[0] for d in res["diferencias"]]
        self.assertIn("b", cadenas)  # a*b acepta "b", el autómata no

    def test_n_minimo(self):
        afnd = caso1()
        _, _, afd = convertir_afnd_a_afd(afnd)
        with self.assertRaises(ValueError):
            verificar_equivalencia(afnd, afd, "aa*b", 3)


class TestCasosLimite(unittest.TestCase):
    def test_alfabeto_de_un_simbolo(self):
        afnd = crear_automata(["q0", "q1"], ["a"], "q0", ["q1"],
                              {("q0", "a"): ["q1"], ("q1", "a"): ["q1"]})
        _, _, afd = convertir_afnd_a_afd(afnd)
        self.assertNotIn("∅", afd["estados"])  # no hace falta pozo
        _, er = afd_a_er(afd)
        self.assertEqual(er, "aa*")

    def test_inicial_tambien_final(self):
        afnd = crear_automata(["q0"], ["a"], "q0", ["q0"],
                              {("q0", "a"): ["q0"]})
        _, er = afd_a_er(afnd)
        self.assertEqual(er, "a*")
        self.assertTrue(acepta_er(er, ""))

    def test_estado_inalcanzable(self):
        afnd = caso1()
        afnd["estados"].append("q9")
        afnd["transiciones"][("q9", "a")] = ["q2"]
        _, _, afd = convertir_afnd_a_afd(afnd)
        self.assertEqual(len(afd["estados"]), 4)  # q9 no aparece
        pasos, er = afd_a_er(afnd)
        # la ER puede escribirse distinto, pero debe ser equivalente
        res = verificar_equivalencia(caso1(), afd, er, 6)
        self.assertTrue(res["equivalentes"])
        self.assertNotIn("q9 =", " ".join(
            e for p in pasos for e in p["ecuaciones"]))

    def test_afnd_sin_finales_lenguaje_vacio(self):
        afnd = crear_automata(["q0"], ["a"], "q0", [], {("q0", "a"): ["q0"]})
        _, er = afd_a_er(afnd)
        self.assertEqual(er, "∅")
        self.assertFalse(acepta_er(er, ""))

    def test_afnd_sin_transiciones(self):
        afnd = crear_automata(["q0"], ["a", "b"], "q0", ["q0"], {})
        _, _, afd = convertir_afnd_a_afd(afnd)
        self.assertEqual(set(afd["estados"]), {"{q0}", "∅"})
        _, er = afd_a_er(afd)
        self.assertEqual(er, "λ")


if __name__ == "__main__":
    unittest.main()
