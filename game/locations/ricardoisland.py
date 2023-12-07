from game import location
import game.config as config
import game.combat as combat
from game.display import announce
from game.events import *
import game.items as items
import random

"""
Los eventos son randoms.
Lo que puedo hacer para terminar el juego es un while loop.

Puedo crear un pirata tipo esqueleto que resguarde el tesoro. Cuando
el pirata llegue al lugar, tendra la oportunidad de pelear con el huesudo o
irse. La medicina que el pirata encuentre en la casa de arbol podra usarla para
recuperar vida, pero el huesudo le quitara vida aleatoreamente asi el pirata no
podra ganar a la primera.
"""

class Island(location.Location):
    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "island"
        self.symbol = 'R'
        self.visitable = True
        self.starting_location = Beach(self)
        self.locations = {}
        self.locations["beach"] = self.starting_location
        self.locations["treewest"] = TreeWest(self)
        self.locations["treeeast"] = TreeEast(self)
        self.locations["volcano"] = Volcano(self)
        self.locations["treehouse"] = TreeHouse(self)
        self.locations["cave"] = Cave(self)
        self.locations["tribe"] = Tribe(self)
        self.locations["treasure"] = Treasure(self)

    def enter(self, ship):
        announce("You have arrived to an island. Let's go ashore!")

    def visit (self):
        config.the_player.location = self.starting_location
        config.the_player.location.enter()
        super().visit()

