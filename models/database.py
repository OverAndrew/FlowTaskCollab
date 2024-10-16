from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = 'flowtaskcollab.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind = engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    username = Column(String)
    selected_project = Column(Integer, ForeignKey('project.id'))

    project_team = relationship("Project_team", back_populates='user')
    team = relationship('Task_team', back_populates='user')
    project = relationship('Project', back_populates='user')


class Project_team(Base):
    __tablename__ = 'project_team'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    user_project_level = Column(Integer)

    user = relationship("User", back_populates="project_team")
    project = relationship("Project", back_populates="project_teams")

class Task_team(Base):
    __tablename__ = 'task_team'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user_team_level = Column(Integer)
    task_id = Column(Integer, ForeignKey('task.id'))

    user = relationship("User", back_populates="team")
    tasks = relationship('Task', back_populates='team')

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    deadline = Column(String)
    # team_id = Column(Integer, ForeignKey('task_team.id'))
    priority = Column(Integer)
    description = Column(String)
    status = Column(Boolean)
    name = Column(String)

    project = relationship("Project", back_populates="tasks")
    team = relationship("Task_team", back_populates="tasks", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    key = Column(Integer)

    project_teams = relationship("Project_team", back_populates="project", cascade='all, delete-orphan')
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    user = relationship('User', back_populates='project')

def create_db():
    Base.metadata.create_all(engine)