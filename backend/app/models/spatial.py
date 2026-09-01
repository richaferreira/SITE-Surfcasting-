from sqlalchemy import func
from sqlalchemy.types import UserDefinedType


class MySQLPoint(UserDefinedType[bytes]):
    """MySQL POINT column with an explicit geographic SRID."""

    cache_ok = True

    def __init__(self, srid: int = 4326):
        self.srid = srid

    def get_col_spec(self, **kw: object) -> str:
        del kw
        return f"POINT SRID {self.srid}"


def mysql_point_expression(latitude: float, longitude: float, srid: int = 4326):
    """Build a geographic point without relying on the SRS default axis order."""

    wkt = f"POINT({longitude:.8f} {latitude:.8f})"
    return func.ST_GeomFromText(wkt, srid, "axis-order=long-lat")
