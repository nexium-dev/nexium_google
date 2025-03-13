from datetime import datetime, date, time
from functools import partial
from logging import getLogger

from gspread import Worksheet
from gspread.utils import ValueInputOption

from nexium_google.spreadsheet.field import Field
from nexium_google.spreadsheet.field_type import FieldType


logger = getLogger(__name__)
TYPES = {
    FieldType.BOOLEAN: bool,
    FieldType.STRING: str,
    FieldType.INTEGER: int,
    FieldType.FLOAT: float,
    FieldType.DATETIME: datetime,
    FieldType.DATE: date,
    FieldType.TIME: time,
}


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {k: v for k, v in dct.items() if isinstance(v, Field)}
        sheet_name = dct.get('__sheet__', None)
        cls_obj = super().__new__(cls, name, bases, dct)
        setattr(cls_obj, '_fields', fields)
        setattr(cls_obj, '_sheet_name', sheet_name)
        return cls_obj


class BaseRowModel(metaclass=ModelMeta):
    _sheet_name: str
    _sheet: Worksheet
    _fields: dict[str, Field]

    def __init__(self, **kwargs):
        self.index = kwargs.get('index', None)
        self._instances = []

        for field_name, field in self._fields.items():
            value = kwargs.get(field_name)
            setattr(self, field_name, value)

        if not self._sheet:
            raise ValueError('Sheet is not bound to the model.')

    async def get_all(self) -> list['BaseRowModel']:
        logger.debug(f'Get all rows on the "{self._sheet_name}" sheet:')

        records = await self.spreadsheet.request(
            function=partial(
                self._sheet.get_all_records,
            ),
        )

        instances = []
        for index, record in enumerate(records, start=2):
            instance = self.__class__(index=index)
            for field_name, field in self._fields.items():
                value = record.get(field.title)
                setattr(instance, field_name, value)
            await instance._deserialization()
            instances.append(instance)
        return instances

    async def create(self):
        await self._serialization()
        data = [getattr(self, f'_{field_name}', None) for field_name in self._fields]
        if self.index:
            logger.debug(f'Creating a new row on the "{self._sheet_name}" sheet with index {self.index}: {data}')
            await self.spreadsheet.request(
                function=partial(
                    self._sheet.insert_row,
                    values=data,
                    index=self.index,
                    value_input_option=ValueInputOption.user_entered,
                ),
            )
            return self

        logger.debug(f'Creating a new row on the "{self._sheet_name}" sheet: {data}')
        await self.spreadsheet.request(
            function=partial(
                self._sheet.append_row,
                values=data,
                value_input_option=ValueInputOption.user_entered,
            ),
        )
        return self

    async def update(self):
        await self._serialization()
        data = [getattr(self, f'_{field_name}', None) for field_name in self._fields]
        logger.debug(f'Updating row on the "{self._sheet_name}" sheet with index {self.index}: {data}:')
        await self.spreadsheet.request(
            function=partial(
                self._sheet.update,
                values=[data],
                range_name=f'A{self.index}:{chr(64+len(data))}{self.index}',
                value_input_option=ValueInputOption.user_entered,
            ),
        )

    async def delete(self):
        logger.debug(f'Deleting row on the "{self._sheet_name}" sheet with index {self.index}')
        await self.spreadsheet.request(
            function=partial(
                self._sheet.delete_rows,
                start_index=self.index,
            ),
        )

    async def _serialization(self):
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)

            formatted_value = None

            if not value and field.default:
                value = field.default
                setattr(self, field_name, value)

            if value is None and not field.nullable:
                raise TypeError(f'Attribute "{field_name}" cannot be None')

            if value is not None:
                type_ = TYPES[field.type]

                if field.type == FieldType.FLOAT and isinstance(value, int):
                    value = float(value)

                if not isinstance(value, type_):
                    raise TypeError(f'Attribute "{field_name}" must have a type {type_}. Now {type(value)}')

                formatted_value = value
                if field.type in [FieldType.DATETIME, FieldType.DATE, FieldType.TIME]:
                    formatted_value = value.strftime(field.format)

            setattr(self, f'_{field_name}', formatted_value)

    async def _deserialization(self):
        for field_name, field in self._fields.items():
            formatted_value = getattr(self, field_name, None)
            value = None

            if formatted_value:
                if field.type == FieldType.BOOLEAN:
                    value = True if formatted_value == 'TRUE' else False
                elif field.type == FieldType.STRING:
                    value = formatted_value

                # Integer
                elif field.type == FieldType.INTEGER and isinstance(formatted_value, int):
                    value = formatted_value
                elif field.type == FieldType.INTEGER and isinstance(formatted_value, str):
                    if formatted_value.isdigit():
                        value = int(formatted_value)

                elif field.type == FieldType.FLOAT and isinstance(formatted_value, float):
                    value = formatted_value
                elif field.type == FieldType.FLOAT and isinstance(formatted_value, int):
                    value = float(formatted_value)

                # Datetime
                elif field.type == FieldType.DATETIME:
                    value = datetime.strptime(formatted_value, field.format)
                elif field.type == FieldType.DATE:
                    value = datetime.strptime(formatted_value, field.format).date()
                elif field.type == FieldType.TIME:
                    value = datetime.strptime(formatted_value, field.format).time()
                else:
                    raise TypeError(
                        f'Value "{field.title}" on line {self.index} does not match the type "{field.type}". '
                        f'The current type is: "{type(formatted_value)}"'
                    )

            setattr(self, field_name, value)
            setattr(self, f'_{field_name}', formatted_value)

    @classmethod
    def bind_sheet(cls, sheet: Worksheet, spreadsheet):
        cls._sheet = sheet
        cls.spreadsheet = spreadsheet
