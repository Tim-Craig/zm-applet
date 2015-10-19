from image_streamer import MessageStreamer, MjpegStreamer, DeadConnectionException


class ZoneminderMonitorStreamer(MjpegStreamer):
    def __init__(self, zoneminder_client, monitor_id, monitor_scale, image_size):
        super(ZoneminderMonitorStreamer, self).__init__()
        self.zoneminder_client = zoneminder_client
        self.image_scale = monitor_scale
        self.monitor_id = monitor_id
        self.set_monitor_stream(monitor_id)
        self.dead_connection_message = MessageStreamer(image_size, "Unable to get video stream.  retrying...")

    def set_monitor_stream(self, monitor_id):
        stream = self.zoneminder_client.get_monitor_stream(monitor_id, self.image_scale)
        self.set_stream(stream)

    def next_frame(self):
        frame = None
        try:
            frame = super(ZoneminderMonitorStreamer, self).next_frame()
        except DeadConnectionException:
            frame = self.dead_connection_message.next_frame()
            try:
                self.set_monitor_stream(self.monitor_id)
            except Exception:
                pass
        return frame
