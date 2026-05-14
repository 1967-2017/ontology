---
name: mysql-to-neo4j-sync
description: Read a local MySQL database schema, primary keys, foreign keys, and row data, then import them into Neo4j as a business-data graph. Use when Codex needs to rebuild or refresh a local demo graph from MySQL tables, inspect table relationships before graph import, or run a one-shot MySQL-to-Neo4j sync for this ontology project.
---

# Mysql To Neo4j Sync

## Overview

Use this skill to inspect a local MySQL database and import selected tables, rows, and foreign-key relationships into Neo4j. The canonical implementation lives in this repository; the skill only orchestrates the existing project script and explains the expected parameters and mapping behavior.

## Quick Start

Run the project import script through the skill wrapper:

```powershell
.\skills\mysql-to-neo4j-sync\scripts\run_sync.ps1 -IncludeTable project -IncludeTable team -Rebuild
```

Or call the project script directly:

```powershell
python .\scripts\import_mysql_to_neo4j.py --include-table project --include-table team --rebuild
```

## Workflow

1. Read the repository import entrypoint at `scripts/import_mysql_to_neo4j.py`.
2. Confirm the target MySQL and Neo4j connection settings.
3. Decide table scope:
   - Use `--include-table` when importing only a demo subset.
   - Use `--exclude-table` when importing most tables but skipping noise.
4. Decide whether to rebuild:
   - Use `--rebuild` for repeatable demo resets.
   - Omit it for additive upsert sync.
5. Run the import.
6. Review the JSON summary:
   - `tables_processed`
   - `nodes_created_or_updated`
   - `relationships_created`
   - `skipped_tables`
   - `errors`

## Behavior

- Import tables with primary keys only.
- Skip tables without primary keys.
- Import rows as Neo4j nodes.
- Import single-column foreign keys as Neo4j relationships.
- Record unsupported composite foreign keys in `errors`.
- Use label and relationship rules from [references/mapping.md](references/mapping.md).

## Use During This Project

- Prefer this skill for one-shot graph rebuilds from local MySQL.
- Prefer this skill before demos when Neo4j needs to match current MySQL data.
- Prefer `--include-table` for small, explainable graph slices during demos.
- Prefer `--rebuild` when you need deterministic, repeatable graph state.
