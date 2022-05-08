from typing import Any
# from database import retrieve_chathistory
from backend.database import *
import os, random
import json
import hashlib
import base64
import secrets
import bcrypt
import sys

from generate_response import *
from filepaths import file_paths
from backend.template_engine import *
from backend.parsers import parse_request

ws_users = {}

# DEAL WITH ONLY GET REQUESTS


def handle_get(self, received_data):
    path = ((received_data.split(b'\r\n')[0]).split(b' ')[1]).decode()
    print("path is: " + str(path))

    if path == '/':
        index(self, received_data)

    elif path == '/login' or path == '/logged_in':
        # (self, received_data)
        send_404(self)
        
    elif path == '/signup_log':
        send_301(self, 'http://localhost:8080/signin')


    elif path == '/signin':
        signin(self)

    elif path == '/signup':
        signup(self)

    elif path == '/websocket':
        websocket(self, received_data)

    elif path == '/chat-history':
        chat(self, received_data)

    elif path == '/functions.js':
        javascript(self)

    elif path == '/Chess/ChessEngine.js':
        chess_engine(self)


    elif '.css' in path:
        style(self, received_data)


    elif '/image/' in path:
        image(self, path)

    elif '/favicon' in path:
        favicon(self, path)
    else:
        print('Unrecognized Request, sending 404')


def index(self, received_data: bytes):
    file_path = file_paths(self)
    with open(file_path['index.html'], 'rb') as content:
        body = content.read()
    mimetype = 'text/html; charset=utf-8'
    length = os.path.getsize(file_path['index.html'])

    if 'Cookie' in str(received_data):
        print(str(received_data))
        cookie = received_data.split(b'Cookie: ')[1].split(b'\r\n')[0]
        cookie = cookie.decode()
        print('Recieved Cookie: ' + str(cookie))
        new_cookie = int(cookie)
        new_cookie += 1
        decoded = body.decode()
        decoded = decoded.replace('{{cookie}}', str(new_cookie))
        body = decoded.encode()
        send_200_with_cookie(self, length, mimetype, body, new_cookie)
    else:
        cookie = 1
        decoded = body.decode()
        decoded = decoded.replace('{{cookie}}', str(cookie))
        body = decoded.encode()
        send_200_with_cookie(self, length, mimetype, body, cookie)


# Displayes singin from with generated token
def signin(tcp_handler):
    print('SIGN IN IS BEING CALLED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    sys.stdout.flush()
    sys.stderr.flush()
    # generate token
    token = secrets.token_urlsafe(32)
    tcp_handler.valid_tokens.append(token)
    # store token and replace in html
    file_path = file_paths(tcp_handler)
    with open(file_path['signin.html'], 'rb') as content:
        body = content.read()

    # template_data = {'token', token}
    # body = render_template(file_path['signin.html'], template_data)
    decoded = body.decode()
    decoded = decoded.replace('{{token}}', token)
    # decoded = decoded.replace('{{auth_token}}', auth_token)
    body = decoded.encode()
    mimetype = 'text/html; charset=utf-8'
    length = len(body)
    send_200(tcp_handler, length, mimetype, body)


# Displays signup from with generated token
def signup(tcp_handler):
    # generate token
    token = secrets.token_urlsafe(32)
    tcp_handler.valid_tokens.append(token)
    # store token and replace in html
    file_path = file_paths(tcp_handler)
    with open(file_path['signup.html'], 'rb') as content:
        body = content.read()
    decoded = body.decode()
    decoded = decoded.replace('{{token}}', token)
    body = decoded.encode()

    mimetype = 'text/html; charset=utf-8'
    length = len(body)

    send_200(tcp_handler, length, mimetype, body)


def websocket(self, received_data):
    path, headers, content = parse_request(received_data)
    set_cookies = list(filter(lambda tuple_val: tuple_val[0] == b'Cookie', headers))
    
    authenticated = ''
    if set_cookies:
        header_content_list = set_cookies[0][1].split(b';')
        for directive in header_content_list:
            if b'=' not in directive:
                continue
            directive_name, directive_content = directive.split(b'=')
            directive_name = directive_name.strip()
            if directive_name == b'homepage_cookie':
                visits = int(directive_content.strip()) + 1
            elif directive_name == b'user':
                user_token = directive_content.strip()
                authenticated = is_authenticated(self.db, self.cursor, user_token)  # Check query token with hash
    # authenticated is the username
    if authenticated:
        ws_users[authenticated] = self
        username = "User" + str(random.randint(0, 1000))
        print('User: ' + username + ' has opened a websocket connection')
        key = received_data.split(b'Sec-WebSocket-Key: ')[1]
        key = key.split(b'\r\n')[0]
        key += (b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
        return_key = hashlib.sha1(key).digest()
        return_key = base64.b64encode(return_key)
        send_101(self, return_key)


def chat(self, received_data):
    # Returns list of comments stored in the database
    chat_array = retrieve_chathistory(cursor, db)
    print(f"\r\nCurrent chat history are {chat_array}\r\n")
    json_array = json.dumps(chat_array)
    send_200(self, len(json_array), 'application/json', json_array.encode())


#   path = '/functions.js'
def javascript(self):
    mimetype = 'application/javascript; charset=utf-8'
    file_path = file_paths(self)
    filename = str(file_path["functions.js"])
    body = ''

    with open(filename, 'rb') as content:
        body = content.read()

    # print(body.decode())
    send_200(self, len(body), mimetype, body)


# path = '/Chess/ChessEngine.js'
def chess_engine(self):
    mimetype = 'application/javascript; charset=utf-8'
    file_path = file_paths(self)
    filename = str(file_path["/Chess/ChessEngine.js"])
    body = ''
    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, len(body), mimetype, body)


def style(self, received_data):
    # Get correct filepath
    file_path = file_paths(self)
    if 'signin' in str(received_data):
        filename = file_path['signin.css']
    elif 'signup' in str(received_data):
        filename = file_path['signup.css']
    else:
        filename = file_path['style.css']

    mimetype = 'text/css; charset=utf-8'

    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, len(body), mimetype, body)


def image(self, path):
    mimetype = 'image/jpeg'
    folder_path = file_paths(self)
    complete_path = path
    path = path.split('/')[2]

    filename = ''
    if complete_path.startswith('/frontend/'):
        filename = '/root' + complete_path
    elif complete_path.startswith('/image/'):
        filename = str(folder_path["imagefolder"]) + path
    len = str(os.path.getsize(filename))

    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, len, mimetype, body)


def favicon(self, path):
    mimetype = 'image/x-icon'
    folder_path = file_paths(self)
    filename = str(folder_path["favicon"])
    length = str(os.path.getsize(filename))

    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, length, mimetype, body)
