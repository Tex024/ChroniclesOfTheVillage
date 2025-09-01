import json
from typing import Dict, List
from .core import Ability, AbilityType, Alignment, ConfigError, Profession, Role, Tier, WinCondition


class Parser:
    """
    Parser for roles.json and professions.json into dataclass objects.
    """

    @staticmethod
    def _parse_abilities(abilities_data: list) -> List[Ability]:
        abilities = []
        for ability in abilities_data:
            abilities.append(
                Ability(
                    ability_type=AbilityType[ability["ability_type"]],
                    effect=ability["effect"],
                    group_ability=ability.get("group_ability", False)
                )
            )
        return abilities

    @staticmethod
    def _parse_tier_distribution(tier_data: Dict[str, int]) -> Dict[Tier, int]:
        """Converts string keys to Tier enum members."""
        distribution = {}
        for tier_str, count in tier_data.items():
            try:
                tier_enum = Tier[tier_str]
                distribution[tier_enum] = count
            except KeyError:
                raise ConfigError(f"Invalid tier name in JSON: {tier_str}")
        return distribution
    
    @staticmethod
    def parse_roles(path: str) -> List[Role]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        required_keys = ["name", "alignment", "tier_distribution"]

        roles: List[Role] = []
        for entry in data:
            for key in required_keys:
                if key not in entry:
                    raise ConfigError(f"Missing required key '{key}' in role definition: {entry}")
            roles.append(
                Role(
                    name=entry["name"],
                    alignment=Alignment[entry["alignment"]],
                    abilities_list=Parser._parse_abilities(entry.get("abilities_list", [])),
                    tier_distribution=Parser._parse_tier_distribution(entry["tier_distribution"]),
                    min_number=entry.get("min_number", 0),
                    win_condition=WinCondition[entry["win_condition"]] if "win_condition" in entry else None
                )
            )
        return roles

    @staticmethod
    def parse_professions(path: str) -> List[Profession]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        required_keys = ["name", "tier_distribution"]
        
        professions: List[Profession] = []
        for entry in data:
            for key in required_keys:
                if key not in entry:
                    raise ConfigError(f"Missing required key '{key}' in role definition: {entry}")
            professions.append(
                Profession(
                    name=entry["name"],
                    abilities_list=Parser._parse_abilities(entry.get("abilities_list", [])),
                    tier_distribution=Parser._parse_tier_distribution(entry["tier_distribution"]),
                    min_number=entry.get("min_number", 0)
                )
            )
        return professions

if __name__ == "__main__":
    roles = Parser.parse_roles("roles.json")
    professions = Parser.parse_professions("professions.json")

    for role in roles:
        print(role)

    for profession in professions:
        print(profession)
