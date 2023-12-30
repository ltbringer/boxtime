from typing import List

from sqlmodel import select

from boxtime.db.schema import (
    Skill,
    TaskType,
    SQLSession,
)


class TaskRegistry:
    def insert(self, name: str, skill: Skill, experience: float) -> None:
        task = TaskType(name=name, skill=skill, experience=experience)
        with SQLSession() as session:
            session.add(task)
            session.commit()

    def search(self, name: str) -> TaskType:
        with SQLSession() as session:
            task = session.get(TaskType, name)
        return task

    def list(self) -> List[TaskType]:
        with SQLSession() as session:
            tasks = session.exec(select(TaskType)).all()
        return tasks

    def delete(self, name: str) -> None:
        with SQLSession() as session:
            session.delete(TaskType(name=name))
            session.commit()

    def update(self, name: str, skill: Skill, experience: float) -> None:
        with SQLSession() as session:
            task = session.get(TaskType, name)
            task.skill = skill
            task.experience = experience
            session.commit()
