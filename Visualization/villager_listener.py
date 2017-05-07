import threading
import json
from constant import Constant
from role import Role
from debug_print import *
class VillagerListener(threading.Thread):

    def __init__(self, villager):
        self.villager = villager
        self.in_msg = ""
        threading.Thread.__init__(self)

    def parse_message(self, msg):
        try:
            json_data = json.loads(msg)
            message_type = json_data[Constant.MESSAGE_TYPE]
        except Exception as e:
                debug_print(" deserialization recv json data failed " + str(e))

        if message_type in Constant.MESSAGE_TYPES:
            return json_data
        else:
            debug_print("message type not found: "+message_type)

    def run(self):
        while True:
            self.in_msg += self.villager.socket.recv(1024).decode("utf-8")
            if self.in_msg:
                debug_print("in message: .")
                debug_print(self.in_msg)
                debug_print(".")
            if "\n" in self.in_msg:
                msg_split_list = self.in_msg.split("\n")
                self.in_msg = msg_split_list[-1]
                msg_split_list = msg_split_list[0:-1]
                while msg_split_list:
                    one_msg = msg_split_list.pop(0)
                    parsed = self.parse_message(one_msg)
                    if parsed:
                        self.villager.requests.append(parsed)

            #debug_print("message list: ")
            #debug_print(self.messages)