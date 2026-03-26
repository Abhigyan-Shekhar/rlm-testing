import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D


TASKS = [
    "Battle of Bastards",
    "AuthProxy",
    "Clinical Extraction",
    "Launch Plan",
    "PDF Cersei",
    "TSP Branch-Bound",
    "Stochastic TSP",
]

LLM_LATENCY = [1.07, 1.463, 1.956, 8.013, 40.646, 97.285, 85.612]
RLM_LATENCY = [7.403, 13.171, 15.507, 20.671, 134.761, 13.053, 91.699]

LLM_TOKENS = [270, 1512, 2124, 2144, 195109, 4578, 6432]
RLM_TOKENS = [11463, 11003, 11771, 11216, 141006, 17519, 91439]

LLM_ACCURACY = [1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 0.5]
RLM_ACCURACY = [0.5, 0.0, 0.5, 1.0, 0.0, 1.0, 0.5]

# Strict hallucination rubric:
# 1 = README explicitly supports fabricated or guessed content not grounded in the task input
# 0 = wrong, incomplete, or unstable output without clear evidence of fabrication
LLM_HALLUCINATION = [0, 0, 0, 0, 0, 1, 0]
RLM_HALLUCINATION = [0, 0, 0, 0, 1, 0, 0]

LLM_RELIABILITY = [1, 1, 1, 1, 0.5, 0, 0]
RLM_RELIABILITY = [0.5, 0, 0.5, 1, 0, 0.5, 0]

LLM_COST_EFF = [a / math.log10(t) for a, t in zip(LLM_ACCURACY, LLM_TOKENS)]
RLM_COST_EFF = [a / math.log10(t) for a, t in zip(RLM_ACCURACY, RLM_TOKENS)]

LLM_COLOR = "steelblue"
RLM_COLOR = "coral"
BAR_WIDTH = 0.38
OUTPUT_DIR = Path(__file__).resolve().parent


def add_value_labels(ax, containers, fmt="{:.2f}"):
    y_min, y_max = ax.get_ylim()
    for container in containers:
        for bar in container:
            height = bar.get_height()
            label = fmt.format(height)
            text_offset = 4
            va = "bottom"

            # Keep labels inside the plotting area for bounded charts like 0-1 scores.
            if y_max > y_min and height >= (y_max - y_min) * 0.9 + y_min:
                text_offset = -4
                va = "top"

            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, text_offset),
                textcoords="offset points",
                ha="center",
                va=va,
                fontsize=9,
                clip_on=False,
            )


def add_grouped_bars(ax, title, llm_values, rlm_values, ylabel, *, log_scale=False):
    x = np.arange(len(TASKS))
    llm_bars = ax.bar(x - BAR_WIDTH / 2, llm_values, BAR_WIDTH, label="LLM", color=LLM_COLOR)
    rlm_bars = ax.bar(x + BAR_WIDTH / 2, rlm_values, BAR_WIDTH, label="RLM", color=RLM_COLOR)

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(TASKS, rotation=30, ha="right")
    ax.legend()

    if log_scale:
        ax.set_yscale("log")

    return llm_bars, rlm_bars


