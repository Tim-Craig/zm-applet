import StringIO


class MjpegStreamer(object):
    def __init__(self, stream):
        self.stream = None
        self.set_stream(stream)

    def set_stream(self, stream):
        self.stream = stream

    def next_frame(self):
        if not self.stream:
            return None
        content_length_line = self.stream.readline()
        while content_length_line[0:15] != 'Content-Length:':
            content_length_line = self.stream.readline()
        count = int(content_length_line[16:])
        img_buffer = self.stream.read(count)
        while img_buffer[0] != chr(0xff):
            img_buffer = img_buffer[1:]

        return StringIO.StringIO(img_buffer)