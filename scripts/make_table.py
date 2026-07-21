#!/usr/bin/env python3
"""Aggregates results/results.csv by (num_catchers, num_runners, alpha)
and prints a LaTeX table with mean +/- stdev of T50/T100."""
import csv
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_CSV = REPO_ROOT / "results" / "results.csv"


def main():
    groups = defaultdict(lambda: {"t50": [], "t100": []})

    with open(RESULTS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            key = (
                int(row["num_catchers"]),
                int(row["num_runners"]),
                float(row["alpha"]),
            )
            groups[key]["t50"].append(float(row["t50"]))
            groups[key]["t100"].append(float(row["t100"]))

    print(r"\begin{table}[H]")
    print(r"\centering")
    print(
        r"\caption{Mean capture times ($\pm$ standard deviation) across "
        r"catcher count, runner count, and distribution factor $\alpha$.}"
    )
    print(r"\label{tab:results}")
    print(r"\begin{tabular}{cccrrc}")
    print(r"\toprule")
    print(
        r"$|\mathcal{C}|$ & $|\mathcal{R}|$ & $\alpha$ & "
        r"$T_{50}$ (s) & $T_{100}$ (s) & $n$ \\"
    )
    print(r"\midrule")

    for c, r, a in sorted(groups):
        t50s = groups[(c, r, a)]["t50"]
        t100s = groups[(c, r, a)]["t100"]
        n = len(t50s)
        t50_std = statistics.stdev(t50s) if n > 1 else 0.0
        t100_std = statistics.stdev(t100s) if n > 1 else 0.0
        print(
            f"{c} & {r} & {a:.2f} & "
            f"{statistics.mean(t50s):.2f} $\\pm$ {t50_std:.2f} & "
            f"{statistics.mean(t100s):.2f} $\\pm$ {t100_std:.2f} & "
            f"{n} \\\\"
        )

    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


if __name__ == "__main__":
    main()
