
"""

Author: Bingfeng Liu
Date Created: 23/04/2017

"""
import time
import socket
import logging
import json
from queue import Queue
from collections import deque
import _thread
import threading
import ast

FORMAT = '[%(module)s][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG, filename="user_log_file", filemode="w")
logger = logging.getLogger("User")

class User:
    def __init__(self, servers_addr_port_list):
        self.first_start = True
        self.lock = threading.RLock()
        self.my_addr_port = None
        self.leader_socket = None
        # socket.socket() only return (socket, addr_port_tuple) => addr_port_tuple is self's
        self.receive_socket_thread = None
        # get remote connection's port and addr
        # self.receive_socket_thread.getpeername()
        self.servers_addr_port_list = servers_addr_port_list
        # dictionary
        self.json_message_recv_queue = Queue()
        # dictioanry
        self.json_message_send_queue = Queue()
        self.my_detail = {"host": "random host", "port": "random port", "peer_id": "user"}
        self.peer_connection_index = -1
        try:
            #use argument (first_arg, second_arg, ) note the extra last comma might be needed?
            _thread.start_new_thread(self.process_json_message_send_queue, ())
            logger.debug( " start thread => process_json_message_send_queue successful ", extra = self.my_detail)
            _thread.start_new_thread(self.process_json_message_recv_queue, ())
            logger.debug( " start thread => process_json_message_recv_queue successful ", extra = self.my_detail)
            self.input_thread = None #_thread.start_new_thread(self.take_user_input, ())
            #logger.debug(" start thread => take_user_input successful ", extra=self.my_detail)
            _thread.start_new_thread(self.receive_from_one_peer_newline_delimiter, ())
            logger.debug(" start thread => receive_from_one_peer_newline_delimiter successful ", extra=self.my_detail)
        except Exception as e:
            logger.debug( "Error: unable to start processing threads " + str(e), extra = self.my_detail)

        logger.debug(" start connect_to_next_peer ", extra=self.my_detail)
        self.connect_to_next_peer()
        # self.connect_to_next_peer()

    def connect_to_next_peer(self):
        print("Connecting to leader ... ")
        are_you_leader = {"msg_type": "request_command",
                          "request_command_list":[]}
        while True:
            with self.lock:
                if self.leader_socket is not None:
                    self.leader_socket.shutdown(socket.SHUT_RDWR)
                if self.input_thread is not None:
                    self.input_thread.exit()
                    self.input_thread = None
                self.json_message_send_queue.empty()
                self.leader_socket = None
                self.peer_connection_index += 1
                if self.peer_connection_index >= len(self.servers_addr_port_list):
                    self.peer_connection_index = 0
                try:
                    print("try to connect " + str(self.servers_addr_port_list[self.peer_connection_index]))
                    leader_socket = socket.socket()
                    leader_socket.connect(self.servers_addr_port_list[self.peer_connection_index])
                    print("connect successfully")
                    are_you_leader["send_to"] = list(leader_socket.getpeername())
                    are_you_leader["send_from"] = list(leader_socket.getsockname())
                    self.leader_socket = leader_socket
                    self.json_message_send_queue.put(are_you_leader)
                    break
                except Exception as e:
                    logger.debug("Error: unable to connect " + str(self.servers_addr_port_list[self.peer_connection_index]) + ", exception => " + str(e), extra=self.my_detail)
                    continue
        print ("Try find leader :], " + str(leader_socket))

    def take_user_input(self):
        #self.connect_to_next_peer()
        print("Enter your command as a list [var_name, command_name， action_param]")
        while True:
            temp_input_list = input("$ ")
            # turn string representation of list into list
            try:
                temp_input_list = ast.literal_eval(temp_input_list)
            except Exception as e:
                print("Invalid input try again " + str(e))
                continue
            if len(temp_input_list) != 3:
                print ("command input with wrong number of params")
                continue
            with self.lock:
                leader_socket = self.leader_socket
            while True:
                if leader_socket == None:
                    time.sleep(0.02)
                    continue
                else:
                    command_send_json_dict = {"msg_type": "request_command",
                                              "request_command_list": temp_input_list,
                                              "send_from": list(leader_socket.getsockname())}
                    break
            self.json_message_send_queue.put(command_send_json_dict)

    def process_json_message_send_queue(self):
        while True:
            one_json_data_dict = self.json_message_send_queue.get()
            logger.debug( " processing one send message " + str(one_json_data_dict), extra = self.my_detail )
            # in json encode it is two element list
            self.send_to_peer(one_json_data_dict)

    def process_json_message_recv_queue(self):
        while True:
            logger.debug(" start receive ", extra=self.my_detail)
            one_recv_json_message_dict = self.json_message_recv_queue.get()

            logger.debug( " processing one recv message " + str(one_recv_json_message_dict), extra = self.my_detail )
            #in json encode it is two element list
            #sendpeer_addr, peer_port = one_recv_json_message_dict["send_from"]

            one_recv_json_message_type = one_recv_json_message_dict["msg_type"]
            receive_processing_functions = {"request_command_reply":self.request_command_request_reply}
            receive_processing_function = receive_processing_functions[one_recv_json_message_type]
            receive_processing_function(one_recv_json_message_dict)

    def request_command_request_reply(self, one_recv_json_message_dict):
        if one_recv_json_message_dict["command_result"] == "not_leader":
            print(one_recv_json_message_dict["command_result"] + " finding leaders now")
            self.connect_to_next_peer()
        elif one_recv_json_message_dict["command_result"] == "is_leader":
            print("leader found " + str(self.leader_socket))
            self.input_thread = _thread.start_new_thread(self.take_user_input, ())
            print("leader found end" + str(self.leader_socket))
        else:
            print(" command result => " + str(one_recv_json_message_dict["command_result"]))


    def send_to_peer(self, json_data_dict):
        logger.debug(" sending json_data to " + str(self.leader_socket), extra=self.my_detail)
        with self.lock:
            peer_socket = self.leader_socket
        if peer_socket == None:
            logger.debug(" no leader socket now, abort sending ", extra = self.my_detail)
            return
        try:
            json_data_dict["send_to"] = list(peer_socket.getpeername())
            serialized_json_data = json.dumps(json_data_dict)
            logger.debug(" json data serialization " + serialized_json_data, extra = self.my_detail)
            #send msg size
            #peer_socket.send(str.encode(str(len(serialized_json_data))+"\n", "utf-8"))
            #logger.debug(" json data sent len " + str(len(serialized_json_data)), extra = self.my_detail)
        except Exception as e:
            logger.debug("command abort json data serialization failed " + str(json_data_dict) + str(e), extra = self.my_detail)
            return
        try:
            peer_socket.sendall(str.encode(serialized_json_data + "\n","utf-8"))
        except Exception as e:
            if "request_command" in json_data_dict:
                if json_data_dict["request_command_list"] != []:
                    print(" command send failed, plz try again when found leader, remote connection closed")
            logger.debug("send failed reconnect to leader now" + str(json_data_dict) + str(e), extra=self.my_detail)

            self.connect_to_next_peer()

        #make it utf8r


    def receive_from_one_peer_newline_delimiter(self):
        logger.debug(" recv json_data from " + str(self.leader_socket), extra = self.my_detail)

        msg = ""
        #could be wrong if msg size bigger than 1024, need further testing
        while True:

            with self.lock:
                peer_socket = self.leader_socket

            if peer_socket == None:
                logger.debug(" no leader socket now, abort receiving ", extra=self.my_detail)
                time.sleep(0.1)
                continue
            try:
                msg += peer_socket.recv(1024).decode("utf-8")
            except Exception as e:
                logger.debug(" leader socket terminated, receive failed " + str(e), extra=self.my_detail)
                # this exception will be triggered if we want to send something
                # self.connect_to_next_peer()
                continue

            if "\n" in msg:
                msg_split_list = msg.split("\n")
                msg = msg_split_list[-1]
                for one_json_msg in msg_split_list[0:-1]:
                    try:
                        logger.debug(" recv one json_data " + one_json_msg, extra = self.my_detail)
                        one_deserialized_json_data = json.loads(one_json_msg)
                        self.json_message_recv_queue.put(one_deserialized_json_data)
                        logger.debug(" put one json_data " + one_json_msg, extra = self.my_detail)
                    except Exception as e:
                        logger.debug( " deserialization recv json data failed " + str(e), extra = self.my_detail)


if __name__ == '__main__':
    peer1 = ("localhost", 1119)
    peer2 = ("localhost", 2229)
    peer3 = ("localhost", 3339)
    #peer4 = ("localhost", 4449)
    #peer5 = ("localhost", 5559)

    # peer_addr_port_tuple_list = [peer1, peer2, peer3, peer4, peer5]
    peer_addr_port_tuple_list = [peer1, peer2, peer3]
    user = User(peer_addr_port_tuple_list)
    time.sleep(10000000)
