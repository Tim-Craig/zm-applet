import urllib2
import cookielib


def build_url(server_host_and_port, web_path='', params=None):
    query_section = ''
    if params:
        query_section = '?%s' % '&'.join([param + '=' + value for param, value in params.iteritems()])
    return 'http://%s/%s%s' % (server_host_and_port, web_path, query_section)


def build_urllib_request(server_host_and_port, web_path, params):
    return urllib2.Request(build_url(server_host_and_port, web_path, params))


class ZoneMinderClient(object):
    def __init__(self, ip, port=80, zm_web_path='', user_name=None, password=None, zms_web_path='cgi-bin/zms'):
        def get_server_host_and_port():
            port_string = '' if not port or str(port) == '80' else ':' + str(port)
            return ip + port_string

        def init_cookie_jar():
            cookie_jar = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
            urllib2.install_opener(opener)

        self.server_host_and_port = get_server_host_and_port()
        self.zm_web_path = zm_web_path
        self.zms_web_path = zms_web_path
        self.user_name = user_name
        self.password = password
        self.logged_in = False
        init_cookie_jar()

    def get_xml_console(self):
        self._login()
        xml_console_params = {'skin': 'xml', 'showGroups': 'true'}
        request = build_urllib_request(self.server_host_and_port, self.zm_web_path, xml_console_params)
        return urllib2.urlopen(request)

    def get_monitor_stream(self, monitor_id, scale='100'):
        self._login()
        stream_parameters = {'mode': 'jpeg', 'monitor': str(monitor_id), 'scale': str(scale)}
        request = build_urllib_request(self.server_host_and_port, self.zms_web_path, stream_parameters)
        return urllib2.urlopen(request)

    def _login(self):
        if not self.logged_in:
            if self.user_name is not None and self.password is not None:
                login_params = {'action': 'login', 'view': 'postlogin', 'username': self.user_name, 'password': self.password}
                request = build_urllib_request(self.server_host_and_port, self.zm_web_path, login_params)
                urllib2.urlopen(request)
            logged_in = True
