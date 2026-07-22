from constants import ARMY_TYPES
from services.territory_math import get_total_population

def get_army_power(player):
    return sum(
        ARMY_TYPES[army["type"]]["power"]
        for army in player["armies"]
    )

def get_total_army(player):
    return len(player["armies"])

def get_manpower(player):
    law = player["mobilization_laws"]
    return get_total_population(player) / (1 if law['women_at_war'] else 2) * law['percent']

def get_manpower_percent(player):
    return  player["mobilization_laws"]["percent"] * 100

def get_women_at_war(player):
    f = player["mobilization"]["women_at_war"]
    return 'разрешена' if f else 'запрещена'