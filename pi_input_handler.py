from input_handler import InputHandler
import RPi.GPIO as GPIO
import os


class PiInputHandler(InputHandler):
    def __init__(self, controller):
            super(self.__class__, self).__init__(controller)
            GPIO.setmode(GPIO.BCM)

            GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def check_input_commands(self):
        if not GPIO.input(23):
            self.controller.move_to_prev_monitor_stream()
        elif not GPIO.input(22):
            self.controller.move_to_next_monitor_stream()
        elif not GPIO.input(27) and not GPIO.input(18):
            os.system('sudo halt')
