from pathlib import Path
import matplotlib.pyplot as plt


def save_plot(save_key: str, filename: str):
    par = Path("assets", save_key)
    par.mkdir(parents=True, exist_ok=True)
    path = par / filename
    if path.exists():
        return
    plt.savefig(path, bbox_inches="tight")
