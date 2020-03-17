import api_comm


class AccountStash:
    def __init__(self):
        self.session = api_comm.get_request_session()
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


if __name__ == '__main__':
    stash = AccountStash()
    stash.get_tabs_names()
    stash.get_tabs_items()
