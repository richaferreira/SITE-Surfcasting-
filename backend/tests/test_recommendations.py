import pytest

from app.integrations.neo4j_recommendations import direction_to_compass


@pytest.mark.parametrize(
    ("degrees", "expected"),
    [
        (0, "N"),
        (44.9, "NE"),
        (90, "E"),
        (180, "S"),
        (225, "SW"),
        (315, "NW"),
        (359.9, "N"),
    ],
)
def test_direction_to_compass(degrees: float, expected: str) -> None:
    assert direction_to_compass(degrees) == expected
