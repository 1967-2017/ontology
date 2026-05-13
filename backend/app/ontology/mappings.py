from app.db.models import DeveloperModel, ProjectModel, TaskModel, TeamModel


MODEL_BY_CLASS = {
    "Project": ProjectModel,
    "Team": TeamModel,
    "Developer": DeveloperModel,
    "Task": TaskModel,
}
