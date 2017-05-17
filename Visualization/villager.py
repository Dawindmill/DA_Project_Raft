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
from attack import AttackAnimation
from house import House
from item import Item
from constant_image import ConstantImage
import random


class Villager(Image, threading.Thread):

    lock = threading.RLock()
    # for testing purpose only want to create one leader
    leader_taken = False
    

    def __init__(self, image, position, villager_id, font, listener, current_leader, skill_images):
        self.role = Role.FOLLOWER
        self.listener = listener
        self.current_leader = current_leader
        self.leadership_term = 0
        # render shouting
        self.message_count = 1
        # for testing to only create one leader
        self.skills = []
        self.skill_adding_list = []
        self.max_health = Constant.VILLAGER_MAX_HP
        self.current_health = self.max_health
        self.current_message = ""
        self.message_countdown = 0
        self.learned_skill_names = []
        self.turning_learned_skills_list = []
        self.dead = False
        self.dead_message_sent = False
        width, height = image.get_rect().size
        center_x, center_y = position
        super().__init__(image, center_x, center_y, height, width)
        self.villager_id = villager_id
        self.font = font
        self.attacked = False
        self.item = []
        self.attack = None


        self.land = Land(self, Constant.LAND_SIZE)

        self.house = None
        self.build_house_countdown = Constant.BUILD_HOUSE_COUNT_DOWN

        threading.Thread.__init__(self)

        self.attack_probability = 0.5
        self.attack_display_count_down = Constant.ATTACK_DISPLAY_COUNT_DOWN
        self.attack_display_count_down_const = Constant.ATTACK_DISPLAY_COUNT_DOWN
        self.attacked = False
        self.attack_power = 1

        self.skill_images = skill_images


    def pickTile(self, tile):
        """
        
        Check which tile is clicked by mouse, and applied its benefits to Villager
        
        :param tile: Tile 
        :return: 
        """
        if tile.mature:
            if tile.tile_type == Constant.TILE_TYPE_PLANT:
                self.current_health_up_with_amount(Constant.PLANT_HEALTH_INCREASE)
            elif tile.tile_type == Constant.TILE_TYPE_ANIMAL:
                self.current_health_up_with_amount(Constant.ANIMAL_HEALTH_INCREASE)
            tile.un_mature()

    def addHouse(self):
        """
        
        Add a house Object to Villager
         
        """
        self.house = House(self.x, self.y)

    # armour
    def addItemToLeftHand(self, image, item_name, image_scale):
        """
        
        Adding a item to the left hand side of the villager
        
        :param image: Image 
        :param item_name:  str
        :param image_scale: int
        :return: 
        """
        width, height = image.get_rect().size
        temp_item_center_x = self.x + width * image_scale // 2
        temp_item_center_y = self.y + width * image_scale
        temp_item = Item(image, temp_item_center_x, temp_item_center_y, item_name, image_scale)
        self.item.append(temp_item)

    # sword
    def addItemToRightHand(self, image, item_name, image_scale):
        """

        Adding a item to the right hand side of the villager

        :param image: Image 
        :param item_name:  str
        :param image_scale: int
        :return: 
        """
        width, height = image.get_rect().size
        temp_item_center_x = self.x - width * image_scale
        temp_item_center_y = self.y
        temp_item = Item(image, temp_item_center_x, temp_item_center_y, item_name, image_scale)
        self.item.append(temp_item)

    def being_attacked(self, hp_decrement):
        """
        
        if villager is attcked set the hp down
        
        :param hp_decrement: int
        
        """
        self.current_health_down_with_amount(hp_decrement)



    def add_skill(self, skill_name):
        """
        
        Add skill Object to player's skill list
        
        :param skill_name: str 
         
        """
        skill_num = len(self.skills)
        image = self.skill_images[skill_name]

        # each row render four skill, then go up
        one_skill = Skill(skill_name, image, self.x - self.width/2 - ((image.get_rect().size)[0] * Constant.SKILL_IMAGE_SCALE_VILLAGER) / 2, (self.y + self.height/2) - (int (skill_num) * int((image.get_rect().size)[1] * Constant.SKILL_IMAGE_SCALE_VILLAGER)), Constant.SKILL_IMAGE_SCALE_VILLAGER, False)
        self.skills.append(one_skill)


    def run(self):
        while (not self.dead) and (not self.listener.stopped):
            # consuming the parsed JSON message from the queue
            request = self.listener.request_queue.get()

            request_type = request[Constant.MESSAGE_TYPE]
            # according to the type of the request applying corresponding methods to villager
            if request_type == Constant.VILLAGER_DEAD:
                self.dead = True
                continue
            if request_type == Constant.APPEND and self.role == Role.LEADER:
                if not request[Constant.NEW_ENTRIES]:
                    self.reclaim_authority()
            elif request_type == Constant.LEADERSHIP:
                self.set_leadership(request)
            elif request_type == Constant.REQUEST_VOTE:
                self.set_candidate(request)
            elif request_type == Constant.REQUEST_VOTE_REPLY:
                self.vote(request)
            elif request_type == Constant.REQUEST_COMMAND_ACK and self.role == Role.LEADER:
                self.leader_receive_learn(request)
            elif request_type == Constant.APPEND_REPLY:
                self.learning_skill(request)
            elif request_type == Constant.COMMIT_INDEX:
                self.learned_skill(request)
            if self.current_health == 0:
                debug_print("Villager" + str(self.villager_id) + " is dead")
                self.dead = True

        if self.listener.stopped:
            print(str(self.villager_id) + "'s listener is dead")
            self.dead = True
        if self.dead:
            # if dead send the JSON to cooresponding remote Raft peer to ask it to terminate
            data = {Constant.MESSAGE_TYPE: "villager_killed", Constant.PEER_ID: self.listener.peer_id}
            try:
                self.listener.socket.sendall(str.encode(json.dumps(data) + "\n"))
                print("villager killed message sent")
            except ConnectionResetError:
                print("connection dead")
            print("villager killed message sent")
            self.listener.stop_listener()
            self.dead_message_sent = True


    def reclaim_authority(self):
        """
        Display a dialgue box to show the string 'I'm the leader'
        
        """
        self.set_message(Constant.AUTHORITY_MESSAGE)

    def set_leadership(self, request):
        """
        
        trying to set the leader by this leadership request dictionary
        
        :param request: dict
        """
        term = request[Constant.SENDER_TERM]
        # if there is still a leader and the term number of JSON messag is smaller than
        # current term ignore this outdated leader messge
        if self.current_leader and self.current_leader.leadership_term > term:
            return
        self.role = Role.LEADER
        self.leadership_term = term
        self.set_message(Constant.NEW_LEADER_MESSAGE)

    def set_candidate(self, request):
        """
        
        set villager to candidate by this request_vote request
        
        :param request: dict
        """
        term = request[Constant.SENDER_TERM]
        # abort the outdated request_vote message
        if self.current_leader and self.current_leader.leadership_term > term:
            return
        self.role = Role.CANDIDATE
        self.set_message(Constant.CANDIDATE_MESSAGE)

    def vote(self, request):
        term = request[Constant.SENDER_TERM]
        if self.current_leader and self.current_leader.leadership_term > term:
            return
        vote_for = request[Constant.VOTE_PEER_ID][4:]
        debug_print(type(request[Constant.VOTE_GRANTED]))
        if request[Constant.VOTE_GRANTED] == True:
            self.set_message(Constant.VOTE_MESSAGE.format(vote_for))

    def leader_receive_learn(self, request):
        skill_name = request[Constant.REQUEST_COMMAND_LIST][0]
        index = int(request[Constant.INDEX])
        if index == len(self.skills):
            self.add_skill(skill_name)
            while self.skill_adding_list:
                length = len(self.skills)
                if self.skill_adding_list[0][0] == length:
                    skill = self.skill_adding_list.pop(0)
                    self.add_skill(skill[1])
                else:
                    break
        elif index > len(self.skills):
            self.skill_adding_list.append((index, skill_name))
            self.skill_adding_list.sort()

    def learning_skill(self, request):
        result = request[Constant.APPEND_RESULT]
        if result and self.current_leader:
            index = int(request[Constant.LAST_LOG_INDEX])
            if (index >= len(self.skills)) and (index < len(self.current_leader.skills)):
                for i in range(len(self.skills), index + 1):
                    self.add_skill(self.current_leader.skills[i].skill_name)

    def learned_skill(self, request):
        debug_print("in learned_skill")
        if not request:
            while self.turning_learned_skills_list and self.turning_learned_skills_list[0][0] == len(
                    self.learned_skill_names):

                skill = self.turning_learned_skills_list.pop(0)
                self.learned_skill(skill[1])
            return
        index = int(request[Constant.INDEX])
        debug_print("index is" + str(index))
        debug_print("skills: ")
        debug_print(self.skills)

        if (index < len(self.skills)) and (index == len(self.learned_skill_names)):
            skill_name = self.skills[index].skill_name
            debug_print("skill name: " + skill_name)
        else:
            while self.turning_learned_skills_list and self.turning_learned_skills_list[0][0] == len(self.learned_skill_names):
                skill = self.turning_learned_skills_list.pop(0)
                self.learned_skill(skill[1])
            self.turning_learned_skills_list.append((index, request))
            self.turning_learned_skills_list.sort()
            debug_print("returned in else")
            return
        if skill_name not in Constant.SKILLS:
            debug_print("not in skills")
            return
        if skill_name == Constant.ARMOUR:
            self.addItemToLeftHand(ConstantImage.ARMOUR_IMAGE_SPRITE,Constant.ITEM_NAME_ARMOUR ,Constant.ARMOUR_IMAGE_SCLAE)
        elif skill_name == Constant.SWORD:
            self.addItemToRightHand(ConstantImage.SWORD_IMAGE_SPRITE, Constant.ITEM_NAME_SWORD, Constant.SWORD_IMAGE_SCALE)
        elif skill_name == Constant.ANIMAL:
            for tile in self.land.tiles:
                if tile.tile_type == Constant.TILE_TYPE_ANIMAL:
                    tile.display_plant_or_animal = True
        elif skill_name == Constant.PLANT:
            for tile in self.land.tiles:
                if tile.tile_type == Constant.TILE_TYPE_PLANT:
                    tile.display_plant_or_animal = True
        elif skill_name == Constant.HOUSE:
            self.addHouse()
        self.skills[index].greyed = False
        self.skills[index].applied = True
        debug_print("set skill greyed false")
        self.learned_skill_names.append(skill_name)

    def set_message(self, message):
        self.current_message = message
        self.message_countdown = Constant.MESSAGE_TIME


    def max_health_up(self):
        self.max_health += 1

    def max_health_down(self):
        self.max_health -= 1

    def current_health_up(self):
        self.current_health += 1

    def current_health_down(self):
        self.current_health -= 1


    def current_health_up_with_amount(self, hp_increment):
        self.current_health += hp_increment
        if self.current_health > self.max_health:
            self.current_health = self.max_health


    def attack_monster_or_not(self, monster):

        if (Constant.SWORD not in self.learned_skill_names) or self.attacked or \
                (Constant.SWORD in self.learned_skill_names):
            return

        self.attacked = random.random() >= self.attack_probability

        if self.attacked and self.attack_power > 0 :
            monster.set_attack(self.attack_power)
            self.attack = AttackAnimation(ConstantImage.VILLAGER_ATTACK_IMAGE_SPRITE, monster.x, monster.y, Constant.VILLAGER_ATTACK_IMAGE_SCALE)
            self.attack_display_count_down = self.attack_display_count_down_const

        else:
            self.attacked = False


    def current_health_down_with_amount(self, hp_decrement):

        if self.house is not None and self.house.display_house:
            self.house.house_durability_decrement_with_amount(hp_decrement)
            if self.house.current_durability <= 0:
                self.house.display_house = False
            return

        if Constant.ARMOUR in self.learned_skill_names:
            hp_decrement -= Constant.ITEM_ARMOUR_DEFEND_POWER_ADD

        if hp_decrement >= self.current_health:
            self.current_health = 0
            self.dead = True
            return
        self.current_health -= hp_decrement

    def build_house(self):
        if self.house:
            if not self.house.display_house:
                if self.build_house_countdown == Constant.BUILD_HOUSE_COUNT_DOWN:
                    self.set_message(Constant.BUILD_HOUSE_MESSAGE)
                    self.build_house_countdown -= 1
                elif self.build_house_countdown > 0:
                    self.build_house_countdown -= 1
                else:
                    self.house.display_house = True
                    self.build_house_countdown = Constant.BUILD_HOUSE_COUNT_DOWN

    def render_attack(self, screen):
        if self.attacked and self.attack_display_count_down != 0:
            self.attack.render(screen)
            self.attack_display_count_down -= 1
            if self.attack_display_count_down <= 0:
                self.attacked = False

    def render(self, screen):

        if self.house and self.house.display_house:
            self.house.render(screen)

        super().render(screen)

        for one_skill in self.skills:
            one_skill.render(screen)

        self.land.render(screen)
        name = self.font.render("Villager " + str(self.villager_id), 1, Constant.BLACK)
        screen.blit(name, (self.x - name.get_width() // 2, self.y + self.height // 2))

        if self.role != Role.FOLLOWER:
            if self.role == Role.LEADER:
                title = "Leader"
                role = self.font.render(title, 1, Constant.BLACK)
                screen.blit(role, (self.x - role.get_width() // 2, self.y + self.height // 2 + role.get_height() + 2))

        if self.message_countdown > 0:
            message = self.font.render(self.current_message, 1, Constant.BLACK)
            screen.blit(message, (self.x - message.get_width() // 2, self.y - self.height // 2 - message.get_height() - 2))
            self.message_countdown -= 1

        pygame.draw.rect(screen, Constant.GRAY, pygame.Rect((self.x - self.width // 2,
                                                    self.y - self.height // 2),
                                                   (self.width, Constant.HEAL_BAR_HEIGHT)))
        pygame.draw.rect(screen, Constant.RED, pygame.Rect((self.x - self.width // 2,
                                                   self.y - self.height // 2),
                                                  (self.width * (self.current_health / self.max_health),
                                                   Constant.HEAL_BAR_HEIGHT)))

        for one_item in self.item:
            one_item.render(screen)

