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
  - `TEAM_BELONGS_TO_PROJECT -> project`
  - `TEAM_LED_BY_DEVELOPER -> developer`

### Developer

- table: `developer`
- display field: `name`
- fields: `name`, `email`, `role`, `team_id`, `skill_tags`
- relations:
  - `DEVELOPER_MEMBER_OF_TEAM -> team`

### Task

- table: `task`
- display field: `title`
- fields: `title`, `description`, `project_id`, `assignee_developer_id`, `status`, `priority`, `estimated_hours`
- relations:
  - `TASK_BELONGS_TO_PROJECT -> project`
  - `TASK_ASSIGNED_TO_DEVELOPER -> developer`

## Query Types

- `developer_tasks`
- `project_teams`
- `team_members`
- `project_tasks`
