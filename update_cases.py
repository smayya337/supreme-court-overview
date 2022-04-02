import json

with open("cases.json") as fil:
    case_info = json.load(fil)

undecided = []
for case in case_info:
    valid = True
    if not case["timeline"]:
        valid = False
    else:
        events = [evt["event"] for evt in case["timeline"] if evt is not None]
        if "Decided" not in events:
            valid = False
    if not valid:
        undecided.append(
            {
                "name": case["name"],
                "link": case["href"],
                "term": case["term"],
                "id": case["ID"],
            }
        )

with open("cases_to_update.json", "w") as fil:
    json.dump(undecided, fil, indent=2)
