import pygame
import threading
import socket
import json
import random

GAME_NAME = "Heritage"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
FRAME_PER_SECOND = 60

WHITE = (225, 225, 225)

VILLAGER_IMAGES = ["assets/villager_m.png", "assets/villager_f.png"]
MONSTER_IMAGE = "assets/monster.png"
#MESSAGE_IMAGE = "assets/message.png"

VILLAGER_POSITIONS = [(100, 300), (200, 200), (300, 100), (400, 100), (500, 200), (600, 300),
                      (600, 400), (500, 500), (400, 600), (300, 600), (200, 500), (100, 400)]

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

HOST_INDEX = 0
PORT_INDEX = 1

MESSAGE_TYPES = [APPEND, APPEND_REPLY, REQUEST_VOTE, REQUEST_VOTE_REPLY, REQUEST_COMMAND, SERVER_INFO]

DEBUG = True

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

    socket = None
    host = ""
    listening_port = 0
    peer_id = ""
    villager_id = 0
    health = 1

    messages = []
    in_msg = ""

    def __init__(self, socket_set, image, position, id):
        self.socket = socket_set
        width, height = image.get_rect().size
        center_x, center_y = position
        super().__init__(image, center_x, center_y, height, width)
        self.villager_id = id
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.in_msg += self.socket.recv(1024).decode("utf-8")
            #debug_print("in messages")
            debug_print(self.in_msg)
            if "\n" in self.in_msg:
                msg_split_list = self.in_msg.split("\n")
                self.in_msg = msg_split_list[-1]
                for one_msg in msg_split_list[0:-1]:
                    try:
                        json_data = json.loads(one_msg)
                        if json_data[MESSAGE_TYPE] == SERVER_INFO:
                            self.host = json_data["host"]
                            self.listening_port = json_data["port"]
                            self.peer_id = json_data["peer_id"]
                        else:
                            self.messages.append(json_data)
                    except Exception as e:
                        debug_print(" deserialization recv json data failed " + str(e))
            #debug_print("message list: ")
            #debug_print(self.messages)

    def set_server_info(self, host, port, peer_id):
        self.host = host
        self.listening_port = port
        self.peer_id = peer_id

    def health_up(self):
        self.health += 1

    def health_down(self):
        self.health -= 1


'''class Message(Image):

    source = None
    dest = None
    content_str = ""
    content_json = None
    message_type = ""

    def __init__(self, image, source, dest, content_str):
        self.content_str = content_str
        width, height = image.get_rect().size
        self.source = source
        self.dest = dest
        super().__init__(image, source.x, source.y, height // 15, width // 15)

    def move(self):
        if (self.x, self.y) != (self.dest.x, self.dest.y):
            self.x += (self.dest.x - self.source.x)//100
            self.y += (self.dest.y - self.source.y)//100
            return False
        return True
'''



class MessageParser(threading.Thread):

    unparsed_messages = []
    #messages = []

    def __init__(self, unparsed_messages, messages):
        self.unparsed_messages = unparsed_messages
        self.messages = messages
        threading.Thread.__init__(self)

    def parse_next(self):
        data = self.unparsed_messages.pop(0)
        json_data = json.loads(data)
        #self.messages.append()
        message_type = json_data[MESSAGE_TYPE]

        if message_type in MESSAGE_TYPES:
            return (message_type, json_data)


class Listener(threading.Thread):

    host = "192.168.1.105"
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
            #message = villager_connection[0].recv(1024)
            #m_json = json.loads(message)
            self.nodes.append(villager_connection)

    def close_socket(self):
        self.skt.close()



def start_game(screen, villager_images, monster_image, clock, villagers_connections):
    done = False

    x = 100
    y = 100

    villager_count = 0
    #debug_print(server_nodes)
    villagers = []
    #node1 = Node(node_image, 100, 100)
    #node2 = Node(node_image, 400, 100)
    #node3 = Node(node_image, 100, 400)
    #node_list = [node1, node2, node3]
    #message1 = Message(message_image,node1,node2)
    #message2 = Message(message_image,node1,node3)
    #message_list = [message1]
    a = 0
    while not done:
        #if server_nodes:
            #debug_print(server_nodes)
        while villagers_connections:
            node_socket, information = villagers_connections.pop(0)
            gender = random.randint(0,10) % 2
            villager = Villager(node_socket, villager_images[gender],
                                VILLAGER_POSITIONS[villager_count],villager_count + 1)
            villagers.append(villager)
            villager.start()
            villager_count += 1
        screen.fill((255,255,255))
        '''node1.render(screen)
        node2.render(screen)
        node3.render(screen)
        message1.move()
        message1.render(screen)
        message2.move()
        message2.render(screen)'''
        for v in villagers:
            #debug_print("villager!")
            v.render(screen)
            #debug_print("rendered!")
        '''for message in message_list:
            arrived = message.move()
            message.render(screen)
            if arrived:
                message_list.remove(message)
        if (a == 15):
            message_list.append(message2)'''
        #a+=1
        #pygame.draw.rect(screen, (255,0,0), pygame.Rect((x,y), (100,100)))
        #if (x != 400):
        #    x+=2
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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(WHITE)
    villager_images = []
    for image in VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    #message_image = pygame.image.load(MESSAGE_IMAGE)
    monster_image = None
    clock = pygame.time.Clock()
    villager_connections = []
    listener = Listener(villager_connections)
    listener.start()
    start_game(screen, villager_images, monster_image, clock, villager_connections)
    listener.close_socket()

if __name__ == "__main__":
    main()