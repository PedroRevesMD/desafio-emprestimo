import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.models.database import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


@pytest.mark.asyncio
async def test_post_customer_loans_success():
    """TC-N-01/05 Success — valid customer profile."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "age": 25,
            "cpf": "123.456.789-09",
            "name": "Maria Souza",
            "income": 4000.00,
            "location": "SP",
        }
        response = await ac.post("/customer-loans", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["customer"] == "Maria Souza"
    assert "loans" in data
    assert isinstance(data["loans"], list)
    assert any(loan["type"] == "CONSIGNMENT" for loan in data["loans"])
    assert any(loan["type"] == "GUARANTEED" for loan in data["loans"])


@pytest.mark.asyncio
async def test_post_customer_loans_high_income():
    """TC-N-01 Success — income > 5000 returns ONLY consignment."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "age": 40,
            "cpf": "123.456.789-09",
            "name": "Ricardo Alta Renda",
            "income": 6000.00,
            "location": "RJ",
        }
        response = await ac.post("/customer-loans", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["customer"] == "Ricardo Alta Renda"
    assert len(data["loans"]) == 1
    assert data["loans"][0]["type"] == "CONSIGNMENT"
    assert data["loans"][0]["interest_rate"] == 2


@pytest.mark.asyncio
async def test_post_customer_loans_malformed_json():
    """TC-E-01 — Malformed JSON payload."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/customer-loans",
            content="invalid json {",
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"


@pytest.mark.asyncio
async def test_post_customer_loans_validation_error_cpf():
    """TC-E-02 — Invalid CPF format."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "age": 25,
            "cpf": "12345678909",
            "name": "Maria Souza",
            "income": 4000.00,
            "location": "SP",
        }
        response = await ac.post("/customer-loans", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert any(detail["field"] == "cpf" for detail in data["error"]["details"])


@pytest.mark.asyncio
async def test_post_customer_loans_missing_age():
    """TC-E-03 — Missing age field."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "cpf": "123.456.789-09",
            "name": "Maria Souza",
            "income": 4000.00,
            "location": "SP",
        }
        response = await ac.post("/customer-loans", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert any(detail["field"] == "age" for detail in data["error"]["details"])


@pytest.mark.asyncio
async def test_method_not_allowed():
    """TC-E-05 — GET method not allowed for /customer-loans."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/customer-loans")

    assert response.status_code == 405
    data = response.json()
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"


@pytest.mark.asyncio
async def test_not_found():
    """TC-E-06 — Requesting a non-existent route."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/not-existent")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
