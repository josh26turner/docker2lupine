import sys
import os
import time

from cgi import FieldStorage
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer


DEFAULT_IP='192.168.100.1'
DEFAULT_PORT=8080
STRACE_OUT='straceout/'


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if 'finish' in self.path:
            self.server.finished = True
    
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(('Continue' if not self.server.done else 'Stop').encode('utf-8'))

    
    def do_POST(self):
        form = FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

        try:
            if not os.path.exists(STRACE_OUT):
                os.mkdir(STRACE_OUT)

            with open(STRACE_OUT +  form['file_1'].filename, 'wb') as f:
                f.write(form['file_1'].file.read())
        except:
            self.send_response(500)
            self.send_header('Context-type', 'text/html')
            self.end_headers()
            self.wfile.write('Error'.encode('utf-8'))

            return

        self.send_response(200)
        self.send_header('Context-type', 'text/html')
        self.end_headers()
        self.wfile.write('Ok'.encode('utf-8'))


    def log_message(self, format, *args):
        return


class LupineHTTPServer(HTTPServer):
    done: bool = False
    finished: bool = False


class LupineServer():
    def __init__(self):
        self.server: HTTPServer
        self.daemon: Thread


    def start_server(self, port=DEFAULT_PORT, ip_addr=DEFAULT_IP):
        _done = False
        try:
            self.server = LupineHTTPServer((ip_addr, port), RequestHandler)
        except OSError as err:
            print(err, file=sys.stderr)
            exit(1)

        print('Starting server on {}:{}'.format(ip_addr, port))
        self.daemon = Thread(target=self.server.serve_forever)
        self.daemon.setDaemon(True)
        self.daemon.start()


    def kill_server(self):
        print("Killing server")
        self.server.shutdown()


    def set_done(self, done: bool):
        self.server.done = done
        print('Set done to {}'.format(done))
    

    def wait_for_finish(self):
        while self.server.finished != True:
            time.sleep(0.25)
        


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(epilog='Run from Lupine root directory')

    parser.add_argument('-ip', default=DEFAULT_IP)
    parser.add_argument('-p', default=DEFAULT_PORT)

    args = parser.parse_args()

    server = LupineServer()
    server.start_server(ip_addr=args.ip, port=args.p)

    try:
        while True:
            pass
    except KeyboardInterrupt as e:
        server.kill_server()
