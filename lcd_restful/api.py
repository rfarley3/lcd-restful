import json
import jsonpickle
import requests
import os
from bottle import (
    run,
    route as get, post, put, delete,
    request,  # response, hook
)
from urllib.parse import unquote, quote

from . import DEBUG, BOTTLE_DEBUG, PORT
from .lcd import Lcd


def load_request(possible_keys):
    """Given list of possible keys, return any matching post data"""
    pdata = request.json
    if pdata is None:
        pdata = json.loads(request.body.getvalue().decode('utf-8'))
    for k in possible_keys:
        if k not in pdata:
            pdata[k] = None
    # print('pkeys: %s pdata: %s' % (possible_keys, pdata))
    return pdata


def marshall_response(success, resp):
    return json.dumps({'success': success, 'resp': resp}) + '\n'


class ApiConnError(BaseException):
    pass


class View(object):
    def __init__(self, msg, vid=None, lcd=None):
        self.msg = msg
        self.lcd = lcd
        self.screen_bytes = self.normalize(msg)
        self.id = vid
        self.valid = True
        if self.screen_bytes is None:
            self.valid = False

    def normalize(self, msg):
        # verify all line lens
        # on errors, return None
        lines = []
        for line in msg.split('\n'):
            if len(line) > 20:  # TODO know lcd width
                line = line[:20]
            lines.append(line)
        if len(lines) > 4:
            lines = lines[:4]
        msg = '\n'.join(lines)
        msg = self.lcd.encode(msg)
        # byte_arr = ''
        # for c in msg:
        #     byte_arr += chr(c)
        # return byte_arr
        # msg = msg.encode()
        # verify character ranges
        # chars = ''
        # for c in msg:
        #     if c != '\n':
        #         o = ord(c)
        #         if o < 32 or o > 255:
        #             c = '?'
        #     chars += c
        # msg = chars/
        return msg

    def safe_msg(self):
        # TODO work out decode
        return self.msg.replace('\n', '\\n').decode('utf-8')

    def __str__(self):
        return 'id: %s msg: %s' % (self.id, self.safe_msg())

    def __repr__(self):
        return "%s(msg='%s',vid=%s)" % (self.__class__.__name__, self.safe_msg(), self.id)