def create_comparison_figure():
    fig, axes = plt.subplots(2, 3, figsize=(20, 14))
    fig.suptitle("LLM vs RLM Benchmark Comparison", fontsize=18, fontweight="bold")

    latency_bars = add_grouped_bars(
        axes[0, 0],
        "Latency (seconds)",
        LLM_LATENCY,
        RLM_LATENCY,
        "Seconds",
        log_scale=True,
    )
    add_value_labels(axes[0, 0], latency_bars)

    accuracy_bars = add_grouped_bars(
        axes[0, 1],
        "Accuracy",
        LLM_ACCURACY,
        RLM_ACCURACY,
        "Score",
    )
    axes[0, 1].set_ylim(0, 1.08)
    axes[0, 1].axhline(0.5, linestyle="--", color="gray", linewidth=1)
    add_value_labels(axes[0, 1], accuracy_bars)

    token_bars = add_grouped_bars(
        axes[0, 2],
        "Token Usage",
        LLM_TOKENS,
        RLM_TOKENS,
        "Tokens",
        log_scale=True,
    )
    add_value_labels(axes[0, 2], token_bars)

    hallucination_bars = add_grouped_bars(
        axes[1, 0],
        "Hallucination Rate",
        LLM_HALLUCINATION,
        RLM_HALLUCINATION,
        "Rate",
    )
    axes[1, 0].set_ylim(0, 1.08)
    add_value_labels(axes[1, 0], hallucination_bars, fmt="{:.0f}")

    reliability_bars = add_grouped_bars(
        axes[1, 1],
        "Reliability Score",
        LLM_RELIABILITY,
        RLM_RELIABILITY,
        "Score",
    )
    axes[1, 1].set_ylim(0, 1.08)
    add_value_labels(axes[1, 1], reliability_bars)

    cost_eff_bars = add_grouped_bars(
        axes[1, 2],
        "Cost Efficiency (Higher = Better)",
        LLM_COST_EFF,
        RLM_COST_EFF,
        "Accuracy / log10(Tokens)",
    )
    add_value_labels(axes[1, 2], cost_eff_bars)

    fig.text(
        0.5,
        0.02,
        "Sources: llm-test/*.md and rlm-test/*.md logs. Accuracy/Reliability are qualitative scores derived from log outcomes.",
        ha="center",
        va="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))

    output_path = OUTPUT_DIR / "llm_vs_rlm_comparison.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def create_single_metric_chart(
    filename,
    title,
    llm_values,
    rlm_values,
    ylabel,
    *,
    log_scale=False,
    ylim=None,
    dashed_half=False,
    label_fmt="{:.2f}",
):
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = add_grouped_bars(ax, title, llm_values, rlm_values, ylabel, log_scale=log_scale)

    if ylim is not None:
        ax.set_ylim(*ylim)

    if dashed_half:
        ax.axhline(0.5, linestyle="--", color="gray", linewidth=1)

    add_value_labels(ax, bars, fmt=label_fmt)
    fig.tight_layout()
    output_path = OUTPUT_DIR / filename
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def create_sparse_hallucination_chart():
    filtered_tasks = []
    filtered_llm = []
    filtered_rlm = []

    for task, llm_value, rlm_value in zip(TASKS, LLM_HALLUCINATION, RLM_HALLUCINATION):
        if llm_value or rlm_value:
            filtered_tasks.append(task)
            filtered_llm.append(llm_value)
            filtered_rlm.append(rlm_value)

    fig, ax = plt.subplots(figsize=(10, 7))
    x = np.arange(len(filtered_tasks))
    llm_bars = ax.bar(x - BAR_WIDTH / 2, filtered_llm, BAR_WIDTH, label="LLM", color=LLM_COLOR)
    rlm_bars = ax.bar(x + BAR_WIDTH / 2, filtered_rlm, BAR_WIDTH, label="RLM", color=RLM_COLOR)

    ax.set_title("Hallucination Rate (Nonzero Cases Only)", fontsize=16, fontweight="bold")
    ax.set_ylabel("Rate")
    ax.set_xticks(x)
    ax.set_xticklabels(filtered_tasks, rotation=30, ha="right")
    ax.set_ylim(0, 1.08)
    ax.legend()

    add_value_labels(ax, [llm_bars, rlm_bars], fmt="{:.0f}")

    fig.tight_layout()
    output_path = OUTPUT_DIR / "llm_vs_rlm_hallucination.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def create_task_profile_heatmap():
    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
    fig.suptitle("Task Outcome Profiles", fontsize=18, fontweight="bold")

    llm_matrix = np.array([LLM_ACCURACY, LLM_RELIABILITY, LLM_HALLUCINATION], dtype=float)
    rlm_matrix = np.array([RLM_ACCURACY, RLM_RELIABILITY, RLM_HALLUCINATION], dtype=float)
    row_labels = ["Accuracy", "Reliability", "Hallucination"]

    for ax, matrix, title in zip(axes, [llm_matrix, rlm_matrix], ["LLM", "RLM"]):
        sns.heatmap(
            matrix,
            ax=ax,
            cmap="YlOrRd",
            vmin=0,
            vmax=1,
            annot=True,
            fmt=".2g",
            cbar=False,
            linewidths=0.5,
            linecolor="white",
            xticklabels=TASKS,
            yticklabels=row_labels,
        )
        ax.set_title(f"{title} Task Profile", fontsize=12, fontweight="bold")
        ax.tick_params(axis="x", rotation=30)
        ax.tick_params(axis="y", rotation=0)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    output_path = OUTPUT_DIR / "llm_vs_rlm_task_profiles.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def create_efficiency_frontier():
    fig, ax = plt.subplots(figsize=(14, 9))

    llm_sizes = [value * 8 for value in LLM_LATENCY]
    rlm_sizes = [value * 8 for value in RLM_LATENCY]

    ax.scatter(
        LLM_TOKENS,
        LLM_ACCURACY,
        s=llm_sizes,
        color=LLM_COLOR,
        alpha=0.75,
        edgecolor="black",
        linewidth=0.5,
        marker="o",
        label="LLM",
    )
    ax.scatter(
        RLM_TOKENS,
        RLM_ACCURACY,
        s=rlm_sizes,
        color=RLM_COLOR,
        alpha=0.75,
        edgecolor="black",
        linewidth=0.5,
        marker="s",
        label="RLM",
    )

    for task, tokens, accuracy in zip(TASKS, LLM_TOKENS, LLM_ACCURACY):
        ax.annotate(task, (tokens, accuracy), xytext=(6, 6), textcoords="offset points", fontsize=8)
    for task, tokens, accuracy in zip(TASKS, RLM_TOKENS, RLM_ACCURACY):
        ax.annotate(task, (tokens, accuracy), xytext=(6, -10), textcoords="offset points", fontsize=8)

    ax.set_xscale("log")
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Total Tokens (log scale)")
    ax.set_ylabel("Accuracy")
    ax.set_title("Accuracy vs Token Cost (Bubble Size = Latency)", fontsize=16, fontweight="bold")
    ax.axhline(0.5, linestyle="--", color="gray", linewidth=1)
    ax.legend()

    size_legend = [
        Line2D([0], [0], marker="o", color="w", label="~10s latency", markerfacecolor="gray", markersize=8),
        Line2D([0], [0], marker="o", color="w", label="~50s latency", markerfacecolor="gray", markersize=14),
        Line2D([0], [0], marker="o", color="w", label="~100s latency", markerfacecolor="gray", markersize=20),
    ]
    ax.add_artist(ax.legend(handles=size_legend, title="Bubble Guide", loc="lower left"))
    ax.legend(loc="upper right")

    fig.tight_layout()
    output_path = OUTPUT_DIR / "llm_vs_rlm_efficiency_frontier.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def create_summary_averages():
    metrics = ["Latency", "Tokens", "Accuracy", "Reliability", "Hallucination"]
    llm_avg = [
        np.mean(LLM_LATENCY),
        np.mean(LLM_TOKENS),
        np.mean(LLM_ACCURACY),
        np.mean(LLM_RELIABILITY),
        np.mean(LLM_HALLUCINATION),
    ]
    rlm_avg = [
        np.mean(RLM_LATENCY),
        np.mean(RLM_TOKENS),
        np.mean(RLM_ACCURACY),
        np.mean(RLM_RELIABILITY),
        np.mean(RLM_HALLUCINATION),
    ]

    normalized = np.array([llm_avg, rlm_avg], dtype=float)
    for index in range(normalized.shape[1]):
        column_max = normalized[:, index].max()
        if column_max > 0:
            normalized[:, index] /= column_max

    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(metrics))
    llm_bars = ax.bar(x - BAR_WIDTH / 2, normalized[0], BAR_WIDTH, color=LLM_COLOR, label="LLM")
    rlm_bars = ax.bar(x + BAR_WIDTH / 2, normalized[1], BAR_WIDTH, color=RLM_COLOR, label="RLM")

    ax.set_title("Task-Average Summary (Normalized by Metric Max)", fontsize=16, fontweight="bold")
    ax.set_ylabel("Normalized Average")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=20, ha="right")
    ax.set_ylim(0, 1.08)
    ax.legend()

    add_value_labels(ax, [llm_bars, rlm_bars])

    summary_lines = [
        f"Latency avg: LLM {np.mean(LLM_LATENCY):.2f}s vs RLM {np.mean(RLM_LATENCY):.2f}s",
        f"Tokens avg: LLM {np.mean(LLM_TOKENS):,.0f} vs RLM {np.mean(RLM_TOKENS):,.0f}",
        f"Accuracy avg: LLM {np.mean(LLM_ACCURACY):.2f} vs RLM {np.mean(RLM_ACCURACY):.2f}",
        f"Reliability avg: LLM {np.mean(LLM_RELIABILITY):.2f} vs RLM {np.mean(RLM_RELIABILITY):.2f}",
        f"Hallucination avg: LLM {np.mean(LLM_HALLUCINATION):.2f} vs RLM {np.mean(RLM_HALLUCINATION):.2f}",
    ]
    fig.text(0.5, 0.01, " | ".join(summary_lines), ha="center", va="bottom", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output_path = OUTPUT_DIR / "llm_vs_rlm_summary_averages.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def main():
    sns.set_theme(style="whitegrid")

    create_comparison_figure()
    create_single_metric_chart(
        "llm_vs_rlm_latency.png",
        "Latency (seconds)",
        LLM_LATENCY,
        RLM_LATENCY,
        "Seconds",
        log_scale=True,
    )
    create_single_metric_chart(
        "llm_vs_rlm_accuracy.png",
        "Accuracy",
        LLM_ACCURACY,
        RLM_ACCURACY,
        "Score",
        ylim=(0, 1.08),
        dashed_half=True,
    )
    create_single_metric_chart(
        "llm_vs_rlm_tokens.png",
        "Token Usage",
        LLM_TOKENS,
        RLM_TOKENS,
        "Tokens",
        log_scale=True,
    )
    create_single_metric_chart(
        "llm_vs_rlm_reliability.png",
        "Reliability Score",
        LLM_RELIABILITY,
        RLM_RELIABILITY,
        "Score",
        ylim=(0, 1.08),
    )
    create_sparse_hallucination_chart()
    create_single_metric_chart(
        "llm_vs_rlm_cost_efficiency.png",
        "Cost Efficiency (Higher = Better)",
        LLM_COST_EFF,
        RLM_COST_EFF,
        "Accuracy / log10(Tokens)",
    )
    create_task_profile_heatmap()
    create_efficiency_frontier()
    create_summary_averages()

    print("Chart saved to llm_vs_rlm_comparison.png")


if __name__ == "__main__":
    main()
