from image import Image
from role import Role
from villager import Villager
from constant import Constant
import json
from debug_print import debug_print

class Player(Image):

    def __init__(self, image, center_x, center_y):
        self.last_skill = None
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)

    def find_leader(self, villager_list):
        for one_villager in villager_list:
            if one_villager and one_villager.role == Role.LEADER:
                # x y is from super they are center x y
                self.x = one_villager.x + (self.width/2)
                self.y = one_villager.y
                return one_villager

    # skill => from button
    def passing_down_skill(self, skill, villager_list):
        # if this skill is already clicked just return
        #if skill.applied:
        #    return
        debug_print("in passing skill" + skill.skill_name)
        with Villager.lock:
            cur_leader = self.find_leader(villager_list)
            if cur_leader:
                debug_print("leader!")
                if self.last_skill == None:
                    #cur_leader.add_skill(skill.skill_name)
                    # disable the skill button
                    skill.applied = True
                    self.last_skill = skill
                    self.send_command_to_leader(skill, cur_leader)
                    return True
                else:
                    debug_print("we've got last skill!")
                    for one_skill_from_villager in cur_leader.skills:
                        if self.last_skill.skill_name == one_skill_from_villager.skill_name:
                            if one_skill_from_villager.applied == False:
                                debug_print("last skill is not applied")
                                return False
                            else:
                                #cur_leader.add_skill(skill.skill_name)
                                # disable the skill button
                                skill.applied = True
                                self.last_skill = skill
                                self.send_command_to_leader(skill, cur_leader)
                                debug_print("True returned!")
                                return True
            return False

    def send_command_to_leader(self, skill, leader):
        request = {Constant.MESSAGE_TYPE: Constant.REQUEST_COMMAND,
                   Constant.REQUEST_COMMAND_LIST: [skill.skill_name, Constant.LEARN_SKILL, True],
                   Constant.SEND_TO: [leader.listener.host, leader.listener.listening_port],
                   Constant.SEND_FROM: [Constant.GAME_HOST, Constant.GAME_PORT]}
        leader.listener.socket.sendall(str.encode(json.dumps(request) + "\n"))





