from image import Image
from constant import Constant
from debug_print import debug_print
from constant_image import ConstantImage
class Skill(Image):

    def __init__(self, skill_name, image, center_x, center_y, scale=Constant.SKILL_IMAGE_SCALE, applied = False, greyed = True):
        self.skill_name = skill_name
        width, height = image.get_rect().size
        self.applied = applied
        self.can_applied = False
        self.greyed = greyed
        super().__init__(image, center_x, center_y, int(height*scale), int(width*scale))


    def skill_handler(self, cur_villager,villagers_list, monster, player):
        skill_name_handler = {
            "animal": self.animal_handler,
            "armour": self.armour_handler,
            "gym": self.armour_handler,
            "plant": self.plant_handler,
            "sword": self.sword_handler,
            "house": self.house_handler
        }

        skill_function = skill_name_handler[self.skill_name]
        skill_function(cur_villager, villagers_list, monster, player)

    def animal_handler(self,cur_villager, villagers_list, monster, player):

        if self.applied:
            return

        if self.can_applied:
            for one_tile in cur_villager.land.tiles:
                if one_tile.tile_type == Constant.TILE_TYPE_ANIMAL:
                    one_tile.display_plant_or_animal = True
                    self.applied = True
                    self.greyed = False

    def armour_handler(self, cur_villager,villagers_list, monsters, player):

        if self.applied:
            return
        if self.can_applied:
            cur_villager.addItemToLeftHand(ConstantImage.ARMOUR_IMAGE_SPRITE,Constant.ITEM_NAME_ARMOUR ,Constant.ARMOUR_IMAGE_SCLAE)
            self.applied = True

    def plant_handler(self,cur_villager ,villagers_list, monster, player):
        if self.can_applied:
            for one_tile in cur_villager.land.tiles:
                if one_tile.tile_type == Constant.TILE_TYPE_PLANT:
                    one_tile.display_plant_or_animal = True
                    self.applied = True

    def sword_handler(self, cur_villager,villagers_list, monsters, player):
        if self.can_applied:
            cur_villager.addItemToRightHand(ConstantImage.ARMOUR_IMAGE_SPRITE,Constant.ITEM_NAME_ARMOUR ,Constant.ARMOUR_IMAGE_SCLAE)
            self.applied = True

    # housebuilder
    def house_handler(self, cur_villager,villagers_list, monsters, player):

        if self.applied:
            return

        if self.can_applied:
            cur_villager.addHouse()
            self.applied = True

    def render(self, screen):
        # if applied show full image with out transparency
        if self.greyed:
            self.image.set_alpha(100)
            self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))

        else:
            self.image.set_alpha(255)
            self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))



