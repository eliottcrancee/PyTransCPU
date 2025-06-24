import sys
import os
from typing import Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, HIGH, LOW, NMOS
from src.gates import NorGate, AndGate, NotGate
from src.mux import Mux2x1


class SRLatch(Component):
    """
    Simule un latch SR (Set-Reset).
    Construite avec 2 NOR.
    """

    def __init__(self):
        self.nor1 = NorGate()
        self.nor2 = NorGate()
        super().__init__(sub_components=[self.nor1, self.nor2])
        self.bit_count = 1  # Un latch SR stocke un bit.
        self.q = LOW
        self.q_bar = HIGH

    def __call__(self, set_signal: int, reset_signal: int) -> Tuple[int, int]:
        """
        Met à jour l'état du latch SR en fonction des signaux d'entrée.
        Simule une stabilisation de l'état du latch.
        """
        assert (
            set_signal == LOW or reset_signal == LOW
        ), "Les signaux SET et RESET ne peuvent pas être HIGH en même temps."

        for _ in range(2):
            # Simule la stabilisation de l'état électrique
            self.q_bar = self.nor1(set_signal, self.q)
            self.q = self.nor2(reset_signal, self.q_bar)

        return self.q, self.q_bar

    def debug(self):
        """
        Teste le latch SR avec les combinaisons possibles.
        """
        assert self(0, 0) == (0, 1)
        assert self(1, 0) == (1, 0)
        assert self(0, 0) == (1, 0)
        assert self(0, 1) == (0, 1)


class DLatch(Component):
    """
    Simule un latch D (Data).
    Construite avec 1 SRLatch.
    """

    def __init__(self):
        self.sr_latch = SRLatch()
        self.not_gate = NotGate()
        self.and_gate1 = AndGate()
        self.and_gate2 = AndGate()
        super().__init__(
            sub_components=[
                self.sr_latch,
                self.not_gate,
                self.and_gate1,
                self.and_gate2,
            ]
        )

    @property
    def q(self) -> int:
        return self.sr_latch.q

    @property
    def q_bar(self) -> int:
        return self.sr_latch.q_bar

    def __call__(self, data: int, enable: int) -> Tuple[int, int]:
        """
        Met à jour l'état du latch D en fonction des signaux d'entrée.
        Si enable est HIGH, le latch prend la valeur de data.
        Si enable est LOW, le latch conserve sa valeur précédente.
        """
        set_signal = self.and_gate1(data, enable)
        reset_signal = self.and_gate2(self.not_gate(data), enable)

        return self.sr_latch(set_signal, reset_signal)

    def debug(self):
        """
        Teste le latch D avec les combinaisons possibles.
        """
        assert self(0, 0) == (0, 1)
        assert self(1, 0) == (0, 1)
        assert self(0, 1) == (0, 1)
        assert self(1, 1) == (1, 0)
        assert self(0, 0) == (1, 0)
        assert self(1, 0) == (1, 0)
        assert self(1, 1) == (1, 0)
        assert self(0, 1) == (0, 1)


class DFlipFlop(Component):
    """
    Simule un flip-flop D (Data).
    Construite avec 2 DLatch.
    """

    def __init__(self):
        self.master_d_latch = DLatch()
        self.slave_d_latch = DLatch()
        self.not_gate = NotGate()
        super().__init__(
            sub_components=[self.master_d_latch, self.slave_d_latch, self.not_gate]
        )
        self.bit_count = 1  # Un flip-flop D stocke un bit.

    @property
    def q(self) -> int:
        return self.slave_d_latch.q

    @property
    def q_bar(self) -> int:
        return self.slave_d_latch.q_bar

    def __call__(self, data: int, clock: int) -> Tuple[int, int]:
        """
        Met à jour l'état du flip-flop D en fonction des signaux d'entrée.
        Le flip-flop prend la valeur de data à chaque front montant du clock.
        """

        master_output, _ = self.master_d_latch(data, self.not_gate(clock))
        q, q_bar = self.slave_d_latch(master_output, clock)

        return q, q_bar

    def debug(self):
        """
        Teste le flip-flop D avec les combinaisons possibles.
        """
        assert self(0, 0) == (0, 1)
        assert self(1, 0) == (0, 1)
        assert self(0, 0) == (0, 1)
        assert self(0, 1) == (0, 1)
        assert self(1, 1) == (0, 1)
        assert self(1, 0) == (0, 1)
        assert self(1, 1) == (1, 0)
        assert self(0, 1) == (1, 0)
        assert self(0, 0) == (1, 0)
        assert self(0, 1) == (0, 1)


