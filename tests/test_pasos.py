"""Pruebas del AFD parcial del paso a paso."""

import unittest

from src.afnd_afd import convertir_afnd_a_afd
from src.pasos import afd_parcial, vista_paso
from src.ejemplos import caso1


class TestPasos(unittest.TestCase):
    def setUp(self):
        _, self.pasos, self.afd = convertir_afnd_a_afd(caso1())

    def test_paso_cero_solo_inicial(self):
        parcial = afd_parcial(self.afd, self.pasos, 0)
        self.assertEqual(parcial["estados"], ["{q0}"])
        self.assertEqual(parcial["transiciones"], {})

    def test_paso_uno_agrega_una_transicion(self):
        parcial = afd_parcial(self.afd, self.pasos, 1)
        self.assertEqual(parcial["estados"], ["{q0}", "{q0,q1}"])
        self.assertEqual(parcial["transiciones"], {("{q0}", "a"): ["{q0,q1}"]})

    def test_ultimo_paso_es_el_afd_completo(self):
        parcial = afd_parcial(self.afd, self.pasos, len(self.pasos) - 1)
        self.assertEqual(set(parcial["estados"]), set(self.afd["estados"]))
        self.assertEqual(parcial["transiciones"], self.afd["transiciones"])
        self.assertEqual(parcial["finales"], self.afd["finales"])

    def test_vista_resalta_conjunto_y_flecha(self):
        _, resaltados, flecha = vista_paso(self.afd, self.pasos, 1)
        self.assertEqual(resaltados, ["{q0}"])
        self.assertEqual(flecha, ("{q0}", "a", "{q0,q1}"))
        _, _, sin_flecha = vista_paso(self.afd, self.pasos, 0)
        self.assertIsNone(sin_flecha)


if __name__ == "__main__":
    unittest.main()
