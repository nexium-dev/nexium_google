from logging import getLogger
from asyncio import get_running_loop, sleep
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Type

from gspread import authorize
from gspread.exceptions import APIError

from nexium_google.spreadsheet.base_row_model import BaseRowModel
from nexium_google.utils import ServiceAccount


logger = getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


class Spreadsheet:
    def __init__(
        self,
        service_account: ServiceAccount,
        id_: str,
        models: list[Type[BaseRowModel]],
        reconnect_attempts: int = 10,
        reconnect_delay: float = 10,
    ):
        self.client = authorize(
            credentials=service_account.get(
                scopes=SCOPES,
            ),
        )
        self.spreadsheet = self.client.open_by_key(id_)
        self.models = models
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self._initialize_sheets()

    def _initialize_sheets(self):
        for model in self.models:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            sheet_name = model._sheet_name

            if not sheet_name:
                raise ValueError(f'Model "{model.__name__}" does not define "__sheet__".')

            logger.debug(f'Initialization of Sheet: {sheet_name}')
            sheet = self.spreadsheet.worksheet(sheet_name)
            model.bind_sheet(
                sheet=sheet,
                spreadsheet=self,
            )

    async def request(self, function: partial):
        loop = get_running_loop()

        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                with ThreadPoolExecutor() as pool:
                    # noinspection PyTypeChecker
                    result = await loop.run_in_executor(pool, function)
                    return result
            except APIError as error:
                if attempt == self.reconnect_attempts:
                    logger.error('Max reconnection attempts reached. Raising exception.')
                    raise

                logger.debug(f'{type(error).__name__}: {str(error)}')
                logger.info(
                    f'Error during request execution. Attempt {attempt}/{self.reconnect_attempts}. '
                    f'Retrying in {self.reconnect_delay} seconds.'
                )
                await sleep(self.reconnect_delay)
