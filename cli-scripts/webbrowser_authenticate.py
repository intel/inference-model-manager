import webbrowser
import argparse
from os.path import expanduser, join
from os import getenv
import sys
import json
import threading
try:
    # Imports for Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs, urlunparse, urlencode, parse_qsl
    import http.client as httplib
except ImportError:
    # Imports for Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    import httplib
    from urlparse import urlparse, parse_qs, urlunparse, parse_qsl
    from urllib import urlencode

html_page = """
<html><body><h1>
Now you can close this web browser window and return to the console.
</h1></body></html>
"""
code = None


def get_dex_auth_url(address, port):
    conn = httplib.HTTPConnection(address, port)
    conn.request("GET", "/authenticate")
    r1 = conn.getresponse()
    dex_auth_url = r1.getheader('location')
    if dex_auth_url is None:
        print("Can`t get dex url.")
        sys.exit()
    return dex_auth_url


def get_dex_auth_token(address, port, auth_code):
    conn = httplib.HTTPConnection(address, port)
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    conn.request("POST", "/authenticate/token", json.dumps({'code': auth_code}), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        dict_data = json.loads(data.decode('utf-8'))
        return dict_data['data']['token']
    else:
        print("Error occurred while trying to get token.")
        sys.exit()


def enable_getting_refresh_token(auth_url):
    url_parts = list(urlparse(auth_url))
    query = dict(parse_qsl(url_parts[4]))
    query['scope'] = query['scope'] + ' offline_access'

    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def open_webbrowser(address):
    print("Your browser has been opened to visit:\n{}".format(address))
    try:
        webbrowser.open(url=address, new=1)
    except webbrowser.Error as e:
        print("Unable to open the web browser: {}".format(e))
        sys.exit()


def run_server(port, auth_url):
    class Server(BaseHTTPRequestHandler):

        def log_message(self, format, *args):
            return

        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            self._set_headers()
            query = urlparse(self.path).query
            parsed_query = parse_qs(query)
            if 'code' in parsed_query:
                print("A request was received with an authorization code.")
                global code
                code = parsed_query['code'][0]
                self.prepare_response()
                self.kill_server()

        def prepare_response(self):
            python_ver = sys.version_info.major
            if python_ver == 3:
                self.wfile.write(bytes(html_page, 'UTF-8'))
            else:
                self.wfile.write(html_page)

        def kill_server(self):
            assassin = threading.Thread(target=httpd.shutdown)
            assassin.daemon = True
            assassin.start()

    handler_class = Server
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler_class)
    open_webbrowser(auth_url)
    print('Waiting for authorization code.')
    httpd.serve_forever()


def save_to_file(file_path, data):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, help='management api address without port',
                        required=True)
    parser.add_argument('--port', type=int, help='management api port', required=False,
                        default=5000)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    config_path = getenv('INFERNO_CONFIG', join(expanduser("~"), '.inferno'))
    auth_url = get_dex_auth_url(address=args.address, port=args.port)
    auth_url_with_refresh_token = enable_getting_refresh_token(auth_url)

    auth_url_unparsed = urlparse(auth_url)
    queries = parse_qs(auth_url_unparsed.query)
    redirect_port = urlparse(queries['redirect_uri'][0]).port

    run_server(redirect_port, auth_url_with_refresh_token)
    print('Code recieved, waiting for token.')
    dex_url = urlunparse((auth_url_unparsed.scheme, auth_url_unparsed.netloc, '', '', '', ''))
    token = get_dex_auth_token(address=args.address, port=args.port, auth_code=code)
    token.update({'dex_url': dex_url})
    save_to_file(config_path, token)
    print("Your token and refresh token are available in file: {}".format(config_path))


if __name__ == '__main__':
    main()
