"""Pruebas de las funciones de posición del dibujo (sin abrir ventanas)."""

import unittest

from src.dibujo import agrupar_aristas, calcular_layout, calcular_niveles
from src.afnd_afd import convertir_afnd_a_afd
from src.ejemplos import caso1


class TestDibujo(unittest.TestCase):
    def test_aristas_agrupadas(self):
        _, _, afd = convertir_afnd_a_afd(caso1())
        aristas = agrupar_aristas(afd)
        self.assertEqual(aristas[("∅", "∅")], ["a", "b"])        # un bucle con a,b
        self.assertEqual(aristas[("{q0}", "{q0,q1}")], ["a"])

    def test_niveles(self):
        nivel = calcular_niveles(caso1())
        self.assertEqual(nivel, {"q0": 0, "q1": 1, "q2": 2})

    def test_estado_inalcanzable_va_al_final(self):
        afnd = caso1()
        afnd["estados"].append("q9")
        self.assertEqual(calcular_niveles(afnd)["q9"], 3)

    def test_posiciones_distintas_y_dentro_de_la_ventana(self):
        _, _, afd = convertir_afnd_a_afd(caso1())
        pos = calcular_layout(afd, 800, 500)
        self.assertEqual(len(set(pos.values())), len(afd["estados"]))
        for x, y in pos.values():
            self.assertGreater(x, 0)
            self.assertGreater(y, 0)

    def test_inicial_a_la_izquierda(self):
        _, _, afd = convertir_afnd_a_afd(caso1())
        pos = calcular_layout(afd, 800, 500)
        self.assertEqual(min(pos.values())[0], pos[afd["inicial"]][0])


if __name__ == "__main__":
    unittest.main()
