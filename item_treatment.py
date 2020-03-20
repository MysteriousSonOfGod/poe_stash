import asyncio
import re
import json
import itertools

import pandas as pd
from stash import AccountStash
from loguru import logger


def get_mods():
    logger.info('Reading mods file')
    with open('RePoE-master/RePoE/data/mods.json', 'r') as f:
        mods = json.load(f)
    return mods


def create_rare_mods_df(mods: dict) -> pd.DataFrame:
    logger.info('Creating mods df')
    mod_names = []
    groups = []
    types = []
    tags = []
    names = []
    min_stats = []
    max_stats = []
    mod_ids = []
    required_levels = []
    for item, value in mods.items():
        if value['domain'] == 'item':
            if value['generation_type'] == 'suffix' or value['generation_type'] == 'prefix':
                for weight in value['spawn_weights']:
                    for stat in value['stats']:
                        mod_name = item
                        group = value['group']
                        type = value['type']
                        name = value['name']
                        required_level = value['required_level']
                        mod_id = stat['id']
                        min_stat = stat['min']
                        max_stat = stat['max']
                        tag = weight['tag']
                        mod_names.append(mod_name)
                        groups.append(group)
                        types.append(type)
                        tags.append(tag)
                        names.append(name)
                        required_levels.append(required_level)
                        mod_ids.append(mod_id)
                        min_stats.append(min_stat)
                        max_stats.append(max_stat)
    df = pd.DataFrame({
        'mod_name': mod_names,
        'group': groups,
        'type': types,
        'tag': tags,
        'name': names,
        'required_level': required_levels,
        'mod_id': mod_ids,
        'min': min_stats,
        'max': max_stats,
    })
    # df.to_json('rare_mods.json', orient='records')
    return df


def get_stats_translations():
    logger.info('Reading translations file')
    with open('RePoE-master/RePoE/data/stat_translations.json', 'r') as f:
        stats_translations = json.load(f)
    return stats_translations


def create_translation_df(translations: dict) -> pd.DataFrame:
    logger.info('Creating translations df')
    formats = []
    strings = []
    ids = []
    for translation in translations:
        for mod in translation['English']:
            format = mod['format']
            string = mod['string']
            string = string.format(*format)
            id = translation['ids'][0]
            formats.append(format)
            strings.append(string)
            ids.append(id)
    df = pd.DataFrame({
        'id': ids,
        'format': formats,
        'string': strings
    })
    # df.to_json('translations.json', orient='records')
    return df


def get_test_stash():
    logger.info('Using test stash')
    with open("test_stash.json", 'r') as f:
        test_stash = json.load(f)
    return test_stash


def select_stash_tabs():
    return [0, 1, 2]


def remove_mods_based_on_item_class(item_class: str, rare_mods: pd.DataFrame) -> pd.DataFrame:
    classes_types_local_base = ['body', 'chest', 'helm', 'shield', 'boots', 'gloves']
    if item_class in ['ring', 'amulet', 'belt', 'quiver']:
        rare_mods = rare_mods[~rare_mods.type.str.contains('LocalBase')]
        rare_mods = rare_mods[~rare_mods.group.str.contains('Body|Chest|Helm|Boots|Gloves')]
        rare_mods = rare_mods[~rare_mods.mod_name.str.contains('Body|Chest|Helm|Boots|Gloves')]
    return rare_mods


def get_first_element_of_list_of_lists_or_self(x):
    if isinstance(x, list):
        if x:
            return list(itertools.chain(*x))[0]
        else:
            return x
    else:
        return x


def clean_properties_df(df: pd.DataFrame) -> pd.DataFrame:
    df['values'] = df['values'].map(get_first_element_of_list_of_lists_or_self)
    df.loc[:, 'values'] = df['values'].str.replace('%', '')
    df = df.rename(columns={'values': 'value'})
    if df['value'].str.contains('-').any():
        df = pd.concat([df, pd.DataFrame(df['value'].str.split('-', expand=True).values,
                                         columns=['min', 'max_value'])], axis=1)
        df = df.drop(['value', 'displayMode', 'type'], axis=1)
        df = df.rename(columns={'min': 'value'})
        df['max_value'] = pd.to_numeric(df['max_value'])
    else:
        df = df.drop(['displayMode', 'type'], axis=1)
    df = df.dropna(subset=['value'])
    df['value'] = pd.to_numeric(df['value'])
    return df


def get_item_properties(properties: list) -> list:
    logger.info('Creating item properties')
    new_properties = []
    phys_damage = 0
    elemental_damage = 0
    properties_df = pd.DataFrame(properties)
    properties = clean_properties_df(properties_df)
    if not properties.empty:
        for idx, row in properties.iterrows():
            prop_name = row['name']
            if prop_name == 'Physical Damage':
                phys_damage = sum([row['value'], row['max_value']])
            if prop_name == 'Elemental Damage':
                elemental_damage = sum([row['value'], row['max_value']])
            if prop_name == 'Attacks per Second':
                aps = row['value']
        if phys_damage > 0 or elemental_damage > 0:
            phys_dps = phys_damage/aps
            ele_dps = elemental_damage/aps
            all_dps = phys_dps + ele_dps
            new_properties = [{'name': 'Dps', 'value': all_dps}, {'name': 'Physical Dps', 'value': phys_dps},
                              {'name': 'Elemental Dps', 'value': ele_dps}]
    properties = properties.to_dict('records')
    return properties + new_properties


