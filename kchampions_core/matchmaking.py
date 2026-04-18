"""
matchmaking.py — Logique d'appariement des joueurs.

Module pur : aucune dépendance vers le connector ou le controller.
"""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Pairing:
    player1: str
    player2: str


def make_pairings(
    players: list[str],
    past_pairings: list[tuple[str, str]],
) -> list[Pairing]:
    """
    Apparie les joueurs 2 par 2 en évitant au maximum les appariements déjà joués.

    L'algorithme tente 200 permutations aléatoires et retient celle qui minimise
    le nombre de répétitions. Si le nombre de joueurs est impair, le dernier joueur
    de la permutation retenue ne reçoit pas d'adversaire (bye).

    Args:
        players:      Liste des noms de joueurs à apparier.
        past_pairings: Appariements déjà réalisés sous forme de couples (nom1, nom2).

    Returns:
        Liste de Pairing (player1, player2). Longueur = len(players) // 2.
    """
    if len(players) < 2:
        return []

    past: set[frozenset] = {frozenset(p) for p in past_pairings}

    best: list[Pairing] = []
    best_score: int = len(players)  # pire cas possible

    pool = list(players)

    for _ in range(200):
        random.shuffle(pool)
        candidate = [
            Pairing(pool[i], pool[i + 1])
            for i in range(0, len(pool) - 1, 2)
        ]
        score = sum(
            1 for p in candidate
            if frozenset((p.player1, p.player2)) in past
        )
        if score < best_score:
            best_score = score
            best = candidate
        if score == 0:
            break

    return best
