from enum import Enum
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
from sqlalchemy import Engine
from loguru import logger

from boxtime.utils.console import console


class Feeling(Enum):
    FEAR = 0
    ANGER = 1
    JOY = 2
    APATHY = 3
    SADNESS = 4


class Skill(Enum):
    SOFT = 0
    HARD = 1


class People(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    team: str
    role: str
    is_self: bool = Field(default=False)


class TaskType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(primary_key=True)
    skill: Skill
    experience: float


class LogPeopleLink(SQLModel, table=True):
    log_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="emotionlog.id"
    )
    people_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="people.id"
    )


class LogTaskLink(SQLModel, table=True):
    log_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="emotionlog.id"
    )
    task_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="tasktype.id"
    )


class EmotionLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    feeling: Feeling = Field(default=None)
    timestamp: datetime
    duration: int
    trigger: str
    reaction: str
    people: List[People] = Relationship(link_model=LogPeopleLink)
    task: List[TaskType] = Relationship(link_model=LogTaskLink)
    resolved: bool = Field(default=False)


def create_db_and_tables():
    path, engine = sqlite_engine()
    console.log("Creating database at", path)
    SQLModel.metadata.create_all(engine)


def sqlite_engine() -> Tuple[str, Engine]:
    home = Path.home()
    par = home / ".boxtime"
    par.mkdir(parents=True, exist_ok=True)
    path = par / "boxtime.db"
    sqlite_url = f"sqlite:///{path}"
    return sqlite_url, create_engine(sqlite_url)


class SQLSession:
    def __init__(self):
        _, engine = sqlite_engine()
        self.session = Session(engine)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.info(f"An exception of type {exc_type} occurred: {exc_value}")
            logger.info(traceback)
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
