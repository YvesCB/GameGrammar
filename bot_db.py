from tinydb import TinyDB, Query


db = TinyDB('./data/db.json')
db_tags = db.table('tags')
db_mods = db.table('mods')


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


def get_mods():
    return db_mods.all()


def is_mod(name):
    Mod = Query()
    mods = db_mods.search(Mod.name == name)
    if len(mods) > 0:
        return True
    else:
        return False
