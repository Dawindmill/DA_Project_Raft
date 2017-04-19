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
    def __str__(self):
        return str(vars(self))
