import random
import random as rnd
import services.ai as ai
from handlers.actions.conscript_army_action import conscript_army
from handlers.actions.militarization_growth_action import change_militarization_growth
from handlers.actions.pops_invest_action import change_pops_invest
from handlers.actions.reorganize_amy_action import reorganize_army
from handlers.actions.reset_national_spirit_action import reset_national_spirit
from handlers.actions.stability_growth_action import change_stability_growth
from handlers.actions.tax_action import change_tax_rate
from services.bot import bot, db
from services.constants import get_player, get_modifier, get_country, MOBILIZATION_LAWS, BUILDINGS, ARMY_TYPES, \
    get_is_pacifism
from services.campaign_effects import CAMPAIGN_BONUS, CAMPAIGN_RESULT
from services.math.ai_logic_math import calculate_balance_change_desire, calculate_tax_rate_change_desire, \
    calculate_stability_change_desire, calculate_militarization_change_desire, calculate_pops_growth_invest_desire, \
    calculate_change_mobilization_law_desire, calculate_goal
from services.math.army_math import get_manpower, get_total_army, get_army, get_army_type, get_reorganization_cost
from services.math.economy_math import get_total_spending, get_total_income, get_prod_units, get_prod_units_consumption
from handlers.ingame_panels.state_panel import open_state_panel
from dateutil.relativedelta import relativedelta
from services.math.spending_math import get_stability_growth, get_militarization_growth
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from bson import ObjectId

from services.math.territory_math import get_percent_pop_growth, get_total_population, get_cities, build_in_city


@bot.callback_query_handler(func= lambda call: call.data == "end_move")
def callback_end_move(call):
    bot.answer_callback_query(call.id)
    player = get_player(call.from_user)
    player_country = get_country(player, 0)
    if rnd.random() <= player["event_chance"] and len(player_country["campaigns"]) < 1:
        event = ai.create_event(player, player_country)
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$set": {
                                      "event_chance": 0.0,
                                      "event_options": event["options"]
                                  }
                              })
        text = (f"{event['event_name']}"
                "\n\n"
                f"{event['event_text']}\n"
                f"Последствия выбора: {event['event_consequences']}")
        event_kb = InlineKeyboardMarkup(row_width=1)
        for i, option in enumerate(event["options"]):
            event_kb.add(InlineKeyboardButton(option["name"], callback_data=f"event:{i}"))
        bot.edit_message_text(
            text,
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = event_kb
        )
    elif len(player_country["campaigns"]) > 0:
        for campaign in player_country["campaigns"]:
            dice = rnd.randint(0,3) + rnd.randint(0,3) + CAMPAIGN_BONUS[campaign["cost"]]
            dice = min(dice, 6)
            print(dice)
            CAMPAIGN_RESULT[dice](player, campaign)
        on_move_effects(player, call.from_user, call.message.chat.id, call.message.message_id)
    else:
        db.players.update_one({"tg_id":player["tg_id"]},
                              {
                                  "$inc": {"event_chance":0.33}
                              })
        on_move_effects(player, call.from_user, call.message.chat.id, call.message.message_id)


def on_move_effects(player, user, chat_id, message_id):
    for country in player["countries"]:
        balance = get_total_income(player, country) - get_total_spending(player, country)
        polit_power_gain = get_modifier(country, "polit_power_gain_flat")
        polit_power_modifier = get_modifier(country, "polit_power_gain_modifier", 1)
        pop_growth = ((get_modifier(country, "population_growth") +
                      get_modifier(country,"population_growth_invest")) *
                      get_modifier(country, "stability", 0.35) + 1)
        db.players.update_one({"tg_id": player["tg_id"], "countries.id":country["id"]},
                              {
                                  "$inc": {
                                      f"countries.$.money": balance,
                                      f"countries.$.polit_power": polit_power_gain * polit_power_modifier,
                                      f"countries.$.national_spirits.0.stability": get_stability_growth(country),
                                      f"countries.$.national_spirits.0.militarization": get_militarization_growth(country)

                                  }
                              })
        db.players.update_one({"tg_id": player["tg_id"]},
                              [
                                  {
                                      "$set": {
                                          "cities": {
                                              "$map": {
                                                  "input": "$cities",
                                                  "as": "city",
                                                  "in": {
                                                      "$cond": [
                                                          {"$eq": ["$$city.owner", country["id"]]},
                                                          {
                                                              "$mergeObjects": [
                                                                  "$$city",
                                                                  {
                                                                      "population": {
                                                                          "$multiply": ["$$city.population", pop_growth]
                                                                      }
                                                                  }
                                                              ]
                                                          },
                                                          "$$city"
                                                      ]
                                                  }
                                              }
                                          }
                                      }
                                  }
                              ])
        if not country["id"] == 0:
            ai_country_move(player, country)
    date = player["date"] + relativedelta(months=1)
    db.players.update_one({"tg_id":player["tg_id"]},
                          {
                              "$inc":{
                                  "step":1
                              },
                              "$set": {
                                  "ai_plot": None,
                                  "date": date
                              }
                          })
    open_state_panel(user, chat_id, message_id)

