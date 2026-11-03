"""Unit tests for observable properties, not 'digital life' claims."""
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

from physiology.core import (Colony, Node, Perturbation, LAW, LAW_HASH,
                             authorize, evolve, expected_shortfall)
from physiology.store import PhysiologyStore


class TestPhysiology(unittest.TestCase):
    def test_cvar_unknown_is_not_zero(self):
        self.assertIsNone(expected_shortfall([.2, .3], minimum=10))

    def test_cvar_ties_and_fractional_tail(self):
        # The worst 15% of 10 points = 1 point plus half next point.
        self.assertAlmostEqual(expected_shortfall([1,.7]+[.1]*8, .85, 10),
                               (1+.5*.7)/1.5)
        self.assertAlmostEqual(expected_shortfall([.2]*10, .9, 10), .2)

    def test_gate_cannot_approve_work_in_risk(self):
        n = Node("t", cvar=.9)
        self.assertFalse(authorize("WORK", n))
        self.assertTrue(authorize("RECOVER", n))
        self.assertFalse(authorize("UNKNOWN", n))

    def test_perturbation_validation(self):
        for signal in [Perturbation(shock=math.nan),
                       Perturbation(coupling=2),
                       Perturbation(supply=-1)]:
            with self.assertRaises(ValueError):
                signal.validate()

    def test_autonomous_tick_without_user_input(self):
        original = Colony.genesis(7)
        one = evolve(original, Perturbation())
        two = evolve(one, Perturbation())
        self.assertEqual(original.tick, 0)
        self.assertEqual(two.tick, 2)
        self.assertNotEqual(one.nodes["omega-0"].bpm, two.nodes["omega-0"].bpm)

    def test_deterministic_reproduction(self):
        a, b = Colony.genesis(51), Colony.genesis(51)
        for t in range(35):
            sig = Perturbation(demand=1.3, shock=(1. if t>8 else .1),
                               supply=1.8, heterogeneity=.91, coupling=.1)
            a = evolve(a, sig)
            b = evolve(b, sig)
        self.assertEqual(a.pack(), b.pack())

    def test_no_spontaneous_fission_while_coupled(self):
        c = Colony.genesis()
        for _ in range(30):
            c = evolve(c, Perturbation(demand=2, shock=1, supply=2,
                                       heterogeneity=1, coupling=.9))
        self.assertEqual(c.fissions, 0)
        self.assertEqual(len(c.nodes), 1)

    def test_fission_under_joint_criteria_and_cap(self):
        c = Colony.genesis()
        for _ in range(80):
            c = evolve(c, Perturbation(demand=2, shock=1, supply=2,
                                       heterogeneity=1, coupling=.05))
        self.assertGreaterEqual(c.fissions, 1)
        self.assertLessEqual(len(c.nodes), LAW.max_nodes)
        self.assertTrue(any(n.parent == "omega-0" for n in c.nodes.values()))
        self.assertTrue(all(n.energy >= 0 for n in c.nodes.values()))
        self.assertEqual(len(set(c.nodes)), len(c.nodes))

    def test_recovery_from_high_risk(self):
        c = Colony.genesis()
        for _ in range(16):
            c = evolve(c, Perturbation(shock=1.0, demand=.6, supply=2))
        n = c.nodes["omega-0"]
        self.assertGreater(n.cvar, LAW.cvar_limit)
        self.assertEqual(n.action, "RECOVER")

    def test_multi_node_shared_resource_budget(self):
        c = Colony.genesis(91)
        c.nodes["omega-1"] = Node("omega-1", energy=50)
        start = sum(n.energy for n in c.nodes.values())
        nxt = evolve(c, Perturbation(demand=.5, supply=2.0))
        end = sum(n.energy for n in nxt.nodes.values())
        # No duplicated 'supply=2' for each node.
        self.assertLessEqual(end, start + 2.0)
        self.assertGreaterEqual(nxt.work, 0)

    def test_sqlite_persistence_replay_and_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "lab.sqlite3"
            store = PhysiologyStore(path, seed=10)
            for _ in range(15):
                store.tick(Perturbation(shock=.9, demand=1.5, supply=2,
                                        heterogeneity=.9, coupling=.1))
            self.assertEqual(store.replay()["status"], "PASS_LOCAL")
            store.close()
            new_store = PhysiologyStore(path, seed=999)  # existing seed remains
            self.assertEqual(new_store.state().tick, 15)
            self.assertEqual(new_store.replay()["status"], "PASS_LOCAL")
            new_store.conn.execute("UPDATE events SET state_hash='bad' WHERE seq=2")
            new_store.conn.commit()
            self.assertEqual(new_store.replay()["status"], "BLOCK")
            new_store.close()


if __name__ == "__main__":
    unittest.main()
