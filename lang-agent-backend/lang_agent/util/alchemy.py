import json

from sqlalchemy.types import TypeDecorator
from sqlalchemy import Text

class JSONEncodedDict(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

    def process_literal_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value

    @property
    def python_type(self):
        return dict
