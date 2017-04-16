import time
from RaftPeer import *

'''
Author: Bingfeng Liu
Date: 16/04/2017
'''

peer1_port = 1235
peer2_port =1236

peer1 = RaftPeer("localhost", peer1_port)

peer2 = RaftPeer("localhost", peer2_port)

peer2.connect_to_peer("localhost", peer1_port)

peer1.accept()


peer1.connect_to_peer("localhost", peer2_port)

peer2.accept()


peer1.sent_to_all_peer({'hello':1})


test_json_data = peer2.receiv_from_all_peer()


peer1.close()
peer2.close()
