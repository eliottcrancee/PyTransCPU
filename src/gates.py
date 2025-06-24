import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, PMOS, NMOS, wire, VCC, GND


# --- Couche 0 : Abstraction des Portes Logiques (basées sur les transistors) ---


class NotGate(Component):
    """
    Simule une porte logique NOT (inverseur).
    Construite avec 1 PMOS et 1 NMOS.
    """

    def __init__(self):
        self.pmos = PMOS()
        self.nmos = NMOS()
        super().__init__(sub_components=[self.pmos, self.nmos])

    def __call__(self, a: int) -> int:
        """
        - Si a = LOW (0), le pmos est passant et connecte VCC à la sortie.
        - Si a = HIGH (1), le nmos est passant et connecte GND à la sortie.
        Le signal de sortie est le résultat du fil qui connecte les deux transistors.
        """
        output = wire(self.pmos(gate=a, source=VCC), self.nmos(gate=a, source=GND))
        assert (
            output is not None
        ), "La porte NOT doit toujours renvoyer un signal valide"
        return output

    def debug(self):
        """
        Teste la porte NOT avec les deux cas possibles.
        """
        assert self(0) == 1, "NOT(0) doit être 1"
        assert self(1) == 0, "NOT(1) doit être 0"


class NandGate(Component):
    """
    Simule une porte logique NAND à 2 entrées.
    Construite avec 2 PMOS en parallèle et 2 NMOS en série.
    """

    def __init__(self):
        self.pmos1 = PMOS()
        self.pmos2 = PMOS()
        self.nmos1 = NMOS()
        self.nmos2 = NMOS()
        super().__init__(
            sub_components=[self.pmos1, self.pmos2, self.nmos1, self.nmos2]
        )

    def __call__(self, a: int, b: int) -> int:
        """
        - La sortie est LOW (0) uniquement si A et B sont HIGH (1).
        - Sinon, la sortie est HIGH (1).
        """
        # PMOS en parallèle : si A ou B est LOW, la branche PMOS connecte à VCC
        pmos_output1 = self.pmos1(gate=a, source=VCC)
        pmos_output2 = self.pmos2(gate=b, source=VCC)

        # NMOS en série : il faut que A ET B soient HIGH pour connecter à GND
        # On connecte la sortie du premier nmos à la source du second.
        nmos_intermediate = self.nmos1(gate=a, source=GND)
        nmos_output = self.nmos2(gate=b, source=nmos_intermediate)

        # La sortie finale est le résultat de la connexion de toutes ces branches
        output = wire(pmos_output1, pmos_output2, nmos_output)
        assert (
            output is not None
        ), "La porte NAND doit toujours renvoyer un signal valide"
        return output

    def debug(self):
        """
        Teste la porte NAND avec tous les cas possibles.
        """
        assert self(0, 0) == 1, "NAND(0, 0) doit être 1"
        assert self(0, 1) == 1, "NAND(0, 1) doit être 1"
        assert self(1, 0) == 1, "NAND(1, 0) doit être 1"
        assert self(1, 1) == 0, "NAND(1, 1) doit être 0"


class NorGate(Component):
    """
    Simule une porte logique NOR à 2 entrées.
    Construite avec 2 PMOS en série et 2 NMOS en parallèle.
    """

    def __init__(self):
        self.pmos1 = PMOS()
        self.pmos2 = PMOS()
        self.nmos1 = NMOS()
        self.nmos2 = NMOS()
        super().__init__(
            sub_components=[self.pmos1, self.pmos2, self.nmos1, self.nmos2]
        )

    def __call__(self, a: int, b: int) -> int:
        """
        - La sortie est HIGH (1) uniquement si A et B sont LOW (0).
        - Sinon, la sortie est LOW (0).
        """
        # PMOS en série : il faut que A ET B soient LOW pour connecter à VCC
        pmos_intermediate = self.pmos1(gate=a, source=VCC)
        pmos_output = self.pmos2(gate=b, source=pmos_intermediate)

        # NMOS en parallèle : si A ou B est HIGH, la branche NMOS connecte à GND
        nmos_output1 = self.nmos1(gate=a, source=GND)
        nmos_output2 = self.nmos2(gate=b, source=GND)

        # La sortie finale est le résultat de la connexion de toutes ces branches
        output = wire(pmos_output, nmos_output1, nmos_output2)
        assert (
            output is not None
        ), "La porte NOR doit toujours renvoyer un signal valide"
        return output

    def debug(self):
        """
        Teste la porte NOR avec tous les cas possibles.
        """
        assert self(0, 0) == 1, "NOR(0, 0) doit être 1"
        assert self(0, 1) == 0, "NOR(0, 1) doit être 0"
        assert self(1, 0) == 0, "NOR(1, 0) doit être 0"
        assert self(1, 1) == 0, "NOR(1, 1) doit être 0"


