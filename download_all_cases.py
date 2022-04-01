import json
import os
import urllib.request

with open("cases.json") as fil:
    cases_json = json.load(fil)
    print(cases_json)

cases = {case["name"]: (case["href"], case["term"], case["ID"]) for case in cases_json}

for name, (link, term, idnum) in cases.items():
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode("utf-8"))
        path = os.path.join("all_cases", str(term), str(idnum) + ".json")
        if os.path.exists(path):
            continue
        print(name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fil:
            json.dump(data, fil, indent=2)
