from tinydb import TinyDB, Query


db = TinyDB('./data/db.json')
db_tags = db.table('tags')
db_mods = db.table('mods')
db_clips = db.table('clips')


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


def get_clip(url):
    Clip = Query()
    clips = db_clips.search(Clip.url == url)
    if len(clips) > 0:
        return clips[0]
    else:
        return None


def exists_clip(url):
    clip = get_clip(url)
    return clip is not None


def get_all_clips():
    return db_clips.all()


def add_clip(url):
    db_clips.insert({'url': url})


def remove_clip(url):
    Clip = Query()
    return db_clips.remove(Clip.url == url)


def get_all_mods():
    return db_mods.all()


def is_mod(name):
    Mod = Query()
    mods = db_mods.search(Mod.name == name)
    if len(mods) > 0:
        return True
    else:
        return False


def add_mod(name):
    db_mods.insert({'name': name})


def remove_mod(name):
    Mod = Query()
    return db_mods.remove(Mod.name == name)
