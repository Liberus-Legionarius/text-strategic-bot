from handlers.callbacks.callback_start import callback
from services.bot import bot
from services.constants import get_player, get_date_move, get_country, get_is_pacifism
from services.math.army_math import *
from services.math.economy_math import get_prod_units_consumption, get_prod_units
from services.math.spending_math import get_army_spending
from services.math.territory_math import get_total_population, get_cities
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from bson import ObjectId

ARMY_KB = InlineKeyboardMarkup(row_width=2)
ARMY_KB.add(InlineKeyboardButton("Политика призыва", callback_data = "army:mobilization:open"),
            InlineKeyboardButton("Армии", callback_data = "army:armies:open"),
            InlineKeyboardButton("Назад", callback_data = "state:open"))
BACK_TO_ARMIES_KB = InlineKeyboardMarkup()
BACK_TO_ARMIES_KB.add(InlineKeyboardButton("Вернуться к армиям", callback_data = "army:armies:open"))

def open_army_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Количество боевых подразделений: {get_total_army(player_country)}\n"
            f"Общая боевая мощь: {get_army_power(player_country)}"
            "\n\n"
            f"Затраты единиц производства: {get_prod_units_consumption(player_country)}\n"
            f"Всего единиц производства: {get_prod_units(player, 0)}\n"
            f"Баланс единиц производства: {get_prod_units(player, 0) - get_prod_units_consumption(player_country)}"
            "\n\n"
            f"Расходы на содержание армии: {get_army_spending(player_country):.2f} монет в ход"
            "\n\n"
            f"Общее население: {get_total_population(player, player_country['id']):.0f}\n"
            f"Мобилизационный резерв: {int(get_manpower(player, player_country))}\n"
            f"Служба для женщин: {get_women_at_war(player_country)}"
            )
    bot.edit_message_text(
            text,
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = ARMY_KB
    )

def open_mobilization_panel(user, chat_id, message_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Общее население страны: {get_total_population(player, player_country['id'])}\n"
                f"Мобилизационный резерв: {int(get_manpower(player, player_country))}"
                "\n\n"
                "Наши законы в отношении призыва:\n"
                f"\t- Закон о призыве: {player_country['national_spirits'][2]['title']}\n"
                f"\t\t- Процент военнообязанных: {get_manpower_percent(player_country):.2f}%\n"
                f"\t\t- Статус женской службы: {get_women_at_war(player_country)}")

        mobilization_kb = InlineKeyboardMarkup(row_width=1)
        if get_is_pacifism(player_country):
                text += ("\n\n"
                         "К сожалению, вы пацифист, а это означает, что вам запрещено менять законы о призыве и как-либо расширять свою армию.\n"
                         "Впрочем, если у вас уже есть армия, никто не запрещает её реорганизовать в более профессиональные подразделения.")
        else:
                for law_id, law in MOBILIZATION_LAWS.items():
                        if not player_country["national_spirits"][2]["_id"] == str(law_id) and not law.get("is_pacifism"):
                                mobilization_kb.add(f'{InlineKeyboardButton(law["title"])} (150 пп)', callback_data = f"army:mobilization:{str(law_id)}")
        mobilization_kb.add(InlineKeyboardButton("Вернуться", callback_data = "army:base:open"))
        bot.edit_message_text(
                text,
                chat_id = chat_id,
                message_id = message_id,
                reply_markup = mobilization_kb
        )

