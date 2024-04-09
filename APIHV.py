import redis
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from Conf import Conf

r = redis.Redis(host='127.0.0.1', port=6379, db=0)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if
        # Parse query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        # Check if 'purge' parameter exists
        purge_value = query_components.get('purge', None)

        if purge_value:
            print(f"Purge request received with value: {purge_value[0]}")
            cache = r.get(f"login: {purge_value[0]}")
            if cache:
                r.delete(f"login: {purge_value[0]}")
                # Respond to the client
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Login {purge_value[0]} found in cache, purging...".encode())
            else:
                self.send_response(404)
                # If login not found in cache
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Login not found: {purge_value[0]} cannot purge from cache".encode())
        else:
            # If no purge parameter, send man
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Please provide a 'purge' query parameter.".encode())


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {server_address[1]}")
    httpd.serve_forever()


if __name__ == '__main__':
    conf = Conf("config.ini")
    run()
