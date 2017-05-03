import logging

logger = logging.getLogger("RequestVote")
logger.setLevel(logging.DEBUG)

class RequestVoteReceive:
    def __init__(self, request_vote_json_dict, raft_peer_state):
        self.msg_type = request_vote_json_dict["msg_type"]
        self.send_from = tuple(request_vote_json_dict["send_from"])
        self.send_to = tuple(request_vote_json_dict["send_to"])
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
                               "vote_granted": True}
        if self.raft_peer_state.peer_state == "leader":
            request_vote_result["vote_granted"] = False
            return request_vote_result

        # if this peer has no log, there is no any peer could have worst log than it
        if len(self.raft_peer_state.state_log) == 0:
            return request_vote_result

        if self.raft_peer_state.vote_for != None:
            request_vote_result["vote_granted"] = False
            return request_vote_result

        if self.raft_peer_state.current_term > self.candidate_term:
            request_vote_result["vote_granted"] = False
            return request_vote_result

        if self.raft_peer_state.vote_for != None:
            request_vote_result["vote_granted"] = False
            return request_vote_result

        # commit index not used in raft paper
        #if self.raft_peer_state.commit_index >

        #at least up to date is fine?
        #ini last_log_index is -1 and state_log len is 0
        if (len(self.raft_peer_state.state_log) -1) > self.last_log_index:
            request_vote_result["vote_grantned"] = False
            return request_vote_result
        # if same log length, but current peer has newer term, then reject the candidate request
        if (len(self.raft_peer_state.state_log) - 1) == self.last_log_index:
            if self.raft_peer_state.state_log[self.last_log_index].log_term > self.last_log_term:
                request_vote_result["vote_grantned"] = False
                return request_vote_result

        self.raft_peer_state.vote_for = self.send_from
        return request_vote_result
