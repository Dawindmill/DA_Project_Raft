import logging
FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.NOTSET)
logger = logging.getLogger("RequestVote")
logger.setLevel(logging.WARN)
class RequestVote:
    def __init__(self, raft_peer_state, send_to_addr_port_tuple):
        #self.received_reply = 0
        self.msg_type = "request_vote"
        self.send_to = list(send_to_addr_port_tuple)
        self.send_from = list(raft_peer_state.my_addr_port_tuple)
        self.sender_term = raft_peer_state.current_term
        self.peer_id = raft_peer_state.peer_id
        if len(raft_peer_state.state_log) > 0:
            self.last_log_index = raft_peer_state.state_log[-1].index
            self.last_log_term = raft_peer_state.state_log[-1].term
        else:
            self.last_log_index = -1
            self.last_log_term = -1

    def __str__(self):
        return str(vars(self))

    def return_instance_vars_in_dict(self):
        return vars(self)
