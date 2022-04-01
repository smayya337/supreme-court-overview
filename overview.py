from datetime import datetime
from thefuzz import fuzz
import json
import re
import os

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'


def case_year(case):
    if case["citation"] and case["citation"]["year"]:
        return case["citation"]["year"]
    elif case["timeline"] and case["timeline"][-1]["event"] == "Decided":
        return datetime.fromtimestamp(case["timeline"][-1]["dates"][0]).strftime("%Y")
    else:
        return "undecided"


with open("cases.json") as fil:
    case_info = json.load(fil)
    case_ref = {case["name"]: (case_year(case), case["href"], str(case["term"]), str(case["ID"])) for case in case_info}

while True:
    user_input = input("Search cases: ").strip()
    relevant_cases = [case for case in case_ref.keys() if fuzz.partial_ratio(user_input, case) >= 80]
    print()
    if len(relevant_cases) == 0:
        print("No cases found. Try again.")
        print()
        continue
    elif len(relevant_cases) == 1:
        selected_case_ref = relevant_cases[0]
    else:
        print("Multiple cases matched:")
        selected_case_ref = len(relevant_cases)
        for i, relevant_case in enumerate(relevant_cases):
            print(f"{i + 1}. {relevant_case} ({case_ref[relevant_case][0] if case_ref[relevant_case][0] else 'undecided'})")
        try:
            selected_case_ref = relevant_cases[int(input("Select a case by number: ")) - 1]
        except ValueError:
            print("Invalid selection.")
    print()
    year, href, term, idnum = case_ref[selected_case_ref]
    print(f"{BOLD}{selected_case_ref} ({year}){END}")
    case = json.load(open(os.path.join("all_cases", term, idnum + ".json")))
    print(f"{BOLD}Facts:{END} {re.sub('</?p>', '', case['facts_of_the_case'])}")
    print()
