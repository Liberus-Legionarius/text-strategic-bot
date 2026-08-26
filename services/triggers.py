from services.constants import get_modifier, get_is_pacifism
from services.math.army_math import get_manpower, get_total_soldiers, get_women_at_war
from services.math.economy_math import get_total_income, get_total_spending
from services.math.territory_math import get_cities, get_total_population, get_city_by_name

triggers ={
    "stability":"Проверяет, что стабильность страны доходит до данного показателя. В значении указывается нужная стабильность.",
    "militarization":"Проверяет, что милитаризация страны доходит до данного показателя. В значении указывается нужная милитаризация.",
    "polit_power":"Проверяет, что текущая политическая власть страны доходит до данного показателя. В значении указывается нужная политическая власть.",
    "money":"Проверяет, что в казне страны денег больше или равно данного показателя. В значении указывается нужное количество монет в казне.",
    "income":"Проверяет, что доход страны как минимум доходит до этого показателя. В значении указывается нужный доход.",
    "spending":"Проверяет, что расходы страны как минимум доходят до этого показателя. В значении указывается нужный объём расходов.",
    "income_balance_relation":"Проверяет, что отношение ежемесячного баланса к доходам как минимум доходит до этого показателя. В значении указывается нужное отношение.",
    "money_balance":"Проверяет, что ежемесячный баланс как минимум доходит до этого показателя. В значении указывается нужный ежемесячный баланс.",
    "country_size":"Проверяет, что количество городов в стране как минимум доходит до этого показателя. В значении указывается нужное количество городов",
    "country_population":"Проверяет, что общее население страны как минимум доходит до этого показателя. В значении указывается нужное население.",
    "is_ideology_group":"Проверяет, что идеология государства относится к определённой идеологической группе. В значении указывается название идеологической группы.",
    "owns_city": "Проверяет, что данная страна владеет определённым городом. В значении указывается name нужного города.",
    "controls_city": "Проверяет, что данная страна контролирует определённый город. В значении указывается name нужного города.",
    "province_control_percentage": "Проверяет, что данная страна владеет как минимум определённым процентом городов в провинции. В значении указывается объект с полями province_name (name нужной провинции) и percentage (нужный процент в виде доли единицы).",
    "modifier_value": "Проверяет, что определённый модификатор в этой стране имеет как минимум данный показатель. В значении указывается объект с полями modifier (название модификатора) и value (значение модификатора).",
    "army_units_size":"Проверяет, что совокупное количество армейских подразделений страны как минимум доходит до этого показателя. В значении указывается нужное количество армейских подразделений.",
    "manpower_in_reserve":"Проверяет, что отношение количества призывников к численности солдат в армии как минимум доходит до этого показателя. В значении указывается нужное отношение количества резервистов к количеству военнослужащих.",
    "army_size":"Проверяет, что в армии служит как минимум столько человек, сколько указано в триггере. В значении указывается нужное количество военнослужащих.",
    "building_amount":"Проверяет, что во всех городах страны построено как минимум столько зданий определённого типа. В значении указывается объект с полями building_type (_id нужного типа зданий) и amount (количество зданий).",
    "is_building_in_city":"Проверяет, что конкретный город имеет конкретное здание. В значении указывается объект с полями city_name (name нужного города) и building_type (_id нужного типа зданий).",
    "is_pacifistic": "Проверяет значение модификатора is_pacifism. В значении указывается референсное значение true или false.",
    "is_women_can_serve": "Проверяет, разрешена или запрещена женская служба в государстве. В значении указывается референсное значение true или false.",
    "current_mobilization_law": "Проверяет, что закон о призыве в государстве является данным. В значении указывается _id закона о призыве."
}

def check_trigger(trigger, value, player, country):
    if trigger == "stability":
        return get_modifier(country, "stability") >= value
    elif trigger == "militarization":
        return get_modifier(country, "militarization") >= value
    elif trigger == "polit_power":
        return country["polit_power"] >= value
    elif trigger == "money":
        return country["money"] >= value
    elif trigger == "income":
        return get_total_income(player, country) >= value
    elif trigger == "spending":
        return get_total_spending(player, country) >= value
    elif trigger == "income_balance_relation":
        income = get_total_income(player, country)
        spending = get_total_spending(player, country)
        return (income - spending)/income >= value
    elif trigger == "money_balance":
        return get_total_income(player, country) - get_total_spending(player, country) >= value
    elif trigger == "country_size":
        return len(get_cities(player, country["id"])) >= value
    elif trigger == "country_population":
        return get_total_population(player, country["id"]) >= value
    elif trigger == "is_ideology_group":
        return country["ideology_type"] == value
    elif trigger == "owns_city":
        return get_city_by_name(player, value)["owner"] == country["id"]
    elif trigger == "controls_city":
        return get_city_by_name(player, value)["controller"] == country["id"]
    elif trigger == "province_control_percentage":
        cities = [city for city in player["cities"] if city["province"] == value["province_name"]]
        return len([city for city in cities if city["owner"] == country["id"]])/len(cities) >= value["percentage"]
    elif trigger == "modifier_value":
        return get_modifier(country, value["modifier"]) >= value["value"]
    elif trigger == "army_units_size":
        return len(country["armies"]) >= value
    elif trigger == "manpower_in_reserve":
        return  get_manpower(player, country)/get_total_soldiers(country) >= value
    elif trigger == "army_size":
        return  get_total_soldiers(country) >= value
    elif trigger == "building_amount":
        buildings_a = 0
        for city in get_cities(player, country["id"]):
            buildings_a += next((b["amount"] for b in city["buildings"] if b["id"] == value["building_type"]), 0)
        return buildings_a >= value["amount"]
    elif trigger == "is_building_in_city":
        city = get_city_by_name(player, value["city_name"])
        return next((b for b in city["buildings"] if b["id"] == value["building_type"]), False)
    elif trigger == "is_pacifistic":
        return get_is_pacifism(country) == value
    elif trigger == "is_women_can_serve":
        return country["national_spirits"][2]["women_at_war"] == value
    elif trigger == "current_mobilization_law":
        return str(country["national_spirits"][2]["_id"]) == value
    return False