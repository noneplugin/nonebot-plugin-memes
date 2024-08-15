from io import BytesIO

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.font_manager import fontManager
from matplotlib.ticker import MaxNLocator
from nonebot.utils import run_sync

matplotlib.use("agg")
fallback_fonts = [
    "PingFang SC",
    "Hiragino Sans GB",
    "Microsoft YaHei",
    "Source Han Sans SC",
    "Noto Sans SC",
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
]
for fontfamily in fallback_fonts.copy():
    try:
        fontManager.findfont(fontfamily, fallback_to_default=False)
    except ValueError:
        fallback_fonts.remove(fontfamily)
matplotlib.rcParams["font.family"] = fallback_fonts


@run_sync
def plot_meme_and_duration_counts(
    meme_counts: dict[str, int], duration_counts: dict[str, int], title: str
) -> BytesIO:
    up_x = list(meme_counts.keys())
    up_y = list(meme_counts.values())
    low_x = list(duration_counts.keys())
    low_y = list(duration_counts.values())
    up_height = len(up_x) * 0.3
    low_height = 3
    fig_width = 8
    fig, axs = plt.subplots(
        nrows=2,
        figsize=(fig_width, up_height + low_height),
        height_ratios=[up_height, low_height],
    )
    up: Axes = axs[0]
    up.barh(up_x, up_y, height=0.6)
    up.xaxis.set_major_locator(MaxNLocator(integer=True))
    low: Axes = axs[1]
    low.plot(low_x, low_y, marker="o")
    if len(low_x) > 24:
        low.set_xticks(low_x[::3])
    elif len(low_x) > 12:
        low.set_xticks(low_x[::2])
    low.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.suptitle(title)
    fig.tight_layout()
    output = BytesIO()
    fig.savefig(output)
    return output


@run_sync
def plot_duration_counts(duration_counts: dict[str, int], title: str) -> BytesIO:
    x = list(duration_counts.keys())
    y = list(duration_counts.values())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, marker="o")
    if len(x) > 24:
        ax.set_xticks(x[::3])
    elif len(x) > 12:
        ax.set_xticks(x[::2])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.suptitle(title)
    fig.tight_layout()
    output = BytesIO()
    fig.savefig(output)
    return output
