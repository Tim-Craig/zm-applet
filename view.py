class View(object):
    """The View (in a MVC sense) of an AppComponent"""

    def __init__(self):
        self.size = None
        self.need_repaint = False
        self.enabled = True

    def check_if_repaint_needed(self):
        return_repaint = self.need_repaint
        self.need_repaint = False
        return return_repaint

    def start_view(self, size):
        self.size = size

    def paint(self, pos, display):
        pass

    def drag(self, drag_start_point, current_pos, delta):
        pass

    def process_pressed(self, pos):
        pass

    def process_press_released(self, pos):
        pass

    def process_click(self, pos):
        pass

    def update(self, time_elapsed):
        pass

    def close(self):
        pass


class CompoundView(View):
    def __init__(self, child_views, relative_dimensions):
        super(CompoundView, self).__init__()
        if len(child_views) != len(relative_dimensions):
            raise ValueError("child_views and relative_dimensions need to be the same size")
        self.child_views = child_views
        self.child_relative_rects = relative_dimensions
        self.child_actual_rects = []

    def start_view(self, size):
        def calculate_child_dimensions(child_view, dimensions):
            child_view_actual_dimensions = (
                int(size[0] * dimensions[0]), int(size[1] * dimensions[1]), int(size[0] * dimensions[2]),
                int(size[1] * dimensions[3]))
            self.child_actual_rects.append(child_view_actual_dimensions)
            child_view.start_view((child_view_actual_dimensions[2], child_view_actual_dimensions[3]))

        super(CompoundView, self).start_view(size)
        self.child_actual_rects = []
        for i in xrange(len(self.child_views)):
            calculate_child_dimensions(self.child_views[i], self.child_relative_rects[i])

    def check_if_repaint_needed(self):
        repaint_self = super(CompoundView, self).check_if_repaint_needed()
        child_repaint_indexes = [i for i in xrange(len(self.child_views)) if
                                 self.child_views[i].check_if_repaint_needed]
        return repaint_self or len(child_repaint_indexes) > 0

    def paint(self, pos, display):
        super(CompoundView, self).paint(pos, display)
        for i in xrange(len(self.child_views)):
            child_view = self.child_views[i]
            if child_view.enabled:
                child_pos = self.child_actual_rects[i]
                child_view.paint((child_pos[0], child_pos[1]), display)

    def _find_child_index_at_point(self, point):
        child_index = -1
        for i in xrange(len(self.child_views)):
            if self.child_views[i].enabled:
                child_rect = self.child_actual_rects[i]
                max_x = child_rect[0] + child_rect[2]
                max_y = child_rect[1] + child_rect[3]
                if child_rect[0] <= point[0] <= max_x and child_rect[1] <= point[1] <= max_y:
                    child_index = i
                    break
        return child_index

    def _translate_point_to_child(self, i, point):
        child_pos = self.child_actual_rects[i]
        return point[0] - child_pos[0], point[1] - child_pos[1]

    def drag(self, drag_start_point, current_pos, delta):
        super(CompoundView, self).drag(drag_start_point, current_pos, delta)
        i = self._find_child_index_at_point(drag_start_point)
        if i != -1:
            self.child_views[i].drag(self._translate_point_to_child(i, drag_start_point),
                                     self._translate_point_to_child(i, current_pos), delta)

    def process_pressed(self, pos):
        super(CompoundView, self).process_pressed(pos)
        i = self._find_child_index_at_point(pos)
        if i != -1:
            self.child_views[i].process_pressed(self._translate_point_to_child(i, pos))

    def process_press_released(self, pos):
        super(CompoundView, self).process_press_released(pos)
        i = self._find_child_index_at_point(pos)
        if i != -1:
            self.child_views[i].process_press_released(self._translate_point_to_child(i, pos))

    def process_click(self, pos):
        super(CompoundView, self).process_click(pos)
        i = self._find_child_index_at_point(pos)
        if i != -1:
            self.child_views[i].process_click(self._translate_point_to_child(i, pos))

    def update(self, time_elapsed):
        super(CompoundView, self).update(time_elapsed)
        for child_view in self.child_views:
            if child_view.enabled:
                child_view.update(time_elapsed)
