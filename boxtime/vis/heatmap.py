from typing import List
from collections import defaultdict

import numpy as np
from seaborn import heatmap

from boxtime.client.calendar import Event, group_by, GroupedEvents, TimePeriod


def plot_heatmap(events: List[Event]):
    """
    Plot a heatmap of the events
    """
    n_rows = 7
    n_cols = 52
    data = np.zeros((n_rows, n_cols))
    grouped_events: GroupedEvents = group_by(
        group_by(events, TimePeriod.DAY_OF_WEEK), TimePeriod.WEEK
    )
    events_agg_by_duration = defaultdict(lambda: defaultdict(float))
    for day, grouped_ in grouped_events.items():
        for week, events in grouped_.items():
            duration = 0
            for event in events:
                duration += event.duration
            events_agg_by_duration[day][week] = duration
    return events_agg_by_duration, grouped_events
