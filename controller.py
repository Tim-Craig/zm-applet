from mjpeg_streamer import MjpegStreamer


class AppController(object):
    def __init__(self, display, group_tracker, zm_client):
        self.display = display
        self.group_tracker = group_tracker
        self.zm_client = zm_client
        self.current_stream = None
        self.current_monitor_id = None

    def start(self):
        self.current_stream = self._start_stream(self.group_tracker.get_current_monitor().id)

    def _start_stream(self, monitor_id):
        stream = self.zm_client.get_monitor_stream(monitor_id)
        self.display.set_stream(MjpegStreamer(stream))
        return stream

    def move_to_prev_monitor_stream(self):
        monitor = self.group_tracker.move_to_prev_monitor()
        self.move_to_new_monitor_stream(monitor.id)

    def move_to_next_monitor_stream(self):
        monitor = self.group_tracker.move_to_next_monitor()
        self.move_to_new_monitor_stream(monitor.id)

    def move_to_new_monitor_stream(self, monitor_id):
        if monitor_id != self.current_monitor_id:
            old_stream = self.current_stream
            self.current_stream = self._start_stream(monitor_id)
            old_stream.close()

    def update(self):
        self.display.update()
