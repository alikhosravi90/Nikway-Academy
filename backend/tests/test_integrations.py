from app.integrations import moodle_link

A = "10000000-0000-4000-8000-000000000001"
B = "10000000-0000-4000-8000-000000000002"

def test_tenant_scoped_launch(monkeypatch):
    monkeypatch.setenv("MOODLE_TENANT_ID", A)
    monkeypatch.setenv("MOODLE_URL", "http://localhost:18701")
    assert moodle_link(A)["url"] == "http://localhost:18701/"
    assert moodle_link(B) == {"enabled": False}
    assert moodle_link("invalid") == {"enabled": False}

def test_missing_or_unsafe_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv("MOODLE_TENANT_ID", raising=False)
    assert moodle_link(A) == {"enabled": False}
    monkeypatch.setenv("MOODLE_TENANT_ID", A)
    for url in ["https://external.example", "http://localhost:18701@evil.example", "javascript:alert(1)", "http://localhost:18701/?token=x", "http://localhost:999999"]:
        monkeypatch.setenv("MOODLE_URL", url)
        assert moodle_link(A) == {"enabled": False}
