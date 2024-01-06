import sqlite3
import abc
from enum import Enum
from typing import Dict, List, Optional
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
    BOTH = 2
    NONE = 3


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
    def search(
        cls, username: str | None = None, id: int | None = None
    ) -> List["People"]:
        with SQLConnect() as cursor:
            if username:
                cursor.execute("SELECT * FROM people WHERE username = ?", (username,))
            elif id:
                cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
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
    def search(cls, name: str | None = None, id: int | None = None) -> List["TaskType"]:
        with SQLConnect() as cursor:
            if name:
                cursor.execute("SELECT * FROM task_type WHERE name = ?", (name,))
            elif id:
                cursor.execute("SELECT * FROM task_type WHERE id = ?", (id,))
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
    people: List[People] = Field(default_factory=list)
    task: List[TaskType] = Field(default_factory=list)
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
            people_id TEXT,
            task_id TEXT,
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
        with SQLConnect() as cursor:
            cursor.execute(
                "INSERT INTO emotion_log (feeling, timestamp, duration, trigger,"
                " reaction, people_id, task_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feeling,
                    timestamp,
                    duration,
                    trigger,
                    reaction,
                    str(people_id),
                    str(task_id),
                ),
            )
            id_ = cursor.lastrowid
        people = [people for id_ in people_id for people in People.search(id=id_)]
        task = [task for id_ in task_id for task in TaskType.search(id=id_)]
        return cls(
            id=id_,
            feeling=feeling,
            timestamp=timestamp,
            duration=duration,
            trigger=trigger,
            reaction=reaction,
            people=people,
            task=task,
        )

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
        time_range: Dict[str, datetime] | None = None,
    ) -> List["EmotionLog"]:
        with SQLConnect() as cursor:
            if id:
                cursor.execute("SELECT * FROM emotion_log WHERE id = ?", (id,))
            elif feeling:
                cursor.execute(
                    "SELECT * FROM emotion_log WHERE feeling = ?", (feeling,)
                )
            elif time_range:
                start = time_range["start"]
                end = time_range["end"]
                cursor.execute(
                    "SELECT * FROM emotion_log WHERE timestamp BETWEEN ? AND ?",
                    (start, end),
                )
            else:
                cursor.execute("SELECT * FROM emotion_log")
            log_data = cursor.fetchall()

        logs = []
        for log_ in log_data:
            log = {}
            log["id"] = log_["id"]
            log["people"] = [
                people for id_ in log_["people_id"] for people in People.search(id=id_)
            ]
            log["task"] = [
                task for id_ in log_["task_id"] for task in TaskType.search(id=id_)
            ]
            log["timestamp"] = datetime.fromisoformat(log_["timestamp"])
            log["feeling"] = Feeling(log_["feeling"])
            log["timestamp"] = datetime.fromisoformat(log_["timestamp"])
            log["duration"] = log_["duration"]
            log["trigger"] = log_["trigger"]
            log["reaction"] = log_["reaction"]
            logs.append(cls(**log))
        return logs
