from neo4j import GraphDatabase


URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"


def main() -> int:
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    mappings = [
        ("Project", "project"),
        ("Team", "team"),
        ("Developer", "developer"),
        ("Task", "task"),
    ]
    try:
        with driver.session() as session:
            for old_label, new_label in mappings:
                session.run(
                    f"MATCH (n:{old_label}) "
                    f"SET n:{new_label} "
                    f"REMOVE n:{old_label}"
                )
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
