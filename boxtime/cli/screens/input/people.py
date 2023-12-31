from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.message import Message
from textual.widgets import (
    Button,
    Label,
    Input,
)

from boxtime.db.schema import People


class PeopleScreen(ModalScreen[Optional[People]]):
    CSS_PATH = "./../../css/people_screen.tcss"

    class Insert(Message):
        def __init__(self) -> None:
            super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="modal"):
            with VerticalScroll(classes="box"):
                yield Label("Username:")
                yield Input(valid_empty=False, id="username")
                yield Label("Team:")
                yield Input(valid_empty=False, id="team")
                yield Label("Role:")
                yield Input(valid_empty=False, id="role")
                yield Button("Submit", id="submit", variant="primary", classes="button")
                yield Button("Back", id="quit", classes="button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            username = self.query_one("#username").value
            team = self.query_one("#team").value
            role = self.query_one("#role").value
            person = People.insert(username, team, role)
            self.dismiss(person)
        else:
            self.dismiss(None)