class Server(object):
    def __init__(self, addr=None, lcd=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr
        self.lcd = lcd
        if self.lcd is None:
            self.lcd = Lcd()
        self.views = [View("this is the default\nview, update me", 0, self.lcd),]
        self.settings = {}
        self.settings['rate'] = 2
        self.curr_view = 0
        self.lcd_view(self.views[self.curr_view])

    def lcd_view(self, view):
        self.lcd_msg(view.screen_bytes)

    def lcd_msg(self, msg):
        self.lcd.clear()
        self.lcd.message(msg)

    def url(self, endpoint, ver='1'):
        return '/api/v%s/%s' % (ver, endpoint)

    def run(self):
        # UI Functions
        get('/')(self.frontend)
        # get('/', method='OPTIONS')(self.options_handler)
        # get('/<path:path>', method='OPTIONS')(self.options_handler)
        # hook('after_request')(self.enable_cors)

        # API functions
        # v1
        get(self.url(''))(self.index)
        get(self.url('msg'))(self.direct_msg_get)
        post(self.url('msg') + '/<msg>')(self.direct_msg)
        put(self.url('msg') + '/<msg>')(self.direct_msg)
        delete(self.url('msg'))(self.clear)
        get(self.url('view'))(self.get_views_settings)
        post(self.url('view'))(self.change_settings)
        put(self.url('view'))(self.set_views)
        delete(self.url('view'))(self.delete_views)
        get(self.url('view') + '/<vid>')(self.get_view)
        post(self.url('view') + '/<vid>')(self.change_to_view)
        put(self.url('view') + '/<vid>')(self.set_view)
        delete(self.url('view') + '/<vid>')(self.delete_view)
        run(host=self.host, port=self.port,
            debug=BOTTLE_DEBUG, quiet=not BOTTLE_DEBUG)

    # def enable_cors(self):
    #     '''Add headers to enable CORS'''
    #     _allow_origin = '*'
    #     _allow_methods = 'PUT, GET, POST, DELETE, OPTIONS'
    #     _allow_headers = ('Authorization, Origin, Accept, ' +
    #                       'Content-Type, X-Requested-With'
    #     response.headers['Access-Control-Allow-Origin'] = _allow_origin
    #     response.headers['Access-Control-Allow-Methods'] = _allow_methods
    #     response.headers['Access-Control-Allow-Headers'] = _allow_headers

    # def options_handler(path=None):
    #     '''Respond to all OPTIONS requests with a 200 status'''
    #     return

    def frontend(self):
        static_dir = os.path.abspath(os.path.dirname(__file__))
        static_html = os.path.join(static_dir, 'index.html')
        with open(static_html, 'r') as f:
            html = f.read()
        return html + '\n'

    def index(self):
        success = True
        resp = 'LCD API is running'
        return marshall_response(success, resp)

    def direct_msg_get(self):
        success = True
        resp = '%s' % self.views[self.curr_view].msg
        return marshall_response(success, resp)

    def direct_msg(self, msg):
        unqouted = unquote(msg)
        v = View(msg, 0, self.lcd)
        if not v.valid:
            success = False
            resp = 'Invalid view: %s' % v
            return marshall_response(success, resp)
        # NOTE clears view list
        self.curr_view = 0
        self.views = [v,]
        self.settings['rate'] = 0
        success = True
        resp = self.lcd_view(v)
        return marshall_response(success, resp)

    def clear(self):
        self.lcd.clear()
        self.settings['rate'] = 0
        success = True
        resp = 'LCD has been cleared'
        return marshall_response(success, resp)

    def get_views_settings(self):
        success = True
        resp = 'this returns all the settings and a list of all views'
        resp = {}
        resp['settings'] = self.settings
        # print('views %s' % self.views)
        resp['views'] = [jsonpickle.encode(v) for v in self.views]
        return marshall_response(success, resp)

    def change_settings(self):
        req = load_request(['settings'])
        # print('req: %s' % req)
        if req['settings'] is None:
            success = False
            resp = 'No settings submitted'
            return marshall_response(success, resp)
        self.settings.update(req['settings'])
        success = True
        resp = 'you have now changed the settings %s' % self.settings
        return marshall_response(success, resp)

    def set_views(self):
        req = load_request(['views'])
        if req['views'] is None:
            success = False
            resp = 'No views submitted'
            return marshall_response(success, resp)
        self.views = []
        for i, v in enumerate(req['views']):
            # TODO test View.valid
            self.views.append(View(v['msg'], i, self.lcd))
        success = True
        resp = 'you have now reset all views to what you uploaded'
        return marshall_response(success, resp)

    def delete_views(self):
        self.views = []
        success = True
        resp = 'you have now deleted all views'
        return marshall_response(success, resp)

    def get_view(self, vid):
        try:
            vid = int(vid)
        except ValueError:
            vid = -1
        if vid < 0 or vid >= len(self.views):
            success = False
            resp = 'Invalid view id submitted'
            return marshall_response(success, resp)
        view = self.views[vid]
        success = True
        resp = 'this returns a particular view %s: %s' % (vid, view)
        return marshall_response(success, resp)

    def change_to_view(self, vid):
        try:
            vid = int(vid)
        except ValueError:
            vid = -1
        if vid < 0 or vid >= len(self.views):
            success = False
            resp = 'Invalid view id submitted'
            return marshall_response(success, resp)
        view = self.views[vid]
        self.curr_view = vid
        self.lcd_view(view)
        success = True
        resp = 'you have now changed the current view to the specified view id %s: %s' % (vid, view)
        return marshall_response(success, resp)

    def set_view(self, vid):
        try:
            vid = int(vid)
        except ValueError:
            vid = -1
        if vid < 0 or vid > len(self.views):
            success = False
            resp = 'Invalid view id submitted'
            return marshall_response(success, resp)
        req = load_request(['view'])
        if req['view'] is None:
            success = False
            resp = 'No view submitted'
            return marshall_response(success, resp)
        if vid == len(self.views):
            # TODO test View.valid
            self.views.append(View(req['view']['msg'], vid, self.lcd))
        else:
            self.views[vid] = View(req['view']['msg'], vid, self.lcd)
        success = True
        resp = 'you have now reset view %s to what you uploaded %s' % (vid, self.views[vid])
        return marshall_response(success, resp)

    def delete_view(self, vid):
        try:
            vid = int(vid)
        except ValueError:
            vid = -1
        if vid < 0 or vid >= len(self.views):
            success = False
            resp = 'Invalid view id submitted'
            return marshall_response(success, resp)
        if vid == 0:
            self.views = self.views[1:]
        elif vid == len(self.views):
            self.views = self.views[:-1]
        else:
            self.views = self.views[:vid - 1] + self.views[vid + 1:]
        success = True
        resp = 'you have now deleted view %s %s' % (vid, self.views)
        return marshall_response(success, resp)


class Client(object):
    """Importable Python object to wrap REST calls"""
    def __init__(self, addr=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr

    def url(self, endpoint, ver='1'):
        return ('http://%s:%s/api/v%s/%s' %
                (self.host, self.port, ver, endpoint))

    def get(self, endpoint):
        try:
            resp = requests.get(self.url(endpoint))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def post(self, endpoint, data={}):
        try:
            resp = requests.post(self.url(endpoint), data=json.dumps(data))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def put(self, endpoint, data={}):
        try:
            resp = requests.put(self.url(endpoint), data=json.dumps(data))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def delete(self, endpoint):
        try:
            resp = requests.delete(self.url(endpoint))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def msg(self, msg=None):
        if msg is None:
            rjson = self.get('msg')
        else:
            msg = quote(msg)
            rjson = self.post('msg/%s' % msg)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def clear(self):
        rjson = self.delete('msg')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def view(self, vid=None):
        if vid is None:
            rjson = self.get('view')
        else:
            rjson = self.get('view/%s' % vid)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    # def pause(self):
    #     rjson = self.put('player')
    #     if rjson is None or not rjson['success']:
    #         print('API request failure: %s' % rjson)
    #         return False
    #     return True

