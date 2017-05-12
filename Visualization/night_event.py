import threading
from constant import Constant
import random
import abc

class NightEvent(threading.Thread):
    __metaclass__ = abc.ABCMeta
    #events = {"monster": ["attack"],
    #          "villager": []}

    def __init__(self, creature):
        self.events = []
        self.current_event = None
        self.creature = creature
        threading.Thread.__init__(self)
        #self.game = game

    def random_event(self):
        self.current_event = random.choice(self.events)

    @abc.abstractmethod
    def perform_event(self):
        return

class MonsterNightEvent(NightEvent):

    def __init__(self, monster):
        super().__init__(monster)
        self.events = Constant.EVENTS[Constant.MONSTER]

    def perform_event(self, alive_villager_list):
        self.random_event()
        if self.current_event == Constant.ATTACK:
            self.creature.attack_villager(alive_villager_list)

    def render_event(self, screen):
        if self.creature.attacking:
            self.creature.render_attack(screen)


