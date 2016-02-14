import StringIO
import time
from functools import partial

import app_config
import process_worker
import util
from app_events import *
from process_worker import ProcessWorkerTask

COMMAND_SWITCH_TO_MONITOR = "command_switch_to_monitor"
COMMAND_NEW_STREAM_FRAME = "command_new_stream_frame"
COMMAND_STREAM_ERROR_RETRYING = "command_stream_error_retrying"


def get_scale(display_size, monitor):
    x_scale = float(display_size[0]) / float(monitor.width)
    y_scale = float(display_size[1]) / float(monitor.height)
    scale = int(x_scale * 100) if x_scale > y_scale else int(y_scale * 100)
    return scale if scale < 100 else 100


def monitor_generator():
    monitor = None
    commands = []
    while True:
        monitor_switch_command = process_worker.get_last_command(COMMAND_SWITCH_TO_MONITOR, commands)
        if monitor_switch_command and monitor_switch_command[1]:
            monitor = monitor_switch_command[1]
        commands = yield monitor


def stream_generator(app_context, output_queue):
    fps = app_context.config.config[app_config.MAX_FPS]
    open_monitor = None
    open_stream = None
    current_monitor = None
    img_scale = None
    while True:
        if current_monitor != open_monitor:
            open_monitor = current_monitor
            if open_stream:
                util.close_stream_ignore_exception(open_stream)
                open_stream = None
            img_scale = get_scale(app_context.display_size, current_monitor)
        if not open_stream and open_monitor:
            try:
                open_stream = app_context.client.get_monitor_stream(open_monitor.id, fps, img_scale)
            except Exception:
                output_queue.put_nowait((COMMAND_STREAM_ERROR_RETRYING, None))
                time.sleep(.5)
        current_monitor, open_stream = yield open_stream


def monitor_stream_generator(app_context, output_queue):
    stream = None
    commands = []

    monitor_gen = monitor_generator()
    monitor_gen.next()
    stream_gen = stream_generator(app_context, output_queue)
    stream_gen.next()
    while True:
        monitor = monitor_gen.send(commands)
        if monitor:
            stream = stream_gen.send((monitor, stream))
            if stream:
                try:
                    frame = next_frame(stream)
                    output_queue.put_nowait((COMMAND_NEW_STREAM_FRAME, (frame, monitor.id)))
                except Exception:
                    output_queue.put_nowait((COMMAND_STREAM_ERROR_RETRYING, None))
                    util.close_stream_ignore_exception(stream)
                    stream = None
        commands = yield process_worker.CODE_WORKER_CONTINUE


def next_frame(stream):
    def read_line():
        try:
            content = stream.readline()
        except Exception:
            raise DeadConnectionException
        return content

    dead_connection_watch_dog = DeadConnectionWatchDog()
    content_length_line = read_line()
    while content_length_line[0:15] != 'Content-Length:':
        content_length_line = read_line()
        dead_connection_watch_dog.check(content_length_line)
    count = int(content_length_line[16:])
    try:
        img_buffer = stream.read(count)
    except Exception:
        raise DeadConnectionException()
    while len(img_buffer) != 0 and img_buffer[0] != chr(0xff):
        img_buffer = img_buffer[1:]

    return StringIO.StringIO(img_buffer)


class DeadConnectionWatchDog(object):
    def __init__(self, dead_wait_time=10):
        self.dead_wait_time = dead_wait_time
        self.current_dead_wait = 0
        self.last_time = 0

    def check(self, line_read):
        if self.last_time == 0:
            self.last_time = time.time()
        if len(line_read) == 0:
            self.current_dead_wait += time.time() - self.last_time
            if self.current_dead_wait > self.dead_wait_time:
                raise DeadConnectionException()
        else:
            self.current_dead_wait = 0
        self.last_time = time.time()


class DeadConnectionException(Exception):
    pass


class MonitorStreamTask(ProcessWorkerTask):
    def __init__(self, app_context):
        super(MonitorStreamTask, self).__init__(partial(monitor_stream_generator, app_context))
        self.app_context = app_context
        self.current_monitor = None

    def process_event(self, event, data=None):
        if self.is_enabled():
            super(MonitorStreamTask, self).process_event(event, data)
            if event == INTERNAL_EVENT_SWITCH_TO_MONITOR_STREAM:
                self.current_monitor = data
                self.process_worker.send_command(COMMAND_SWITCH_TO_MONITOR, data)

    def update(self):
        super(MonitorStreamTask, self).update()
        commands = self.process_worker.get_commands()
        if len(commands) > 0:
            command = commands[len(commands) - 1]
            if command[0] == COMMAND_NEW_STREAM_FRAME:
                self.event_bus.publish_event(INTERNAL_EVENT_NEW_STREAM_FRAME, command[1])
            elif command[0] == COMMAND_STREAM_ERROR_RETRYING:
                self.event_bus.publish_event(INTERNAL_EVENT_STREAM_ERROR_RETRYING)

    def _handle_process_recovery(self):
        if self.current_monitor:
            self.process_worker.send_command(COMMAND_SWITCH_TO_MONITOR, self.current_monitor)
