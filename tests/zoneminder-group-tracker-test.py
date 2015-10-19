import os

from zoneminder.group_tracker import ZmGroupTracker


def test_tracker_initialization():
    console_file = open(os.path.join('.', 'test-resources', 'zoneminder-xml-console.xml'))
    ZmGroupTracker(console_file)


def test_get_monitors():
    console_file = open(os.path.join('.', 'test-resources', 'zoneminder-xml-console.xml'))
    tracker = ZmGroupTracker(console_file)
    monitors = tracker.get_current_group_monitors()
    assert (monitors[0].id == '11')
    assert (monitors[1].id == '6')
    assert (monitors[2].id == '1')
    assert (monitors[3].id == '7')
    assert (monitors[4].id == '3')
    assert (monitors[5].id == '5')
    assert (monitors[6].id == '8')
    assert (monitors[7].id == '2')
    assert (monitors[8].id == '9')
    assert (monitors[9].id == '12')
    assert (monitors[10].id == '13')


def test_move_to_next_monitor():
    console_file = open(os.path.join('.', 'test-resources', 'zoneminder-xml-console.xml'))
    tracker = ZmGroupTracker(console_file)
    monitors = tracker.get_current_group_monitors()
    monitor = tracker.move_to_next_monitor()
    assert (monitor == monitors[1])


def test_move_to_prev_monitor():
    console_file = open(os.path.join('.', 'test-resources', 'zoneminder-xml-console.xml'))
    tracker = ZmGroupTracker(console_file)
    monitors = tracker.get_current_group_monitors()
    monitor = tracker.move_to_prev_monitor()
    assert (monitor == monitors[len(monitors) - 1])


def test_move_to_next_monitor_wrap_end():
    console_file = open(os.path.join('.', 'test-resources', 'zoneminder-xml-console.xml'))
    tracker = ZmGroupTracker(console_file)
    monitors = tracker.get_current_group_monitors()
    monitor = None
    for i in xrange(len(monitors)):
        monitor = tracker.move_to_next_monitor()
    assert (monitor == monitors[0])
