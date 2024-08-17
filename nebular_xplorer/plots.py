import matplotlib.pyplot as plt
import seaborn as sns

from .stat import cal_nav, DDS

def snapshot(return_table):
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*1.2)
    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex='col', gridspec_kw={'height_ratios': [2, 1, 1]})
    for ax in axes:
        for spine in ax.spines:
            ax.spines[spine].set_visible(False)
        ax.grid(alpha=0.3)
    for col in return_table.columns:
        axes[0].plot(
            cal_nav(return_table[col]) * 100,
            label=col,
            zorder=1,
        )
    dd = -DDS(return_table)*100
    for col in dd.columns:
        axes[1].plot(dd[col], label=col.replace('_dd', ''), lw=1, zorder=1)
    for col in dd.columns:
        axes[1].fill_between(
            dd[col].index, 0, dd[col], alpha=0.25
        )
    axes[1].axhline(0, color="silver", lw=1.5, zorder=0)
    axes[0].axhline(100, color="silver", lw=1.5, zorder=0, linestyle='--')
    axes[2].axhline(0, linestyle="--", lw=0.5, zorder=2)

    for i, col in enumerate(return_table.columns):
        axes[2].plot(
            return_table[col],
            label=col,
            zorder=1,
        )
    axes[0].legend(fontsize=6, ncol=2, frameon=False)
    axes[1].set_ylabel("Drawdown", fontweight="bold", fontsize=12)
    axes[0].set_ylabel("Net Value", fontweight="bold", fontsize=12)
    axes[2].set_ylabel("Returns", fontweight="bold", fontsize=12)
    plt.tight_layout()
    fig.suptitle("Portfolia Performance", fontsize=10)
    return fig


def groupNav(return_table):
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*0.6)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    for col in return_table.columns:
        ax.plot(
            cal_nav(return_table[col]) * 100,
            label=col,
            zorder=1,
        )
    ax.axhline(100, color="silver", lw=1.5, zorder=0, linestyle='--')
    ax.legend(fontsize=6, ncol=2, frameon=False)
    ax.set_ylabel("Net Value", fontweight="bold", fontsize=12)
    ax.grid(alpha=0.3)
    for spine in ax.spines:
        ax.spines[spine].set_visible(False)
    ax.title.set_text("Group Net Value")
    plt.tight_layout()
    return fig