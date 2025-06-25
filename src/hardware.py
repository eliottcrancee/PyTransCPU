from typing import Union, List, Tuple, Callable, Any, Literal, TypeAlias, Set, cast


# --- Nos constantes physiques ---

HIGH = 1  # Représente VCC (tension d'alimentation)
LOW = 0  # Représente GND (la masse)

VCC = HIGH  # Source de tension
GND = LOW  # Masse

# --- Nos composants de base ---


Bit: TypeAlias = Literal[0, 1]
Signal: TypeAlias = Union[
    Bit, None
]  # Un signal peut être un bit ou None (haute impédance)
Signal8: TypeAlias = Tuple[
    Signal, Signal, Signal, Signal, Signal, Signal, Signal, Signal
]


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

    def __call__(self, gate: Signal, source: Signal) -> Signal:
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

    def __call__(self, gate: Signal, source: Signal) -> Signal:
        """
        Si la grille est à HIGH, le transistor est passant (renvoie la source).
        Sinon, il est bloqué (haute impédance -> None).
        """
        if gate == HIGH:
            return source
        return None


def wire(*signals: Signal) -> Signal:
    """
    Simule un fil connectant plusieurs sorties.
    Renvoie le premier signal qui n'est pas en haute impédance.
    En CMOS, il ne devrait y en avoir qu'un seul.
    """
    active_signals: Set[Bit] = {cast(Bit, s) for s in signals if s is not None}

    if len(active_signals) > 1:
        raise ValueError(
            f"Conflit sur le fil : plusieurs signaux actifs détectés {active_signals}"
        )

    if len(active_signals) == 0:
        return None

    else:
        return active_signals.pop()


def bus8bits(*signals: Signal8) -> Signal8:
    """
    Simule un bus de données de 8 bits.
    Renvoie un tuple de 8 signaux, chacun étant le premier signal non en haute impédance.
    """

    s0, s1, s2, s3, s4, s5, s6, s7 = zip(*signals)

    return (
        wire(*s0),
        wire(*s1),
        wire(*s2),
        wire(*s3),
        wire(*s4),
        wire(*s5),
        wire(*s6),
        wire(*s7),
    )


def stabilize(
    get_state: Callable[[], Tuple[Any, ...]],
    update_state: Callable[[], None],
    max_iter: int = 3,
) -> bool:
    """
    Simule la stabilisation électrique d'un circuit rétro-bouclé.

    Args:
        get_state: fonction qui retourne les états à surveiller (ex: [q, q̅]).
        update_state: fonction qui met à jour les états à chaque itération logique.
        max_iter: nombre maximum d'itérations de stabilisation (évite les boucles infinies).

    Returns:
        True si le circuit s'est stabilisé (état constant atteint), False sinon.
    """
    for _ in range(max_iter):
        prev = get_state()
        update_state()
        if get_state() == prev:
            return True
    print("⚠️ Avertissement : le circuit ne s'est pas stabilisé.")
    return False


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
