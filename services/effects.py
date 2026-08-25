from services.bot import db
from services.constants import ARMY_TYPES
from bson import ObjectId

from services.math.territory_math import get_cities, get_city_by_name, build_in_city

effects = {
    "money": "Эффект, меняющий количество денег в казне. Рекомендуется увеличивать или уменьшать на значения, кратные доходу.",
    "polit_power": "Эффект, меняющий политическую власть. Небольшое политическое действие отнимает 15-25 единиц, а крупные влияние политической власти могут расходовать по 200-250 единиц.",
    "change_stability": "Эффект, меняющий стабильность государства. Меняется в долях единицы, то есть 0.05 это 5%, к примеру. Не делай слишком радикальные изменения.",
    "change_militarization": "Эффект, меняющий милитаризацию общества в государстве. Меняется в долях единицы, как стабильность. Если страна пацифична, то милитаризация меняется в отрицательном направлении.",
    "add_national_spirit": "Добавляет национальный дух, который совмещает в себе различные модификаторы. Значение является объектом с обязательным полем name, также можно использовать поле duration, чтобы остановить длительность в количестве ходов. Помимо обязательных полей обязательно должен присутствовать минимум один модификатор из modifiers_information.",
    "remove_national_spirit":"Удаляет национальный дух. Значение представляет из себя name национального духа к удалению.",
    "add_to_actions": "Эффект, позволяющий добавлять записи в летопись, которая в дальнейшем может использоваться для событий. Запись должна быть краткой с указанием номера шага, описанием типа события и выбора. Пауза между однотипными событиями должна быть не менее 3 шагов.",
    "destroy_army_unit": "Эффект, позволяющий уничтожить армейское подразделение. Значение указывает на army_id уничтожаемого подразделения.",
    "destroy_building": "Эффект, позволяющий уничтожить здание в городе. Значение представляет из себя объект с полями city_name (указывает на name города) и building_id (указывает на id уничтожаемого здания)",
    "create_army_unit": "Эффект, позволяющий создать армейское подразделение. Значение представляет из себя объект с полями name и type_id (указывает на _id выбранного типа), опционально может быть поле is_free со значением true, если рекруты для подразделения добавляются к общему количеству.",
    "create_building": "Эффект, позволяющий создать здание. Значение это объект из двух полей: city_name и building_id с указанием на name города и _id здания соответственно.",
    "change_population": "Эффект, позволяющий изменить население в городе. Значение является объектом из полей city_name (name города) и population (число, на которое меняется население).",
    "add_mark_to_city": "Эффект, позволяющий отметить город определённым тэгом, который может быть использован в дальнейшем. Значение является объектом из полей city_name (имя города) и tag (тэг, который ставится на город).",
    "remove_mark_from_city": "Эффект, позволяющий убрать тэг с города. Значение - объект с полями city_name (название города) и tag (название тэга, который будет удалён).",
    "add_mark_to_country": "Эффект, позволяющий отметить страну определённым тэгом, который может быть использован в дальнейшем. Значение является объектом из полей country_id (id страны) и tag (тэг, который ставится на страну).",
    "remove_mark_from_country": "Эффект, позволяющий убрать тэг со страны. Значение - объект с полями country_id (id страны) и tag (название тэга, который будет удалён).",
    "destroy_country":"Эффект, который разрушает выбранную страну, при этом города теряют 75% населения. Значение - id страны, которая будет уничтожена.",
    "rename_country":"Эффект, позволяющий переименовать страну. Значение - объект с полями countryname (новое короткое название страны) и full_countryname (новое полное название страны).",
    "rename_city":"Эффект, позволяющий переименовать город. Значение - объект, состоящий из полей city_name (название города) и new_name (новое название города)",
    "move_capital":"Эффект, позволяющий сменить столицу. Значение - название города, в который будет перемещена столица.",

}

