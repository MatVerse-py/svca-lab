"""Atomic SQLite state + hash-linked events + independent recomputation.

This is LOCAL tamper evidence; not a signature or immutable on-chain anchor.
"""
import json
import sqlite3
from pathlib import Path
from .core import Colony, Perturbation, LAW_HASH, canonical, digest, evolve


class PhysiologyStore:
    def __init__(self, path, seed=510859281488):
        self.conn = sqlite3.connect(str(Path(path)), timeout=20)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS config(k TEXT PRIMARY KEY,v TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
            seq INTEGER PRIMARY KEY,input_json TEXT NOT NULL,
            state_hash TEXT NOT NULL,prev TEXT NOT NULL,hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS snapshot(
            id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
        """)
        if self.conn.execute("SELECT 1 FROM config WHERE k='seed'").fetchone() is None:
            with self.conn:
                self.conn.execute("INSERT INTO config VALUES('seed',?)", (str(seed),))
                self.conn.execute("INSERT INTO config VALUES('law_hash',?)", (LAW_HASH,))
                self.conn.execute("INSERT INTO snapshot VALUES(1,?)",
                                  (canonical(Colony.genesis(seed).pack()),))
        self.check_law()

    def check_law(self):
        cfg = dict(self.conn.execute("SELECT k,v FROM config"))
        if cfg["law_hash"] != LAW_HASH:
            raise RuntimeError("CONSTITUTION_MISMATCH: fail-closed")

    def state(self):
        return Colony.unpack(json.loads(
            self.conn.execute("SELECT value FROM snapshot WHERE id=1").fetchone()[0]))

    def tick(self, signal=None, governed=True):
        signal = signal or Perturbation()
        signal.validate()
        with self.conn:
            current = self.state()
            updated = evolve(current, signal, governed)
            prior = self.conn.execute(
                "SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            prev_hash = prior[0] if prior else "GENESIS:"+LAW_HASH
            inp = canonical({"signal": signal.__dict__, "governed": governed})
            state_hash = digest(updated.pack())
            h = digest({"seq": updated.tick, "input": inp,
                        "state_hash": state_hash, "prev": prev_hash})
            self.conn.execute("INSERT INTO events VALUES(?,?,?,?,?)",
                              (updated.tick, inp, state_hash, prev_hash, h))
            self.conn.execute("UPDATE snapshot SET value=? WHERE id=1",
                              (canonical(updated.pack()),))
        return updated

    def replay(self):
        self.check_law()
        seed = int(dict(self.conn.execute("SELECT k,v FROM config"))["seed"])
        reconstructed = Colony.genesis(seed)
        prev = "GENESIS:"+LAW_HASH
        count = 0
        for seq, inp, state_hash, prev_hash, event_hash in self.conn.execute(
                "SELECT seq,input_json,state_hash,prev,hash FROM events ORDER BY seq"):
            if seq != count+1 or prev_hash != prev:
                return {"status": "BLOCK", "reason": "CHAIN_ORDER", "seq": seq}
            computed = digest({"seq": seq, "input": inp,
                               "state_hash": state_hash, "prev": prev_hash})
            if computed != event_hash:
                return {"status": "BLOCK", "reason": "CHAIN_HASH", "seq": seq}
            try:
                data = json.loads(inp)
                reconstructed = evolve(reconstructed,
                                       Perturbation(**data["signal"]),
                                       data["governed"])
            except (KeyError, TypeError, ValueError) as exc:
                return {"status": "BLOCK", "reason": str(exc), "seq": seq}
            if digest(reconstructed.pack()) != state_hash:
                return {"status": "BLOCK", "reason": "REPLAY_DIVERGENCE", "seq": seq}
            prev = event_hash
            count += 1
        if digest(reconstructed.pack()) != digest(self.state().pack()):
            return {"status": "BLOCK", "reason": "SNAPSHOT_DIVERGENCE"}
        return {"status": "PASS_LOCAL", "events": count,
                "law_hash": LAW_HASH, "head": prev}

    def close(self):
        self.conn.close()
