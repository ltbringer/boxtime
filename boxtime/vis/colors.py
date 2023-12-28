from enum import Enum
from typing import Tuple


class Color(Enum):
    LAVENDER = "1"
    SAGE = "2"
    GRAPE = "3"
    FLAMINGO = "4"
    BANANA = "5"
    TANGERINE = "6"
    PEACOCK = "7"
    GRAPHITE = "8"
    BLUEBERRY = "9"
    BASIL = "10"
    TOMATO = "11"
    UNASSIGNED = "12"


color_map = {
    Color.LAVENDER: "#7986cb",
    Color.SAGE: "#33b679",
    Color.GRAPE: "#8e24aa",
    Color.FLAMINGO: "#e67c73",
    Color.BANANA: "#f6c026",
    Color.TANGERINE: "#f5511d",
    Color.PEACOCK: "#039be5",
    Color.GRAPHITE: "#616161",
    Color.BLUEBERRY: "#3f51b5",
    Color.BASIL: "#0b8043",
    Color.TOMATO: "#d60000",
    Color.UNASSIGNED: "#e3e3e3",
}

dark_colors = [Color.GRAPE, Color.BASIL, Color.BLUEBERRY]
