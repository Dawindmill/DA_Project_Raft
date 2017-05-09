from image import Image
import threading
from role import Role
from villager_listener import VillagerListener
from constant import Constant
from debug_print import *
from skill import Skill
import json
import pygame
from land import Land
from attack import Attack
from house import House
from item import Item
from constant_image import ConstantImage


class Villager(Image, threading.Thread):

    HEAL_BAR_HEIGHT = 5
    # for testing purpose only want to create one leader
    leader_taken = False

    def __init__(self, socket_set, image, position, villager_id, font):
        # render shouting
        self.message_count = 1
        # for testing to only create one leader
        self.skills = []
        self.max_health = 2.0
        self.current_health = 1.0
        self.requests = []
        self.current_message = ""
        self.message_countdown = 0
        self.learned_skills = []
        self.learning_skill = None
        self.host = ""
        self.listening_port = 0
        self.peer_id = ""
        self.dead = False
        self.socket = socket_set
        width, height = image.get_rect().size
        center_x, center_y = position
        super().__init__(image, center_x, center_y, height, width)
        self.villager_id = villager_id
        self.font = font
        self.attacked = False
        self.item = []
        # self.attack_display_count_down = Constant.ATTACK_DISPLAY_COUNT_DOWN
        # self.attack_display_count_down_const = Constant.ATTACK_DISPLAY_COUNT_DOWN
        self.attack = None

        #Attack(ConstantImage.VILLAGER_ATTACK_IMAGE_SPRITE, self.x, self.y)

        self.land = Land(self, Constant.LAND_SIZE)

        self.house = House(self.x, self.y)

        self.addItemToLeftHand(ConstantImage.ARMOUR_IMAGE_SPRITE,Constant.ITEM_NAME_ARMOUR ,Constant.ARMOUR_IMAGE_SCLAE)
        self.addItemToRightHand(ConstantImage.SWORD_IMAGE_SPRITE, Constant.ITEM_NAME_SWORD, Constant.SWORD_IMAGE_SCALE)

        # self.request_parser = VillagerListener(self)
        # threading.Thread.__init__(self)

    # armour
    def addItemToLeftHand(self, image, item_name, image_scale):
        width, height = image.get_rect().size
        temp_item_center_x = self.x + width * image_scale // 2
        temp_item_center_y = self.y + width * image_scale
        temp_item = Item(image, temp_item_center_x, temp_item_center_y, item_name, image_scale)
        self.item.append(temp_item)
    # sword
    def addItemToRightHand(self, image, item_name, image_scale):
        width, height = image.get_rect().size
        temp_item_center_x = self.x - width * image_scale
        temp_item_center_y = self.y
        temp_item = Item(image, temp_item_center_x, temp_item_center_y, item_name, image_scale)
        self.item.append(temp_item)

    def set_attack(self, hp_decrement):
        # self.attacked = True
        # self.attack_display_count_down = self.attack_display_count_down_const
        self.current_health_down_with_amount(hp_decrement)



    def add_skill(self, skill_name, skill_image):
        skill_num = len(self.skills)

        # each row render four skill, then go up
        one_skill = Skill(skill_name, skill_image, self.x - self.width/2 + (int (skill_num%4) * ((skill_image.get_rect().size)[0] * Constant.SKILL_IMAGE_SCALE_VILLAGER)), (self.y - self.height/2) - 15 - (int(skill_num / 4) * int((skill_image.get_rect().size)[1] * Constant.SKILL_IMAGE_SCALE_VILLAGER)), Constant.SKILL_IMAGE_SCALE_VILLAGER, False)
        self.skills.append(one_skill)

    def set_leader_role(self, role):
        if not Villager.leader_taken and role == Role.LEADER:
            Villager.leader_taken = True
            self.role = role
        else:
            self.role = Role.CANDIDATE

    def run(self):
        # self.request_parser.start()
        while not self.dead:
            while self.requests:
                request = self.requests.pop(0)
                request_type = request[Constant.MESSAGE_TYPE]
                if request_type == Constant.SERVER_INFO:
                    self.set_info(request)
                elif request_type == Constant.APPEND and self.role == Role.LEADER:
                    if not request[Constant.NEW_ENTRIES]:
                        self.reclaim_authority()
                elif request_type == Constant.APPEND_REPLY:
                    self.learned_skill(request)
            if self.current_health == 0:
                self.dead = True
        if self.dead:
            data = {Constant.MESSAGE_TYPE: "villager_killed", Constant.PEER_ID: self.peer_id}
            self.socket.sendall(str.encode(json.dumps(data)))

    def set_info(self, info):
        self.host = info["host"]
        self.listening_port = info["port"]
        self.peer_id = info["peer_id"]

    def reclaim_authority(self):
        self.current_message = Constant.AUTHORITY_MESSAGE
        self.message_countdown = Constant.MESSAGE_TIME

    def max_health_up(self):
        self.max_health += 1

    def max_health_down(self):
        self.max_health -= 1

    def current_health_up(self):
        self.current_health += 1

    def current_health_down(self):
        self.current_health -= 1

    def grab_plant_or_animal(self, tiles):
        for one_tile in tiles:
            if one_tile.mature:
                self.current_health_up_with_amount(one_tile.increase_health_amount)
                one_tile.un_mature

    def current_health_down_with_amount(self, hp_decrement):

        if self.house.display_house:
            self.house.house_durability_decrement_with_amount(hp_decrement)
            return

        if hp_decrement >= self.current_health:
            self.current_health = 0
            self.dead = True
            return
        self.current_health -= hp_decrement

    def render(self, screen):
        if self.house.display_house:
            self.house.render(screen)

        super().render(screen)

        for one_skill in self.skills:
            one_skill.render(screen)

        self.land.render(screen)
        # text blocked? need them or not ?
        name = self.font.render("Villager " + str(self.villager_id), 1, Constant.BLACK)
        screen.blit(name, (self.x - name.get_width() // 2, self.y + self.height // 2))

        if self.role != Role.FOLLOWER:
            if self.role == Role.LEADER:
                m = "Leader"
            else:
                m = "Candidate"
            role = self.font.render(m, 1, Constant.BLACK)
            screen.blit(role, (self.x - role.get_width() // 2, self.y + self.height // 2 + role.get_height() + 2))

        if self.message_countdown > 0:
            debug_print("printing messages")
            message = self.font.render(self.current_message, 1, Constant.BLACK)
            screen.blit(message, (self.x - message.get_width() // 2, self.y - self.height // 2 - message.get_height() - 2))
            self.message_countdown -= 1

        pygame.draw.rect(screen, Constant.GRAY, pygame.Rect((self.x - self.width // 2,
                                                    self.y - self.height // 2),
                                                   (self.width, Villager.HEAL_BAR_HEIGHT)))
        pygame.draw.rect(screen, Constant.RED, pygame.Rect((self.x - self.width // 2,
                                                   self.y - self.height // 2),
                                                  (self.width * (self.current_health / self.max_health),
                                                   Villager.HEAL_BAR_HEIGHT)))

        if self.role == Role.LEADER:

            pygame.draw.rect(screen, Constant.RED, pygame.Rect((self.x - self.width * 1.5,
                                                                self.y - self.height // 4),
                                                               (self.width,
                                                                self.height)))

            for i in range(self.message_count):
                message = self.font.render("I am Leader", 1, Constant.BLACK)
                screen.blit(message, (self.x - self.width * 1.5 + 1, self.y - self.height // 4 + message.get_height() * i))
            self.message_count += 1
            if self.message_count > 5:
                self.message_count = 1
        for one_item in self.item:
            one_item.render(screen)

        # if self.attacked & self.attack_display_count_down != 0:
        #     self.attack.render(screen)
        #     self.attack_display_count_down -= 0
        #     if self.attack_display_count_down == 0:
        #         self.attacked = False
