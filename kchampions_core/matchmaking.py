"""
matchmaking.py — Logique d'appariement des joueurs.

Module pur : aucune dépendance vers le connector ou le controller.
"""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Pairing:
    player1: str
    player2: str | None  # None = bye (joueur sans adversaire ce round)


def _select_bye_player(players: list[str], past_byes: list[str]) -> str:
    """Retourne le joueur ayant le moins de byes dans l'historique (tiebreak aléatoire)."""
    bye_counts = {p: 0 for p in players}
    for p in past_byes:
        if p in bye_counts:
            bye_counts[p] += 1
    min_byes = min(bye_counts.values())
    candidates = [p for p, c in bye_counts.items() if c == min_byes]
    return random.choice(candidates)


def make_pairings(
    players: list[str],
    past_pairings: list[tuple[str, str | None]],
) -> list[Pairing]:
    """
    Apparie les joueurs 2 par 2 en évitant au maximum les répétitions.

    Si le nombre de joueurs est impair, le joueur ayant eu le moins de byes
    dans l'historique reçoit un bye (Pairing avec player2=None). En cas
    d'égalité le choix est aléatoire.

    Args:
        players:       Liste des noms de joueurs à apparier.
        past_pairings: Historique des appariements sous forme de couples
                       (player1, player2). player2=None indique un bye passé.

    Returns:
        Liste de Pairing. Les byes sont en fin de liste.
        Longueur = ceil(len(players) / 2).
    """
    if not players:
        return []
    if len(players) == 1:
        return [Pairing(player1=players[0], player2=None)]

    past_byes = [p1 for p1, p2 in past_pairings if p2 is None]
    past_set = {frozenset(p) for p1, p2 in past_pairings if p2 is not None for p in [(p1, p2)]}

    pool = list(players)
    bye_pairing: Pairing | None = None

    if len(pool) % 2 == 1:
        bye_player = _select_bye_player(pool, past_byes)
        pool.remove(bye_player)
        bye_pairing = Pairing(player1=bye_player, player2=None)

    best: list[Pairing] = []
    best_score = len(pool)

    for _ in range(200):
        random.shuffle(pool)
        candidate = [
            Pairing(pool[i], pool[i + 1])
            for i in range(0, len(pool) - 1, 2)
        ]
        score = sum(
            1 for p in candidate
            if frozenset((p.player1, p.player2)) in past_set
        )
        if score < best_score:
            best_score = score
            best = candidate
        if score == 0:
            break

    if bye_pairing is not None:
        best.append(bye_pairing)

    return best
