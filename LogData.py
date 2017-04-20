'''
Author: Bingfeng Liu

Date: 19/04/2017
'''


#use vars() to get instance variables' name and their values in dictioanry
class LogData:
    def __init__(self, index, term, command_type, committed):
        self.log_index = index
        self.log_term = term
        self.log_command_type = command_type
        self.log_committed = committed
        #only leader keep track of this, do not send this to other peers?
        self.majority_count = 0
    def __str__(self):
        return_dict_str = vars(self)
        return_dict_str.pop("majority_count")
        return str(return_dict_str)

    def apply_log(self, majority):
        if self.majority_count >= majority:
            print (" log apply ")

