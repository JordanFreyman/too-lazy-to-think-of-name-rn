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

def generate_random(food_items):
    if len(food_items) < 5:
        raise ValueError("Not enough food items to generate a selection. At least 5 items are required.")
    return random.sample(food_items, 5)


def buy_food(money, current_food, dailies_list):
    bought_food = {}
    selection = load_food_items("food.json")
    # dailies = []
    # if gen_new_food:
    #     dailies = generate_random(selection)
    #     for i in dailies:
    #         dailies_list.append(i.name)
    # else:
    #     for i in selection:
    #         if i.name in dailies_list:
    #             dailies.append(i)
    #     dailies = random.shuffle(dailies) #Fix later so it doesn't shuffle every time
    
    dailies = [food for food in selection if food.name in dailies_list]
    for i in dailies:
        print(i.name)
    choice = 0
    while choice != 3:
        print(f"Your money: ${money}")
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
                    if 1 <= food_choice <= len(dailies):
                        quantity = int(input("Cuanto? "))
                        if quantity >= 0:
                            if money >= (dailies[food_choice-1].price) * quantity:
                                print(f"you bought {quantity} {dailies[food_choice-1].name} :J")
                                bought_food[dailies[food_choice-1].name] = quantity
                                money -=  (dailies[food_choice-1].price) * quantity
                            else:
                                print("haha. POOR. no way am i letting you buy this...")
                        else:
                            print("what. what")
                    else:
                        print("ooh so close try again")
                elif choice == 2:
                    print(f"Your money: ${money}")
                    count = 0
                    for i in selection:
                        count += 1
                        print(f"{count}) {i.name} - ${i.price}\n{i.description}\n")
                    food_choice = int(input("Select a food: "))
                    if 1 <= food_choice <= len(selection):
                        quantity = int(input("Cuanto? "))
                        if quantity >= 0:
                            print(f"you bought {quantity} {selection[food_choice-1].name}")
                            bought_food[selection[food_choice-1].name] = quantity
                        else:
                            print("what. what")
                    else:
                        print("wrong")
                else:
                    # current_food.update(bought_food)
                    for food, quant in bought_food.items():
                        current_food[food] = current_food.get(food, 0) + quant
                    print(f"current food inventory: {current_food}")
                    print("See yuh again soon")
                    return money, current_food
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input. Please enter a number.")