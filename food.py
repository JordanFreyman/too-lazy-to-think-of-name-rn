import json
import random

class FoodItem:
    def __init__(self, name, description, category, price):
        self.name = name
        self.description = description
        self.category = category
        self.price = price

def load_food_items(json_filename="food.json"):
    food_items = []
    with open(json_filename, "r") as file:
        data = json.load(file)
        for category, items in data.items():
            for item in items:
                food_item = FoodItem(item["name"], item["description"], category ,item["price"])
                food_items.append(food_item)
    return food_items

# def generate_random(food_items, num_items=5):
#     return random.sample(food_items, num_items)

# def generate_random(food_items):
#     selected_items = []
#     while len(selected_items) < 5:
#         rand = random.randint(0, len(food_items) - 1)  # Ensure the index is in range
#         if food_items[rand] not in selected_items:
#             selected_items.append(food_items[rand])
#     return selected_items

def generate_random(food_items):
    if len(food_items) < 5:
        raise ValueError("Not enough food items to generate a selection. At least 5 items are required.")
    return random.sample(food_items, 5)


def buy_food(money, current_food, randomize, dailies_strings):
    bought_food = {}
    selection = load_food_items("food.json")
    selection_strings = []
    for i in selection:
        selection_strings.append(i.name)
    if randomize:
        dailies = generate_random(selection)
    for i in dailies:
        dailies_strings.append(i.name)
    
    print("(1) Daily Specials, or (2) In Stock?\n(3) Exit\n")
    try:
        choice = int(input("Make a selection: "))
        if 1 <= choice <= 3:
            if choice == 1:
                print(f"Your money: ${money}")
                count = 0
                for i in dailies:
                    count += 1
                    print(f"{count}) {i.name} - ${i.price}\n{i.description}\n")
                food_choice = int(input("Select a food: "))
                quantity = int(input("Cuanto? "))
                if 1 <= food_choice <= len(dailies):
                    print(f"you bought {quantity} {dailies[food_choice-1].name}")
                    bought_food[dailies[food_choice-1]] = quantity
                else:
                    print("wrong")
            elif choice == 2:
                print(f"Your money: ${money}")
                count = 0
                for i in selection:
                    count += 1
                    print(f"{count}) {i.name} - ${i.price}\n{i.description}\n")
                food_choice = int(input("Select a food: "))
                quantity = int(input("Cuanto? "))
                if 1 <= food_choice <= len(selection):
                    print(f"you bought {quantity} {selection[food_choice-1].name}")
                    bought_food[dailies[food_choice-1]] = quantity
                else:
                    print("wrong")
            else:
                current_food.update(bought_food)
                print("See yuh again soon")
                return dailies_strings
        else:
            print("Invalid input.")
    except ValueError:
        print("Invalid input. Please enter a number.")