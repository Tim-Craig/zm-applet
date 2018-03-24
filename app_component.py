class AppComponent(object):
    """A inner application of the applet.  Groups a controller, view and overlay together."""

    def __init__(self, app_context, activation_event):
        self.app_context = app_context
        self.activation_event = activation_event
        self.controller = None
        self.view = None
        self.overlay = None

    def activate(self, data=None):
        if self.controller:
            self.controller.activate()

    def deactivate(self):
        if self.controller:
            self.controller.deactivate()

    def update(self, time_elapsed):
        if self.view:
            self.view.update(time_elapsed)
        if self.overlay:
            self.overlay.update(time_elapsed)
