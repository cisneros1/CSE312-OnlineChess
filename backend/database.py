import pymongo
import mysql.connector as mysql
import os

mongo_client = pymongo.MongoClient('mongo')
db = mongo_client["312project"]

users_collection = db["users"]
users_id_collection = db["users_id"]

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
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      email TEXT,
                      username TEXT,
                      deleted TEXT)
                      """)

show_databases = "SHOW DATABASES"
cursor.execute(show_databases)  # Should only display 'CSE312-Project'
databases = cursor.fetchall()
for database in databases:
    print(database)



def get_next_id():
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1


def create(user_dict):
    users_collection.insert_one(user_dict)
    user_dict.pop("id")


def list_all():
    # Get all values except for id
    all_users = users_collection.find({})  # , {"_id": 0})
    return list(all_users)


