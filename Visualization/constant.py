class Constant:
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
    # MESSAGE_IMAGE = "assets/message.png"

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

    MESSAGE_TIME = 5 * FRAME_PER_SECOND

    ONE_DAY = 20 * FRAME_PER_SECOND
    DAY_TIME = ONE_DAY / 4 * 3
    NIGHT_TIME = ONE_DAY / 4

    DEBUG = True

    # day_countdown = ONE_DAY