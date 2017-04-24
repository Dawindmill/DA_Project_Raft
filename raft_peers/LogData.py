'''
Author: Bingfeng Liu

Date: 19/04/2017
'''


#use vars() to get instance variables' name and their values in dictioanry
class LogData:
    def __init__(self, index, term, request_command_action_list, committed,request_user_addr_port_tuple = None):
        self.log_index = index
        self.log_term = term
        # self.log_command_type = command_type
        self.log_committed = committed
        # only leader keep track of this, do not send this to other peers?
        self.majority_count = 0
        self.request_user_addr_port_tuple = request_user_addr_port_tuple
        self.request_command_action_list = request_command_action_list
    def __str__(self):
        return_dict_str = vars(self)
        return_dict_str.pop("majority_count")
        return_dict_str.pop("request_user_addr_port_tuple")
        return str(return_dict_str)

    def check_over_majority(self, majority):
        if self.majority_count >= majority:
            return True
        return False

