import backend.database as db
import secrets
import bcrypt
from template_engine import *
from generate_response import *
from filepaths import *


def handle_post(tcp_handler, received_data):
    print('POST DATA: ' + str(received_data))
    path = ((received_data.split(b'\r\n')[0]).split(b' ')[1]).decode()
    print('POST Request for: ' + str(path))

    if 'logi' in str(path):
        login(tcp_handler, received_data)
    elif 'signup_log' in str(path):
        signup(tcp_handler, received_data)
    elif 'chat' in str(path):
        chat(tcp_handler, received_data)
    else:
        print('Unrecognized Post Request, sending 404')
        send_404(tcp_handler)
        
        

# This function is not called
def chat(tcp_handler, received_data: bytes):
    # At this point user has been checked
    print('chat')
    username = ""
    comment = escape_html(received_data.split(b'name="comment"\r\n\r\n')[
        1].split(b'\r\n')[0].decode())
    token = escape_html(received_data.split(b'name="xsrf_token"\r\n\r\n')[
                        1].split(b'\r\n')[0].decode())

    is_token_valid: bool = False
    for t in tcp_handler.valid_tokens:
        if t == token:
            is_token_valid = True
            print('Token is valid')

    if is_token_valid:
        # check database for username and password
        for user in tcp_handler.usernames:
            if len(user) > 0:
                username = user
        print('USER FOR COMMENT: ' + str(username))
        # store
        id = db.get_comment_id()
        entry = {'_id': id, 'messageType': 'chatMessage',
                 'username': username, 'comment': comment}
        db.insert_comment(entry)
        send_201(tcp_handler)
    else:
        print('404 in chat')
        send_404(tcp_handler)


def login(tcp_handler, received_data: bytes):
    print('-------------------------')
    token = escape_html(received_data.split(b'name="xsrf_token"\r\n\r\n')[
                        1].split(b'\r\n')[0].decode())
    username = escape_html(received_data.split(b'name="username"\r\n\r\n')[
                           1].split(b'\r\n')[0].decode())
    password = escape_html(received_data.split(b'name="password"\r\n\r\n')[
                           1].split(b'\r\n')[0].decode())
    cookie = escape_html(received_data.split(b'Cookie: ')
                         [1].split(b'\r\n')[0].decode())
    print('Token: ' + token)
    print('Username: ' + username)
    print('password: ' + password)
    print('Cookie:' + cookie)
    # Check if token is valid
    is_token_valid: bool = False

    for t in tcp_handler.valid_tokens:
        if t == token:
            is_token_valid = True
            print('Token is valid')

    if is_token_valid:
        # check database for username and password
        json_users = (db.list_all()).copy()
        print(json_users)
        # print('List is: ' + str(json_users))
        userfound = False
        for json_dict in json_users:
            if username == json_dict['username']:
                encoded_pwd = password.encode()
                hashed = bcrypt.hashpw(encoded_pwd, json_dict['salt'])
                print('Comparing: ' + str(encoded_pwd) + ' with ' + str(hashed))
                if bcrypt.checkpw(json_dict['password'].encode(), hashed):
                    userfound = True
                    print('User has been found in the database')
        if userfound == False:
            print('That user does not exist')
            send_404(tcp_handler)
        else:
            tcp_handler.usernames.append(username)
            new_token = secrets.token_urlsafe(32)
            tcp_handler.valid_tokens.append(new_token)

            file_path = file_paths(tcp_handler)
            with open(file_path['logged_in.html'], 'rb') as content:
                body = content.read()
            decoded = body.decode()
            decoded = decoded.replace('{{token}}', new_token)
            decoded = decoded.replace('{{username}}', username)

            if 'Cookie' in str(received_data):
                print(str(received_data))
                cookie = received_data.split(b'Cookie: ')[1].split(b'\r\n')[0]
                cookie = cookie.decode()
                print('Recieved Cookie: ' + str(cookie))
                new_cookie = int(cookie)
                new_cookie += 1
                decoded = decoded.replace('{{cookie}}', str(new_cookie))
                body = decoded.encode()
                mimetype = 'text/html; charset=utf-8'
                length = len(body)
                send_200_with_cookie(tcp_handler, length,
                                     mimetype, body, new_cookie)
            else:
                cookie = 1
                decoded = decoded.replace('{{cookie}}', cookie)
                body = decoded.encode()
                mimetype = 'text/html; charset=utf-8'
                length = len(body)
                send_200_with_cookie(tcp_handler, length,
                                     mimetype, body, cookie)

    else:
        send_404(tcp_handler)
        print('404 has been sent')


def signup(tcp_handler, received_data):
    print('-------------------------')
    token = escape_html(received_data.split(b'name="xsrf_token"\r\n\r\n')[
                        1].split(b'\r\n')[0].decode())
    username = escape_html(received_data.split(b'name="username"\r\n\r\n')[
                           1].split(b'\r\n')[0].decode())
    password = escape_html(received_data.split(b'name="password"\r\n\r\n')[
                           1].split(b'\r\n')[0].decode())
    cookie = escape_html(received_data.split(b'Cookie: ')
                         [1].split(b'\r\n')[0].decode())
    print('Token: ' + token)
    print('Username: ' + username)
    print('password: ' + password)
    print('Cookie:' + cookie)
    # Check if token is valid
    is_token_valid: bool = False

    for t in tcp_handler.valid_tokens:
        if t == token:
            is_token_valid = True
            print('Token is valid')

    if is_token_valid:
        # check password requirements
        print('Hasing and Storing password...')
        encoded_pwd = password.encode()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(encoded_pwd, salt)
        print(salt)
        print(hashed)
        # store user
        id = db.get_next_id()
        user_dict = {"_id": id, "username": username,
                     "password": password, "salt": salt}
        db.insert(user_dict)
        print('The following has been assed to users: ' + str(user_dict))

        new_token = secrets.token_urlsafe(32)
        tcp_handler.valid_tokens.append(new_token)
        file_path = file_paths(tcp_handler)

        with open(file_path['logged_in.html'], 'rb') as content:
            body = content.read()
        decoded = body.decode()
        decoded = decoded.replace('{{token}}', new_token)
        body = decoded.encode()
        mimetype = 'text/html; charset=utf-8'
        length = len(body)

        if 'Cookie' in str(received_data):
            print(str(received_data))
            cookie = received_data.split(b'Cookie: ')[1].split(b'\r\n')[0]
            cookie = cookie.decode()
            print('Recieved Cookie: ' + str(cookie))
            new_cookie = int(cookie)
            new_cookie += 1
            send_200_with_cookie(tcp_handler, length,
                                 mimetype, body, new_cookie)
        else:
            cookie = 1
            send_200_with_cookie(tcp_handler, length, mimetype, body, cookie)

    else:
        send_404(tcp_handler)
