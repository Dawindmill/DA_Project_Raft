import logging
FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.NOTSET)
logger = logging.getLogger("TimeoutCounter")
logger.setLevel(logging.DEBUG)

import _thread
import time
class TimeoutCounter:
    #timeout -> in second
    def __init__(self, time_out, owner_addr_port_tuple, peer_id):
        self.my_detial = {"host": str(owner_addr_port_tuple[0]),
                          "port": str(owner_addr_port_tuple[1]),
                          "peer_id": str(peer_id)}
        self.lock = _thread.allocate_lock()
        self.time_out = time_out
        self.time_out_const = time_out
        self.last = 0
        self.sleep_time = 0.001
        # send heat beat in 10 ms
        self.append_entries_heart_beat_time_out = 0.01

    def start_time_out(self, time_out, action_func):
        last = time.time()
        time.sleep(self.sleep_time)
        gap = time.time() - self.last
        # logger.debug(" gap => " + str(gap), extra = self.my_detial)
        with self.lock:
            # 1ms
            time_out -= gap
            if time_out < 0:
                # will dead lock if called it inside
                # self.time_out = self.time_out_const
                logger.debug(" time_out left => " + str(time_out), extra=self.my_detial)
                action_func()
                time_out = self.time_out_const
                # if self.time_out <= 0:

    def start_time_counter(self, raft_peer):
        self.last =time.time()
        while True:
            if raft_peer.raft_peer_state.peer_state == "leader":
                self.start_time_out(self.append_entries_heart_beat_time_out, raft_peer.put_sent_to_all_peer_append_entries_heart_beat)
            else:
                self.start_time_out(self.time_out, raft_peer.put_sent_to_all_peer_request_vote)
    def reset_timeout(self):
        with self.lock:
            self.time_out = self.time_out_const
            logger.debug(" time_out reset => " + str(self.time_out), extra=self.my_detial)
