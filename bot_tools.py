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


def get_trailing_numbers(phrase):
    splits = phrase.split(' ')
    if splits[-1].isdigit():
        return [' '.join(splits[:-1]), int(splits[-1])]
    else:
        return [phrase, None]


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
    results = json.loads(requests.get(
        "http://jisho.org/api/v1/search/words?keyword={}".format(keyword)
    ).text)["data"]

    return results
