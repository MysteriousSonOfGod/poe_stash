import re
import json

import pandas as pd
from stash import AccountStash


def get_mods():
    with open('RePoE-master/RePoE/data/mods.json', 'r') as f:
        mods = json.load(f)
    return mods


def create_rare_mods_df(mods: dict) -> pd.DataFrame:
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
    with open('RePoE-master/RePoE/data/stat_translations.json', 'r') as f:
        stats_translations = json.load(f)
    return stats_translations


def create_translation_df(translations: dict) -> pd.DataFrame:
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


def get_item_properties(properties: list) -> list:
    new_properties = []
    phys_damage = 0
    elemental_damage = 0
    for property in properties:
        if property['name'] == 'Physical Damage':
            phys_damage = property['values'][0][0].split('-')
            phys_damage = sum([int(x) for x in phys_damage])
        if property['name'] == 'Elemental Damage':
            elemental_damage = property['values'][0][0].split('-')
            elemental_damage = sum([int(x) for x in elemental_damage])
        if property['name'] == 'Attacks per Second':
            aps = float(property['values'][0][0])
        if property['values']:
            property['values'] = property['values'][0][0]
    if phys_damage > 0 or elemental_damage > 0:
        phys_dps = phys_damage/aps
        ele_dps = elemental_damage/aps
        all_dps = phys_dps + ele_dps
        new_properties = [{'name': 'Dps', 'value': all_dps}, {'name': 'Physical Dps', 'value': phys_dps},
                          {'name': 'Elemental Dps', 'value': ele_dps}]
    return properties + new_properties


def create_item_mod(possible_mod_ids: list, item_mod: pd.Series, rare_mods: pd.DataFrame, mod_value: int) -> dict:
    for mod_id in possible_mod_ids:
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
        rare_mods = remove_mods_based_on_item_class(item_class, rare_mods)
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
    with open('pseudo_mods.json', 'r') as f:
        pseudo_mods_db = json.load(f)
    item_pseudo_mods = []
    all_elemental = 0
    for item_mod in item_mods:
        for key, pseudo_mod in pseudo_mods_db.items():
            if item_mod:
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
    return item_pseudo_mods


def get_items(tab):
    all_mods = get_mods()
    rare_mods = create_rare_mods_df(all_mods)
    bases = pd.read_json('bases.json', orient='records')
    translations = get_stats_translations()
    translations = create_translation_df(translations)
    items = {}
    for item in tab:
        mods = []
        properties = []
        item_name = item['name']
        inventory_id = item['inventoryId']
        x = item['x']
        y = item['y']
        item_class = bases.item_class[bases.name.str.contains(item['typeLine'])].values[0].lower()
        for key, value in item.items():
            if key == 'properties':
                properties = get_item_properties(value)
            if key == 'implictMods':
                for mod in value:
                    mods.append(mod)
            if key == 'explicitMods':
                for mod in value:
                    mods.append(mod)
        if item_class in ['stackablecurrency', 'jewel']:
            continue
        new_mods = create_item_mods(mods, translations, item_class, rare_mods)
        pseudo_mods = create_item_pseudo_mods(new_mods)
        new_item = {
            'properties': properties,
            'mods': new_mods + pseudo_mods,
            'item_class': item_class,
            'inventory_id': inventory_id,
            'x': x,
            'y': y
        }
        items[item_name] = new_item
    return items


def main():
    with open('test_stash.json', 'r') as f:
        tab = json.load(f)
    items = get_items(tab)
    pass


if __name__ == '__main__':
    main()
