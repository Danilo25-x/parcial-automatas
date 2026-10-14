"""La ER no puede crecer sin control (error encontrado en la Fase 5)."""

import time
import unittest

from src.modelo import crear_automata
from src.afnd_afd import convertir_afnd_a_afd
from src.af_er import afd_a_er, ERDemasiadoGrande
from src.ejemplos import caso2


def quinto_desde_el_final(k):
    """AFND: 'el símbolo k desde el final es a'. Su AFD tiene 2^k estados."""
    estados = [f"q{i}" for i in range(k + 1)]
    trans = {("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0"]}
    for i in range(1, k):
        trans[(f"q{i}", "a")] = [f"q{i + 1}"]
        trans[(f"q{i}", "b")] = [f"q{i + 1}"]
    return crear_automata(estados, ["a", "b"], "q0", [f"q{k}"], trans)


class TestLimites(unittest.TestCase):
    def test_er_gigante_se_rechaza_rapido(self):
        _, _, afd = convertir_afnd_a_afd(quinto_desde_el_final(7))
        inicio = time.time()
        with self.assertRaises(ERDemasiadoGrande):
            afd_a_er(afd)
        self.assertLess(time.time() - inicio, 5)

    def test_casos_normales_no_se_afectan(self):
        _, er = afd_a_er(caso2())
        self.assertEqual(er, "x(xy*y)*")
        _, _, afd = convertir_afnd_a_afd(quinto_desde_el_final(3))
        afd_a_er(afd)  # 8 estados: sigue funcionando


if __name__ == "__main__":
    unittest.main()
