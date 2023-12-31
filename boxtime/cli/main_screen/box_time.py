from typing import Optional, List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    DataTable,
    Static,
)

from boxtime.db.schema import People
from boxtime.cli.art import LOGO
from boxtime.cli.main_screen.people_view import PeopleScreen


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
        with Container(classes="main"):
            with Vertical():
                yield Header()
                yield Static(LOGO)
                yield DataTable(id="data_table")
                yield Footer()

    def on_mount(self) -> None:
        table: DataTable = self.query_one("DataTable")
        table.add_columns("Username", "Team", "Role")
        for person in People.search():
            table.add_row(*[person.username, person.team, person.role])

    def action_add_people(self) -> None:
        def check_people(person: Optional[People]) -> None:
            table = self.query_one("DataTable")
            if person:
                table.add_row(*[person.username, person.team, person.role])

        self.push_screen(PeopleScreen(), check_people)
