import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="session")
def base_url():
    return "http://10.0.0.1:8501"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))
