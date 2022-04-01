
def send_101(self, b64):
    response = b'HTTP/1.1 101 Switching Protocols'
    response += b'\r\nConnection: Upgrade'
    response += b'\r\nUpgrade: websocket'
    response += b'\r\nSec-WebSocket-Accept: ' + b64 + b'\r\n\r\n'
    print('Full response to be sent is: ' + str(response))
    self.request.sendall(response)


def send_200(self, length, mimetype, body):
    nosniff = "X-Content-Type-Options:nosniff"

    response = b"HTTP/1.1 200 OK"
    response += b"\r\nContent-Length: " + str(length).encode()
    response += b"\r\nContent-Type: " + mimetype.encode()
    response += b"\r\n"
    response += nosniff.encode()
    response += b"\r\n\r\n"
    response += body  # should be in bytes
    self.request.sendall(response)


def send_303(self, new_location):
    response = b"HTTP/1.1 303 See Other"
    response += b"\r\nContent-Length: 0"
    response += b"\r\nLocation: " + new_location.encode()
    self.request.sendall(response)


def send_403(self):
    response = b"HTTP/1.1 403 Forbidden"
    response += b"\r\nContent-Length: 0"
    self.request.sendall(response)
