import sys
from configparser import ConfigParser
import logging
from RaftPeer import RaftPeer
import time

import argparse

if __name__ == '__main__':
    config_parser = ConfigParser()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("peer_name", help="peer name of the current process",
                            type=str)

    arg_parser.add_argument("peer_num", help="total peer number in this Raft",
                            type=int)

    arg_parser.add_argument("-v", "--visualization", help="connecting to the visualization game server",
                    action="store_true")
    command_line_args = arg_parser.parse_args()

    # if len(sys.argv) != 3:
    #     sys.exit("Raft needs host ip, peer name and total number of peers, please follow the peer names in  raft_peer.ini file.")


    # cur_peer_name = sys.argv[1]
    cur_peer_name = command_line_args.peer_name
    # total_peer_num = int(sys.argv[2])
    total_peer_num = command_line_args.peer_num

    try:
        config_parser.read("raft_peer.ini")
    except Exception as e:
        sys.exit(str(e) + " must have raft_peer.ini file")

    try:

        host_ip = config_parser[cur_peer_name]["raft_peer_host_ip"]

        # passively listen to other peer's connection
        listen_port = int(config_parser[cur_peer_name]["raft_peer_listen_port"])

        # port use to listen connection from user.py
        user_listen_port = int(config_parser[cur_peer_name]["raft_peer_user_listen_port"])
    except Exception as e:
        sys.exit(str(e) + " Please check the format of raft_peer.ini file, it should contain raft_peer_listen_port and raft_peer_client_port")

    FORMAT = '[%(module)s][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename= ("logs/" + cur_peer_name+"_raft_log_file"), filemode="w")

    print ("host_ip => " + host_ip)
    peer1_raft = RaftPeer(host_ip, listen_port, user_listen_port, cur_peer_name, total_peer_num)

    peer_addr_port_tuple_list = []

    # gather other peer's listen port, assume launching peer is in order from peer1 -> peer12
    for i in range(total_peer_num):
        other_peer_host_ip = config_parser["peer"+str(i + 1)]["raft_peer_host_ip"]
        other_peer_listen_port = int(config_parser["peer"+str(i + 1)]["raft_peer_listen_port"])
        peer_addr_port_tuple_list.append((other_peer_host_ip, other_peer_listen_port))

    if command_line_args.visualization:
        try:
            visual_host_ip = config_parser["visualization"]["visualization_host_ip"]
            visual_host_port = config_parser["visualization"]["visualization_listen_port"]
        except Exception as e:
            print ("visualization visualization_host_ip/visualization_listen_port not present")
        peer1_raft.start_visualization_connection_thread(str(visual_host_ip), int(visual_host_port))
        time.sleep(1)
    peer1_raft.start_connect_to_all_peer_thread(peer_addr_port_tuple_list)
    peer1_raft.start_raft_peer()

    while True:
        time.sleep(60)

    sys.exit(str(e) + " Something is wrong ")


