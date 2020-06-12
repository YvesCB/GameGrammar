from tinydb import TinyDB, Query

db = TinyDB('./data/db.json')
db_tags = db.table('tags')
db_admin_roles = db.table('admin_roles')


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


def get_admin_role(name):
    Admin_role = Query()
    admins = db_admin_roles.search(Admin_role.name == name)
    if len(admins) > 0:
        return admins[0]
    else:
        return None


def add_admin_role(name):
    db_admin_roles.insert({'name': name})


def remove_admin_role(name):
    Admin_role = Query()
    return db_admin_roles.remove(Admin_role.name == name)


def get_all_admin_roles():
    return db_admin_roles.all()


def exists_admin_role(name):
    admin_role = get_admin_role(name)
    return admin_role is not None