# --- Couche 1 : Construire les autres portes à partir de NAND et NOT ---


class AndGate(Component):
    """
    Simule une porte logique AND à 2 entrées.
    Construite avec 1 NAND et 1 NOT.
    """

    def __init__(self):
        self.nand_gate = NandGate()
        self.not_gate = NotGate()
        super().__init__(sub_components=[self.nand_gate, self.not_gate])

    def __call__(self, a: int, b: int) -> int:
        return self.not_gate(self.nand_gate(a, b))

    def debug(self):
        """
        Teste la porte AND avec tous les cas possibles.
        """
        assert self(0, 0) == 0, "AND(0, 0) doit être 0"
        assert self(0, 1) == 0, "AND(0, 1) doit être 0"
        assert self(1, 0) == 0, "AND(1, 0) doit être 0"
        assert self(1, 1) == 1, "AND(1, 1) doit être 1"


class OrGate(Component):
    """
    Simule une porte logique OR à 2 entrées.
    Construite avec 1 NOR et 1 NOT.
    """

    def __init__(self):
        self.nor_gate = NorGate()
        self.not_gate = NotGate()
        super().__init__(sub_components=[self.nor_gate, self.not_gate])

    def __call__(self, a: int, b: int) -> int:
        return self.not_gate(self.nor_gate(a, b))

    def debug(self):
        """
        Teste la porte OR avec tous les cas possibles.
        """
        assert self(0, 0) == 0, "OR(0, 0) doit être 0"
        assert self(0, 1) == 1, "OR(0, 1) doit être 1"
        assert self(1, 0) == 1, "OR(1, 0) doit être 1"
        assert self(1, 1) == 1, "OR(1, 1) doit être 1"


class XorGate(Component):
    """
    Simule une porte logique XOR à 2 entrées.
    Construite avec 4 portes NAND.
    """

    def __init__(self):
        self.nand1 = NandGate()
        self.nand2 = NandGate()
        self.nand3 = NandGate()
        self.nand4 = NandGate()
        super().__init__(
            sub_components=[self.nand1, self.nand2, self.nand3, self.nand4]
        )

    def __call__(self, a: int, b: int) -> int:
        nand_ab = self.nand1(a, b)
        nand_a_nand_ab = self.nand2(a, nand_ab)
        nand_b_nand_ab = self.nand3(b, nand_ab)
        return self.nand4(nand_a_nand_ab, nand_b_nand_ab)

    def debug(self):
        """
        Teste la porte XOR avec tous les cas possibles.
        """
        assert self(0, 0) == 0, "XOR(0, 0) doit être 0"
        assert self(0, 1) == 1, "XOR(0, 1) doit être 1"
        assert self(1, 0) == 1, "XOR(1, 0) doit être 1"
        assert self(1, 1) == 0, "XOR(1, 1) doit être 0"


class XnorGate(Component):
    """
    Simule une porte logique XNOR à 2 entrées.
    Construite avec 1 XOR et 1 NOT.
    """

    def __init__(self):
        self.xor_gate = XorGate()
        self.not_gate = NotGate()
        super().__init__(sub_components=[self.xor_gate, self.not_gate])

    def __call__(self, a: int, b: int) -> int:
        return self.not_gate(self.xor_gate(a, b))

    def debug(self):
        """
        Teste la porte XNOR avec tous les cas possibles.
        """
        assert self(0, 0) == 1, "XNOR(0, 0) doit être 1"
        assert self(0, 1) == 0, "XNOR(0, 1) doit être 0"
        assert self(1, 0) == 0, "XNOR(1, 0) doit être 0"
        assert self(1, 1) == 1, "XNOR(1, 1) doit être 1"


if __name__ == "__main__":
    # Exécution des tests de débogage

    not_gate = NotGate()
    print(not_gate)
    not_gate.debug()

    nand_gate = NandGate()
    print(nand_gate)
    nand_gate.debug()

    nor_gate = NorGate()
    print(nor_gate)
    nor_gate.debug()

    and_gate = AndGate()
    print(and_gate)
    and_gate.debug()

    or_gate = OrGate()
    print(or_gate)
    or_gate.debug()

    xor_gate = XorGate()
    print(xor_gate)
    xor_gate.debug()

    xnor_gate = XnorGate()
    print(xnor_gate)
    xnor_gate.debug()
