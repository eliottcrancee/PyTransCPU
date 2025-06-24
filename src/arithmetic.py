import sys
import os
from typing import Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, NMOS
from src.gates import (
    XorGate,
    AndGate,
    OrGate,
)


class HalfAdder(Component):
    """
    Simule un additionneur binaire de base (Half Adder).
    Construite avec 1 XOR et 1 AND.
    """

    def __init__(self):
        self.xor_gate = XorGate()
        self.and_gate = AndGate()
        super().__init__(sub_components=[self.xor_gate, self.and_gate])

    def __call__(self, a: int, b: int) -> Tuple[int, int]:
        """
        Retourne la somme et la retenue.
        - La somme est le résultat de l'opération XOR.
        - La retenue est le résultat de l'opération AND.
        """
        sum_result = self.xor_gate(a, b)
        carry_out = self.and_gate(a, b)
        return sum_result, carry_out

    def debug(self):
        """
        Teste l'additionneur avec les quatre combinaisons possibles.
        """
        assert self(0, 0) == (0, 0), "HalfAdder(0, 0) doit être (0, 0)"
        assert self(0, 1) == (1, 0), "HalfAdder(0, 1) doit être (1, 0)"
        assert self(1, 0) == (1, 0), "HalfAdder(1, 0) doit être (1, 0)"
        assert self(1, 1) == (0, 1), "HalfAdder(1, 1) doit être (0, 1)"


class FullAdder(Component):
    """
    Simule un additionneur binaire complet (Full Adder).
    Construite avec 2 Half Adders et 1 OR.
    """

    def __init__(self):
        self.half_adder1 = HalfAdder()
        self.half_adder2 = HalfAdder()
        self.or_gate = OrGate()
        super().__init__(
            sub_components=[self.half_adder1, self.half_adder2, self.or_gate]
        )

    def __call__(self, a: int, b: int, carry_in: int) -> Tuple[int, int]:
        """
        Retourne la somme et la retenue.
        - La somme est le résultat de l'opération XOR des deux bits d'entrée et de la retenue.
        - La retenue est le résultat de l'opération OR des deux retenues intermédiaires.
        """
        sum1, carry1 = self.half_adder1(a, b)
        sum_result, carry2 = self.half_adder2(sum1, carry_in)
        carry_out = self.or_gate(carry1, carry2)
        return sum_result, carry_out

    def debug(self):
        """
        Teste l'additionneur complet avec les huit combinaisons possibles.
        """
        assert self(0, 0, 0) == (0, 0), "FullAdder(0, 0, 0) doit être (0, 0)"
        assert self(0, 1, 0) == (1, 0), "FullAdder(0, 1, 0) doit être (1, 0)"
        assert self(1, 0, 0) == (1, 0), "FullAdder(1, 0, 0) doit être (1, 0)"
        assert self(1, 1, 0) == (0, 1), "FullAdder(1, 1, 0) doit être (0, 1)"
        assert self(0, 0, 1) == (1, 0), "FullAdder(0, 0, 1) doit être (1, 0)"
        assert self(0, 1, 1) == (0, 1), "FullAdder(0, 1, 1) doit être (0, 1)"
        assert self(1, 0, 1) == (0, 1), "FullAdder(1, 0, 1) doit être (0, 1)"
        assert self(1, 1, 1) == (1, 1), "FullAdder(1, 1, 1) doit être (1, 1)"


class Adder8Bits(Component):
    """
    Simule un additionneur binaire de 8 bits.
    Utilise 8 Full Adders en cascade.
    """

    def __init__(self):
        self.full_adders = [FullAdder() for _ in range(8)]
        super().__init__(sub_components=[*self.full_adders])

    def __call__(self, a: Tuple[int], b: Tuple[int]) -> Tuple[Tuple[int], int]:
        """
        Additionne deux nombres binaires de 8 bits.
        Retourne la somme et la retenue finale.
        """
        assert len(a) == 8 and len(b) == 8, "Les entrées doivent être de 8 bits."

        sum_bit1, carry = self.full_adders[0](a[0], b[0], 0)
        sum_bit2, carry = self.full_adders[1](a[1], b[1], carry)
        sum_bit3, carry = self.full_adders[2](a[2], b[2], carry)
        sum_bit4, carry = self.full_adders[3](a[3], b[3], carry)
        sum_bit5, carry = self.full_adders[4](a[4], b[4], carry)
        sum_bit6, carry = self.full_adders[5](a[5], b[5], carry)
        sum_bit7, carry = self.full_adders[6](a[6], b[6], carry)
        sum_bit8, carry = self.full_adders[7](a[7], b[7], carry)

        return (
            (
                sum_bit1,
                sum_bit2,
                sum_bit3,
                sum_bit4,
                sum_bit5,
                sum_bit6,
                sum_bit7,
                sum_bit8,
            ),
            carry,
        )

    def debug(self):
        """
        Teste l'additionneur 8 bits avec quelques exemples.
        """
        assert self((0, 0, 1, 0, 0, 0, 1, 0), (0, 0, 0, 1, 0, 1, 0, 0)) == (  # type: ignore
            (0, 0, 1, 1, 0, 1, 1, 0),
            0,
        )
        assert self((1, 0, 0, 0, 0, 0, 0, 0), (1, 1, 1, 1, 1, 1, 1, 1)) == (  # type: ignore
            (0, 0, 0, 0, 0, 0, 0, 0),
            1,
        )


class ALU8Bits(Component):
    """
    Simule une unité arithmétique et logique (ALU).
    Peut effectuer des opérations d'addition, de soustraction, de multiplication,
    de division, et des opérations logiques.
    """

    def __init__(self):
        self.adder = Adder8Bits()
        self.nmoss = [NMOS() for _ in range(8)]
        super().__init__(sub_components=[self.adder, *self.nmoss])

    def __call__(
        self, a: Tuple[int], b: Tuple[int], output_enable: int
    ) -> Tuple[Union[int, None], ...]:

        result, _ = self.adder(a, b)

        result = tuple(self.nmoss[i](output_enable, result[i]) for i in range(8))

        return result

    def debug(self):
        """
        Teste l'ALU avec quelques exemples d'addition.
        """
        assert self((0, 0, 1, 0, 0, 0, 1, 0), (0, 0, 0, 1, 0, 1, 0, 0), 1) == (0, 0, 1, 1, 0, 1, 1, 0)  # type: ignore
        assert self((1, 0, 0, 0, 0, 0, 0, 0), (1, 1, 1, 1, 1, 1, 1, 1), 0) == tuple([None for _ in range(8)])  # type: ignore


if __name__ == "__main__":
    # Exécution des tests de débogage

    half_adder = HalfAdder()
    print(half_adder)
    half_adder.debug()

    full_adder = FullAdder()
    print(full_adder)
    full_adder.debug()

    adder_8_bits = Adder8Bits()
    print(adder_8_bits)
    adder_8_bits.debug()

    alu_8_bits = ALU8Bits()
    print(alu_8_bits)
    alu_8_bits.debug()
