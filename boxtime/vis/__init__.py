from matplotlib import font_manager
import matplotlib.pyplot as plt
from pathlib import Path

home = str(Path.home())

fp = font_manager.FontProperties(fname=Path.home() / ".fonts/Roboto-Light.ttf")
font_manager.findfont(fp)
plt.rcParams["font.family"] = fp.get_name()
# plt.rcParams["font.weight"] = "light"
