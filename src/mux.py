import sys
import os
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component
from src.gates import NotGate, AndGate, OrGate


class Mux2x1(Component):
    """
    Simule un multiplexeur 2x1.
    Retourne a si select=0, sinon retourne b.
    Construite avec 1 NOT, 2 AND et 1 OR.
    """

    def __init__(self):
        self.not_s = NotGate()
        self.and_a = AndGate()
        self.and_b = AndGate()
        self.or_out = OrGate()
        super().__init__(
            sub_components=[
                NotGate(),
                AndGate(),
                AndGate(),
                OrGate(),
            ]
        )

    def __call__(self, a, b, select):
        s_inv = self.not_s(select)
        path_a = self.and_a(a, s_inv)
        path_b = self.and_b(b, select)
        return self.or_out(path_a, path_b)

    def debug(self):
        """
        Teste le multiplexeur 2x1 avec les combinaisons possibles.
        """

        assert self(0, 0, 0) == 0
        assert self(0, 1, 0) == 0
        assert self(1, 0, 0) == 1
        assert self(1, 1, 0) == 1
        assert self(0, 0, 1) == 0
        assert self(0, 1, 1) == 1
        assert self(1, 0, 1) == 0
        assert self(1, 1, 1) == 1


class Mux8bits2x1(Component):
    """
    Simule un multiplexeur 2x1 pour des entrées de 8 bits.
    Retourne a si select=0, sinon retourne b.
    Construite avec 8 Mux2x1.
    """

    def __init__(self):
        self.muxes = [Mux2x1() for _ in range(8)]
        super().__init__(sub_components=[*self.muxes])

    def __call__(self, a: Tuple[int], b: Tuple[int], select: int) -> Tuple[int]:
        assert len(a) == 8 and len(b) == 8, "Les entrées doivent être de 8 bits."
        return tuple(self.muxes[i](a[i], b[i], select) for i in range(8))

    def debug(self):
        """
        Teste le multiplexeur 8 bits 2x1 avec les combinaisons possibles.
        """
        assert self((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0), 0) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore # format: ignore
        assert self((1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1), 0) == (1, 1, 1, 1, 1, 1, 1, 1)  # type: ignore # format: ignore
        assert self((0, 0, 0, 0, 0, 0, 0, 0), (1, 1, 1, 1, 1, 1, 1, 1), 1) == (1, 1, 1, 1, 1, 1, 1, 1)  # type: ignore # format: ignore


if __name__ == "__main__":
    # Exécution des tests de débogage

    mux2x1 = Mux2x1()
    print(mux2x1)
    mux2x1.debug()

    mux8bits2x1 = Mux8bits2x1()
    print(mux8bits2x1)
    mux8bits2x1.debug()
