import time
from RaftPeer import *

'''
Author: Bingfeng Liu
Date: 16/04/2017
'''

def test_two_peer():
    test_json_data = {'hello':1}
    peer1_port = 1235
    peer2_port =1236

    peer1 = RaftPeer("localhost", peer1_port)

    peer2 = RaftPeer("localhost", peer2_port)

    peer2.connect_to_peer("localhost", peer1_port)

    peer1.accept()


    peer1.connect_to_peer("localhost", peer2_port)

    peer2.accept()


    peer1.sent_to_all_peer(test_json_data)


    #return_json_data = peer2.receive_from_peer(list(peer2.peers_addr_listen_socket.keys())[0])
    peer2.receive_from_one_peer_newline_delimiter(list(peer2.peers_addr_listen_socket.keys())[0])

    return_json_data = peer2.json_message_queue.get()

    print (str(return_json_data))

    assert test_json_data == return_json_data

    peer1.close()
    peer2.close()

test_two_peer()


