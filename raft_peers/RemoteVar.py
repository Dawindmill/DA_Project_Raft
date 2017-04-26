'''

Author: Bingfeng Liu
Date Created: 24/04/2017

'''

import _thread


class RemoteVar:
    def __init__(self):
        self.lock = _thread.allocate_lock()
        # dictionary key is the var name, and value is var's value
        self.vars = {}

    # param list [0] => var name, [1] => action func， [2] => action func single param
    def perform_action(self, action_param_list):
        if str(action_param_list[0]) not in self.vars:
            self.vars[str(action_param_list[0])] = 0.0

        action_funcs = {"add":self.add,
                        "sub":self.sub,
                        "div":self.div,
                        "time":self.time}

        action_func = action_funcs[str(action_param_list[1])]
        action_func(str(action_param_list[0]),float(action_param_list[2]))

    def add(self, var_name, action_param):
        self.vars[var_name] += action_param

    def sub(self, var_name, action_param):
        self.vars[var_name] -= action_param

    def div(self, var_name, action_param):
        self.vars[var_name] /= action_param

    def time(self, var_name, action_param):
        self.vars[var_name] *= action_param

    def __str__(self):
        return str(vars(self))



