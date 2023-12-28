from typing import List
from pathlib import Path

import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from boxtime.client.calendar import Event
from boxtime.vis.aggregate import agg_by, AggField


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
    events_agg_by_duration = agg_by(events, AggField.DAY_OF_WEEK, AggField.WEEK)

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

    plt.figure(figsize=(20, 15), dpi=300)
    ax = heatmap(
        data,
        square=True,
        annot=True,
        fmt=".0f",
        cbar=False,
        cbar_kws={"shrink": 0.4},
        vmax=15,
        linewidths=0.2,
        linecolor="#ffffff",
        cmap=cmap,
        yticklabels=days_of_week.values(),
    )

    ax.set_xlabel("# Week", fontsize=14)
    ax.set_ylabel("Days", fontsize=14)

    if save_key:
        par = Path("assets", save_key)
        par.mkdir(parents=True, exist_ok=True)
        path = par / "heatmap.png"
        if path.exists():
            return
        plt.savefig(path)
