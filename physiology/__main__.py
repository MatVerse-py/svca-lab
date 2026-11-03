"""Run with: python -m physiology --help"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .core import Colony, Perturbation, LAW_HASH
from .store import PhysiologyStore


def main():
    parser = argparse.ArgumentParser(description="MatVerse local physiology lab (synthetic)")
    parser.add_argument("--db", default="organism.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    tick = sub.add_parser("tick")
    for field, default in [("demand", .6), ("shock", 0.), ("supply", 1.25),
                           ("heterogeneity", .3), ("coupling", .75)]:
        tick.add_argument("--"+field, type=float, default=default)
    demo = sub.add_parser("demo")
    demo.add_argument("--ticks", type=int, default=90)
    sub.add_parser("verify")
    sub.add_parser("state")
    server = sub.add_parser("serve")
    server.add_argument("--port", type=int, default=8844)
    args = parser.parse_args()
    store = PhysiologyStore(args.db)
    if args.command == "init":
        print(json.dumps({"status": "PASS_LOCAL", "db": args.db,
                          "law_hash": LAW_HASH}, indent=2))
    elif args.command == "tick":
        s = store.tick(Perturbation(args.demand, args.shock, args.supply,
                                    args.heterogeneity, args.coupling))
        print(json.dumps(s.pack(), ensure_ascii=False, indent=2))
    elif args.command == "demo":
        if args.ticks <= 0:
            parser.error("--ticks must be positive")
        for idx in range(args.ticks):
            # controlled lab excitation; never real-world environmental measurement
            shock = 1.0 if 12 <= idx % 80 < 38 else 0.04
            signal = Perturbation(demand=1.5 if shock > .5 else .6,
                                  shock=shock, supply=1.7,
                                  heterogeneity=.95 if shock > .5 else .25,
                                  coupling=.05 if shock > .5 else .8)
            state = store.tick(signal)
        print(json.dumps({"ticks": state.tick, "nodes": len(state.nodes),
                          "fissions": state.fissions, "work": state.work,
                          "verification": store.replay()}, indent=2))
    elif args.command == "verify":
        print(json.dumps(store.replay(), indent=2))
    elif args.command == "state":
        print(json.dumps(store.state().pack(), ensure_ascii=False, indent=2))
    elif args.command == "serve":
        # Read-only same-origin projection. Local loopback only by design.
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/state":
                    payload = json.dumps({"mode": "SYNTHETIC_LOCAL", "law_hash": LAW_HASH,
                                          "colony": store.state().pack()},
                                         ensure_ascii=False).encode()
                    mime = "application/json"
                elif self.path in ("/", "/index.html"):
                    payload = (Path(__file__).resolve().parent.parent / "web" /
                               "cube_colony.html").read_bytes()
                    mime = "text/html; charset=utf-8"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        print(f"LOCAL READ-ONLY at http://127.0.0.1:{args.port}")
        HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
    store.close()


if __name__ == "__main__":
    main()
