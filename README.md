# Chronicles of the Village

**Chronicles of the Village** is a modular **social deduction game engine** inspired by *Werewolf* and *Mafia*.  
It generates **character sheets** for players and a **Narrator’s script** using LaTeX.

- 🎭 **Professions** → Public identities, known to everyone.  
- 🕵️ **Roles** → Secret identities with alignments and powers.  
- 📜 **Narrator Script** → Step-by-step guide for the game master.  

The project is fully modular: new roles, professions, and abilities can be added by editing JSON files.

> 👉 For the full game rules and how to play, see [RULES.md](RULES.md).

---

## 📂 Project Structure

- `roles.json` → Defines roles (secret identities, alignments, abilities).  
- `professions.json` → Defines professions (public abilities).  
- `core.py` → Core definitions: `Player`, `Character`, `Role`, `Profession`, `Ability`, `Alignment`.  
- `parser.py` → Loads JSON data.  
- `generator.py` → Randomly assigns roles and professions to players.  
- `writer.py` → Generates LaTeX sheets (players + narrator).  
- `out/` → Output directory (generated PDFs).  

---

## ⚙️ Requirements

- **Python 3.9+**
- **LaTeX distribution** (for PDF generation):
  - **Windows** → [MiKTeX](https://miktex.org/download) or [TeX Live](https://www.tug.org/texlive/). Ensure `pdflatex.exe` is in your `PATH`.  
  - **macOS** → [MacTeX](https://tug.org/mactex/)  
  - **Linux** → `texlive-full` (e.g. `sudo apt install texlive-full`)  

Verify installation by running:

```bash
pdflatex --version
```

## 🚀 Installation and Usage

Clone the repository:

```bash
git clone https://github.com/Tex024/ChroniclesOfTheVillage.git
cd ChroniclesOfTheVillage
```

Run the main script, and write the players names when requested:
```bash
python3 main.py
```

Outputs:
- `out/player_<name>.pdf`: personalized character sheet for the player
- `out/narrator_script.pdf`: complete narrator script

## 🛠️ Customization

Add new professions/roles by editing the JSON files:

- `professions.json` → Add new public identities.

- `roles.json` → Add new secret roles, alignments, and abilities.

The system automatically integrates new definitions when generating sheets.

## 🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests for:

- new roles/professions
- bug fixes
- improved LaTeX templates

## 📜 License
MIT License – free to use and modify.