from app.main import app


def test_expected_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/token" in paths
    assert "/api/v1/auth/me" in paths
    assert "/api/v1/beaches" in paths
    assert "/api/v1/admin/beaches" in paths
    assert "/api/v1/fishing-score" in paths
    assert "/api/v1/beaches/{beach_slug}/points" in paths
    assert "/api/v1/admin/beaches/{beach_id}/points" in paths
    assert "/api/v1/admin/points/{point_id}" in paths
    assert "/api/v1/academy/posts" in paths
    assert "/api/v1/academy/posts/{slug}" in paths
    assert "/api/v1/admin/posts" in paths
    assert "/api/v1/admin/posts/{post_id}" in paths
    assert "/api/v1/admin/media" in paths
    assert "/api/v1/admin/monitoring" in paths
    assert "/api/v1/beaches/{beach_slug}/recommendations" in paths
    assert "/api/v1/community/threads" in paths
    assert "/api/v1/community/threads/{thread_id}/comments" in paths
    assert "/api/v1/community/threads/{thread_id}/reactions" in paths
    assert "/api/v1/admin/community/threads" in paths
    assert "/api/v1/ads" in paths
    assert "/api/v1/admin/ads" in paths
    assert "/api/v1/admin/users" in paths
