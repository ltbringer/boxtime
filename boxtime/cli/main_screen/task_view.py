from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, Input, RadioButton, RadioSet

from boxtime.db.schema import TaskType, Skill
from boxtime.utils.logger import logger


class TaskScreen(ModalScreen[Optional[TaskType]]):
    CSS_PATH = "./../css/task_screen.tcss"

    class Insert(Message):
        def __init__(self) -> None:
            super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="modal"):
            with VerticalScroll(classes="box"):
                yield Label("Task category name:")
                yield Input(valid_empty=False, id="task_name")
                yield Label("Skill:")

                with RadioSet(id="skill_option"):
                    yield RadioButton("Soft-skill", value=Skill.SOFT)
                    yield RadioButton("Hard-skill", value=Skill.HARD)

                yield Label("Experience (years):")
                yield Input(valid_empty=False, id="experience", type="number")
                yield Button("Submit", id="submit", variant="primary", classes="button")
                yield Button("Back", id="quit", classes="button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            name = self.query_one("#task_name").value
            skill = self.query_one("#skill_option").pressed_button.value
            experience = self.query_one("#experience").value
            logger.debug(f"Inserting task: {name}, {skill}, {experience}")
            task = TaskType.insert(name, skill, experience)
            self.dismiss(task)
        else:
            self.dismiss(None)
