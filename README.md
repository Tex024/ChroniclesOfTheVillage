# Chronicles of the Village

**Chronicles of the Village** is a modular **social deduction game** inspired by *Werewolf* and *Mafia*.  
Each player receives a **Profession** (public identity) and a **Role** (secret identity).  
The **Narrator** (Master of the Game) guides the story through alternating **Day** and **Night** phases until one side wins.

---

## Game Overview

- **Professions** → Public identities, visible to all players.  
- **Roles** → Secret identities, alignments, and win conditions.  
- **Abilities** → Actions usable at night or triggered by specific conditions.  

### Alignments
- 🟢 **Good** → Protect the village and eliminate all evils.  
- 🔴 **Evil** → Conspire to overthrow the village.  
- ⚪ **Neutral** → Pursue personal victory conditions.  

---

## Game Phases

### Night
The Narrator resolves abilities in this order:
1. **Dusk Phase** → Abilities at the start of the night.  
2. **Midnight Phase** → Most actions (attacks, investigations, protections).  
3. **Predawn Phase** → Abilities at the end of the night.  

### Day
1. **Morning** → Open discussion among players.  
2. **Afternoon** → Voting phase.  
   - Plurality decides who is executed.  
   - In case of a tie, nobody is eliminated.  

---

## Victory Conditions
- **Good wins** if all Evil players are eliminated.  
- **Evil wins** if all Good players are eliminated.  
- **Neutral wins** if their personal win condition is met when the game ends.  

---

## Project Structure

### Data Files
- `roles.json` → Defines secret roles (alignments, win conditions, abilities).  
- `professions.json` → Defines professions and their public abilities.  

### Code Modules
- **`core.py`** → Core definitions: `Player`, `Character`, `Role`, `Profession`, `Ability`, `Alignment`.  
- **`parser.py`** → Loads roles and professions from JSON.  
- **`generator.py`** → Randomly assigns characters to players.  
- **`writer.py`** → Generates LaTeX player sheets and the Narrator’s script.

The system generates:
- **Character Sheets** → Personalized LaTeX scrolls for each player.  
- **Narrator Script** → A structured LaTeX guide for the Narrator.  

---

## Getting Started

### Requirements
- `Python 3.9+`

### Installation
```bash
git clone https://github.com/Tex024/ChroniclesOfTheVillage.git
```

### Usage
```bash
cd chronicles-of-the-village
python3 main.py
```
Outputs will be written in the output directory

---

## Contributing
The system is fully modular.
New professions, roles, and abilities can be added by editing the JSON files.
Pull requests are welcome!
