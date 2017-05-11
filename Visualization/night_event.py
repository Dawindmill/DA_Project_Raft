import threading
from constant import Constant
import random

class NightEvent(threading.Thread):
    events = {"monster": ["attack"],
              "villager": []}

    def __init__(self):
        self.current_event = None
        threading.Thread.__init__(self)
        #self.game = game

    def getEvent(self):
        print(random.choice(self.events["monster"]))