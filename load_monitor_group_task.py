import time
from functools import partial

import app_config
import process_worker
from app_events import *
from process_worker import ProcessWorkerTask

WORKER_COMMAND_NEW_MONITOR_GROUP_DATA = 'new_monitor_group_data'
WORKER_COMMAND_ERROR_LOADING_MONITOR_GROUP_DATA = 'error_loading_monitor_data'


def load_monitor_generator(app_context, output_queue):
    load_interval = float(app_context.config.config[app_config.MONTOR_GROUP_LOAD_INTERVAL])
    yield
    while True:
        group_data = None
        monitor_data = None
        while not monitor_data:
            try:
                group_data = app_context.client.get_groups()
                monitor_data = app_context.client.get_monitors()
            except Exception as e:
                group_data = None
                monitor_data = None
                output_queue.put_nowait((WORKER_COMMAND_ERROR_LOADING_MONITOR_GROUP_DATA, e))
                yield process_worker.CODE_WORKER_CONTINUE
                time.sleep(1)
        output_queue.put_nowait((WORKER_COMMAND_NEW_MONITOR_GROUP_DATA, (group_data, monitor_data)))
        yield process_worker.CODE_WORKER_CONTINUE
        time.sleep(load_interval)


class LoadMonitorGroupsTask(ProcessWorkerTask):
    def __init__(self, app_context):
        super(LoadMonitorGroupsTask, self).__init__(partial(load_monitor_generator, app_context))

    def update(self):
        super(LoadMonitorGroupsTask, self).update()
        commands = self.process_worker.get_commands()
        if commands and len(commands) > 0:
            last_command = commands[len(commands) - 1]
            if last_command:
                if last_command[0] == WORKER_COMMAND_NEW_MONITOR_GROUP_DATA:
                    self.event_bus.publish_event(INTERNAL_EVENT_MONITOR_GROUPS_DATA_LOAD, last_command[1])
                elif last_command[0] == WORKER_COMMAND_ERROR_LOADING_MONITOR_GROUP_DATA:
                    self.event_bus.publish_event(INTERNAL_EVENT_MONITOR_GROUPS_DATA_LOAD_ERROR, last_command[1])
