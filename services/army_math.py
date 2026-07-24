from constants import ARMY_TYPES, MOBILIZATION_LAWS
from services.territory_math import get_total_population

def get_army_power(player):
    return sum(
        ARMY_TYPES[army["type"]]["power"]
        for army in player["armies"]
    )

def get_total_army(player):
    return len(player["armies"])

def get_manpower(player):
    return get_total_population(player) / (1 if MOBILIZATION_LAWS[player["mobilization_laws"]]['women_at_war'] else 2) * MOBILIZATION_LAWS[player["mobilization_laws"]]['percent']

def get_manpower_percent(player):
    return  MOBILIZATION_LAWS[player["mobilization_laws"]]["percent"] * 100

def get_women_at_war(player):
    f = MOBILIZATION_LAWS[player["mobilization_laws"]]["women_at_war"]
    return 'разрешена' if f else 'запрещена'

def get_mob_law_title(player):
    return MOBILIZATION_LAWS[player["mobilization_laws"]]["title"]