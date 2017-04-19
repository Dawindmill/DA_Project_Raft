import _thread
import time
class TimeoutCounter:
    def __init__(self, time_out):
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
            gap = self.last - time.time()
            with self.lock:
                #1ms
                self.time_out -= gap
                #if self.time_out <= 0:

    def reset_timeout(self):
        with self.lock:
            self.time_out = self.ftime_out_const