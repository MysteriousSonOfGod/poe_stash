import pandas as pd


def create_item_mod_types_json():
    data = pd.read_json('data/rare_mods.json')
    rare_mod_types = data.drop_duplicates(['type'], ignore_index=True).type
    pseudo_mod = pd.Series(list(pd.read_json('data/pseudo_mods.json').columns)).str.capitalize()
    rare_mod_types = rare_mod_types.append(pseudo_mod).sort_values()
    rare_mod_types.to_json('data/modtypes.json', orient='records')
    pass


def main():
    create_item_mod_types_json()


if __name__ == '__main__':
    main()
