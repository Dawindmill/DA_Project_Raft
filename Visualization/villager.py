from image import Image
import threading
from role import Role
from villager_listener import VillagerListener
from constant import Constant
from debug_print import *
import json
import pygame
class Villager(Image, threading.Thread):

    HEAL_BAR_HEIGHT = 5
    # for testing purpose only want to create one leader
    leader_taken = False

    def __init__(self, socket_set, image, position, villager_id, font):

        # for testing to only create one leader
        self.skills = []
        self.max_health = 2
        self.current_health = 1
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
        # self.request_parser = VillagerListener(self)
        threading.Thread.__init__(self)

    def set_leader_role(self, role):
        if not Villager.leader_taken:
            Villager.leader_taken = True
            self.role = role
        else:
            self.role = role

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

    def render(self, screen):
        super().render(screen)

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