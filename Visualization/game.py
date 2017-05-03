import pygame
import threading
import socket
import json
import random
from enum import Enum
from image import Image
from villager import Villager
from villager_listener import VillagerListener
from constant import Constant
from debug_print import *
from connection_listener import ConnectionListener
from monster import Monster
from player import Player

day_countdown = Constant.ONE_DAY

def start_game(screen, font, villager_images, monster_image, clock, villagers_connections, player):
    done = False

    global day_countdown

    villager_count = 0
    villagers = []
    monster = Monster(monster_image, Constant.MONSTER_POSITIONS[0][0], Constant.MONSTER_POSITIONS[0][1])
    monster2 = Monster(monster_image, Constant.MONSTER_POSITIONS[1][0], Constant.MONSTER_POSITIONS[1][1])
    next_villager_id = 1


    while not done:
        while villagers_connections and villager_count < len(Constant.VILLAGER_POSITIONS):
            node_socket, information = villagers_connections.pop(0)
            gender = random.randint(0,10) % 2
            villager = Villager(node_socket, villager_images[gender],
                                Constant.VILLAGER_POSITIONS[villager_count],next_villager_id, font)
            villagers.append(villager)
            villager.start()
            villager_count += 1
            next_villager_id += 1
        screen.fill(Constant.WHITE)
        for v in villagers:
            if not v.dead:
                v.render(screen)
        player.render(screen)
        monster.render(screen)
        monster2.render(screen)

        if day_countdown <= 0:
            day_countdown = Constant.ONE_DAY
        elif day_countdown <= Constant.NIGHT_TIME:
            screen.fill(Constant.BLACK)

        day_countdown -= 1

        #a+=1
        #pygame.draw.rect(screen, (255,0,0), pygame.Rect((x,y), (100,100)))
        #if (x != 400):
            #x+=2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        pygame.display.flip()
        clock.tick(Constant.FRAME_PER_SECOND)



def main():
    # pygame.__init__(GAME_NAME)
    pygame.init()
    pygame.display.set_caption(Constant.GAME_NAME)
    font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SIZE)
    screen = pygame.display.set_mode((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
    screen.fill(Constant.WHITE)
    villager_images = []
    for image in Constant.VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    player_image = pygame.image.load(Constant.PLAYER_IMAGE)
    monster_image = pygame.image.load(Constant.MONSTER_IMAGE)
    clock = pygame.time.Clock()
    villager_connections = []
    # listener = ConnectionListener(villager_connections)
    # listener.start()
    player = Player(player_image, Constant.SAGE_POSITION[0], Constant.SAGE_POSITION[1])
    start_game(screen, font, villager_images, monster_image, clock, villager_connections, player)
    # listener.close_socket()

if __name__ == "__main__":
    main()