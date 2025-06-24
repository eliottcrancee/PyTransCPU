### Les Règles du Jeu (Notre Contrat de Simulation)

1.  **Les États Physiques :** On ne manipule que deux états, représentant une tension haute et une tension basse. On les modélisera en Python par des booléens, c'est le plus simple.
    ```python
    HIGH = True  # Représente VCC (tension d'alimentation)
    LOW = False  # Représente GND (la masse)
    ```
2.  **Le Composant de Base :** Le transistor. On n'a le droit d'utiliser que des fonctions modélisant des transistors NMOS et PMOS. Toute autre logique (`if`, `and`, `or`, `not` de Python) est interdite *dans la création de nos composants logiques*.
3.  **Le Câblage :** L'assignation `variable = resultat_fonction()` est autorisée. Elle ne représente pas un stockage de donnée au sens d'un registre, mais simplement un "fil" qui connecte la sortie d'un composant à l'entrée d'un autre.
4.  **État et Mémoire :** C'est le point le plus délicat. Un CPU a besoin d'état (registres, PC). Pour simuler un composant qui a un état (comme une bascule), on devra modéliser le temps. On le fera en passant l'état précédent du composant en argument de la fonction, qui retournera le nouvel état. La boucle principale de notre simulation (l'horloge) se chargera de maintenir cet état d'un cycle à l'autre.
5.  **L'Horloge :** L'horloge sera une simple boucle `for` ou `while` en Python. C'est le "moteur" externe de notre simulation, qui fait avancer le temps discret.

En logique CMOS (Complementary Metal-Oxide-Semiconductor), on utilise deux types de transistors qui fonctionnent de manière opposée.

*   **Transistor NMOS :** Quand sa grille (gate) est à `HIGH`, il laisse passer le courant entre sa source et son drain. C'est comme un interrupteur fermé. Quand la grille est à `LOW`, il bloque le courant (interrupteur ouvert).
*   **Transistor PMOS :** C'est l'inverse. Quand sa grille est à `LOW`, il laisse passer le courant. Quand la grille est à `HIGH`, il bloque.

On peut les modéliser comme des fonctions Python. Pour simuler l'état "déconnecté" (haute impédance), on utilisera `None`.

```python
# --- Nos constantes physiques ---
HIGH = True
LOW = False
VCC = HIGH  # Source de tension
GND = LOW   # Masse

# --- Nos composants de base ---

def pmos(gate, source):
    """
    Simule un transistor PMOS.
    Si la grille est à LOW, le transistor est passant (renvoie la source).
    Sinon, il est bloqué (haute impédance -> None).
    """
    if gate == LOW:
        return source
    return None

def nmos(gate, source):
    """
    Simule un transistor NMOS.
    Si la grille est à HIGH, le transistor est passant (renvoie la source).
    Sinon, il est bloqué (haute impédance -> None).
    """
    if gate == HIGH:
        return source
    return None
```

Pour connecter la sortie de plusieurs transistors, on a besoin d'un "fil". Si un transistor est passant vers VCC et l'autre vers GND, il y a un court-circuit. Notre modèle ne gérera pas ça, mais la logique CMOS est conçue pour l'éviter. Un seul des chemins (vers VCC ou vers GND) doit être actif à la fois.

```python
def wire(*signals):
    """
    Simule un fil connectant plusieurs sorties.
    Renvoie le premier signal qui n'est pas en haute impédance.
    En CMOS, il ne devrait y en avoir qu'un seul.
    """
    for signal in signals:
        if signal is not None:
            return signal
    return None # État flottant, ce qui est une erreur de conception en CMOS
```

---

### Étape 2 : Les Portes Logiques Fondamentales (NOT, NAND, NOR)

Avec nos transistors, on peut maintenant construire nos premières portes. C'est la magie du CMOS !

#### Porte NOT (Inverseur)

C'est la plus simple. Un PMOS connecte la sortie à VCC, un NMOS la connecte à GND. Leurs grilles sont connectées ensemble à l'entrée `a`.

*   Si `a` est `HIGH` : le PMOS est bloqué, le NMOS est passant. La sortie est connectée à GND -> `LOW`.
*   Si `a` est `LOW` : le PMOS est passant, le NMOS est bloqué. La sortie est connectée à VCC -> `HIGH`.

```python
def not_gate(a):
    """Porte NON, construite avec des transistors."""
    # Le réseau "pull-up" (vers VCC) est fait de PMOS
    pull_up = pmos(a, VCC)
    # Le réseau "pull-down" (vers GND) est fait de NMOS
    pull_down = nmos(a, GND)
    
    return wire(pull_up, pull_down)

# Testons !
print(f"NOT(LOW)  -> {not_gate(LOW)}")   # Attendu: True (HIGH)
print(f"NOT(HIGH) -> {not_gate(HIGH)}")  # Attendu: False (LOW)
```

#### Porte NAND (NON-ET)

*   **Réseau Pull-up (PMOS) :** Deux PMOS en parallèle. Si `a` OU `b` est `LOW`, la sortie est `HIGH`.
*   **Réseau Pull-down (NMOS) :** Deux NMOS en série. Si `a` ET `b` sont `HIGH`, la sortie est `LOW`.

