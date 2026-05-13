# Ontology Model

## Classes

### Project

- table: `project`
- display field: `name`
- fields: `name`, `description`, `status`, `start_date`, `end_date`

### Team

- table: `team`
- display field: `name`
- fields: `name`, `project_id`, `leader_developer_id`, `description`
- relations:
  - `BELONGS_TO -> Project`
  - `LED_BY -> Developer`

### Developer

- table: `developer`
- display field: `name`
- fields: `name`, `email`, `role`, `team_id`, `skill_tags`
- relations:
  - `MEMBER_OF -> Team`

### Task

- table: `task`
- display field: `title`
- fields: `title`, `description`, `project_id`, `assignee_developer_id`, `status`, `priority`, `estimated_hours`
- relations:
  - `BELONGS_TO -> Project`
  - `ASSIGNED_TO -> Developer`

## Query Types

- `developer_tasks`
- `project_teams`
- `team_members`
- `project_tasks`
