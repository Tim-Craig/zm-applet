from input_handler import InputHandler
import RPi.GPIO as GPIO
import os

class DelayTracker(object):
    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.remaining_time = 0

    def trigger(self):
        self.remaining_time = self.delay_time

    def is_delayed(self):
        print self.remaining_time > 0
        return self.remaining_time > 0

    def update(self, elapsed_time):
        self.remaining_time -= elapsed_time
        if self.remaining_time < 0:
            self.remaining_time = 0


class PiInputHandler(InputHandler):
    def __init__(self, controller):
            super(self.__class__, self).__init__(controller)
            self.move_left_delay = DelayTracker(.5)
            self.move_right_delay = DelayTracker(.5)

            GPIO.setmode(GPIO.BCM)

            GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def check_input_commands(self, elapsed_time):
        self.move_left_delay.update(elapsed_time)
        self.move_right_delay.update(elapsed_time)

        if not GPIO.input(23) and not self.move_left_delay.is_delayed():
            self.controller.move_to_prev_monitor_stream()
            self.move_left_delay.trigger()
        elif not GPIO.input(22) and not self.move_right_delay.is_delayed():
            self.controller.move_to_next_monitor_stream()
            self.move_right_delay.trigger()
        elif not GPIO.input(27) and not GPIO.input(18):
            os.system('sudo halt')
