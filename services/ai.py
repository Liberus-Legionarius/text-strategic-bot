from google import genai
from pathlib import Path
import re
import json
from services.bot import db
from services.ideologies import ideologies, ideology_relations
from services.map.map_management import province_map
from services.math.economy_math import get_total_income, get_total_spending
from services.math.territory_math import get_cities, get_free_cities
from services.modifiers import modifiers
from services.constants import ARMY_TYPES, MOBILIZATION_LAWS, get_modifier, BUILDINGS, get_country
from services.effects import effects
from services.npc_logic import npc_logic_parameters

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
EVENTS_PROMPT = Path("prompts/events.txt").read_text(encoding="utf-8")
CITY_GEN_PROMPT = Path("prompts/cities_generator.txt").read_text(encoding="utf-8")
COUNTRY_GEN_PROMPT = Path("prompts/countries_generator.txt").read_text(encoding="utf-8")

JSON_PATTERN = r"\{.*\}"

def check_countryname(name, api_key):
    return ask_ai(name, NAME_CHECKER_PROMPT, api_key)

def check_ideology(ideology, api_key):
    return ask_ai(ideology, IDEOLOGY_CHECKER_PROMPT, api_key)

def check_fullname(fullname, countryname, ideology, api_key):
    request = ("{"
               f'"base_countryname":"{countryname}",'
               f'"ideology":"{ideology}",'
               f'"full_countryname": "{fullname}"'
               '}')
    return ask_ai(request, FULLNAME_CHECKER_PROMPT, api_key)

def check_capital(name, countryname, api_key):
    request = ("{"
               f'"countryname":{countryname},'
               f'"capitalname":{name}'
               "}")
    return ask_ai(request, CAPITAL_CHECKER_PROMPT, api_key)

def write_country_lore(player):
    country = player["countries"][0]
    request = ("{"
               f'"full_countryname":"{country["full_countryname"]}",'
               f'"countryname":"{country["countryname"]}",'
               f'"capital":"{country["capital"]}",'
               f'"ideology":"{country["ideology"]}",'
               f'"ideology_types": {json.dumps(ideologies, ensure_ascii=False)},'
               f'"provinces": {json.dumps(province_map, ensure_ascii=False)}'
               "}")
    return ask_ai(request, COUNTRY_LORE_PROMPT, player["api_key"])

def define_details(details, player):
    country = player["countries"][0]
    request = ("{"
               f'"full_countryname":"{country["full_countryname"]}",'
               f'"countryname":"{country["countryname"]}",'
               f'"capital":"{country["capital"]}",'
               f'"ideology":"{country["ideology"]}",'
               f'"ideology_types": {json.dumps(ideologies, ensure_ascii=False)},'
               f'"provinces": {json.dumps(province_map, ensure_ascii=False)},'
               f'"user_input":"{details}"'
               "}")
    return ask_ai(request, DETAILS_PROMPT, player["api_key"])

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
    return ask_ai(request, INITIALIZATION_PROMPT, player["api_key"])

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
        return ask_ai(request, NARRATOR_PROMPT, player["api_key"])
    return json.loads('{"response":"С момента прошлого хода ничего не произошло..."}')

def check_country_short_renaming(old_countryname, cities, capital, new_countryname, api_key):
    request = ("{"
               f'"old_countryname":"{old_countryname}",'
               f'"cities":{cities},'
               f'"capital":"{capital}",'
               f'"new_countryname":"{new_countryname}"')
    return ask_ai(request, RENAME_SHORT_CHECKER_PROMPT, api_key)

def check_country_long_renaming(countryname, old_full_countryname, characteristics, ideology, ideology_desc, cities, capital, new_full_countryname, api_key):
    request = ("{"
               f'"countryname":"{countryname}",'
               f'"old_full_countryname":"{old_full_countryname}",'
               f'"country_characteristics":"{characteristics}",'
               f'"ideology":"{ideology}",'
               f'"ideology_description":"{ideology_desc}",'
               f'"cities":{cities},'
               f'"capital":"{capital}",'
               f'"new_full_countryname":"{new_full_countryname}"')
    return ask_ai(request, RENAME_LONG_CHECKER_PROMPT, api_key)

