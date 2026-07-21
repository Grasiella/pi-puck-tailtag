#!/usr/bin/env python3
"""Runs the tailtag experiment grid by launching a fresh headless Webots
process per trial (each process exits on its own once T100 is logged,
via AUTO_QUIT=1 read by controllers/supervisor/supervisor.py)."""
import csv
import itertools
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORLD = REPO_ROOT / "worlds" / "tailtag.wbt"
RESULTS_CSV = REPO_ROOT / "results" / "results.csv"
WEBOTS_BIN = os.environ.get(
    "WEBOTS_BIN", "/Applications/Webots.app/Contents/MacOS/webots"
)

NUM_RUNNERS = int(os.environ.get("NUM_RUNNERS", "10"))
CATCHER_COUNTS = [int(x) for x in os.environ.get("CATCHER_COUNTS", "5,10,15,20").split(",")]
ALPHAS = [float(x) for x in os.environ.get("ALPHAS", "0.0,0.25,0.5,0.75,1.0").split(",")]
REPEATS = int(os.environ.get("REPEATS", "5"))
TRIAL_TIMEOUT_S = int(os.environ.get("TRIAL_TIMEOUT_S", "240"))


def count_existing(num_catchers, num_runners, alpha):
    if not RESULTS_CSV.exists():
        return 0

    count = 0
    with open(RESULTS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            try:
                if (
                    int(row["num_catchers"]) == num_catchers
                    and int(row["num_runners"]) == num_runners
                    and abs(float(row["alpha"]) - alpha) < 1e-9
                ):
                    count += 1
            except (KeyError, ValueError):
                continue

    return count


def run_trial(num_catchers, alpha):
    env = os.environ.copy()
    env.update(
        {
            "NUM_CATCHERS": str(num_catchers),
            "NUM_RUNNERS": str(NUM_RUNNERS),
            "ALPHA": str(alpha),
            "AUTO_QUIT": "1",
        }
    )
    cmd = [
        WEBOTS_BIN,
        "--mode=fast",
        "--minimize",
        "--no-rendering",
        "--stdout",
        "--stderr",
        "--batch",
        str(WORLD),
    ]
    try:
        subprocess.run(
            cmd,
            env=env,
            timeout=TRIAL_TIMEOUT_S,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        print(f"  [!] timed out (C={num_catchers}, alpha={alpha}) - skipped", file=sys.stderr)


def main():
    combos = list(itertools.product(CATCHER_COUNTS, ALPHAS))
    remaining_per_combo = {}

    for num_catchers, alpha in combos:
        existing = count_existing(num_catchers, NUM_RUNNERS, alpha)
        remaining_per_combo[(num_catchers, alpha)] = max(0, REPEATS - existing)

    total = sum(remaining_per_combo.values())
    if total == 0:
        print(f"Nothing to do: every combo already has >= {REPEATS} trials.")
        return

    start = time.time()
    done = 0

    for num_catchers, alpha in combos:
        remaining = remaining_per_combo[(num_catchers, alpha)]

        for rep in range(remaining):
            done += 1
            elapsed = time.time() - start
            print(
                f"[{done}/{total}] C={num_catchers} R={NUM_RUNNERS} "
                f"alpha={alpha} rep={rep + 1}/{remaining} (elapsed {elapsed:.0f}s)"
            )
            run_trial(num_catchers, alpha)

    print(f"Done in {time.time() - start:.0f}s. Results appended to {RESULTS_CSV}")


if __name__ == "__main__":
    main()
