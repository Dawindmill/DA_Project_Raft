import pygame
import threading
import socket
import json
import random
from enum import Enum

GAME_NAME = "Heritage"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FRAME_PER_SECOND = 60

WHITE = (225, 225, 225)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (225, 0, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 225)

VILLAGER_IMAGES = ["assets/villager_m.png", "assets/villager_f.png"]
MONSTER_IMAGE = "assets/monster.png"
PLAYER_IMAGE = "assets/sage.png"
#MESSAGE_IMAGE = "assets/message.png"

VILLAGER_POSITIONS = [(100, 100), (200, 100), (300, 100), (400, 100), (500, 100), (600, 100),
                      (600, 300), (500, 300), (400, 300), (300, 300), (200, 300), (100, 300)]
MONSTER_POSITIONS = [(20, 50), (20, 100), (20, 150)]
SAGE_POSITION = (300, 500)

FONT_NAME = "comicsansms"
FONT_SIZE = 10

MESSAGE_TYPE = "msg_type"

# different message types
APPEND = "append_entries_leader"
APPEND_REPLY = "append_entries_follower_reply"
REQUEST_VOTE = "request_vote"
REQUEST_VOTE_REPLY = "request_vote_reply"
REQUEST_COMMAND = "request_command"
SERVER_INFO = "information"

SEND_FROM = "send_from"
SEND_TO = "send_to"

PEER_ID = "peer_id"

NEW_ENTRIES = "new_entries"

AUTHORITY_MESSAGE = "I'm the leader!"

HOST_INDEX = 0
PORT_INDEX = 1

MESSAGE_TYPES = [APPEND, APPEND_REPLY, REQUEST_VOTE, REQUEST_VOTE_REPLY, REQUEST_COMMAND, SERVER_INFO]

MESSAGE_TIME = 5*FRAME_PER_SECOND

ONE_DAY = 20*FRAME_PER_SECOND
DAY_TIME = ONE_DAY / 4 *3
NIGHT_TIME = ONE_DAY / 4

DEBUG = True

day_countdown = ONE_DAY

class Role(Enum):
    LEADER = 1
    CANDIDATE = 2
    FOLLOWER = 3


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


