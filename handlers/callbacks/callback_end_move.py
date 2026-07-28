from services.bot import bot, db
from services.constants import get_player, get_modifier
from services.math.economy_math import get_total_spending, get_total_income
from handlers.ingame_panels.state_panel import open_state_panel
from dateutil.relativedelta import relativedelta

@bot.callback_query_handler(func= lambda call: call.data == "end_move")
def callback_end_move(call):
    bot.answer_callback_query(call.id)
    player = get_player(call.from_user)
    balance = get_total_income(player) - get_total_spending(player)
    polit_power_gain = get_modifier(player, "polit_power_gain_flat")
    polit_power_modifier = get_modifier(player, "polit_power_gain_modifier")
    pop_growth = get_modifier(player, "population_growth") + get_modifier(player, "population_growth_invest")
    date = player["date"] + relativedelta(months = 1)
    db.players.update_one({"tg_id":call.from_user.id},
                          {
                              "$inc":{
                                  "money":balance,
                                  "polit_power":polit_power_gain * (1+polit_power_modifier),
                                  "step":1,

                              },
                              "$mul":{
                                  "cities.$[].population":1+pop_growth
                              },
                              "$set":{
                                  "ai_plot":None,
                                  "date":date
                              }
                          })
    open_state_panel(call.from_user, call.message.chat.id, call.message.message_id)