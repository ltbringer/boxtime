from typing import List
from sqlmodel import select

from boxtime.db.schema import (
    People,
    SQLSession,
)


class PeopleRegistry:
    def insert(self, username: str, team: str, role: str) -> None:
        person = People(username=username, team=team, role=role)
        with SQLSession() as session:
            session.add(person)
            session.commit()

    def search(self, username: str) -> People:
        with SQLSession() as session:
            person = session.get(People, username)
        return person

    def list(self) -> List[People]:
        with SQLSession() as session:
            people = session.exec(select(People)).all()
        return people

    def delete(self, username: str) -> None:
        with SQLSession() as session:
            session.delete(People(username=username))
            session.commit()

    def update(self, username: str, team: str, role: str) -> None:
        with SQLSession() as session:
            person = session.get(People, username)
            person.team = team
            person.role = role
            session.commit()
