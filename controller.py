from mjpeg_streamer import MjpegStreamer


def get_scale(monitor, display_size):
    x_scale = float(display_size[0]) / float(monitor.width)
    y_scale = float(display_size[1]) / float(monitor.height)
    scale = int(x_scale * 100) if x_scale < y_scale else int(y_scale * 100)
    return scale if scale < 100 else 100


class AppController(object):
    def __init__(self, display, group_tracker, zm_client):
        self.display = display
        self.group_tracker = group_tracker
        self.zm_client = zm_client
        self.current_stream = None
        self.current_monitor_id = None

    def start(self):
        self.current_stream = self._start_stream(self.group_tracker.get_current_monitor())

    def _start_stream(self, monitor):
        scale = get_scale(monitor, self.display.get_display_size())
        stream = self.zm_client.get_monitor_stream(monitor.id, scale)
        self.display.set_stream(MjpegStreamer(stream))
        return stream

    def move_to_prev_monitor_stream(self):
        monitor = self.group_tracker.move_to_prev_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_next_monitor_stream(self):
        monitor = self.group_tracker.move_to_next_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_new_monitor_stream(self, monitor):
        if monitor.id != self.current_monitor_id:
            old_stream = self.current_stream
            self.current_stream = self._start_stream(monitor)
            old_stream.close()

    def update(self):
        self.display.update()
