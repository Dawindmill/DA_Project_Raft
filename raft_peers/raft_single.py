import sys
from configparser import ConfigParser
import logging
from RaftPeer import RaftPeer
import time


if __name__ == '__main__':
    parser = ConfigParser()

    if len(sys.argv) != 4:
        sys.exit("Raft needs host ip, peer name and total number of peers, please follow the peer names in  raft_peer.ini file.")

    host_ip = sys.argv[1]
    cur_peer_name = sys.argv[2]
    total_peer_num = int(sys.argv[3])

    try:
        parser.read("raft_peer.ini")
    except Exception as e:
        sys.exit(str(e) + " must have raft_peer.ini file")

    try:
        # passively listen to other peer's connection
        listen_port = int(parser[cur_peer_name]["raft_peer_listen_port"])

        # port use to establish initiative connection to other peers
        client_port = int(parser[cur_peer_name]["raft_peer_client_port"])
    except Exception as e:
        sys.exit(str(e) + " Please check the format of raft_peer.ini file, it should contain raft_peer_listen_port and raft_peer_client_port")

    FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename= ("logs/" + cur_peer_name+"_raft_log_file"), filemode="w")

    peer1_raft = RaftPeer(host_ip, listen_port, client_port, cur_peer_name, total_peer_num)

    while True:
        time.sleep(60)

    sys.exit(str(e) + " Something is wrong ")


