import json
import requests

import utils


def jisho(keyword):
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
