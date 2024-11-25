import json

class Islander:
    def __init__(self, name, aptNum):
        self.name = name
        self.aptNum = aptNum

class Island:
    def __init__(self, islanders=None, name=""):
        self.islanders = islanders if islanders else []
        self.name = name
        self.saved = False

    def tutorial(self):
        """Introduce the game and name the island."""
        print("Hello!")
        self.name = input("What would you like to name your island?\n________ Island\n\nName: ")
        print(f"Good choice. Welcome to {self.name} Island!")

    def islander_maker(self):
        """Add a new islander to the island."""
        print("\nCreate your island resident...")
        name = input("Enter the name of the new islander: ")
        aptNum = len(self.islanders)
        new_islander = Islander(name, aptNum)
        self.islanders.append(new_islander)
        print(f"{name} has been added to the island!\n")
        self.saved = False

    def map(self, save_file):
        """Main menu for interacting with the island."""
        validChoice = False
        while not validChoice:
            choice = int(input(
                "Where would you like to go?\n"
                "1) Apartments\n"
                "2) Make a new islander\n"
                "3) Save the game\n"
                "4) Exit the game\n"
            ))
            if choice == 1:
                validChoice = True
                self.apts()
            elif choice == 2:
                validChoice = True
                self.islander_maker()
            elif choice == 3:
                validChoice = True
                self.save_game(save_file)
            elif choice == 4:
                if not self.saved:
                    sureSaved = input("You have not saved the game. Are you sure you would like to quit? (Y/N)\n").lower()
                    if sureSaved == "y":
                        print("Goodbye!")
                        exit()
                    elif sureSaved == "n":
                        pass
                    else:
                        print("Invalid choice.")
                else:
                    print("Goodbye!")
                    exit()
            else:
                print("Invalid choice.")

    def apts(self):
        """Visit an apartment of an islander."""
        print("\nApartments! Who to visit...")
        if len(self.islanders) == 0:
            print("\nNo one to visit...")
            return
        else:
            for idx, islander in enumerate(self.islanders, start=1):
                print(f"{idx}) {islander.name}")
            validChoice = False
            while not validChoice:
                choice = int(input("Enter a number: "))
                if 1 <= choice <= len(self.islanders):
                    print(f"Let's visit {self.islanders[choice-1].name}'s apartment!\n")
                    validChoice = True
                else:
                    print("Invalid choice.")

            self.inside_apt(self.islanders[choice-1])

    def inside_apt(self, islander):
        """Enter an islander's apartment."""
        print(f"You are in {islander.name}'s home. Take your shoes off!\n")

    def save_game(self, save_file):
        """Save the current state of the game to a file."""
        save_data = {
            "island_name": self.name,
            "islanders": [{"name": i.name, "aptNum": i.aptNum} for i in self.islanders],
        }
        with open(save_file, "w") as f:
            json.dump(save_data, f, indent=4)
        print("Game saved!")
        self.saved = True

    def load_game(self, save_file):
        """Load the game state from a file."""
        try:
            with open(save_file, "r") as f:
                save_data = json.load(f)
                self.name = save_data.get("island_name", "")
                self.islanders = [Islander(i["name"], i["aptNum"]) for i in save_data.get("islanders", [])]
                print(f"Welcome back to {self.name} Island!")
        except FileNotFoundError:
            print("No save file found. Starting a new game.")
            self.islanders = []

if __name__ == "__main__":
    # Save file location
    save_file = "island_game_save.json"
    # Initialize the island and load any saved data
    leIsland = Island()
    leIsland.load_game(save_file)

    # Show the tutorial only if no island name is loaded
    if not leIsland.name:
        leIsland.tutorial()

    # Main game loop
    while True:
        leIsland.map(save_file)
