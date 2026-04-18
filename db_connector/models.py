"""
models.py — Structures de données retournées par le connecteur.
Utilise des dataclasses pour un typage clair et sans dépendance externe.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Battleroom:
    id: int
    name: str
    date: str
    round: int


@dataclass
class Battle:
    id: int
    battleroom_id: int
    round: int
    finished: bool
    content: dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    name: str
    teamlist: str
    number_battle: int
