from typing import Dict, List

import pandas as pd
import numpy as np
from seaborn import violinplot, color_palette
import matplotlib.pyplot as plt

from boxtime.client.calendar import Event
from boxtime.vis.aggregate import group_by, AggField
from boxtime.vis.colors import color_map, Color


def plot_radar(
    events: List[Event],
    tags: Dict[Color, str],
    save_key: str | None = None,
):
    events_agg_by_duration_tags = group_by(
        events,
        AggField.TAG,
    )
    reverese_tags = {v: k for k, v in tags.items()}
    data = {}

    for tag, t_events in events_agg_by_duration_tags.items():
        if tag not in reverese_tags:
            continue
        data[tag] = sum([e.duration for e in t_events])

    normalized_values = list(data.values())

    theta = np.arange(len(normalized_values) + 1) / len(normalized_values) * 2 * np.pi
    values = np.array(normalized_values + [normalized_values[0]])

    fig = plt.figure(figsize=(20, 10), dpi=300)
    ax = fig.add_subplot(111, polar=True)
    ax.plot(theta, values, color="C2", marker=".", label="Week N")
    plt.xticks(
        theta[:-1], [k.title() for k in reverese_tags.keys()], color="#000", size=8
    )
    ax.fill(theta, values, "green", alpha=0.1)

    plt.title("Title")
    plt.show()
