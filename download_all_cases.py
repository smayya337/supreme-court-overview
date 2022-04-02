import json
import os
import urllib.request

with open("cases.json") as fil:
    cases_json = json.load(fil)
    # print(cases_json)

cases = {case["name"]: (case["href"], case["term"], case["ID"]) for case in cases_json}

not_cited_yet = []

for name, (link, term, idnum) in cases.items():
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode("utf-8"))
        path = os.path.join("all_cases", str(term), str(idnum) + ".json")
        print(name, end="")
        if os.path.exists(path):
            print("... exists")
            continue
        print("... downloading")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fil:
            json.dump(data, fil, indent=2)
        if not data["citation"]:
            not_cited_yet.append(
                {"name": name, "link": link, "term": term, "id": idnum}
            )

with open("cases_to_update.json", "w") as fil:
    json.dump(not_cited_yet, fil, indent=2)
