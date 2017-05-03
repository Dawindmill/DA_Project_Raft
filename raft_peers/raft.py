import time
import _thread
from RaftPeer import *
from RaftPeerState import RaftPeerState
from TimeoutCounter import TimeoutCounter


FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.DEBUG, filename="raft_log_file", filemode="w")
logger = logging.getLogger("RequestVote")
logger.setLevel(logging.DEBUG)

'''
Author: Bingfeng Liu
Date: 16/04/2017
'''

def test_take_user_request_three():
    test_start_time_out_election_three()


def test_start_time_out_election_three():

    peer1 = ("localhost", 1111)
    peer2 = ("localhost", 2222)
    peer3 = ("localhost", 3333)

    peer1_user = 1119
    peer2_user = 2229
    peer3_user = 3339


    peer_addr_port_tuple_list = [peer1, peer2, peer3]

    peer_num = len(peer_addr_port_tuple_list)

    peer1_raft = RaftPeer(peer1[0], peer1[1], peer1_user, "peer1", peer_num)

    peer2_raft = RaftPeer(peer2[0], peer2[1], peer2_user, "peer2", peer_num)

    peer3_raft = RaftPeer(peer3[0], peer3[1], peer3_user, "peer3", peer_num)


    peer_raft_list = [peer1_raft, peer2_raft, peer3_raft]

    for one_peer_raft in peer_raft_list:
        one_peer_raft.connect_to_all_peer(peer_addr_port_tuple_list)

    for one_peer_raft in peer_raft_list:
        one_peer_raft.start_raft_peer()

    time.sleep(10000)



def test_start_time_out_election_five():

    peer1 = ("localhost", 1111)
    peer2 = ("localhost", 2222)
    peer3 = ("localhost", 3333)
    peer4 = ("localhost", 4444)
    peer5 = ("localhost", 5555)

    peer1_user = 1119
    peer2_user = 2229
    peer3_user = 3339
    peer4_user = 4449
    peer5_user = 5559


    peer_addr_port_tuple_list = [peer1, peer2, peer3, peer4, peer5]

    peer_num = len(peer_addr_port_tuple_list)

    peer1_raft = RaftPeer(peer1[0], peer1[1], peer1_user, "peer1", peer_num)

    peer2_raft = RaftPeer(peer2[0], peer2[1], peer2_user, "peer2", peer_num)

    peer3_raft = RaftPeer(peer3[0], peer3[1], peer3_user, "peer3", peer_num)

    peer4_raft = RaftPeer(peer4[0], peer4[1], peer4_user, "peer4", peer_num)
    peer5_raft = RaftPeer(peer5[0], peer5[1], peer5_user, "peer5", peer_num)


    peer_raft_list = [peer1_raft, peer2_raft, peer3_raft, peer4_raft, peer5_raft]

    for one_peer_raft in peer_raft_list:
        one_peer_raft.connect_to_all_peer(peer_addr_port_tuple_list)

    for one_peer_raft in peer_raft_list:
        one_peer_raft.start_raft_peer()

    time.sleep(100)

def test_print_raft_peer_state():
    peer_state = RaftPeerState(("localhost", 1111))
    peer_state.state_log = [123,123,123]
    peer_state.peers_match_index = {"peer1":123, "peer2":123,"peer3":999, "peer4":2222}
    print (str(peer_state))


def test_five_peer_send_recv():
    peer1 = ("localhost", 1111)
    peer2 = ("localhost", 2222)
    peer3 = ("localhost", 3333)
    peer4 = ("localhost", 4444)
    peer5 = ("localhost", 5555)

    peer_addr_port_tuple_list = [peer1, peer2, peer3, peer4, peer5]

    peer1_raft = RaftPeer(peer1[0], peer1[1], "peer1")
    peer2_raft = RaftPeer(peer2[0], peer2[1], "peer2")
    peer3_raft = RaftPeer(peer3[0], peer3[1], "peer3")
    peer4_raft = RaftPeer(peer4[0], peer4[1], "peer4")
    peer5_raft = RaftPeer(peer5[0], peer5[1], "peer5")

    peer_raft_list = [peer1_raft, peer2_raft, peer3_raft, peer4_raft, peer5_raft]

    for one_peer_raft in peer_raft_list:
        one_peer_raft.connect_to_all_peer(peer_addr_port_tuple_list)
    send_json_data = {"send_to": [peer2[0], peer2[1]], "send_from": [peer1[0], peer1[1]], "msg_type": "test"}
    peer1_raft.json_message_send_queue.put(send_json_data)
    time.sleep(100)

def test_five_peer():
    peer1 = ("localhost", 1111)
    peer2 = ("localhost", 2222)
    peer3 = ("localhost", 3333)
    peer4 = ("localhost", 4444)
    peer5 = ("localhost", 5555)

    peer_addr_port_tuple_list = [peer1, peer2, peer3, peer4, peer5]

    peer1_raft = RaftPeer(peer1[0], peer1[1], "peer1")
    peer2_raft = RaftPeer(peer2[0], peer2[1], "peer2")
    peer3_raft = RaftPeer(peer3[0], peer3[1], "peer3")
    peer4_raft = RaftPeer(peer4[0], peer4[1], "peer4")
    peer5_raft = RaftPeer(peer5[0], peer5[1], "peer5")

    peer_raft_list = [peer1_raft, peer2_raft, peer3_raft, peer4_raft, peer5_raft]

    for one_peer_raft in peer_raft_list:
        one_peer_raft.connect_to_all_peer(peer_addr_port_tuple_list)


def test_two_peer():
    test_json_data = {'hello':1}
    peer1_port = 1235
    peer2_port =1236

    peer1 = RaftPeer("localhost", peer1_port, "peer1")

    peer2 = RaftPeer("localhost", peer2_port, "peer2")

    peer2.connect_to_peer(("localhost", peer1_port))

    peer1.accept()


    peer1.connect_to_peer(("localhost", peer2_port))

    peer2.accept()


    peer1.sent_to_all_peer(test_json_data)


    #return_json_data = peer2.receive_from_peer(list(peer2.peers_addr_listen_socket.keys())[0])
    peer2.receive_from_one_peer_newline_delimiter(list(peer2.peers_addr_listen_socket.keys())[0])

    return_json_data = peer2.json_message_recv_queue.get()

    print (str(return_json_data))

    assert test_json_data == return_json_data

    peer1.close()
    peer2.close()


def test_sleep_time():
    lock = _thread.allocate_lock()
    last = time.time()
    time.sleep(0.001)

    with lock:
        gap = time.time() - last
    #gap = time.time() - last

    print(str(gap))

def test_time_counter():
    peer_id = "peer1"
    addr_port_tuple = ("localhost", 1111)
    time_counter = TimeoutCounter(0.1, addr_port_tuple, peer_id)
    #time_counter.time_counter()
    _thread.start_new_thread(time_counter.start_time_counter, ())
    while True:
        print ("="*100 + "main thread")
        time.sleep(1)

    #sleep main thread
    #time.sleep(10)

#test_two_peer()

#test_five_peer()

#test_five_peer_send_recv()

#test_print_raft_peer_state()

#test_sleep_time()

#test_time_counter()
if __name__ == '__main__':
    #test_start_time_out_election_three()
    #test_start_time_out_election_five()
    test_take_user_request_three()
