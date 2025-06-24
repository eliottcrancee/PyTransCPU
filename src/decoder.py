import sys
import os
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, HIGH, LOW
from src.gates import AndGate, NotGate


class Decoder2to4(Component):
    """
    Simule un décodeur 2 vers 4.
    Prend en entrée 2 bits et active l'une des 4 sorties.
    """

    def __init__(self):
        self.and_gate1 = AndGate()
        self.and_gate2 = AndGate()
        self.and_gate3 = AndGate()
        self.and_gate4 = AndGate()
        self.not_gate1 = NotGate()
        self.not_gate2 = NotGate()
        super().__init__(
            sub_components=[
                self.and_gate1,
                self.and_gate2,
                self.and_gate3,
                self.and_gate4,
                self.not_gate1,
                self.not_gate2,
            ]
        )

    def __call__(self, a: int, b: int) -> Tuple[int, int, int, int]:

        a_not = self.not_gate1(a)
        b_not = self.not_gate2(b)
        output1 = self.and_gate1(a_not, b_not)
        output2 = self.and_gate2(a_not, b)
        output3 = self.and_gate3(a, b_not)
        output4 = self.and_gate4(a, b)

        return output1, output2, output3, output4

    def debug(self):
        """
        Teste le décodeur avec les combinaisons possibles.
        """
        assert self(0, 0) == (HIGH, LOW, LOW, LOW)
        assert self(0, 1) == (LOW, HIGH, LOW, LOW)
        assert self(1, 0) == (LOW, LOW, HIGH, LOW)
        assert self(1, 1) == (LOW, LOW, LOW, HIGH)


class Decoder4to16(Component):
    """
    Simule un décodeur 4 vers 16.
    Prend en entrée 4 bits et active l'une des 16 sorties.
    """

    def __init__(self):
        self.decoder2to4_1 = Decoder2to4()
        self.decoder2to4_2 = Decoder2to4()
        self.and_gates = [AndGate() for _ in range(16)]
        self.not_gates = [NotGate() for _ in range(4)]
        super().__init__(sub_components=[self.decoder2to4_1, self.decoder2to4_2])

    def __call__(self, signal: Tuple[int]) -> Tuple[int, ...]:

        assert len(signal) == 4, "Le signal doit être de 4 bits"

        d, c, b, a = signal

        output_1 = self.decoder2to4_1(a, b)
        output_2 = self.decoder2to4_2(c, d)
        o1_0, o1_1, o1_2, o1_3 = output_1
        o2_0, o2_1, o2_2, o2_3 = output_2

        out0 = self.and_gates[0](o1_0, o2_0)
        out1 = self.and_gates[1](o1_0, o2_1)
        out2 = self.and_gates[2](o1_0, o2_2)
        out3 = self.and_gates[3](o1_0, o2_3)
        out4 = self.and_gates[4](o1_1, o2_0)
        out5 = self.and_gates[5](o1_1, o2_1)
        out6 = self.and_gates[6](o1_1, o2_2)
        out7 = self.and_gates[7](o1_1, o2_3)
        out8 = self.and_gates[8](o1_2, o2_0)
        out9 = self.and_gates[9](o1_2, o2_1)
        out10 = self.and_gates[10](o1_2, o2_2)
        out11 = self.and_gates[11](o1_2, o2_3)
        out12 = self.and_gates[12](o1_3, o2_0)
        out13 = self.and_gates[13](o1_3, o2_1)
        out14 = self.and_gates[14](o1_3, o2_2)
        out15 = self.and_gates[15](o1_3, o2_3)

        return (
            out0,
            out1,
            out2,
            out3,
            out4,
            out5,
            out6,
            out7,
            out8,
            out9,
            out10,
            out11,
            out12,
            out13,
            out14,
            out15,
        )

    def debug(self):
        """
        Teste le décodeur avec toutes les combinaisons possibles.
        """
        for d in (0, 1):
            for c in (0, 1):
                for b in (0, 1):
                    for a in (0, 1):
                        outputs = self((a, b, c, d))  # type: ignore
                        idx = a | (b << 1) | (c << 2) | (d << 3)
                        for i, val in enumerate(outputs):
                            if i == idx:
                                assert (
                                    val == HIGH
                                ), f"Erreur: entrée {a}{b}{c}{d}, sortie {i} devrait être HIGH"
                            else:
                                assert (
                                    val == LOW
                                ), f"Erreur: entrée {a}{b}{c}{d}, sortie {i} devrait être LOW"


if __name__ == "__main__":
    # Exécution des tests de débogage

    decoder2to4 = Decoder2to4()
    print(decoder2to4)
    decoder2to4.debug()

    decoder4to16 = Decoder4to16()
    print(decoder4to16)
    decoder4to16.debug()
