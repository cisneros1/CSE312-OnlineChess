import mysql.connector as mysql
import os

# This retrieves the environment variable from the docker compose file
user = os.getenv('DATABASE_USER')   # This is set to 'Felipe' in the docker compose file for now
password = os.getenv('DATABASE_PASSWORD')   # 'Gallardo'
# This connects us to the mysql container database
db = mysql.connect(
    host='mysql',
    user=user,
    passwd=password,
    database="CSE312-Project"
)
cursor = db.cursor(prepared=True)
# This create the table with an auto incremented id
# We can use the 'TEXT' type for string and 'BLOB' to store bytes (for images)
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                    username TEXT,
                    json_message TEXT,
                    id INT AUTO_INCREMENT PRIMARY KEY)
                    """)

show_databases = "SHOW DATABASES"   # a query to return all databases
cursor.execute(show_databases)  # Should only display 'CSE312-Project'
databases = cursor.fetchall()
for database in databases:
    print(database)

# Add a user to the users table
# {messageType, username, comment}
def add_user(user_name: str, message:str, cursor, db):
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
        #message_type = user[0]
        user_name = user[0]
        user_message = user[1]
        user_id = user[2]
        user_array.append((user_name, user_message, user_id))
    return user_array

def retrieve_chathistory(cursor, db):
    query = "SELECT json_message from users"
    cursor.execute(query)
    all_users = []
    user_array = []
    for user in all_users:
        message = user[0]
        user_array.append(message)
    return user_array
