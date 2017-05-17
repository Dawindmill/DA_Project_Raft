"""


Author: Bingfeng Liu

This is the class to process the append entreis from the leader



"""

import logging
from LogData import LogData

logger = logging.getLogger("AppendEntiesFollower")


class AppendEntriesFollower:
    #for follower to receive it
    def __init__(self, append_entries_json_data_dict, raft_peer_state, json_message_commit_queue):
        self.json_message_commit_queue = json_message_commit_queue
        self.raft_peer_state = raft_peer_state
        self.host_port_dict = {"host":str(raft_peer_state.my_addr_port_tuple[0]),
                               "port":str(raft_peer_state.my_addr_port_tuple[1]),
                               "peer_id":str(raft_peer_state.peer_id)}
        self.leader_term = append_entries_json_data_dict["sender_term"]
        self.leader_id = append_entries_json_data_dict["peer_id"]
        self.prev_log_index = int(append_entries_json_data_dict["prev_log_index"])
        self.prev_log_term = int(append_entries_json_data_dict["prev_log_term"])
        #could be one or more for efficiency, should be a list of log_data_dict
        self.new_entries = append_entries_json_data_dict["new_entries"]
        self.leader_commit_index = int(append_entries_json_data_dict["leader_commit_index"])
        #first => addr, second => port
        self.send_from = tuple(append_entries_json_data_dict["send_from"])
        self.send_to = tuple(append_entries_json_data_dict["send_to"])

    #for follower to process received append entries and return result as dict

    def process_append_entries(self):

        log_index_start = -1
        log_index_end = -1

        result = {"log_index_start": log_index_start,
                  "log_index_end": log_index_end,
                  "send_from": list(self.raft_peer_state.my_addr_port_tuple),
                  "send_to": list(self.send_from),
                  "sender_term": self.raft_peer_state.current_term,
                  "append_entries_result": True,
                  "msg_type": "append_entries_follower_reply"}

        # meet heartbeat append entries
        if len(self.new_entries) != 0:

            log_index_start = self.new_entries[0]["log_index"]
            log_index_end = self.new_entries[-1]["log_index"]


        # #reply false if this.follower's term > leader's term
        if self.raft_peer_state.current_term > self.leader_term:
            result["append_entries_result"] = False
            return result

        #reply false if this.follower's does not have this prev_index, and term does not match
        #so even the follower has more log we only check the prev_index one?



        #leader's prev log term does not match with follower's last entry's term
        if self.prev_log_index != -1:
            # prevent peer restart get into this if and get false back
            if (len(self.raft_peer_state.state_log) - 1) < self.prev_log_index:
                result["append_entries_result"] = False
                return result

            if (self.raft_peer_state.state_log[self.prev_log_index].log_term != self.prev_log_term):
                result["append_entries_result"] = False
                return result

        if len(self.new_entries) == 0:
            self.process_commit_index(self.leader_commit_index)
            return result

        result["log_index_start"] = log_index_start
        result["log_index_end"] = log_index_end

        result["append_entries_result"] = True

        # self.raft_peer_state.current_term = self.leader_term

        self.add_in_new_entries()

        # self.raft_peer_state.commit_index = self.leader_commit_index

        self.process_commit_index(self.leader_commit_index)


        return result

    def add_in_new_entries(self):
        prev_log_index = self.prev_log_index
        for one_new_log in self.new_entries:
            one_new_log_data = LogData(one_new_log["log_index"],
                                       one_new_log["log_term"],
                                       one_new_log["request_command_action_list"])
            #if follower is not longer than leader
            if prev_log_index == (len(self.raft_peer_state.state_log) - 1):
                self.raft_peer_state.state_log.append(one_new_log_data)
                prev_log_index += 1
            #if follower id longer, it can be shorter bc of above filter
            else:
                self.raft_peer_state.state_log[prev_log_index + 1] = one_new_log_data
                # self.raft_peer_state.state_log = self.raft_peer_state.state_log[0:prev_log_index + 2]
                prev_log_index += 1

    def process_commit_index(self, commit_index):
        if (commit_index == -1):
            return
        # [include: exclude]
        for one_log_data in self.raft_peer_state.state_log[0:commit_index+1]:
            if one_log_data.log_applied == False:
                self.json_message_commit_queue.put(one_log_data)
                # self.raft_peer_state.remote_var.perform_action(one_log_data.request_command_action_list)
                # one_log_data.log_applied = True
        # self.raft_peer_state.last_apply = commit_index
        # self.commit_index = commit_index

    def __str__(self):
        return str(vars(self))







