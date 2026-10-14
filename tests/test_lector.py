"""Pruebas del lector del editor."""

import unittest

from src.lector import leer_afnd, automata_a_textos
from src.ejemplos import caso1


class TestLector(unittest.TestCase):
    def test_lee_caso1(self):
        afnd = leer_afnd("q0,q1,q2", "a,b", "q0", "q2",
                         "q0,a,q0\nq0,a,q1\nq1,b,q2")
        self.assertEqual(afnd["transiciones"][("q0", "a")], ["q0", "q1"])
        self.assertEqual(afnd["finales"], ["q2"])

    def test_ida_y_vuelta(self):
        textos = automata_a_textos(caso1())
        self.assertEqual(leer_afnd(*textos)["transiciones"], caso1()["transiciones"])

    def test_acepta_espacios_y_comentarios(self):
        afnd = leer_afnd("q0 q1", "a", "q0", "q1", "# comentario\nq0 a q1\n\n")
        self.assertEqual(afnd["transiciones"], {("q0", "a"): ["q1"]})

    def test_errores_claros(self):
        casos = [
            (("", "a", "q0", "", ""), "al menos un estado"),
            (("q0", "", "q0", "", ""), "alfabeto"),
            (("q0", "ab", "q0", "", ""), "un solo carácter"),
            (("q0", "+", "q0", "", ""), "no se puede usar"),
            (("q0", "a", "q9", "", ""), "inicial"),
            (("q0", "a", "q0", "q9", ""), "final"),
            (("q0", "a", "q0", "", "q0,a"), "Línea 1"),
            (("q0", "a", "q0", "", "q0,a,q5"), "'q5' no existe"),
            (("q0", "a", "q0", "", "q0,z,q0"), "'z' no está"),
        ]
        for argumentos, fragmento in casos:
            with self.assertRaises(ValueError) as contexto:
                leer_afnd(*argumentos)
            self.assertIn(fragmento, str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
