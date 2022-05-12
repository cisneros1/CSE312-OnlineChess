# import backend.database as db
from backend.database import *
import secrets
import bcrypt
# from template_engine import *
from backend.template_engine import *
from backend.generate_response import *
from backend.filepaths import *
from stored_users import *


def handle_post(tcp_handler, received_data):
    # print('POST DATA: ' + str(received_data))
    path = ((received_data.split(b'\r\n')[0]).split(b' ')[1]).decode().strip()
    print('POST Request for: ' + str(path))

    if 'login' in str(path):
        login(tcp_handler, received_data)

    elif path == '/signup_log':
        print(str(received_data))
        signup(tcp_handler, received_data)

    elif 'chat' in str(path):
        chat(tcp_handler, received_data)

    # elif path.startswith('/send_dm'):
    #     direct_message(tcp_handler, received_data, path)

    elif 'challenge' in str(path):
        challenge(tcp_handler, received_data, path)

    else:
        print('Unrecognized Post Request, sending 404')
        send_404(tcp_handler)


def direct_message(tcp_handler, received_data: bytes, path: str):
    username = path.split('_')[1].split('_')[1]
    print(f'User receiving dm from {username}')


def challenge(self, received_data: bytes, path: str):
    file_path = file_paths(self)
    # parse the entire path first
    challenger = path.split('_')[1].split('_')[0]
    acceptor = path.split('_')[1].split('_')[1]
    print(f'Challenger: {challenger}, Acceptor: {acceptor}')

    with open(file_path['game.html', 'rb']) as content:
        body = content.read()
    length = len(body)
    mimetype = 'text/html; charset=utf-8'
    send_200(self, length, mimetype, body)


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


# /login
def login(tcp_handler, received_data: bytes):
    print('----------- post login --------------')
    # token = received_data.split(b'name="xsrf_token"\r\n\r\n')[1].split(b'\r\n')[0].strip()
    username = received_data.split(b'name="username"\r\n\r\n')[1].split(b'\r\n')[0].decode().strip()
    password = received_data.split(b'name="password"\r\n\r\n')[1].split(b'\r\n')[0].decode()
    color = received_data.split(b'name="color"\r\n\r\n')[1].split(b'\r\n')[0].decode()

    # print('Token: ' + token)
    print('Username: ' + username)
    print('password: ' + password)
    print(f'Color: {color}')

    auth_token: str = secrets.token_hex(nbytes=80)
    auth_token_hashed: bytes = bcrypt.hashpw(auth_token.encode('utf8'), (bcrypt.gensalt()))
    user_found: bool = authenticate_login(db, cursor, username, password.encode('utf8'), auth_token_hashed)

    if not user_found:
        print('That user does not exist')
        send_301(tcp_handler, '/')
    else:
        # if user found
        authenticated_users[username] = auth_token  # Save user to global hashmap of users
        # print(f'Authenticated users are {authenticated_users}')
        tcp_handler.usernames.append(username)

        if color != '#ffffff':
            change_color(db, cursor, username, color)

        new_token = secrets.token_urlsafe(32)
        tcp_handler.valid_tokens.append(new_token)

        # TODO - find a way to handle disconnects
        auth_users = []
        for auth_user in authenticated_users.keys():
            auth_users.append({'logged_in_user': auth_user})
        template_dict = {'username': username, 'loop_data': auth_users}

        file_path = file_paths(tcp_handler)

        print('Sending Auth Token: ' + str(auth_token))
        send_301_with_token(tcp_handler, '/', auth_token)
        # send_200_with_authtoken(tcp_handler, length, mimetype, body, auth_token)

    # else:
    #     send_404(tcp_handler)
    #     print('404 has been sent')


def signup(tcp_handler, received_data):
    print('------------ post /signup_log -------------')
    token = received_data.split(b'name="xsrf_token"\r\n\r\n')[
        1].split(b'\r\n')[0].decode()
    username = received_data.split(b'name="username"\r\n\r\n')[
        1].split(b'\r\n')[0].decode()
    password = received_data.split(b'name="password"\r\n\r\n')[1].split(b'\r\n')[0].decode()
    # cookie = received_data.split(b'Cookie: ')[1].split(b'\r\n')[0].decode()
    print('Token: ' + token)
    print('Username: ' + username)
    print('password: ' + password)
    # print('Cookie:' + cookie)
    # Check if token is valid
    is_token_valid: bool = False

    for t in tcp_handler.valid_tokens:
        if t == token:
            is_token_valid = True
            print('Token is valid')

    if is_token_valid:
        # check password requirements
        if username and password:
            hashed_password: bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            print(f'HASED_PWD: {hashed_password}')

            register_user(db, cursor, username, hashed_password)

        send_301(tcp_handler, 'http://localhost:8080/signin')
        print('REDIRECT WAS SENT')


    else:
        send_404(tcp_handler)
