from model.generator import *
from model.parser import *
from model.writer import *
import shutil

def ask_player_names(n_players: int) -> list[str]:
    """
    Ask the user to input player names one by one.
    """
    names = []
    print(f"Please enter {n_players} player names:")
    for i in range(n_players):
        name = input(f"  Player {i + 1} name: ").strip()
        while not name:
            print("Name cannot be empty. Try again.")
            name = input(f"  Player {i + 1} name: ").strip()
        names.append(name)
    return names


def main():
    # Step 1: Ask how many players
    n_players = int(input("Enter number of players: "))

    # Step 2: Parse roles and professions
    parser = Parser()
    roles = parser.parse_roles("model/roles.json")
    professions = parser.parse_professions("model/professions.json")

    # Step 3: Generate characters
    generator = Generator(roles, professions)
    characters = generator.generate_characters(n_players)

    # Step 4: Ask for player names
    names = ask_player_names(n_players)

    # Step 5: Build players
    players = [Player(str(i), names[i], characters[i]) for i in range(n_players)]

    # Step 6: Clean output directory
    out_dir = Path("out")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    # Step 7: Write character sheets
    pwriter = PlayerWriter("model/character_template.tex","out")
    pwriter.write_players(players)
    
    # Step 8: Write narrator sheet
    nwriter = NarratorWriter("model/narrator_template.tex","out")
    nwriter.write_narrator(players)

if __name__ == "__main__":
    main()
