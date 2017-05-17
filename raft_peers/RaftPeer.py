"""


Author: Bingfeng Liu

This is the class to process and send the json message
between peer communications.


"""

import _thread
import json
import os

import jsonpickle
import random
import socket
import logging
from queue import Queue

import sys

from RaftPeerState import RaftPeerState
from LogData import LogData
from TimeoutCounter import TimeoutCounter
from RequestVote import RequestVote
from RequestVoteReceive import RequestVoteReceive
from AppendEntriesFollower import AppendEntriesFollower
from AppendEntriesLeader import AppendEntriesLeader
from RemoteVar import RemoteVar
import time
import threading
import copy

logger = logging.getLogger("RaftPeer")


# this RaftPeer is inspired from http://lesoluzioni.blogspot.com.au/2015/12/python-json-socket-serverclient.html
class RaftPeer:
    backlog = 5
    recv_buffer_size = 1024

    # thread safe queue FIFO
    # https://docs.python.org/2/library/queue.html

    def __init__(self, host, port, user_port, peer_id, max_peer_number, append_entries_timeout, min_leader_election_timeout, max_leader_election_timeout):

        self.visualizaiton_on = False
        self.visualization_scoket = None
        self.visualization_listen_thread = None
        self.visualization_addr_port_tuple = None

        self.peer_addr_port_tuple_list = []

        self.max_peer_number = max_peer_number
        # this is host ip and listening port for this peer
        self.my_addr_port_tuple = (host, port)
        self.peer_id = peer_id
        # this port is peer's listening port
        self.my_detail = {"host": str(host), "port": str(port), "peer_id": str(peer_id)}
        logger.debug(" init raft peer " + str(host) + " " + str(port), extra=self.my_detail)
        # use to listen or recv message from other peers
        self.socket = socket.socket()
        # reuse the socket instead of waiting for OS to release the previous port
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(self.backlog)

        self.user_socket = socket.socket()
        self.user_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.user_socket.bind((host, user_port))
        self.user_socket.listen(self.backlog)

        # use to store current user socket
        self.user_addr_listen_socket = {}

        # key is peer_addr => (ip, port)
        # used to rec message
        self.peers_addr_listen_socket = {}
        # used to send message
        self.peers_addr_client_socket = {}
        # when recv fron server listen port, we must include sender's listen port and ip
        # other wise we dont know the msg is from which peer and send to who in peer_addr_client_socket
        # in peer_addr_client_socket we use known peer's ip and port as key
        # dictionary
        self.json_message_recv_queue = Queue()
        # dictioanry
        self.json_message_send_queue = Queue()
        self.json_message_commit_queue = Queue()
        self.raft_peer_state = RaftPeerState(self.my_addr_port_tuple, self.peer_id)
        # btw 100ms - 150ms
        # random_timeout = random.randint(100, 150)/1000
        # set time as seed
        random.seed(time.time())
        # seconds
        # self.random_timeout = random.randint(10000, 15000) / 1000
        # random betwee a second and b second inclusively, only keep result in 2 decimal places
        self.random_timeout = float("{0:.2f}".format(random.uniform(min_leader_election_timeout, max_leader_election_timeout)))
        logger.debug(" random_timeout =>  " + str(self.random_timeout) + " s", extra=self.my_detail)
        # heart beat should be 5 times quicker than candidate timeoutm in here it is c seconds
        self.append_entries_heart_beat_time_out = append_entries_timeout
        self.timeout_counter = TimeoutCounter(self.random_timeout, self.my_addr_port_tuple, self.peer_id,
                                              self.raft_peer_state, self.append_entries_heart_beat_time_out)
        try:

            self.thread_connect_to_all = None

            self.thread_send = threading.Thread(target=self.process_json_message_send_queue, args=())
            self.thread_send.daemon = True
            self.thread_send.start()
            logger.debug(" start thread => process_json_message_send_queue successful ", extra=self.my_detail)

            self.thread_rev = threading.Thread(target=self.process_json_message_recv_queue, args=())
            self.thread_rev.daemon = True
            self.thread_rev.start()
            logger.debug(" start thread => process_json_message_recv_queue successful ", extra=self.my_detail)

            self.thread_peer_listen = threading.Thread(target=self.accept,
                                                       args=(self.socket, self.peers_addr_listen_socket,))
            self.thread_peer_listen.daemon = True
            self.thread_peer_listen.start()
            logger.debug(" start thread => accept peer servers successful ", extra=self.my_detail)

            # listen for user.py
            self.thread_user_listen = threading.Thread(target=self.accept,
                                                       args=(self.user_socket, self.user_addr_listen_socket,))
            self.thread_user_listen.daemon = True
            self.thread_user_listen.start()
            logger.debug(" start thread => accept user successful ", extra=self.my_detail)

            # processing commits:
            self.thread_processing_commits = threading.Thread(target=self.start_processing_commits_thread,
                                                              args=())
            self.thread_processing_commits.daemon = True
            self.thread_processing_commits.start()
            logger.debug(" start thread =>  processing commits successful ", extra=self.my_detail)

        except Exception as e:
            logger.debug("Error: unable to start processing threads " + str(e), extra=self.my_detail)

    def start_processing_commits_thread(self):
        """
        This method is used to process the logs that is ready to be committed, because we assume in the real
        world situation, the commits might take long time to complete and we dont want to block recv while
        comitting entreis, that is why we have this method here.
        """
        while True:
            # FIFO queue so will always commit from most left
            one_log = self.json_message_commit_queue.get()
            with self.raft_peer_state.lock:
                if one_log.log_applied == False:
                    if self.visualizaiton_on:
                        # for visualization we want to delay the commit,
                        # so we can show each peers commit in different time
                        time.sleep(float("{0:.2f}".format(random.uniform(0, self.append_entries_heart_beat_time_out))))

                    self.raft_peer_state.remote_var.perform_action(one_log.request_command_action_list)
                    one_log.log_applied = True
                    # if this log is added when this peer is a leader
                    if self.raft_peer_state.peer_state == "leader" and one_log.request_user_addr_port_tuple != None:
                        self.json_message_send_queue.put({"msg_type": "request_command_reply",
                                                          "send_from": list(self.my_addr_port_tuple),
                                                          "send_to": list(one_log.request_user_addr_port_tuple),
                                                          "command_result": self.raft_peer_state.remote_var.vars[
                                                              one_log.request_command_action_list[0]],
                                                          "sender_term": self.raft_peer_state.current_term})
                    if self.raft_peer_state.commit_index < one_log.log_index:
                        self.raft_peer_state.last_apply = one_log.log_index
                        self.raft_peer_state.commit_index = one_log.log_index
                    if self.visualizaiton_on:
                        print("sent to visual new commit index")
                        self.json_message_send_queue.put({
                            "msg_type":"commit_index",
                            "send_from":list(self.my_addr_port_tuple),
                            "send_to": list(self.visualization_addr_port_tuple),
                            "index": one_log.log_index,
                            "skill_name": str(one_log.request_command_action_list[0])
                            })

    def start_visualization_connection_thread(self, visualizaiton_ip, visualization_port):
        """
        This method is used to establish connection with visualization server        
        :param visualizaiton_ip: string
        :param visualization_port: int
        """
        self.visualizaiton_on = True
        self.visualization_scoket = socket.socket()
        self.visualization_addr_port_tuple = (str(visualizaiton_ip), int(visualization_port))
        self.visualization_scoket.connect(self.visualization_addr_port_tuple)
        self.visualization_listen_thread = threading.Thread(target=self.receive_from_one_peer_newline_delimiter,
                                                            args=(self.visualization_addr_port_tuple,))
        self.visualization_listen_thread.daemon = True
        self.visualization_listen_thread.start()

        # after connected to visualization, need to send a 'information' JSON to tell visualization that
        # there is new peer in the Raft system.
        cur_peer_info_json = {
            "msg_type": "information",
            "send_to": list(self.visualization_addr_port_tuple),
            "send_from": list(self.raft_peer_state.my_addr_port_tuple),
            "peer_id": self.my_detail["peer_id"]
        }

        self.json_message_send_queue.put(cur_peer_info_json)

        print("visusalization server connection established")

    def start_raft_peer(self):
        self.thread_timer = threading.Thread(target=self.timeout_counter.start_time_counter, args=(self,))
        self.thread_timer.daemon = True
        self.thread_timer.start()
        # _thread.start_new_thread(self.timeout_counter.start_time_counter, (self, ))

    def process_json_message_recv_queue(self):
        """
        
        This method is running as an independent thread, so it will consume the JSON data which are read
        from the recv thread.
         
        """
        while True:
            logger.debug(" start receive ", extra=self.my_detail)
            one_recv_json_message_dict = self.json_message_recv_queue.get()
            with self.raft_peer_state.lock:
                # update terms from candidate
                logger.debug(" inside receive ", extra=self.my_detail)
                # those JSON message does not have term, they are used by User.py and visualization/game
                if one_recv_json_message_dict["msg_type"] not in ["request_command", "villager_killed"]:

                    # if my term is same as request vote sender means, I am a candidate or I receive this term msg
                    # from someone else already, there should one person who is already electing from my knowledge
                    # no reason to accept a same term requxest vote
                    if one_recv_json_message_dict["msg_type"] in ["request_vote"] and (
                        one_recv_json_message_dict["sender_term"] == self.raft_peer_state.current_term):
                        logger.debug(" same term request vote abort " + str(one_recv_json_message_dict),
                                     extra=self.my_detail)
                        continue

                    # in Raft we always favour the largest term number
                    if one_recv_json_message_dict["sender_term"] > self.raft_peer_state.current_term:
                        logger.debug(" see larger term " + str(one_recv_json_message_dict),
                                     extra=self.my_detail)
                        self.raft_peer_state.current_term = one_recv_json_message_dict["sender_term"]
                        # current term is outdate, so if it starts voting need to stop immediately
                        # term will reject the previous voting request actually
                        self.raft_peer_state.peer_state = "follower"
                        self.raft_peer_state.leader_majority_count = 0
                        # every new term clear old vote_for, might experience new term election
                        self.raft_peer_state.vote_for = None
                        # force reset timer, since it is outdated not reseting only vote true then reset and receive append entries
                        # self.timeout_counter.reset_timeout()
                    if one_recv_json_message_dict["sender_term"] < self.raft_peer_state.current_term:
                        logger.debug(" received outdated term msg abort " + str(one_recv_json_message_dict),
                                     extra=self.my_detail)
                        continue
            logger.debug(" processing one recv message " + str(one_recv_json_message_dict), extra=self.my_detail)
            # in json encode it is two element list
            # sendpeer_addr, peer_port = one_recv_json_message_dict["send_from"]

            # calling right methods to handle the different JSON data
            one_recv_json_message_type = one_recv_json_message_dict["msg_type"]
            receive_processing_functions = {"append_entries_follower_reply": self.process_append_entries_follower_reply,
                                            "append_entries_leader": self.process_append_entries_leader,
                                            "request_vote_reply": self.process_request_vote_reply,
                                            "request_vote": self.process_request_vote,
                                            "request_command": self.process_request_command,
                                            "villager_killed": self.process_killed}
            receive_processing_function = receive_processing_functions[one_recv_json_message_type]
            receive_processing_function(one_recv_json_message_dict)

    def process_killed(self, one_recv_json_message_type):
        """
        
        This method will respond to visualization's kill json to terminate the current peer.
        
        :param one_recv_json_message_type: dict
        """
        print ("termiated by remote rpc")
        print (" killed json => " + str(one_recv_json_message_type))
        os._exit(0)

    def process_request_command(self, one_recv_json_message_type):
        """
        
        Processing the request_command from user, it will send out not_leader if the
        User.py connect to the current peer who is not leader.
        
        :param one_recv_json_message_type: dict
        """
        with self.raft_peer_state.lock:
            # if command_request == [] means init finding leader
            if self.raft_peer_state.peer_state == "leader":

                if one_recv_json_message_type["request_command_list"] == []:
                    self.json_message_send_queue.put({"msg_type": "request_command_reply",
                                                      "command_result": "is_leader",
                                                      "send_from": list(self.user_socket.getsockname()),
                                                      "send_to": list(one_recv_json_message_type["send_from"]),
                                                      "sender_term": self.raft_peer_state.current_term})
                    return
                temp_log = LogData(len(self.raft_peer_state.state_log),
                                   self.raft_peer_state.current_term,
                                   one_recv_json_message_type["request_command_list"],
                                   (one_recv_json_message_type["send_from"]))
                temp_log.increment_majority_count()
                # temp_log.one_log.check_over_majority((self.max_peer_number/2)+1)

                self.raft_peer_state.state_log.append(temp_log)

                if self.visualizaiton_on:
                    one_recv_json_message_type_deep_copy = copy.deepcopy(one_recv_json_message_type)
                    one_recv_json_message_type_deep_copy["msg_type"] = "request_command_ack"
                    one_recv_json_message_type_deep_copy["send_from"] = list(self.raft_peer_state.my_addr_port_tuple)
                    one_recv_json_message_type_deep_copy["send_to"] = list(self.visualization_addr_port_tuple)
                    one_recv_json_message_type_deep_copy["sender_term"] = self.raft_peer_state.current_term
                    one_recv_json_message_type_deep_copy["index"] = temp_log.log_index
                    self.json_message_send_queue.put(one_recv_json_message_type_deep_copy)

            else:
                self.json_message_send_queue.put({"msg_type": "request_command_reply",
                                                  "command_result": "not_leader",
                                                  "send_from": self.user_socket.getsockname(),
                                                  "send_to": list(one_recv_json_message_type["send_from"]),
                                                  "sender_term": self.raft_peer_state.current_term})

    def process_append_entries_follower_reply(self, one_recv_json_message_dict):
        """
        Thie method is for 'leader' to collect append entries reply from
        the followers.
        
        If the append entries is not heartbeat one, it will increase the majority count
        of the log and if the log's majority count over the majority leader will commit the log
        and send out its newest commit index in future append entries.
        
        :param one_recv_json_message_dict: dict
         
        """
        # print (str(one_recv_json_message_dict))
        logger.debug(" starting process_append_entries_follower_reply " + str(one_recv_json_message_dict),
                     extra=self.my_detail)

        # index_start indicates where the follower start to add in the entries
        # index_end indciates the last index after adding in the entries
        # if both of them are -1 means it is a heartbeat or this append entries are rejected
        log_index_start = int(one_recv_json_message_dict["log_index_start"])
        log_index_end = int(one_recv_json_message_dict["log_index_end"])

        with self.raft_peer_state.lock:
            # heart beat if reply is true, and log start = -1, log end = -1
            if one_recv_json_message_dict["append_entries_result"] == True:
                # increase this peer's next index
                self.raft_peer_state.peers_match_index[tuple(one_recv_json_message_dict["send_from"])] = \
                self.raft_peer_state.peers_next_index[tuple(one_recv_json_message_dict["send_from"])]

                # print(" log_index_start " + str(log_index_start) + " log_index_end " + str(log_index_end))

                for one_log in self.raft_peer_state.state_log[log_index_start:(log_index_end + 1)]:
                    self.raft_peer_state.peers_next_index[tuple(one_recv_json_message_dict["send_from"])] += 1
                    one_log.majority_count += 1
                    if one_log.check_over_majority((self.max_peer_number // 2) + 1):
                        with self.raft_peer_state.remote_var.lock:

                            self.raft_peer_state.commit_index = one_log.log_index
                            self.raft_peer_state.last_apply = self.raft_peer_state.commit_index

                            if one_log.log_applied == False:

                                # make sure all log before it is applied
                                for i in range(self.raft_peer_state.commit_index + 1):
                                    one_temp_log = self.raft_peer_state.state_log[i]
                                    if one_temp_log.log_applied == False:
                                        self.json_message_commit_queue.put(one_temp_log)

            else:
                logger.debug(" starting process_append_entries_follower_reply False" + str(one_recv_json_message_dict),
                             extra=self.my_detail)
                logger.debug(" starting process_append_entries_follower_reply False next_index => " + str(
                    self.raft_peer_state.peers_next_index[tuple(one_recv_json_message_dict["send_from"])]) + " " + str(
                    one_recv_json_message_dict),
                             extra=self.my_detail)
                with self.raft_peer_state.lock:
                    if self.raft_peer_state.peers_next_index[tuple(one_recv_json_message_dict["send_from"])] > 0:
                        # decrease the next index if the false append entreis returned. the min next is 0
                        self.raft_peer_state.peers_next_index[tuple(one_recv_json_message_dict["send_from"])] -= 1


            # match index can only increase, so we only record when it is true, it is always one less than nextIndex
            # could be used to optimize finding right nextIndex? let's see later
            logger.debug(" finished process_append_entries_follower_reply " + str(one_recv_json_message_dict),
                         extra=self.my_detail)

    def process_append_entries_leader(self, one_recv_json_message_dict):
        """
        This method is used to process the append entries sent from the leader to
        follower.
        
        Followeor will make decision on rejecting or accepting the append entries RPC.
        :param one_recv_json_message_dict: dict
        
        """
        # sent from leader, received by this follower to append entry
        logger.debug(" starting process_append_entries_leader " + str(one_recv_json_message_dict), extra=self.my_detail)
        with self.raft_peer_state.lock:
            # when received heart beat from leader, reset self timeout of starting new election
            # reset timeout to eleciton timeout
            self.timeout_counter.reset_timeout()
            # if JSON come here means, the term is either equal to current peer or greater so
            # to be safe set it to follower
            self.raft_peer_state.peer_state = "follower"
            self.raft_peer_state.vote_for = None
            append_entries_follower = AppendEntriesFollower(one_recv_json_message_dict, self.raft_peer_state,
                                                            self.json_message_commit_queue)

            temp_processed_append_entries_result_json = append_entries_follower.process_append_entries()

            # send a copy of reply to visualization, if the reuslt is true
            if self.visualizaiton_on and \
                    temp_processed_append_entries_result_json["append_entries_result"] and \
                    temp_processed_append_entries_result_json["log_index_start"] != -1 and \
                    temp_processed_append_entries_result_json["log_index_end"] != -1:

                time.sleep(float("{0:.2f}".format(random.uniform(0, self.append_entries_heart_beat_time_out))))
                temp_processed_append_entries_result_json_deep_copy = copy.deepcopy(temp_processed_append_entries_result_json)
                temp_processed_append_entries_result_json_deep_copy["send_to"] = list(self.visualization_addr_port_tuple)
                # note that leader append entries used the key 'leader_commit_index' which is different key used in here
                temp_processed_append_entries_result_json_deep_copy["sender_commit_index"] = self.raft_peer_state.current_term
                self.json_message_send_queue.put(temp_processed_append_entries_result_json_deep_copy)
                print (" sent append reply to visual ")

            self.json_message_send_queue.put(temp_processed_append_entries_result_json)
            logger.debug(" after append entries from leader => \n " + str(self.raft_peer_state),
                         extra=self.my_detail)
        logger.debug(" finished process_append_entries_leader " + str(one_recv_json_message_dict), extra=self.my_detail)

    def process_request_vote_reply(self, one_recv_json_message_dict):
        """
        
        This method is used for candidate to collect the request_reply from other peers
        after it started the election.
        
        The peer will count the votes and if it has over majority vote, it will become leader
        and take the role to send out append entries as the authority to be the leader.
        
        :param one_recv_json_message_dict: dict
        """
        # receive the request vote reply from other peers for my leader request vote
        logger.debug(" starting process_request_vote_reply " + str(one_recv_json_message_dict), extra=self.my_detail)
        with self.raft_peer_state.lock:
            if self.raft_peer_state.peer_state == "leader":
                logger.debug(" I am already a leader ", extra=self.my_detail)
                return
            if one_recv_json_message_dict["vote_granted"] == True:
                self.raft_peer_state.increment_leader_majority_count()
                # check if got majority vote or not
                self.raft_peer_state.elected_leader(int(self.max_peer_number // 2) + 1)
                if self.raft_peer_state.peer_state == "leader":

                    if self.visualizaiton_on:
                        leadership_json = {
                            "msg_type": "leadership",
                            "sender_term": self.raft_peer_state.current_term,
                            "send_from": self.raft_peer_state.my_addr_port_tuple,
                            "send_to": list(self.visualization_addr_port_tuple),
                            "peer_id": self.raft_peer_state.peer_id
                        }
                        self.json_message_send_queue.put(leadership_json)

                    logger.debug(" I am leader ", extra=self.my_detail)
                    # init nextIndex[] and matchIndex[]
                    # set self.timeout to append entries if the current peer become leader
                    self.timeout_counter.reset_timeout_append_entries()
                    self.raft_peer_state.initialize_peers_next_and_match_index(self.peers_addr_client_socket)
                    # boardcast the append entries
                    self.put_sent_to_all_peer_append_entries_heart_beat()


                    # logger.debug(" finished process_request_vote_reply " + str(one_recv_json_message_dict), extra=self.my_detail)
                    # logger.debug(" raft_peer_state \n " + str(self.raft_peer_state), extra=self.my_detail)

    def process_request_vote(self, one_recv_json_message_dict):
        """
        This method is for peers to respond for the request_vote RPC call,
        the peer will vote for the candidate in following conditions:
        if his log is shorter than candidate,
        if the the peer is not voted yet,
        if the peer has older term/current term log at the last log and they both have same log length 
        
        :param one_recv_json_message_dict:dict 
         
        """
        logger.debug(" starting process_request_vote " + str(one_recv_json_message_dict), extra=self.my_detail)
        # reply the candidate who sent the vote request to here
        with self.raft_peer_state.lock:
            # if the leader receive thie requet vote means its leader term is outdated
            # leader should downgrade to follower and make decision of voting to current term
            # candidate
            if self.raft_peer_state.peer_state == "leader":
                self.raft_peer_state.peer_state = "follower"
            # if receive vote request from others means new election, should set self state to candidate,
            # refuse incoming append entries
            # self.raft_peer_state.peer_state = "candidate"
            request_vote_receive = RequestVoteReceive(one_recv_json_message_dict, self.raft_peer_state)
            temp_request_vote_result = request_vote_receive.process_request_vote()
            if temp_request_vote_result["vote_granted"] == True:
                self.timeout_counter.reset_timeout()

            if self.visualizaiton_on:
                temp_request_vote_result_deep_copy = copy.deepcopy(temp_request_vote_result)
                temp_request_vote_result_deep_copy["send_to"] = list(self.visualization_addr_port_tuple)
                self.json_message_send_queue.put(temp_request_vote_result_deep_copy)

            self.json_message_send_queue.put(temp_request_vote_result)
        logger.debug(" finished process_request_vote " + str(one_recv_json_message_dict), extra=self.my_detail)

    def process_json_message_send_queue(self):
        """
        This method will be invoked in an independent thread for sending JSON from sending queue.
        
        """
        while True:
            one_json_data_dict = self.json_message_send_queue.get()
            logger.debug(" processing one send message " + str(one_json_data_dict), extra=self.my_detail)
            # in json encode it is two element list
            peer_addr, peer_port = one_json_data_dict["send_to"]
            self.send_to_peer((peer_addr, peer_port), one_json_data_dict)

    def start_connect_to_all_peer_thread(self, peer_addr_port_tuple_list):
        """
        
        Raft is a peer to peer structure, so current peer must connect to remote peers'
        listening port and we make a thread to perform this for both connection and reconnection.
        
        :param peer_addr_port_tuple_list: list of (str, int)
        """
        self.thread_connect_to_all = threading.Thread(target=self.connect_to_all_peer,
                                                      args=(peer_addr_port_tuple_list,))
        self.thread_connect_to_all.daemon = True
        self.thread_connect_to_all.start()
        logger.debug(" start thread => connect to all thread ", extra=self.my_detail)

    # [(ip => str, port => int)...]
    def connect_to_all_peer(self, peer_addr_port_tuple_list):
        """
        
        This method will trying to connect to peers that is in the unconnected queue,
        and will take turn to connect peers not blocking on unconnected peer.
        
        :param peer_addr_port_tuple_list: 
        :return: 
        """
        self.peer_addr_port_tuple_list = peer_addr_port_tuple_list
        my_peer_addr_port_tuple = (str(self.my_detail['host']), int(self.my_detail['port']))
        self.peer_addr_port_tuple_list.remove(my_peer_addr_port_tuple)
        # in referece remove
        # peer_addr_port_tuple_list.remove(my_peer_addr_port_tuple)
        # for one_peer_addr, one_peer_port in peer_addr_port_tuple_list:
        count = -1
        while True:
            # always mode cout to max number of peers so we are not blocking at one peer if it can't be connected
            count += 1
            if len(self.peer_addr_port_tuple_list) > 0:
                one_peer_addr, one_peer_port = peer_addr_port_tuple_list[count % len(self.peer_addr_port_tuple_list)]
            else:
                # print("self")
                time.sleep(1)
                continue
            # while True:
            try:
                self.connect_to_peer((str(one_peer_addr), int(one_peer_port)))
                peer_addr_port_tuple_list.remove((one_peer_addr, one_peer_port))
                print("finished connect to " + str((str(one_peer_addr), int(one_peer_port))))
            except Exception as e:
                print("failed connect to " + str((str(one_peer_addr), int(one_peer_port))))
                # logger.debug("raft peer connect to " + str((one_peer_addr, one_peer_port)) + " failed retry, exception => " + str(e), extra=self.my_detail)
                time.sleep(1)
                continue
            time.sleep(1)

    def connect_to_peer(self, peer_addr_port_tuple):
        """
        
        Trying to establish with remote peer's listen port
        
        :param peer_addr_port_tuple: (str, int)
         
        """
        # use to send message to other peers
        client_socket = socket.socket()
        logger.debug("raft peer connect to " + str(peer_addr_port_tuple), extra=self.my_detail)
        client_socket.connect(peer_addr_port_tuple)
        self.peers_addr_client_socket[peer_addr_port_tuple] = client_socket

    # listen from user and other peer servers
    def accept(self, socket, peers_addr_listen_socket):
        """
        
        listening connection from other peers
        
        :param socket: socket
        :param peers_addr_listen_socket: (str, int)
        
        """
        while True:
            peer_socket, peer_addr_port_tuple = socket.accept()
            # peer_addr => (ip, port)
            peers_addr_listen_socket[peer_addr_port_tuple] = peer_socket
            logger.debug(" recv socket from " + str(peer_addr_port_tuple), extra=self.my_detail)
            try:
                temp_thread = threading.Thread(target=self.receive_from_one_peer_newline_delimiter,
                                               args=(peer_addr_port_tuple,))
                temp_thread.daemon = True
                temp_thread.start()
                # _thread.start_new_thread(self.receive_from_one_peer_newline_delimiter, (peer_addr_port_tuple, ))
                logger.debug(" creating recv thread successful => " + str(peer_addr_port_tuple), extra=self.my_detail)
            except Exception as e:
                logger.debug(" creating recv thread failed => " + str(peer_addr_port_tuple), extra=self.my_detail)

    def close(self):
        """
        close all socket when exit
        
        """
        for peer_addr, socket_from_listen in self.peers_addr_listen_socket.items():
            socket_from_listen.close()
        for peer_addr, socket_from_client in self.peers_addr_client_socket.items():
            socket_from_client.close()
        self.socket.close()

    def _check_peer_in(self, peer_addr):
        """
        check wheter if this host is in the system or not
        
        :param peer_addr: str
        
        """
        if peer_addr not in self.peers_addr_listen_socket and peer_addr not in self.peers_addr_client_socket:
            logger.debug(" " + str(peer_addr) + " not in peers_addr_socket", extra=self.my_detail)
            return

    def put_sent_to_all_peer_request_vote(self):
        """
        
        Boardcasting request_vote JSON to all other peers.
        
        
        """
        logger.debug(" sending request vote to all peers as client ", extra=self.my_detail)
        with self.raft_peer_state.lock:
            self.raft_peer_state.vote_for = self.my_addr_port_tuple
            self.raft_peer_state.peer_state = "candidate"
            # every new election need to increase current term
            self.raft_peer_state.current_term += 1
            # vote self
            self.raft_peer_state.leader_majority_count = 1
            socket_keys = self.peers_addr_client_socket.keys()
            temp_request_vote = None
            # logger.debug(" before loop ", extra=self.my_detail)
            for one_add_port_tuple in socket_keys:
                # logger.debug(" in loop ", extra=self.my_detail)
                temp_request_vote = RequestVote(self.raft_peer_state, one_add_port_tuple).return_instance_vars_in_dict()
                self.json_message_send_queue.put(temp_request_vote)
            if self.visualizaiton_on and len(socket_keys) is not 0:
                # send to visualization one request json among all other peers
                temp_request_vote_deep_copy = copy.deepcopy(temp_request_vote)
                temp_request_vote_deep_copy["send_to"] = list(self.visualization_addr_port_tuple)
                self.json_message_send_queue.put(temp_request_vote_deep_copy)
        logger.debug(" finished request vote to all peers as client ", extra=self.my_detail)

    def put_sent_to_all_peer_append_entries_heart_beat(self):
        """
        
        boadcast append entries as heartbeat or normal append entries to add in new logs
        
        """
        logger.debug(" sending append entries heart beats to all peers as client ", extra=self.my_detail)
        with self.raft_peer_state.lock:
            log_len = len(self.raft_peer_state.state_log)
            append_entries_heart_beat_leader = None
            for one_add_port_tuple in self.peers_addr_client_socket.keys():
                # this peer is uptodated and we have no new entries just send empty heartbeat
                if self.raft_peer_state.peers_next_index[one_add_port_tuple] == log_len or \
                                self.raft_peer_state.peers_match_index == log_len:
                    append_entries_heart_beat_leader = AppendEntriesLeader(self.raft_peer_state, one_add_port_tuple,
                                                                           "heartbeat").return_instance_vars_in_dict()
                else:
                    append_entries_heart_beat_leader = AppendEntriesLeader(self.raft_peer_state, one_add_port_tuple,
                                                                           "append").return_instance_vars_in_dict()
                self.json_message_send_queue.put(append_entries_heart_beat_leader)
            if self.visualizaiton_on:
                # send one copy of appendentries to visualization even though peers getting different append entries
                append_entries_heart_beat_leader_deep_copy = copy.deepcopy(append_entries_heart_beat_leader)
                append_entries_heart_beat_leader_deep_copy["send_to"] = self.visualization_addr_port_tuple
                append_entries_heart_beat_leader_deep_copy["new_entries"] = []
                self.json_message_send_queue.put(append_entries_heart_beat_leader_deep_copy)


    # not used so far
    def sent_to_all_peer(self, json_data_dict):
        """
        
        send to message with remote peer's listen port socket
        
        :param json_data_dict: dict
        
        """
        logger.debug(" sending json_data to all peers as client ", extra=self.my_detail)
        with self.raft_peer_state.lock:
            for peer_addr in self.peers_addr_client_socket.keys():
                self.send_to_peer(peer_addr, json_data_dict)

    # only send as client for current peer not using listen socket to send
    def send_to_peer(self, peer_addr_port_tuple, json_data_dict):
        """
        
        turn dictionary into valid JSON string with jsonpickle which will automatically
        serilize the objects in the dictionary to be dictionary str.
        
        :param peer_addr_port_tuple: (str, int) 
        :param json_data_dict: dict
        
        """
        logger.debug(" sending json_data to " + str(peer_addr_port_tuple), extra=self.my_detail)
        # self._check_peer_in(peer_addr_port_tuple)
        # logger.debug(" sending json_data to " + str(self.peers_addr_client_socket), extra=self.my_detail)
        # sent to user
        # sent to user/visualization because they are not p2p only have one socket
        if json_data_dict["msg_type"] in ["request_command_reply"]:
            try:
                peer_socket = self.user_addr_listen_socket[peer_addr_port_tuple]
            except Exception as e:
                logger.debug(" not this user socket abort " + str(e), extra=self.my_detail)
                return
        elif peer_addr_port_tuple == self.visualization_addr_port_tuple:
            peer_socket = self.visualization_scoket
            if peer_socket is None:
                print("visualization send failed, the socket is none")
                return
        else:
            try:
                peer_socket = self.peers_addr_client_socket[peer_addr_port_tuple]
            except Exception as e:
                logger.debug(" peer not connected as client yet, put this term message back => " + str(e), extra=self.my_detail)
                # if json_data_dict["sender_term"] == self.raft_peer_state.current_term:
                #     self.json_message_send_queue.put(json_data_dict)
                return

        try:
            # serialized_json_data = json.dumps(json.loads(jsonpickle.encode(json_data_dict)))
            serialized_json_data = jsonpickle.encode(json_data_dict)
            logger.debug(" json data serialization " + serialized_json_data, extra=self.my_detail)
            # send msg size
            # peer_socket.send(str.encode(str(len(serialized_json_data))+"\n", "utf-8"))
            # logger.debug(" json data sent len " + str(len(serialized_json_data)), extra = self.my_detail)
        except Exception as e:
            logger.debug(" json data serialization failed " + str(json_data_dict) + str(e), extra=self.my_detail)
            return
        # make it utf8r
        try:
            peer_socket.sendall(str.encode(serialized_json_data + "\n", "utf-8"))
        except Exception as e:
            # reconnect to peer
            # no reconnecting to user socket, we use listen socket to send message to user
            if peer_addr_port_tuple in self.peers_addr_client_socket:
                logger.debug(" json data serialization sent failed reconnect to peer " + str(json_data_dict) + str(
                    e) + " " + str(
                    peer_addr_port_tuple), extra=self.my_detail)
                # put json back to the end of queue
                # self.json_message_send_queue.put(json_data_dict)
                try:
                    # put it back for thread to reconnect it
                    # python list append is thread-safe
                    self.peer_addr_port_tuple_list.append(peer_addr_port_tuple)
                    # self.connect_to_peer(peer_addr_port_tuple)
                    # if this message is still in current term then put it back to end of queu
                    # if it is outdated remove it
                    # if json_data_dict["sender_term"] == self.raft_peer_state.current_term:
                    # self.json_message_send_queue.put(json_data_dict)
                except Exception as e:
                    logger.debug(" reconnection failed " + str(json_data_dict) + str(e) + " " + str(
                        peer_addr_port_tuple), extra=self.my_detail)
                    # else:
                    #     logger.debug(" json data serialization sent failed  user abort " + str(peer_addr_port_tuple) , extra = self.my_detail)

    def receiv_from_all_peer(self):
        """
        
        retireve JSON from each listent incoming sockets
        
        
        """
        # this part is blocking for every client start a new thread ?
        # put them in a queue use one thread to do the job
        for peer_addr in self.peers_addr_listen_socket.keys():
            self.receive_from_one_peer_newline_delimiter(peer_addr)

    def receive_from_one_peer_newline_delimiter(self, peer_addr_port_tuple):
        """
        
        Each JSON message are sperated with newline, so befor we send we need to add new line
        at the end of each JSON message
        
        :param peer_addr_port_tuple: dict
        
        """
        logger.debug(" recv json_data from " + str(peer_addr_port_tuple), extra=self.my_detail)
        # self._check_peer_in(peer_addr_port_tuple)

        # pick socket from User, visualization or remote incoming socket of other peers
        if peer_addr_port_tuple in self.peers_addr_listen_socket:
            peer_socket = self.peers_addr_listen_socket[peer_addr_port_tuple]
        elif peer_addr_port_tuple in self.user_addr_listen_socket:
            peer_socket = self.user_addr_listen_socket[peer_addr_port_tuple]
        elif peer_addr_port_tuple == self.visualization_addr_port_tuple:
            peer_socket = self.visualization_scoket
        else:
            logger.debug(" can't find this addr_port_tuple in either dicts ", extra=self.my_detail)
            return

        msg = ""
        # could be wrong if msg size bigger than 1024, need further testing
        while True:

            try:
                # if remote close it should return "" ?
                # receive max 1024 bytes every time
                temp = peer_socket.recv(1024).decode("utf-8")
                # python is cool, it just return empty string when remote closed the connection
                if temp == "":
                    raise Exception()
                    # remote closed recev will still return infinite empty string
            except Exception as e:
                logger.debug(" one listen incoming socket closed " + str(e) + str(peer_addr_port_tuple),
                             extra=self.my_detail)
                # called this will terminate accept?
                # peer_socket.close()
                if peer_addr_port_tuple in self.peers_addr_listen_socket:
                    self.peers_addr_listen_socket.pop(peer_addr_port_tuple)
                elif peer_addr_port_tuple in self.user_addr_listen_socket:
                    self.user_addr_listen_socket.pop(peer_addr_port_tuple)
                return

            msg += temp
            # if msg has new line means we have received some complete JSON data
            # it is time to deserilize it to dictionary
            if "\n" in msg:
                msg_split_list = msg.split("\n")
                msg = msg_split_list[-1]
                # get all JSON but leave the incomplete message in the msg
                for one_json_msg in msg_split_list[0:-1]:
                    try:
                        # logger.debug(" recv one json_data " + one_json_msg, extra = self.my_detail)
                        one_deserialized_json_data = json.loads(one_json_msg)
                        self.json_message_recv_queue.put(one_deserialized_json_data)
                        logger.debug(" put one json_data " + one_json_msg, extra=self.my_detail)
                    except Exception as e:
                        logger.debug(" deserialization recv json data failed " + str(e), extra=self.my_detail)
