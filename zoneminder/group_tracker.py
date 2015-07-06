from collections import namedtuple
import threading
import time
from urllib2 import URLError

Group = namedtuple('Group', ['id', 'name', 'monitor_ids'])
Monitor = namedtuple('Monitor', ['id', 'name', 'state', 'width', 'height'])


def parse_group_element(group_element):
    group_id = group_element.find('ID').text
    name = group_element.find('NAME').text
    monitor_ids = group_element.find('MONITORIDS').text.split(',')
    return Group(group_id, name, monitor_ids)


def parse_monitor_element(monitor_element):
    monitor_id = monitor_element.find('ID').text
    name = monitor_element.find('NAME').text
    state = monitor_element.find('STATE').text
    width = monitor_element.find('WIDTH').text
    height = monitor_element.find('HEIGHT').text
    return Monitor(monitor_id, name, state, width, height)


class GroupFilter(object):
    def __init__(self, monitor_map):
        self.monitor_map = monitor_map

    def __call__(self, group):
        group_ok = True
        for monitor_id in group.monitor_ids:
            if monitor_id not in self.monitor_map:
                group_ok = False
                break
            monitor = self.monitor_map[monitor_id]
            if monitor.state != 'OK':
                group_ok = False
                break
        return group_ok


def parse_group_info_from_zm_xml(zm_xml_console):
    from lxml import etree

    xml_doc = etree.parse(zm_xml_console)
    monitor_list = [parse_monitor_element(monitor_element) for monitor_element in
                    xml_doc.xpath('//MONITOR_LIST/MONITOR')]
    monitor_map = {monitor.id: monitor for monitor in monitor_list if monitor.state == 'OK'}
    groups = [parse_group_element(group_element) for group_element in xml_doc.xpath('//GROUP_LIST/GROUP')]
    groups = filter(GroupFilter(monitor_map), groups)
    return groups, monitor_map


class ZmGroupTracker(object):
    def __init__(self):
        self.groups = None
        self.monitors = None
        self.group_names = None
        self.current_group = None
        self.current_group_idx = None
        self.current_monitor = None
        self.current_monitor_idx = None

    @classmethod
    def from_xml_console(cls, zm_xml_console):
        tracker = cls()
        tracker._load_xml_console(zm_xml_console)
        return tracker

    def load_xml_console(self, zm_xml_console):
        self._load_xml_console(zm_xml_console, self.current_group, self.current_monitor)

    def _load_xml_console(self, zm_xml_console, current_group=None, current_monitor=None):
        def set_current_group_and_monitor():
            if current_group and current_group in self.groups:
                self.current_group = current_group
            else:
                self.current_group = self.groups[0]
            self.current_group_idx = self.groups.index(self.current_group)

            if current_monitor and current_group in self.current_group.monitor_ids:
                self.current_monitor = current_monitor
            else:
                self.current_monitor = self.current_group.monitor_ids[0]
            self.current_monitor_idx = self.current_group.monitor_ids.index(self.current_monitor)

        self.groups, self.monitors = parse_group_info_from_zm_xml(zm_xml_console)
        self.group_names = [group.name for group in self.groups]

        if len(self.groups) > 0:
            set_current_group_and_monitor()
        else:
            self.current_group = None
            self.current_group_idx = None
            self.current_monitor = None
            self.current_monitor_idx = None

    def set_current_group(self, group_idx):
        if group_idx < 0 or group_idx >= len(self.groups):
            raise Exception("Group id out of range")
        self.current_group_idx = 0
        self.current_monitor_idx = self.groups[self.current_group_idx].monitor_ids[0]

    def move_to_next_monitor(self):
        self.current_monitor_idx += 1
        if self.current_monitor_idx == len(self.groups[self.current_group_idx].monitor_ids):
            self.current_monitor_idx = 0
        return self.get_current_monitor()

    def move_to_prev_monitor(self):
        self.current_monitor_idx -= 1
        if self.current_monitor_idx < 0:
            self.current_monitor_idx = len(self.groups[self.current_group_idx].monitor_ids) - 1
        return self.get_current_monitor()

    def get_current_monitor(self):
        monitor = None
        if self.current_group_idx is not None and self.current_group_idx < len(self.groups):
            if self.current_monitor_idx < len(self.groups[self.current_group_idx].monitor_ids):
                monitor_id = self.groups[self.current_group_idx].monitor_ids[self.current_monitor_idx]
                if monitor_id not in self.monitors:
                    raise Exception("Missing monitor id {0}".format(monitor_id))
                monitor = self.monitors[monitor_id]
        return monitor

    def get_monitors(self):
        return [self.monitors[monitor_id] for monitor_id in self.groups[self.current_group_idx].monitor_ids]


class RefreshingZmGroupTracker(ZmGroupTracker):
    def __init__(self, zm_client, reload_time_secs=600):
        def start_refresh_thread():
            self.runner = threading.Thread(target=self._run)
            self.runner.daemon = True
            self.runner.start()

        super(RefreshingZmGroupTracker, self).__init__()
        self.zm_client = zm_client
        self.zm_group_tracker = None
        self.reload_time = reload_time_secs
        self.load_error = False
        self._load_console_from_client()
        start_refresh_thread()

    def _load_console_from_client(self):
        try:
            xml_console = self.zm_client.get_xml_console()
            self.load_xml_console(xml_console)
            self.load_error = False
        except URLError:
            self.load_error = True

    def _run(self):
        while True:
            if self.load_error:
                self._load_console_from_client()
            else:
                time.sleep(self.reload_time)
                self._load_console_from_client()
