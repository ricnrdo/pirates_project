from game import event
from game.player import Player
from game.context import Context
from game.display import announce
import game.config as config
import random

class DistractMonkeys(Context, event.Event):
    def __init__(self):
        super().__init__()
        self.name = "Monkeys"
        self.num_of_monkeys = random.randint(3, 6)
        self.num_of_bananas_needed = 0
        self.num_of_bananas_can_give = 0
        self.prev_inventory_count = 0
        self.monkeys = {}
        self.i = 0
        # create monkeys with random of bananas they are asking for.
        while self.i < self.num_of_monkeys:
            monkey_key = f"monkey_{self.i + 1}"
            self.monkeys[monkey_key] = {"bananas": random.randint(5, 13), "done": False}
            self.i += 1

        # a counter of bananas all money are asking for so the user knows how many to collect.
        for i in self.monkeys:
            self.num_of_bananas_needed += self.monkeys[i]['bananas']

        self.verbs['give'] = self
        self.result = {}

    def process_verb(self, verb, cmd_list, nouns):
        if verb == 'give':
            announce(f"There's {self.num_of_monkeys} monkeys that want bananas")
            announce(f"You need {self.num_of_bananas_needed} bananas")
            announce(f"You can give {self.num_of_bananas_can_give} bananas")

            if self.num_of_bananas_in_inventory == 0:
                announce("You don't have any bananas. Explore the island and pick up some.")
            else:
                for monkey_key, monkey_data in self.monkeys.items():
                    bananas_needed = monkey_data['bananas']
                    # If there are enough bananas in the inventory
                    if not monkey_data['done']:
                        bananas_needed = monkey_data['bananas']
                        if self.num_of_bananas_can_give >= bananas_needed:
                            announce(f"Gave {bananas_needed} bananas to {monkey_key}.")
                            self.num_of_bananas_can_give -= bananas_needed
                            monkey_data['bananas'] -= bananas_needed
                            monkey_data['done'] = True
                        else:
                            # If there are not enough bananas, reduce the count
                            announce(f"Gave {self.num_of_bananas_can_give} bananas to {monkey_key}.")
                            monkey_data['bananas'] -= self.num_of_bananas_can_give

                            self.num_of_bananas_can_give = 0

                # Update the total bananas needed
                self.num_of_bananas_needed = sum(monkey_data['bananas'] for monkey_data in self.monkeys.values())
            self.result["message"] = "----------------------"
            self.result["newevents"] = [self]

        self.prev_inventory_count = self.num_of_bananas_in_inventory

        # elif verb == "done_1":
        #     self.monkeys['monkey_1']['done'] = True
    
    def process(self, world):
        self.num_of_bananas_in_inventory = 0
        self.access_inventory = config.the_player.inventory
        for item in self.access_inventory:
            if 'banana' in item.name:
                self.num_of_bananas_in_inventory += 1

        self.num_of_bananas_can_give += self.num_of_bananas_in_inventory - self.prev_inventory_count

        Player.get_interaction([self])

        return self.result