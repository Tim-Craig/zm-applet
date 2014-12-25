from collections import namedtuple

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
    monitor_list = [parse_monitor_element(monitor_element) for monitor_element in xml_doc.xpath('//MONITOR_LIST/MONITOR')]
    monitor_map = {monitor.id: monitor for monitor in monitor_list if monitor.state == 'OK'}
    groups = [parse_group_element(group_element) for group_element in xml_doc.xpath('//GROUP_LIST/GROUP')]
    groups = filter(GroupFilter(monitor_map), groups)
    return groups, monitor_map


class ZmGroupTracker(object):
    def __init__(self, zm_xml_console):
        self.groups, self.monitors = parse_group_info_from_zm_xml(zm_xml_console)
        self.group_names = [group.name for group in self.groups]
        self.current_group_idx = 0
        self.current_monitor_idx = 0

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
        if self.current_group_idx < len(self.groups):
            if self.current_monitor_idx < len(self.groups[self.current_group_idx].monitor_ids):
                monitor_id = self.groups[self.current_group_idx].monitor_ids[self.current_monitor_idx]
                if monitor_id not in self.monitors:
                    raise Exception("Missing monitor id {0}".format(monitor_id))
                monitor = self.monitors[monitor_id]
        return monitor

    def get_monitors(self):
        return [self.monitors[monitor_id] for monitor_id in self.groups[self.current_group_idx].monitor_ids]