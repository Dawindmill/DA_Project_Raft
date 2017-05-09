from image import Image
from constant import Constant
from debug_print import debug_print
class Skill(Image):

    def __init__(self, skill_name, image, center_x, center_y, scale=Constant.SKILL_IMAGE_SCALE, applied = False):
        self.skill_name = skill_name
        width, height = image.get_rect().size
        self.applied = applied
        super().__init__(image, center_x, center_y, int(height*scale), int(width*scale))


    def skill_handler(self, villagers_list, monster, player):
        skill_name_handler = {
            "animal": self.animal_handler,
            "armour": self.armour_handler,
            "bow": self.bow_handler,
            "gym": self.armour_handler,
            "plant": self.plant_handler,
            "sword": self.sword_handler,
            "tool": self.tool_handler
        }

        skill_function = skill_name_handler[self.skill_name]
        skill_function()


    def render(self, screen):
        if self.applied:
            self.image.set_alpha(255)
            self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))

        else:
            self.image.set_alpha(100)
            self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))



