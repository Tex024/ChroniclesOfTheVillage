from typing import List
from pathlib import Path

from .core import Player, Alignment, Ability


class Writer:
    def __init__(self, template_path: str, narrator_template_path: str, output_dir: str = ".output"):
        """
        Initialize the writer with template paths and output directory.
        """
        self.template_path = template_path
        self.narrator_template_path = narrator_template_path
        self.output_dir = Path(output_dir)
        if self.output_dir.exists():
            # Clear previous output to ensure fresh run
            for f in self.output_dir.glob("*"):
                f.unlink()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load templates once
        with open(self.template_path, "r", encoding="utf-8") as f:
            self.template = f.read()
        with open(self.narrator_template_path, "r", encoding="utf-8") as f:
            self.narrator_template = f.read()

    def _format_abilities(self, abilities: List[Ability]) -> str:
        """
        Format abilities list into LaTeX using displayability.
        """
        if not abilities:
            return ""
        formatted = []
        for ability in abilities:
            group = "(Group Ability)" if ability.group_ability else ""
            formatted.append(
                f"\\displayability{{{ability.ability_type.name.title().replace('_',' ')}}}{{{ability.effect}}}{{{group}}}"
            )
        return "\n".join(formatted)

    def _format_narrator_abilities(self, abilities: List[Ability], role_or_profession: str) -> str:
        """
        Format abilities for narrator template.
        """
        if not abilities:
            return ""
        formatted = []
        for ability in abilities:
            formatted.append(
                f"\\abilityentry{{{role_or_profession}}}{{{ability.ability_type.name.title().replace('_',' ')}}}{{{ability.effect}}}"
            )
        return "\n".join(formatted)

    def _alignment_color(self, alignment: Alignment) -> str:
        """
        Map alignment to LaTeX color command.
        """
        if alignment == Alignment.GOOD:
            return "\\color{GoodGreen}"
        elif alignment == Alignment.EVIL:
            return "\\color{EvilRed}"
        else:
            return "\\color{NeutralGray}"

    def _fill_template(self, player: Player) -> str:
        """
        Replace placeholders with actual player data for personal sheet.
        """
        profession = player.character.profession
        role = player.character.role

        tex_content = self.template
        tex_content = tex_content.replace("[Player Name]", f"{player.player_name}")
        tex_content = tex_content.replace("[Player ID]", f"{player.player_id}")
        tex_content = tex_content.replace("[Profession Name]", f"{profession.name}")
        tex_content = tex_content.replace("[Profession Abilities]", f"{self._format_abilities(profession.abilities_list)}")
        tex_content = tex_content.replace("[Role Name]", f"{role.name}")
        tex_content = tex_content.replace("[Role Abilities]", f"{self._format_abilities(role.abilities_list)}")
        tex_content = tex_content.replace("[Alignement]", f"{role.alignment.name.title()}")
        tex_content = tex_content.replace("[Alignement Color]", f"{self._alignment_color(role.alignment)}")
        tex_content = tex_content.replace("[Win Condition]", f"{role.win_condition.name.title().replace('_',' ')}")

        return tex_content

    def _fill_narrator_template(self, players: List[Player]) -> str:
        """
        Replace narrator placeholders with data aggregated from all players.
        """
        # --- Player list ---
        player_list_entries = []
        for p in players:
            player_list_entries.append(
                f"\\playerentry{{{p.player_name}}}{{{p.character.profession.name}}}{{{p.character.role.name}}}{{{self._alignment_color(p.character.role.alignment)}{p.character.role.alignment.name.title()}\\color{{black}}}}"
            )

        # --- Abilities ---
        special = []
        dusk = []
        midnight = []
        predawn = []
        initial = []

        for p in players:
            role = p.character.role
            profession = p.character.profession

            # Group abilities by type
            for ab in profession.abilities_list + role.abilities_list:
                if ab.ability_type.name == "SPECIAL":
                    special.append(self._format_narrator_abilities([ab], role.name))
                elif ab.ability_type.name == "DUSK_CHOICE":
                    dusk.append(self._format_narrator_abilities([ab], role.name))
                elif ab.ability_type.name == "MIDNIGHT_CHOICE":
                    midnight.append(self._format_narrator_abilities([ab], role.name))
                elif ab.ability_type.name == "PREDAWN_CHOICE":
                    predawn.append(self._format_narrator_abilities([ab], role.name))
                elif ab.ability_type.name == "INITIAL_KNOWLEDGE":
                    initial.append(self._format_narrator_abilities([ab], role.name))

        tex_content = self.narrator_template
        tex_content = tex_content.replace("[Player List]", "\n".join(player_list_entries))
        tex_content = tex_content.replace("[Special Abilities]", "\n".join(special))
        tex_content = tex_content.replace("[Dusk Phase Abilities]", "\n".join(dusk))
        tex_content = tex_content.replace("[Midnight Phase Abilities]", "\n".join(midnight))
        tex_content = tex_content.replace("[Predawn Phase Abilities]", "\n".join(predawn))
        tex_content = tex_content.replace("[Initial Knowledge Abilities]", "\n".join(initial))

        return tex_content

    def write_all(self, players: List[Player]):
        """
        Generate one .tex file per player and one narrator script.
        """
        # Individual player sheets
        for player in players:
            tex_content = self._fill_template(player)
            filename = f"{player.player_id}_{player.player_name.replace(' ', '_')}.tex"
            filepath = self.output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(tex_content)
            print(f"✔ Written {filepath}")

        # Narrator script
        narrator_tex = self._fill_narrator_template(players)
        narrator_path = self.output_dir / "narrator_script.tex"
        with open(narrator_path, "w", encoding="utf-8") as f:
            f.write(narrator_tex)
        print(f"✔ Written {narrator_path}")
