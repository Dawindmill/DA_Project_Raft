import threading
import json
from constant import Constant
from role import Role
from debug_print import *
from queue import Queue
class VillagerListener(threading.Thread):

    def __init__(self, socket):
        self.in_msg = ""
        threading.Thread.__init__(self)
        self.host = ""
        self.listening_port = 0
        self.peer_id = ""
        self.socket = socket
        self.info_set = False
        self.request_queue = Queue()
        self.stopped = False

    def parse_message(self, msg):
        """
        Turn the JSON string received into native dictionary structure
        
        :param msg:str 
        
        """
        try:
            json_data = json.loads(msg)
            message_type = json_data[Constant.MESSAGE_TYPE]
        except Exception as e:
            debug_print(" deserialization recv json data failed " + str(e))
            return

        if message_type in Constant.MESSAGE_TYPES:
            if not self.info_set and message_type == Constant.SERVER_INFO:
                # receive the information JSON from remote Raft peer and save its details
                self.set_info(json_data)
                self.info_set = True
            else:
                return json_data
        else:
            debug_print("message type not found: "+message_type)


    def set_info(self, info):
        """
        
        Set Raft peer's information according to the 'information' JSON sent from the Raft peer
        
        :param info: dict
        
        """
        debug_print("setting info")
        self.host = info[Constant.SEND_FROM][0]
        self.listening_port = info[Constant.SEND_FROM][1]
        self.peer_id = info["peer_id"]

    def run(self):
        """
        Used to receive JSON string message from the Raft peer
        
        """
        while not self.stopped:
            try:

                temp = self.socket.recv(1024).decode("utf-8")
                # if temp == "" or None it means remote had closed the connection
                if not temp:
                    raise ConnectionResetError

                self.in_msg += temp

                if self.in_msg:
                    debug_print("in message: .")
                    debug_print(self.in_msg)
                    debug_print(".")
                # if there is new line in accumulated bytes in 'in_msg'
                # which means we have receive some complete JSON string messages
                if "\n" in self.in_msg:
                    msg_split_list = self.in_msg.split("\n")
                    # leave the incomplete JSON string in the buffer
                    self.in_msg = msg_split_list[-1]
                    msg_split_list = msg_split_list[0:-1]
                    # turn each complete JSON string into dictionary
                    # and put them into queues waiting for the Villager to consume them
                    while msg_split_list:
                        one_msg = msg_split_list.pop(0)
                        parsed = self.parse_message(one_msg)
                        if parsed:
                            self.request_queue.put(parsed)
            except ConnectionAbortedError:
                print(self.peer_id + " connection aborted")
                self.request_queue.put({Constant.MESSAGE_TYPE: Constant.VILLAGER_DEAD})
                self.stopped = True
            except ConnectionResetError:
                print(self.peer_id + " connection closed by remote host")
                self.request_queue.put({Constant.MESSAGE_TYPE: Constant.VILLAGER_DEAD})
                self.stopped = True

    def stop_listener(self):
        self.stopped = True