```python
def nand_gate(a, b):
    """Porte NON-ET, construite avec des transistors."""
    # Pull-up : PMOS en parallèle
    pull_up = wire(pmos(a, VCC), pmos(b, VCC))
    
    # Pull-down : NMOS en série
    # La sortie du premier NMOS est la source du second
    gnd_connection = nmos(a, GND)
    pull_down = nmos(b, gnd_connection)
    
    return wire(pull_up, pull_down)

# Testons !
print("\n--- Porte NAND ---")
print(f"NAND(LOW, LOW)   -> {nand_gate(LOW, LOW)}")    # Attendu: True
print(f"NAND(LOW, HIGH)  -> {nand_gate(LOW, HIGH)}")   # Attendu: True
print(f"NAND(HIGH, LOW)  -> {nand_gate(HIGH, LOW)}")   # Attendu: True
print(f"NAND(HIGH, HIGH) -> {nand_gate(HIGH, HIGH)}")  # Attendu: False
```

#### Porte NOR (NON-OU)

C'est la structure duale de la NAND.

*   **Réseau Pull-up (PMOS) :** Deux PMOS en série. Si `a` ET `b` sont `LOW`, la sortie est `HIGH`.
*   **Réseau Pull-down (NMOS) :** Deux NMOS en parallèle. Si `a` OU `b` sont `HIGH`, la sortie est `LOW`.

```python
def nor_gate(a, b):
    """Porte NON-OU, construite avec des transistors."""
    # Pull-up : PMOS en série
    vcc_connection = pmos(a, VCC)
    pull_up = pmos(b, vcc_connection)
    
    # Pull-down : NMOS en parallèle
    pull_down = wire(nmos(a, GND), nmos(b, GND))
    
    return wire(pull_up, pull_down)
    
# Testons !
print("\n--- Porte NOR ---")
print(f"NOR(LOW, LOW)   -> {nor_gate(LOW, LOW)}")    # Attendu: True
print(f"NOR(LOW, HIGH)  -> {nor_gate(LOW, HIGH)}")   # Attendu: False
print(f"NOR(HIGH, LOW)  -> {nor_gate(HIGH, LOW)}")   # Attendu: False
print(f"NOR(HIGH, HIGH) -> {nor_gate(HIGH, HIGH)}")  # Attendu: False
```

---

### Prochaines Étapes : La Suite du Voyage

Félicitations ! Vous venez de créer les briques fondamentales de tout ordinateur moderne à partir d'une simulation de la physique des semi-conducteurs. Vous n'avez "triché" à aucun moment.

Voici la feuille de route pour la suite :

1.  **Construire les autres portes (AND, OR, XOR) :** Maintenant que nous avons NAND et NOT (qui sont des portes universelles), on peut construire toutes les autres par composition. Par exemple, `AND(a, b)` est simplement `NOT(NAND(a, b))`. C'est la première couche d'abstraction.

2.  **L'Arithmétique (Additionneurs) :**
    *   **Demi-Additionneur (Half Adder) :** Prend deux bits en entrée (A, B) et sort une Somme (S) et une Retenue (Carry, C).
        *   `S = XOR(A, B)`
        *   `C = AND(A, B)`
    *   **Additionneur Complet (Full Adder) :** Prend trois bits (A, B, Carry_in) et sort une Somme et une Retenue (Carry_out). On le construit avec deux demi-additionneurs.
    *   **Additionneur N-bits :** On chaîne N additionneurs complets pour additionner des nombres de N bits.

3.  **La Mémoire (Le plus grand défi de la simulation) :**
    *   **Bascule SR (SR Latch) :** Le composant mémoire le plus simple, créé avec deux portes NOR (ou NAND) interconnectées. C'est ici que le concept d'état apparaît. On devra gérer la boucle de feedback dans notre simulation.
    *   **Bascule D (D Latch & D Flip-Flop) :** La brique de base pour les registres. Elle stocke un bit, mais ne change sa valeur que sur un signal d'horloge. C'est ce qui permet de synchroniser le CPU.

4.  **L'Unité Arithmétique et Logique (ALU) :**
    *   Combine l'additionneur N-bits avec des portes logiques (AND, OR, etc.) sur N bits.
    *   Utilise un **Multiplexeur** (que nous devrons aussi construire avec des portes) pour sélectionner l'opération à effectuer (ADD, AND, OR...) en fonction d'un code d'opération.

5.  **Assemblage du CPU :**
    *   **Registres :** Des ensembles de D-Flip-Flops pour stocker les données temporaires (ex: R1, R2...).
    *   **Compteur de Programme (Program Counter - PC) :** Un registre spécial qui contient l'adresse de la prochaine instruction à exécuter et qui peut s'incrémenter.
    *   **Unité de Contrôle :** Décode l'instruction en cours et génère les signaux pour l'ALU, les registres, la mémoire... C'est le chef d'orchestre.
    *   **Mémoire (RAM) :** Pour la simulation, on peut la représenter comme un gros tableau de registres, adressable via un **Décodeur** (également fait de portes).

6.  **Exécuter un programme :**
    *   Définir un jeu d'instructions simple (ISA - Instruction Set Architecture).
    *   Écrire un petit programme en "assembleur" (ex: "additionner 3 et 5").
    *   Le traduire en binaire et le "charger" dans notre RAM simulée.
    *   Lancer la boucle d'horloge et regarder notre CPU exécuter le cycle "Fetch-Decode-Execute".

Je vous propose de continuer étape par étape. Voulez-vous que l'on passe maintenant à la construction des portes composées (AND, OR, XOR) et des premiers circuits arithmétiques ?