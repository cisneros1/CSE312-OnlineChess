import socketserver

import sys
import os
import secrets
from parsers import *

class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    
    if os.path.isdir('/root'):
        inDocker = True

    def handle(self):
        while True:
            received_data = self.request.recv(1024).strip()
            string_data: str = received_data.decode()
            path, headers, content = parse_request(self.data)
            # Data buffering
            data = self.data
            boundary = None # This is used when form data is sent   
            buffered = False
            content_read = bytes_read(self.data)    # Content read in the first packet
            content_length = get_content_length(self.data)  # The value of the content length header

            if len(self.data) <= 0:
                return

            # Buffering loop
            while content_read < content_length:
                buffer_data = self.request.recv(1024)
                content_read += len(buffer_data)
                buffered = True
                data += buffer_data # Append the buffered bytes

            # Parsing the buffered data
            if buffered:
                boundary = get_boundary(headers)
                content = parse_content(data, boundary)
            request_type = find_request_type(string_data)   # is either 'get', 'post', 'delete' etc

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
