from game import event
import random
from game.combat import Combat
from game.combat import Macaque
from game.display import announce
import game.config as config

class VolcanoEruption(event.Event):
    def __init__(self):
        self.name = "Volcano might erupt!"

    def process(self, world):
        announce("Volcano has erupted!")
        pirates_in_island = config.the_player.pirates
        counter_of_pirates = 0
        result = {}
        for i in pirates_in_island:
            counter_of_pirates += 1

        self.no_kill_pirates = random.randint(1, counter_of_pirates // 2)
        self.list_of_pirates_to_kill = []
        self.stop = 0

        while self.stop < self.no_kill_pirates:
            self.list_of_pirates_to_kill.append(random.choice(config.the_player.pirates))
            self.stop += 1
        
        for i in self.list_of_pirates_to_kill:
            i.health -= 100
            result["message"] = f"{i.name} has been killed by magma!"
            result["newevents"] = [self, VolcanoEruption()]
        
        if len(config.the_player.pirates) > 0:
            for i in config.the_player.pirates:
                i.health -= random.randint(10, 24)
        
        return result