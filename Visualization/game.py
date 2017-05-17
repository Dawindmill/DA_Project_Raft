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
    # day_countdown is to simulate the day time and evening time in the game.
    global day_countdown

    villager_count = 0
    # villagers' collection
    villagers = []
    # monsters' collection
    monsters = []

    # init two monsters
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[0][0], Constant.MONSTER_POSITIONS[0][1]))
    monsters.append(Monster(monster_image, Constant.MONSTER_POSITIONS[1][0], Constant.MONSTER_POSITIONS[1][1]))


    global done
    done = False

    listener_list = []
    existing_peer_ids = []
    alive_villagers_list = []
    current_leader = None
    stop_night_event = False
    while not done:
        # if there is some peer connected the game server
        while villagers_connections and villager_count < len(Constant.VILLAGER_POSITIONS):
            # get the socket and information of the peer
            node_socket, information = villagers_connections.pop(0)

            # create peer's listener and later use to receive message to render
            # corresponding game logcs for associated villager
            listener = VillagerListener(node_socket)

            listener_list.append(listener)
            listener.daemon = True
            listener.start()

            debug_print("listener list: ")
            debug_print(listener_list)

        # if there is villager listener in the listener_list
        # which means we haven't create the Villager object to render the graphics
        for listener in listener_list:
            if len(alive_villagers_list) < len(Constant.VILLAGER_POSITIONS):
                if listener.info_set:
                    debug_print("info set")
                    listener_list.remove(listener)
                    if listener.peer_id not in existing_peer_ids:
                        # keep track of peers in the visualization
                        existing_peer_ids.append(listener.peer_id)
                        # randomly make it female or male villager
                        gender = random.randint(0, 10) % 2
                        villager_id = int(listener.peer_id[4:])
                        # we can only create up to the max pos of villagers in the constant.py
                        if len(villagers) < len(Constant.VILLAGER_POSITIONS):
                            position = Constant.VILLAGER_POSITIONS[len(villagers)]
                            villager = Villager(villager_images[gender], position,
                                                villager_id, font, listener, current_leader, skill_images)
                            villagers.append(villager)
                        else:
                            # if the max nmber of villagers are reached
                            # we needt check which villager is none and create new Villager object for it
                            for i in range(len(villagers)):
                                if not villagers[i]:
                                    position = Constant.VILLAGER_POSITIONS[i]
                                    villager = Villager(villager_images[gender], position,
                                                        villager_id, font, listener, current_leader, skill_images)
                                    villagers[i] = villager
                                    break
                        alive_villagers_list.append(villager)

                        villager.daemon = True
                        villager.start()
                        villager_count += 1
                        debug_print(villagers)
            else:
                break

        # reset the game graphics
        screen.fill(Constant.WHITE)

        for villager_index in range(len(villagers)):
            villager = villagers[villager_index]
            if villager:
                # alive villager render the graph, and trying to build house if skill learnt
                if not villager.dead:
                    villager.render(screen)
                    villager.build_house()
                    # remove the transparency of learnt skill icon
                    if villager.turning_learned_skills_list:
                        villager.learned_skill(None)

                        for one_skill_from_villager in villager.skills:
                            one_skill_from_villager.skill_handler(villager, villagers, monsters, player)
                        villager.render_attack(screen)
                elif villager.dead_message_sent:
                    # if village dead send RPC to kill the remote peer
                    alive_villagers_list.remove(villager)
                    existing_peer_ids.remove(villager.listener.peer_id)
                    villagers[villager_index] = None
                    villager_count -= 1

        # find leader
        new_leader = player.find_leader(villagers)
        player.render(screen)
        # checking the leadership changes
        if new_leader != current_leader:
            current_leader = new_leader
            for villager in villagers:
                if villager:
                    villager.current_leader = new_leader
        # rendering monster
        for one_monster in monsters:
            if not one_monster.dead:
                one_monster.render(screen)
        # if the skilled learnt, make the skill button transparent
        for one_skill in skills.values():
            greyed = False
            if current_leader:
                for l_skill in current_leader.skills:
                    if one_skill.skill_name == l_skill.skill_name:
                        greyed = True
                        break
            one_skill.greyed = greyed
            one_skill.render(screen)

        # if day count is less than 0 means we should reset it to day time
        if day_countdown <= 0:
            day_countdown = Constant.ONE_DAY
        # when day_countdown less than NIGHT_TIME threshold, start to rendering night events
        elif day_countdown <= Constant.NIGHT_TIME:
            for monster in monsters:
                if not monster.dead:
                    if day_countdown == Constant.NIGHT_TIME:
                        monster.night_event.stop = stop_night_event
                        monster.night_event.perform_event(alive_villagers_list)

                    monster.night_event.render_event(screen)

        # add a transparent black layers to simulate night effect
            # inspired from http://stackoverflow.com/questions/6339057/draw-a-transparent-rectangle-in-pygame
            s.set_alpha(200)  # alpha level
            s.fill(Constant.BLACK)  # this fills the entire surface
            screen.blit(s, (0, 0))  # (0,0) are the top-left coordinates


        day_countdown -= 1

        for event in pygame.event.get():
            # check the events in the game like mouseclick and quite button clicked
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
                clicked_skills = [(skill_name, one_skill) for skill_name, one_skill in skills.items() if one_skill.image_rect.collidepoint(pos)]
                clicked_villager_tiles_tuple = []
                # click the villager to kill it instantly
                for one_villager in villagers:
                    if not one_villager:
                        continue
                    if one_villager.image_rect.collidepoint(pos):
                        one_villager.dead = True
                        print("villager dead")
                    temp_tiles = []
                    for one_tile in one_villager.land.tiles:
                        if one_tile.image_rect.collidepoint(pos):
                            temp_tiles.append(one_tile)
                    clicked_villager_tiles_tuple.append((one_villager, temp_tiles))
                if len(clicked_skills) > 0:
                    # check which skill button is clicked
                    skill = clicked_skills[0][1]
                    if (not skill.applied) and (not skill.greyed):
                        applied = player.passing_down_skill(clicked_skills[0][1], alive_villagers_list)
                        if applied:
                            skill.greyed = True

                if len(clicked_villager_tiles_tuple) > 0:
                    for one_villager, one_tile_list in clicked_villager_tiles_tuple:
                        for one_tile in one_tile_list:
                            one_villager.pickTile(one_tile)
            # press key 's' could stop monster's attck
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if stop_night_event:
                    stop_night_event = False
                else:
                    stop_night_event = True

        pygame.display.flip()
        clock.tick(Constant.FRAME_PER_SECOND)
    pygame.quit()


def main():
    # print ("start")
    pygame.init()
    # print("start init")
    pygame.display.set_caption(Constant.GAME_NAME)
    # print("start caption")
    font = pygame.font.Font(Constant.FONT_NAME, Constant.FONT_SIZE)
    # print("start font")
    screen = pygame.display.set_mode((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
    screen.fill(Constant.WHITE)
    villager_images = []

    # load all skill images group them with image name and image object
    skill_images = {(image_file_name.split("/")[-1]).split(".")[0]:pygame.image.load(image_file_name) for image_file_name in Constant.SKILL_IMAGES}
    # print(skill_images.items())
    skills = {}
    debug_print(str(skill_images))
    # load all villager's image, girl and boy
    for image in Constant.VILLAGER_IMAGES:
        villager_images.append(pygame.image.load(image))
    # load player's image
    player_image = pygame.image.load(Constant.PLAYER_IMAGE)
    # load monster's image
    monster_image = pygame.image.load(Constant.MONSTER_IMAGE)
    # set the clock in pygame, so later on we could adjust the Frame Rate Per Second
    clock = pygame.time.Clock()
    # each villager is is a thread to consuming their own JSON data
    villager_connections = []
    # start visualization listening socket
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
