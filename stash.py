import json

import pandas as pd

import api_comm
from loguru import logger


class AccountStash:
    def __init__(self, poesessid: str):
        self.session = api_comm.get_request_session(poesessid)
        self.tabs_names = self.get_tabs_names()
        self.tabs = self.get_tabs_items()

    def get_tabs_names(self):
        stashs = self.session.get('https://www.pathofexile.com/character-window/'
                                  'get-stash-items?accountName=mininim212&realm=pc&league'
                                  '=SSF+Delirium&tabs=1&tabIndex=1&public=false').json()
        tabs_names = [stashs['tabs'][i]['n'] for i in range(len(stashs['tabs']))]
        return tabs_names

    def get_tabs_items(self):
        tabs = []
        for i in range(len(self.tabs_names)):
            url_base = f'https://www.pathofexile.com/character-window/get-stash-items?' \
                       f'accountName=mininim212&realm=pc&league=SSF+Delirium&tabs=0&tabIndex={i}&public=false'
            stash_items = self.session.get(url_base).json()['items']
            tabs.append(stash_items)
        return tabs


def get_account_stash(sessid: str):
    stash = AccountStash(sessid)
    return stash


def get_test_stash():
    logger.info('Using test stash')
    with open("data/test_stash.json", 'r') as f:
        test_stash = json.load(f)
    return test_stash


def select_stash_tabs(stash_tab_names: list, input_names: list) -> list:
    selected_tabs = []
    for input_name in input_names:
        selected_tabs.append(stash_tab_names.index(input_name))
    return selected_tabs


def get_account_tabs(sessid: str, input_tabs_names: list) -> list:
    """
    Function to be used in gui. If no tabs names given, use all tabs
    :param sessid:
    :param input_tabs_names:
    :return:
    """
    stash = get_account_stash(sessid)
    if input_tabs_names:
        selected_tabs = []
        tabs_index = select_stash_tabs(stash.tabs_names, input_tabs_names)
        for i in tabs_index:
            df_tab = pd.DataFrame(stash.tabs[i])
            tab = df_tab.to_dict(orient='records')
            selected_tabs.append(tab)
        logger.debug('Return selected tabs')
        return selected_tabs
    else:
        return stash.tabs


if __name__ == '__main__':
    tabs = get_account_tabs('16a62217622ed9fe506e0e91fdd10f34', ['q1', 'q2', 'q3'])
    tabs