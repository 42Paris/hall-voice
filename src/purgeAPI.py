import sys
import redis
import urllib.parse
import ipaddress
from http.server import HTTPServer, BaseHTTPRequestHandler
from Conf import Conf

if sys.argv[1] is not None:
    conf = Conf(sys.argv[1])
    r = redis.Redis(host=conf.getRedisHost(), port=conf.getRedisPort(), db=0)
else:
    print(f"Usage: python3 purgeAPI.py <path-to-conf-file>")
    exit(1)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_address = ipaddress.ip_address(self.client_address[0])
        if (client_address in ipaddress.ip_network("10.42.0.0/16")
                or (client_address in ipaddress.ip_network("10.43.0.0/16"))
                or (client_address in ipaddress.ip_network("10.41.0.0/16"))
                or (client_address in ipaddress.ip_network("10.50.0.0/16"))
                or (client_address in ipaddress.ip_network("10.51.0.0/16"))
                or (client_address in ipaddress.ip_network("127.0.0.1/32"))):
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
                    self.wfile.write(f"Login {purge_value[0]} purged from cache.".encode())
                else:
                    self.send_response(404)
                    # If login not found in cache
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f"Login not found: {purge_value[0]} not in cache".encode())
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
    run()
