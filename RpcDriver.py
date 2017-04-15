import json
import socket
import logging

logger = logging.getLogger("RpcDriver")
FORMAT = '[%(asctime)-15s][%(levelname)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG)
logging.debug("Hello world")

#this RpcDriver is inspired from http://lesoluzioni.blogspot.com.au/2015/12/python-json-socket-serverclient.html
class RpcDriver:
    backlog = 5
    def __init__(self, host, port):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(self.backlog)
        self.peers_addr_socket = {}


    def connect_to_peer(self):


    def accept(self):
        peer_socket, peer_addr = self.socket.accept()
        self.peers[peer_addr] = peer_socket
        logging.debug(" recv socket from " + str(peer_addr))



    def _check_peer_in(self, peer_addr):
        if peer_addr not in self.peers_addr_socket:
            logging.debug(" " + str(peer_addr) + " not in peers_addr_socket")
            return

    def send_to_peer(self, peer_addr, json_data):
        logging.debug(" sending json_data to " + str(peer_addr))
        self._check_peer_in(peer_addr)
        peer_socket = self.peers_addr_socket[peer_addr]
        try:
            serialized_json_data = json.dumps(json_data)
        except Exception as e:
            logging.debug(" json data serialization failed " + str(json_data))

        peer_socket.sendall("{0}\n".format(len(json_data)))
        peer_socket.sendall(serialized_json_data)

    def receive_from_peer(self, peer_addr):
        logging.debug(" recv json_data from " + str(peer_addr))
        self._check_peer_in(peer_addr)
        peer_socket = self.peers_addr_socket[peer_addr]
        msg_length = ""
        one_byte = peer_socket.recv(1)
        while one_byte != '\n':
            msg_length += one_byte
            one_byte = peer_socket.recv(1)

        msg_length = int(msg_length)
        view = memoryview(bytearray(msg_length))
        next_offset = 0
        while msg_length - next_offset > 0:
            recv_size = peer_socket.recv_into(view[next_offset:], msg_length - next_offset)
            next_offset += recv_size
        try:
            deserialized_json_data = json.loads(view.tobytes())

        except Exception as e:
            logging.debug( " deserialization recv json data failed " + str(e) )

        return deserialized_json_data




