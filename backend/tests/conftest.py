from collections.abc import Generator
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

import app.main as app_main
from app.db.mysql import Base, get_db
from app.main import app


class FakeNeo4jResult:
    def __init__(self, data=None):
        self._data = data or []

    def consume(self):
        return None

    def __iter__(self):
        for item in self._data:
            yield type("FakeRecord", (), {"data": lambda self, payload=item: payload})()

    def data(self):
        return self._data

    def single(self):
        return self._data[0] if self._data else {"ok": 1}


class FakeNeo4jSession:
    def __init__(self, should_fail: bool = False):
        self.queries = []
        self.should_fail = should_fail

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query, **params):
        if self.should_fail:
            raise RuntimeError("neo4j unavailable")
        self.queries.append((query, params))
        if "TASK_ASSIGNED_TO_DEVELOPER" in query:
            return FakeNeo4jResult([{"id": 1, "title": "task-1", "status": "todo", "priority": "high"}])
        if "TEAM_BELONGS_TO_PROJECT" in query and "team" in query:
            return FakeNeo4jResult([{"id": 1, "name": "team", "description": None}])
        if "DEVELOPER_MEMBER_OF_TEAM" in query:
            return FakeNeo4jResult([{"id": 1, "name": "张三", "role": "backend"}])
        return FakeNeo4jResult()


class FakeNeo4jDriver:
    def __init__(self, should_fail: bool = False):
        self.session_obj = FakeNeo4jSession(should_fail=should_fail)

    def session(self):
        return self.session_obj


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, class_=Session)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def fake_driver() -> FakeNeo4jDriver:
    return FakeNeo4jDriver()


@pytest.fixture
def failing_driver() -> FakeNeo4jDriver:
    return FakeNeo4jDriver(should_fail=True)


@pytest.fixture
def client(db_session: Session, fake_driver: FakeNeo4jDriver, test_engine) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    from app.db.neo4j import get_neo4j_driver

    def override_get_neo4j_driver():
        yield fake_driver

    original_engine = app_main.engine
    app_main.engine = test_engine
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_neo4j_driver] = override_get_neo4j_driver
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app_main.engine = original_engine
