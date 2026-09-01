from sqlalchemy.types import UserDefinedType


class MySQLPoint(UserDefinedType[bytes]):
    """MySQL POINT column with an explicit geographic SRID."""

    cache_ok = True

    def __init__(self, srid: int = 4326):
        self.srid = srid

    def get_col_spec(self, **kw: object) -> str:
        del kw
        return f"POINT SRID {self.srid}"

