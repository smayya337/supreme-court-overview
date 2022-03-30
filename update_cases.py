import json
import unicodedata
import urllib.request

with urllib.request.urlopen("https://api.oyez.org/cases?per_page=0") as url:
    data = url.read().decode("unicode_escape").replace("\/", "/").replace("<p>", "").replace("</p>", "").replace("\n", "")
    data = unicodedata.normalize("NFKD", data).encode("ascii", "ignore")

print(data)
