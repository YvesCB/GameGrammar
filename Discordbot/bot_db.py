from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['discord']
server = db.server
users = db.users

def server_update (action, filter={}, incr_value=1, incr_index='', list_name='', pull_dict={}, new_value=None):
    result = None
    if action == 'insert':
        result = server.insert_one(
            new_value
        )
    elif action == 'update':
        result = server.update_one(
            filter,
            {'$set': new_value},
        )
    elif action == 'increment':
        result = server.update_one(
            filter,
            {'$inc': {incr_index: incr_value}}
        )
    elif action == 'delete':
        result = server.delete_one(
            filter
        )
    elif action == 'push':
        if list_name not in list(server.find_one().keys()):
            server.insert_one(
                {list_name: [new_value]}
            )
        result = server.update_one(
            filter,
            {'$push': {list_name: new_value}}
        )
    elif action == 'pull':
        result = server.update_one(
            filter,
            {'$pull': {list_name: pull_dict}}
        )
    return result

def server_get (filter={}, project={'_id': 0}):
    result = server.find_one(
        filter,
        project
    )
    if project != {'_id': 0} and len(result) != 0:
        return list(result.values())[0][0]
    return result

def user_update (action, filter={}, incr_value=1, incr_index='', list_name='', pull_dict={}, new_value=None):
    result = None
    if action == 'insert':
        result = users.insert_one(
            new_value
        )
    elif action == 'update':
        result = users.update_one(
            filter,
            {'$set': new_value}
        )
    elif action == 'increment':
        result = users.update_one(
            filter,
            {'$inc': {incr_index: incr_value}}
        )
    elif action == 'delete':
        result = users.delete_one(
            filter
        )
    elif action == 'push':
        if list_name not in list(users.find_one().keys()):
            server.insert_one(
                {list_name: [new_value]}
            )
        result = users.update_one(
            filter,
            {'$push': {list_name: new_value}}
        )
    elif action == 'pull':
        result = users.update_one(
            filter,
            {'$pull': {list_name: pull_dict}}
        )
    return result

def user_get (filter={}, project={'_id': 0}):
    result = users.find_one(
        filter,
        project
    )
    if project != {'_id': 0} and len(result) != 0:
        return list(result.values())[0][0]
    return result

def user_get_all():
    result = users.find()
    return result

def user_new (user_id, user_name):
    user_update('insert', new_value={
        '_id': user_id,
        'name': user_name,
        'point_amount': 0,
        'warnings': [],
        'mutes': [],
        'bans': []
        })
    return users.find_one({'_id': user_id})