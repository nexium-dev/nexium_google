from json import load

# noinspection PyPackageRequirements
from google.oauth2.service_account import Credentials

from nexium_google.utils.exceptions.service_account import OneFieldRequiredException


class ServiceAccount:
    def __init__(self, json: dict = None, filename: str = None):
        if json:
            self.info = json
        elif filename:
            with open(filename, 'r', encoding='utf-8') as file:
                self.info = load(file)
        else:
            OneFieldRequiredException('One of the fields is required: json, filename')

    def get(self, scopes: list):
        return Credentials.from_service_account_info(
            info=self.info,
            scopes=scopes,
        )
