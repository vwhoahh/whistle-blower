import pytest
from app.mcp_server import reset_demo_state

@pytest.fixture(autouse=True)
def clean_state():
    reset_demo_state()
    yield
