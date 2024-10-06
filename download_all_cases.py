import datetime
import json
import os
import urllib.request

CURRENT_TERM = datetime.datetime.now().year

TERMS = {"1789-1850", "1850-1900", "1900-1940", "1940-1955"}

for year in range(1955, CURRENT_TERM + 1):
    TERMS.add(str(year))

cases_json = []

for term in TERMS:
    with urllib.request.urlopen(f"https://api.oyez.org/cases?per_page=0&filter=term:{term}") as url:
        term_data = json.loads(url.read().decode("utf-8"))
        cases_json.extend(term_data)

with open("cases.json", "w") as f:
    json.dump(cases_json, f, indent=2)

# with open("cases.json") as fil:
#     cases_json = json.load(fil)
#     # print(cases_json)

cases = {case["name"]: (case["href"], case["term"], case["ID"]) for case in cases_json}

not_cited_yet = []

for name, (link, term, idnum) in cases.items():
    path = os.path.join("all_cases", str(term), str(idnum) + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(name, end="")
    if os.path.exists(path):
        data = json.load(open(path))
        if data["citation"] and data["citation"]["volume"]:
            print("... exists")
            continue
        else:
            print("... updating")
    else:
        print("... downloading")
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode("utf-8"))
    with open(path, "w") as fil:
        json.dump(data, fil, indent=2)
    if not data["citation"] or not data["citation"]["volume"]:
        not_cited_yet.append(
            {"name": name, "link": link, "term": term, "id": idnum}
        )

with open("cases_to_update.json", "w") as fil:
    json.dump(not_cited_yet, fil, indent=2)
