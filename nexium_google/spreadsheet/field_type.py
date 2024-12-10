from enum import Enum


class FieldType(str, Enum):
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    DATETIME = 'DATETIME'
    DATE = 'DATE'
    TIME = 'TIME'
