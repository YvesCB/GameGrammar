from tinydb import TinyDB, Query, operations

db = TinyDB('./data/db.json')
db_tags = db.table('tags')
db_admin_roles = db.table('admin_roles')
db_user_roles = db.table('user_roles')
db_user_points = db.table('user_points')

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
    User_points = Query()
    points = db_user_points.search(User_points.id == user_id)
    if len(points) > 0:
        return points[0]
    else:
        db_user_points.insert({'id': user_id, 'amount': 0})
        points = db_user_points.search(User_points.id == user_id)
        return points[0]


def user_points_upsert(user_id, incrdecr):
    User_points = Query()
    points = db_user_points.search(User_points.id == user_id)
    if len(points) > 0 and incrdecr == 'incr':
        db_user_points.update(operations.increment('amount'), User_points.id == user_id)
    elif len(points) > 0 and incrdecr == 'decr':
        db_user_points.update(operations.decrement('amount'), User_points.id == user_id)
    else:
        db_user_points.insert({'id': user_id, 'amount': 1})


def user_points_update(user_id, point_amount):
    User_points = Query()
    points = db_user_points.search(User_points.id == user_id)
    if len(points) > 0:
        db_user_points.update(operations.set('amount', point_amount), User_points.id == user_id)
        print(f'Updated {user_id}')
    elif len(points) == 0 and point_amount > 0:
        db_user_points.insert({'id': user_id, 'amount': point_amount})
        print(f'Inserted {user_id}')


def get_all_user_points():
    return db_user_points.all()