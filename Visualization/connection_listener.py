import threading
import socket
from debug_print import *
class ConnectionListener(threading.Thread):

    host = "192.168.1.104"
    #host = "10.13.225.187"
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
            self.nodes.append(villager_connection)

    def close_socket(self):
        self.skt.close()