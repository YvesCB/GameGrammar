from tinydb import TinyDB, Query, operations

db = TinyDB('./data/db.json')
db_tags = db.table('tags')
db_admin_roles = db.table('admin_roles')
db_user_roles = db.table('user_roles')
db_user_data = db.table('user_data')
db_voice_text = db.table('voice_text')

# functions for tag db
def get_tag(name):
    Tag = Query()
    tags = db_tags.search(Tag.name == name)
    if len(tags) > 0:
        return tags[0]
    else:
        return None


def exists_tag(name):
    tag = get_tag(name)
    return tag is not None


def get_all_tags():
    return db_tags.all()


def add_tag(name, response):
    db_tags.insert({'name': name, 'response': response})


def remove_tag(name):
    Tag = Query()
    return db_tags.remove(Tag.name == name)

# functions for admin role db
def get_admin_role(name):
    Admin_role = Query()
    admins = db_admin_roles.search(Admin_role.name == name)
    if len(admins) > 0:
        return admins[0]
    else:
        return None


def exists_admin_role(name):
    admin_role = get_admin_role(name)
    return admin_role is not None
    

def get_all_admin_roles():
    return db_admin_roles.all()


def add_admin_role(name):
    db_admin_roles.insert({'name': name})


def remove_admin_role(name):
    Admin_role = Query()
    return db_admin_roles.remove(Admin_role.name == name)

# functions for user assignable roles db
def get_user_role(name):
    User_role = Query()
    roles = db_user_roles.search(User_role.name == name)
    if len(roles) > 0:
        return roles[0]
    else:
        return None


def exists_user_role(name):
    user_role = get_user_role(name)
    return user_role is not None


def get_all_user_roles():
    return db_user_roles.all()


def add_user_role(name):
    db_user_roles.insert({'name': name})


def remove_user_role(name):
    User_role = Query()
    return db_user_roles.remove(User_role.name == name)

# functions for user points
def get_user_points(user_id):
    User_data = Query()
    points = db_user_data.search(User_data.id == user_id)
    if len(points) > 0:
        return points[0]
    else:
        db_user_data.insert({'id': user_id, 'point_amount': 0, 'warnings': [], 'mutes': []})
        points = db_user_data.search(User_data.id == user_id)
        return points[0]


def user_points_upsert(user_id, incrdecr):
    User_data = Query()
    points = db_user_data.search(User_data.id == user_id)
    if len(points) > 0 and incrdecr == 'incr':
        db_user_data.update(operations.increment('point_amount'), User_data.id == user_id)
    elif len(points) > 0 and incrdecr == 'decr':
        db_user_data.update(operations.decrement('point_amount'), User_data.id == user_id)
    else:
        db_user_data.insert({'id': user_id, 'point_amount': 1, 'warnings': [], 'mutes': []})


def user_points_update(user_id, point_amount):
    User_data = Query()
    points = db_user_data.search(User_data.id == user_id)
    if len(points) > 0:
        db_user_data.update(operations.set('point_amount', point_amount), User_data.id == user_id)
        print(f'Updated {user_id}')
    elif len(points) == 0 and point_amount > 0:
        db_user_data.insert({'id': user_id, 'point_amount': point_amount, 'warnings': [], 'mutes': []})
        print(f'Inserted {user_id}')


def get_all_user_points():
    return db_user_data.all()

# functions for user warns and mutes
def get_user_warnings(user_id):
    User_warns = Query()
    warns = db_user_data.search(User_warns.id == user_id)
    if len(warns) > 0:
        return warns[0]['warnings']
    else:
        return None


def add_warning(user_id, warning):
    User_data = Query()
    warns = db_user_data.search(User_data.id == user_id)
    warnings = [warning]
    if len(warns) > 0:
        warnings.extend(warns[0]['warnings'])
        db_user_data.update(operations.set('warnings', warnings), User_data.id == user_id)
    else:
        db_user_data.insert({'id': user_id, 'point_amount': 0, 'warnings': warnings, 'mutes': []})


def remove_warning(user_id, warning_number):
    User_data = Query()
    warns = db_user_data.search(User_data.id == user_id)
    if len(warns) > 0:
        warns = warns[0]['warnings']
        if len(warns) >= warning_number:
            del warns[warning_number - 1]
            db_user_data.update(operations.set('warnings', warns), User_data.id == user_id)
            return True
        else:
            return False
    else:
        return False


# Voice/text db
def get_voice_text(voice_id):
    Voice_text = Query()
    voice_text_entry = db_voice_text.search(Voice_text.vc_id == voice_id)
    if len(voice_text_entry) > 0:
        return voice_text_entry[0]
    else:
        return None
    

def exists_voice_text(voice_id):
    voice_text_entry = get_voice_text(voice_id)
    return voice_text_entry is not None


def get_all_voice_text():
    return db_voice_text.all()


def add_voice_text(voice_id, text_id, role_id):
    db_voice_text.insert({'vc_id': voice_id, 'tc_id': text_id, 'r_id': role_id})


def remove_voic_text(vocie_id):
    Voice_text = Query()
    return db_voice_text.remove(Voice_text.vc_id == vocie_id)