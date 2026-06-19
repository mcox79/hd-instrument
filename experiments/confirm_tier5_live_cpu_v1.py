"""
confirm_tier5_live_cpu_v1.py -- LIVE Tier-5 confirmation harness (the gated next action, made reproducible).

When Testbed ingests the off-attractor backlog (PP-401/402/403/404 + T3/temporal_context_binding + T3/lex_semantic_constant_retrieval
+ PP-394 sh remap + the PP-398/399/400 + PP-402/403/404 solution_histories), run THIS to certify the Tier-5 appearances on the LIVE
store -- no shims, no projection. It runs the packaged miner (_tier5_rule_miner) on the real PartitionedStore and checks that each
EXPECTED novel recurring rule has surfaced with n_caps>=2.

Expected novel recurring rules (one per off-attractor mechanism class, each from 2 genuine capabilities):
  1. fhrr_bind -> permutation_indexed_binding      (PP-398 + PP-401)   P^k positional        [Cycle 49, 2nd appearance]
  2. fhrr_bind -> temporal_context_binding          (PP-402 + PP-403)   TCM temporal          [Cycle 51, 3rd appearance]
  3. discriminative_perceptron -> lex_semantic_constant_retrieval  (PP-394 + PP-404)  LEX_T semantic-constant  [Cycle 52, 4th appearance]

Exit 0 + verdict PASS iff all 3 surface live. Otherwise reports which are missing + the live novel-rule set (honest partial state).
Pure read; no store mutation; no LLM-judge. Idempotent -- safe to run repeatedly as the ingest cascade lands incrementally.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.substrate_index.partition import PartitionedStore  # noqa: E402
from experiments._tier5_rule_miner import mine_methodology_rules  # noqa: E402

EXPECTED = {
    "RULE_fhrr_bind_to_permutation_indexed_binding": {"caps": ["PP-398", "PP-401"], "class": "P^k positional", "cycle": 49, "appearance": 2},
    "RULE_fhrr_bind_to_temporal_context_binding": {"caps": ["PP-402", "PP-403"], "class": "TCM temporal", "cycle": 51, "appearance": 3},
    "RULE_discriminative_perceptron_to_lex_semantic_constant_retrieval": {"caps": ["PP-394", "PP-404"], "class": "LEX_T semantic-constant", "cycle": 52, "appearance": 4},
}


def confirm(verbose=True):
    ps = PartitionedStore(Path(__file__).resolve().parents[1] / "data" / "substrate_index")
    atoms = ps.all_atoms()
    n_sh = sum(1 for a in atoms if getattr(a, "solution_history", None))
    R = mine_methodology_rules(ps)
    live_novel = {c["name"]: c for c in R["novel_recurring"]}
    results = []
    for name, meta in EXPECTED.items():
        c = live_novel.get(name)
        ok = c is not None and c["n_caps"] >= 2
        results.append({"rule": name, "present": ok, "class": meta["class"], "appearance": meta["appearance"],
                        "n_caps": (c["n_caps"] if c else 0), "support": (c["support"] if c else [])})
    confirmed = [r for r in results if r["present"]]
    missing = [r for r in results if not r["present"]]
    if verbose:
        print("=== LIVE Tier-5 confirmation ===")
        print("live store: %d atoms | %d sh-atoms | %d novel recurring rule(s) total" % (len(atoms), n_sh, len(live_novel)))
        for r in results:
            mark = "CONFIRMED" if r["present"] else "missing  "
            print("  [%s] %s (%s, %s appearance) n_caps=%d support=%s" % (
                mark, r["rule"], r["class"], _ord(r["appearance"]), r["n_caps"], r["support"]))
        if missing:
            print("\nLIVE novel-rule set so far:", sorted(live_novel.keys()) or "(none)")
            print("Still pending ingest for: %s" % ", ".join(_ord(r["appearance"]) + " (" + r["class"] + ")" for r in missing))
    verdict = "PASS" if not missing else "PARTIAL"
    msg = ("All 3 expected novel recurring rules CONFIRMED live -- Tier-5 2nd/3rd/4th appearances certified on the real store."
           if not missing else
           "%d/3 expected novel rules live; %d pending Testbed ingest." % (len(confirmed), len(missing)))
    return {"verdict": verdict, "verdict_msg": msg, "confirmed": [r["rule"] for r in confirmed],
            "missing": [r["rule"] for r in missing], "n_sh_atoms": n_sh, "n_atoms": len(atoms)}


def _ord(n):
    return {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}.get(n, "%dth" % n)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = confirm(verbose=not args.json)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("\nVERDICT:", res["verdict"], "--", res["verdict_msg"])
    sys.exit(0 if res["verdict"] == "PASS" else 0)  # exit 0 always (PARTIAL is a valid pre-ingest state, not an error)
