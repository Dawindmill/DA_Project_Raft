import pygame
import threading
import socket
import json
import random
from enum import Enum
from image import Image
from role import Role
from villager import Villager
from villager_listener import VillagerListener
from constant import Constant
from debug_print import *
from connection_listener import ConnectionListener
from monster import Monster
from player import Player
from skill import  Skill
import sys
import os
from night_event import NightEvent

day_countdown = Constant.ONE_DAY

# skills => {skill_name: Skill()}
def start_game(screen, font, villager_images, monster_image, skills, clock, villagers_connections, player):
    global day_countdown

    villager_count = 0
    villagers = []
    monsters = []
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[0][0], Constant.MONSTER_POSITIONS[0][1]))
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[1][0], Constant.MONSTER_POSITIONS[1][1]))

    next_villager_id = 1

    global done
    done = False
    while not done:
        # while villagers_connections and villager_count < len(Constant.VILLAGER_POSITIONS):
        while villager_count < len(Constant.VILLAGER_POSITIONS):
            # node_socket, information = villagers_connections.pop(0)

            gender = random.randint(0, 10) % 2
            # villager = Villager(node_socket, villager_images[gender],
            #                     Constant.VILLAGER_POSITIONS[villager_count], next_villager_id, font)

            villager = Villager(None, villager_images[gender],
                                Constant.VILLAGER_POSITIONS[villager_count], next_villager_id, font)

            # test setting skill
            villager.add_skill("animal", skills["animal"].image_sprite)
            villager.add_skill("armour", skills["armour"].image_sprite)

            # SET LEADER TO FIRST FEMALE FOR TESTING
            if gender == 1:
                villager.set_leader_role(Role.LEADER)
            else:
                villager.set_leader_role(Role.CANDIDATE)
            villagers.append(villager)
            # diable villager thread for game devs
            # villager.start()
            villager_count += 1
            next_villager_id += 1
        screen.fill(Constant.WHITE)
        for one_villager in villagers:
            if not one_villager.dead:
                one_villager.render(screen)
        # find leader

        player.find_leader(villagers)
        player.render(screen)

        for one_monster in monsters:
            if not one_monster.dead:
                one_monster.render(screen)

        # render attack
        for one_villager in villagers:
            if not one_villager.dead:
                # apply skills
                for one_skill_from_villager in one_villager.skills:
                    one_skill_from_villager.skill_handler(one_villager, villagers, monsters, player)
                one_villager.render_attack(screen)

        for one_monster in monsters:
            if not one_monster.dead:
                one_monster.render_attack(screen)

        for one_skill in skills.values():
            one_skill.render(screen)

        if day_countdown <= 0:
            day_countdown = Constant.ONE_DAY
        elif day_countdown <= Constant.NIGHT_TIME:

            for one_monster in monsters:
                villagers_not_dead = [one_villager for one_villager in villagers if not one_villager.dead]
                one_monster.attack_villager_or_not(villagers_not_dead, True)
                # one_monster.render(screen)

            # inspired from http://stackoverflow.com/questions/6339057/draw-a-transparent-rectangle-in-pygame
            s = pygame.Surface((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))  # the size of your rect
            s.set_alpha(200)  # alpha level
            s.fill(Constant.BLACK)  # this fills the entire surface
            screen.blit(s, (0, 0))  # (0,0) are the top-left coordinates
            # debug_print("night")


        day_countdown -= 1

        # a+=1
        # pygame.draw.rect(screen, (255,0,0), pygame.Rect((x,y), (100,100)))
        # if (x != 400):
        # x+=2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False
                pygame.display.quit()
                pygame.quit()
                debug_print("quit")
                # does not close on mac so need to add os._exit(0)
                os._exit(0)
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                # debug_print(str(skills))
                clicked_skills = [(skill_name, one_skill) for skill_name, one_skill in skills.items() if one_skill.image_rect.collidepoint(pos)]
                clicked_villager_tiles_tuple = []
                for one_villager in villagers:
                    temp_tiles = []
                    for one_tile in one_villager.land.tiles:
                        if one_tile.image_rect.collidepoint(pos):
                            temp_tiles.append(one_tile)
                    clicked_villager_tiles_tuple.append((one_villager, temp_tiles))
                # debug_print("clicked image => " + str(clicked_sprites))
                if len(clicked_skills) > 0:
                    clicked_skills[0][1].applied = False

                if len(clicked_villager_tiles_tuple) > 0:
                    for one_villager, one_tile_list in clicked_villager_tiles_tuple:
                        for one_tile in one_tile_list:
                            one_villager.pickTile(one_tile)

        pygame.display.flip()
        clock.tick(Constant.FRAME_PER_SECOND)
    pygame.quit()


def main():
    # this does not work on mac
    # pygame.__init__(GAME_NAME)
    pygame.init()
    pygame.display.set_caption(Constant.GAME_NAME)
    font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SIZE)
    screen = pygame.display.set_mode((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
    screen.fill(Constant.WHITE)
    villager_images = []
    skill_images = {image_file_name.split("/")[-1]:pygame.image.load(image_file_name) for image_file_name in Constant.SKILL_IMAGES}
    skills = {}
    debug_print(str(skill_images))
    for image in Constant.VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    player_image = pygame.image.load(Constant.PLAYER_IMAGE)
    monster_image = pygame.image.load(Constant.MONSTER_IMAGE)
    clock = pygame.time.Clock()
    villager_connections = []
    night_event = NightEvent()
    night_event.getEvent()
    # listener = ConnectionListener(villager_connections)
    # listener.start()
    index = 0
    for skill_name, skill_image in skill_images.items():
        # discard the suffix
        skills[skill_name.split(".")[0]] = Skill(skill_name, skill_image,50 + index * ((skill_image.get_rect().size)[0] * Constant.SKILL_IMAGE_SCALE), Constant.SCREEN_HEIGHT - 50, Constant.SKILL_IMAGE_SCALE,True)
        index += 1
    player = Player(player_image, Constant.SAGE_POSITION[0], Constant.SAGE_POSITION[1])
    start_game(screen, font, villager_images, monster_image, skills, clock, villager_connections, player)
    # listener.close_socket()


if __name__ == "__main__":
    main()
