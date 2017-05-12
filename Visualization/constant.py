import os
class Constant:
    GAME_NAME = "Heritage"

    SCREEN_WIDTH = 1100
    SCREEN_HEIGHT = 800
    FRAME_PER_SECOND = 60

    WHITE = (225, 225, 225)
    BLACK = (0, 0, 0)
    GRAY = (50, 50, 50)
    RED = (225, 0, 0)
    GREEN = (0, 225, 0)
    BLUE = (0, 0, 225)

    ITEM_NAME_SWORD = "sword"
    ITEM_NAME_SWORD_ATTACK_POWER_ADD = 1
    ITEM_NAME_ARMOUR = "armour"
    ITEM_ARMOUR_DEFEND_POWER_ADD = 0.5

    ARMOUR_IMAGE = "./assets/armour.png"
    ARMOUR_IMAGE_SCLAE = 0.1
    SWORD_IMAGE = "./assets/sword.png"
    SWORD_IMAGE_SCALE = 0.25
    VILLAGER_ATTACK_IMAGE= "./assets/villager_attack.png"
    VILLAGER_ATTACK_IMAGE_SCALE = 0.5

    FENCE_IMAGE = "./assets/fence.png"
    FENCE_SCALE = 1.12
    HOUSE_IMAGE = "./assets/house.png"
    HOUSE_DURABILITY = 5
    HOUSE_IMAGE_SCALE = 0.3

    TILE_TYPE_PLANT = "plant"
    TILE_PLANT_IMAGE = "./assets/tiles/grass_tile.png"
    TILE_TYPE_ANIMAL = "animal"
    TILE_ANIMAL_IMAGE = "./assets/tiles/animal_tile.png"

    CHICKEN_EGG_IMAGE = "./assets/plant_animal/egg.png"
    CHICKEN_IMAGE = "./assets/plant_animal/chicken.png"
    CHICHEN_EGG_IMAGE_SCALE = 1
    CHICEN_IAMGE_SCALE = 1
    CHICKEN_MATURE_COUNT_DOWN = 100
    ANIMAL_HEALTH_INCREASE = 1


    TREE_IMAGE = "./assets/plant_animal/tree.png"
    TREE_WITH_APPLE_IMAGE = "./assets/plant_animal/tree_with_apple.png"
    TREE_IMAGE_SCALE = 0.3
    TREE_WITH_APPLE_IMAGE_SCALE = 0.3
    TREE_MATURE_COUNT_DOWN = 60
    PLANT_HEALTH_INCREASE = 0.5

    TILE_IMAGE_SCALE = 0.3

    LAND_SIZE = 4

    SKILL_IMAGES = ['./assets/skill_icons/using/'+str(f) for f in os.listdir('./assets/skill_icons/using') if f.endswith('.png')]
    VILLAGER_IMAGES = ["assets/villager_m.png", "assets/villager_f.png"]
    VILLAGER_MAX_HP = 2.0
    MONSTER_IMAGE = "assets/monster.png"
    # MONSTER_ATTACK_POWER = 0.5
    MONSTER_ATTACK_POWER = 2
    MONSTER_ATTACK_IMAGE = "assets/monster_attack.png"
    MONSTER_ATTACK_IMAGE_SCALE = 1
    ATTACK_DISPLAY_COUNT_DOWN = 20
    MONSTER_ATTACK_FREQUENT = 10
    MONSTER_MAX_HP = 5.0


    PLAYER_IMAGE = "assets/sage.png"

    SKILL_IMAGE_SCALE = 0.2
    SKILL_IMAGE_SCALE_VILLAGER = 0.05
    # MESSAGE_IMAGE = "assets/message.png"

    # y increase move down, x increase move right
    VILLAGER_POSITIONS = [(200, 200), (350, 200), (500, 200), (650, 200), (800, 200), (950, 200),
                          (950, 500), (800, 500), (650, 500), (500, 500), (350, 500), (200, 500)]
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

    MESSAGE_TIME = 5 * FRAME_PER_SECOND

    ONE_DAY = 20 * FRAME_PER_SECOND
    # ONE_DAY = 70
    DAY_TIME = ONE_DAY / 4 * 3
    NIGHT_TIME = ONE_DAY / 4
    # NIGHT_TIME = 70

    DEBUG = True

    HEAL_BAR_HEIGHT = 5

    MONSTER = "monster"
    VILLAGER = "villager"

    ATTACK = "attack"
    GIVE_BIRTH = "give_birth"
    NOTHING = "nothing"

    EVENTS = {MONSTER: [ATTACK],#, NOTHING],
              VILLAGER: [GIVE_BIRTH, NOTHING]}