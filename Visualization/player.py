from image import Image
from role import Role
from villager import Villager
class Player(Image):

    def __init__(self, image, center_x, center_y):
        self.last_skill = None
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)

    def find_leader(self, villager_list):
        for one_villager in villager_list:
            if one_villager.role == Role.LEADER:
                # x y is from super they are center x y
                self.x = one_villager.x + (self.width/2)
                self.y = one_villager.y
                return one_villager

    # skill => from button
    def passing_down_skill(self, skill, villager_list):
        # if this skill is already clicked just return
        #if skill.applied:
        #    return

        with Villager.lock:
            cur_leader = self.find_leader(villager_list)
            if self.last_skill == None:
                cur_leader.add_skill(skill.skill_name, skill.image_sprite)
                # disable the skill button
                skill.applied = True
                self.last_skill = skill
            else:
                for one_skill_from_villager in cur_leader.skills:
                    if self.last_skill.skill_name == one_skill_from_villager.skill_name:
                        if one_skill_from_villager.applied == False:
                            return
                        else:
                            cur_leader.add_skill(skill.skill_name, skill.image_sprite)
                            # disable the skill button
                            skill.applied = True
                            self.last_skill = skill






