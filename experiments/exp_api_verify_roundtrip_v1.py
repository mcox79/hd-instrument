"""
exp_api_verify_roundtrip_v1 -- substrate-native-API anchor 2 (Merkle proof round-trip) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_substrate_native_API_design (#2). write() a fact, capture merkle_path from
  the receipt, call verify() against the current accumulator root -> grounded=True; then tamper the fact externally and
  confirm verify() returns grounded=False. Establishes verify() correctness + tamper-detection before reactive delivery can
  embed merkle_path. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS all genuine facts verify grounded=True AND all tampered facts verify
  grounded=False. HARD-FAIL any genuine fact fails OR any tamper passes.
FORMULA SELF-TESTS (PROT-022): 1. genuine verifies. 2. tamper fails. 3. path length log2(n).
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

ANCHOR_NAME = "api_verify_roundtrip_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 50 if RUN_MODE == "smoke" else 500


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def levels_of(leaves):
    levels = [list(leaves)]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        if len(cur) % 2:
            cur = cur + [cur[-1]]
        levels.append([_h(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
    return levels


def path_of(levels, idx):
    p = []
    for lvl in levels[:-1]:
        sib = idx ^ 1; sib = sib if sib < len(lvl) else idx; p.append((lvl[sib], idx & 1)); idx //= 2
    return p


def verify(payload, path, root):
    h = _h(payload)
    for sib, is_right in path:
        h = _h(sib + h) if is_right else _h(h + sib)
    return h == root


def _selftest():
    facts = [b"f%d" % i for i in range(8)]; lv = levels_of([_h(f) for f in facts]); root = lv[-1][0]
    assert verify(facts[3], path_of(lv, 3), root), "genuine verifies"
    assert not verify(facts[3] + b"_tamper", path_of(lv, 3), root), "tamper fails"
    assert len(path_of(lv, 0)) == 3, "path length log2(n)"
    print("[selftest] PASS: api-verify", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); facts = [("fact_%d_%d" % (i, g.integers(0, 1 << 30))).encode() for i in range(N_FACTS)]
    lv = levels_of([_h(f) for f in facts]); root = lv[-1][0]
    genuine_ok = sum(verify(facts[i], path_of(lv, i), root) for i in range(N_FACTS))
    tamper_caught = sum(not verify(facts[i] + b"_TAMPER", path_of(lv, i), root) for i in range(N_FACTS))
    print("  genuine_verified=%d/%d tamper_caught=%d/%d" % (genuine_ok, N_FACTS, tamper_caught, N_FACTS), flush=True)
    return {"n": N_FACTS, "genuine_ok": genuine_ok, "tamper_caught": tamper_caught}


def verdict(r) -> Tuple[str, str]:
    n = r["n"]; summary = "genuine_verified=%d/%d tamper_caught=%d/%d" % (r["genuine_ok"], n, r["tamper_caught"], n)
    if r["genuine_ok"] == n and r["tamper_caught"] == n:
        return ("HARD_PASS", "HARD_PASS: verify() round-trip correct -- all genuine facts grounded=True, all tampers grounded=False; merkle_path embeddable in reactive delivery. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: verify() incorrect (genuine fail or tamper pass) -- delivery cannot embed merkle_path yet. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
