from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import JSON, Date, DateTime, Enum as SqlEnum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.mysql import Base


class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    completed = "completed"
    archived = "archived"


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"
    blocked = "blocked"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ProjectModel(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(ProjectStatus, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=ProjectStatus.planning,
    )
    start_date: Mapped[date | None] = mapped_column(Date())
    end_date: Mapped[date | None] = mapped_column(Date())
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TeamModel(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    leader_developer_id: Mapped[int | None] = mapped_column(ForeignKey("developer.id"))
    description: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DeveloperModel(Base):
    __tablename__ = "developer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False, default="developer")
    team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    skill_tags: Mapped[list[str] | None] = mapped_column(JSON())
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TaskModel(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    assignee_developer_id: Mapped[int | None] = mapped_column(ForeignKey("developer.id"))
    status: Mapped[TaskStatus] = mapped_column(
        SqlEnum(TaskStatus, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=TaskStatus.todo,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SqlEnum(TaskPriority, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=TaskPriority.medium,
    )
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )
