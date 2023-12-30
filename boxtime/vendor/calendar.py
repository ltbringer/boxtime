import json
from typing import Dict, List, ClassVar
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field
from googleapiclient.discovery import Resource

from boxtime.auth.scope import Scope
from boxtime.auth.service import get_calendar_client
from boxtime.vis.colors import Color


class CalendarUser(BaseModel):
    email: str
    response_status: str | None = Field(alias="responseStatus", default=None)
    organizer: bool | None = Field(default=None)
    self: bool | None = Field(default=None)


class Time(BaseModel):
    date_time: str = Field(alias="dateTime")
    time_zone: str = Field(alias="timeZone")

    @property
    def dt(self) -> datetime:
        return datetime.strptime(self.date_time, "%Y-%m-%dT%H:%M:%S%z")


class Event(BaseModel):
    id: str
    color_id: str | None = Field(alias="colorId", default=None)
    created: datetime = Field(repr=False)
    updated: datetime = Field(repr=False)
    title: str | None = Field(alias="summary", default=None)
    description: str | None = Field(default=None)
    status: str
    location: str | None = Field(default=None)
    creator: CalendarUser | None = Field(default=None, repr=False)
    organizer: CalendarUser | None = Field(default=None, repr=False)
    start: Time = Field(repr=False)
    end: Time = Field(repr=False)
    url: str = Field(alias="htmlLink", repr=False)
    tags: ClassVar[Dict[str, str]] = {}
    attendees: List[CalendarUser] = Field(default_factory=list, repr=False)

    @classmethod
    def set_tags(cls, tags: Dict[str, str]):
        cls.tags = tags

    @property
    def duration(self) -> float:
        """
        Duration of the event in seconds
        """
        seconds_in_an_hour = 3600.0
        return (self.end.dt - self.start.dt).total_seconds() / seconds_in_an_hour

    @property
    def tag(self) -> str | None:
        """
        Color tag of the event
        """
        if not self.color_id:
            return "unassigned"
        return Event.tags[self.color_id]


class EventService:
    client: Resource = get_calendar_client(Scope.READ_ONLY)

    @classmethod
    def list(
        cls,
        start: datetime,
        end: datetime,
        tags: Dict[Color, str],
        calendar_id: str = "primary",
        show_deleted: bool = False,
        expand_recurring: bool = True,
    ) -> List[Event]:
        """
        List events in a calendar

        Args:
            start (datetime): Start of the time range
            end (datetime): End of the time range
            calendar_id (str, optional): Calendar ID. Defaults to "primary".
            show_deleted (bool, optional): Show deleted events. Defaults to False.
            expand_recurring (bool, optional): True: Creates an event for every instance of a
                recurring event. False: Only a single event for the recurring event.
                Defaults to True.
        """
        args_key = f"{calendar_id}_{start.date()}_{end.date()}_{show_deleted}_{expand_recurring}"

        par = Path("assets", "events")
        par.mkdir(parents=True, exist_ok=True)
        path = par / args_key
        event_objects = {}

        if path.exists():
            with open(path) as f:
                event_objects["items"] = json.load(f)
        else:
            event_objects = (
                cls.client.events()
                .list(
                    timeMin=start.isoformat() + "Z",
                    timeMax=end.isoformat() + "Z",
                    calendarId=calendar_id,
                    showDeleted=show_deleted,
                    singleEvents=expand_recurring,
                )
                .execute()
            )

            with open(path, "w") as f:
                json.dump(event_objects["items"], f)

        Event.set_tags({k.value: v for k, v in tags.items()})
        return [Event(**event) for event in event_objects["items"]]
