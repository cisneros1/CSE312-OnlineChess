import socketserver

import sys
import os
import secrets
from backend.parsers import *
from backend.get import handle_get

class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    
    if os.path.isdir('/root'):
        inDocker = True
        
    full_bytes_sent: bytes = b''
    def handle(self):
        while True:
            self.data = self.request.recv(1024).strip()
            string_data: str = self.data.decode()
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
            sys.stdout.flush()
            sys.stderr.flush()
            
            if request_type == 'get':
                handle_get(self, data)
            
        
if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
