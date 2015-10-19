import time


class TimeTracker(object):
    def __init__(self, track_time):
        self.track_time = track_time
        self.start_time = time.time()

    def passed(self):
        return (time.time() - self.start_time) > self.track_time
