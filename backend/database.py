import mysql.connector as mysql
import os
import json
import bcrypt

# This retrieves the environment variable from the docker compose file
user = os.getenv('DATABASE_USER')  # This is set to 'Felipe' in the docker compose file for now
password = os.getenv('DATABASE_PASSWORD')  # 'Gallardo'

# This connects us to the mysql container database
db = mysql.connect(
    host='mysql',
    user=user,
    passwd=password,
    database="CSE312-Project"
)
cursor = db.cursor(prepared=True)
# This create the table with an auto incremented id
# We can use the 'TEXT' type for string and 'BLOB' to store bytes
# This table is for chat history
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                    username TEXT,
                    json_message TEXT,
                    id INT AUTO_INCREMENT PRIMARY KEY)
                    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS registered_users (
                    username TEXT,
                    password BLOB,
                    color TEXT,
                    auth_token BLOB,
                    id INT AUTO_INCREMENT PRIMARY KEY)
                    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS images (
                    username TEXT,
                    image_path TEXT,
                    id INT AUTO_INCREMENT PRIMARY KEY)
                    """)

show_databases = "SHOW DATABASES"  # a query to return all databases
cursor.execute(show_databases)  # Should only display 'CSE312-Project'
databases = cursor.fetchall()
for database in databases:
    print(database)

cursor.close()
db.close()


def create_connection(buffered=False):
    new_database = mysql.connect(
        host='mysql',
        user=user,
        passwd=password,
        database="CSE312-Project"
    )
    if buffered:
        return new_database, new_database.cursor(prepared=True)

    return new_database, new_database.cursor(buffered=True)


def close_connection(close_db, close_cursor):
    close_cursor.close()
    close_db.close()


def insert_image(image_path, username):
    database, cursor = create_connection()
    print(f'\r\nInserting an image = {image_path} with username {username}')
    query = "INSERT INTO images (username, image_path) VALUES (%s, %s)"
    values = (username, image_path)
    cursor.execute(query, values)
    db.commit()

    close_connection(database, cursor)


# # for debugging purposes
# def retrieve_authenticated_users():
#     query = 'SELECT * FROM registered_users'
#     cursor.execute(query)
#     return cursor.fetchall()


def retrieve_images():
    database, cursor = create_connection(True)
    print('Loading user images...')
    query = "SELECT image_path FROM images"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        # print(f"Found color {a_user[0]}")
        close_connection(database, cursor)
        return row[0]
    print('returning falsy value')
    close_connection(database, cursor)
    return ''


def is_authenticated(token: bytes):
    database, cursor = create_connection(True)
    try:
        # query = 'SELECT username, auth_token FROM registered_users' # this query doesn't work as expected :(
        query = 'SELECT * FROM registered_users'
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        # print(f'Attempted to authenticate token = {token}. Got error {e}')
        return ''
    try:
        # print(f'all authenticated rows with token set are {rows}')
        for row in rows:
            username = row[0]
            color = row[2]
            hashed_token = row[3]

            print(f'Background Color: {color}')
            if isinstance(hashed_token, bytes) or isinstance(hashed_token, bytearray):
                #  print(f'checking user = {username} and stored token = {hashed_token}')
                if hashed_token is None:
                    continue
                if bcrypt.checkpw(token, hashed_token):
                    print(f'Found a match with user {username}')
                    close_connection(database, cursor)
                    return username

            else:
                # print(f'checking user = {username} and stored token = {hashed_token}')
                if hashed_token is None:
                    continue
                if bcrypt.checkpw(token, hashed_token.encode('utf8')):
                    post_token(username, token)
                    return username

    except Exception as e:
        # print(f'2. Attempted to authenticate token = {token}. Got error {e}')
        return ''
    # print(f'is_authenticated = false on token = {token}')
    close_connection(database, cursor)
    return ''


def post_token(username: str, token: bytes):
    try:
        db, cursor = create_connection(True)
        query = "UPDATE registered_users SET auth_token = %s WHERE username = %s"
        values = (token, username)
        # print(f"Setting values = {values} for username = {username}")
        cursor.execute(query, values)
        db.commit()
        close_connection(db, cursor)
    except Exception as e:
        # print(f"Attempted to update token on username = {username}")
        return


def change_color(username: str, color: str):
    db, cursor = create_connection(True)
    select_query = "SELECT * FROM registered_users WHERE username = %s"
    values = (username,)
    cursor.execute(select_query, values)
    is_present = len(cursor.fetchall())
    if is_present:
        print(f"Updating user info. is_present = {is_present}")
        query = "UPDATE registered_users SET color = %s WHERE username = %s"
        values = (color, username)
        cursor.execute(query, values)
        db.commit()
    close_connection(db, cursor)


def get_color(username):
    db, cursor = create_connection(True)
    color = "#cc0000"
    query = "SELECT color FROM registered_users WHERE username = %s"
    values = (username,)
    cursor.execute(query, values)
    all_users = cursor.fetchall()
    for a_user in all_users:
        print(f"Found color {a_user[0]}")
        close_connection(db, cursor)
        return a_user[0]
    print('returning default color')
    close_connection(db, cursor)
    return color


def authenticate_login(username: str, password, token):
    print('AUTHENTICATING LOGIN')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'token: {token}')
    try:
        db, cursor = create_connection(True)
        query = "SELECT password FROM registered_users WHERE username = %s"
        values = (username,)
        cursor.execute(query, values)
        row = cursor.fetchone()
        if row:
            stored_password = row[0]
            # print(f'Stored Password: {stored_password}')

            if (isinstance(stored_password, bytes) or isinstance(stored_password, bytearray)):
                if bcrypt.checkpw(password, stored_password):
                    post_token(username, token)
                    return True
                else:
                    return False
            else:
                if bcrypt.checkpw(password, str(stored_password).encode()):
                    post_token(username, token)
                    return True
                else:
                    return False
        else:
            return False
    except Exception as e:
        print(f"Attempted to authenticate user. Got error {e}")
        return False


# Register a user and store a hash of their password on the database
# password parameter is assumed to already be hashed
# If a username is already present in the database then simply update the password
def register_user(username: str, password: bytes):
    db, cursor = create_connection(True)
    select_query = "SELECT * FROM registered_users WHERE username = (%s)"
    values = (username,)
    cursor.execute(select_query, values)
    is_present = len(cursor.fetchall())
    if is_present:
        print(f"Updating user info. is_present = {is_present}")
        query = "UPDATE registered_users SET password = %s WHERE username = %s"
        values = (username, password)
        cursor.execute(query, values)
        db.commit()

    else:
        try:
            # print(f"Insert a new user. username = {username} and pass = {password}")
            query = "INSERT INTO registered_users (username, password, color, auth_token) VALUES (%s, %s, %s, %s)"
            values = (username, password, "white", b'')
            cursor.execute(query, values)
            db.commit()
        except Exception as e:
            print(f"Attempted to insert a user. Got error {e}")


# Add a user to the users table
# {messageType, username, comment}
def add_user(user_name: str, message: str):
    db, cursor = create_connection(True)
    query = "INSERT INTO users (username, json_message) VALUES (%s, %s)"
    values = (user_name, message)
    cursor.execute(query, values)
    db.commit()
    close_connection(db, cursor)


# all users and their unique ids in a list
def retrieve_users():
    db, cursor = create_connection(True)
    query = "SELECT * FROM users"
    cursor.execute(query)
    all_users = cursor.fetchall()
    user_array = []
    for a_user in all_users:
        # message_type = user[0]
        user_name = a_user[0]
        color = a_user[1]
        user_message = a_user[2]
        user_id = a_user[3]
        print(f'Retrieving user {a_user} with color: {color}')
        user_array.append((user_name, user_message, color, user_id))
    close_connection(db, cursor)
    return user_array


def retrieve_chathistory():
    db, cursor = create_connection(True)
    try:
        query = "SELECT json_message FROM users"
        cursor.execute(query)
        all_users = cursor.fetchall()
        json_messages = []
        for a_user in all_users:
            message = json.loads(a_user[0])
            json_messages.append(message)
        close_connection(db, cursor)
        return json_messages
    except Exception as e:
        print(f'\r\nGot error {e} in retrieve_chathistory')
        return []
