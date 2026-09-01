from app.main import app


def test_expected_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/token" in paths
    assert "/api/v1/auth/me" in paths
    assert "/api/v1/beaches" in paths
    assert "/api/v1/admin/beaches" in paths
    assert "/api/v1/fishing-score" in paths
