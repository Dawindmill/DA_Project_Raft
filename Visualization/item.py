from image import Image
from constant import Constant
import pygame
class Item(Image):

    def __init__(self, image, center_x, center_y, item_name,scale):
        self.item_name = item_name

        width, height = image.get_rect().size

        super().__init__(image, center_x, center_y, int(height*scale), int(width*scale))


