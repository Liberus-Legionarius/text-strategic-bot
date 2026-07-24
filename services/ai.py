from http.client import responses

from google import genai
from pathlib import Path
from config import GEMINI_APIKEY
import re
import json

ai = genai.Client(api_key=GEMINI_APIKEY)

NARRATOR_PROMPT = Path("prompts/narrator.txt").read_text(encoding = "utf-8")
NAME_CHECKER_PROMPT = Path("prompts/name_checker.txt").read_text(encoding="utf-8")
IDEOLOGY_CHECKER_PROMPT = Path("prompts/ideology_checker.txt").read_text(encoding="utf-8")
FULLNAME_CHECKER_PROMPT = Path("prompts/fullname_checker.txt").read_text(encoding="utf-8")
CAPITAL_CHECKER_PROMPT = Path("prompts/capital_checker.txt").read_text(encoding="utf-8")

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

def write_step_plot(player, population):
    request = ("{"
               f'"countryname":"{player["countryname"]}",'
               f'"ful_countryname":"{player["full_countryname"]}",'
               f'"capital":"{player["capital"]}",'
               f'"date":{player["date"]},'
               f'"money":{player["money"]},'
               f'"stability":{player["stability"]},'
               f'"militarization":{player["militarization"]},'
               f'"population":{population}')
    return ask_ai(request, NARRATOR_PROMPT)

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
