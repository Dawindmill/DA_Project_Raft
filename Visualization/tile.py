from image import Image
from constant import Constant
import pygame
class Tile(Image):

    def __init__(self, tile_type, owner_center_x, owner_center_y, owner_height, y_gap_factor, num,scale=Constant.TILE_IMAGE_SCALE):
        # has two phase for plant and animal, at index 0 is the inital, 1 is mature
        self.animal_or_plant = []


        if (tile_type == Constant.TILE_TYPE_PLANT):
            self.count_down_const = Constant.TREE_MATURE_COUNT_DOWN
            self.count_down = self.count_down_const
            image = pygame.image.load(Constant.TILE_PLANT_IMAGE)
            not_mature_image = pygame.image.load(Constant.TREE_IMAGE)
            height, width = not_mature_image.get_rect().size
            self.animal_or_plant.append(pygame.transform.scale(not_mature_image, (int(width * Constant.TREE_IMAGE_SCALE), int(height * Constant.TREE_IMAGE_SCALE))))

            mature = pygame.image.load(Constant.TREE_WITH_APPLE_IMAGE)
            height, width = mature.get_rect().size
            self.animal_or_plant.append(pygame.transform.scale(mature, ( int(width * Constant.TREE_WITH_APPLE_IMAGE_SCALE), int(height * Constant.TREE_WITH_APPLE_IMAGE_SCALE))))
        else:
            self.count_down_const = Constant.CHICKEN_MATURE_COUNT_DOWN
            self.count_down = self.count_down_const
            image = pygame.image.load(Constant.TILE_ANIMAL_IMAGE)
            not_mature_image = pygame.image.load(Constant.CHICKEN_EGG_IMAGE)
            height, width = not_mature_image.get_rect().size
            self.animal_or_plant.append(pygame.transform.scale(not_mature_image, (int(width * Constant.CHICHEN_EGG_IMAGE_SCALE), int(height * Constant.CHICHEN_EGG_IMAGE_SCALE))))

            mature = pygame.image.load(Constant.CHICKEN_IMAGE)
            height, width = mature.get_rect().size
            self.animal_or_plant.append( pygame.transform.scale(mature, (int(width * Constant.CHICEN_IAMGE_SCALE), int(height * Constant.CHICEN_IAMGE_SCALE))))

        self.tile_type = tile_type
        self.display_plant_or_animal = True
        self.mature = False
        width, height = image.get_rect().size
        self.applied = False


        center_x = owner_center_x - image.get_rect().width * scale + num * image.get_rect().width * scale
        center_y = owner_center_y + owner_height + y_gap_factor * image.get_rect().height * scale

        super().__init__(image, center_x, center_y, int(height*scale), int(width*scale))

    def un_mature(self):
        if self.mature == True:
            self.mature = False

    def render(self, screen):

        if not self.mature:
            self.count_down -= 1
        if self.count_down == 0:
            self.mature = True
            self.count_down = self.count_down_const

        self.image_rect = screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))
        if self.display_plant_or_animal == True:
            if self.mature:
                self.animal_image_rect = screen.blit(self.animal_or_plant[1], (self.x - self.width // 2, self.y - self.height // 2))
            else:
                self.animal_image_rect = screen.blit(self.animal_or_plant[0], (self.x - self.width // 2, self.y - self.height // 2))



