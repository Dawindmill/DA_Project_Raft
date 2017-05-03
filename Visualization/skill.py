from image import Image
from constant import Constant
class Skill(Image):

    def __init__(self, skill_name, image, center_x, center_y):
        self.skill_name = skill_name
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, int(height*Constant.SKILL_IMAGE_SCALE), int(width*Constant.SKILL_IMAGE_SCALE))

    def skill_handler(self, game_state):
        print()