class Beach(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "beach"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['east'] = self

    def enter(self):
        announce("A treasure hides in within this island. You might encounter danger along the way, try to make it out alive. Good luck!")
        announce("Verbs: north, south, west, and east")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            announce ("You return to your ship.")
            config.the_player.next_loc = config.the_player.ship
            config.the_player.visiting = False
        elif verb == "north":
            config.the_player.next_loc = self.main_location.locations["treehouse"]
        elif verb == "west":
            config.the_player.next_loc = self.main_location.locations["treewest"]
        elif verb == "east":
            config.the_player.next_loc = self.main_location.locations["treeeast"]
        else:
            announce("That's not a valid verb.")

class TreeWest(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "treewest"
        self.verbs['north'] = self
        self.verbs['east'] = self
        self.verbs['check'] = self
        self.distracted_all_monkeys = False

        if self.distracted_all_monkeys == False:
            self.event_chance = 100
            distract_monkeys_event = monkeys.DistractMonkeys()
            self.events.append(distract_monkeys_event)

    def check_monkeys_distracted(self):
        return all(monkey_data["done"] for monkey_data in self.events[0].monkeys.values())

    def enter(self):
        announce("Monkeys are blocking the way. Give them bananas to go west!")
        announce("Verbs: north, west, east, give, and check (see whether you can go west or not)")
    
    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'north':
            config.the_player.next_loc = self.main_location.locations["volcano"]
        elif verb == 'check':
            if self.check_monkeys_distracted():
                self.distracted_all_monkeys = True
                self.verbs['west'] = self
                announce("You distracted all monkeys. You can now head west.")
            else:
                announce("There's still monkeys to distract. Go find more bananas!")
        elif verb == 'west':
            if self.distracted_all_monkeys:
                config.the_player.next_loc = self.main_location.locations["tribe"]
            else:
                announce("There's a location, but you need to distract the monkeys first. Go explore the island and pick up some bananas!")
        elif verb == 'east':
            config.the_player.next_loc = self.main_location.locations["beach"]
        else:
            announce("That's not a valid verb.")


class TreeEast(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "treeeast"
        self.verbs['west'] = self
        self.verbs['north'] = self
    
    def enter(self):
        announce("Pirates can heal here only when their health is at 50ph")
        announce("Verbs: north, west")
        
        pirates_in_island = config.the_player.pirates
        for individual_pirate in pirates_in_island:
            pirate_information = individual_pirate

            if pirate_information.health <= 50 and pirate_information.health > 0:
                pirate_information.health += random.randint(1, 29)
                
            elif pirate_information.health > 100:
                pirate_information.health = 100

    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'west':
            config.the_player.next_loc = self.main_location.locations["beach"]
        elif verb == "north":
            config.the_player.next_loc = self.main_location.locations["cave"]
        else:
            announce("That's not a valid verb.")

class Volcano(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = 'volcano'
        self.verbs['banana'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.banana_pickup = 1
        
        self.event_chance = 75
        self.events.append(volcano.VolcanoEruption())
    
    def enter(self):
        announce("This volcano might erupt! But you can pick up bananas, if you survive.")
        announce("Verbs: south, east, and banana")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            config.the_player.next_loc = self.main_location.locations["treewest"]
            if self.banana_pickup == 0:
                self.banana_pickup = 1
        elif verb == "east":
            config.the_player.next_loc = self.main_location.locations["treehouse"]
            if self.banana_pickup == 0:
                self.banana_pickup = 1
        elif verb == "banana":
            if self.banana_pickup == 1:
                i = 0
                banana_counter = random.randint(3, 9)
                while i < banana_counter:
                    config.the_player.add_to_inventory([items.Bananas()])
                    i += 1
                self.banana_pickup -= 1
                announce("Check your inventory. Bananas have been added!")
            else:
                announce("You cannot pickup bananas infinitely. Come back later and more bananas will appear.")
        else:
            announce("That's not a valid verb.")

class TreeHouse(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = 'treehouse'
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['east'] = self
        self.verbs['banana'] = self
        self.bananas = items.Bananas()
        self.counter_for_bananas = 5
        self.banana_pickup = 1

    def enter(self):
        announce("This is your safe spot. You won't face danger here. If you're lucky, you'll find some items needed for your mission on this island.")
        announce("Verbs: south, west, east, and banana")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'south':
            config.the_player.next_loc = self.main_location.locations["beach"]
            if self.banana_pickup == 0:
                self.banana_pickup = 1
        elif verb == 'west':
            config.the_player.next_loc = self.main_location.locations["volcano"]
            if self.banana_pickup == 0:
                self.banana_pickup = 1
        elif verb == 'east':
            config.the_player.next_loc = self.main_location.locations["cave"]
            if self.banana_pickup == 0:
                self.banana_pickup = 1
        elif verb == 'banana':
            if self.banana_pickup == 0:
                announce("You already picked up bananas, come back later!")
            else:
                if self.counter_for_bananas == 0:
                    announce("There's no more bananas to take")
                else:
                    i = 0
                    banana_counter = random.randint(2, 4)
                    while i < banana_counter:
                        config.the_player.add_to_inventory([items.Bananas()])
                        i += 1
                    self.banana_pickup -= 1
                    self.counter_for_bananas -= 1
                    announce("Check your inventory. Bananas have been added!")
        else:
            announce("That's not a valid verb.")
            
        # elif verb == 'sword':
        #     announce("You got a nice sword! In case of an attack, you will be able to use this sword!")
        #     config.the_player.add_to_inventory([items.Sword])


class Cave(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = 'cave'
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['banana'] = self
        self.bananas = items.Bananas()
        self.random_count_bananas = random.randint(1, 4)
        self.counter = 0

        self.event_chance = 100
        self.events.append(bats_in_cave.BatsEvent())

    def enter(self):
        announce("This place is a little dark. Be careful!")
        announce("Verbs: south, west, and banana")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'south':
            config.the_player.next_loc = self.main_location.locations["treeeast"]
        elif verb == 'west':
            config.the_player.next_loc = self.main_location.locations["treehouse"]
        elif verb == 'banana':
            self.random_count_bananas = random.randint(1, 4)
            while self.counter < self.random_count_bananas:
                config.the_player.add_to_inventory([self.bananas])
                self.counter += 1
            announce("Check your inventory. Bananas have been added!")
        else:
            announce("That's not a valid verb.")

class Tribe(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = 'tribe'
        self.verbs['north'] = self
        self.verbs['east'] = self
        self.verbs['meet'] = self

    def enter(self):
        announce("There's a tribe in this location! Let's meet them")
        announce("Verbs: north, east, and meet")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'meet':
            announce("I am Jordan, the leader.")
            answer = input("You must be here for the treasure? (Y): ")
            if answer == "y" or answer == "Y":
                announce("Treasure is located north, but it won't be easy. You must solve a riddle in order to win the treasure! Good luck pirate!")
        elif verb == 'north':
            config.the_player.next_loc = self.main_location.locations["treasure"]
        elif verb == 'east':
            config.the_player.next_loc = self.main_location.locations["treewest"]
        else:
            announce("That's not a valid verb.")

class Treasure(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Riddles"
        self.verbs['south'] = self
        self.treasureWon = False

    def enter(self):
        announce("Welcome to Treasure!")

        if self.treasureWon == False:
            questions_asked = set()
            correct_answers = 0

            while correct_answers < 3:
                riddle = self.GetUniqueRiddleAndAnswer(questions_asked)
                guesses = 1

                while guesses > 0:
                    announce(riddle[0])
                    plural = "" if guesses != 1 else "s"
                    announce(f"You may guess {guesses} more time{plural}.")
                    choice = input("What is your guess? ")
                    if riddle[1].lower() in choice.lower(): 
                        announce("You have guessed correctly!")
                        correct_answers += 1
                        break
                    else:
                        guesses -= 1
                        announce("You have guessed incorrectly. Please try again.")

                if guesses <= 0:
                    announce(f"You've run out of guesses! The correct answer was {riddle[1]}. Restarting...")

            if correct_answers == 3:
                announce("Congratulations! You've answered three different questions correctly and found the treasure!")
                for i in config.the_player.get_pirates():
                    i.lucky = True
                    i.sick = False
                    i.health = i.max_health
                self.treasureWon = True
        else:
            announce("You already got the treasure!")

    def GetUniqueRiddleAndAnswer(self, questions_asked):
        riddleList = [
            ("What is black and white and red all over?", "newspaper"),
            ("What do you call a cow with no legs?", "ground beef"),
            ("What has many rings but no finger?", "phone"),
            ("What goes up but never goes down?", "age")
        ]
        available_questions = [riddle for riddle in riddleList if riddle[0] not in questions_asked]
        if not available_questions:
            questions_asked.clear()
            available_questions = riddleList

        chosen_riddle = random.choice(available_questions)
        questions_asked.add(chosen_riddle[0])
        return chosen_riddle


    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            announce ("You return to the tribe!")
            config.the_player.next_loc = self.main_location.locations["tribe"]
