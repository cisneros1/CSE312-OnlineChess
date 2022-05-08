
def send_101(self, b64):
    response = b'HTTP/1.1 101 Switching Protocols'
    response += b'\r\nConnection: Upgrade'
    response += b'\r\nUpgrade: websocket'
    response += b'\r\nSec-WebSocket-Accept: ' + b64 + b'\r\n'
    response += b'X-Content-Type-Options: nosniff\r\n\r\n'
    # print('Full response to be sent is: ' + str(response))
    self.request.sendall(response)
                 
def send_200(self, length, mimetype, body):
    nosniff = "X-Content-Type-Options:nosniff"
    
    response = b"HTTP/1.1 200 OK"
    response += b"\r\nContent-Length: " + str(length).encode()
    response += b"\r\nContent-Type: " + mimetype.encode()
    response += b"\r\n"
    response += nosniff.encode()
    response += b"\r\n\r\n"
    response += body #should be in bytes
    self.request.sendall(response)
    

def send_200_with_cookie(self, length, mimetype, body, cookie: str):
    nosniff = "X-Content-Type-Options:nosniff"

    response = b"HTTP/1.1 200 OK"
    response += b"\r\nContent-Length: " + str(length).encode()
    response += b"\r\nContent-Type: " + mimetype.encode()
    response += b"\r\nSet-Cookie: " + str(cookie).encode() + b'; Max-Age: 3600'
    response += b"\r\n"
    response += nosniff.encode()
    response += b"\r\n\r\n"
    response += body  # should be in bytes
    self.request.sendall(response)
    
def send_201(self):
    nosniff = "X-Content-Type-Options:nosniff"

    response = b'HTTP/1.1 201 Created\r\n'
    response += b"\r\nContent-Length: 4"
    response += b"\r\nContent-Type: text/plain\r\n"
    response += nosniff.encode()
    response += b"\r\n\r\n"
    response += b"\r\nGood"
    self.request.sendall(response)


def send_json(self, length, mimetype, body):
    nosniff = "X-Content-Type-Options:nosniff"

    response = b"HTTP/1.1 200 OK"
    response += b"\r\nContent-Length: " + str(length).encode()
    response += b"\r\nContent-Type: " + mimetype.encode()
    response += b"\r\n"
    response += nosniff.encode()
    response += b"\r\n\r\n"
    response += body.decode()
    self.request.sendall(response)
    

def send_301(self, new_location):
    response = b"HTTP/1.1 301 Moved Permanently"
    response += b"\r\nContent-Length: 0"
    response += b"\r\nLocation: " + new_location.encode()
    self.request.sendall(response)
    

def send_303(self):
    response = b"HTTP/1.1 303 See Other"
    response += b"\r\nContent-Type: text/html"
    response += b"\r\nContent-Length: " + \
        str(len('/signin')).encode()
    response += b"\r\nLocation: /signin"
    self.request.sendall(response)
    
    
def send_403(self):
    response = b"HTTP/1.1 403 Forbidden"
    response += b"\r\nContent-Length: 0"
    self.request.sendall(response)


def send_404(self):
    response = b"HTTP/1.1 404 Not Found"
    response += b"\r\nContent-Type: text/plain"
    response += b"\r\nContent-Length: 36"
    response += b"\r\nThe requested content does not exist"
    response += b"\r\nX-content-type-Options: nosniff"
    self.request.sendall(response)
