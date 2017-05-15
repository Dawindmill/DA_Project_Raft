import threading
import socket
from debug_print import *
class ConnectionListener(threading.Thread):

    host = Constant.GAME_HOST
    #host = "10.13.248.44"
    port = Constant.GAME_PORT
    nodes = []
    listening = True
    skt = None

    def __init__(self, nodes):
        self.nodes = nodes
        threading.Thread.__init__(self)

    def run(self):
        self.skt = socket.socket()
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skt.bind((self.host, self.port))
        self.skt.listen(5)
        debug_print("Listener started listinging on port " + str(self.port))
        while self.listening:
            villager_connection = self.skt.accept()
            debug_print("connected: ")
            debug_print(villager_connection)
            self.nodes.append(villager_connection)

    def close_socket(self):
        self.skt.close()