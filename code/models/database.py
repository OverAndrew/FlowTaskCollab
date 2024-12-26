from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_NAME = 'flowtaskcollab.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    surname: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    selected_project: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"), nullable=True)

    project_team: Mapped[List["Project_team"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    team: Mapped[List["Task_team"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    project: Mapped[Optional["Project"]] = relationship(back_populates="users")



class Project_team(Base):
    __tablename__ = "project_team"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"), nullable=True)
    user_project_level: Mapped[Optional[int]] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="project_team")
    project: Mapped["Project"] = relationship(back_populates="project_teams")


class Task_team(Base):
    __tablename__ = "task_team"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    user_team_level: Mapped[Optional[int]] = mapped_column(nullable=True)
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("task.id"), nullable=True)

    user: Mapped["User"] = relationship(back_populates="team")
    tasks: Mapped["Task"] = relationship(back_populates="team")


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"), nullable=True)
    deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    team: Mapped[List["Task_team"]] = relationship(
        back_populates="tasks", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    key: Mapped[Optional[int]] = mapped_column(nullable=True)

    project_teams: Mapped[List["Project_team"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    users: Mapped[List["User"]] = relationship(back_populates="project")


def create_db():
    Base.metadata.create_all(engine)