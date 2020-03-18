import json
import os

import pandas as pd
#
#
# def create_type_tags():
#     a = pd.read_json('RePoE-master/RePoE/data/mod_types.json')
#     a = a.transpose()
#     a['name'] = a.index
#     a.index = range(len(a))
#     possible_tags = ['poison', 'minion', 'jewellery_elemental', 'gem_level', 'life', 'cold', 'jewellery_quality_ignore',
#                      'lightning', 'jewellery_attribute', 'jewellery_caster', 'jewellery_attack', 'bleed',
#                      'flat_life_regen', 'fire', 'jewellery_defense', 'elemental', 'jewellery_resistance', 'mana',
#                      'aura', 'jewellery_resource', 'defences', 'physical', 'speed', 'attack', 'vaal', 'chaos', 'caster']
#     tags_wanted = ['jewellery_elemental', 'gem_level', 'life', 'jewellery_caster', 'fire', 'jewellery_defense',
#                    'elemental', 'jewellery_resistance', 'defences', 'speed', 'caster']
#     return a


def get_dict_from_input(input_type: str) -> dict:
    names = []
    values = []
    new_input = input(f'Want to add {input_type} base filter? [Y/N]')
    while new_input == 'Y':
        names.append(input(f'{input_type} name: '))
        values.append(input(f'{input_type} value: '))
        new_input = input('Add new input? [Y/N]')
        while new_input != 'Y' and new_input != 'N':
            print('Please insert "Y" or "N"')
            new_input = input('Add new input? [Y/N]')
    if names:
        input_values = {k: v for k, v in zip(names, values)}
    else:
        input_values = {}
    return input_values


def get_item_class_from_input():
    item_class = []
    new_input = input(f'Want to add item class base filter? [Y/N]')
    while new_input == 'Y':
        item_class.append(input('Type item class: '))
        new_input = input('Add new input? [Y/N]')
        while new_input != 'Y' and new_input != 'N':
            print('Please insert "Y" or "N"')
            new_input = input('Add new input? [Y/N]')
    item_class = '|'.join(item_class)
    return item_class


def get_and_values():
    and_values = {
        'item_class': input('Type item class to filter: '),
        'mods': get_dict_from_input('mod'),
        'props': get_dict_from_input('prop')
    }
    return and_values


def get_alternative_values():
    alt_values = [
        {
            'mods': {
                'pseudo_maximum_life': 50
            },
            'props': {
                'Evasion Rating': 200
            }
        },
        {
            'mods': {
                'pseudo_maximum_life': 50
            },
            'props': {
                'Armour Rating': 200
            }
        },
        {
            'props': {
                'Energy Shield': 150
            }
        },
    ]
    return alt_values


def save_filter_model(filter_model):
    if isinstance(filter_model, dict):
        filter_model = [filter_model]
    with open('filters.json', 'w') as f:
        json.dump(filter_model, f)


def update_filter_model(filter_model: dict):
    # TODO: Check if filter model is already in filters.json
    with open('filters.json', 'r') as f:
        filters = json.load(f)
    filters.append(filter_model)
    save_filter_model(filters)


def save_or_update_filter_model(filter_model: dict):
    if 'filters.json' in os.listdir():
        update_filter_model(filter_model)
    else:
        save_filter_model(filter_model)


def create_filter_model():
    and_dict = get_and_values()
    or_values = get_alternative_values()
    filter_model = {
        'AND': and_dict,
        'OR': or_values
    }
    save_or_update_filter_model(filter_model)
    return filter_model


def create_filters_from_filter_model(raw_filter: dict) -> list:
    new_filters = []
    and_item_class = raw_filter['AND']['item_class']
    and_mods = raw_filter['AND']['mods']
    and_prop = raw_filter['AND']['props']
    for key, value in raw_filter.items():
        if key == 'OR':
            for alternative in value:
                or_item_class = alternative.get('item_class', None)
                or_mods = alternative.get('mods', {})
                or_prop = alternative.get('props', {})
                filter_item_class = '|'.join([and_item_class, or_item_class]) if or_item_class else and_item_class
                filter_mods = {**and_mods, **or_mods}
                filter_prop = {**and_prop, **or_prop}
                new_filters.append({
                    'item_class': filter_item_class,
                    'mods': filter_mods,
                    'props': filter_prop,
                })
    if not new_filters:
        new_filters = [{
            'item_class': and_item_class,
            'mods': and_mods,
            'prop': and_prop,
        }]
    return new_filters


def filter_item():
    wanted_items = []
    # Filter AND must always exist, even if blank
    test_filter = create_filter_model()
    filters = create_filters_from_filter_model(test_filter)
    pass


if __name__ == '__main__':
    filter_item()
