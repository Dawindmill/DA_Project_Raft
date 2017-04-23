import logging
logger = logging.getLogger("AppendEntiesLeader")
FORMAT = '[AppendEntries][%(asctime)-15s][%(levelname)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG)
from LogData import LogData

class AppendEntriesLeader:
    # for leader to initialize appen entry
    # assume add entry frist to raft_peer_state then create this obj
    def __init__(self, raft_peer_state, send_to_addr_port_tuple, type = "append"):
        self.msg_type = "append_entries_leader"
        # self.raft_peer_state = raft_peer_state
        # self.append_entries_type = "leader_send"
        self.sender_term = raft_peer_state.current_term
        self.peer_id = raft_peer_state.peer_id
        # leader's log index before the new appended entry
        if len(raft_peer_state.state_log) >= 2:
            self.prev_log_index = raft_peer_state.peers_next_index[send_to_addr_port_tuple]
            self.prev_log_term = raft_peer_state.state_log[self.prev_log_index].term
        else:
            #init state
            self.prev_log_index = -1
            self.prev_log_term = -1
        # could be one or more for efficiency
        if type == "append":
            self.new_entries = raft_peer_state[-1]
        elif type == "heartbeat":
            self.new_entries = []
        self.leader_commit_index = raft_peer_state.commit_index
        self.send_from = list(raft_peer_state.my_addr_port_tuple)
        self.send_to = list(send_to_addr_port_tuple)

    def __str__(self):
        return str(vars(self))

    def return_instance_vars_in_dict(self):
        return vars(self)