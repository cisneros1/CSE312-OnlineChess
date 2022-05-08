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
                    auth_token BLOB,
                    id INT AUTO_INCREMENT PRIMARY KEY)
                    """)

show_databases = "SHOW DATABASES"  # a query to return all databases
cursor.execute(show_databases)  # Should only display 'CSE312-Project'
databases = cursor.fetchall()
for database in databases:
    print(database)


def is_authenticated(db, cursor, token):
    query = 'SELECT username, auth_token FROM registered_users'
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f'authenticating random token = {token}')
    for row in rows:
        username = row[0]
        hashed_token = row[1]
        if hashed_token is None:
            continue
        if bcrypt.checkpw(token, hashed_token):
            return username

    return ''


def post_token(db, cursor, username, token):
    query = "UPDATE registered_users SET auth_token = %s WHERE username = %s"
    values = (token, username)
    cursor.execute(query, values)
    db.commit()


def authenticate_login(db, cursor, username, password, token):
    try:
        query = "SELECT password FROM registered_users WHERE username = %s"
        values = (username,)
        cursor.execute(query, values)
        row = cursor.fetchone()
        if row:
            stored_password = row[0]
            if bcrypt.checkpw((password.encode()), (stored_password.encode())):
                post_token(db, cursor, username, token)
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
def register_user(db, cursor, username, password):
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
        print(f"Insert a new user. username = {username} and pass = {password}")
        query = "INSERT INTO registered_users (username, password) VALUES (%s, %s)"
        values = (username, password)
        cursor.execute(query, values)
        db.commit()


# Add a user to the users table
# {messageType, username, comment}
def add_user(user_name: str, message: str, cursor, db):
    query = "INSERT INTO users (username, json_message) VALUES (%s, %s)"
    values = (user_name, message)
    cursor.execute(query, values)
    db.commit()


# all users and their unique ids in a list
def retrieve_users(cursor, db):
    query = "SELECT * FROM users"
    cursor.execute(query)
    all_users = cursor.fetchall()
    user_array = []
    for user in all_users:
        # message_type = user[0]
        user_name = user[0]
        user_message = user[1]
        user_id = user[2]
        user_array.append((user_name, user_message, user_id))
    return user_array


def retrieve_chathistory(cursor, db):
    query = "SELECT json_message from users"
    cursor.execute(query)
    all_users = cursor.fetchall()
    json_messages = []
    for user in all_users:
        message = json.loads(user[0])
        json_messages.append(message)
    return json_messages
