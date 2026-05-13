from collections.abc import Generator

from neo4j import Driver, GraphDatabase

from app.config import get_settings


settings = get_settings()
driver: Driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_username, settings.neo4j_password),
)


def get_neo4j_driver() -> Generator[Driver, None, None]:
    yield driver
