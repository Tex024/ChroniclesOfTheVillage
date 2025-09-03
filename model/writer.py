from typing import List, Optional, Dict
from pathlib import Path
import subprocess
import shutil
import re

# import your models (adjust the import path if necessary)
from .core import Player, Ability, Alignment


class PlayerWriter:
    r"""
    Generate one PDF per Player using a LaTeX template with <<<PLACEHOLDER>>> tokens.

    - template_path: path to the .tex template (use the template above).
    - output_dir: directory where .tex/.pdf/logs are written.
    - allow_latex: if False, plain text fields are escaped for LaTeX; if True, fields
                   are inserted verbatim (useful if effects already contain LaTeX).
    - pdflatex_cmd: name/path of the pdflatex executable (default 'pdflatex').
    """

    def __init__(
        self,
        template_path: str,
        output_dir: str = ".output",
        allow_latex: bool = False,
        pdflatex_cmd: str = "pdflatex",
    ) -> None:
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        self.template = self.template_path.read_text(encoding="utf-8")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.allow_latex = allow_latex
        self.pdflatex_cmd = pdflatex_cmd

    # ------------------ Utilities ------------------

    def _escape_latex(self, text: Optional[str]) -> str:
        """
        Escape minimal set of LaTeX special chars. This is conservative and safe
        for plain text. If you want to include custom LaTeX, set allow_latex=True.
        """
        if not text:
            return ""
        s = str(text)
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        # Use regex substitution for speed and correctness
        pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
        return pattern.sub(lambda m: replacements[m.group(0)], s)

    def _sanitize_filename(self, text: str) -> str:
        """
        Make a safe filename from arbitrary text.
        """
        s = re.sub(r"[^\w\-\. ]+", "", text)
        s = s.strip().replace(" ", "_")
        return s[:120] if len(s) > 120 else s

    # ------------------ Abilities formatting ------------------

    def _format_ability_item(self, ability: Ability) -> str:
        """
        Return a single displayability{<name>}{<effect>} line.
        If Ability has group_ability True, append an italic suffix to effect.
        """
        name = ability.ability_type.name.title().replace("_", " ")
        effect = ability.effect or ""
        if getattr(ability, "group_ability", False):
            # append suffix as plain text (escaped if needed)
            effect = effect + " \\textit{(Group ability)}"

        if not self.allow_latex:
            name = self._escape_latex(name)
            effect = self._escape_latex(effect)
        return f"\\displayability{{{name}}}{{{effect}}}"

    def _abilities_block(self, abilities: List[Ability]) -> str:
        """
        Return either an itemize block (if abilities non-empty) or empty string.
        """
        if not abilities:
            return ""
        items = [self._format_ability_item(a) for a in abilities]
        block = (
            "\\begin{itemize}[leftmargin=*, itemsep=2pt]\n"
            + "\n".join(items)
            + "\n\\end{itemize}"
        )
        return block

    # ------------------ Alignment ------------------

    def _aligned_and_color(self, alignment: Alignment) -> str:
        """
        Return \textcolor{<color>}{<Alignment>} as a single string.
        """
        label = alignment.name.title()
        if not self.allow_latex:
            label = self._escape_latex(label)

        if alignment == Alignment.GOOD:
            return r"\textcolor{GoodGreen}{" + label + "}"
        if alignment == Alignment.EVIL:
            return r"\textcolor{EvilRed}{" + label + "}"
        return r"\textcolor{NeutralGray}{" + label + "}"

    # ------------------ Template filling ------------------

    def _fill_template(self, player: Player) -> str:
        """
        Replace <<<TOKENS>>> in the loaded template with prepared LaTeX fragments.
        """
        profession = player.character.profession
        role = player.character.role

        mapping = {
            "<<<PLAYER_NAME>>>": player.player_name or "",
            "<<<PLAYER_ID>>>": str(getattr(player, "player_id", "")),
            "<<<PROFESSION_NAME>>>": profession.name if profession else "",
            "<<<ROLE_NAME>>>": role.name if role else "",
            "<<<WIN_CONDITION>>>": (role.win_condition.name.title().replace("_", " ") if getattr(role, "win_condition", None) else ""),
            "<<<ALIGNED_AND_COLOR>>>": self._aligned_and_color(role.alignment) if role else "",
            "<<<PROFESSION_ABILITIES>>>": self._abilities_block(getattr(profession, "abilities_list", [])),
            "<<<ROLE_ABILITIES>>>": self._abilities_block(getattr(role, "abilities_list", [])),
        }

        # Escape simple text placeholders when allow_latex is False
        if not self.allow_latex:
            for key in ("<<<PLAYER_NAME>>>", "<<<PROFESSION_NAME>>>", "<<<ROLE_NAME>>>", "<<<WIN_CONDITION>>>"):
                mapping[key] = self._escape_latex(mapping[key])

        tex = self.template
        for token, val in mapping.items():
            tex = tex.replace(token, val)
        return tex

    # ------------------ PDF compilation ------------------

    def _run_pdflatex(self, tex_path: Path) -> None:
        """
        Run pdflatex in the output directory. Capture stdout/stderr; on error
        write a .log file and raise RuntimeError with hint to the log path.
        """
        # Check pdflatex presence
        if shutil.which(self.pdflatex_cmd) is None:
            raise RuntimeError(
                f"'{self.pdflatex_cmd}' not found in PATH. Install a TeX distribution (MiKTeX/TeX Live) or set pdflatex_cmd."
            )

        # Run pdflatex twice for stability (references)
        for pass_no in (1, 2):
            proc = subprocess.run(
                [self.pdflatex_cmd, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=tex_path.parent,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                log_path = tex_path.with_suffix(".log")
                log_path.write_text(proc.stdout + "\n\nSTDERR:\n" + proc.stderr, encoding="utf-8")
                # do not delete tex on failure to aid debugging
                raise RuntimeError(f"pdflatex failed for {tex_path.name}. See log: {log_path}")
        # success: clean auxiliaries, keep pdf
        for ext in (".aux", ".log", ".out", ".toc", ".synctex.gz"):
            p = tex_path.with_suffix(ext)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
        # remove the .tex by default (safe to keep if you want)
        if tex_path.exists():
            tex_path.unlink()

    # ------------------ Public API ------------------

    def write_players(self, players: List[Player]) -> None:
        """
        Generate one PDF per player in output_dir.
        Filenames: {player_id}_{player_name_sanitized}.pdf
        """
        for player in players:
            tex = self._fill_template(player)
            name_part = self._sanitize_filename(str(player.player_name or "player"))
            id_part = str(getattr(player, "player_id", "0"))
            filename = f"{id_part}_{name_part}.tex"
            tex_path = self.output_dir / filename
            tex_path.write_text(tex, encoding="utf-8")
            try:
                self._run_pdflatex(tex_path)
                print(f"✔ Generated {tex_path.with_suffix('.pdf').name}")
            except Exception as e:
                print(f"✖ Error for {tex_path.name}: {e}")
                # leave the .tex and .log so you can inspect them

class NarratorWriter:
    r"""
    Produce a narrator .tex and compile to PDF from a LaTeX template that uses
    <<<...>>> tokens. Tokens replaced:
      - <<<PLAYER_LIST>>>        -> full itemize block or ""
      - <<<SPECIAL_ABILITIES>>>  -> full itemize block or ""
      - <<<INITIAL_ABILITIES>>>  -> full (nested) itemize block or ""
      - <<<DUSK_PHASE>>>         -> full itemize block or ""
      - <<<MIDNIGHT_PHASE>>>     -> full itemize block or ""
      - <<<PREDAWN_PHASE>>>      -> full itemize block or ""
    """

    def __init__(
        self,
        template_path: str,
        output_dir: str = "out",
        allow_latex: bool = False,
        pdflatex_cmd: str = "pdflatex",
    ) -> None:
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        self.template = self.template_path.read_text(encoding="utf-8")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.allow_latex = allow_latex
        self.pdflatex_cmd = pdflatex_cmd

    # ------------------ Utilities ------------------

    def _escape_latex(self, text: Optional[str]) -> str:
        if not text:
            return ""
        s = str(text)
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
        return pattern.sub(lambda m: replacements[m.group(0)], s)

    def _abilities_item( self, source_label: str, owner_name: str, ability_type_label: str, effect: str, is_special: bool = False) -> str:
        """
        Build a single \abilityentry{source}{owner}{third}.

        - For non-special abilities (night / initial): third == effect
        -> \textbf{source} (owner): effect

        - For special abilities: third == "AbilityType - effect"
        -> \textbf{source} (owner): AbilityType - effect

        Escapes fields unless allow_latex is True.
        """
        if not self.allow_latex:
            source_label = self._escape_latex(source_label)
            owner_name = self._escape_latex(owner_name)
            ability_type_label = self._escape_latex(ability_type_label)
            effect = self._escape_latex(effect)

        if is_special:
            third = f"{ability_type_label} - {effect}" if ability_type_label else effect
        else:
            third = effect

        return f"\\abilityentry{{{source_label}}}{{{owner_name}}}{{{third}}}"


    def _block_itemize(self, items: List[str], nested: bool = False) -> str:
        """
        Return either a full itemize block with the supplied items or empty string.
        Use nested=True for nested (smaller left margin).
        """
        if not items:
            return ""
        lm = "leftmargin=2em" if nested else "leftmargin=*, itemsep=2pt"
        body = "\n".join(items)
        return f"\\begin{{itemize}}[{lm}]\n{body}\n\\end{{itemize}}"

    def _color_for_alignment(self, alignment: Alignment, label: str) -> str:
        """
        Return \textcolor{...}{label}
        """
        if not self.allow_latex:
            label = self._escape_latex(label)
        if alignment == Alignment.GOOD:
            return r"\textcolor{GoodGreen}{" + label + "}"
        if alignment == Alignment.EVIL:
            return r"\textcolor{EvilRed}{" + label + "}"
        return r"\textcolor{NeutralGray}{" + label + "}"

    # ------------------ Formatting collections ------------------

    def _format_player_list(self, players: List[Player]) -> str:
        """
        Produce a full itemize block with playerentry{Player}{Profession}{Role}{AlignmentColor}
        """
        items = []
        for p in players:
            pname = p.player_name or ""
            prof = getattr(p.character, "profession", None)
            role = getattr(p.character, "role", None)
            prof_name = prof.name if prof else ""
            role_name = role.name if role else ""
            alignment_label = role.alignment.name.title() if role and getattr(role, "alignment", None) else ""
            alignment_fragment = self._color_for_alignment(role.alignment, alignment_label) if role else ""
            if not self.allow_latex:
                pname = self._escape_latex(pname)
                prof_name = self._escape_latex(prof_name)
                role_name = self._escape_latex(role_name)
            items.append(f"\\playerentry{{{pname}}}{{{prof_name}}}{{{role_name}}}{{{alignment_fragment}}}")
        return self._block_itemize(items)

    def _collect_abilities_by_phase(self, players: List[Player]) -> Dict[str, List[str]]:
        """
        Group abilities from profession and role into buckets.
        Returns a dict with keys: 'special','initial','dusk','midnight','predawn'
        Each value is a list of formatted \abilityentry lines (strings).
        """
        buckets = {"special": [], "initial": [], "dusk": [], "midnight": [], "predawn": []}
        mapping = {
            "SPECIAL": "special",
            "INITIAL_KNOWLEDGE": "initial",
            "DUSK_CHOICE": "dusk",
            "MIDNIGHT_CHOICE": "midnight",
            "PREDAWN_CHOICE": "predawn",
        }

        for p in players:
            player_name = p.player_name or ""
            # profession and role names (source labels) should be just the profession/role name
            prof_name = getattr(p.character, "profession", None)
            prof_label = prof_name.name if prof_name else ""
            role_name = getattr(p.character, "role", None)
            role_label = role_name.name if role_name else ""

            # helper to process a single ability object into the right bucket
            def process_ability(ab, source_label):
                type_name = getattr(ab.ability_type, "name", str(ab.ability_type)).upper()
                bucket = mapping.get(type_name, "special")
                ability_type_label = type_name.title().replace("_", " ")
                effect_text = ab.effect or ""
                if getattr(ab, "group_ability", False):
                    effect_text = effect_text + " (Group ability)"
                # special abilities should format as: [source] ([player]): [ability type] - [effect]
                is_special = bucket == "special"
                entry = self._abilities_item(source_label, player_name, ability_type_label, effect_text, is_special=is_special)
                buckets[bucket].append(entry)

            # profession abilities
            for ab in list(getattr(p.character.profession, "abilities_list", [])):
                process_ability(ab, prof_label)

            # role abilities
            for ab in list(getattr(p.character.role, "abilities_list", [])):
                process_ability(ab, role_label)

        return buckets


    # ------------------ Template filling & compilation ------------------

    def _fill_template(self, players: List[Player]) -> str:
        """
        Replace tokens in the template with prepared LaTeX fragments.
        """
        players_block = self._format_player_list(players)
        buckets = self._collect_abilities_by_phase(players)

        mapping = {
            "<<<PLAYER_LIST>>>": players_block,
            "<<<SPECIAL_ABILITIES>>>": self._block_itemize(buckets["special"]),
            "<<<INITIAL_ABILITIES>>>": self._block_itemize(buckets["initial"], nested=True),
            "<<<DUSK_PHASE>>>": self._block_itemize(buckets["dusk"]),
            "<<<MIDNIGHT_PHASE>>>": self._block_itemize(buckets["midnight"]),
            "<<<PREDAWN_PHASE>>>": self._block_itemize(buckets["predawn"]),
        }

        tex = self.template
        for token, val in mapping.items():
            tex = tex.replace(token, val)
        return tex

    def _run_pdflatex(self, tex_path: Path) -> None:
        if shutil.which(self.pdflatex_cmd) is None:
            raise RuntimeError(f"'{self.pdflatex_cmd}' not found in PATH. Install MiKTeX/TeX Live or set pdflatex_cmd.")

        for _ in (1, 2):
            proc = subprocess.run(
                [self.pdflatex_cmd, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=tex_path.parent,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                log_path = tex_path.with_suffix(".log")
                log_path.write_text(proc.stdout + "\n\nSTDERR:\n" + proc.stderr, encoding="utf-8")
                raise RuntimeError(f"pdflatex failed for {tex_path.name}. See log: {log_path}")

        # cleanup auxiliaries on success
        for ext in (".aux", ".log", ".out", ".toc", ".synctex.gz"):
            p = tex_path.with_suffix(ext)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
        if tex_path.exists():
            tex_path.unlink()

    def write_narrator(self, players: List[Player], filename: str = "narrator_script.tex") -> None:
        """
        Create and compile narrator script for the given players.
        """
        tex = self._fill_template(players)
        path = self.output_dir / filename
        path.write_text(tex, encoding="utf-8")
        try:
            self._run_pdflatex(path)
            print(f"✔ Generated {path.with_suffix('.pdf').name}")
        except Exception as e:
            print(f"✖ Error generating narrator PDF: {e}")
            # leave .tex and .log for inspection
