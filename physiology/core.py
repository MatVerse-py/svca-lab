"""MatVerse OCG v0.1: deterministic, SYNTHETIC physiology experiment.

Not life, AGI, financial CVaR, a secure enclave or an attested runtime.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from math import isfinite
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def clamp(value, low=0.0, high=1.0):
    return min(high, max(low, value))


@dataclass(frozen=True)
class Constitution:
    schema: str = "matverse.physiology.v0.1"
    alpha: float = 0.90
    min_samples: int = 10
    cvar_limit: float = 0.65
    min_energy: float = 12.0
    fission_energy: float = 55.0
    fission_cost: float = 6.0
    fission_persistence: int = 3
    heterogeneity_min: float = 0.72
    coupling_max: float = 0.25
    max_nodes: int = 4


LAW = Constitution()
LAW_HASH = digest(asdict(LAW))


def expected_shortfall(losses, alpha=0.9, minimum=10):
    """Empirical upper-tail CVaR using FRACTIONAL order statistic.

    Unlike mean(loss >= VaR), this treats ties and fractional tails correctly.
    Insufficient data -> None (unknown), never zero risk.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0,1)")
    if len(losses) < minimum:
        return None
    if any(not isfinite(float(x)) or not 0 <= x <= 1 for x in losses):
        raise ValueError("losses must be normalized and finite")
    xs = sorted(losses, reverse=True)
    tail_mass = (1-alpha)*len(xs)
    whole = int(tail_mass)
    fractional = tail_mass-whole
    return (sum(xs[:whole]) + (fractional*xs[whole] if fractional > 1e-10 else 0)) / tail_mass


@dataclass(frozen=True)
class Perturbation:
    demand: float = 0.6
    shock: float = 0.0
    supply: float = 1.25
    heterogeneity: float = 0.3
    coupling: float = 0.75

    def validate(self):
        for key, val in asdict(self).items():
            if not isfinite(val):
                raise ValueError("non-finite " + key)
        if not 0 <= self.demand <= 4:
            raise ValueError("invalid demand")
        if not 0 <= self.shock <= 1 or not 0 <= self.heterogeneity <= 1:
            raise ValueError("invalid shock or heterogeneity")
        if not 0 <= self.coupling <= 1 or not 0 <= self.supply <= 4:
            raise ValueError("invalid coupling or supply")


@dataclass
class Node:
    id: str
    parent: str | None = None
    energy: float = 80.0
    backlog: float = 0.0
    coherence: float = 0.88
    losses: list[float] = field(default_factory=list)
    cvar: float | None = None
    stress: int = 0
    bpm: float = 60.0
    age: int = 0
    action: str = "OBSERVE"


@dataclass
class Colony:
    seed: int
    tick: int = 0
    nodes: dict[str, Node] = field(default_factory=dict)
    work: int = 0
    rejected: int = 0
    fissions: int = 0
    events: list[dict] = field(default_factory=list)

    @classmethod
    def genesis(cls, seed=510859281488):
        return cls(seed=seed, nodes={"omega-0": Node("omega-0")})

    def pack(self):
        return asdict(self)

    @classmethod
    def unpack(cls, data):
        return cls(seed=data["seed"], tick=data["tick"],
                   nodes={k: Node(**v) for k,v in data["nodes"].items()},
                   work=data["work"], rejected=data["rejected"],
                   fissions=data["fissions"], events=list(data.get("events", [])))


def internal_fluctuation(seed, tick, node_id):
    """Endogenous perturbation independent of any prompt / UI / network."""
    bits = sha256(f"{seed}|{tick}|{node_id}".encode()).digest()
    return 0.06 * (int.from_bytes(bits[:8], "big") / (2**64-1) - 0.5)


def propose(node):
    """Physiological response candidate: NO authority over effects."""
    if node.energy < LAW.min_energy or (node.cvar is not None and node.cvar > LAW.cvar_limit):
        return "RECOVER"
    if node.backlog > 1:
        return "THROTTLE"
    return "WORK"


