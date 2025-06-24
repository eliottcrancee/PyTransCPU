import sys
import os
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware import Component, HIGH, LOW, bus8bits
from src.memory import Register8Bits, ProgramCounter8Bits, Ram256bits
from src.arithmetic import ALU8Bits
from src.decoder import Decoder4to16


class SAP1(Component):
    """
    Simule le SAP-1 (Simple As Possible 1), un ordinateur simple.
    """

    def __init__(self):
        self.program_counter = ProgramCounter8Bits()
        self.instruction_register = Register8Bits()
        self.accumulator = Register8Bits()
        self.data_register = Register8Bits()
        self.adder = ALU8Bits()
        self.decoder = Decoder4to16()
        self.ram = Ram256bits()

        super().__init__(
            sub_components=[
                self.program_counter,
                self.instruction_register,
                self.accumulator,
                self.data_register,
                self.adder,
                self.decoder,
                self.ram,
            ]
        )

        self.clock_signal = LOW  # Signal d'horloge
        self._program_counter_data = (LOW,) * 8  # Valeur du compteur de programme
        self._program_counter_save = (
            LOW  # Signal de sauvegarde du compteur de programme
        )
        self._program_counter_load = (
            LOW  # Signal de chargement du compteur de programme
        )

    def clock_tick(self) -> int:
        self.clock_signal = 1 - self.clock_signal  # Inverse le signal d'horloge
        return self.clock_signal

    def execute_cycle(self, clock: int) -> None:
        """
        Exécute un cycle complet (fetch, decode, execute) du SAP-1.
        Utilise uniquement les connexions de composants.
        """
        # --- FETCH ---
        # Lire l'adresse du compteur de programme
        program_counter_output = self.program_counter(self._program_counter_data, clock, self._program_counter_save, self._program_counter_load)  # type: ignore

        # On se limite à 4 bits pour l'adresse du programme
        program_counter_output = program_counter_output[:4]

        # Charger l'instruction depuis la RAM
        instruction = self.ram(
            tuple([LOW for _ in range(8)]), program_counter_output, clock, HIGH, LOW  # type: ignore
        )

        # Charger l'instruction dans le registre d'instruction
        self.instruction_register(instruction, clock, clock, HIGH)  # type: ignore

        # --- DECODE ---
        # Décoder l'instruction
        decoded_instruction = self.decoder(self.instruction_register.state[:4])
