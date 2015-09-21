class SelectionHandler(object):
    def handle_selection(self, selection):
        pass


class MethodCallbackSelectionHandler(SelectionHandler):
    def __init__(self, method):
        self.method = method

    def handle_selection(self, selection):
        self.method(selection)