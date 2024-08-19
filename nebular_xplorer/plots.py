import matplotlib.pyplot as plt
import seaborn as sns

from .stat import cal_nav, DDS, dd_details

def snapshot(return_table):
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*1.2)
    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex='col', gridspec_kw={'height_ratios': [2, 0.7, 0.7]})
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
    fig.suptitle("Portfolia Performance", fontsize=10)
    plt.tight_layout()
    return fig


def groupNav(return_table):
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*0.8)
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
    plt.title(f"Group{len(return_table.columns)} Performance", fontsize=14, fontweight="bold")
    return fig

def ic(ic_data):
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*1.2)
    fig, axes = plt.subplots(2, 1, figsize=figsize, gridspec_kw={'height_ratios': [2, 1]})
    for ax in axes:
        for spine in ax.spines:
            ax.spines[spine].set_visible(False)
        ax.grid(alpha=0.3)
    for col in ic_data.columns:
        axes[0].plot(ic_data[col].cumsum(), label=col, zorder=1)
    axes[0].legend(fontsize=6, ncol=2, frameon=False)
    axes[0].set_ylabel("Cum IC", fontweight="bold", fontsize=12)
    ax_bar = axes[0].twinx()
    for spine in ax_bar.spines:
        ax_bar.spines[spine].set_visible(False)
    for col in ic_data.columns:
        ax_bar.bar(ic_data.index, ic_data[col], label=col, zorder=1)
    ax_bar.set_ylabel("IC", fontweight="bold", fontsize=12)
    sns.histplot(ic_data, ax=axes[1], bins=40, kde=True, alpha=0.5)
    mean_value = ic_data.mean().values[0]
    axes[1].axvline(
            mean_value,
            ls="--",
            lw=1.5,
            zorder=2,
            label="Average",
            color="red",
        )
    axes[1].text(
        mean_value,  
        axes[1].get_ylim()[0] * 1.05,  
        f'{mean_value:.2f}', 
        color="red", 
        fontsize=10,  
        fontweight="bold",  
        ha="center",  
    )
    axes[1].set_ylabel("Density", fontweight="bold", fontsize=12)
    plt.title("Information Coefficient", fontsize=14, fontweight="bold")
    return fig

def icHeatMap(ic_data):
    monthly_ic = ic_data.resample("ME").mean()
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*0.6)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    monthly_ic["year"] = monthly_ic.index.year
    monthly_ic["month"] = monthly_ic.index.month
    monthly_ic = monthly_ic.pivot(index='year', columns='month', values=ic_data.columns[0])
    sns.heatmap(monthly_ic, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, center=0, cbar_kws={'label': 'IC'}, annot_kws={"fontsize": 8})
    ax.set_ylabel("Year", fontweight="bold", fontsize=12)
    plt.title("Monthly IC Heatmap", fontsize=14, fontweight="bold")
    return fig

def returnHeatMap(return_table):
    monthly_return = return_table.resample("ME").sum()
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*0.6)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    monthly_return["year"] = monthly_return.index.year
    monthly_return["month"] = monthly_return.index.month
    monthly_return = monthly_return.pivot(index='year', columns='month', values=return_table.columns[0])
    sns.heatmap(monthly_return, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, center=0, cbar_kws={'label': 'Return'}, annot_kws={"fontsize": 8})
    ax.set_ylabel("Year", fontweight="bold", fontsize=12)
    plt.title("Monthly Return Heatmap", fontsize=14, fontweight="bold")
    return fig

def ddNav(return_table, n=5):
    ddd = dd_details(return_table)[:n]
    top_start = [x.index[0] for x in ddd]
    top_end = [x.index[-1] for x in ddd]
    size = list(plt.gcf().get_size_inches())
    figsize = (size[0], size[1]*0.5)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    for spine in ax.spines:
        ax.spines[spine].set_visible(False)
    ax.plot(return_table.add(1).cumprod())
    for i in range(len(top_start)):
        ax.axvspan(top_start[i], top_end[i], color='red', alpha=0.3)
    ax.set_ylabel("Net Value", fontweight="bold", fontsize=12)
    plt.title("Top Drawdown Periods", fontsize=14, fontweight="bold")
    return fig