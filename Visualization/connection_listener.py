import threading
import socket
from debug_print import *
class ConnectionListener(threading.Thread):



    def __init__(self, nodes):
        self.host = Constant.GAME_HOST
        self.port = Constant.GAME_PORT
        self.skt = None
        self.listening = True
        self.nodes = nodes
        threading.Thread.__init__(self)
        self.backlog = 5

    def run(self):
        """
        This method will act like accept method to listen for incoming connections
        from Raft peers
        """
        self.skt = socket.socket()
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skt.bind((self.host, self.port))
        self.skt.listen(self.backlog)
        debug_print("Listener started listinging on port " + str(self.port))
        while self.listening:
            villager_connection = self.skt.accept()
            debug_print("connected: ")
            debug_print(villager_connection)
            self.nodes.append(villager_connection)

    def close_socket(self):
        self.skt.close()