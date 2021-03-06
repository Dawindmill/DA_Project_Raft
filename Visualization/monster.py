from image import Image
from constant import *
import random
from attack import AttackAnimation
from constant_image import ConstantImage
import pygame
from night_event import MonsterNightEvent

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
        self.attacking = False
        self.attack = AttackAnimation(ConstantImage.MONSTER_ATTACK_IMAGE_SPRITE, self.x, self.y,
                                 Constant.MONSTER_ATTACK_IMAGE_SCALE)
        self.dead = False
        self.current_health = Constant.MONSTER_MAX_HP
        self.max_health = Constant.MONSTER_MAX_HP
        self.night_event = MonsterNightEvent(self)

    def set_attack(self, hp_decrement):
        self.current_health_down_with_amount(hp_decrement)



    def current_health_down_with_amount(self, hp_decrement):
        if hp_decrement >= self.current_health:
            self.current_health = 0
            self.dead = True
            return
        self.current_health -= hp_decrement


    def attack_villager(self, alive_villager_list):
        if len(alive_villager_list) != 0:
            attack_index = random.randint(0, len(alive_villager_list) - 1)
            villager = alive_villager_list[attack_index]
            villager.being_attacked(self.attack_power)
            # see if monster get attacked by villager or not

            self.attack.set_position(villager.x, villager.y)
            self.attack_display_count_down = self.attack_display_count_down_const
            self.x = villager.x - villager.width // 2
            self.y = villager.y + int(random.random() * villager.height)
            self.attacking = True
            # after monster moved, villager attack it, so the attack image could be rendered in the right monster position
            villager.attack_monster_or_not(self)

    # need to put them on top
    def render_attack(self, screen):
        if self.attack_display_count_down != 0:
            self.attack.render(screen)
            self.attack_display_count_down -= 1
            if self.attack_display_count_down <= 0:
                self.x = self.original_x
                self.y = self.original_y
                self.attacking = False

    def render(self, screen):

        pygame.draw.rect(screen, Constant.GRAY, pygame.Rect((self.x - self.width // 2,
                                                             self.y - self.height // 2),
                                                            (self.width, Constant.HEAL_BAR_HEIGHT)))
        pygame.draw.rect(screen, Constant.RED, pygame.Rect((self.x - self.width // 2,
                                                            self.y - self.height // 2),
                                                           (self.width * (self.current_health / self.max_health),
                                                            Constant.HEAL_BAR_HEIGHT)))

        self.image_rect = screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))
