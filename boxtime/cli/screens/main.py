from typing import Optional, List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    DataTable,
    Static,
)

from boxtime.db.schema import People, TaskType, EmotionLog
from boxtime.cli.art import LOGO
from boxtime.cli.screens.input.people import PeopleScreen
from boxtime.cli.screens.input.task import TaskScreen
from boxtime.cli.screens.input.log import LogScreen


class BoxTime(App):
    """An app with a modal dialog."""

    CSS_PATH = "./../css/main.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="t", action="add_task", description="Add a task category"),
        Binding(key="p", action="add_people", description="Add a person"),
        Binding(key="l", action="add_log", description="Log a new emotion"),
    ]

    rows: List[People] = reactive([], layout=True)

    def compose(self) -> ComposeResult:
        yield Header(name="BoxTime", show_clock=True)
        with Grid(classes="main"):
            yield DataTable(id="people_list")
            yield DataTable(id="emotion_logs", classes="primary")
            yield Static("")
            yield DataTable(id="task_list")
            yield Static("")
            yield Static("")
            yield Static("")
            yield Static("")
            yield Static("")
            yield Static("")
            yield Static("")
            yield Static("")
        yield Footer()

    def on_mount(self) -> None:
        people_list: DataTable = self.query_one("#people_list")
        people_list.add_columns("ID", "Username", "Team", "Role")

        task_list: DataTable = self.query_one("#task_list")
        task_list.add_columns("ID", "Task", "Skill", "Experience")

        emotion_logs: DataTable = self.query_one("#emotion_logs")
        emotion_logs.add_columns(
            "ID",
            "Emotion",
            "Timestamp",
            "People",
            "Task",
        )

        for person in People.search():
            people_list.add_row(*[person.id, person.username, person.team, person.role])

        for task in TaskType.search():
            task_list.add_row(*[task.id, task.name, task.skill, task.experience])

        for log in EmotionLog.search():
            emotion_logs.add_row(
                *[
                    log.id,
                    log.feeling,
                    log.timestamp,
                    [person.username for person in log.people],
                    [task.name for task in log.task],
                ]
            )

    def action_add_people(self) -> None:
        def check_people(person: Optional[People]) -> None:
            people_list = self.query_one("#people_list")

            if person:
                people_list.add_row(
                    *[person.id, person.username, person.team, person.role]
                )

        self.push_screen(PeopleScreen(), check_people)

    def action_add_task(self) -> None:
        def check_task(task: Optional[TaskType]) -> None:
            task_list = self.query_one("#task_list")

            if task:
                task_list.add_row(*[task.id, task.name, task.skill, task.experience])

        self.push_screen(TaskScreen(), check_task)

    def action_add_log(self) -> None:
        def check_log(log: Optional[EmotionLog]) -> None:
            emotion_logs = self.query_one("#emotion_logs")
            if log:
                emotion_logs.add_row(
                    *[log.id, log.feeling, log.timestamp, log.people, log.task]
                )

        self.push_screen(LogScreen(), check_log)
