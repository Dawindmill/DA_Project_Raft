class RaftPeerData:
    def __init__(self, addr_port_tupe):
        self.my_addr_port_tuple = addr_port_tupe
        self.current_term = 0
        #can set it to addr_port_tuple?
        self.vote_for = None
        #might not be used but for completeness of Raft
        state_log = []
        

