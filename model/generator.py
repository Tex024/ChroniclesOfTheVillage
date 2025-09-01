# generator.py
from collections import Counter
import random
from math import floor
from typing import List
from .core import Character, Role, Profession, Alignment, Tier, ConfigError


class Generator:
    """
    Generates Characters given available roles, professions, and player count.
    """

    def __init__(self, roles: List[Role], professions: List[Profession]):
        self.roles = roles
        self.professions = professions

    def _get_tier(self, num_players: int) -> Tier:
        """Determine the game tier based on number of players."""
        if 4 <= num_players <= 7:
            return Tier.TIER1
        elif 8 <= num_players <= 11:
            return Tier.TIER2
        elif 12 <= num_players <= 15:
            return Tier.TIER3
        else:
            return Tier.TIER4

    def _choose_roles(self, num_players: int, tier: Tier) -> List[Role]:
        """
        Selects roles for players, considering alignment distribution,
        tier distribution, and min_number.
        """
        num_neutral = floor(num_players / 6)
        num_evil = floor(num_players / 3)
        num_good = num_players - num_neutral - num_evil

        # group roles by alignment
        good_roles = [r for r in self.roles if r.alignment == Alignment.GOOD and r.tier_distribution.get(tier, 0) > 0]
        evil_roles = [r for r in self.roles if r.alignment == Alignment.EVIL and r.tier_distribution.get(tier, 0) > 0]
        neutral_roles = [r for r in self.roles if r.alignment == Alignment.NEUTRAL and r.tier_distribution.get(tier, 0) > 0]

        def pick_roles(pool: List[Role], count: int) -> None:
            selected: List['Role'] = []
            selected_counts = Counter() # Use Counter to track selected roles efficiently
            
            while len(selected) < count:
                if not pool:
                    raise ConfigError(f"Not enough roles available to fill {num_players} slots")
                
                role = random.choice(pool)
                max_allowed = role.tier_distribution.get(tier, 0)
                min_required = role.min_number
                
                already_added = selected_counts[role.name]
                
                # if the min is still to satisfy and there are enough spots to satisfy it, add the roles
                if already_added < min_required and (count - len(selected)) >= (min_required - already_added):
                    to_add = min_required - already_added
                    selected.extend([role] * to_add)
                    selected_counts[role.name] += to_add
                # if the min is already satisfied and the max is not add 1 of this role
                elif already_added >= min_required and already_added < max_allowed:
                    selected.append(role)
                    selected_counts[role.name] += 1
                # Filter out roles that can no longer be added
                
                pool = [
                    r for r in pool
                    if selected_counts[r.name] < r.tier_distribution.get(tier, 0)  # not at max
                    and (count - len(selected)) >= (r.min_number - selected_counts[r.name])  # enough slots for min
                ]

            random.shuffle(selected)
            return selected


        selected: List[Role] = []
        selected.extend(pick_roles(good_roles, num_good))
        selected.extend(pick_roles(evil_roles, num_evil))
        selected.extend(pick_roles(neutral_roles, num_neutral))

        return selected

    def _choose_professions(self, num_players: int, tier: 'Tier') -> List['Profession']:
        """
        Selects professions for players, considering tier distribution and min_number.
        """
        
        # Filter professions based on the current tier.
        pool = [p for p in self.professions if p.tier_distribution.get(tier, 0) > 0]
        
        selected: List[Profession] = []
        selected_counts = Counter()
        
        while len(selected) < num_players:
            # Check if there are any professions left to choose from
            if not pool:
                raise ConfigError(f"Not enough professions available to fill {num_players} slots")
            
            profession = random.choice(pool)
            max_allowed = profession.tier_distribution.get(tier, 0)
            min_required = profession.min_number
            already_added = selected_counts[profession.name]
            
            # if the min is still to satisfy and there are enough spots to satisfy it, add the professions
            if already_added < min_required and (num_players - len(selected)) >= (min_required - already_added):
                to_add = min_required - already_added
                selected.extend([profession] * to_add)
                selected_counts[profession.name] += to_add
            # if the min is already satisfied and the max is not, add 1 of this profession
            elif already_added >= min_required and already_added < max_allowed:
                selected.append(profession)
                selected_counts[profession.name] += 1
            
            # Filter out professions that have reached their maximum allowed count
            pool = [p for p in pool if selected_counts[p.name] < p.tier_distribution.get(tier, 0)]

        random.shuffle(selected)
        return selected

    def generate_characters(self, num_players: int) -> List[Character]:
        """
        Main entrypoint: generates a full list of Characters.
        """
        if num_players < 4:
            raise ConfigError("Minimum number of players is 4")

        tier = self._get_tier(num_players)

        roles = self._choose_roles(num_players, tier)
        professions = self._choose_professions(num_players, tier)

        # shuffle roles and professions separately, then pair
        random.shuffle(roles)
        random.shuffle(professions)

        characters = [Character(prof, role) for prof, role in zip(professions, roles)]
        random.shuffle(characters)
        return characters

if __name__ == "__main__":
    from parser import GameDataParser

    roles = GameDataParser.parse_roles("roles.json")
    professions = GameDataParser.parse_professions("professions.json")
    
    generator = Generator(roles, professions)
    
    num_players = 6
    
    try:
        characters = generator.generate_characters(num_players)
        for idx, char in enumerate(characters, start=1):
            print(f"Player {idx}:")
            print(char)
            print("-" * 30)
    except ConfigError as e:
        print("Failed: ", e)
