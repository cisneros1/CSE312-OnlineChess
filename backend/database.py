import pymongo

mongo_client = pymongo.MongoClient('mongo')
db = mongo_client["312project"]

users_collection = db["users"]
users_id_collection = db["users_id"]


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


