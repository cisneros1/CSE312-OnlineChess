import socketserver

import sys
import os
import secrets


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    
    if os.path.isdir('/root'):
        inDocker = True

    def handle(self):
        while True:
            received_data = self.request.recv(1024).strip()
            string_data: str = received_data.decode()

            if len(self.data) <= 0:
                return

            print('Length of incoming data: ' + str(len(self.data)))
            print("{} sent:".format(self.client_address[0]))
            print(str(self.data))
            sys.stdout.flush()
            sys.stderr.flush()
            self.full_bytes_sent += self.data
            self.iterations += 1
            
            
            


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
