from typing import Any
import backend.database as db
import os, random, json, hashlib, base64

from template_engine import render_template
from generate_response import send_200, send_101
from filepaths import file_paths
from websocket import ws_server

# DEAL WITH ONLY GET REQUESTS


def handle_get(self, received_data):
    path = ((received_data.split(b'\r\n')[0]).split(b' ')[1]).decode()

    if path == '/':
        index(self, received_data)

    elif path == '/websocket':
        websocket(self, received_data)

    elif path == '/chat-history':
        chat(self, received_data)

    elif path == '/functions.js':
        javascript(self)

    elif path == '/style.css':
        style(self)

    elif '/image/' in path:
        image(self, path)

    elif '/favicon' in path:
        favicon(self, path)
    else:
        print('Unrecognized Request, sending 404')
        # 404 here


def index(self, received_data):
    file_path = file_paths(self)

    with open(file_path['index.html'], 'rb') as content:
        body = content.read()
    mimetype = 'text/html; charset=utf-8'
    length = os.path.getsize(file_path['index.html'])

    send_200(self, length, mimetype, body)


def websocket(self, received_data):
    # Generate user name
    # Get websocket key
    # Append 258EAFA5-E914-47DA-95CA-C5AB0DC85B11
    # Return sha1 digest
    # base 64 encode it 
    # send 101
    # enter webocket server
    print('Websocket received')
    


def chat(self, received_data):
    # Get list of users in sqlite database
    # Create list of json containing each in format {"username": ["username"], "comment": ["comment"]}
    # encode list and send 200 
    # AJAX weill be in charge of html placement
    print('/get-history request was receieved')
    


def javascript(self):
    mimetype = 'application/javascript; charset=utf-8'
    file_path = file_paths(self)
    filename = str(file_path["functions.js"])
    body = ''

    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, len(body), mimetype, body)


def style(self):
    mimetype = 'text/css; charset=utf-8'
    file_path = file_paths(self)
    filename = str(file_path["style.css"])
    body = ''

    with open(filename, 'rb') as content:
        body = content.read()

    send_200(self, len(body), mimetype, body)


def image(self, path):
    mimetype = 'image/jpeg'
    folder_path = file_paths(self)
    path = path.split('/')[2]
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