def create_event(player, country):
    buildings = list(BUILDINGS.values())
    for b in buildings:
        b.update({"_id": str(b["_id"])})
    army_types = list(ARMY_TYPES.values())
    for a in army_types:
        a.update({"_id": str(a["_id"]), "counteracts": None})
    cities = get_cities(player, country["id"])
    request = ("{"
               f'"countryname":"{country["countryname"]}",'
               f'"full_countryname":"{country["full_countryname"]}",'
               f'"capital":"{country["capital"]}",'
               f'"ideology":"{country["ideology"]}",'
               f'"ideology_desc":{country["ideology_desc"]},'
               f'"country_characteristics":"{country["country_characteristics"]}",'
               f'"goals":{json.dumps(country["goals"], ensure_ascii=False)},'
               f'"completed_goals":{json.dumps(country["completed_goals"], ensure_ascii=False)},'
               f'"territorial_ambitions":{json.dumps(country["territorial_ambitions"], ensure_ascii=False)},'
               f'"date":{player["date"]},'
               f'"money":{country["money"]},'
               f'"income":{get_total_income(player, country)},'
               f'"spending":{get_total_spending(player, country)},'
               f'"political_power":{country["polit_power"]},'
               f'"national_spirits":{json.dumps(country["national_spirits"], ensure_ascii=False)},\n'
               f'"cities": {json.dumps(cities, ensure_ascii=False)},\n'
               f'"move":{player["step"]},'
               f'"modifiers_information":{json.dumps(modifiers, ensure_ascii=False)},'
               f'"effects_information": {json.dumps(effects, ensure_ascii=False)},\n'
               f'"building_types":{json.dumps(buildings, ensure_ascii=False)},\n'
               f'"army_types":{json.dumps(army_types, ensure_ascii=False)},'
               f'"history": {json.dumps(player["history"], ensure_ascii=False)}')
    return ask_ai(request, EVENTS_PROMPT, player["api_key"])

def generate_city(player, city, population = None, buildings = None):
    building_types = list(BUILDINGS.values())
    for b in building_types:
        b.update({"_id": str(b["_id"])})
    request = ("{"
               f'"city":"{city}"')
    if population:
        request += f', "population":{population}'
        if buildings:
            request += f', "buildings":{json.dumps(buildings, ensure_ascii=False)}'
    request += (f', "building_types": {json.dumps(building_types, ensure_ascii=False)}'
                "}")
    return ask_ai(request, CITY_GEN_PROMPT, player["api_key"])

def generate_country(player, city_name, max_size, new_country_ideology):
    country = get_country(player, 0)
    cities = get_cities(player, 0)
    free_cities = get_free_cities(player)
    army_types = list(ARMY_TYPES.values())
    for a in army_types:
        a.update({"_id": str(a["_id"]), "counteracts": None})

    mobilization_laws = list(MOBILIZATION_LAWS.values())
    for l in mobilization_laws:
        l.update({"_id": str(l["_id"])})
    request = ("{"
               f'"player_countryname": "{country["full_countryname"]}",'
               f'"player_ideology": "{country["ideology"]}",'
               f'"player_ideology_type":"{country["ideology_type"]}",'
               f'"player_ideology_desc": "{country["ideology_desc"]}",'
               f'"player_cities":{json.dumps(cities, ensure_ascii=False)},'
               f'"army_types":{json.dumps(army_types, ensure_ascii=False)},'
               f'"max_country_size":{max_size},'
               f'"free_cities":{json.dumps(free_cities, ensure_ascii=False)},'
               f'"provinces": {json.dumps(province_map, ensure_ascii=False)},'
               f'"discovered_city": "{city_name}",'
               f'"new_country_ideology": "{new_country_ideology}",'
               f'"modifiers":{json.dumps(modifiers, ensure_ascii=False)},'
               f'"mobilization_laws":{json.dumps(mobilization_laws, ensure_ascii=False)},'
               f'"ideologies_info": {json.dumps(ideologies, ensure_ascii=False)},'
               f'"ideologies_relations": {json.dumps(ideology_relations, ensure_ascii=False)},'
               f'"ai_logic_control": {json.dumps(npc_logic_parameters, ensure_ascii=False)}'
               "}")
    return ask_ai(request, COUNTRY_GEN_PROMPT, player["api_key"])

def ask_ai(request, base_prompt, api_key):
    ai = genai.Client(api_key=api_key)
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

def check_api_key(api_key):
    try:
        ai = genai.Client(api_key = api_key)
        interaction = ai.interactions.create(
            model="gemini-3.1-flash-lite",
            input="Answer me: Ok."
        )
        return True
    except Exception as e:
        return False