def ai_country_move(player, country):
    logic = country["ai_logic"]
    ml_id = next(i for i, ml in enumerate(MOBILIZATION_LAWS) if str(ml) == country["national_spirits"][2]["_id"])
    balance_change_desire = calculate_balance_change_desire(country["money"],
                                                            get_total_income(player, country),
                                                            get_total_spending(player, country),
                                                            logic["preferred_balance"])
    tax_rate_change_desire = calculate_tax_rate_change_desire(get_modifier(country, "tax_rate"), logic["min_tax_rate"],
                                                              logic["max_tax_rate"], logic["preferred_tax_rate"], country["money"],
                                                              balance_change_desire, get_modifier(country, "stability"),
                                                              logic["min_stability"], logic["preferred_stability"])
    stability_change_desire = calculate_stability_change_desire(get_modifier(country, "stability"), logic["min_stability"],
                                                                logic["preferred_stability"], country["money"], balance_change_desire)
    militarization_change_desire = calculate_militarization_change_desire(get_modifier(country, "militarization"),
                                                                          logic["min_militarization"],logic["preferred_militarization"],
                                                                          country["money"], balance_change_desire)
    pops_growth_invest_desire = calculate_pops_growth_invest_desire(get_percent_pop_growth(country), logic["preferred_population_growth"],
                                                                    country["money"], balance_change_desire)
    mobil_law_change_desire = calculate_change_mobilization_law_desire(ml_id,
                                                                       get_modifier(country, "militarization"),
                                                                       get_manpower(player, country), logic["preferred_manpower_reserve"],
                                                                       get_total_army(country), get_total_population(player, country["id"]),
                                                                       get_modifier(country, "mobilization_percent",
                                                                                    -country["national_spirits"][2]["mobilization_percent"]))
    if not country.get("goal"):
        goal = calculate_goal(logic["militarization_desire"], logic["peaceful_desire"],
                              get_total_income(player, country), get_total_spending(player, country),
                              logic["preferred_balance"], get_manpower(player, country), get_total_army(country),
                              logic["preferred_manpower_reserve"], get_prod_units(player, country["id"]),
                              get_prod_units_consumption(country), country["armies"], get_is_pacifism(country))
        db.players.update_one({"tg_id":player["tg_id"], "countries.id":country["id"]},
                              {
                                  "$set":{
                                      "countries.$.goal":goal
                                  }
                              })
    else:
        if country["goal"] == "construct prod building":
            building_type = BUILDINGS[max(BUILDINGS, key=lambda b:BUILDINGS[b].get("prod_unit_inc"))]
            if country["money"] >= building_type["cost"]:
                city = random.choice(get_cities(player, country["id"]))
                build_in_city(player, city, building_type["_id"], country["id"])
        elif country["goal"] == "construct money building":
            building_type = BUILDINGS[max(BUILDINGS, key=lambda b:BUILDINGS[b].get("income_per_pop"))]
            if country["money"] >= building_type["cost"]:
                city = random.choice(get_cities(player, country["id"]))
                build_in_city(player, city, building_type["_id"], country["id"])
        elif country["goal"].startswith("construct new army of type"):
            a_type = ARMY_TYPES[ObjectId(country["goal"].split(":")[1])]
            if country["money"] >= a_type["cost"] and get_manpower(player, country) >= 100:
                conscript_army(player, country, str(a_type["_id"]))
        elif country["goal"].startswith("construct new army of type"):
            a_type = ARMY_TYPES[ObjectId(country["goal"].split(":")[1])]
            if country["money"] >= a_type["cost"]:
                conscript_army(player, country, str(a_type["_id"]))
        elif country["goal"].startswith("upgrade:"):
            splited = country["goal"].split(":")
            army = get_army(country, splited[1])
            cost = get_reorganization_cost(army, ARMY_TYPES[ObjectId(splited[3])])
            if country["money"] >= cost:
                reorganize_army(player,country["id"], army["army_id"], ObjectId(splited[3]))

    if tax_rate_change_desire > 1:
        change_tax_rate(player, country["id"], 0.05)
    elif tax_rate_change_desire < -1:
        change_tax_rate(player, country["id"], -0.05)
    elif -random.random() > tax_rate_change_desire:
        change_tax_rate(player, country["id"], -0.025)
    elif random.random() < tax_rate_change_desire:
        change_tax_rate(player, country["id"], 0.025)

    if stability_change_desire > 1:
        change_stability_growth(player, country["id"], 0.001)
    elif stability_change_desire < -1:
        change_stability_growth(player, country["id"], -0.001)
    elif -random.random() > stability_change_desire:
        change_stability_growth(player, country["id"], -0.0005)
    elif random.random() < stability_change_desire:
        change_stability_growth(player, country["id"], 0.0005)

    if militarization_change_desire > 1:
        change_militarization_growth(player, country["id"], 0.001)
    elif militarization_change_desire < -1:
        change_militarization_growth(player, country["id"], -0.001)
    elif -random.random() > militarization_change_desire:
        change_militarization_growth(player, country["id"], -0.0005)
    elif random.random() < militarization_change_desire:
        change_militarization_growth(player, country["id"], 0.0005)

    if pops_growth_invest_desire > 1:
        change_pops_invest(player, country["id"], 0.01)
    elif pops_growth_invest_desire < -1:
        change_pops_invest(player, country["id"], -0.01)
    elif -random.random() > pops_growth_invest_desire:
        change_pops_invest(player, country["id"], -0.005)
    elif random.random() < pops_growth_invest_desire:
        change_pops_invest(player, country["id"], 0.005)

    if country["polit_power"] > 150:
        if (mobil_law_change_desire > 1 or random.random() < mobil_law_change_desire) and ml_id + 1< len(MOBILIZATION_LAWS):
            reset_national_spirit(player, country["id"], 2, MOBILIZATION_LAWS[list(MOBILIZATION_LAWS)[ml_id+1]])
        elif (mobil_law_change_desire < -1 or -random.random() > mobil_law_change_desire) and ml_id + 1< len(MOBILIZATION_LAWS):
            reset_national_spirit(player, country["id"], 2, MOBILIZATION_LAWS[list(MOBILIZATION_LAWS)[ml_id-1]])
        db.players.update_one({"tg_id":player["tg_id"], "countries.id":country["id"]},
                              {
                                  "$inc":{
                                      "countries.$.polit_power": -150
                                  }
                              })
    print(f"Желание наращивать доходы: {balance_change_desire}")
    print(f"(Налоги) Желание: {tax_rate_change_desire}. Значение: {get_modifier(country, 'tax_rate')}")
    print(f"(Стабильность) Желание: {stability_change_desire}. Значение: +{get_modifier(country, 'stability_growth')}/{get_modifier(country, 'stability')}")
    print(f"(Милитаризация) Желание: {militarization_change_desire}. Значение: +{get_modifier(country, 'militarization_growth')}/{get_modifier(country, 'militarization')}")
    print(f"(Население) Желание: {pops_growth_invest_desire}. Значение: +{get_percent_pop_growth(country)}/{get_total_population(player, country['id'])}")
    print(f"(Призыв) Желание: {mobil_law_change_desire}. Значение: {get_modifier(country, 'mobilization_percent')}")
    print(f"Доходы: {get_total_income(player,country)}")
    print(f"Расходы: {get_total_spending(player,country)}")

def calculate_desire(logic, d_type, value):
    if value < logic[f"min_{d_type}"]:
        return 1
    elif value < logic[f"preferred_{d_type}"]:
        return value / logic[f"preferred_{d_type}"]
    else:
       return -logic[f"preferred_{d_type}"] / value

