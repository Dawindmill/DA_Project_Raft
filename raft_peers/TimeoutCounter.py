import logging

logger = logging.getLogger("TimeoutCounter")
logger.setLevel(logging.DEBUG)

import _thread
import time
import threading
class TimeoutCounter:
    #timeout -> in second
    def __init__(self, time_out, owner_addr_port_tuple, peer_id):
        self.my_detial = {"host": str(owner_addr_port_tuple[0]),
                          "port": str(owner_addr_port_tuple[1]),
                          "peer_id": str(peer_id)}
        self.lock = threading.RLock()
        self.time_out = time_out
        self.time_out_const = time_out
        self.last = 0
        self.sleep_time = 0.001
        # send heat beat in 10 ms
        self.append_entries_heart_beat_time_out = 0.01

    def start_time_out(self, time_out, action_func):

        # logger.debug(" gap => " + str(gap), extra = self.my_detial)
        with self.lock:
            # 1ms
            last = time.time()
            time.sleep(self.sleep_time)
            gap = time.time() - last
            self.time_out -= gap

            if self.time_out <= 0:
                self.time_out = time_out
                # will dead lock if called it inside
                # self.time_out = self.time_out_const
                logger.debug(" time_out ", extra=self.my_detial)
                action_func()
                # if self.time_out <= 0:

    def start_time_counter(self, raft_peer):
        logger.debug(" counter started ", extra=self.my_detial)
        while True:
            if raft_peer.raft_peer_state.peer_state == "leader":
                self.start_time_out(self.append_entries_heart_beat_time_out, raft_peer.put_sent_to_all_peer_append_entries_heart_beat)
            else:
                self.start_time_out(self.time_out_const, raft_peer.put_sent_to_all_peer_request_vote)

    def reset_timeout(self):
        with self.lock:
            self.time_out = self.time_out_const
            logger.debug(" time_out reset => " + str(self.time_out), extra=self.my_detial)
