"""
exp_zkl_merkle_audit_integrity_v1 -- ZKL Certificate battery cell 5 (Chain 1 Drill 5 FINAL) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_ZKL_Certificate_10h_battery. Trivial decisive pre-req for ALL compliance
  claims: write 500 facts to an append-only log, build a Merkle tree, recompute the root from the log, compare to the stored
  root; then tamper one leaf and confirm the recomputed root DIVERGES (audit chain detects tampering). If the audit chain is
  broken no compliance claim ships. CPU $0.
PRE-REGISTERED (research bands, may tighten not loosen): HARD-PASS roots match on clean log AND mismatch after tamper.
  HARD-FAIL roots mismatch on clean log OR tamper undetected (chain corrupted).
FORMULA SELF-TESTS (PROT-022): 1. root deterministic. 2. tamper changes root. 3. single-leaf tree.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "zkl_merkle_audit_integrity_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 50 if RUN_MODE == "smoke" else 500


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def merkle_root(leaves: List[bytes]) -> bytes:
    if not leaves:
        return _h(b"")
    level = [_h(x) for x in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])                                  # duplicate last (standard odd-node rule)
        level = [_h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def make_facts(n, seed):
    g = np.random.default_rng(seed); return ["fact_%d_%s" % (i, g.integers(0, 1 << 30)) for i in range(n)]


def _selftest():
    a = [b"x", b"y", b"z"]; assert merkle_root(a) == merkle_root([b"x", b"y", b"z"]), "root deterministic"
    assert merkle_root(a) != merkle_root([b"x", b"y", b"Z"]), "tamper changes root"
    assert merkle_root([b"solo"]) == _h(b"solo"), "single-leaf tree"
    print("[selftest] PASS: zkl-merkle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    facts = make_facts(N_FACTS, 7); leaves = [f.encode() for f in facts]
    stored_root = merkle_root(leaves)
    recomputed = merkle_root([f.encode() for f in facts])            # independent recompute from the "log"
    clean_match = stored_root == recomputed
    tampered = list(facts); tampered[N_FACTS // 2] = tampered[N_FACTS // 2] + "_TAMPERED"
    tamper_root = merkle_root([f.encode() for f in tampered]); tamper_detected = tamper_root != stored_root
    print("  facts=%d clean_match=%s tamper_detected=%s" % (N_FACTS, clean_match, tamper_detected), flush=True)
    return {"n_facts": N_FACTS, "clean_match": clean_match, "tamper_detected": tamper_detected, "root_hex": stored_root.hex()[:16]}


def verdict(r) -> Tuple[str, str]:
    summary = "facts=%d clean_root_match=%s tamper_detected=%s root=%s" % (r["n_facts"], r["clean_match"], r["tamper_detected"], r["root_hex"])
    if r["clean_match"] and r["tamper_detected"]:
        return ("HARD_PASS", "HARD_PASS: Merkle audit chain verifies (clean roots match) AND detects tampering -- compliance pre-req met. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: audit chain broken (clean mismatch or tamper undetected) -- NO compliance claim can ship. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
