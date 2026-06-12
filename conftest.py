import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/ecommerce_test"
)

engine_test = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():

    Base.metadata.create_all(bind=engine_test)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine_test)

    app.dependency_overrides.clear()


@pytest.fixture
def produto_existente(client):

    response = client.post(
        "/produtos",
        json={
            "nome": "Mouse Gamer",
            "preco": 150.0,
            "estoque": 10,
            "ativo": True
        }
    )

    return response.json()