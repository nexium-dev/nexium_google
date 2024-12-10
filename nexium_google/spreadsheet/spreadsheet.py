from typing import Type

from gspread import authorize

from nexium_google.spreadsheet.base_row_model import BaseRowModel
from nexium_google.utils import ServiceAccount


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


class Spreadsheet:
    def __init__(self, service_account: ServiceAccount, id_: str, models: list[Type[BaseRowModel]]):
        self.client = authorize(
            credentials=service_account.get(
                scopes=SCOPES,
            ),
        )
        self.spreadsheet = self.client.open_by_key(id_)
        self.models = models
        self._initialize_sheets()

    def _initialize_sheets(self):
        for model in self.models:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if not model._sheet_name:
                raise ValueError(f'Model "{model.__name__}" does not define "__sheet__".')
            # noinspection PyUnresolvedReferences,PyProtectedMember
            sheet = self.spreadsheet.worksheet(model._sheet_name)
            model.bind_sheet(sheet)
