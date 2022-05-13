import socketserver

import sys
import os
import secrets
from parsers import *
from get import *
from database import *
from post import *
from frame_parser import parse_frame, build_frame
from stored_users import authenticated_users, web_socket_connections
import time


class MyTCPHandler(socketserver.BaseRequestHandler):
    # clients = []
    # registered_users = {}  # username -> self
    # web_sockets = []  # all websocket connections
    if os.path.isdir('/root'):
        inDocker = True

    usernames = []

    colors = []
    xsrf_token = {}
    valid_tokens = []  # The same for each user

    full_bytes_sent: bytes = b''

    def handle_websocket(self, username):
        print(f"\r\nUpgraded to websocket connection on instance {self} with user {username}\r\n")
        # Add this instance to global variable containing all the websocket connections
        # TODO - right now users can see new changes on reload but cannot send message
        registered = False
        if username in authenticated_users:
            print(f"Added {username} to websocket connections")
            web_socket_connections[username] = self
            registered = True

        while not registered:
            pass

        set_username = {'messageType': 'setUsername', 'username': username}
        set_username = json.dumps(set_username)
        set_username_frame = build_frame(set_username, 129)
        self.request.sendall(set_username_frame)

        while True:
            data = self.request.recv(1024)
            # print(str(data))
            if data != b'':
                payload: bytearray = parse_frame(self, data)  # This function parses the frame
                print(f'payload is {payload}')
                # TODO - How do we handle a disconnect request?
                if payload == b'disconnect':
                    print(f'\r\nDisconnecting on user {username}\r\n')
                    web_socket_connections.pop(username, None)  # delete websocket connection from global variable
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
                        for connection in web_socket_connections.values():
                            if connection != self:
                                frame = build_frame(payload.decode(), 129)
                                print(f"Sending frame of size {len(frame)} with message type {message_type}")
                                connection.request.sendall(frame)
                    except Exception as e:
                        print(e)
                        continue
                elif message_type == 'chatMessage':
                    # Send chat message
                    response = {'messageType': 'chatMessage', 'username': username,
                                'comment': escape_html(message['comment'])}
                    response = json.dumps(response)
                    add_user(username, response, cursor, db)  # Store on database

                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)
                    for connection in web_socket_connections.values():
                        connection.request.sendall(response_frame)

                elif message_type == 'DirectMessage':
                    sender = message['sender']
                    receiver = message['receiver']
                    message = f'Received DM from {sender}: {message["comment"]}'

                    response = {'messageType': 'chatMessage', 'username': username,
                                'comment': escape_html(message)}
                    response = json.dumps(response)

                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)

                    receiver_connection = web_socket_connections.get(receiver)
                    if receiver_connection:
                        receiver_connection.request.sendall(response_frame)
                    else:
                        print("\r\n1. Recipient was disconnected.\r\n")

                elif message_type == 'Challenge':
                    sender = message['sender']
                    receiver = message['receiver']
                    response = {'messageType': 'Challenge', 'sender': sender, 'receiver': receiver}
                    response = json.dumps(response)

                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)
                    receiver_connection = web_socket_connections.get(receiver)

                    if receiver_connection:
                        receiver_connection.request.sendall(response_frame)
                    else:
                        print("\r\n2. Recipient was disconnected.\r\n")

                elif message_type == 'ChallengeAccepted':
                    sender = message['sender']
                    receiver = message['receiver']
                    response = {'messageType': 'ChallengeAccepted', 'sender': sender, 'receiver': receiver}
                    response = json.dumps(response)

                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)
                    sender_connection = web_socket_connections.get(sender)

                    if sender_connection:
                        sender_connection.request.sendall(response_frame)
                    else:
                        print("\r\n3. Recipient was disconnected.\r\n")

                elif message_type == 'chessMessage':
                    pass
            sys.stdout.flush()
            sys.stderr.flush()

    def handle_game_connection(self, username):
        print(f"\r\nUpgraded to websocket connection on instance {self} with user {username}\r\n")

        while True:
            data = self.request.recv(1024)
            # print(str(data))
            if data != b'':
                payload: bytearray = parse_frame(self, data)  # This function parses the frame
                # TODO - How do we handle a disconnect request?
                if payload == b'disconnect':
                    print(f'\r\nDisconnecting\r\n')
                    # web_socket_connections.pop(username, None)  # delete websocket connection from global variable
                    break
                # Pack into a json object
                message = {}
                try:
                    message = json.loads(payload.decode())
                except Exception as e:
                    print(e)
                    continue
                print(f"Payload = {payload} on connect users")

                user_conn = connected_sockets[username]
                connected_user = connected_users[username]
                response = "some response"
                opcode = 129
                response_frame = build_frame(response, opcode)
                connected_user.request.sendall(response_frame)

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
