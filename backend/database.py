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
                      message TEXT,
                      id INT AUTO_INCREMENT PRIMARY KEY)
                      """)

show_databases = "SHOW DATABASES"
cursor.execute(show_databases)  # Should only display 'CSE312-Project'
databases = cursor.fetchall()
for database in databases:
    print(database)

# Add a user to the users table
def add_user(user_name: str, message:str, cursor, db):
    query = "INSERT INTO users (username, message) VALUES (%s, %s)"
    values = (user_name, message)
    cursor.execute(query, values)
    db.commit()


