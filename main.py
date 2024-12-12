import sqlite3
from island import Island
from islander import Islander
import time

if __name__ == "__main__":
    # Save file location
    save_file = "island_game_save.json"
    # Initialize the island and load any saved data
    leIsland = Island()
    leIsland.load_game(save_file)

    # Main game loop
    while True:
        print(leIsland.timenow)
        leIsland.map(save_file)
