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
def start_game(screen, font, villager_images, monster_image, skills, skill_images, clock, villagers_connections, player, s):
    global day_countdown

    villager_count = 0
    villagers = []
    monsters = []
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[0][0], Constant.MONSTER_POSITIONS[0][1]))
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[1][0], Constant.MONSTER_POSITIONS[1][1]))

    #next_villager_id = 1

    global done
    done = False

    listener_list = []
    existing_peer_ids = []
    alive_villagers_list = []
    current_leader = None
    while not done:
        while villagers_connections and villager_count < len(Constant.VILLAGER_POSITIONS):
        #while villager_count < len(Constant.VILLAGER_POSITIONS):
            node_socket, information = villagers_connections.pop(0)

            listener = VillagerListener(node_socket)

            listener_list.append(listener)
            listener.daemon = True
            listener.start()
            # print("start listeners")

            debug_print("listener list: ")
            debug_print(listener_list)

        for listener in listener_list:
            # print(" listener_list")
            if len(alive_villagers_list) < len(Constant.VILLAGER_POSITIONS):
                #debug_print("in game")
                if listener.info_set:
                    debug_print("info set")
                    listener_list.remove(listener)
                    if listener.peer_id not in existing_peer_ids:
                        existing_peer_ids.append(listener.peer_id)
                        gender = random.randint(0, 10) % 2
                        villager_id = int(listener.peer_id[4:])
                        if len(villagers) < len(Constant.VILLAGER_POSITIONS):
                            position = Constant.VILLAGER_POSITIONS[len(villagers)]
                            villager = Villager(villager_images[gender], position,
                                                villager_id, font, listener, current_leader, skill_images)
                            villagers.append(villager)
                        else:
                            for i in range(len(villagers)):
                                if not villagers[i]:
                                    position = Constant.VILLAGER_POSITIONS[i]
                                    villager = Villager(villager_images[gender], position,
                                                        villager_id, font, listener, current_leader, skill_images)
                                    villagers[i] = villager
                                    break
                        alive_villagers_list.append(villager)

                        # test setting skill
                        #villager.add_skill("animal", skills["animal"].image_sprite)
                        #villager.add_skill("armour", skills["armour"].image_sprite)

                        # SET LEADER TO FIRST FEMALE FOR TESTING
                        #if gender == 1:
                        #    villager.set_leader_role(Role.LEADER)
                        #else:
                        #    villager.set_leader_role(Role.CANDIDATE)
                        #villagers.append(villager)
                        # diable villager thread for game devs
                        villager.daemon = True
                        villager.start()
                        villager_count += 1
                        #next_villager_id += 1
                        debug_print(villagers)
            else:
                break

        screen.fill(Constant.WHITE)

        for villager_index in range(len(villagers)):
            villager = villagers[villager_index]
            if villager:
                if not villager.dead:
                    villager.render(screen)

                    if villager.turning_learned_skills_list:
                        villager.learned_skill(None)

                        for one_skill_from_villager in villager.skills:
                            one_skill_from_villager.skill_handler(villager, villagers, monsters, player)
                        villager.render_attack(screen)
                else:
                    alive_villagers_list.remove(villager)
                    existing_peer_ids.remove(villager.listener.peer_id)
                    villagers[villager_index] = None
                    villager_count -= 1
        # find leader

        new_leader = player.find_leader(villagers)
        player.render(screen)
        if new_leader != current_leader:
            current_leader = new_leader
            for villager in villagers:
                if villager:
                    villager.current_leader = new_leader

        for one_monster in monsters:
            if not one_monster.dead:
                one_monster.render(screen)

        # render attack
        '''for one_villager in villagers:
            if one_villager and not one_villager.dead:
                if one_villager.turning_learned_skills_list:
                    one_villager.learned_skill(None)
                # apply skills
                for one_skill_from_villager in one_villager.skills:
                    one_skill_from_villager.skill_handler(one_villager, villagers, monsters, player)
                one_villager.render_attack(screen)'''

        '''for one_monster in monsters:
            if not one_monster.dead:
                one_monster.render_attack(screen)'''

        for one_skill in skills.values():
            greyed = False
            if current_leader:
                for l_skill in current_leader.skills:
                    if one_skill.skill_name == l_skill.skill_name:
                        greyed = True
                        break
            one_skill.greyed = greyed
            one_skill.render(screen)

        #print(" day_countdown " + str(day_countdown))
        if day_countdown <= 0:
            day_countdown = Constant.ONE_DAY
        elif day_countdown <= Constant.NIGHT_TIME:
            #print ("night")
                #alive_villagers_list = [one_villager for one_villager in villagers if not one_villager.dead]
            for monster in monsters:
                if not monster.dead:
                    if day_countdown == Constant.NIGHT_TIME:
                        monster.night_event.perform_event(alive_villagers_list)

                    monster.night_event.render_event(screen)

            '''for one_monster in monsters:
                villagers_not_dead = [one_villager for one_villager in villagers if not one_villager.dead]
                one_monster.attack_villager_or_not(villagers_not_dead, True)
                # one_monster.render(screen)'''

            '''for monster in monsters:
                if not monster.dead:'''

            # inspired from http://stackoverflow.com/questions/6339057/draw-a-transparent-rectangle-in-pygame
            #s = pygame.Surface((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))  # the size of your rect
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
                    if not one_villager:
                        continue
                    temp_tiles = []
                    for one_tile in one_villager.land.tiles:
                        if one_tile.image_rect.collidepoint(pos):
                            temp_tiles.append(one_tile)
                    clicked_villager_tiles_tuple.append((one_villager, temp_tiles))
                # debug_print("clicked image => " + str(clicked_sprites))
                if len(clicked_skills) > 0:
                    skill = clicked_skills[0][1]
                    if (not skill.applied) and (not skill.greyed):
                        applied = player.passing_down_skill(clicked_skills[0][1], alive_villagers_list)
                        if applied:
                            skill.greyed = True

                if len(clicked_villager_tiles_tuple) > 0:
                    for one_villager, one_tile_list in clicked_villager_tiles_tuple:
                        for one_tile in one_tile_list:
                            one_villager.pickTile(one_tile)

        pygame.display.flip()
        clock.tick(Constant.FRAME_PER_SECOND)
    pygame.quit()


