import logging
logger = logging.getLogger("RPC")
FORMAT = '[AppendEntries][%(asctime)-15s][%(levelname)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG)
from LogData import LogData
class AppendEntries:
    #for leader to initialize appen entry
    def __init__(self, raft_peer_state, send_to_addr_port_tuple):
        self.raft_peer_state = raft_peer_state
        self.append_entries_type = "leader_send"
        self.leader_term = raft_peer_state.current_term
        self.leader_id = raft_peer_state.my_addr_port_tuple
        #leader's log index before the new appended entry
        self.prev_log_index = raft_peer_state.state_log[-2].index
        self.prev_log_term = raft_peer_state.state_log[-2].term
        #could be one or more for efficiency
        self.new_entries = raft_peer_state[-1]
        self.leader_commit_index = raft_peer_state.commit_index
        self.send_from = raft_peer_state.my_addr_port_tuple
        self.send_to = send_to_addr_port_tuple

    #for follower to receive it
    def __init__(self, append_entries_json_data, raft_peer_state):
        self.raft_peer_state = raft_peer_state
        self.host_port_dict = {"host":raft_peer_state.my_addr_port_tuple[0], "port":raft_peer_state.my_addr_port_tuple[1]}
        self.append_entries_type = "follower_receive"
        self.leader_term = append_entries_json_data["leader_term"]
        self.leader_id = append_entries_json_data["leader_id"]
        self.prev_log_index = int(append_entries_json_data["prev_log_index"])
        self.prev_log_term = int(append_entries_json_data["prev_log_term"])
        #could be one or more for efficiency, should be a list of log_data_dict
        self.new_entries = append_entries_json_data["new_entries"]
        self.leader_commit_index = int(append_entries_json_data["leader_commit_index"])
        #first => addr, second => port
        self.send_from = tuple(append_entries_json_data["send_from"])
        self.send_to = tuple(append_entries_json_data["send_to"])

    #for follower to process received append entries and return result as dict

    def process_append_entries(self):
        if self.append_entries_type == "leader_send":
            logging.debug(" leader shouldn't process append entries ", extra = self.host_port_dict)
        result = {"send_from": list(self.raft_peer_state.my_addr_port_tuple),
                  "send_to": list(self.send_from),
                  "follower_term":self.raft_peer_state.current_term,
                  "append_entries_result": True,
                  "type": "follower_append_entries_reply"}

        #reply false if this.follower's term > leader's term
        if self.raft_peer_state.current_term > self.leader_term:
            result["append_entries_result"] = False
            return result
        #reply false if this.follower's does not have this prev_index, and term does not match
        #so even the follower has more log we only check the prev_index one?
        if len(self.raft_peer_state.state_log - 1) < self.prev_log_index:
            result["append_entries_result"] = False
            return result

        #leader's prev log term does not match with follower's last entry's term
        if self.raft_peer_state.state_log[self.prev_log_index].term != self.prev_log_term:
            result["append_entries_result"] = False
            return result
        result["append_entries_result"] = True
        self.add_in_new_entries()
        return result

    def add_in_new_entries(self):
        for one_new_log in self.new_entries:
            one_new_log_data = LogData(one_new_log["log_index"],
                                       one_new_log["log_term"],
                                       one_new_log["log_command_type"],
                                       one_new_log["log_committed"])
            #if follower is not longer than leader
            if self.prev_log_index == len(self.raft_peer_state.state_log - 1):
                self.raft_peer_state.state_log.append(one_new_log_data)
            #if follower id longer, it can be shorter bc of above filter
            else:
                self.raft_peer_state.state_log[self.prev_log_index + 1] = one_new_log_data
                self.raft_peer_state.state_log = self.raft_peer_state.state_log[0:self.prev_log_index + 2]

    def __str__(self):
        return str(vars(self))

    def return_instance_vars_in_dict(self):
        return vars(self)






