import random as rnd
import services.ai as ai
from services.bot import bot, db
from services.constants import get_player, get_modifier, get_country
from services.campaign_effects import CAMPAIGN_BONUS, CAMPAIGN_RESULT
from services.math.economy_math import get_total_spending, get_total_income
from handlers.ingame_panels.state_panel import open_state_panel
from dateutil.relativedelta import relativedelta
from services.math.spending_math import get_stability_growth, get_militarization_growth
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

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
        on_move_effects(player, player_country, call.from_user, call.message.chat.id, call.message.message_id)
    else:
        db.players.update_one({"tg_id":player["tg_id"]},
                              {
                                  "$inc": {"event_chance":0.33}
                              })
        on_move_effects(player, player_country, call.from_user, call.message.chat.id, call.message.message_id)


def on_move_effects(player, country, user, chat_id, message_id):
    balance = get_total_income(player, country) - get_total_spending(player, country)
    polit_power_gain = get_modifier(country, "polit_power_gain_flat")
    polit_power_modifier = get_modifier(country, "polit_power_gain_modifier", 1)
    pop_growth = ((get_modifier(country, "population_growth") +
                  get_modifier(country,"population_growth_invest")) *
                  get_modifier(country, "stability", 0.35) + 1)
    date = player["date"] + relativedelta(months=1)
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$inc": {
                                  "countries.0.money": balance,
                                  "countries.0.polit_power": polit_power_gain * polit_power_modifier,
                                  "countries.0.national_spirits.0.stability": get_stability_growth(country),
                                  "countries.0.national_spirits.0.militarization": get_militarization_growth(country),
                                  "step": 1,

                              },
                              "$set": {
                                  "ai_plot": None,
                                  "date": date
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
                                                      {"$eq": ["$$city.owner", 0]},
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
    open_state_panel(user, chat_id, message_id)