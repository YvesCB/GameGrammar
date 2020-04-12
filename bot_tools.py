import re
import json
import requests

import config
import utils


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
    print('HELLO WE ARE SEARCHING FOR THIS')
    print(keyword)
    print('THANK YOU')
    data = json.loads(requests.get(
        "http://jisho.org/api/v1/search/words?keyword={}".format(keyword)
    ).text)["data"]

    results = []

    if len(data) == 0:
        utils.log_kv("No results...")
        return(-1)
    else:
        for search_result in data:
            curr = {"word_jp": "", "reading": "", "english": [], "parts_of_speech": []}
            if "word" in search_result["japanese"][0]:
                curr["word_jp"] = search_result["japanese"][0]["word"]
            if "reading" in search_result["japanese"][0]:
                curr["reading"] = search_result["japanese"][0]["reading"]
            for eng in search_result["senses"][0]["english_definitions"]:
                curr["english"].append(eng)
            for parts in search_result["senses"][0]["parts_of_speech"]:
                curr["parts_of_speech"].append(parts)
            results.append(curr)
        # for key in range(len(data["data"])):
        #     results.append({"word_jp": "", "reading": "", "english": [], "parts_of_speech": []})
        #     for entry in range(len(data["data"][key]["japanese"])):
        #         if "word" in data["data"][key]["japanese"][entry]:
        #             results[key]["word_jp"] = data["data"][key]["japanese"][entry]["word"]
        #             print(
        #                 data["data"][key]["japanese"][entry]["word"] + ' ' +
        #                 data["data"][key]["japanese"][entry]["reading"]
        #             )
        #         if "reading" in data["data"][key]["japanese"][entry]:
        #             results[key]["reading"] = data["data"][key]["japanese"][entry]["reading"]

        #     for eng in data["data"][key]["senses"][0]["english_definitions"]:
        #         results[key]["english"].append(eng)
        #     for parts in data["data"][key]["senses"][0]["parts_of_speech"]:
        #         results[key]["parts_of_speech"].append(parts)
    return results