def on_effect(effect, value, player, country):
    if effect == "money":
        db.players.update_one({"tg_id":player["tg_id"]},
                              {
                                  "$inc":{f"countries.{country['id']}.money":value}
                              })
    elif effect == "polit_power":
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$inc": {f"countries.{country['id']}.polit_power": value}
                              })
    elif effect == "change_stability":
        db.players.update_one({"tg_id": player["tg_id"], "countries.id":0},
                              {
                                  "$inc": {f"countries.$.national_spirits.0.stability": value}
                              })
    elif effect == "change_militarization":
        db.players.update_one({"tg_id": player["tg_id"], "countries.id":0},
                              {
                                  "$inc": {f"countries.$.national_spirits.0.militarization": value}
                              })
    elif effect == "add_national_spirit":
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {f"countries.{country['id']}.national_spirits": value}
                              })
    elif effect == "remove_national_spirit":
        db.players.update_one({"tg_id":player["tg_id"]},
                              {
                                  "$pull":{f"countries.{country['id']}.national_spirits.name":value}
                              })
    elif effect == "add_to_actions":
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {f"actions": value}
                              })
    elif effect == "destroy_army_unit":
        army = next((army for army in country["army"] if str(army["id"]) == str(value)), None)
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$pull": {f"countries.{country['id']}.army": army}
                              })
    elif effect == "destroy_building":
        city = get_city_by_name(player, value["city_name"])
        b = next((b for b in city["buildings"] if b["id"] == value["building_id"]), None)
        db.players.update_one({"tg_id": player["tg_id"], "cities.name":value["city_name"]},
                              {
                                  "$pull": {"cities.$.buildings": b}
                              })
    elif effect == "create_army_unit":
        i = max(country["armies"], key=lambda a: a["army_id"])["army_id"] + 1
        a_type = ARMY_TYPES[ObjectId(value["type_id"])]
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "countries.0.armies": {
                                          "army_id": i,
                                          "name": f"{value['name']}",
                                          "size": 1,
                                          "hp": a_type["hp"],
                                          "morale": a_type["morale"],
                                          "type_id": ObjectId(value["type_id"])
                                      }
                                  }
                              })
    elif effect == "create_building":
        build_in_city(player, get_city_by_name(player, value["city_name"]), value["building_id"], 0, True)
    elif effect == "change_population":
        db.players.update_one({"tg_id": player["tg_id"], "cities.name":value["city_name"]},
                             {
                                 "$inc": {f"cities.$.population": value["population"]}
                             })
    elif effect == "add_mark_to_city":
        db.players.update_one({"tg_id":player["tg_id"], "cities.name":value["city_name"]},
                              {
                                  "$push":{f"cities.$.tags": value["tag"]}
                              })
    elif effect == "remove_mark_from_city":
        db.players.update_one({"tg_id": player["tg_id"], "cities.name": value["city_name"]},
                              {
                                  "$pull": {f"cities.$.tags": value["tag"]}
                              })
    elif effect == "add_mark_to_country":
        db.players.update_one({"tg_id": player["tg_id"], "countries.id": value["country_id"]},
                              {
                                  "$push": {f"countries.$.tags": value["tag"]}
                              })
    elif effect == "remove_mark_from_country":
        db.players.update_one({"tg_id": player["tg_id"], "countries.id": value["country_id"]},
                              {
                                  "$pull": {f"countries.$.tags": value["tag"]}
                              })
    elif effect == "destroy_country":
        db.players.update_many({"tg_id":player["tg_id"], "cities.owner": value},
                               {
                                   "$set":{
                                       "cities.$.owner":None,
                                       "cities.$.controller": None
                                   },
                                   "$mul":{
                                       "cities.$[].population":0.25
                                   }
                               })
    elif effect == "rename_country":
        db.players.update_one({"tg_id":player["tg_id"], "countries.id":country["id"]},
                              {
                                  "$set":{
                                      f"countries.$.countryname": value["countryname"],
                                      f"countries.$.full_countryname": value["full_countryname"],
                                  }
                              })
    elif effect == "rename_city":
        db.players.update_one({"tg_id":player["tg_id"], "cities.name":value["city_name"]},
                              {
                                  "$set":{
                                      "cities.$.name":value["new_name"]
                                  }
                              })
    elif effect == "move_capital":
        db.players.update_one({"tg_id":player["tg_id"], "countries.id":country["id"]},
                              {
                                  "$set":{
                                      "countries.$.capital":value
                                  }
                              })
