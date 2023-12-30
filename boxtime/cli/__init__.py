import os
from rich.table import Table
from rich.layout import Layout
from rich import print

from boxtime.db.schema import create_db_and_tables
from boxtime.utils.console import console
from boxtime.cli.people import PeopleRegistry
from boxtime.cli.task import TaskRegistry
from boxtime.db.schema import People
from rich.panel import Panel


def people_layout(layout: Layout):
    all_people = PeopleRegistry().list()
    table = Table(title="People")
    table.add_column("ID", style="cyan")
    table.add_column("USERNAME")
    table.add_column("TEAM")
    table.add_column("ROLE")

    for person in all_people:
        table.add_row(str(person.id), person.username, person.team, person.role)
    layout["people"].update(Panel(table, border_style="blue"))


def task_layout(layout: Layout):
    all_tasks = TaskRegistry().list()
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("NAME")
    table.add_column("SKILL")
    table.add_column("EXPERIENCE")

    for task in all_tasks:
        table.add_row(str(task.id), task.name, task.skill, task.experience)
    layout["tasks"].update(Panel(table, border_style="blue"))


def setup_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="logs"), Layout(name="data"), Layout(name="commands")
    )
    layout["data"].split_row(Layout(name="people"), Layout(name="tasks"))
    return layout


def main():
    os.system("clear")
    console.rule("BoxTime")
    layout = setup_layout()
    with console.status("Setting things up..."):
        create_db_and_tables()
    people_layout(layout)
    task_layout(layout)
    print(layout)
