from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt

from boxtime.client.calendar import Event
from boxtime.vis.aggregate import group_by, AggField
from boxtime.vis.colors import Color
from boxtime.vis.utils import save_plot


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

    values = list(data.values())

    theta = np.arange(len(values) + 1) / len(values) * 2 * np.pi
    values_ = np.array(values + [values[0]])

    fig = plt.figure(figsize=(20, 10), dpi=300)
    ax = fig.add_subplot(111, polar=True)

    ax.plot(theta, values_, color="C2", marker=".", label="Week N")
    plt.xticks(theta[:-1], [k.title() for k in data.keys()], color="#000", size=8)

    ax.fill(theta, values_, "green", alpha=0.1)
    plt.title("(Un)Balanced time investment.")

    if save_key:
        save_plot(save_key, "radar.png")