def create_item_mod(possible_mod_ids: list, item_mod: pd.Series, rare_mods: pd.DataFrame, mod_value: int) -> dict:
    logger.info('Creating item mods dict')
    for mod_id in possible_mod_ids:
        # Comparing mod with rare mods multiple times is expensive
        possible_mods = rare_mods[rare_mods.mod_id == mod_id]
        if len(possible_mods) > 0:
            for idx, row in possible_mods.iterrows():
                min_value = row['min']
                max_value = row['max']
                if min_value < 0:
                    mod_value = -mod_value
                if min_value <= mod_value <= max_value + 1:
                    item_mod = possible_mods.loc[idx, :]
                    break
                else:
                    continue
            if isinstance(item_mod, dict):
                if not item_mod:
                    item_mod = possible_mods.loc[idx, :]
            else:
                if item_mod.empty:
                    item_mod = possible_mods.loc[idx, :]
            item_mod['value'] = mod_value
            item_mod = item_mod.drop(['min', 'max', 'required_level'])
            item_mod = item_mod.to_dict()
            break
    return item_mod


def create_item_mods(mods: list, translations: pd.DataFrame,
                       item_class: str, rare_mods: pd.DataFrame) -> dict:
    """
    Not supporting jewels at the moment
    :param mods:
    :param translations:
    :param item_class:
    :param rare_mods:
    :return:
    """
    regex = r'\d+\.*\d*'
    replaced_mods = []
    for mod in mods:
        item_mod = {}
        mod_values = re.findall(regex, mod)
        mod_values = [float(x) for x in mod_values]
        if len(mod_values) == 1:
            mod_value = mod_values[0]
        if len(mod_values) > 1:
            mod_value = sum(mod_values[:2])/len(mod_values)
        replaced_mod = re.sub(regex, '#', mod)
        possible_mod_ids = translations.id[translations.string == replaced_mod].tolist()
        # rare_mods = remove_mods_based_on_item_class(item_class, rare_mods)
        class_rare_mods = rare_mods[rare_mods.tag == item_class]
        default_rare_mods = rare_mods[rare_mods.tag == 'default']
        item_mod = create_item_mod(possible_mod_ids, item_mod, class_rare_mods, mod_value)
        if not item_mod:
            item_mod = create_item_mod(possible_mod_ids, item_mod, default_rare_mods, mod_value)
        if not item_mod:
            print('error')
        replaced_mods.append(item_mod)
    if len(replaced_mods) != len(mods):
        print('error')
    return replaced_mods


def create_item_pseudo_mods(item_mods: dict) -> dict:
    logger.info("Creating pseudo mods for item")
    with open('pseudo_mods.json', 'r') as f:
        pseudo_mods_db = json.load(f)
    item_pseudo_mods = []
    all_elemental = 0
    for item_mod in item_mods:
        if item_mod:
            for key, pseudo_mod in pseudo_mods_db.items():
                if item_mod['type'] in pseudo_mod['types']:
                    mult = pseudo_mod['mult'][pseudo_mod['types'].index(item_mod['type'])]
                    pseudo_mod_value = item_mod['value'] * mult
                    if key in ['pseudo_lightning_resistance', 'pseudo_fire_resistance', 'pseudo_cold_resistance']:
                        all_elemental += pseudo_mod_value
                    item_pseudo_mods.append({'type': key,
                                             'value': pseudo_mod_value})
                else:
                    item_pseudo_mods.append({'type': key,
                                             'value': 0})
    item_pseudo_mods.append({'type': 'pseudo_sum_elemental_resistance',
                             'value': all_elemental})
    item_pseudo_mods = pd.DataFrame(item_pseudo_mods).drop_duplicates('type').to_dict('records')
    return item_pseudo_mods


def create_item_info(item: dict, bases: pd.DataFrame, translations: pd.DataFrame, rare_mods: pd.DataFrame):
    mods = []
    properties = []
    inventory_id = item['inventoryId']
    x = item['x']
    y = item['y']
    item_class = bases.item_class[bases.name.str.contains(item['typeLine'])].values[0].lower()
    if item_class in ['stackablecurrency', 'jewel']:
        return {
            'props': [],
            'mods': [],
            'item_class': '',
            'inventory_id': inventory_id,
            'x': x,
            'y': y
        }
    for key, value in item.items():
        if key == 'properties':
            properties = get_item_properties(value)
        if key == 'implictMods':
            for mod in value:
                mods.append(mod)
        if key == 'explicitMods':
            for mod in value:
                mods.append(mod)
    new_mods = create_item_mods(mods, translations, item_class, rare_mods)
    pseudo_mods = create_item_pseudo_mods(new_mods)
    new_item = {
        'props': properties,
        'mods': new_mods + pseudo_mods,
        'item_class': item_class,
        'inventory_id': inventory_id,
        'x': x,
        'y': y
    }
    return new_item


def get_items(tab) -> dict:
    logger.info('Creating items dict')
    all_mods = get_mods()
    rare_mods = create_rare_mods_df(all_mods)
    bases = pd.read_json('bases.json', orient='records')
    translations = get_stats_translations()
    translations = create_translation_df(translations)
    items = {}
    for item in tab:
        item_name = item['name']
        new_item = create_item_info(item, bases, translations, rare_mods)
        items[item_name] = new_item
    return items


def main():
    with open('test_stash.json', 'r') as f:
        tab = json.load(f)
    items = get_items(tab)
    pass


if __name__ == '__main__':
    main()
