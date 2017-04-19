import logging
FORMAT = '[TimeoutCounter][%(asctime)-15s][%(levelname)s][%(peer_id)s][%(host)s][%(port)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT, level = logging.NOTSET)
logger = logging.getLogger("TimeoutCounter")
logger.setLevel(logging.WARN)

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

    def time_counter(self):
        self.last =time.time()
        while True:
            self.last = time.time()
            time.sleep(self.sleep_time)
            gap = time.time() - self.last
            logger.debug(" gap => " + str(gap), extra = self.my_detial)
            with self.lock:
                #1ms
                self.time_out -= gap
                if self.time_out < 0:
                    #will dead lock if called it inside
                    self.time_out = self.time_out_const
                logger.debug(" time_out left => " + str(self.time_out), extra=self.my_detial)

                    #if self.time_out <= 0:

    def reset_timeout(self):
        with self.lock:
            self.time_out = self.time_out_const