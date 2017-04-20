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
from .codec import encode_char, decode_char


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
    def __init__(self, msg, cols=20, rows=4, is_utf=True, truncate=True):
        self.msg = msg
        self.cols = cols
        self.rows = rows
        self.is_utf = is_utf
        self.valid = True
        # TODO validate dimensions

    def as_utf(self):
        if self.is_utf:
            return self.msg
        lines = []
        for l in self.msg:
            lines.append(''.join([decode_char(c) for c in l]))
        return '\r\n'.join(lines)

    def as_hitachi(self):
        if not self.is_utf:
            return self.msg
        lines = []
        line = b''
        for c in self.msg:
            if c == '\r':  # TODO handle
                pass
            elif c == '\n':
                lines.append(line)
                line = b''
            else:
                line += encode_char(c)
        return lines

    def safe_msg(self):
        # TODO work out decode
        return self.msg.replace('\n', '\\n').replace('\r','\\r')

    def __str__(self):
        return 'View: %s' % (self.safe_msg())

    def __repr__(self):
        return "%s(msg='%s',cols=%s,rows=%s,is_utf=%s)" % (
            self.__class__.__name__,
            self.safe_msg(),
            self.cols,
            self.rows,
            self.is_utf)


class Server(object):
    def __init__(self, addr=None, lcd=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr
        self.lcd = lcd
        if self.lcd is None:
            self.lcd = Lcd()
        self.views = [View("this is the default\r\nview, update me", 0), ]
        self.settings = {}
        self.settings['rate'] = 2
        self.curr_view = 0
        self.lcd_view(self.views[self.curr_view])

    def lcd_view(self, view):
        # TODO auto-detect utf/hitachi to leverage msg's ordinal kwarg
        self.lcd.message(view.as_utf(), clear=True)

    def url(self, endpoint, ver='1'):
        return '/api/v%s/%s' % (ver, endpoint)

    def run(self):
        # UI Functions
        get('/')(self.frontend)
        # get('/', method='OPTIONS')(self.options_handler)
        # get('/<path:path>', method='OPTIONS')(self.options_handler)
        # hook('after_request')(self.enable_cors)

        # API v1 functions
        # UI
        get(self.url(''))(self.index)
        # non-view based API
        get(self.url('msg'))(self.get_msg)
        get(self.url('msg/'))(self.get_msg)
        post(self.url('msg') + '/<msg>')(self.set_msg)
        post(self.url('msg') + '/<msg>/')(self.set_msg)
        put(self.url('msg') + '/<msg>')(self.set_msg)
        put(self.url('msg') + '/<msg>/')(self.set_msg)
        delete(self.url('msg'))(self.clear_lcd)
        delete(self.url('msg/'))(self.clear_lcd)
        # settings API
        get(self.url('settings'))(self.get_settings)
        get(self.url('settings/'))(self.get_settings)
        post(self.url('settings'))(self.set_settings)
        post(self.url('settings/'))(self.set_settings)
        put(self.url('settings'))(self.set_settings)
        put(self.url('settings/'))(self.set_settings)
        # view based API
        get(self.url('view'))(self.get_view)
        get(self.url('view/'))(self.get_view)
        get(self.url('view') + '/<vid>')(self.get_view)
        get(self.url('view') + '/<vid>/')(self.get_view)
        post(self.url('view'))(self.set_view)
        post(self.url('view/'))(self.set_view)
        post(self.url('view') + '/<vid>')(self.set_view)
        post(self.url('view') + '/<vid>/')(self.set_view)
        put(self.url('view'))(self.set_view)
        put(self.url('view/'))(self.set_view)
        put(self.url('view') + '/<vid>')(self.set_view)
        put(self.url('view') + '/<vid>/')(self.set_view)
        delete(self.url('view'))(self.delete_view)
        delete(self.url('view/'))(self.delete_view)
        delete(self.url('view') + '/<vid>')(self.delete_view)
        delete(self.url('view') + '/<vid>/')(self.delete_view)
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

    def get_msg(self):
        success = True
        resp = '%s' % self.views[self.curr_view].msg
        return marshall_response(success, resp)

    def set_msg(self, msg):
        unqouted = unquote(msg)
        v = View(unqouted, 0)
        if not v.valid:
            success = False
            resp = 'Invalid view: %s' % v
            return marshall_response(success, resp)
        # Clears view list
        self.views = [v, ]
        self.settings['rate'] = 0
        success = self._change_to_vid(0)
        resp = '%s' % self.views[self.curr_view].msg
        return marshall_response(success, resp)

    # Does not clear any of the views
    def clear_lcd(self):
        self.lcd.clear()
        self.settings['rate'] = 0
        success = True
        resp = 'LCD has been cleared'
        return marshall_response(success, resp)

    def get_settings(self):
        success = True
        resp = {}
        resp['settings'] = self.settings
        return marshall_response(success, resp)

    def set_settings(self):
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

    def get_view(self, vid=None):
        success = True
        resp = {}
        # print('views %s' % self.views)
        if vid is None:
            resp['views'] = [jsonpickle.encode(v) for v in self.views]
            return marshall_response(success, resp)
        try:
            vid = int(vid)
        except ValueError:
            vid = -1
        if vid < 0 or vid >= len(self.views):
            success = False
            resp['msg'] = 'Invalid view id submitted'
            resp['views'] = []
            return marshall_response(success, resp)
        view = self.views[vid]
        success = True
        resp['views'].append(jsonpickle.encode(view))
        return marshall_response(success, resp)

    def set_views(self, views):
        self.views = []
        for i, v in enumerate(views):
            # TODO test View.valid
            self.views.append(View(v['msg'], i))
        success = True
        resp = 'you have now reset all views to what you uploaded'
        return marshall_response(success, resp)

    def change_to_vid(self, vid):
        success = True
        if not self._change_to_vid(vid):
            success = False
        if success:
            resp = 'you have now changed the current view to the specified view id %s: %s' % (vid, view)
        else:
            resp = 'View content incorrect dimensions'
        return marshall_response(success, resp)

    def _change_to_vid(self, vid):
        view = self.views[vid]
        self.curr_view = vid
        try:
            self.lcd_view(view)
        except IndexError:
            return False
        return True

    def set_view(self, vid=None):
        # if no vid, then set all from ['views']
        if vid is None:
            req = load_request(['views'])
            if req['views'] is None:
                success = False
                resp = 'No views submitted'
                return marshall_response(success, resp)
            return self.set_views(req['views'])
        # all others need vid to be valid
        try:
            vid = int(vid)
        except ValueError:
            success = False
            resp = 'Invalid view id submitted %s' % vid
            return marshall_response(success, resp)
        max_vid = len(self.views)
        req = load_request(['view'])
        if req['view'] is None:
            max_vid -= 1
        if vid > max_vid:
            success = False
            resp = 'Invalid view id submitted %s' % vid
            return marshall_response(success, resp)
        # if vid but no req, then change curr view to vid
        if req['view'] is None:
            return self.change_to_vid(vid)
        # if vid and req, then update that vid to req
        if vid == len(self.views):
            # TODO test View.valid
            self.views.append(View(req['view']['msg'], vid))
        else:
            self.views[vid] = View(req['view']['msg'], vid)
        success = True
        resp = 'you have now reset view %s to what you uploaded %s' % (vid, self.views[vid])
        return marshall_response(success, resp)

    def delete_view(self, vid=None):
        if vid is None:
            self.views = []
            success = True
            resp = 'you have now deleted all views'
            return marshall_response(success, resp)
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

    def settings(self, settings=None):
        if settings is None:
            rjson = self.get('settings')
        else:
            rjson = self.post('settings', {'settings': settings})
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def get_view(self, vid=None):
        """Get all views or particular vid"""
        if vid is None:
            rjson = self.get('view')
        else:
            rjson = self.get('view/%s' % vid)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def print_view(self, vid):
        """Make a particular vid show on LCD"""
        rjson = self.put('view/%s' % vid)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def set_view(self, msg, vid):
        """Set all views, particular vid, or append"""
        if isinstance(msg, list):
            return self.set_views(msg)
        # TODO if vid is -1, get index to use for append
        rjson = self.post('view/%s' % vid, {'view': {'msg': msg}})
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def set_views(self, msgs):
        """Set all views"""
        view_d = {}
        view_d['views'] = []
        for m in msgs:
            view_d['views'].append({'msg': m})
        rjson = self.post('view', view_d)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def del_view(self, vid=None):
        if vid is None:
            rjson = self.delete('view')
        else:
            rjson = self.delete('view/%s' % vid)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']
