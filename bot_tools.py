import re
import json
import requests

import config
import utils


def shorten_part_of_speech(pos):
    shortened_parts_of_speech = {
        'Noun': 'N',
        'No-adjective': 'の-adj',
        'I-adjective': 'い-adj',
        'Suru verb': 'する-vb',
        'Wikipedia definition': 'Wikipedia def.',
        'Ichidan verb': 'Ichidan-vb.',
        'Transitive verb': 'Trans-vb.',
        'Expression': 'Expr.',
    }
    if 'Godan' in pos:
        return 'Godan-vb.'
    return shortened_parts_of_speech.get(pos, pos)


def is_superadmin(name):
    return name in config.superadmins


def parse_command(message, n_arguments=None):
    """
    Splits a message into its command's components. A command has the structure:

    ```
    !<name>[ <argument>]*
    ```

    So for example `!hello`, `!hello a` or `!hello a b`.

    If we know we only have `n_arguments`, we can collapse the superfluous arguments into one
    string. This is useful for example when we have `!add_tag hello Hello everyone!`. Parsing
    this with `n_arguments = 2` yields `['add_tag', 'hello', 'Hello everyone!']`.
    """
    if not message.startswith(config.bot_prefix):
        raise ValueError('Not a command: ' + message)
    splits = message[1:].split(' ')
    if len(splits) - 1 < n_arguments:
        raise ValueError(
            'Too few arguments. Expected {} and got {}.'.format(n_arguments, len(splits) - 1)
        )
    if n_arguments is None:
        return splits
    else:
        return splits[:n_arguments] + [' '.join(splits[n_arguments:])]


def jisho(keyword):
    data = json.loads(requests.get(
        "http://jisho.org/api/v1/search/words?keyword={}".format(keyword)
    ).text)["data"]

    results = []

    if len(data) == 0:
        return None

    for search_result in data:
        curr = {"word_jp": "", "reading": "", "english": [], "parts_of_speech": []}

        if "word" in search_result["japanese"][0]:
            curr["word_jp"] = search_result["japanese"][0]["word"]

        if "reading" in search_result["japanese"][0]:
            curr["reading"] = search_result["japanese"][0]["reading"]

        curr["english"] = search_result["senses"][0]["english_definitions"]
        curr["parts_of_speech"] = search_result["senses"][0]["parts_of_speech"]

        results.append(curr)

    return results
