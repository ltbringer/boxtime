from typing import Dict, List
from pathlib import Path

import pandas as pd
from seaborn import violinplot, color_palette
import matplotlib.pyplot as plt

from boxtime.client.calendar import Event
from boxtime.vis.aggregate import agg_by, AggField
from boxtime.vis.colors import color_map, Color, dark_colors


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

    # Create the violin plot
    plt.figure(figsize=(20, 12))
    plt.gca().set_facecolor("#ede6ce")

    ax = violinplot(data=df, inner="quart", palette=colors, legend=True)

    # Add gridlines
    ax.yaxis.grid(True, linestyle="--", alpha=0.6)

    # Customize labels and title
    ax.set_xlabel("Categories", fontsize=14)
    ax.set_ylabel("Values", fontsize=14)
    ax.set_title("Time distribution", fontsize=16)

    for i, col in enumerate(df.columns):
        x = i
        median = 0.5
        quantiles = df[col].quantile([median])
        modes = df[col].value_counts().nlargest(3)
        print_median = True

        for j, mode in enumerate(modes.index):
            plot_color = reverse_tags.get(col, Color.UNASSIGNED)
            ax.text(
                i,
                mode,
                f"M{j + 1}: {mode:.1f}",
                ha="center",
                va="bottom",
                fontsize=10,
                # color="white" if plot_color in dark_colors else "black",
                # weight="bold" if plot_color in dark_colors else "normal",
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
                # color="white" if plot_color in dark_colors else "black",
                # weight="bold" if plot_color in dark_colors else "normal",
            )

    # Customize legend
    # handles, labels = ax.get_legend_handles_labels()
    # ax.legend(handles, labels, title="Categories", title_fontsize=12, loc="upper right")

    # Save the plot if a save_key is provided
    # if save_key:
    #     plt.savefig(f"{save_key}.png", bbox_inches="tight")

    plt.show()
