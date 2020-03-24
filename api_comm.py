import requests
from loguru import logger

from config import AccountConfig


def get_session_id():
    ssid = AccountConfig.POESSID
    return ssid


def get_request_session(ssid: str):
    ssid_name = 'POESESSID'
    session = requests.Session()
    session.cookies.set(**{'name': ssid_name, 'value': ssid})
    return session
