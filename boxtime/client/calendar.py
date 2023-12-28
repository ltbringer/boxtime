from typing import Dict, List
from datetime import datetime
from enum import Enum
from collections import defaultdict

from pydantic import BaseModel, Field
from googleapiclient.discovery import Resource

from boxtime.auth.scope import Scope
from boxtime.auth.service import get_calendar_client


class TimePeriod(Enum):
    DAY = "day"
    DAY_OF_WEEK = "day_of_week"
    WEEK = "week"
    MONTH = "month"


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

    @property
    def duration(self) -> float:
        """
        Duration of the event in seconds
        """
        seconds_in_an_hour = 3600.0
        return (self.end.dt - self.start.dt).total_seconds() / seconds_in_an_hour


class EventService:
    client: Resource = get_calendar_client(Scope.READ_ONLY)

    @classmethod
    def list(
        cls,
        start: datetime,
        end: datetime,
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
        return [Event(**event) for event in event_objects["items"]]


def key_by(time_period: TimePeriod, dt: datetime) -> int:
    """
    Get the key to group events by

    Args:
        time_period (TimePeriod): Time period

    Returns:
        str: Key to group events by
    """
    key_fn = {
        TimePeriod.DAY: dt.day - 1,
        TimePeriod.WEEK: dt.isocalendar().week - 1,
        TimePeriod.MONTH: dt.month - 1,
        TimePeriod.DAY_OF_WEEK: dt.isoweekday() - 1,
    }
    return key_fn[time_period]


GroupedEvents = Dict[str, List[Event] | Dict[str, List[Event]]]


def group_by(
    events: List[Event] | Dict[str, List[Event]],
    time_period: TimePeriod = TimePeriod.DAY,
) -> GroupedEvents:
    """
    Group events by day

    Args:
        events (List[Event]): List of events

    Returns:
        dict[str, List[Event]]: Dictionary with the date as key and a list of events as value
    """
    container: dict[str, List[Event]] = defaultdict(list)
    if isinstance(events, list):
        for event in events:
            start_dt = event.start.dt
            container[key_by(time_period, start_dt)].append(event)
        return container
    for key, event_list in events.items():
        events[key] = group_by(event_list, time_period)
    return events
