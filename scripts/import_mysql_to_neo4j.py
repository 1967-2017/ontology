import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas.import_api import MysqlToNeo4jImportRequest  # noqa: E402
from app.services.mysql_to_neo4j_import_service import MysqlToNeo4jImportService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Import local MySQL tables and data into Neo4j.")
    parser.add_argument("--mysql-url", dest="mysql_url")
    parser.add_argument("--neo4j-uri", dest="neo4j_uri")
    parser.add_argument("--neo4j-username", dest="neo4j_username")
    parser.add_argument("--neo4j-password", dest="neo4j_password")
    parser.add_argument("--include-table", dest="include_tables", action="append", default=[])
    parser.add_argument("--exclude-table", dest="exclude_tables", action="append", default=[])
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()

    request = MysqlToNeo4jImportRequest(
        mysql_url=args.mysql_url,
        neo4j_uri=args.neo4j_uri,
        neo4j_username=args.neo4j_username,
        neo4j_password=args.neo4j_password,
        include_tables=args.include_tables,
        exclude_tables=args.exclude_tables,
        rebuild=args.rebuild,
        batch_size=args.batch_size,
    )
    result = MysqlToNeo4jImportService().run_import(request)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
