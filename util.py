# util.py
import sqlite3
from islander import Islander
import datetime, random

def ensure_last_login_column(db_name):
    """Ensure the last_login and money columns exist in the island table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if 'last_login' and 'money' columns exist
    cursor.execute("PRAGMA table_info(island);")
    columns = [col[1] for col in cursor.fetchall()]

    if "last_login" not in columns:
        cursor.execute("ALTER TABLE island ADD COLUMN last_login TEXT")
    
    if "money" not in columns:
        cursor.execute("ALTER TABLE island ADD COLUMN money INTEGER DEFAULT 0")  # Default to 0

    conn.commit()
    conn.close()


def dailies_food_column(db_name="island_game.db"):
    """Ensure the dailies_food column exists in the island table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the column exists
    cursor.execute("PRAGMA table_info(island)")
    columns = [row[1] for row in cursor.fetchall()]  # Column names are in the second field (index 1)

    if "dailies_food" not in columns:
        cursor.execute('ALTER TABLE island ADD COLUMN dailies_food TEXT')

    conn.commit()
    conn.close()




def save_game_to_db(island, islanders, dailies_food, money, db_name="island_game.db"):
    """Save the current state of the game to the SQLite database."""
    ensure_last_login_column(db_name)
    dailies_food_column(db_name)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ensure tables exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS island (
        name TEXT,
        last_login TEXT,
        dailies_food TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS islanders (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        gender TEXT,
        age INTEGER,
        height REAL,
        sleeping_tonight INTEGER,
        bedtime INTEGER,
        waketime INTEGER
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appearance (
        islander_id INTEGER,
        hair TEXT,
        eyes TEXT,
        voice TEXT,
        FOREIGN KEY(islander_id) REFERENCES islanders(id)
    )''')

    # Save island details
    cursor.execute('''
        INSERT OR REPLACE INTO island (name, last_login, dailies_food, money)
        VALUES (?, ?, ?, ?)
    ''', (island, datetime.datetime.now().isoformat(), ','.join(dailies_food), money))

    # cursor.execute("UPDATE island SET last_login = ? WHERE last_login IS NULL", (datetime.datetime.now().isoformat(),))

    # Save islanders
    for islander in islanders:
        cursor.execute('SELECT id FROM islanders WHERE name = ?', (islander.name,))
        existing_islander = cursor.fetchone()

        bedtime_seconds = int(islander.bedtime.total_seconds())
        waketime_seconds = int(islander.waketime.total_seconds())

        if existing_islander:
            # Update existing record
            cursor.execute('''
            UPDATE islanders 
            SET gender = ?, age = ?, height = ?, sleeping_tonight = ?, bedtime = ?, waketime = ?
            WHERE id = ?
            ''', (
                islander.gender, islander.age, islander.height,
                int(islander.sleeping_tonight), bedtime_seconds, waketime_seconds,
                existing_islander[0]
            ))
        else:
            # Insert new record
            cursor.execute('''
            INSERT INTO islanders (name, gender, age, height, sleeping_tonight, bedtime, waketime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                islander.name, islander.gender, islander.age, islander.height,
                int(islander.sleeping_tonight), bedtime_seconds, waketime_seconds
            ))

    conn.commit()
    conn.close()


def load_game_from_db(db_name="island_game.db"):
    """Load the game state from the SQLite database without overwriting valid bedtimes and waketimes."""
    islanders = []
    island_name = ""
    last_login = None  # Use None if no value is available
    dailies_food = []
    money = 0
    ensure_last_login_column(db_name)
    # print_table_schema(db_name)
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # # Fetch the island name
        # cursor.execute('SELECT * FROM island')
        # row = cursor.fetchall()
        # if row:
        #     island_name = row[0][0]
        #     last_login = datetime.datetime.fromisoformat(row[0][1]) if len(row[0]) > 1 and row[0][1] else None
            
        #     # Check if the column for dailies_food exists
        #     if len(row[0]) > 2 and row[0][2]:  # Ensure the 3rd column exists and has data
        #         dailies_food = row[0][2].split(',')  # Split by commas if dailies_food exists
        #     else:
                # dailies_food = []  # If not, assign an empty list

        cursor.execute('SELECT name, last_login, dailies_food, money FROM island LIMIT 1')
        row = cursor.fetchone()

        if row:
            island_name, last_login_str, dailies_food_str, money = row
            last_login = datetime.datetime.fromisoformat(last_login_str) if last_login_str else None
            dailies_food = dailies_food_str.split(',') if dailies_food_str else []
        else:
            money = 0  # Default value if no record exists


        # Fetch all islanders
        cursor.execute('SELECT * FROM islanders')
        rows = cursor.fetchall()

        for row in rows:
            (
                islander_id, name, gender, age, height, 
                sleeping_tonight, bed_time_seconds, wake_time_seconds
            ) = row

            # Create the Islander object
            islander = Islander(name, gender, age, height, bool(sleeping_tonight))

            # Ensure bed_time_seconds and wake_time_seconds are integers (handle if they are strings or None)
            try:
                bed_time_seconds = int(float(bed_time_seconds)) if bed_time_seconds else 0
            except ValueError:
                bed_time_seconds = 0  # Default to 0 if conversion fails

            try:
                wake_time_seconds = int(float(wake_time_seconds)) if wake_time_seconds else 0
            except ValueError:
                wake_time_seconds = 0  # Default to 0 if conversion fails


            # Handle bedtime
            if bed_time_seconds is None or bed_time_seconds == 0:
                # Randomize only if missing or invalid
                startbed_seconds = 21 * 3600 + 30 * 60  # 9:30 PM
                endbed_seconds = (1 + 24) * 3600 + 30 * 60  # 1:30 AM next day
                bed_rand_seconds = random.randint(startbed_seconds, endbed_seconds)
                islander.bedtime = datetime.timedelta(seconds=bed_rand_seconds % (24 * 3600))
            else:
                islander.bedtime = datetime.timedelta(seconds=int(bed_time_seconds))

            # Handle waketime
            if wake_time_seconds is None or wake_time_seconds == 0:
                # Randomize only if missing or invalid
                start_seconds = 6 * 3600 + 30 * 60  # 6:30 AM
                end_seconds = 10 * 3600  # 10:00 AM
                rand_seconds = random.randint(start_seconds, end_seconds)
                islander.waketime = datetime.timedelta(seconds=rand_seconds)
            else:
                islander.waketime = datetime.timedelta(seconds=int(wake_time_seconds))

            # Fetch appearance details
            cursor.execute('SELECT * FROM appearance WHERE islander_id = ?', (islander_id,))
            appearance_row = cursor.fetchone()
            if appearance_row:
                islander.hair, islander.eyes, islander.voice = appearance_row[1:]

            islanders.append(islander)

        conn.close()
    except sqlite3.Error as e:
        print(f"Error loading game: {e}")
    return island_name, islanders, dailies_food, last_login, money




# def load_game_from_db(db_name="island_game.db"):
#     """Load the game state from the SQLite database."""
#     islanders = []
#     island_name = ""
#     try:
#         conn = sqlite3.connect(db_name)
#         cursor = conn.cursor()

#         #Fetch the island name from the island table
#         cursor.execute('SELECT name FROM island')
#         row = cursor.fetchone()
#         if row:
#             island_name = row[0]

#         # Fetch all islanders
#         cursor.execute('SELECT * FROM islanders')
#         rows = cursor.fetchall()

#         for row in rows:
#             # Ensure enough columns are present
#             if len(row) >= 5:
#                 name, gender, age, height, sleeping_tonight = row[1], row[2], row[3], row[4], row[5]

#                 startbed_seconds = 21 * 3600 + 30 * 60  # 9:30 PM in seconds
#                 endbed_seconds = (1 + 24) * 3600 + 30 * 60  # 1:30 AM (next day) in seconds
#                 bed_rand_seconds = random.randint(startbed_seconds, endbed_seconds)
#                 bedtime = row[6] if len(row) > 6 else datetime.timedelta(seconds=bed_rand_seconds % (24 * 3600))

#                 start_seconds = 6 * 3600 + 30 * 60  # 6:30 AM in seconds
#                 end_seconds = 10 * 3600  # 10:00 AM in seconds
#                 rand_seconds = random.randint(start_seconds, end_seconds)
#                 waketime = row[7] if len(row) > 7 else datetime.timedelta(seconds=rand_seconds)

#                 islander = Islander(name, gender, age, height, bool(sleeping_tonight))
#                 islander.bedtime = bedtime
#                 islander.waketime = waketime

#                 # Load appearance details
#                 cursor.execute('SELECT * FROM appearance WHERE islander_id = ?', (row[0],))
#                 appearance_row = cursor.fetchone()

#                 if appearance_row:
#                     islander.hair = appearance_row[1]
#                     islander.eyes = appearance_row[2]
#                     islander.voice = appearance_row[3]
#                 print(f"Loading {islander.name}: sleeping_tonight={islander.sleeping_tonight}")

#                 islanders.append(islander)
#         conn.close()
#     except sqlite3.Error as e:
#         print(f"Error loading game: {e}")
#     return island_name, islanders

def save_islander_sleeping_status(islander, db_name="island_game.db"):
    """Save sleeping_tonight status for an islander to the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE islanders SET sleeping_tonight = ? WHERE name = ?",
            (int(islander.sleeping_tonight), islander.name),
        )
        conn.commit()
        print(f"Loaded {islander.name}: sleeping_tonight={islander.sleeping_tonight}")
        conn.close()
    except sqlite3.Error as e:
        print(f"Error saving sleeping status: {e}")

def add_columns_if_not_exist(db_name="island_game.db"):
    """Ensure the database has bedtime and waketime columns."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Check if 'bedtime' and 'waketime' columns exist
    cursor.execute("PRAGMA table_info(islanders);")
    columns = [col[1] for col in cursor.fetchall()]
    if "bedtime" not in columns:
        cursor.execute("ALTER TABLE islanders ADD COLUMN bedtime TEXT DEFAULT '{bedtime}'")
    if "waketime" not in columns:
        cursor.execute("ALTER TABLE islanders ADD COLUMN waketime TEXT DEFAULT '{waketime}'")
    conn.commit()
    conn.close()



# add_column_if_not_exists()
def print_table_schema(db_name="island_game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(islanders);")
    cursor.execute("PRAGMA table_info(island);")
    schema = cursor.fetchall()
    conn.close()
    print(schema)


def check_time_for_sleeping_randomization(islanders, current_time):
    """Check if it's time to randomize sleeping_tonight for each islander."""
    for islander in islanders:
        # Get the hour after the islander's waketime
        waketime_hour = islander.waketime.seconds // 3600  # Convert waketime from timedelta to hour
        hour_after_wake = waketime_hour + 1  # The hour after the islander's wake time
        
        # Get the current hour
        current_hour = current_time.hour
        
        # Check if the current time is the hour after the islander's waketime
        if current_hour == hour_after_wake:
            islander.randomize_sleeping_tonight()