EVENT_QUIT = 'quit'
EVENT_PREV_MONITOR = 'prev_monitor'
EVENT_NEXT_MONITOR = 'next_monitor'
EVENT_SHUTDOWN = 'shutdown'
EVENT_OPEN_GROUP_VIEW = 'open_group_view'

INTERNAL_EVENT_RELEASE_COMPONENT = 'release_component'


def get_event_type_configs():
    return [EVENT_QUIT, EVENT_PREV_MONITOR, EVENT_NEXT_MONITOR, EVENT_SHUTDOWN, EVENT_OPEN_GROUP_VIEW]