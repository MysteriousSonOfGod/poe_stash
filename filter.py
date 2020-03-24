import json
import os
import re

import pandas as pd
from loguru import logger
import numpy as np
from item_treatment import get_items

#
#
# def create_type_tags(): a = pd.read_json('RePoE-master/RePoE/data/mod_types.json') a = a.transpose() a['name'] =
# a.index a.index = range(len(a)) possible_tags = ['poison', 'minion', 'jewellery_elemental', 'gem_level', 'life',
# 'cold', 'jewellery_quality_ignore', 'lightning', 'jewellery_attribute', 'jewellery_caster', 'jewellery_attack',
# 'bleed', 'flat_life_regen', 'fire', 'jewellery_defense', 'elemental', 'jewellery_resistance', 'mana', 'aura',
# 'jewellery_resource', 'defences', 'physical', 'speed', 'attack', 'vaal', 'chaos', 'caster'] tags_wanted = [
# 'jewellery_elemental', 'gem_level', 'life', 'jewellery_caster', 'fire', 'jewellery_defense', 'elemental',
# 'jewellery_resistance', 'defences', 'speed', 'caster'] return a


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
    # and_values = {
    #     'item_class': get_item_class_from_input or '',
    #     'mods': get_dict_from_input('mod') or {},
    #     'props': get_dict_from_input('name') or {}
    # }
    and_values = {
        'item_class': 'boots',
        'mods': {'MovementVelocity': 10},
        'props': {'Evasion Rating': 0,
                  'Armour': 0,
                  'Energy Shield': 0}
    }
    return and_values


def get_alternative_values():
    # new_alt_values = []
    # new_input = input(f'Want to add alt values to base filter? [Y/N]')
    # while new_input == 'Y':
    #     alt_values = {
    #         'item_class': get_item_class_from_input or '',
    #         'mods': get_dict_from_input('mod') or {},
    #         'props': get_dict_from_input('name') or {}
    #     }
    #     new_alt_values.append(alt_values)
    #     while new_input != 'Y' and new_input != 'N':
    #         print('Please insert "Y" or "N"')
    #         new_input = input('Add new input? [Y/N]')
    alt_values = [
        {
            'props': {
                'Evasion Rating': 0
            }
        },
        {
            'props': {
                'Armour': 0
            }
        },
        {
            'props': {
                'Energy Shield': 0
            }
        },
    ]
    return alt_values


def open_filters_files(path: str):
    with open(path, 'r') as f:
        filters = json.load(f)
    return filters


def save_filter_model(filter_model):
    with open('filters.json', 'w') as f:
        json.dump(filter_model, f)


def update_filter_model(filter_model: dict):
    with open('filters.json', 'r') as f:
        filters = json.load(f)
    filters = {**filters, **filter_model}
    save_filter_model(filters)


# noinspection PyArgumentList
def save_or_update_filter_model(filter_model: dict):
    if 'filters.json' in os.listdir():
        update_filter_model(filter_model)
    else:
        save_filter_model(filter_model)


def create_filter_model(filter_name: str):
    and_dict = get_and_values()
    or_values = get_alternative_values()
    filter_model = {
        filter_name: {
            'AND': and_dict,
            'OR': or_values
        }
    }
    save_or_update_filter_model(filter_model)
    return filter_model


def create_filters_from_filter_model(raw_filter: dict, filter_name: str) -> list:
    new_filters = []
    raw_filter = raw_filter[filter_name]
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
            'name': and_prop,
        }]
    return new_filters


def compare_item_class(filter_item_class: str, item_item_class: str) -> bool:
    """
    Filter_item_class is a regex string, so we are going to use regex to check for the item_class
    :param filter_item_class: str
    :param item_item_class: str
    :return:
    """
    if re.match(filter_item_class, item_item_class):
        return True
    else:
        return False


def compare_mods(filter_mods: dict, item_mods: list) -> bool:
    operator = '>'
    filter_df = pd.DataFrame(filter_mods.items(), columns=['type', 'filter_value'])
    item_df = pd.DataFrame(item_mods)
    if 'type' in item_df.columns:
        if filter_df['type'].isin(item_df['type']).any():
            filter_df_in_item = (filter_df.loc[filter_df['type'].isin(item_df['type']), :]
                                 .sort_values('type').reset_index(drop=True))
            item_df_in_filter = (item_df.loc[item_df['type'].isin(filter_df['type']), :]
                                 .sort_values('type').reset_index(drop=True))
            item_df_in_filter.loc[:, 'filter_value'] = filter_df_in_item.loc[:, 'filter_value']
            item_df_in_filter.loc[:, 'value_check'] = eval(f'np.where(item_df_in_filter.value {operator}'
                                                           f' item_df_in_filter.filter_value, True, False)')
            if item_df_in_filter['value_check'].all(axis=None):
                return True

        else:
            return False


def compare_props(filter_props: dict, item_props: list) -> bool:
    operator = '>'
    filter_df = pd.DataFrame(filter_props.items(), columns=['name', 'filter_value'])
    item_df = pd.DataFrame(item_props)
    if 'name' in item_df.columns:
        if filter_df['name'].isin(item_df['name']).any():
            filter_df_in_item = (filter_df.loc[filter_df['name'].isin(item_df['name']), :]
                                 .sort_values('name').reset_index(drop=True))
            item_df_in_filter = (item_df.loc[item_df['name'].isin(filter_df['name']), :]
                                 .sort_values('name').reset_index(drop=True))
            item_df_in_filter.loc[:, 'filter_value'] = filter_df_in_item.loc[:, 'filter_value']
            item_df_in_filter.loc[:, 'value_check'] = eval(f'np.where(item_df_in_filter.value {operator}'
                                                           f' item_df_in_filter.filter_value, True, False)')
            if item_df_in_filter['value_check'].all(axis=None):
                return True
        else:
            return False


def filter_item(filters: list, item: dict):
    for filter in filters:
        class_check = compare_item_class(filter.get('item_class'), item.get('item_class'))
        mods_check = compare_mods(filter.get('mods'), item.get('mods'))
        props_check = compare_props(filter.get('props'), item.get('props'))
        checks = [class_check, mods_check, props_check]
        if all(checks):
            return True
        else:
            return False


def get_wanted_items():
    wanted_items = []
    with open('data/test_stash.json', 'r') as f:
        tab = json.load(f)
    stash_items = get_items(tab)
    test_filter = create_filter_model()
    filters = create_filters_from_filter_model(test_filter)
    for item_name, item_values in stash_items.items():
        if filter_item(filters, item_values):
            wanted_items.append(item_name)
    return wanted_items


def main():
    filter_name = 'boots1'
    test_filter = create_filter_model(filter_name)
    filters = create_filters_from_filter_model(test_filter, filter_name)
    pass


if __name__ == '__main__':
    main()
