from typing import Union, List, Tuple

# --- Nos constantes physiques ---

HIGH = 1  # Représente VCC (tension d'alimentation)
LOW = 0  # Représente GND (la masse)

VCC = HIGH  # Source de tension
GND = LOW  # Masse

# --- Nos composants de base ---


class Component:
    """
    Classe de base pour tous nos composants électroniques.
    Elle gère le comptage des transistors et des bits mémoire.
    """

    def __init__(self, sub_components: Union[List["Component"], None] = None):
        if sub_components:
            self.transistor_count = sum(c.transistor_count for c in sub_components)
            self.bit_count = sum(c.bit_count for c in sub_components)
        else:
            # Si pas de sous-composants, ce n'est pas un composant composite.
            # Le comptage se fera dans les classes filles.
            self.transistor_count = 0
            self.bit_count = 0

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__} (Transistors: {self.transistor_count}, Bits: {self.bit_count})"

    def debug(self):
        """
        Méthode de débogage pour tester le composant.
        """
        raise NotImplementedError


class PMOS(Component):
    """
    Simule un transistor PMOS.
    """

    def __init__(self):
        super().__init__()
        self.transistor_count = 1  # Un PMOS est un transistor.

    def __call__(
        self, gate: Union[int, None], source: Union[int, None]
    ) -> Union[int, None]:
        """
        Si la grille est à LOW, le transistor est passant (renvoie la source).
        Sinon, il est bloqué (haute impédance -> None).
        """
        if gate == LOW:
            return source
        return None


class NMOS(Component):
    """
    Simule un transistor NMOS.
    """

    def __init__(self):
        super().__init__()
        self.transistor_count = 1  # Un NMOS est un transistor.

    def __call__(
        self, gate: Union[int, None], source: Union[int, None]
    ) -> Union[int, None]:
        """
        Si la grille est à HIGH, le transistor est passant (renvoie la source).
        Sinon, il est bloqué (haute impédance -> None).
        """
        if gate == HIGH:
            return source
        return None


def wire(*signals: Union[int, None]) -> Union[int, None]:
    """
    Simule un fil connectant plusieurs sorties.
    Renvoie le premier signal qui n'est pas en haute impédance.
    En CMOS, il ne devrait y en avoir qu'un seul.
    """
    active_signals = set([s for s in signals if s is not None])

    if len(active_signals) > 1:
        raise ValueError(
            f"Conflit sur le fil : plusieurs signaux actifs détectés {active_signals}"
        )

    return list(active_signals)[0] if active_signals else None


def bus8bits(*signals: Tuple[Union[int, None], ...]) -> Tuple[Union[int, None], ...]:
    """
    Simule un bus de données de 8 bits.
    Renvoie un tuple de 8 signaux, chacun étant le premier signal non en haute impédance.
    """

    for signal in signals:
        if len(signal) != 8:
            raise ValueError("Chaque signal doit être un tuple de 8 bits.")

    return tuple(wire(*signal) for signal in zip(*signals))


if __name__ == "__main__":
    # Exécution des tests de débogage
    pmos = PMOS()
    nmos = NMOS()

    print(pmos)
    print(nmos)

    # Test PMOS
    assert pmos(LOW, VCC) == VCC, "PMOS(LOW, VCC) doit être VCC"
    assert pmos(HIGH, VCC) is None, "PMOS(HIGH, VCC) doit être None"

    # Test NMOS
    assert nmos(HIGH, GND) == GND, "NMOS(HIGH, GND) doit être GND"
    assert nmos(LOW, GND) is None, "NMOS(LOW, GND) doit être None"

    # Test du fil
    assert wire(pmos(LOW, VCC), nmos(LOW, GND)) == VCC, "Le fil doit renvoyer VCC"
    assert wire(pmos(HIGH, VCC), nmos(LOW, GND)) is None, "Le fil doit renvoyer None"

    # Test du bus 8 bits
    bus_result = bus8bits(
        (None, None, 1, None, None, 0, None, 0),
        (0, 1, None, 1, 0, None, 1, None),
        (None, None, None, None, None, None, None, None),
    )
    assert bus_result == (
        0,
        1,
        1,
        1,
        0,
        0,
        1,
        0,
    ), "Le bus doit renvoyer le bon résultat"
