from datetime import datetime
from thefuzz import fuzz
import json
import re
import os

PURPLE = "\033[95m"
CYAN = "\033[96m"
DARKCYAN = "\033[36m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"
ITALIC = "\033[3m"


def case_year(case):
    if case["citation"] and case["citation"]["year"]:
        return case["citation"]["year"]
    elif case["timeline"] and case["timeline"][-1]["event"] == "Decided":
        return datetime.fromtimestamp(case["timeline"][-1]["dates"][0]).strftime("%Y")
    else:
        return "undecided"


def process_text(text):
    text = text.strip()
    text = re.sub("</?p>", "", text)
    text = re.sub("<(em|i)>", ITALIC, text)
    text = re.sub("</(em|i)>", END, text)
    text = re.sub("</(li|ol)>", "", text)
    text = re.sub("<li>", "  - ", text)
    text = re.sub("<ol>", "\n", text)
    if text.endswith("\n"):
        text = text[:-1]
    return text


def decision_string(case, sort_by="seniority"):
    justice_data = sorted(
        [j for j in case["decisions"][-1]["votes"]],
        key=lambda j: j["member"]["last_name"],
        reverse=False,
    )
    justice_data.sort(key=lambda j: j[sort_by], reverse=False)
    justice_names = [j["member"]["last_name"] for j in justice_data]
    outcome_list = []
    for i, justice in enumerate(justice_names):
        if justice_data[i]["vote"] == "majority":
            outcome_list.append(f"{GREEN}{justice}{END}")
        elif justice_data[i]["vote"] == "minority":
            outcome_list.append(f"{RED}{justice}{END}")
        else:
            outcome_list.append(f"{BLUE}{justice}{END}")
    return ", ".join(outcome_list)


with open("cases.json") as fil:
    case_info = json.load(fil)
    case_ref = {
        case["name"]: (
            case_year(case),
            case["href"],
            str(case["term"]),
            str(case["ID"]),
        )
        for case in case_info
    }

while True:
    user_input = input('Search cases ("exit" to exit): ').strip()
    if not user_input:
        continue
    if user_input.strip().lower() == "exit":
        exit(0)
    relevant_cases = [
        case
        for case in case_ref.keys()
        if fuzz.partial_ratio(user_input.lower(), case.lower()) >= 90
        and os.path.exists(
            os.path.join("all_cases", case_ref[case][2], case_ref[case][3] + ".json")
        )
    ]
    relevant_cases.sort(
        key=lambda c: fuzz.partial_ratio(user_input.lower(), c.lower()), reverse=True
    )
    val = len(relevant_cases)
    print()
    if len(relevant_cases) == 0:
        print("No cases found. Try again.")
        print()
        continue
    elif len(relevant_cases) == 1:
        selected_case_ref = relevant_cases[0]
    else:
        print("Multiple cases matched:")
        for i, relevant_case in enumerate(relevant_cases):
            print(f"{i + 1}. {relevant_case} ({case_ref[relevant_case][0]})")
        while True:
            try:
                val = int(input("Select a case by number (-1 to exit): "))
                if val == -1:
                    break
                elif val > len(relevant_cases):
                    print("Invalid selection.")
                    continue
                else:
                    selected_case_ref = relevant_cases[val - 1]
                    break
            except ValueError:
                print("Invalid selection.")
                continue
    if val == -1:
        continue
    print()
    year, href, term, idnum = case_ref[selected_case_ref]
    first_party = selected_case_ref.split(" v. ")[0]
    second_party = re.sub(r"\s+\(\d+\)$", "", selected_case_ref.split(" v. ")[1])
    print(f"{BOLD}{YELLOW}{first_party}{END}{BOLD} v. ", end="")
    print(f"{PURPLE}{second_party}{END}{BOLD} ({year}){END}")
    case = json.load(open(os.path.join("all_cases", term, idnum + ".json")))
    print(f"{BOLD}{case['first_party_label']}:{END} {YELLOW}{case['first_party']}{END}")
    print(
        f"{BOLD}{case['second_party_label']}:{END} {PURPLE}{case['second_party']}{END}"
    )
    if case["facts_of_the_case"]:
        print(f"{BOLD}Facts:{END} {process_text(case['facts_of_the_case'])}")
    if case["question"]:
        print(f"{BOLD}Questions:{END} {process_text(case['question'])}")
    if case["decided_by"]:
        print(f"{BOLD}Decided By:{END} {case['decided_by']['name']}")
    print(f"{BOLD}Decision:{END}", end=" ")
    if year == "undecided":
        print("undecided")
    else:
        if case["decisions"][-1]["winning_party"]:
            winner = max(
                [case["first_party"], case["second_party"]],
                key=lambda c: fuzz.partial_ratio(
                    c, case["decisions"][-1]["winning_party"]
                ),
            )
            print(
                f"in favor of {BOLD}{YELLOW if winner == case['first_party'] else PURPLE}{winner}{END}",
                end=", ",
            )
        print(
            f"{GREEN}{case['decisions'][-1]['majority_vote']}{END}-{RED}{case['decisions'][-1]['minority_vote']}{END}"
        )
        print(
            f"({GREEN}green{END} is majority, {RED}red{END} is minority, {BLUE}blue{END} is neither)"
        )
        print(decision_string(case))
        print(process_text(case["conclusion"]))
    print()
