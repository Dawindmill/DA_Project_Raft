from tile import Tile
from constant import Constant
class Land:
    def __init__(self, land_owner, land_size):
        self.land_ownder = land_owner
        self.plant_count_down = 0
        self.animal_count_down = 0
        self.tiles = []
        self.land_size = land_size
        self.init_land()

    def init_land(self):
        for i in range(self.land_size//2):
            self.tiles.append(Tile(Constant.TILE_TYPE_PLANT, self.land_ownder.x, self.land_ownder.y, self.land_ownder.height, 0, i ))

        for i in range(self.land_size//2):
            self.tiles.append(Tile(Constant.TILE_ANIMAL_IMAGE, self.land_ownder.x, self.land_ownder.y, self.land_ownder.height, 1, i))


    def render(self, screen):
        for one_tile in self.tiles:
            one_tile.render(screen)
