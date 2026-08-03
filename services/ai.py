from google import genai
from pathlib import Path
from config import GEMINI_APIKEY
import re
import json
from services.modifiers import modifiers
from services.constants import ARMY_TYPES, MOBILIZATION_LAWS, get_modifier

ai = genai.Client(api_key=GEMINI_APIKEY)

NARRATOR_PROMPT = Path("prompts/narrator.txt").read_text(encoding = "utf-8")
NAME_CHECKER_PROMPT = Path("prompts/name_checker.txt").read_text(encoding="utf-8")
IDEOLOGY_CHECKER_PROMPT = Path("prompts/ideology_checker.txt").read_text(encoding="utf-8")
FULLNAME_CHECKER_PROMPT = Path("prompts/fullname_checker.txt").read_text(encoding="utf-8")
CAPITAL_CHECKER_PROMPT = Path("prompts/capital_checker.txt").read_text(encoding="utf-8")
COUNTRY_LORE_PROMPT = Path("prompts/country_lore.txt").read_text(encoding="utf-8")
DETAILS_PROMPT = Path("prompts/details.txt").read_text(encoding="utf-8")
INITIALIZATION_PROMPT = Path("prompts/initialization.txt").read_text(encoding="utf-8")
RENAME_SHORT_CHECKER_PROMPT = Path("prompts/rename_short_checker.txt").read_text(encoding="utf-8")
RENAME_LONG_CHECKER_PROMPT = Path("prompts/rename_long_checker.txt").read_text(encoding="utf-8")

JSON_PATTERN = r"\{.*\}"

def check_countryname(name):
    return ask_ai(name, NAME_CHECKER_PROMPT)

def check_ideology(ideology):
    return ask_ai(ideology, IDEOLOGY_CHECKER_PROMPT)

def check_fullname(fullname, countryname, ideology):
    request = ("{"
               f'"base_countryname":"{countryname}",'
               f'"ideology":"{ideology}",'
               f'"full_countryname": "{fullname}"'
               '}')
    return ask_ai(request, FULLNAME_CHECKER_PROMPT)

def check_capital(name, countryname):
    request = ("{"
               f'"countryname":{countryname},'
               f'"capitalname":{name}'
               "}")
    return ask_ai(request, CAPITAL_CHECKER_PROMPT)

def write_country_lore(player):
    country = player["countries"][0]
    request = ("{"
               f'"full_countryname":{country["full_countryname"]},'
               f'"countryname":{country["countryname"]},'
               f'"capital":{country["capital"]},'
               f'"ideology":{country["ideology"]}'
               "}")
    return ask_ai(request, COUNTRY_LORE_PROMPT)

def define_details(details, player):
    country = player["countries"][0]
    request = ("{"
               f'"full_countryname":{country["full_countryname"]},'
               f'"countryname":{country["countryname"]},'
               f'"capital":{country["capital"]},'
               f'"ideology":{country["ideology"]},'
               f'"user_input":{details}'
               "}")
    return ask_ai(request, DETAILS_PROMPT)

def write_step_first(player):
    country = player["countries"][0]
    army_types = list(ARMY_TYPES.values())
    for a in army_types:
        a.update({"_id":str(a["_id"]), "counteracts":None})

    mobilization_laws = list(MOBILIZATION_LAWS.values())
    for l in mobilization_laws:
        l.update({"_id":str(l["_id"])})

    request = ("{"
               f'"countryname":"{country["countryname"]}",'
               f'"ful_countryname":"{country["full_countryname"]}",'
               f'"capital":"{country["capital"]}",'
               f'"ideology":"{country["ideology"]}",'
               f'"ideology_desc":"{country["ideology_desc"]}",'
               f'"country_characteristics":"{country["country_characteristics"]}",'
               f'"goals":{json.dumps(country["goals"])},'
               f'"territorial_ambitions":{json.dumps(country["territorial_ambitions"])},'
               f'"modifiers_information":{json.dumps(modifiers)},'
               f'"army_types":{json.dumps(army_types)},'
               f'"mobilization_laws":{json.dumps(mobilization_laws)}')
    return ask_ai(request, INITIALIZATION_PROMPT)

def write_step_plot(player):
    if len(player["actions"]) > 0:
        country = player["countries"][0]
        request = ("{"
                   f'"countryname":"{country["countryname"]}",'
                   f'"full_countryname":"{country["full_countryname"]}",'
                   f'"capital":"{country["capital"]}",'
                   f'"ideology":"{country["ideology"]}",'
                   f'"ideology_desc":{country["ideology_desc"]},'
                   f'"country_characteristics":"{country["country_characteristics"]}",'
                   f'"goals":{json.dumps(country["goals"])},'
                   f'"completed_goals":{json.dumps(country["completed_goals"])},'
                   f'"territorial_ambitions":{json.dumps(country["territorial_ambitions"])},'
                   f'"date":{player["date"]},'
                   f'"money":{country["money"]},'
                   f'"stability":{get_modifier(country, "stability") * 100},'
                   f'"militarization":{get_modifier(country, "militarization")*100},'
                   f'"move":{player["step"]},'
                   f'"modifiers_information":{json.dumps(modifiers)},'
                   f'actions":{player["actions"]}')
        return ask_ai(request, NARRATOR_PROMPT)
    return json.loads('{"response":"С момента прошлого хода ничего не произошло..."}')

def check_country_short_renaming(old_countryname, cities, capital, new_countryname):
    request = ("{"
               f'"old_countryname":"{old_countryname}",'
               f'"cities":{cities},'
               f'"capital":"{capital}",'
               f'"new_countryname":"{new_countryname}"')
    return ask_ai(request, RENAME_SHORT_CHECKER_PROMPT)

def check_country_long_renaming(countryname, old_full_countryname, characteristics, ideology, ideology_desc, cities, capital, new_full_countryname):
    request = ("{"
               f'"countryname":"{countryname}",'
               f'"old_full_countryname":"{old_full_countryname}",'
               f'"country_characteristics":"{characteristics}",'
               f'"ideology":"{ideology}",'
               f'"ideology_description":"{ideology_desc}",'
               f'"cities":{cities},'
               f'"capital":"{capital}",'
               f'"new_full_countryname":"{new_full_countryname}"')
    return ask_ai(request, RENAME_LONG_CHECKER_PROMPT)

def ask_ai(request, base_prompt):
    prompt = f"""{base_prompt}
    Ввод пользователя: {request}"""
    interaction = ai.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt
    )
    output = interaction.output_text
    json_text = re.search(JSON_PATTERN, output, re.DOTALL)
    result = json.loads(json_text.group())
    return result
