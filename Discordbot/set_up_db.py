from pymongo import MongoClient
import config
import json
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017')
db = client['discord']
server = db.server
users = db.users

def get_data():
    with open('./data/db.json', "r") as json_file:
        data = json.load(json_file)

    tags = [] 
    for key, item in data['tags'].items():
        tags.append(item)

    admin_roles = []
    for key, item in data['admin_roles'].items():
        admin_roles.append(item)

    users = []
    for key, item in data['user_data'].items():
        users.append(item)

    return tags, admin_roles, users

tags, admin_roles, users = get_data()

refreshtime = datetime.utcnow() + timedelta(days=30)

server.insert_one(
    {'_id': 0}
)

server.update_one(
    {'_id': 0},
    {'$set': {
        'admin_roles': [],
        'welcome_channel_id': config.welcome_ch_id,
        'log_channel_id': config.log_channel_id,
        'stream_channel_id': config.stream_channel_id,
        'point_emote_id': config.point_emote_id,
        'mute_role_id': config.mute_role_id,
        'twitch': {
            'client_id': config.Client_id,
            'client_secret': config.Client_secret,
            'oauth2': config.Oauth2,
            'channel_id': config.user_id,
            'refresh': config.refresh,
            'refreshtime': refreshtime
        },
        'tags': tags,
        'unmute_queue': [],
        'unban_queue': []}
    },
)