from typing import List

import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from boxtime.vendor.calendar import Event
from boxtime.vis.aggregate import agg_by, AggregateBy
from boxtime.vis.utils import save_plot


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
    events_agg_by_duration = agg_by(events, AggregateBy.DAY_OF_WEEK, AggregateBy.WEEK)

    for day, grouped_ in events_agg_by_duration.items():
        for week, duration in grouped_.items():
            data[day][week] = duration

    cmap = make_cmap(
        {"#fff5f1": 0, "#fee4b1": 4, "green": 8, "#fe8888": 10, "#fe4848": 15}
    )

    days_of_week = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    plt.figure(figsize=(20, 5), dpi=300)
    ax = heatmap(
        data,
        square=True,
        annot=True,
        fmt=".0f",
        cbar=False,
        cbar_kws={"shrink": 0.4},
        vmax=15,
        linewidths=1,
        linecolor="#ffffff",
        cmap=cmap,
        yticklabels=days_of_week.values(),
    )
    ax.set_title(
        "Quality of time spent.",
        fontsize=16,
    )
    ax.set_xlabel("Weeks", fontsize=14)
    ax.set_ylabel("Days", fontsize=14)

    if save_key:
        save_plot(save_key, "heatmap.png")
