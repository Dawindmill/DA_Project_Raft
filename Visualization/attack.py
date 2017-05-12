from image import Image
from constant import *
import pygame

class AttackAnimation(Image):
    def __init__(self, image ,center_x, center_y, scale):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, int(height * scale), int(width * scale))

    def set_position(self, center_x, center_y):
        self.x = center_x
        self.y = center_y