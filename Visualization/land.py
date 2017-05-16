from tile import Tile
from constant import Constant
from image import Image
import pygame
class Land:
    def __init__(self, land_owner, land_size):
        self.land_ownder = land_owner
        self.plant_count_down = 0
        self.animal_count_down = 0
        self.tiles = []
        self.land_size = land_size
        self.init_land()
        fence_image = pygame.image.load(Constant.FENCE_IMAGE)
        fence_height, fence_width = fence_image.get_rect().size
        self.fence = Image(fence_image, self.tiles[0].x + self.tiles[0].width//2, self.tiles[0].y + self.tiles[0].height//2, int(fence_height * Constant.FENCE_SCALE), int(fence_width * Constant.FENCE_SCALE))

    def init_land(self):
        for i in range(self.land_size//2):
            self.tiles.append(Tile(Constant.TILE_TYPE_PLANT, self.land_ownder.x, self.land_ownder.y + 20, self.land_ownder.height, 0, i ))

        for i in range(self.land_size//2):
            self.tiles.append(Tile(Constant.TILE_TYPE_ANIMAL, self.land_ownder.x, self.land_ownder.y + 20, self.land_ownder.height, 1, i))


    def render(self, screen):
        for one_tile in self.tiles:
            one_tile.render(screen)
        self.fence.render(screen)
