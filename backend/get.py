from typing import Any
from backend.database import retrieve_chathistory
from database import *
import os ,random
import json
import hashlib
import base64

from generate_response import send_200, send_101, send_301
from filepaths import file_paths
from websocket import websocket_server

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



def index(self, received_data):
        file_path = file_paths(self)

        with open(file_path['index.html'], 'rb') as content:
            body = content.read()
        mimetype = 'text/html; charset=utf-8'
        length = os.path.getsize(file_path['index.html'])
        
        send_200(self, length, mimetype, body)



def websocket(self, received_data):
    username = "User" + str(random.randint(0, 1000))
    print('User: ' + username + ' has opened a websocket connection')
    key = received_data.split(b'Sec-WebSocket-Key: ')[1]
    key = key.split(b'\r\n')[0]
    key += (b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
    return_key = hashlib.sha1(key).digest()
    return_key = base64.b64encode(return_key)
    send_101(self, return_key)
    # with open("status.txt", 'w') as f:
    #     f.write("upgraded")
    # websocket_server(self, username)


# /chathistory
def chat(self, received_data):
    # Returns list of comments stored in the database
    chat_array = retrieve_chathistory(cursor, db)
    print(chat_array)
    json_array = json.dumps(chat_array)
    # content_length = len(json_array)
    # response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length:{content_length}\r\n\r\n{json_array}"
    # return response.encode()
    send_200(self, len(json_array), 'application/json', json_array.encode())
    # print('JSON Sent to User: ' + str(body))
    
    
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
    
    