class DFlipFlopSave(Component):
    """
    Simule un flip-flop D avec un signal de sauvegarde.
    """

    def __init__(self):
        self.master_d_latch = DLatch()
        self.slave_d_latch = DLatch()
        self.not_gate = NotGate()
        self.mux = Mux2x1()
        super().__init__(
            sub_components=[
                self.master_d_latch,
                self.slave_d_latch,
                self.not_gate,
                self.mux,
            ]
        )
        self.bit_count = 1  # Un flip-flop D stocke un bit.*

    @property
    def q(self) -> int:
        return self.slave_d_latch.q

    @property
    def q_bar(self) -> int:
        return self.slave_d_latch.q_bar

    def __call__(self, data: int, clock: int, save: int) -> Tuple[int, int]:
        """
        Met à jour l'état du flip-flop D avec un signal de sauvegarde.
        Si save est HIGH, le flip-flop prend la valeur de data.
        Si save est LOW, le flip-flop conserve sa valeur précédente.
        """

        master_output, _ = self.master_d_latch(data, self.not_gate(clock))
        selected_input = self.mux(self.slave_d_latch.q, master_output, save)
        q, q_bar = self.slave_d_latch(selected_input, clock)

        return q, q_bar

    def debug(self):
        """
        Teste le flip-flop D avec un signal de sauvegarde.
        """
        assert self(0, 0, 0) == (0, 1)
        assert self(1, 0, 0) == (0, 1)
        assert self(0, 0, 0) == (0, 1)
        assert self(0, 1, 0) == (0, 1)
        assert self(1, 1, 0) == (0, 1)
        assert self(1, 0, 0) == (0, 1)
        assert self(1, 1, 0) == (0, 1)
        assert self(0, 1, 0) == (0, 1)
        assert self(0, 0, 0) == (0, 1)
        assert self(0, 1, 0) == (0, 1)

        assert self(0, 0, 1) == (0, 1)
        assert self(1, 0, 1) == (0, 1)
        assert self(0, 0, 1) == (0, 1)
        assert self(0, 1, 1) == (0, 1)
        assert self(1, 1, 1) == (0, 1)
        assert self(1, 0, 1) == (0, 1)
        assert self(1, 1, 1) == (1, 0)
        assert self(0, 1, 1) == (1, 0)
        assert self(0, 0, 1) == (1, 0)
        assert self(0, 1, 1) == (0, 1)


class DFlipFlopSaveLoad(Component):
    """
    Simule un flip-flop D avec un signal de sauvegarde et de chargement.
    """

    def __init__(self):
        self.d_flip_flop_save = DFlipFlopSave()
        self.nmos1 = NMOS()
        self.nmos2 = NMOS()
        super().__init__(
            sub_components=[
                self.d_flip_flop_save,
                self.nmos1,
                self.nmos2,
            ]
        )

    @property
    def q(self) -> int:
        return self.d_flip_flop_save.q

    @property
    def q_bar(self) -> int:
        return self.d_flip_flop_save.q_bar

    def __call__(
        self, data: int, clock: int, save: int, load: int
    ) -> Tuple[Union[int, None], Union[int, None]]:
        """
        Met à jour l'état du flip-flop D avec un signal de sauvegarde et de chargement.
        """

        q, q_bar = self.d_flip_flop_save(data, clock, save)

        return self.nmos1(load, q), self.nmos2(load, q_bar)

    def debug(self):
        """
        Teste le flip-flop D avec un signal de sauvegarde et de chargement.
        """
        assert self(0, 0, 0, 0) == (None, None)
        assert self(1, 0, 0, 1) == (0, 1)


if __name__ == "__main__":
    # Exécution des tests de débogage

    sr_latch = SRLatch()
    print(sr_latch)
    sr_latch.debug()

    d_latch = DLatch()
    print(d_latch)
    d_latch.debug()

    d_flip_flop = DFlipFlop()
    print(d_flip_flop)
    d_flip_flop.debug()

    d_flip_flop_save = DFlipFlopSave()
    print(d_flip_flop_save)
    d_flip_flop_save.debug()

    d_flip_flop_save_load = DFlipFlopSaveLoad()
    print(d_flip_flop_save_load)
    d_flip_flop_save_load.debug()
