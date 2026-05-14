# Mapping Rules

- 每张 MySQL 表映射为一个 Neo4j 标签。
- 每行数据映射为一个节点。
- 节点唯一键使用 `source_pk`。
- 节点统一保留：
  - `table_name`
  - `source_pk`
  - `_source_label`
  - `_source_pk_columns`
- 所有原始列值作为节点属性写入。
- `DECIMAL` 转 `float`。
- `DATE/DATETIME` 转 ISO 字符串。
- `bytes` 转 UTF-8 字符串。
- `list/dict/json` 转 JSON 字符串。
- 每个单列外键映射为一条关系。
- 关系类型规则：`REF_<table_name>_<fk_column>`。
- 组合主键会被序列化为 JSON 字符串写入 `source_pk`。
- 组合外键在第一版不导入关系，记录为错误。
