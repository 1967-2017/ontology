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


class DocumentOCRStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentKnowledgeStatus(str, Enum):
    pending = "pending"
    indexed = "indexed"


class PresentationStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


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


class DocumentModel(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    ocr_status: Mapped[DocumentOCRStatus] = mapped_column(
        SqlEnum(DocumentOCRStatus, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=DocumentOCRStatus.pending,
    )
    knowledge_status: Mapped[DocumentKnowledgeStatus] = mapped_column(
        SqlEnum(DocumentKnowledgeStatus, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=DocumentKnowledgeStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DocumentOCRResultModel(Base):
    __tablename__ = "document_ocr_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False, unique=True)
    full_text: Mapped[str] = mapped_column(Text(), nullable=False)
    pages: Mapped[list[dict]] = mapped_column(JSON(), nullable=False, default=list)
    blocks: Mapped[list[dict]] = mapped_column(JSON(), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class PresentationModel(Base):
    __tablename__ = "presentation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PresentationStatus] = mapped_column(
        SqlEnum(PresentationStatus, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
        default=PresentationStatus.pending,
    )
    file_path: Mapped[str | None] = mapped_column(String(512))
    slide_count: Mapped[int] = mapped_column(nullable=False, default=0)
    source_document_ids: Mapped[list[int] | None] = mapped_column(JSON())
    outline: Mapped[list[dict] | None] = mapped_column(JSON())
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )
