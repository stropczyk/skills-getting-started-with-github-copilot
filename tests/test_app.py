import copy

from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)


def _reset_activities(original):
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


import pytest


@pytest.fixture(autouse=True)
def reset_activities_fixture():
    original = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        _reset_activities(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    email = "unittest@example.com"
    activity = "Chess Club"

    # Ensure not already in participants
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]

    # Sign up
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert f"Signed up {email}" in r.json().get("message", "")

    # Now participant should be present
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Duplicate signup should return 400
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 400

    # Unregister
    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 200
    assert f"Unregistered {email}" in r.json().get("message", "")

    # Participant should no longer be present
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    email = "doesnotexist@example.com"
    activity = "Chess Club"
    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 404
