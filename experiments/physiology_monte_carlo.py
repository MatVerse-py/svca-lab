"""Paired Monte Carlo synthetic stress test. Results are not external validation."""
import argparse
import json
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from physiology.core import Colony, Perturbation, evolve


def run(seed, governed, ticks):
    """Independent stochastic scenarios, but IDENTICAL signals between arms."""
    rng = random.Random(seed)
    colony = Colony.genesis(seed)
    first = 8 + (seed % 11)
    second = 49 + ((seed * 7) % 13)
    for t in range(ticks):
        during_shock = (first <= t < first + 14) or (second <= t < second + 15)
        shock = (.88 + .12 * rng.random()) if during_shock else (.02 + .28 * rng.random())
        demand = (1.7 + 1.8*rng.random()) if during_shock else (.4 + 1.35*rng.random())
        supply = 1.0 + .8*rng.random()
        signal = Perturbation(demand=demand, shock=shock, supply=supply,
                              heterogeneity=(.85+.15*rng.random()) if during_shock else .25,
                              coupling=(.02+.17*rng.random()) if during_shock else .80)
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
