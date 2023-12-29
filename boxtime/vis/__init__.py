from matplotlib import font_manager
import matplotlib.pyplot as plt
from pathlib import Path

home = str(Path.home())

fp = font_manager.FontProperties(fname=Path.home() / ".fonts/Roboto-Light.ttf")
font_manager.findfont(fp)
custom_font = fp.get_name()

if custom_font == "Roboto":
    plt.rcParams["font.family"] = custom_font