def authorize(action, node):
    """Separate fail-closed constitutional check."""
    if action not in {"WORK", "THROTTLE", "RECOVER"}:
        return False
    if action == "WORK" and (node.energy < LAW.min_energy or
                            (node.cvar is not None and node.cvar > LAW.cvar_limit)):
        return False
    return True


def evolve(original, input_signal, governed=True):
    """One logical tick, no wall clock. Never mutates caller's state."""
    input_signal.validate()
    colony = Colony.unpack(original.pack())
    colony.tick += 1
    colony.events = []
    for node_id in sorted(list(colony.nodes)):
        node = colony.nodes[node_id]
        demand = clamp(input_signal.demand +
                       internal_fluctuation(colony.seed, colony.tick, node_id), 0, 4)
        # Loss observable: a documented, synthetic operational cost model.
        loss = clamp(0.70*input_signal.shock +
                     0.20*clamp(node.backlog/3) +
                     0.10*(1-node.coherence))
        node.losses = (node.losses + [round(loss, 8)])[-64:]
        previous = node.cvar
        node.cvar = expected_shortfall(node.losses, LAW.alpha, LAW.min_samples)
        proposed = propose(node) if governed else "WORK"
        authorized = authorize(proposed, node)
        if not authorized:
            colony.rejected += 1
            action = "RECOVER"   # safe LOCAL default, no external side effects
        else:
            action = proposed
        factor = {"WORK": 1.0, "THROTTLE": .38, "RECOVER": .15}[action]
        capacity = {"WORK": 1.15, "THROTTLE": 1.30, "RECOVER": 1.25}[action]
        node.backlog = clamp(node.backlog*.82 + demand*factor-capacity, 0, 10)
        cost = {"WORK": 1.20, "THROTTLE": .82, "RECOVER": .35}[action]
        node.energy = clamp(node.energy + input_signal.supply-cost, 0, 100)
        node.coherence = clamp(node.coherence +
                               (.018 if action == "RECOVER" else .008) -
                               .025*input_signal.shock-.012*node.backlog)
        if action == "WORK" and node.backlog < 3:
            colony.work += 1
        gradient = (abs(node.cvar-previous)
                    if node.cvar is not None and previous is not None
                    else abs(internal_fluctuation(colony.seed, colony.tick, node_id)))
        node.bpm = round(clamp(60+125*gradient, 48, 120), 4)
        node.age += 1
        node.action = action
        high_risk = node.cvar is not None and node.cvar > LAW.cvar_limit
        node.stress = node.stress+1 if high_risk else 0
        colony.events.append({"tick": colony.tick, "node": node_id,
                              "action": action, "gate": "PASS_LOCAL" if authorized else "BLOCK",
                              "loss": round(loss, 8), "cvar": node.cvar})
        if (governed and high_risk and node.stress >= LAW.fission_persistence and
                input_signal.heterogeneity >= LAW.heterogeneity_min and
                input_signal.coupling <= LAW.coupling_max and
                node.energy >= LAW.fission_energy and
                len(colony.nodes) < LAW.max_nodes):
            child_id = "omega-" + sha256(
                f"{colony.seed}:{node_id}:{colony.tick}:{LAW_HASH}".encode()
            ).hexdigest()[:10]
            if child_id not in colony.nodes:
                # Invariant: E_parent_after + E_child = E_parent_before - split_cost
                allocated = (node.energy-LAW.fission_cost)/2
                node.energy = allocated
                colony.nodes[child_id] = Node(child_id, parent=node_id,
                                               energy=allocated,
                                               backlog=node.backlog/2,
                                               coherence=node.coherence,
                                               losses=list(node.losses),
                                               cvar=node.cvar)
                node.backlog /= 2
                node.stress = 0
                colony.fissions += 1
                colony.events.append({"tick": colony.tick, "event": "FISSION_LOCAL",
                                      "parent": node_id, "child": child_id,
                                      "constitution_hash": LAW_HASH})
    return colony
