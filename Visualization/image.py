import pygame
class Image:

    x = 0
    y = 0
    image = None
    height = 0
    width = 0

    def __init__(self, image, center_x, center_y, height, width):
        self.x = center_x
        self.y = center_y
        self.height = height
        self.width = width
        self.image = pygame.transform.scale(image, (width, height))

    def render(self, screen):
        screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))
