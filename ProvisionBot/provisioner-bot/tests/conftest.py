import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add parent directory to path so app can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app, init_db

@pytest.fixture
async def client():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
