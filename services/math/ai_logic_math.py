import random

from services.constants import MOBILIZATION_LAWS, ARMY_TYPES, get_is_pacifism
from bson import ObjectId

from services.math.army_math import get_army_type


def calculate_balance_change_desire(money, income, spending, preferred_balance_rel):
    desire = 0
    balance_abs = income - spending
    balance_rel = balance_abs/income
    if money + balance_abs < 0:
        desire += 0.75
    elif balance_abs < 0:
        desire += 10
    else:
        if balance_rel < preferred_balance_rel:
            desire += balance_rel / preferred_balance_rel
        else:
            desire -= 1 - preferred_balance_rel / balance_rel
    return desire

def calculate_tax_rate_change_desire(tax_rate, min_tr, max_tr, preferred_tr, money, balance_change_desire, stability, min_stability, preferred_stability):
    desire = 0
    if tax_rate < min_tr:
        desire += 0.75 * balance_change_desire
    elif tax_rate < preferred_tr:
        desire += tax_rate / preferred_tr * balance_change_desire
    elif max_tr > tax_rate >= preferred_tr:
        desire -= (tax_rate/preferred_tr) * (tax_rate/max_tr) * balance_change_desire
    else:
        desire -= 0.75 - balance_change_desire
    if money < 0:
        desire += 0.75
    if stability < min_stability:
        desire -= 0.75 - balance_change_desire
    elif 1 > stability > preferred_stability:
        desire += 0.25 * (1 + stability / preferred_stability) * balance_change_desire
    else:
        desire +=10
    return desire

def calculate_stability_change_desire(stab, min_stab, pref_stab, money, balance_change_desire):
    desire = 0
    if stab < min_stab:
        desire += 1 + 0.15 * -balance_change_desire
    elif stab < pref_stab:
        desire += 0.5 * stab/pref_stab + 0.15 * -balance_change_desire
    elif 100 > stab > pref_stab:
        desire -= 0.35 * stab/pref_stab - 0.15 * -balance_change_desire
    else:
        desire -= 5
    if money < 0:
        desire -= 0.75 - 0.25 * -balance_change_desire
    return desire

def calculate_militarization_change_desire(mil, min_mil, pref_mil, money, balance_change_desire):
    desire = 0
    if mil < min_mil:
        desire += 1 + 0.15 * -balance_change_desire
    elif mil < pref_mil:
        desire += 0.5 * mil/pref_mil + 0.15 * -balance_change_desire
    elif 100 > mil > pref_mil:
        desire -= 0.35 * mil/pref_mil - 0.15 * -balance_change_desire
    else:
        desire -= 5
    if money < 0:
        desire -= 0.75 - 0.25 * -balance_change_desire
    return desire

def calculate_pops_growth_invest_desire(pops_growth, pref_growth, money, balance_change_desire):
    desire = 0
    if pops_growth < pref_growth:
        desire += pops_growth/pref_growth * 0.35 + -balance_change_desire * 0.15
    elif pops_growth < pref_growth * 2:
        desire -= pops_growth/pref_growth * 0.25 - -balance_change_desire * 0.1
    if money < 0:
        desire -= 0.75 - 0.25 * -balance_change_desire

    return desire

def calculate_change_mobilization_law_desire(cur_mobil_law_id, mil, cur_reserve, pref_rel_reserve, army_size, population, mobil_percent_bonus):
    desire = 0

    cur_rel_reserve = cur_reserve/(army_size*100)
    if cur_rel_reserve < 0:
        desire += 1 * (mil/0.55)
    else:
        if cur_rel_reserve < pref_rel_reserve:
            desire += 0.5 * (1 - cur_rel_reserve/pref_rel_reserve) + 0.1 * mil/0.55
        else:
            lower_ml = MOBILIZATION_LAWS[next(ml for i, ml in enumerate(MOBILIZATION_LAWS) if i + 1 == cur_mobil_law_id)]
            manpower_lower = (population / (1 if lower_ml['women_at_war'] else 2) *
                              (mobil_percent_bonus + lower_ml["mobilization_percent"]) - army_size)
            if manpower_lower/army_size < pref_rel_reserve:
                desire = 0
            else:
                desire -= 5
    return desire

def calculate_goal(mil_f, peace_f, income, spending, pref_balance_rel, manpower_abs, army_size, pref_manpower_rel, prod_units, prod_units_cons, armies, is_pacifism):
    balance = income-spending
    balance_rel = balance/income
    manpower_rel = manpower_abs/(army_size*100)
    if is_pacifism:
        mil_f = 0
        peace_f = 1
    else:
        mil_f = ((mil_f * (balance_rel/pref_balance_rel - 1)) *
                 (prod_units/prod_units_cons if not prod_units_cons == 0 else 1 + 0.1 * prod_units) *
                 (0 if manpower_abs < 250 else manpower_rel/pref_manpower_rel))
        peace_f = ((peace_f * (1 - balance_rel/pref_balance_rel)) *
                   (prod_units_cons/prod_units if prod_units > prod_units_cons else 1 + (1-(prod_units/prod_units_cons if not prod_units_cons == 0 else 0))))
    print(f"Мир:{peace_f}\nВойна:{mil_f}")
    if peace_f > mil_f:
        if prod_units < prod_units_cons:
            return "construct prod building"
        else:
            return "construct money building"
    else:
        if len(armies) > 1:
            best_army_type= ARMY_TYPES[list(ARMY_TYPES)[-1]]["_id"]
            worst_army = None
            for army in armies:
                if worst_army is None or get_army_type(worst_army)["power"] > get_army_type(army)["power"]:
                    worst_army = army
            if best_army_type == worst_army["type_id"]:
                return f"construct new army of type:{best_army_type}"
            return f"upgrade:{worst_army['army_id']}:to:{best_army_type}"
        else:
            return f"construct new army of type:{ARMY_TYPES[list(ARMY_TYPES)[-1]]['_id']}"