def main():
    print ("start")
    # this does not work on mac
    # pygame.__init__(GAME_NAME)
    pygame.init()
    print("start init")
    pygame.display.set_caption(Constant.GAME_NAME)
    print("start caption")
    # font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SIZE)
    font = pygame.font.Font(Constant.FONT_NAME, 25)
    print("start font")
    screen = pygame.display.set_mode((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
    screen.fill(Constant.WHITE)
    villager_images = []
    skill_images = {(image_file_name.split("/")[-1]).split(".")[0]:pygame.image.load(image_file_name) for image_file_name in Constant.SKILL_IMAGES}
    print(skill_images.items())
    skills = {}
    debug_print(str(skill_images))
    for image in Constant.VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    player_image = pygame.image.load(Constant.PLAYER_IMAGE)
    monster_image = pygame.image.load(Constant.MONSTER_IMAGE)
    clock = pygame.time.Clock()
    villager_connections = []

    listener = ConnectionListener(villager_connections)
    listener.daemon = True
    listener.start()
    index = 0
    for skill_name, skill_image in skill_images.items():
        # discard the suffix
        skills[skill_name.split(".")[0]] = Skill(skill_name.split(".")[0], skill_image, Constant.SCREEN_WIDTH - (((skill_image.get_rect().size)[0] * Constant.SKILL_IMAGE_SCALE)/2), 50 + index * ((skill_image.get_rect().size)[0] * Constant.SKILL_IMAGE_SCALE), Constant.SKILL_IMAGE_SCALE, applied=False, greyed=False)
        index += 1
    player = Player(player_image, Constant.SAGE_POSITION[0], Constant.SAGE_POSITION[1])
    surface = pygame.Surface((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
    start_game(screen, font, villager_images, monster_image, skills, skill_images, clock, villager_connections, player, surface)
    listener.close_socket()


if __name__ == "__main__":
    main()
