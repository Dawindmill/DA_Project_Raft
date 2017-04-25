'''
Author: Bingfeng Liu
Created Date: 18/04/2017
'''
import _thread
import threading
from LogData import LogData

class RaftPeerState:
    def __init__(self, addr_port_tuple, peer_id):
        # self.lock = _thread.allocate_lock()
        self.lock = threading.RLock()
        self.peer_id = peer_id
        self.my_addr_port_tuple = addr_port_tuple
        self.current_term = -1
        # can set it to addr_port_tuple?
        self.vote_for = None
        # might not be used but for completeness of Raft
        self.state_log = []
        self.commit_index = -1
        self.last_apply = -1
        # reinitialize after election use self next index?
        # peer_addr_port_tuple and its next index
        self.peers_next_index = {}
        self.peers_match_index = {}
        #follower, candidate, leader
        self.peer_state = "follower"
        self.leader_majority_count = 0

    def initialize_peers_next_and_match_index(self, peers_addr_port_tuple_list):
        next_index = len(self.state_log)
        self.peers_next_index = {peer_addr_port_tuple:next_index for peer_addr_port_tuple in peers_addr_port_tuple_list}
        self.peers_match_index = {peer_addr_port_tuple:-1 for peer_addr_port_tuple in peers_addr_port_tuple_list}
    def increment_leader_majority_count(self):
        if self.peer_state == "candidate":
            self.leader_majority_count += 1

    def elected_leader(self, majority):
        if self.leader_majority_count >= majority and self.peer_state == "candidate":
            self.peer_state = "leader"
            self.leader_majority_count = 0
            return True
        return False



    def top_horizontal_line_with_num(self, max_length):
        horizontal_line = "-"
        return " " + (horizontal_line * max_length) + " " + "\n"

    def top_horiozntal_line_with_middle_vertical_line(self, middle_vertical_line):
        horizontal_line = "-"
        return " " + (horizontal_line * (len(middle_vertical_line) -3 )) + " " + "\n"

    def middle_vertical_line_for_list(self, data_name, num_elem_break, data_list):
        middle_vertical_line = ""
        vertical_line = "|"

        temp_middle_vertical_line = " "
        max_len = -1
        for index, elem in enumerate(data_list):
            if (index + 1) % (num_elem_break) == 0:
                temp_middle_vertical_line += str(elem) + " "
                middle_vertical_line += temp_middle_vertical_line
                middle_vertical_line += "\n"
                if len(temp_middle_vertical_line) > max_len:
                    max_len = len(temp_middle_vertical_line)
                temp_middle_vertical_line = " "
                continue
            temp_middle_vertical_line += str(elem) + " "

        middle_vertical_line += temp_middle_vertical_line
        #print( "=> " + str(middle_vertical_line))

        temp_header = "| " + str(data_name) + " "
        if len(temp_header) > max_len:
            max_len = len(temp_header)
            temp_header += (len(temp_header) - max_len) * " " + " |\n"
        else:
            temp_header += (max_len - len(temp_header) ) * " " + " |\n"

        temp_middle_vertical_line = ""
        for one_split_line in middle_vertical_line.split("\n"):
            if one_split_line == " " or one_split_line == "":
                continue
            temp_space_gap = max_len - len(one_split_line)
            temp_middle_vertical_line += vertical_line + one_split_line + " " * temp_space_gap + vertical_line +"\n"
        middle_vertical_line = temp_header + temp_middle_vertical_line
        return (max_len, middle_vertical_line)



    def middle_vertical_line_msg(self, name_value_pair_tuple_list):
        middle_vertical_line = ""
        vertical_line = "|"
        middle_vertical_line += vertical_line
        for name, value in name_value_pair_tuple_list:
            middle_vertical_line += " " + str(name) + " => " + str(value) + " " + vertical_line
        return middle_vertical_line


    def __str__(self, *args, **kwargs):
        state_str = ""
        horizontal_line = "-"
        vertical_line = "|"
        middle_vertical_line = self.middle_vertical_line_msg([("my_addr_port", self.my_addr_port_tuple)])

        state_str += self.top_horiozntal_line_with_middle_vertical_line(middle_vertical_line)
        state_str += middle_vertical_line + "\n"

        middle_vertical_line = self.middle_vertical_line_msg(vars(self).items())
        state_str += self.top_horiozntal_line_with_middle_vertical_line(middle_vertical_line)
        state_str += middle_vertical_line + "\n"

        max_length, state_str_temp = self.middle_vertical_line_for_list("state_log", 3, self.state_log)
        state_str += self.top_horizontal_line_with_num(max_length)
        state_str += state_str_temp


        #
        max_length, state_str_temp = self.middle_vertical_line_for_list("peers_next_index", 3,sorted(self.peers_next_index.items(), key = lambda x:x[0]))
        state_str += self.top_horizontal_line_with_num(max_length)
        state_str += state_str_temp
        #
        max_length, state_str_temp = self.middle_vertical_line_for_list("peers_match_index", 3, sorted(self.peers_match_index.items(), key = lambda x:x[0]))
        state_str += self.top_horizontal_line_with_num(max_length)
        state_str += state_str_temp
        state_str += self.top_horizontal_line_with_num(max_length)

        return state_str







