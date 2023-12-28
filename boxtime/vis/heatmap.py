from typing import List
from collections import defaultdict
from pathlib import Path

import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from boxtime.client.calendar import Event, group_by, GroupedEvents, TimePeriod


def agg_by_duration(events: List[Event]) -> dict[str, float]:
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
    return events_agg_by_duration


def make_cmap(cmap: dict[str, int]) -> LinearSegmentedColormap:
    color_transitions = []
    for key, value in cmap.items():
        color_transitions.append((value / 15, key))
    cmap_ = LinearSegmentedColormap.from_list("cmap", color_transitions, N=256)
    return cmap_


def plot_heatmap(events: List[Event], save_key: str | None = None):
    """
    Plot a heatmap of the events
    """
    n_rows = 7
    n_cols = 52
    data = np.zeros((n_rows, n_cols))
    events_agg_by_duration = agg_by_duration(events)

    for day, grouped_ in events_agg_by_duration.items():
        for week, duration in grouped_.items():
            data[day][week] = duration

    cmap = make_cmap(
        {"#fff5f1": 0, "#fee4b1": 4, "green": 8, "#f97397": 10, "#fe4848": 15}
    )

    plt.figure(figsize=(20, 10))
    heatmap(
        data,
        square=True,
        annot=True,
        fmt=".0f",
        cbar_kws={"shrink": 0.4},
        vmax=15,
        cmap=cmap,
    )

    if save_key:
        path = Path("assets", save_key, "heatmap.png").mkdir(
            parents=True, exist_ok=True
        )
        plt.savefig(path)
