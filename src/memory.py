import sys
import os
from typing import Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, NMOS, HIGH, LOW, bus8bits
from src.latches import DFlipFlopSaveLoad
from src.arithmetic import Adder8Bits
from src.mux import Mux8bits2x1
from src.decoder import Decoder4to16
from src.gates import AndGate


class Register8Bits(Component):
    """
    Un registre 8 bits. Mémorise une valeur de 8 bits sur un front montant
    d'horloge, avec un signal de chargement pour écrire une nouvelle valeur.
    """

    def __init__(self):
        self.flip_flops = [DFlipFlopSaveLoad() for i in range(8)]
        super().__init__(sub_components=[*self.flip_flops])

    @property
    def state(self) -> Tuple[int, ...]:
        """
        Retourne l'état actuel du registre sous forme de tuple de bits.
        """
        return tuple([int(ff.q) for ff in self.flip_flops])

    def __call__(
        self, data_in: Tuple[int], clock: int, save: int, load: int
    ) -> Tuple[Union[int, None]]:
        assert len(data_in) == 8, "L'entrée doit être de 8 bits."

        output = tuple(
            self.flip_flops[i](data_in[i], clock, save, load)[0] for i in range(8)
        )

        return output

    def debug(self):
        """
        Teste le registre 8 bits avec différentes entrées et l'activation de l'écriture.
        """
        assert self((0, 0, 0, 0, 0, 0, 0, 0), 0, 0, 1) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 0, 0, 1) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 1, 0, 1) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 0, 0, 1) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 1, 1, 1) == (1, 0, 1, 0, 1, 0, 1, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 0, 0, 1) == (1, 0, 1, 0, 1, 0, 1, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 0, 1, 1) == (1, 0, 1, 0, 1, 0, 1, 0)  # type: ignore
        assert self((1, 0, 1, 0, 1, 0, 1, 0), 0, 1, 0) == tuple([None for _ in range(8)])  # type: ignore


