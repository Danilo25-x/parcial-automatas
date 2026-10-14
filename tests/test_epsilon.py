"""Bonus: AFND con transiciones ε."""

import random
import unittest

from src.modelo import crear_automata, clausura_epsilon, acepta_cadena, EPS
from src.afnd_afd import convertir_afnd_a_afd
from src.af_er import afd_a_er
from src.verificador import verificar_equivalencia
from src.lector import leer_afnd
from src.ejemplos import caso_epsilon


class TestEpsilon(unittest.TestCase):
    def test_clausura(self):
        afnd = caso_epsilon()
        self.assertEqual(clausura_epsilon(afnd, {"q0"}), {"q0", "q1"})
        self.assertEqual(clausura_epsilon(afnd, {"q2"}), {"q0", "q1", "q2"})  # q2→q0→q1
        self.assertEqual(clausura_epsilon(afnd, {"q1"}), {"q1"})

    def test_acepta_cadenas(self):
        afnd = caso_epsilon()                  # lenguaje (a*b)+
        for cadena in ["b", "ab", "aab", "bb", "abab"]:
            self.assertTrue(acepta_cadena(afnd, cadena), cadena)
        for cadena in ["", "a", "ba", "aba"]:
            self.assertFalse(acepta_cadena(afnd, cadena), cadena)

    def test_conversion_usa_clausura_en_inicial_y_en_cada_conjunto(self):
        _, pasos, afd = convertir_afnd_a_afd(caso_epsilon())
        self.assertEqual(afd["inicial"], "{q0,q1}")
        self.assertIn("Clausura-ε", pasos[0]["descripcion"])
        # desde {q0,q1} con b se llega a q2 y su clausura {q0,q1,q2}
        self.assertEqual(afd["transiciones"][("{q0,q1}", "b")], ["{q0,q1,q2}"])
        self.assertIn("{q0,q1,q2}", afd["finales"])

    def test_flujo_completo_equivalente(self):
        afnd = caso_epsilon()
        _, _, afd = convertir_afnd_a_afd(afnd)
        _, er = afd_a_er(afd)
        self.assertTrue(verificar_equivalencia(afnd, afd, er, 6)["equivalentes"])

    def test_er_directa_desde_afnd_con_epsilon(self):
        afnd = caso_epsilon()
        _, _, afd = convertir_afnd_a_afd(afnd)
        _, er = afd_a_er(afnd)                 # el Módulo 2 también acepta ε
        self.assertTrue(verificar_equivalencia(afnd, afd, er, 6)["equivalentes"])

    def test_lector_acepta_epsilon_y_alias(self):
        for escrito in ("ε", "eps", "epsilon"):
            afnd = leer_afnd("q0,q1", "a", "q0", "q1", f"q0,{escrito},q1")
            self.assertEqual(afnd["transiciones"], {("q0", EPS): ["q1"]})

    def test_aleatorios_con_epsilon(self):
        random.seed(5)
        for _ in range(200):
            n = random.randint(1, 4)
            estados = [f"q{i}" for i in range(n)]
            trans = {}
            for e in estados:
                for s in ["a", "b", EPS]:
                    ds = [d for d in estados if random.random() < 0.25]
                    if ds:
                        trans[(e, s)] = ds
            finales = [e for e in estados if random.random() < 0.4]
            afnd = crear_automata(estados, ["a", "b"], "q0", finales, trans)
            _, _, afd = convertir_afnd_a_afd(afnd)
            _, er = afd_a_er(afd)
            res = verificar_equivalencia(afnd, afd, er, 6)
            self.assertTrue(res["equivalentes"], (afnd, er, res["diferencias"][:2]))


if __name__ == "__main__":
    unittest.main()
