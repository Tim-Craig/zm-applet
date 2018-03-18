class InputManager(object):
    def __init__(self, input_handlers):
        self.input_handlers = input_handlers

    def process_inputs(self):
        for handler in self.input_handlers:
            handler.check_input_commands()
