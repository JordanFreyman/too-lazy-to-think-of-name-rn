import json
import sqlite3

class Islander:
    def __init__(self, name, aptNum, gender, age, height, hair=None, eyes=None, voice=None):
        self.name = name
        self.aptNum = aptNum
        self.gender = gender
        self.age = age
        self.height = height
        self.hair = hair
        self.eyes = eyes
        self.voice = voice

class Island:
    def __init__(self, db_name="island_game.db"):
        self.db_name = db_name
        self.islanders = []
        self.saved = False
        self.name = ""
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the SQLite database and create tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        #Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS islanders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            age INTEGER,
            height INTEGER
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appearance (
            islander_id INTEGER,
            hair INTEGER,
            eyes INTEGER,
            voice INTEGER,
            FOREIGN KEY(islander_id) REFERENCES islanders(id)
        )''')

        conn.commit()
        conn.close()

    def save_game(self, save_file):
        """Save the current state of the game to the SQLite database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create the island table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS island (
            id INTEGER PRIMARY KEY,
            name TEXT
        )''')

        # Save the island's name if not already saved
        cursor.execute('''
        INSERT OR REPLACE INTO island (id, name) VALUES (1, ?)
        ''', (self.name,))  # Insert or replace the island name in the table (id = 1 is just a placeholder)
        
        # Save islander's main details
        for islander in self.islanders:
            cursor.execute('''
            INSERT INTO islanders (name, gender, age, height)
            VALUES (?, ?, ?, ?)''', (islander.name, islander.gender, islander.age, islander.height))

            # Save the islander's appearance details
            cursor.execute('''
            INSERT INTO appearance (islander_id, hair, eyes, voice)
            VALUES ((SELECT id FROM islanders WHERE name = ?), ?, ?, ?)''', 
            (islander.name, islander.hair, islander.eyes, islander.voice))

        conn.commit()
        conn.close()
        print("Game saved.")
        self.saved = True


    def load_game(self, save_file):
        """Load the game state from the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Ensure the island table exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS island (
                id INTEGER PRIMARY KEY,
                name TEXT
            )''')

            # Check if island name exists in the island table
            cursor.execute('SELECT name FROM island WHERE id = 1')
            row = cursor.fetchone()

            if row:
                # If island name is found, load it
                self.name = row[0]
                print(f"Welcome back to {self.name} Island!\n")
            else:
                # If island name is not found, ask for a new name and save it
                self.name = input("What would you like to name your island?\n________ Island\n\nName: ")
                cursor.execute('''
                INSERT INTO island (id, name) VALUES (1, ?)
                ''', (self.name,))  # Save the island name
                conn.commit()
                print(f"Good choice. Welcome to {self.name} Island!\n")

            # Fetch all islanders from the islanders table
            cursor.execute('SELECT * FROM islanders')
            rows = cursor.fetchall()

            for row in rows:
                # Assuming row[1] is name, row[2] is gender, row[3] is age, row[4] is height
                # (adjust the indices based on your schema if needed)
                if len(row) >= 5:  # Ensure there are enough columns
                    name, gender, age, height = row[1], row[2], row[3], row[4]
                    islander = Islander(name, row, gender, age, height)

                    # Load appearance details
                    cursor.execute('SELECT * FROM appearance WHERE islander_id = ?', (row[0],))
                    appearance_row = cursor.fetchone()

                    if appearance_row:
                        islander.hair = appearance_row[1]
                        islander.eyes = appearance_row[2]
                        islander.voice = appearance_row[3]

                    self.islanders.append(islander)

            conn.close()
        except sqlite3.Error as e:
            print(f"Error loading game: {e}")
            print("Starting a new game.")
            self.islanders = []




    def tutorial(self):
        """Introduce the game and name the island."""
        print("Hello!")
        self.name = input("What would you like to name your island?\n________ Island\n\nName: ")
        print(f"Good choice. Welcome to {self.name} Island!")

    def islander_maker(self):
        """Add a new islander to the island."""
        print("\nCreate your island resident...")
        name = input("Enter the name of the new islander: ")
        gender = input("Enter gender: ")
        age = int(input("Enter age: "))
        height = int(input("Enter height (in inches): "))
        aptNum = len(self.islanders)

        islander = Islander(name, aptNum, gender, age, height)
        self.islanders.append(islander)
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
            print(f"{len(self.islanders)+1}) NVM")
            validChoice = False
            while not validChoice:
                choice = int(input("Enter a number: "))
                if 1 <= choice <= len(self.islanders):
                    print(f"Let's visit {self.islanders[choice-1].name}'s apartment!\n")
                    validChoice = True
                    self.inside_apt(self.islanders[choice-1])
                elif choice == len(self.islanders) +1:
                    validChoice = True
                    pass
                else:
                    print("Invalid choice.")

            

    def inside_apt(self, islander):
        """Enter an islander's apartment."""
        print(f"You are in {islander.name}'s home. Take your shoes off!\n")

if __name__ == "__main__":
    # Save file location
    save_file = "island_game_save.json"
    # Initialize the island and load any saved data
    leIsland = Island()
    leIsland.load_game(save_file)

    # # Show the tutorial only if no island name is loaded
    # if not leIsland.name:
    #     leIsland.tutorial()

    # Main game loop
    while True:
        leIsland.map(save_file)
