from bot import bot
import handlers.start
import handlers.texting
import services.callbacks.callback_state_panels
import services.callbacks.callback_economy_panels
import services.callbacks.callback_territory_panels
import services.callbacks.callback_army_panels
from constants import set_buildings, set_army_types, set_mobilization

set_buildings()
set_army_types()
set_mobilization()

bot.infinity_polling()