import sqlite3, json
from islander import Islander
from util import *
from food import buy_food
import random 
import time, datetime

class Island:
    def __init__(self, db_name="island_game.db"):
        self.seconds = time.time()
        self.local_time = time.ctime(self.seconds)
        self.timenow = datetime.datetime.now()  # Full datetime object
        # self.timenow = datetime.datetime(2024, 12, 11, hour=10,minute=30,second=0) #debugging for bedtime testing
        self.generate_new_food_dailies = False
        self.fountain_visited = False
        self.dailies_food = []
        self.db_name = db_name
        self.islanders = []
        self.saved = False
        self.name = ""
        self.last_login = None  # Use None if no value is available
        self.money = 0.0
        self.unlocked_food = {}
        self.all_food = []
        self._initialize_db()
        self.locations = ["Apartments", "Town Hall", "Fountain", "Food Mart", "Clothing Shop", "Hat Shop", "Interior Shop", "Compatibility Tester", "Beach", "Tower",
                          "Rankings Board", "Mii News", "Concert Hall", "Pawn Shop", "Photo Studio", "Amusement Park", "Park", "Cafe", "Homes"]
        self.unlocked_locations = ["Apartments", "Food Mart", "Town Hall", "Beach", "Fountain"]

        self.food_list = []
        with open("food.json", "r") as file:
            data = json.load(file)
            for i, j in data.items():
                for k in j:
                    self.food_list.append(k["name"])

        for islander in self.islanders:
            save_islander_sleeping_status(islander)

    def advance_time(self, seconds=1):
        self.timenow += datetime.timedelta(seconds=seconds)

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
            height INTEGER,
            sleeping_tonight BOOLEAN DEFAULT 1
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
        add_columns_if_not_exist(self.db_name)
    
    def save_game(self, save_file):
        """Save the current state of the game."""
        self.last_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Convert dailies_food to a comma-separated string
        dailies_food_str = ','.join(self.dailies_food) if self.dailies_food else ''

        save_game_to_db(self.name, self.islanders, dailies_food_str, self.db_name)  # Use utility function
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE island
            SET last_login = ?, dailies_food = ?
            WHERE name = ?
        ''', (self.last_login, dailies_food_str ,self.name))

        conn.commit()
        conn.close()
        self.saved = True
        print(f"Game saved. {random.choice(self.islanders).name} appreciates it!\n")
    
    def load_game(self, save_file):
        """Load the game state."""
        self.name, self.islanders, self.dailies_food, self.last_login = load_game_from_db(self.db_name)
        if self.last_login:
            print(f"last login: {self.last_login}")
        else:
            print("No previous login time recorded.")

        if self.timenow.date() != self.last_login.date():
            #Generate new dailies food list
            # print(f"timenow: {type(self.timenow.date())} , last_login: {type(self.last_login.date())}")
            # print(f"{self.timenow.strftime('%Y-%m-%d')} and {self.last_login.strftime('%Y-%m-%d')}")

            self.generate_new_food_dailies = True
        else:
            self.generate_new_food_dailies = False
        if self.generate_new_food_dailies:
            self.dailies_food = random.sample(self.food_list, 5)
        #DEBUG!!!!!!!!!!!!!!!!!
        if self.dailies_food:
            print(f"Today's food list: {', '.join(self.dailies_food)}")
        else:
            print("No daily food list recorded.")
        for i in self.islanders:
            self.reset_sleeping_status(i)

        if self.islanders:
            print(f"Welcome back to {self.name} island!\n")
            # Assuming you have a list of islanders and a 'current_time' value
            check_time_for_sleeping_randomization(self.islanders, self.timenow)

        else:
            print("Starting a new game.")
            self.tutorial()

    def is_in_time_range(self, start, end, time):
            # Ensure inputs are datetime.time objects
            if isinstance(start, datetime.timedelta):
                start = (datetime.datetime.min + start).time()
            if isinstance(end, datetime.timedelta):
                end = (datetime.datetime.min + end).time()
            if isinstance(time, datetime.timedelta):
                time = (datetime.datetime.min + time).time()

            if end < start:  # Wraparound midnight case
                return time >= start or time <= end
            return start <= time <= end


    def reset_sleeping_status(self, islander):
        # if self.last_login and (self.timenow.date() != self.last_login.date()) and self.timenow.hour >= 2:
        #     print("DEBUG!!!")
        #     islander.randomize_sleeping_tonight()
        #     islander.set_bedtime_waketime()
        #     save_islander_sleeping_status(islander)
        # wktime = datetime.datetime.strptime(str(islander.waketime), "%H:%M:%S")
        # bdtime = datetime.datetime.strptime(str(islander.bedtime), "%H:%M:%S")
        #set new waketime
        if self.timenow.hour >= 12 and self.timenow.minute >= 0 and self.last_login and self.timenow.date() != self.last_login.date():
            print(f"set new waketime for {islander.name}")
            # islander.randomize_sleeping_tonight()
            islander.set_waketime()

        #set new bedtime
        if self.timenow.hour < 20 and self.timenow.hour > 6 and self.last_login and self.timenow.date() != self.last_login.date():
            print(f"set new bedtime for {islander.name}")
            islander.set_bedtime()
            islander.randomize_sleeping_tonight()
            

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
                    if self.timenow.date() != self.last_login.date():
                        self.fountain_visited = False
                    self.fountain()
                
            elif choice == len(self.unlocked_locations) + 1:    #save game
                self.save_game(save_file)
            elif choice == len(self.unlocked_locations) + 2:    #exit game
                if self.last_login:
                    if isinstance(self.last_login, str):
                        self.last_login = datetime.datetime.strptime(self.last_login, "%Y-%m-%d %H:%M:%S")
                    time_diff = self.timenow - self.last_login
                    # print(f"time difference since last save is : {time_diff}\nsaved = {self.saved}")
                    if time_diff >= datetime.timedelta(minutes=10):
                        self.saved = False
                    else:
                        self.saved = True
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
        # for i in self.islanders:
        #     print(f"{i.name} - {i.sleeping_tonight}")
            # print_table_schema()
        # print(self.timenow) #for debugging. remove later
        print("\nApartments! Who to visit...")
        if len(self.islanders) == 0:
            print("\nNo one to visit...")
            return
        else:
            for idx, islander in enumerate(self.islanders, start=1):
                # Convert bedtime and waketime to datetime.time objects
                # bed_time_obj = datetime.datetime.strptime(islander.bedtime, '%H:%M').time()
                # wake_time_obj = datetime.datetime.strptime(islander.waketime, '%H:%M').time()



                # Check if the current time falls within the range
                # sleeping = self.is_in_time_range(bed_time_obj, wake_time_obj, self.timenow.time())

                # Assuming islander.bedtime and islander.waketime are datetime.timedelta objects
                bed_time_hours = islander.bedtime.seconds // 3600  # Extract hours from timedelta
                bed_time_minutes = (islander.bedtime.seconds // 60) % 60  # Extract minutes from timedelta

                wake_time_hours = islander.waketime.seconds // 3600  # Extract hours from timedelta
                wake_time_minutes = (islander.waketime.seconds // 60) % 60  # Extract minutes from timedelta

                # Create datetime objects for bedtime and waketime using current date to compare with timenow
                bed_time_obj = datetime.time(bed_time_hours, bed_time_minutes)
                wake_time_obj = datetime.time(wake_time_hours, wake_time_minutes)

                # Now, use these time objects in the comparison
                sleeping = self.is_in_time_range(bed_time_obj, wake_time_obj, self.timenow.time())



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
        buy_food(self.money, self.unlocked_food, self.dailies_food)
    
    def town_hall(self):
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
        if self.timenow.date() != self.last_login.date():
            self.fountain_visited = True
        print("Collecting island donations...")
        totaldonations = 0
        for i in self.islanders:
            donation = random.randint(1,5)
            print(f"{i.name} donated ${donation}!")
            totaldonations += donation
        print(f"${totaldonations} collected today")
        self.money += totaldonations

    def inside_apt(self, islander):
        """Enter an islander's apartment."""
        print(f"You are in {islander.name}'s home. Take your shoes off!\n")
        # Convert waketime and bedtime into datetime objects for comparison
        # wake_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.waketime
        # bed_datetime = datetime.datetime.combine(self.timenow.date(), datetime.time()) + islander.bedtime

        # Get the current time as a timedelta
        current_delta = datetime.timedelta(hours=self.timenow.hour, minutes=self.timenow.minute, seconds=self.timenow.second)
        # Print for debugging!!!!!!!!!!
        # print(f"\n{islander.name} sleeping tonight: {islander.sleeping_tonight}\n{islander.name}'s waketime: {islander.waketime}\n{islander.name}'s bedtime: {islander.bedtime}")

        # Use `is_in_time_range` with timedelta objects
        sleeping = self.is_in_time_range(islander.bedtime, islander.waketime, current_delta)

        if islander.sleeping_tonight and not sleeping:
            print(f"{islander.name}: heyo!!!\n")
        elif not islander.sleeping_tonight and not sleeping:
            print(f"{islander.name}: hey bud\n")
        elif not islander.sleeping_tonight:
            print(f"{islander.name}: I'm pulling an all-nighter tonight. Care to join?\n")
        else:
            print(f"{islander.name} is sleeping rn.\n")