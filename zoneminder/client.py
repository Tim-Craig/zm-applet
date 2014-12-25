class ZoneMinderClient(object):
    def __init__(self, ip, port=80, web_path="/", user_name=None, password=None):
        self.ip = ip
        self.port = port
        self.web_path = web_path
        self.user_name = user_name
        self.password = password

    def login(self):
        if self.user_name != None and self.password != None:
            pass #TODO log into the zoneminder

    def get_groups(self):
        pass