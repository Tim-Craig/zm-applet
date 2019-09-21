from collections import namedtuple

Group = namedtuple('Group', ['id', 'name', 'monitor_ids'])
Monitor = namedtuple('Monitor', ['id', 'name', 'state', 'width', 'height', 'sequence'])


def parse_monitor_json(monitor_json):
    monitor_id = monitor_json['Id']
    name = monitor_json['Name']
    # TODO: find how to get monitor state from ZM API
    state = 'OK'
    if monitor_json['Enabled'] != "1":
        state = 'DISABLED'
    width = monitor_json['Width']
    height = monitor_json['Height']
    sequence = monitor_json['Sequence']
    return Monitor(monitor_id, name, state, width, height, sequence)


def parse_group_json(groups_json):
    group_id = groups_json['Id']
    name = groups_json['Name']
    group = None
    if 'MonitorIds' in groups_json:
        monitor_ids = groups_json['MonitorIds'].split(',')
        group = Group(group_id, name, monitor_ids)
    return group


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


def parse_group_info_from_api(group_api_json, monitor_api_json):
    monitor_list = [parse_monitor_json(monitor['Monitor']) for monitor in monitor_api_json['monitors']]
    monitor_list = sorted(monitor_list, key=lambda m: int(m.sequence))
    monitor_list = filter(lambda mon: mon.state == 'OK', monitor_list)
    monitor_map = {monitor.id: monitor for monitor in monitor_list}
    groups = [parsed_group for parsed_group in (parse_group_json(group['Group']) for group in group_api_json['groups'])
              if parsed_group is not None]
    all_monitors_group = Group("0", "All", [monitor.id for monitor in monitor_list])
    groups.insert(0, all_monitors_group)
    return groups, monitor_map


class ZmGroupTracker(object):
    def __init__(self):
        self.groups = None
        self.monitors = None
        self.group_names = None
        self.current_group = None
        self.current_group_index = None
        self.current_monitor = None
        self.current_monitor_index = None

    @classmethod
    def create_from_json_api(cls, zm_api_groups_json, zm_api_monitors_json):
        tracker = cls()
        tracker.load_from_json_api(zm_api_groups_json, zm_api_monitors_json)
        return tracker

    def load_from_json_api(self, zm_api_groups_json, zm_api_monitors_json, current_group=None, current_monitor=None):
        def find_item_index_in_list(item, item_list):
            if item:
                for index, list_item in enumerate(item_list):
                    if item.id == list_item.id:
                        return index

        def set_current_group_and_monitor():
            current_group_index = find_item_index_in_list(current_group, self.groups)
            if current_group_index:
                self.current_group_index = current_group_index
            else:
                self.current_group_index = 0
            if current_group and current_group in self.groups:
                self.current_group = current_group
            self.current_group = self.groups[self.current_group_index]

            self.current_monitor_index = 0
            if current_monitor and current_monitor.id in self.current_group.monitor_ids:
                self.current_monitor_index = self.current_group.monitor_ids.index(current_monitor.id)
            self.current_monitor = self.monitors[self.current_group.monitor_ids[self.current_monitor_index]]

        new_group, new_monitors = parse_group_info_from_api(zm_api_groups_json, zm_api_monitors_json)
        self.groups = new_group
        self.monitors = new_monitors
        if new_monitors and new_group:
            self.group_names = [group.name for group in self.groups]

            if len(self.groups) > 0:
                set_current_group_and_monitor()
            else:
                self.current_group = None
                self.current_group_index = None
                self.current_monitor = None
                self.current_monitor_index = None

    def set_current_group(self, group_id):
        index = 0
        for index, group in enumerate(self.groups):
            if group.id == group_id:
                break
        self._set_current_group(index)

    def set_current_group_by_name(self, group_name):
        index = 0
        for index, group in enumerate(self.groups):
            if group.name == group_name:
                break
        self._set_current_group(index)

    def _set_current_group(self, group_index):
        if -1 <= group_index < len(self.groups):
            self.current_group_index = group_index
        else:
            self.current_group_index = 0
        self.current_group_index = group_index
        self.current_group = self.groups[group_index]
        self.current_monitor_index = 0
        self.set_current_monitor(self.current_group.monitor_ids[0])

    def set_current_monitor(self, monitor_id):
        if monitor_id in self.current_group.monitor_ids:
            index = self.current_group.monitor_ids.index(monitor_id)
            self.current_monitor_index = index
            self.current_monitor = self.monitors[monitor_id]

    def set_current_monitor_by_name(self, monitor_name):
        id = 0
        for id, monitor in self.monitors.iteritems():
            if monitor.name == monitor_name:
                break
        self.set_current_monitor(id)

    def move_to_next_monitor(self):
        if self.groups:
            self.current_monitor_index += 1
            if self.current_monitor_index == len(self.groups[self.current_group_index].monitor_ids):
                self.current_monitor_index = 0
            self.current_monitor = self.get_current_monitor()
        return self.current_monitor

    def move_to_prev_monitor(self):
        if self.groups:
            self.current_monitor_index -= 1
            if self.current_monitor_index < 0:
                self.current_monitor_index = len(self.groups[self.current_group_index].monitor_ids) - 1
            self.current_monitor = self.get_current_monitor()
        return self.current_monitor

    def get_current_monitor(self):
        monitor = None
        if self.current_group_index is not None and self.current_group_index < len(self.groups):
            if self.current_monitor_index < len(self.groups[self.current_group_index].monitor_ids):
                monitor_id = self.groups[self.current_group_index].monitor_ids[self.current_monitor_index]
                if monitor_id not in self.monitors:
                    raise Exception("Missing monitor id {0}".format(monitor_id))
                monitor = self.monitors[monitor_id]
        return monitor

    def get_current_group_monitors(self):
        return [self.monitors[monitor_id] for monitor_id in self.groups[self.current_group_index].monitor_ids if
                monitor_id in self.monitors]
