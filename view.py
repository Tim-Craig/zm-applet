class View(object):
    def __init__(self):
        self.size = None
        self.need_repaint = False

    def check_if_repaint_needed(self):
        return_repaint = self.need_repaint
        self.need_repaint = False
        return return_repaint

    def start_view(self, size):
        self.size = size

    def paint(self, display):
        pass

    def close(self):
        pass
