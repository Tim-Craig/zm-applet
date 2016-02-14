import time
from multiprocessing import Process, Queue

from app_events import *
from task import Task

COMMAND_SHUTDOWN = "command_shutdown"

CODE_WORKER_CONTINUE = 0
CODE_WORKER_STOP = 1


class ProcessWorker(object):
    def __init__(self, work_generator_func):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.work_generator_func = work_generator_func
        self.p = Process(target=self.run, args=())
        self.p.daemon = True
        self.p.start()
        self.is_running = True

    def shutdown(self):
        self.input_queue.put_nowait((COMMAND_SHUTDOWN, None))

    def is_alive(self):
        return self.p.is_alive()

    def send_command(self, command, data=None):
        if self.is_running:
            self.input_queue.put_nowait((command, data))

    def get_commands(self):
        return get_commands(self.output_queue)

    def run(self):
        work_generator = self.work_generator_func(self.output_queue)
        work_generator.next()
        while True:
            commands = get_commands(self.input_queue)
            if has_shutdown_command(commands):
                work_generator.close()
                break

            worker_result = work_generator.send(commands)
            if worker_result == CODE_WORKER_STOP:
                self.is_running = False
                break


def get_commands(queue):
    commands = []
    while not queue.empty():
        command = queue.get_nowait()
        commands.append(command)
    return commands


def has_shutdown_command(commands):
    has_command = False
    for command in commands:
        if command[0] == COMMAND_SHUTDOWN:
            has_command = True
    return has_command


def get_last_command(command, commands):
    for x in reversed(xrange(len(commands))):
        if commands[x][0] == command:
            return commands[x]


class ProcessWorkerTask(Task):
    def __init__(self, process_work_generator, watch_dog_check_time=5):
        super(ProcessWorkerTask, self).__init__()
        self.process_worker = ProcessWorker(process_work_generator)
        self.process_work_generator = process_work_generator
        self.last_update_time = time.time();
        self.last_watch_dog_check = 0
        self.watch_dog_check_time = watch_dog_check_time

    def process_event(self, event, data=None):
        super(ProcessWorkerTask, self).process_event(event, data)
        if event in QUIT_APP_EVENTS:
            self.process_worker.shutdown()
            self.alive = False

    def update(self):
        def check_for_watchdog_time():
            cur_time = time.time()
            update_duration = cur_time - self.last_update_time
            self.last_update_time = cur_time
            self.last_watch_dog_check = self.last_watch_dog_check + update_duration

            do_check = False
            if self.last_watch_dog_check >= self.watch_dog_check_time:
                do_check = True
                self.last_watch_dog_check = 0
            return do_check

        super(ProcessWorkerTask, self).update()
        if check_for_watchdog_time():
            if not self.process_worker.is_alive():
                self.process_worker.shutdown()
                self.process_worker = ProcessWorker(self.process_work_generator)
                self._handle_process_recovery()

    def _handle_process_recovery(self):
        pass
