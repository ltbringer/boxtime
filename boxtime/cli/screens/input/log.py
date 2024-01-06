from typing import Optional
from datetime import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll, Horizontal, Grid
from textual.screen import ModalScreen
from textual.message import Message
from textual.widgets import Button, Label, Input, SelectionList, TextArea
from textual.widgets.selection_list import Selection
from textual.validation import Number

from boxtime.db.schema import EmotionLog, Feeling, People, TaskType
from boxtime.utils.logger import logger


class LogScreen(ModalScreen[Optional[EmotionLog]]):
    CSS_PATH = "./../../css/log_screen.tcss"
    BINDINGS = (Binding(key="q", action="back", description="Back"),)

    class Insert(Message):
        def __init__(self) -> None:
            super().__init__()

    def compose(self) -> ComposeResult:
        """
        feeling: Feeling = Field(default=None)
        timestamp: datetime
        duration: int
        trigger: str
        reaction: str
        people_id: List[int]
        task_id: List[int]
        resolved: bool = Field(default=False)
        """
        feeling_selections = []
        for feeling in Feeling:
            feeling_selections.append(
                Selection(feeling.name.capitalize(), value=feeling.value)
            )

        people_selections = []
        for person in People.search():
            people_selections.append(
                Selection(person.username.capitalize(), value=person.id)
            )

        task_selections = []
        for task in TaskType.search():
            task_selections.append(Selection(task.name.capitalize(), value=task.id))

        with VerticalScroll(classes="log-screen-modal"):
            with Container(id="feeling"):
                yield Label("How do you feel?")
                yield SelectionList[int](
                    *feeling_selections,
                    id="feeling-list",
                )

            with Container(id="timestamp"):
                yield Label("What time did this start?")
                with Horizontal():
                    yield Input(
                        valid_empty=False,
                        id="hours",
                        type="integer",
                        placeholder="HH (0 - 23)",
                        classes="half-width",
                        validators=[Number(minimum=0, maximum=23)],
                    )
                    yield Input(
                        valid_empty=False,
                        id="minutes",
                        type="integer",
                        placeholder="MM (0 - 59)",
                        classes="half-width",
                        validators=[Number(minimum=0, maximum=59)],
                    )

            with Container(id="duration"):
                yield Label("How long did it last?")
                yield Input(
                    valid_empty=False,
                    id="duration_text",
                    type="integer",
                    placeholder="Duration in minutes",
                    validators=[Number(minimum=0, maximum=500)],
                )

            with Container(id="people"):
                yield Label("Who were you with?")
                yield SelectionList[int](*people_selections, id="people_list")

            with Container(id="task"):
                yield Label("What were you doing?")
                yield SelectionList[int](*task_selections, id="task_list")

            with Container(id="trigger"):
                yield Label("What triggered it?")
                yield TextArea(id="trigger_text")

            with Container(id="reaction"):
                yield Label("How did you respond?")
                yield TextArea(id="reaction_text")

            with Container(id="buttons"):
                yield Button(
                    "Submit", id="submit", variant="primary", classes="half-width"
                )
                yield Button("Back", id="quit", classes="half-width")

    def on_mount(self) -> None:
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "submit":
                feeling = self.query_one("#feeling-list").selected[0]
                hours = int(self.query_one("#hours").value)
                minutes = int(self.query_one("#minutes").value)
                duration = int(self.query_one("#duration_text").value)
                trigger = self.query_one("#trigger_text").text
                reaction = self.query_one("#reaction_text").text
                people = self.query_one("#people_list").selected
                task = self.query_one("#task_list").selected
                timestamp = datetime.now().replace(
                    hour=hours, minute=minutes, second=0, microsecond=0
                )
                log = EmotionLog.insert(
                    feeling=feeling,
                    timestamp=timestamp,
                    duration=duration,
                    trigger=trigger,
                    reaction=reaction,
                    people_id=people,
                    task_id=task,
                )
                self.dismiss(log)
            case "quit":
                self.dismiss(None)
            case _:
                logger.error(f"Unknown button pressed: {event.button.id}")