def open_armies_panel(user, chat_id, message_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Количество боевых подразделений: {get_total_army(player_country)}\n"
                f"Общая боевая мощь: {get_army_power(player_country)}"
                "\n\n"
                f"Типы подразделений и их распределение:\n")

        for a_type in ARMY_TYPES.values():
                text += f'{str(a_type["title"])} - {len(list(filter(lambda unit: unit["type_id"] == a_type["_id"], player_country["armies"])))}\n'

        armies_kb = InlineKeyboardMarkup(row_width=2)
        for army in player_country["armies"]:
                armies_kb.add(InlineKeyboardButton(f"{army['name']} ({next((city for city in get_cities(player, player_country['id']) if city['_id'] == army['city_id']), None)['name']})",
                                                   callback_data = f"army:armies:{army['army_id']}"))

        armies_kb.row(InlineKeyboardButton("Назад", callback_data = "army:base:open"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=armies_kb
        )

def open_one_army_panel(user, chat_id, message_id, army_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        army = get_army(player_country, army_id)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Название подразделения: {army['name']}"
                "\n\n"
                f"{get_unit_info(player_country, army)}")

        one_army_kb = InlineKeyboardMarkup(row_width = 2)
        one_army_kb.add(InlineKeyboardButton("Реорганизовать", callback_data = f"army:armies:{army_id}:reorganize"),
                        InlineKeyboardButton("Расформировать", callback_data = f"army:armies:{army_id}:delete"),
                        InlineKeyboardButton("Переместить", callback_data = f"army:armies:{army_id}:move"),
                        InlineKeyboardButton("Провести вылазку", callback_data = f"army:campaign:{army_id}"))
        one_army_kb.row(InlineKeyboardButton("Назад", callback_data="army:armies:open"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=one_army_kb
        )

def open_campaign_panel(user, chat_id, message_id, army_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        army = get_army(player_country, army_id)
        city = next((c for c in get_cities(player, player_country['id']) if c["_id"] == army["city_id"]), None)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Наше подразделение {army['name']}, расположенное в городе {city['name']} совершит исследовательскую вылазку.\n"
                "В результате мы сможем обнаружить что-то из этого списка:\n"
                "\t\t\t- Руины. Никем не занятые территории разрушенного много веков назад города, в котором можно будет найти бункер с выжившими, пустой бункер с полезными нам припасами или ничего. В любом случае руины можно будет заселить.\n"
                "\t\t\t- Неизвестное государство. То есть такие же выжившие, как и мы, которые уже основали собственное государство. Если нам повезёт, местное население будет мирным и согласится на сотрудничество (в лучшем случае, если их положение тяжёлое, они принесут нам присягу), в противном случае мы найдём себе нового врага, возможно, даже будем вынуждены подчиниться более могущественной державе.\n"
                "\t\t\t- Ничего. Просто выжженные пустоши... Совсем ничего."
                "\n\n"
                f"Нужно лишь определить субсидирование вылазки...\n"
                f"На данный момент у нас в казне {player_country['money']:.2f} монет")

        campaign_kb = InlineKeyboardMarkup()
        campaign_kb.add(InlineKeyboardButton("250 монет (шанс успеха 15%)", callback_data=f"army:campaign:{army_id}:250"),
                             InlineKeyboardButton("500 монет (шанс успеха 25%)", callback_data=f"army:campaign:{army_id}:500"),
                             InlineKeyboardButton("1000 монет (шанс успеха 55%)", callback_data=f"army:campaign:{army_id}:1000"),
                             InlineKeyboardButton("2500 монет (шанс успеха 75%)", callback_data=f"army:campaign:{army_id}:2500"),
                             InlineKeyboardButton("Вернуться", callback_data=f"army:armies:{army_id}"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=campaign_kb
        )

def open_campaign_started_panel(user, chat_id, message_id, city_name, army_name):
        text = (f'Мы отправили армию "{army_name}" из города {city_name} в исследовательскую вылазку. Надеемся, они вернутся с хорошими новостями... \n'
                'Если вообще вернутся.')

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=BACK_TO_ARMIES_KB
        )

def open_delete_confirmation(user, chat_id, message_id, army_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        text = "Вы уверены, что хотите расформировать подразделение?"

        deletion_kb = InlineKeyboardMarkup()
        deletion_kb.row(InlineKeyboardButton("Да", callback_data= f"army:armies:{army_id}:delete:yes"),
                        InlineKeyboardButton("Нет", callback_data= f"army:armies:{army_id}:delete:no"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=deletion_kb
        )

def open_army_reorganize(user, chat_id, message_id, army_id):
        player = get_player(user)
        player_country = get_country(player, 0)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Ваша казна составляет {player_country['money']}\n"
                "Выберите один из предложенных типов армейских подразделений.\n")
        army = get_army(player_country, army_id)
        types_kb = InlineKeyboardMarkup(row_width = 3)
        for army_type in ARMY_TYPES.values():
                if not army_type["_id"] == army["type_id"]:
                        types_kb.add(InlineKeyboardButton(f'{army_type["title"]} ({get_reorganization_cost(army, army_type):.2f})', callback_data = f"army:armies:{army_id}:reorganize:{army_type['_id']}"))
        types_kb.row(InlineKeyboardButton("Вернуться", callback_data = f"army:armies:{army_id}"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=types_kb
        )

def open_army_reorganize_unit_info(user, chat_id, message_id, army_id, type_id):
        player = get_player(user)
        player_country = get_country(player, 0)
        army = get_army(player_country, army_id)
        army_type = ARMY_TYPES[ObjectId(type_id)]
        text = (f"{get_date_move(player)}"
                "\n\n"
                f"{get_unit_reorg_info(player_country, army, army_type)}"
                "\n\n"
                f'Стоимость реорганизации: {get_reorganization_cost(army, army_type):.2f}'
                "\n\n"
                "Вы согласны на реорганизацию данного подразделения?")

        reorganize_kb = InlineKeyboardMarkup()
        reorganize_kb.row(InlineKeyboardButton("Да", callback_data = f"army:armies:{army_id}:reorganize:{type_id}:yes"),
                          InlineKeyboardButton("Нет", callback_data = f"army:armies:{army_id}"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reorganize_kb
        )

def open_army_move_selection(user, chat_id, message_id, army_id):
        pass

def open_army_creation_panel(user, chat_id, message_id, city_id):
        player = get_player(user)
        player_country = get_country(player, 0)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Типы армейских юнитов: {get_unit_types_info_foreach(player_country)}"
                f"Ваша казна составляет: {player_country['money']} монет")

        types_kb = InlineKeyboardMarkup(row_width=3)
        for army_type in ARMY_TYPES.values():
                types_kb.add(InlineKeyboardButton(
                        f'{army_type["title"]} ({army_type["cost"]:.2f})',
                        callback_data=f"army:create:{city_id}:{army_type['_id']}"))
        types_kb.row(InlineKeyboardButton("Вернуться", callback_data=f"territory:cities:{city_id}"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=types_kb
        )

def get_unit_reorg_info(country, army, new_type):
        was_type = get_army_type(army)
        return (f"Тип: {was_type['title']} --> {new_type['title']}\n"
                f"Боевая мощь: {was_type['power']} --> {new_type['power']:}"
                "\n\n"
                f"Очки здоровья: {was_type['hp'] * get_modifier(country, 'hp_modifier', 1):.2f} --> {new_type['hp'] * get_modifier(country, 'hp_modifier', 1):.2f}\n"
                f"Боевой дух: {was_type['morale'] * get_modifier(country, 'morale_modifier', 1):.2f} --> {new_type['morale'] * get_modifier(country, 'morale_modifier', 1):.2f}"
                "\n\n"
                f"Атака: {was_type['attack'] * get_modifier(country, 'attack_modifier', 1):.2f} --> {new_type['attack'] * get_modifier(country, 'attack_modifier', 1):.2f}\n"
                f"Бронебойность: {was_type['armour_piercing']} --> {new_type['armour_piercing']}\n"
                f"Защита: {was_type['defense'] * get_modifier(country, 'defense_modifier', 1):.2f} --> {new_type['defense'] * get_modifier(country, 'defense_modifier', 1):.2f}\n"
                f"Является бронированным: {get_is_armour(was_type)} --> {get_is_armour(new_type)}"
                "\n\n"
                f"Противодействовал: {get_army_counteracts(was_type)}\n"
                f"Будет противодействовать: {get_army_counteracts(new_type)}"
                "\n\n"
                f"Расходы производства: {was_type['prod_units_consumption']} --> {new_type['prod_units_consumption']}\n"
                f"Ежемесячные расходы: {was_type['per_unit_spending'] * get_modifier(country, 'army_maintenance', 1):.2f} --> {new_type['per_unit_spending'] * get_modifier(country, 'army_maintenance', 1):.2f}")

def get_unit_info(country, army):
        a_type = get_army_type(army)
        return (f"Тип: {a_type['title']}\n"
                f"Боевая мощь: {a_type['power']}"
                "\n\n"
                f"Очки здоровья: {a_type['hp'] * get_modifier(country, 'hp_modifier', 1):.2f}\n"
                f"Боевой дух: {a_type['morale'] * get_modifier(country, 'morale_modifier', 1):.2f}"
                "\n\n"
                f"Атака: {a_type['attack'] * get_modifier(country, 'attack_modifier', 1):.2f}\n"
                f"Бронебойность: {a_type['armour_piercing']}\n"
                f"Защита: {a_type['defense'] * get_modifier(country, 'defense_modifier', 1):.2f}\n"
                f"Является бронированным: {get_is_armour(a_type)}"
                "\n\n"
                f"Противодействует: {get_army_counteracts(a_type)}"
                "\n\n"
                f"Расходы производства: {a_type['prod_units_consumption']}\n"
                f"Ежемесячные расходы: {a_type['per_unit_spending'] * get_modifier(country, 'army_maintenance',1):.2f}\n\n")

def get_unit_types_info_foreach(country):
        text = ""
        for a_type in ARMY_TYPES.values():
                text += (f"\n{a_type['title']}\n"
                         f"Боевая мощь: {a_type['power']}\n"
                         f"Очки здоровья: {a_type['hp'] * get_modifier(country, 'hp_modifier', 1):.2f}\n"
                         f"Боевой дух: {a_type['morale'] * get_modifier(country, 'morale_modifier', 1):.2f}]\n"
                         f"Атака: {a_type['attack'] * get_modifier(country, 'attack_modifier', 1):.2f}\n"
                         f"Бронебойность: {a_type['armour_piercing']}\n"
                         f"Защита: {a_type['defense'] * get_modifier(country, 'defense_modifier', 1):.2f}\n"
                         f"Является бронированным: {get_is_armour(a_type)}\n"
                         f"Противодействует: {get_army_counteracts(a_type)}\n"
                         f"Расходы производства: {a_type['prod_units_consumption']}\n"
                         f"Ежемесячные расходы: {a_type['per_unit_spending'] * get_modifier(country, 'army_maintenance',1):.2f}\n\n")
        return text