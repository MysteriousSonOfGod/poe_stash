import requests
from config import AccountConfig


def get_request_session():
    ssid = AccountConfig.POESSID
    ssid_name = 'POESESSID'
    session = requests.Session()
    session.cookies.set(**{'name': ssid_name, 'value': ssid})
    return session
