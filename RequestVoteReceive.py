import logging
FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.NOTSET)
logger = logging.getLogger("RequestVote")
logger.setLevel(logging.WARN)

class RequestVoteReceive:
    def __init__(self, request_vote_json_dict, raft_peer_state):
        self.msg_type = request_vote_json_dict["msg_type"]
        self.send_from = request_vote_json_dict["send_from"]
        self.send_to = request_vote_json_dict["send_to"]
        self.candidate_term = request_vote_json_dict["sender_term"]
        self.candidate_id = request_vote_json_dict["peer_id"]
        self.last_log_index = request_vote_json_dict["last_log_index"]
        self.last_log_term = request_vote_json_dict["last_log_term"]
        self.raft_peer_state = raft_peer_state

    def process_request_vote(self):
    # leader append entries without lock is fine because there is always one leader?
        request_vote_result = {"msg_type": "request_vote_reply",
                               "send_to": list(self.send_from),
                               "send_from": list(self.raft_peer_state.my_addr_port_tuple),
                               "sender_term": self.raft_peer_state.current_term,
                               "vote_grantned": True}

        if self.raft_peer_state.current_term > self.candidate_term:
            request_vote_result["vote_grantned"] = False
            return request_vote_result

        #put a lock here?
        if self.raft_peer_state.vote_for != None:
            request_vote_result["vote_grantned"] = False
            return request_vote_result

        #at least up to date is fine?
        if (len(self.raft_peer_state.state_log) -1) >= self.last_log_index:
            if self.raft_peer_state.state_log[self.last_log_index].term > self.last_log_term:
                request_vote_result["vote_grantned"] = False
                return request_vote_result
        return request_vote_result
