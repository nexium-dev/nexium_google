from datetime import datetime, date, time

from nexium_google.spreadsheet.field_type import FieldType


class Field:
    def __init__(
            self,
            title: str,
            type_: FieldType,
            nullable: bool = True,
            default: str | int | float | datetime | date | time = None,
            format_: str = None,
    ):
        if not format_ and type_ == FieldType.DATETIME:
            format_ = '%Y-%m-%d %H:%M:%S'
        elif not format_ and type_ == FieldType.DATE:
            format_ = '%Y-%m-%d'
        elif not format_ and type_ == FieldType.TIME:
            format_ = '%H:%M:%S'

        self.title = title
        self.type = type_
        self.nullable = nullable
        self.default = default
        self.format = format_