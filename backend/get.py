import database as db
import os
import json
import hashlib
import base64

from template_engine import render_template
from generate_response import send_200, send_101
from filepaths import file_paths


def hangle_get(received_data):
    print("In handle get method")
    import database as db


def handle_get(self, received_data):
    path = ((received_data.split(b'\r\n')[0]).split(b' ')[1]).decode()
    print("Processing Get Request of path: " + str(path))

    if path == '/':
        file_path = file_paths(self)
        
        messages = [{"username": "Jim", "message": "Hello my name is Jim"},
                    {"username": "Mike", "message": "Hello my name is Mike"}]
        
        content = render_template(file_path["index.html"],
                                    {"image_name": "Eagle!",
                                    "image_filename": '"' + "image/flamingo.jpg" + '"',
                                    "token": str(self.token),
                                    "loop_data": messages})

        
        mimetype = 'text/html; charset=utf-8'
        send_200(self, len(content), mimetype, content.encode())

    elif path == '/functions.js':
        javascript(self)

    elif path == '/style.css':
        style(self)

    elif '/image/' in path:
        image(self, path)


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