class ProgramCounter8Bits(Component):
    """
    Un compteur de programme 8 bits. Incrémente sa valeur sur un front montant
    d'horloge avec un signal d'activation.
    """

    def __init__(self):
        self.register = Register8Bits()
        self.adder = Adder8Bits()
        self.mux8bits = Mux8bits2x1()
        self.nmoss = [NMOS() for _ in range(8)]  # Simule les NMOS pour la sortie
        super().__init__(
            sub_components=[self.register, self.adder, self.mux8bits, *self.nmoss]
        )
        self._output_state = (
            LOW,
            LOW,
            LOW,
            LOW,
            LOW,
            LOW,
            LOW,
            LOW,
        )

    @property
    def state(self) -> Tuple[int, ...]:
        """
        Retourne l'état actuel du compteur de programme sous forme de tuple de bits.
        """
        return self.register.state

    def __call__(
        self, data: Tuple[int], clock: int, save: int, load: int
    ) -> Tuple[Union[int, None], ...]:
        """
        Incrémente la valeur du compteur de programme sur un front montant, ou
        charge une nouvelle valeur si le signal de chargement est activé.
        """
        for _ in range(2):
            # Simule la stabilisation de l'état électrique

            added_output, _ = self.adder(
                self._output_state, (HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW)  # type: ignore
            )

            selected_signal = self.mux8bits(added_output, data, save)

            self._output_state = self.register(selected_signal, clock, clock, HIGH)

        output = tuple(self.nmoss[i](load, self._output_state[i]) for i in range(8))

        return output

    def debug(self):
        """
        Teste le compteur de programme 8 bits avec différentes entrées et l'activation de l'écriture.
        """
        assert self((0, 0, 0, 0, 0, 0, 0, 0), 0, 0, 1) == (0, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((0, 0, 0, 0, 0, 0, 0, 0), 1, 0, 1) == (1, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((0, 0, 0, 0, 0, 0, 0, 0), 0, 0, 1) == (1, 0, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((0, 0, 0, 1, 0, 1, 0, 0), 1, 1, 1) == (0, 1, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((0, 0, 0, 1, 0, 1, 0, 0), 0, 1, 1) == (0, 1, 0, 0, 0, 0, 0, 0)  # type: ignore
        assert self((0, 0, 0, 1, 0, 1, 0, 0), 1, 1, 1) == (0, 0, 0, 1, 0, 1, 0, 0)  # type: ignore
        assert self((0, 0, 0, 1, 0, 1, 0, 0), 0, 0, 0) == tuple([None for _ in range(8)])  # type: ignore
        assert self((0, 0, 0, 1, 0, 1, 0, 0), 1, 0, 0) == tuple([None for _ in range(8)])  # type: ignore


class Ram256bits(Component):
    """
    RAM 256 bits (16 x 8 bits) utilisant 16 registres 8 bits, un décodeur 4 vers 16,
    et un bus8bits pour la sortie. L'adresse sélectionne le registre à charger/lire.
    """

    def __init__(self):
        self.registers = [Register8Bits() for _ in range(16)]
        self.decoder = Decoder4to16()
        self.and_gates_save = [AndGate() for _ in range(16)]
        self.and_gates_load = [AndGate() for _ in range(16)]

        # Pour activer la sortie du bon registre
        super().__init__(
            sub_components=[
                *self.registers,
                self.decoder,
                *self.and_gates_save,
                *self.and_gates_load,
            ]
        )

    @property
    def state(self) -> Tuple[Tuple[int, ...], ...]:
        """
        Retourne l'état actuel de la RAM sous forme de tuple de tuples de bits.
        Chaque tuple représente l'état d'un registre 8 bits.
        """
        return tuple(register.state for register in self.registers)

    def __call__(
        self,
        data_in: Tuple[int, ...],  # 8 bits
        addr: Tuple[int, ...],  # 4 bits
        clock: int,
        save: int,
        load: int,
    ) -> Tuple[Union[int, None], ...]:

        assert len(data_in) == 8, "data_in doit être 8 bits"
        assert len(addr) == 4, "addr doit être 4 bits"

        # Décodeur 4 vers 16 pour sélectionner le registre à charger
        decoder_out = self.decoder(addr)  # type: ignore

        print(f"Decoder output: {decoder_out}")

        # Ecriture : chaque registre reçoit un signal de save individuel (save AND decoder_out[i])
        signals = tuple([self.registers[i](data_in, clock, self.and_gates_save[i](save, decoder_out[i]), self.and_gates_save[i](load, decoder_out[i])) for i in range(16)])  # type: ignore

        return bus8bits(*signals)

    def debug(self):
        """
        Teste la RAM 256 bits avec différentes adresses, écritures et lectures.
        """
        # Ecriture à l'adresse 0 : front descendant puis montant
        self((1, 0, 1, 0, 1, 0, 1, 0), (0, 0, 0, 0), 0, 1, 0)  # clock bas
        self((1, 0, 1, 0, 1, 0, 1, 0), (0, 0, 0, 0), 1, 1, 0)  # front montant

        # Lecture à l'adresse 0
        out0 = self((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0), 0, 0, 1)
        assert out0 == (1, 0, 1, 0, 1, 0, 1, 0), f"Lecture adresse 0: {out0}"

        # Ecriture à l'adresse 1
        self((0, 1, 0, 1, 0, 1, 0, 1), (1, 0, 0, 0), 0, 1, 0)  # clock bas
        self((0, 1, 0, 1, 0, 1, 0, 1), (1, 0, 0, 0), 1, 1, 0)  # front montant

        # Lecture à l'adresse 1
        out1 = self((0, 0, 0, 0, 0, 0, 0, 0), (1, 0, 0, 0), 0, 0, 1)
        assert out1 == (0, 1, 0, 1, 0, 1, 0, 1), f"Lecture adresse 1: {out1}"

        # Lecture à l'adresse 0 (doit rester inchangé)
        out0b = self((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0), 0, 0, 1)
        assert out0b == (1, 0, 1, 0, 1, 0, 1, 0), f"Lecture adresse 0 bis: {out0b}"

        # Lecture à une adresse non écrite (par défaut 0)
        out2 = self((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 1, 0), 0, 0, 1)
        assert out2 == (0, 0, 0, 0, 0, 0, 0, 0), f"Lecture adresse 2: {out2}"


if __name__ == "__main__":
    # Exécution des tests de débogage

    reg_8_bits = Register8Bits()
    print(reg_8_bits)
    reg_8_bits.debug()
    print(reg_8_bits.state)

    pc_8_bits = ProgramCounter8Bits()
    print(pc_8_bits)
    pc_8_bits.debug()
    print(pc_8_bits.state)

    ram_256_bits = Ram256bits()
    print(ram_256_bits)
    ram_256_bits.debug()
    for i, reg in enumerate(ram_256_bits.registers):
        print(f"Registre {i} état: {reg.state}")
