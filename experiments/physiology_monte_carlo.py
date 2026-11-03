"""Paired Monte Carlo synthetic stress test. Results are not external validation."""
import argparse
import json
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from physiology.core import Colony, Perturbation, evolve


def run(seed, governed, ticks):
    colony = Colony.genesis(seed)
    for t in range(ticks):
        shock = .97 if t % 55 in range(14, 38) else (.05 if t % 2 else .18)
        demand = 2.3 if shock > .5 else .65
        signal = Perturbation(demand=demand, shock=shock, supply=1.5,
                              heterogeneity=.93 if shock > .5 else .2,
                              coupling=.08 if shock > .5 else .78)
        colony = evolve(colony, signal, governed=governed)
    return {"work": colony.work, "fissions": colony.fissions,
            "nodes": len(colony.nodes), "backlog": sum(n.backlog for n in colony.nodes.values()),
            "energy": sum(n.energy for n in colony.nodes.values()),
            "risk": max(n.cvar or 0 for n in colony.nodes.values())}


def bootstrap_mean_ci(values, seed=42, replicates=1000):
    rng = random.Random(seed)
    n = len(values)
    means = [sum(values[rng.randrange(n)] for _ in range(n))/n
             for _ in range(replicates)]
    means.sort()
    return [means[int(.025*replicates)], means[int(.975*replicates)-1]]


def experiment(runs=200, ticks=120):
    if runs < 2 or ticks < 10:
        raise ValueError("runs >= 2 and ticks >= 10 required")
    paired = []
    for seed in range(runs):
        a = run(seed, True, ticks)
        b = run(seed, False, ticks)
        paired.append({"seed": seed, "governed": a, "baseline": b})
    metric = {}
    for key in ("work", "backlog", "energy", "fissions", "risk"):
        differences = [x["governed"][key]-x["baseline"][key] for x in paired]
        metric[key] = {"mean_paired_difference": sum(differences)/runs,
                       "bootstrap_CI_95": bootstrap_mean_ci(differences)}
    return {"status": "SYNTHETIC_LOCAL", "runs": runs, "ticks": ticks,
            "control": "same seeds, shocks, demand and supply",
            "comparison": metric, "no_claim": "not a real-world effect or autonomous income"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=200)
    parser.add_argument("--ticks", type=int, default=120)
    args = parser.parse_args()
    print(json.dumps(experiment(args.runs, args.ticks), indent=2))
