from image import Image
from constant import Constant
import pygame
class House(Image):

    def __init__(self, owner_center_x, owner_center_y):
        image = pygame.image.load(Constant.HOUSE_IMAGE)

        self.display_house = False
        self.max_durability = Constant.HOUSE_DURABILITY
        self.current_durability = Constant.HOUSE_DURABILITY
        width, height = image.get_rect().size


        center_x = owner_center_x
        center_y = owner_center_y

        super().__init__(image, center_x, center_y, int(height*Constant.HOUSE_IMAGE_SCALE), int(width*Constant.HOUSE_IMAGE_SCALE))

    def house_durability_decrement_with_amount(self, durability_decrement):
        """
        This method is used to decrese the duralibity of the house, when it reached 0
        villager can't not longer protected by the house
        
        :param durability_decrement: int
        
        """
        if self.current_durability >= durability_decrement:
            self.current_durability -= durability_decrement
        else:
            self.current_durability = 0

        # if the durability is 0 dont display house
        if self.current_durability <= 0:
            self.display_house = False

    def house_durability_increase_with_amount(self, durability_increment):
        """
        this method will increase the durability of the house
        
        :param durability_increment: int
        
        """
        if self.current_durability == self.max_durability:
            return

        self.current_durability += durability_increment
        if self.current_durability > self.max_durability:
            self.current_durability = self.max_durability
            self.display_house = True

    def render(self, screen):
        if self.display_house:
            # not sure why self.image.set_alpha(100) does not work
            # this works on images with per pixel alpha too
            # credit to http://stackoverflow.com/questions/12879225/pygame-applying-transparency-to-an-image-with-alpha
            # house will become transparent, the degree of transparency is depending on current house durability
            alpha_image = self.image.copy()
            alpha = int (255 * (self.current_durability/self.max_durability))
            alpha_image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            self.image_rect = screen.blit(alpha_image, (self.x - self.width//2, self.y - self.height//2))

