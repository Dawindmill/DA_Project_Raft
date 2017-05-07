import threading
from constant import Constant
class NightEvent(threading.Thread):
    Events = {"monster": []}

    def __init__(self, game):
        self.current_event = None
        super().__init__(self)
        self.game = game

    def random_event(self):
        if self.game.day_countdown < Constant.NIGHT_TIME and self.current_event == None:
            print()