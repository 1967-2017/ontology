param(
  [string]$MysqlUrl = "",
  [string]$Neo4jUri = "",
  [string]$Neo4jUsername = "",
  [string]$Neo4jPassword = "",
  [string[]]$IncludeTable = @(),
  [string[]]$ExcludeTable = @(),
  [switch]$Rebuild,
  [int]$BatchSize = 500
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$scriptPath = Join-Path $repoRoot "scripts\import_mysql_to_neo4j.py"

$args = @($scriptPath, "--batch-size", $BatchSize)
if ($MysqlUrl) { $args += @("--mysql-url", $MysqlUrl) }
if ($Neo4jUri) { $args += @("--neo4j-uri", $Neo4jUri) }
if ($Neo4jUsername) { $args += @("--neo4j-username", $Neo4jUsername) }
if ($Neo4jPassword) { $args += @("--neo4j-password", $Neo4jPassword) }
foreach ($table in $IncludeTable) { $args += @("--include-table", $table) }
foreach ($table in $ExcludeTable) { $args += @("--exclude-table", $table) }
if ($Rebuild) { $args += "--rebuild" }

python @args
