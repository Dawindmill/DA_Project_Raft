from image import Image
from role import Role
class Player(Image):

    def __init__(self, image, center_x, center_y):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)

    def find_leader(self, villager_list):
        for one_villager in villager_list:
            if one_villager.role == Role.LEADER:
                # x y is from super they are center x y
                self.x = one_villager.x + (self.width/2)
                self.y = one_villager.y