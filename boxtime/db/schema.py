import sqlite3
import abc
from enum import Enum
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from pydantic import Field, BaseModel


class SQLConnect:
    def __init__(self):
        par = Path.home() / ".boxtime"
        par.mkdir(parents=True, exist_ok=True)
        self.path = par / "boxtime.db"
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __enter__(self) -> sqlite3.Cursor:
        self.connect()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


class Feeling(Enum):
    FEAR = 0
    ANGER = 1
    JOY = 2
    APATHY = 3
    SADNESS = 4


class Skill(Enum):
    SOFT = 0
    HARD = 1


class Table(BaseModel, abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def create_table(cls) -> str:
        pass


class People(Table):
    id: Optional[int] = Field(default=None)
    username: str
    team: str
    role: str
    is_self: bool = Field(default=False)

    @staticmethod
    def create_table() -> None:
        sql = """CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            team TEXT NOT NULL,
            role TEXT NOT NULL,
            is_self INTEGER NOT NULL DEFAULT 0
        )"""
        with SQLConnect() as cursor:
            cursor.execute(sql)

    @classmethod
    def insert(cls, username: str, team: str, role: str) -> "People":
        person = cls(username=username, team=team, role=role)
        with SQLConnect() as cursor:
            cursor.execute(
                "INSERT INTO people (username, team, role) VALUES (?, ?, ?)",
                (person.username, person.team, person.role),
            )
            id_ = cursor.lastrowid
        person.id = id_
        return person

    def update(self, team: str, role: str) -> None:
        with SQLConnect() as cursor:
            cursor.execute(
                "UPDATE people SET team = ?, role = ?, username = ? WHERE id = ?",
                (team, role, self.username),
            )

    def delete(self) -> None:
        with SQLConnect() as cursor:
            cursor.execute("DELETE FROM people WHERE id = ?", (self.id,))
        self.id = None

    @classmethod
    def search(cls, username: str | None = None) -> List["People"]:
        with SQLConnect() as cursor:
            if username:
                cursor.execute("SELECT * FROM people WHERE username = ?", (username,))
            else:
                cursor.execute("SELECT * FROM people")
            people = cursor.fetchall()
        return [cls(**person) for person in people]


class TaskType(Table):
    id: Optional[int] = Field(default=None)
    name: str = Field(primary_key=True)
    skill: Skill
    experience: float

    @staticmethod
    def create_table() -> str:
        sql = """CREATE TABLE IF NOT EXISTS task_type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            skill INTEGER NOT NULL,
            experience REAL NOT NULL
        )"""
        with SQLConnect() as cursor:
            cursor.execute(sql)

    @classmethod
    def insert(cls, name: str, skill: Skill, experience: float) -> "TaskType":
        task = cls(name=name, skill=skill, experience=experience)
        with SQLConnect() as cursor:
            cursor.execute(
                "INSERT INTO task_type (name, skill, experience) VALUES (?, ?, ?)",
                (task.name, task.skill, task.experience),
            )
        return task

    def update(self, skill: Skill, experience: float) -> None:
        with SQLConnect() as cursor:
            cursor.execute(
                "UPDATE task_type SET skill = ?, experience = ? WHERE id = ?",
                (skill, experience, self.id),
            )

    def delete(self) -> None:
        with SQLConnect() as cursor:
            cursor.execute("DELETE FROM task_type WHERE id = ?", (self.id,))
        self.id = None

    @classmethod
    def search(cls, name: str | None = None) -> List["TaskType"]:
        with SQLConnect() as cursor:
            if name:
                cursor.execute("SELECT * FROM task_type WHERE name = ?", (name,))
            else:
                cursor.execute("SELECT * FROM task_type")
            tasks = cursor.fetchall()
        return [cls(**task) for task in tasks]


class EmotionLog(Table):
    id: int = Field(default=None)
    feeling: Feeling = Field(default=None)
    timestamp: datetime
    duration: int
    trigger: str
    reaction: str
    people_id: List[int]
    task_id: List[int]
    resolved: bool = Field(default=False)

    @staticmethod
    def create_table() -> str:
        sql = """CREATE TABLE IF NOT EXISTS emotion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feeling INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            duration INTEGER NOT NULL,
            trigger TEXT NOT NULL,
            reaction TEXT NOT NULL,
            people_id INTEGER,
            task_id INTEGER,
            resolved INTEGER NOT NULL DEFAULT 0
        )"""
        with SQLConnect() as cursor:
            cursor.execute(sql)

    @classmethod
    def insert(
        cls,
        feeling: Feeling,
        timestamp: datetime,
        duration: int,
        trigger: str,
        reaction: str,
        people_id: List[int],
        task_id: List[int],
    ) -> "EmotionLog":
        log = cls(
            feeling=feeling,
            timestamp=timestamp,
            duration=duration,
            trigger=trigger,
            reaction=reaction,
            people_id=people_id,
            task_id=task_id,
        )
        with SQLConnect() as cursor:
            cursor.execute(
                "INSERT INTO emotion_log (feeling, timestamp, duration, trigger,"
                " reaction, people_id, task_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    log.feeling,
                    log.timestamp,
                    log.duration,
                    log.trigger,
                    log.reaction,
                    log.people_id,
                    log.task_id,
                ),
            )
        return log

    def update(
        self,
        feeling: Feeling,
        timestamp: datetime,
        duration: int,
        trigger: str,
        reaction: str,
        people_id: List[int],
        task_id: List[int],
    ) -> None:
        with SQLConnect() as cursor:
            cursor.execute(
                "UPDATE emotion_log SET feeling = ?, timestamp = ?, duration = ?,"
                " trigger = ?, reaction = ?, people_id = ?, task_id = ? WHERE id = ?",
                (
                    feeling,
                    timestamp,
                    duration,
                    trigger,
                    reaction,
                    people_id,
                    task_id,
                    self.id,
                ),
            )

    def delete(self) -> None:
        with SQLConnect() as cursor:
            cursor.execute("DELETE FROM emotion_log WHERE id = ?", (self.id,))
        self.id = None

    @classmethod
    def search(
        cls,
        id: int | None = None,
        feeling: Feeling | None = None,
        timestamp: datetime | None = None,
        people_ids: int | None = None,
    ) -> List["EmotionLog"]:
        with SQLConnect() as cursor:
            if id:
                cursor.execute("SELECT * FROM emotion_log WHERE id = ?", (id,))
            else:
                cursor.execute("SELECT * FROM emotion_log")
            logs = cursor.fetchall()
        return [cls(**log) for log in logs]
