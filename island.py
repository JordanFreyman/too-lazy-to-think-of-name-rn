import sqlite3
from islander import Islander
from util import save_game_to_db, load_game_from_db
from food import buy_food
import random 
import time, datetime

class Island:
    def __init__(self, db_name="island_game.db"):
        self.seconds = time.time()
        self.local_time = time.ctime(self.seconds)
        self.timenow = datetime.datetime.now()  # Full datetime object
        # self.timenow = datetime.datetime(2024, 11, 27, hour=23,minute=11,second=0) #debugging for bedtime testing

        self.db_name = db_name
        self.islanders = []
        self.saved = False
        self.name = ""
        self.money = 0.0
        self.unlocked_food = []
        self._initialize_db()
        self.locations = ["Apartments", "Town Hall", "Fountain", "Food Mart", "Clothing Shop", "Hat Shop", "Interior Shop", "Compatibility Tester", "Beach", "Tower",
                          "Rankings Board", "Mii News", "Concert Hall", "Pawn Shop", "Photo Studio", "Amusement Park", "Park", "Cafe", "Homes"]
        self.unlocked_locations = ["Apartments", "Food Mart", "Town Hall", "Beach", "Fountain"]

    
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
        """Save the current state of the game."""
        save_game_to_db(self.name, self.islanders, self.db_name)  # Use utility function
        self.saved = True
    
    def load_game(self, save_file):
        """Load the game state."""
        self.name, self.islanders = load_game_from_db(self.db_name)  # Use utility function
        if self.islanders:
            print(f"Welcome back to {self.name} island!\n")
        else:
            print("Starting a new game.")
            self.tutorial()

    def is_in_time_range(self, start, end, time):
        if end < start:
            return start < time or end > time
        return start < time < end

    def tutorial(self):
        print("Hey, you! Welcome to The Cafeteria Room!")
        print("What would you like to name your island?\n(Will appear as '_______ Island.')\n")
        name = input("Enter name: ")
        self.name = name
        print(f"Good choice, handsome/gorgeous/mom. Welcome to {self.name} Island! Let's get started by making your first resident.")
        self.islander_maker()

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

        print("Where would you like to go?\n")
        for idx, location in enumerate(self.unlocked_locations, start=1):
            print(f"{idx}) {location}")
        print(f"{len(self.unlocked_locations)+1}) Save game\n"
              f"{len(self.unlocked_locations)+2}) Exit game")
        try:
            choice = int(input("\nChoose a number: "))
            if 1 <= choice <= len(self.unlocked_locations):
                selected_location = self.unlocked_locations[choice - 1]
                if selected_location == "Apartments":
                    self.apts()
                elif selected_location == "Food Mart":
                    self.food_mart()
                elif selected_location == "Town Hall":
                    self.town_hall()
                elif selected_location == "Beach":
                    self.beach()
                elif selected_location == "Fountain":
                    self.fountain()
                
            elif choice == len(self.unlocked_locations) + 1:    #save game
                self.save_game(save_file)
            elif choice == len(self.unlocked_locations) + 2:    #exit game
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
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def apts(self):
        """Visit an apartment of an islander."""
        print(self.timenow) #for debugging. remove later
        current_delta = datetime.timedelta(hours=self.timenow.hour, minutes=self.timenow.minute, seconds=self.timenow.second)
        print("\nApartments! Who to visit...")
        if len(self.islanders) == 0:
            print("\nNo one to visit...")
            return
        else:
            for idx, islander in enumerate(self.islanders, start=1):
                bed_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.bedtime
                wake_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.waketime

                sleeping = self.is_in_time_range(islander.bedtime, islander.waketime, current_delta)

                if islander.sleeping_tonight and sleeping:
                    print(f"{idx}) {islander.name} (asleep)")
                else:
                    print(f"{idx}) {islander.name}")
            
            #debug: check if all-nighter
            # for i in self.islanders:
            #     print(f"{i.name} chances: {i.chances}")
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

    def food_mart(self):
        print("Hey there hungry boy")
        buy_food()
    
    def town_hall(self):
        print("Business business business")
        print(f"Welcome to the Town Hall of {self.name}!\n"
              "1) New Islander\n2) Resident List\n3) Collection\n4) Settings")
        choice = int(input("Make a selection: "))
        if choice == 1:
            self.islander_maker()
        elif choice == 2:
            for i in self.islanders:
                print(f"{i.name} - {i.gender}\nAge {i.age}\t{i.height} inches tall")
        elif choice == 3:
            print("wip")
        elif choice == 4:
            print("wip")
            #settings page includes clock settings, change island name, and delete save data.

    def beach(self):
        some_islander = random.choice(self.islanders)
        print(f"{some_islander.name} is frolicking in the sand...")
    
    def fountain(self):
        print("I just farted amd it smells so bad...")

    def inside_apt(self, islander):
        """Enter an islander's apartment."""
        print(f"You are in {islander.name}'s home. Take your shoes off!\n")
        # Convert waketime and bedtime into datetime objects for comparison
        wake_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.waketime
        bed_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.bedtime

        # Get the current time as a timedelta
        current_delta = datetime.timedelta(hours=self.timenow.hour, minutes=self.timenow.minute, seconds=self.timenow.second)

        # Print for debugging
        print(f"\n{islander.name} sleeping tonight: {islander.sleeping_tonight}\n{islander.name}'s waketime: {islander.waketime}\n{islander.name}'s bedtime: {islander.bedtime}")

        # Use `is_in_time_range` with timedelta objects
        sleeping = self.is_in_time_range(islander.bedtime, islander.waketime, current_delta)
        # print(sleeping)

        # Determine the state of the islander based on the current time
        # if self.timenow > wake_datetime and self.timenow < bed_datetime and islander.bedtime.total_seconds() < 0:
        #     print(f"{islander.name}: heyo!!\n")
        # elif islander.bedtime.total_seconds() > 0 and self.timenow > wake_datetime and self.timenow > bed_datetime:
        #     print(f"{islander.name}: hey bud\n")    #fix sleeping label in apartments method
        # elif islander.sleeping_tonight == False:
        #     print(f"{islander.name}: I'm pulling an all-nighter tonight. Care to join?\n")
        # else:
        #     print(f"{islander.name} is sleeping rn.\n")
        print(islander.chances)
        if islander.sleeping_tonight and not sleeping:
            print(f"{islander.name}: heyo!!!\n")
        elif not islander.sleeping_tonight and not sleeping:
            print(f"{islander.name}: hey bud\n")
        elif not islander.sleeping_tonight:
            print(f"{islander.name}: I'm pulling an all-nighter tonight. Care to join?\n")
        else:
            print(f"{islander.name} is sleeping rn.\n")