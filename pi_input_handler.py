from input_handler import InputHandler, InputTracker
from app_events import *
import RPi.GPIO as GPIO
import threading
import time

GPIO_23 = 23
GPIO_22 = 22
GPIO_27 = 27
GPIO_18 = 18

GPIO_KEY_MAPPING = {'GPIO_23': GPIO_23, 'GPIO_22': GPIO_22, 'GPIO_27': GPIO_27, 'GPIO_18': GPIO_18}


class PiInputHandler(InputHandler):
    def __init__(self, event_bus, app_config):
        def event_ticker(gpio):
            while not GPIO.input(gpio):
                time.sleep(1.5)
                if not GPIO.input(gpio):
                    self.gpio_events.add(gpio)

        def falling_callback(gpio_num):
            if not self.gpio_state[gpio_num]:
                self.gpio_state[gpio_num] = True
                self.gpio_events.add(gpio_num)
                t = threading.Thread(target=event_ticker, args=(gpio_num,))
                t.start()
            else:
                self.gpio_state[gpio_num] = False

        super(PiInputHandler, self).__init__(event_bus, app_config)
        self.gpio_events = set()
        self.gpio_state = {GPIO_23: False, GPIO_22: False, GPIO_27: False, GPIO_18: False}

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(23, GPIO.BOTH, callback=falling_callback, bouncetime=300)
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(22, GPIO.BOTH, callback=falling_callback, bouncetime=300)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(27, GPIO.BOTH, callback=falling_callback, bouncetime=300)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(18, GPIO.BOTH, callback=falling_callback, bouncetime=300)

        self.input_trigger = InputTracker(app_config, GPIO_KEY_MAPPING)

    def check_input_commands(self):
        triggered_events = self.input_trigger.get_triggered_events(self.gpio_events)
        self.gpio_events.clear()
        for triggered_event in triggered_events:
            if triggered_event == EVENT_PREV_MONITOR:
                self.event_bus.publish_event(triggered_event)
            elif triggered_event == EVENT_NEXT_MONITOR:
                self.event_bus.publish_event(triggered_event)
            elif triggered_event == EVENT_SHUTDOWN:
                self.event_bus.publish_event(triggered_event)
