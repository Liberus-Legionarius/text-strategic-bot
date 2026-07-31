from services.bot import bot, db
from services.constants import get_player, get_modifier, get_country
from services.math.economy_math import get_total_spending, get_total_income
from handlers.ingame_panels.state_panel import open_state_panel
from dateutil.relativedelta import relativedelta

@bot.callback_query_handler(func= lambda call: call.data == "end_move")
def callback_end_move(call):
    bot.answer_callback_query(call.id)
    player = get_player(call.from_user)
    player_country = get_country(player, 0)
    balance = get_total_income(player,player_country) - get_total_spending(player, player_country)
    polit_power_gain = get_modifier(player_country, "polit_power_gain_flat")
    polit_power_modifier = get_modifier(player_country, "polit_power_gain_modifier", 1)
    pop_growth = (get_modifier(player_country, "population_growth") + get_modifier(player_country, "population_growth_invest")) * get_modifier(player_country, "stability", 0.35) + 1
    print(pop_growth)

    date = player["date"] + relativedelta(months = 1)
    db.players.update_one({"tg_id":call.from_user.id},
                          {
                              "$inc":{
                                  "countries.0.money":balance,
                                  "countries.0.polit_power":polit_power_gain * polit_power_modifier,
                                  "step":1,

                              },
                              "$set":{
                                  "ai_plot":None,
                                  "date":date
                              }
                          })
    db.cities.update_one({"player_id":call.from_user.id, "owner":0},
                         {
                             "$mul":{
                                 "population":pop_growth
                             }
                         })
    open_state_panel(call.from_user, call.message.chat.id, call.message.message_id)