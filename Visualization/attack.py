from image import Image
from constant import *
import pygame

class Attack(Image):
    def __init__(self, image ,center_x, center_y):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)