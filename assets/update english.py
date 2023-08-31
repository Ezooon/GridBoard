import json

strings = {}
with open("lang/arabic.json", 'r', encoding="utf-8") as f:
    strings = json.load(f)

english_strings = {}
for string in strings:
    english_strings[string] = string

with open("lang/english.json", 'w') as f:
    json.dump(english_strings, f, indent=4)
