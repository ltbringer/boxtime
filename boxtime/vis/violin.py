from typing import Dict, List

import numpy as np
import pandas as pd
from seaborn import violinplot, color_palette
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from boxtime.client.calendar import Event
from boxtime.vis.aggregate import agg_by, AggField
from boxtime.vis.colors import color_map, Color
from boxtime.vis.utils import save_plot


def plot_violin(
    events: List[Event],
    tags: Dict[Color, str],
    period: AggField,
    save_key: str | None = None,
):
    """
    Plot a violin plot of the events
    """
    events_agg_by_duration_tags = agg_by(
        events,
        AggField.TAG,
        period,
    )
    df = pd.DataFrame.from_dict(events_agg_by_duration_tags)
    df.fillna(0, inplace=True)

    # Set a color palette for the violin plots
    reverse_tags = {v: k for k, v in tags.items()}
    hex_colors = [
        color_map[reverse_tags.get(col, Color.UNASSIGNED)] for col in df.columns
    ]
    colors = color_palette(hex_colors)
    columns = {col: col.title() for col in df.columns}
    df.rename(columns=columns, inplace=True)

    # Create the violin plot
    plt.figure(figsize=(20, 12), dpi=300)

    ax = violinplot(
        data=df,
        inner="quart",
        palette=colors,
        legend=False,
        cut=0,
        fill=False,
        linewidth=1,
    )

    # Add gridlines
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, color="#333333", which="major")

    # Customize labels and title
    ax.set_xlabel("Categories", fontsize=14)
    ax.set_ylabel("Hours", fontsize=14)
    ax.set_title(
        "Different modes of task priority.",
        fontsize=16,
    )

    for i, col in enumerate(df.columns):
        x = i
        median = 0.5
        quantiles = df[col].quantile([median])
        modes = df[col].value_counts().nlargest(3)
        print_median = True

        for j, mode in enumerate(modes.index):
            ax.text(
                i,
                mode,
                f"M{j + 1}: {mode:.1f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )
            if print_median and abs(quantiles[median] - mode) < 0.2:
                print_median = False

        if print_median:
            ax.text(
                x,
                quantiles[median],
                f"Med: {quantiles[median]:.1f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    custom_legend = [
        Line2D(
            [0],
            [0],
            color="#ffffff",
            lw=1,
            label="M1 - Mode 1 or most common observation.",
        ),
        Line2D([0], [0], color="#ffffff", lw=1, label="M2 - Mode 2"),
        Line2D([0], [0], color="#ffffff", lw=1, label="M3 - Mode 3"),
        Line2D([0], [0], color="#ffffff", lw=1, label="Med - Median"),
    ]

    # Add the legend to the plot
    plt.legend(handles=custom_legend, title="Legend", loc="upper right")

    if save_key:
        save_plot(save_key, "violin.png")
