import time
import logging

class Curing_Active_Alignment(XYscan):
    def __init__(self):
        super().__init__()
        self.minutes = 3
    

    def curing_run(self, P0):
        while True:
            self.fetch_loss()
            start_time = time.time()
            if self.loss[-1] >= self.loss_criteria:
                end_time = time.time()
                if (end_time - start_time) > self.minutes  * 60:
                    logging.info('Reach Time Limit')
                    print('Reach Time Limit')
                    break
                continue
            else:
                pass