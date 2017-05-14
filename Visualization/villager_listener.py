import threading
import json
from constant import Constant
from role import Role
from debug_print import *
class VillagerListener(threading.Thread):

    def __init__(self, socket):
        #self.villager = villager
        self.in_msg = ""
        threading.Thread.__init__(self)
        self.host = ""
        self.listening_port = 0
        self.peer_id = ""
        self.socket = socket
        self.info_set = False
        self.request_queue = []

    def parse_message(self, msg):
        try:
            json_data = json.loads(msg)
            message_type = json_data[Constant.MESSAGE_TYPE]
        except Exception as e:
            debug_print(" deserialization recv json data failed " + str(e))
            return

        if message_type in Constant.MESSAGE_TYPES:
            if not self.info_set and message_type == Constant.SERVER_INFO:
                self.set_info(json_data)
                self.info_set = True
            else:
                return json_data
        else:
            debug_print("message type not found: "+message_type)


    def set_info(self, info):
        debug_print("setting info")
        self.host = info[Constant.SEND_FROM][0]
        self.listening_port = info[Constant.SEND_FROM][1]
        self.peer_id = info["peer_id"]

    def run(self):
        while True:
            try:
                self.in_msg += self.socket.recv(1024).decode("utf-8")
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
                            self.request_queue.append(parsed)
            except ConnectionAbortedError:
                print(self.peer_id + " connection aborted")
                self.wait()



            #debug_print("message list: ")
            #debug_print(self.messages)