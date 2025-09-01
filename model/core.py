from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Callable


# --------------------
# Exceptions
# --------------------

class ConfigError(ValueError):
    """Raised when a game object is misconfigured (invalid tier map, etc.)."""


# --------------------
# Core Enums
# --------------------

class Tier(Enum):
    TIER1 = auto()  # 4..7 players
    TIER2 = auto()  # 8..11 players
    TIER3 = auto()  # 12..15 players
    TIER4 = auto()  # 16+ players


class DayPhase(Enum):
    MORNING = auto()
    AFTERNOON = auto()


class NightPhase(Enum):
    DUSK = auto()
    MIDNIGHT = auto()
    PREDAWN = auto()


class Alignment(Enum):
    GOOD = auto()
    EVIL = auto()
    NEUTRAL = auto()


class WinCondition(Enum):
    ELIMINATE_ALL_EVILS = auto()
    ELIMINATE_ALL_GOOD = auto()
    SURVIVE = auto()
    VOTED_OUT = auto()
    LAST_NEUTRAL = auto()
    # Add more as needed


class AbilityType(Enum):
    DEATH_TRIGGER = auto()
    DUSK_CHOICE = auto()
    MIDNIGHT_CHOICE = auto()
    PREDAWN_CHOICE = auto()
    ONE_TIME = auto()
    PASSIVE = auto()
    VOTE = auto()
    INITIAL_KNOWLEDGE = auto()
    
# --------------------
# Helper Function
# --------------------

def _format_abilities(abilities: List[Ability]) -> str:
    """Helper function to format a list of abilities into a readable string."""
    if not abilities:
        return "None"
    return "\n" + "\n".join([f"    - {str(ability)}" for ability in abilities])


# --------------------
# Ability
# --------------------

@dataclass(frozen=True)
class Ability:
    """
    A unit of power a character can have. `effect` is descriptive text.
    """
    ability_type: AbilityType
    effect: str
    group_ability: bool = False
    
    def __init__(self, ability_type: AbilityType, effect: str, group_ability: bool = False):
        object.__setattr__(self, "ability_type", ability_type)
        object.__setattr__(self, "effect", effect)
        object.__setattr__(self, "group_ability", group_ability)
    
    def __str__(self) -> str:
        group_text = " (Group Ability)" if self.group_ability else ""
        return f"[{self.ability_type.name}]{group_text}: {self.effect}"

# --------------------
# Profession
# --------------------

@dataclass(frozen=True)
class Profession:
    """
    Public identity. Visible to all players.
    """
    name: str
    abilities_list: List[Ability]
    tier_distribution: Dict[Tier, int]
    min_number: int = 0

    def __init__(self, name: str, abilities_list: List[Ability],
                 tier_distribution: Dict[Tier, int], min_number: int = 0):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "abilities_list", abilities_list)
        object.__setattr__(self, "tier_distribution", tier_distribution)
        object.__setattr__(self, "min_number", min_number)
    
    def __str__(self) -> str:
        return (f"Profession: {self.name}\n"
                f"  Abilities: {_format_abilities(self.abilities_list)}")


# --------------------
# Role
# --------------------

@dataclass(frozen=True)
class Role:
    """
    Secret identity. Defines alignment and win condition.
    """
    name: str
    alignment: Alignment
    abilities_list: List[Ability]
    tier_distribution: Dict[Tier, int]
    min_number: int = 0
    win_condition: Optional[WinCondition] = None

    def __init__(self, name: str, alignment: Alignment, abilities_list: List[Ability],
                 tier_distribution: Dict[Tier, int], min_number: int = 0,
                 win_condition: Optional[WinCondition] = None):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "alignment", alignment)
        object.__setattr__(self, "abilities_list", abilities_list)
        object.__setattr__(self, "tier_distribution", tier_distribution)
        object.__setattr__(self, "min_number", min_number)

        if alignment == Alignment.GOOD:
            object.__setattr__(self, "win_condition", WinCondition.ELIMINATE_ALL_EVILS)
        elif alignment == Alignment.EVIL:
            object.__setattr__(self, "win_condition", WinCondition.ELIMINATE_ALL_GOOD)
        else:
            object.__setattr__(self, "win_condition", win_condition)
    
    def __str__(self) -> str:
        win_text = self.win_condition.name.replace('_', ' ').title() if self.win_condition else "Custom"
        return (f"Role: {self.name}\n"
                f"  Alignment: {self.alignment.name.title()}\n"
                f"  Win Condition: {win_text}\n"
                f"  Abilities: {_format_abilities(self.abilities_list)}")


# --------------------
# Character
# --------------------

@dataclass(frozen=True)
class Character:
    """
    The full identity of a player (Profession + Role).
    """
    profession: Profession
    role: Role

    def __init__(self, profession: Profession, role: Role):
        object.__setattr__(self, "profession", profession)
        object.__setattr__(self, "role", role)
    
    def __str__(self) -> str:
        return f"Character:\n{str(self.profession)}\n{str(self.role)}"


# --------------------
# Player
# --------------------

class Player:
    """
    Represents a single participant in the game setup.
    Used only for definition, not for tracking live game state.
    """
    player_id: str
    player_name: str
    character: Character

    def __init__(self, player_id: str, player_name: str, character: Character):
        self.player_id = player_id
        self.player_name = player_name
        self.character = character

    def __repr__(self) -> str:
        return f"Player(id={self.player_id}, name='{self.player_name}', profession='{self.character.profession.name}', role='{self.character.role.name}')"

    def __str__(self) -> str:
        return (f"Player: {self.player_name} (ID: {self.player_id})\n"
                f"------------------------------------\n"
                f"{str(self.character)}")
