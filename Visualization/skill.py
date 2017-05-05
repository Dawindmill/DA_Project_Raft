from image import Image
from constant import Constant
class Skill(Image):

    def __init__(self, skill_name, image, center_x, center_y, scale=Constant.SKILL_IMAGE_SCALE):
        self.skill_name = skill_name
        width, height = image.get_rect().size
        self.applied = False
        super().__init__(image, center_x, center_y, int(height*scale), int(width*scale))

    def skill_handler(self, villagers_list, monster, player):
        self.skill_name == "apple"
        self.set_health(villagers_list)
        print()

