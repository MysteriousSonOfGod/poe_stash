import json

# import pandas as pd


def create_type_tags():
    a = pd.read_json('RePoE-master/RePoE/data/mod_types.json')
    a = a.transpose()
    a['name'] = a.index
    a.index = range(len(a))
    possible_tags = ['poison', 'minion', 'jewellery_elemental', 'gem_level', 'life', 'cold', 'jewellery_quality_ignore',
                     'lightning', 'jewellery_attribute', 'jewellery_caster', 'jewellery_attack', 'bleed',
                     'flat_life_regen', 'fire', 'jewellery_defense', 'elemental', 'jewellery_resistance', 'mana',
                     'aura', 'jewellery_resource', 'defences', 'physical', 'speed', 'attack', 'vaal', 'chaos', 'caster']
    tags_wanted = ['jewellery_elemental', 'gem_level', 'life', 'jewellery_caster', 'fire', 'jewellery_defense',
                   'elemental', 'jewellery_resistance', 'defences', 'speed', 'caster']
    return a


def filter_item():
    wanted_items = []
    # Filter AND
    test_filter = {
        'AND': {
            'item_class': 'boots',
            'mods': {
                'MovementVelocity': 25,
                'pseudo_total_elemental_resistance': 50,
            },
            'prop': {}
        },
        'OR': [
            {
                'mods': {
                    'pseudo_maximum_life': 50
                },
                'prop': {
                    'Evasion Rating': 200
                }
            },
            {
                'mods': {
                    'pseudo_maximum_life': 50
                },
                'prop': {
                    'Armour Rating': 200
                }
            },
            {
                'prop': {
                    'Energy Shield': 150
                }
            },
        ]
    }
    filters = create_filters(test_filter)
    pass


def create_filters(raw_filter: dict) -> list:
    new_filters = []
    and_item_class = raw_filter['AND']['item_class']
    and_mods = raw_filter['AND']['mods']
    and_prop = raw_filter['AND']['prop']
    for key, value in raw_filter.items():
        if key == 'OR':
            for alternative in value:
                or_item_class = alternative.get('item_class', None)
                or_mods = alternative.get('mods', {})
                or_prop = alternative.get('prop', {})
                filter_item_class = '|'.join([and_item_class, or_item_class]) if or_item_class else and_item_class
                filter_mods = and_mods | or_mods
                filter_prop = and_prop | or_prop
                new_filters.append({
                    'item_class': filter_item_class,
                    'mods': filter_mods,
                    'prop': filter_prop,
                })
    if not new_filters:
        new_filters = [{
            'item_class': and_item_class,
            'mods': and_mods,
            'prop': and_prop,
        }]
    return new_filters


if __name__ == '__main__':
    filter_item()
