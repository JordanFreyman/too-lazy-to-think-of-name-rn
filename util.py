# util.py
import sqlite3
from islander import Islander

def save_game_to_db(island, islanders, db_name="island_game.db"):
    """Save the current state of the game to the SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS island (
        name TEXT
    )''')

    cursor.execute('''
    INSERT OR REPLACE INTO island (name) VALUES (?)
    ''', (island,))
    
    # Save islander's main details
    for islander in islanders:
        cursor.execute('SELECT id FROM islanders WHERE name = ?', (islander.name,))
        existing_islander = cursor.fetchone()

        if existing_islander:
            # Update existing record
            islander_id = existing_islander[0]
            cursor.execute('''
            UPDATE islanders 
            SET gender = ?, age = ?, height = ?
            WHERE id = ?
            ''', (islander.gender, islander.age, islander.height, islander_id))

            # Update appearance details
            cursor.execute('''
            UPDATE appearance
            SET hair = ?, eyes = ?, voice = ?
            WHERE islander_id = ?
            ''', (islander.hair, islander.eyes, islander.voice, islander_id))
        else:
            # Insert new islander
            cursor.execute('''
            INSERT INTO islanders (name, gender, age, height)
            VALUES (?, ?, ?, ?)
            ''', (islander.name, islander.gender, islander.age, islander.height))

            islander_id = cursor.lastrowid

            # Insert appearance details
            cursor.execute('''
            INSERT INTO appearance (islander_id, hair, eyes, voice)
            VALUES (?, ?, ?, ?)
            ''', (islander_id, islander.hair, islander.eyes, islander.voice))

    conn.commit()
    conn.close()
    print("Game saved.")

def load_game_from_db(db_name="island_game.db"):
    """Load the game state from the SQLite database."""
    islanders = []
    island_name = ""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        #Fetch the island name from the island table
        cursor.execute('SELECT name FROM island')
        row = cursor.fetchone()
        if row:
            island_name = row[0]

        # Fetch all islanders
        cursor.execute('SELECT * FROM islanders')
        rows = cursor.fetchall()

        for row in rows:
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

                islanders.append(islander)

        conn.close()
    except sqlite3.Error as e:
        print(f"Error loading game: {e}")
    return island_name, islanders