class Villager(Image, threading.Thread):

    HEAL_BAR_HEIGHT = 5

    def __init__(self, socket_set, image, position, villager_id, font):
        self.role = Role.LEADER
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
        self.request_parser = VillagerListener(self)
        threading.Thread.__init__(self)

    def run(self):
        self.request_parser.start()
        while not self.dead:
            while self.requests:
                request = self.requests.pop(0)
                request_type = request[MESSAGE_TYPE]
                if request_type == SERVER_INFO:
                    self.set_info(request)
                elif request_type == APPEND and self.role == Role.LEADER:
                    if not request[NEW_ENTRIES]:
                        self.reclaim_authority()
                elif request_type == APPEND_REPLY:
                    self.learned_skill(request)
            if self.current_health == 0:
                self.dead = True
        if self.dead:
            data = {MESSAGE_TYPE: "villager_killed", PEER_ID: self.peer_id}
            self.socket.sendall(str.encode(json.dumps(data)))

    def set_info(self, info):
        self.host = info["host"]
        self.listening_port = info["port"]
        self.peer_id = info["peer_id"]

    def reclaim_authority(self):
        self.current_message = AUTHORITY_MESSAGE
        self.message_countdown = MESSAGE_TIME

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

        name = self.font.render("Villager " + str(self.villager_id), 1, BLACK)
        screen.blit(name, (self.x - name.get_width() // 2, self.y + self.height // 2))

        if self.role != Role.FOLLOWER:
            if self.role == Role.LEADER:
                m = "Leader"
            else:
                m = "Candidate"
            role = self.font.render(m, 1, BLACK)
            screen.blit(role, (self.x - role.get_width() // 2, self.y + self.height // 2 + role.get_height() + 2))

        if self.message_countdown > 0:
            debug_print("printing messages")
            message = self.font.render(self.current_message, 1, BLACK)
            screen.blit(message, (self.x - message.get_width() // 2, self.y - self.height // 2 - message.get_height() - 2))
            self.message_countdown -= 1

        pygame.draw.rect(screen, GRAY, pygame.Rect((self.x - self.width // 2,
                                                    self.y - self.height // 2),
                                                   (self.width, Villager.HEAL_BAR_HEIGHT)))
        pygame.draw.rect(screen, RED, pygame.Rect((self.x - self.width // 2,
                                                   self.y - self.height // 2),
                                                  (self.width * (self.current_health / self.max_health),
                                                   Villager.HEAL_BAR_HEIGHT)))


class VillagerListener(threading.Thread):

    def __init__(self, villager):
        self.villager = villager
        self.in_msg = ""
        threading.Thread.__init__(self)

    def parse_message(self, msg):
        try:
            json_data = json.loads(msg)
            message_type = json_data[MESSAGE_TYPE]
        except Exception as e:
                debug_print(" deserialization recv json data failed " + str(e))

        if message_type in MESSAGE_TYPES:
            return json_data
        else:
            debug_print("message type not found: "+message_type)

    def run(self):
        while True:
            self.in_msg += self.villager.socket.recv(1024).decode("utf-8")
            if self.in_msg:
                debug_print("in message: .")
                debug_print(self.in_msg)
                debug_print(".")
            if "\n" in self.in_msg:
                msg_split_list = self.in_msg.split("\n")
                self.in_msg = msg_split_list[-1]
                msg_split_list = msg_split_list[0:-1]
                while msg_split_list:
                    one_msg = msg_split_list.pop(0)
                    parsed = self.parse_message(one_msg)
                    if parsed:
                        self.villager.requests.append(parsed)

            #debug_print("message list: ")
            #debug_print(self.messages)

class Monster(Image):

    def __init__(self, image, center_x, center_y):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)

class Player(Image):

    def __init__(self, image, center_x, center_y):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height, width)

class NightEvent(threading.Thread):
    Events = {"monster": []}

    def __init__(self):
        self.current_event = None
        super().__init__(self)

    def random_event(self):
        if day_countdown < NIGHT_TIME and self.current_event == None:
            print()


class ConnectionListener(threading.Thread):

    host = "192.168.1.104"
    #host = "10.13.225.187"
    port = 8888
    nodes = []
    listening = True
    skt = None

    def __init__(self, nodes):
        self.nodes = nodes
        threading.Thread.__init__(self)

    def run(self):
        self.skt = socket.socket()
        self.skt.bind((self.host, self.port))
        self.skt.listen(5)
        debug_print("Listener started listinging on port " + str(self.port))
        while self.listening:
            villager_connection = self.skt.accept()
            self.nodes.append(villager_connection)

    def close_socket(self):
        self.skt.close()



def start_game(screen, font, villager_images, monster_image, clock, villagers_connections, player):
    done = False

    global day_countdown

    villager_count = 0
    villagers = []
    monster = Monster(monster_image, MONSTER_POSITIONS[0][0], MONSTER_POSITIONS[0][1])
    monster2 = Monster(monster_image, MONSTER_POSITIONS[1][0], MONSTER_POSITIONS[1][1])
    next_villager_id = 1


    while not done:
        while villagers_connections and villager_count < len(VILLAGER_POSITIONS):
            node_socket, information = villagers_connections.pop(0)
            gender = random.randint(0,10) % 2
            villager = Villager(node_socket, villager_images[gender],
                                VILLAGER_POSITIONS[villager_count],next_villager_id, font)
            villagers.append(villager)
            villager.start()
            villager_count += 1
            next_villager_id += 1
        screen.fill(WHITE)
        for v in villagers:
            if not v.dead:
                v.render(screen)
        player.render(screen)
        monster.render(screen)
        monster2.render(screen)

        if day_countdown <= 0:
            day_countdown = ONE_DAY
        elif day_countdown <= NIGHT_TIME:
            screen.fill(BLACK)

        day_countdown -= 1

        #a+=1
        #pygame.draw.rect(screen, (255,0,0), pygame.Rect((x,y), (100,100)))
        #if (x != 400):
            #x+=2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        pygame.display.flip()
        clock.tick(FRAME_PER_SECOND)

def debug_print(message):
    if DEBUG:
        print(message)

def main():
    pygame.__init__(GAME_NAME)
    pygame.init()
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(WHITE)
    villager_images = []
    for image in VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    player_image = pygame.image.load(PLAYER_IMAGE)
    monster_image = pygame.image.load(MONSTER_IMAGE)
    clock = pygame.time.Clock()
    villager_connections = []
    listener = ConnectionListener(villager_connections)
    listener.start()
    player = Player(player_image, SAGE_POSITION[0], SAGE_POSITION[1])
    start_game(screen, font, villager_images, monster_image, clock, villager_connections, player)
    listener.close_socket()

if __name__ == "__main__":
    main()