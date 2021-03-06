import time
import socket

from threading import Thread


DEFAULT_IP='192.168.100.1'
DEFAULT_PORT=8080
STRACE_OUT='straceout/'


class SocketServer():
    def __init__(self):
        self.done = False
        self.ip_addr: str
        self.port: int
        self.finished: bool = False


    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockfd:
            sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockfd.bind((self.ip_addr, self.port))
            sockfd.listen(5)

            conn, addr = sockfd.accept()
            print('\nGuest connected from {}'.format(addr[0]))

            while True:
                rd_buffer = conn.recv(1024)

                if rd_buffer == b'get':
                    if self.done:
                        conn.sendall(b'stop')
                        break
                    else:
                        conn.sendall(b'cont')

                time.sleep(1)

            sockfd.shutdown(socket.SHUT_RDWR)
            sockfd.close()
            self.finished = True


class LupineServer():
    def __init__(self):
        self.server = SocketServer()
        self.daemon: Thread


    def start_server(self, port=DEFAULT_PORT, ip_addr=DEFAULT_IP):
        self.server.ip_addr = ip_addr
        self.server.port = port

        print('Starting server on {}:{}'.format(ip_addr, port))
        self.daemon = Thread(target=self.server.serve_forever)
        self.daemon.setDaemon(True)
        self.daemon.start()


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

    lupine_server = LupineServer()
    lupine_server.start_server(ip_addr=args.ip, port=args.p)

    input('Press enter when finished')
    lupine_server.set_done(True)
    lupine_server.wait_for_finish()
