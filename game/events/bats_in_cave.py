import game.event as event
import random
import game.combat as combat
import game.superclasses as superclasses
from game.display import announce

class BatsEvent(event.Event):
    def __init__ (self):
        self.name = "bats in the cave"

    def process (self, world):
        result = {}
        result["message"] = "the bats are defeated!"
        monsters = []
        min = 2
        uplim = 6
        if random.randrange(2) == 0:
            min = 1
            uplim = 5
            monsters.append(combat.Bat("Big Bat"))
            monsters[0].speed = 1.2*monsters[0].speed
            monsters[0].health = 2*monsters[0].health
        n_appearing = random.randrange(min, uplim)
        n = 1
        while n <= n_appearing:
            monsters.append(combat.Bat("Bat's "+str(n)))
            n += 1
        announce ("You are attacked by a crew of bats!")
        combat.Combat(monsters).combat()
        result["newevents"] = [ self ]
        return result
