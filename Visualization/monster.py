from image import Image
from constant import *
import random
from attack import Attack


class Monster(Image):
    def __init__(self, image, center_x, center_y):
        self.attack_power = Constant.MONSTER_ATTACK_POWER
        self.original_x = center_x
        self.original_y = center_y
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)
        self.attack_probability = 0.5
        self.attack_frequent = Constant.MONSTER_ATTACK_FREQUENT
        self.attack_frequent_const = Constant.MONSTER_ATTACK_FREQUENT
        self.attack_display_count_down = Constant.ATTACK_DISPLAY_COUNT_DOWN
        self.attack_display_count_down_const = Constant.ATTACK_DISPLAY_COUNT_DOWN
        self.attacked = False
        self.attack = Attack(self.x, self.y)



    def attack_or_not(self, villager_list_not_dead, night = False):

        if self.attack_frequent > 0 and night:
            self.attack_frequent -= 1
            return
        else:
            self.attack_frequent = self.attack_frequent_const

        if self.attacked:
            return not self.attacked

        self.attacked = random.random() >= self.attack_probability

        if self.attacked and len(villager_list_not_dead) != 0:
            attack_index = random.randint(0, len(villager_list_not_dead) - 1)
            villager = villager_list_not_dead[attack_index]
            villager.set_attack(self.attack_power)
            self.attack = Attack(villager.x, villager.y)
            self.attack_display_count_down = self.attack_display_count_down_const
            self.x = villager.x - villager.width//2
            self.y = villager.y + int (random.random() * villager.height)


        return self.attacked

    def render(self, screen):

        if self.attacked and self.attack_display_count_down != 0:
            self.attack.render(screen)
            self.attack_display_count_down -= 1
            if self.attack_display_count_down <= 0:
                self.x = self.original_x
                self.y = self.original_y
                self.attacked = False


        self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))


    def find_leader(self, villager_list):

        attack_index = random.randint(0, len(villager_list) - 1)
        villager_list[attack_index].set_attack()