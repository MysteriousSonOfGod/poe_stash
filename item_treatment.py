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


def create_item_mods(mods: list, translations: pd.DataFrame,
                       item_class: str, rare_mods: pd.DataFrame) -> dict:
    regex = r'\d+'
    replaced_mods = []
    for mod in mods:
        item_mod = {}
        mod_values = re.findall(regex, mod)
        mod_values = [int(x) for x in mod_values]
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
        replaced_mods.append(item_mod)
    if len(replaced_mods) != len(mods):
        print('error')
    return replaced_mods


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


def get_items(tab):
    all_mods = get_mods()
    rare_mods = create_rare_mods_df(all_mods)
    bases = pd.read_json('bases.json', orient='records')
    translations = get_stats_translations()
    translations = create_translation_df(translations)
    items = {}
    for item in tab:
        mods = []
        for key, value in item.items():
            if key == 'name':
                item_name = value
            if key == 'typeLine':
                item_class = bases.item_class[bases.name.str.contains(value)].values[0].lower()
            if key == 'inventoryId':
                inventory_id = value
            if key == 'x':
                x = value
            if key == 'y':
                y = value
            if key == 'implictMods':
                for mod in value:
                    mods.append(mod)
            if key == 'explicitMods':
                for mod in value:
                    mods.append(mod)
        if item_class == 'stackablecurrency':
            continue
        new_mods = create_item_mods(mods, translations, item_class, rare_mods)
        new_item = {
            'mods': new_mods,
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


if __name__ == '__main__':
    main()
