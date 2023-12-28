from typing import List, Dict
from collections import defaultdict
from enum import Enum

from boxtime.client.calendar import Event


class AggField(Enum):
    DAY = "day"
    DAY_OF_WEEK = "day_of_week"
    WEEK = "week"
    MONTH = "month"
    TAG = "tag"


def key_by(event: Event, field: AggField) -> int:
    """
    Get the key to group events by

    Args:
        time_period (TimePeriod): Time period

    Returns:
        str: Key to group events by
    """
    dt = event.start.dt
    keys = {
        AggField.DAY: dt.day - 1,
        AggField.WEEK: dt.isocalendar().week - 1,
        AggField.MONTH: dt.month - 1,
        AggField.DAY_OF_WEEK: dt.isoweekday() - 1,
        AggField.TAG: event.tag,
    }
    return keys[field]


GroupedEvents = Dict[str | int, List[Event] | Dict[str | int, List[Event]]]


def group_by(
    events: List[Event] | Dict[int | str, List[Event]],
    field: AggField = AggField.DAY,
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
            container[key_by(event, field)].append(event)
        return container

    for key, event_list in events.items():
        events[key] = group_by(event_list, field)
    return events


def agg_by(events: List[Event], *fields: AggField) -> Dict[str, Dict[int, float]]:
    inner, outer = fields
    grouped_events: GroupedEvents = group_by(group_by(events, inner), outer)
    events_agg_by_duration = defaultdict(lambda: defaultdict(float))

    for tag, grouped_ in grouped_events.items():
        for week, events in grouped_.items():
            duration = 0
            for event in events:
                duration += event.duration
            events_agg_by_duration[tag][week] = duration

    return events_agg_by_duration
