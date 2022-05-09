import socketserver

import sys
import os
import secrets
from parsers import *
from get import *
from database import *
from post import *
from frame_parser import parse_frame, build_frame


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    registered_users = {}  # username -> self
    web_sockets = []  # all websocket connections
    if os.path.isdir('/root'):
        inDocker = True

    usernames = []
    xsrf_token = {}
    valid_tokens = []  # The same for each user

    full_bytes_sent: bytes = b''
    

    def handle_websocket(self):
        print(f"Upgraded to websocket connection on instance {self}")
        username = ""
        ws_users = []
        ws_conn = []
        for usertxt in self.usernames:
            if len(usertxt) != 0:
                username = usertxt
                if username not in ws_users:
                    ws_users.append(username)
                    ws_conn.append(self)
        print('usernmae: ' + str(username))

        while True:
            data = self.request.recv(1024)
            print(str(data))
            if data != b'':
                payload = parse_frame(self, data)   # This function parses the frame and returns the payload (bytearray)
                print(f'payload is {payload}')
                # TODO - How do we handle a disconnect request?
                if payload == b'disconnect':
                    MyTCPHandler.web_sockets.remove(self)
                    break
                # Pack into a json object
                message = {}
                try:
                    message = json.loads(payload.decode())
                except Exception as e:
                    print(e)
                    continue
                print(f"\r\nmessage = {message}\r\n")

                # This is where we handle different message types
                message_type: str = message['messageType']
                if message_type.startswith('webRTC-'):
                    try:
                        for connection in MyTCPHandler.web_sockets:
                            if connection != self:
                                frame = build_frame(payload.decode(), 129)
                                print(f"Sending frame of size {len(frame)} with message type {message_type}")
                                connection.request.sendall(frame)
                    except Exception as e:
                        print(e)
                        continue
                elif message_type == 'chatMesssage':
                    # Send chat message
                    response = {'messageType': 'chatMessage', 'username': username,
                                'comment': escape_html(message['comment'])}
                    response = json.dumps(response)
                    add_user(username, response, cursor, db)  # Store on database

                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)
                    for connection in MyTCPHandler.web_sockets:
                        connection.request.sendall(response_frame)

                elif message_type == 'chessMessage':
                    pass
            sys.stdout.flush()
            sys.stderr.flush()

    def handle(self):
        while True:
            self.data = self.request.recv(1024)
            string_data: str = self.data.decode()

            sys.stdout.flush()
            sys.stderr.flush()

            self.full_bytes_sent += self.data

            if len(self.data) < 1023:
                break

        if 'GET' in str(self.full_bytes_sent):
            handle_get(self, self.full_bytes_sent)

        elif 'POST' in str(self.full_bytes_sent):
            handle_post(self, self.full_bytes_sent)
        else:
            print('ERROR OCCURRED IN SERVER.PY')


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
