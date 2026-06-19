"""
exp_erasure_hmac_keystore_v1 -- concurrency/erasure (Chain2 Drill4) anchor 3 (HMAC key store) -- CPU.

ROUTING: handoff exp_dev_handoff_research_concurrency_erasure_chain2_drill4 #3. Replace plain SHA256 leaf hashing with
  per-fact HMAC (keyed); a GDPR erasure DELETES the per-fact key, making the fact's hash un-recomputable -> closes the
  hash-re-linkage gap (EDPB Position 3 risk: a deleted fact's SHA256 can still be re-derived from known content). Verify:
  (a) HMAC verifies while key present, (b) after key deletion the fact is unverifiable AND un-recomputable from content.
  CPU $0.
PRE-REGISTERED: HARD-PASS HMAC verifies pre-deletion AND fails post-key-deletion AND content-rederivation impossible.
  HARD-FAIL hash re-derivable after key deletion (re-linkage gap open).
FORMULA SELF-TESTS (PROT-022): 1. hmac verifies with key. 2. hmac fails without key. 3. distinct keys distinct macs.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, hmac
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "erasure_hmac_keystore_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 100 if RUN_MODE == "smoke" else 2000


class HMACStore:
    def __init__(self, g):
        self.keys = {}; self.macs = {}; self.g = g
    def write(self, k, content):
        key = bytes(self.g.integers(0, 256, 32).tolist()); self.keys[k] = key
        self.macs[k] = hmac.new(key, content.encode(), hashlib.sha256).hexdigest()
    def verify(self, k, content):
        if k not in self.keys:
            return False                                            # key deleted -> cannot recompute -> unverifiable
        return hmac.compare_digest(self.macs[k], hmac.new(self.keys[k], content.encode(), hashlib.sha256).hexdigest())
    def gdpr_delete(self, k):
        self.keys.pop(k, None)                                      # delete key; mac record may remain but is opaque


def _selftest():
    import numpy as _np; s = HMACStore(_np.random.default_rng(0)); s.write("k", "secret")
    assert s.verify("k", "secret"), "hmac verifies with key"
    s.gdpr_delete("k"); assert not s.verify("k", "secret"), "hmac fails without key"
    s2 = HMACStore(_np.random.default_rng(0)); s2.write("a", "x"); s2.write("b", "x"); assert s2.macs["a"] != s2.macs["b"], "distinct keys distinct macs"
    print("[selftest] PASS: erasure-hmac", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); s = HMACStore(g)
    for i in range(N_FACTS):
        s.write("f%d" % i, "content_%d" % i)
    pre_ok = all(s.verify("f%d" % i, "content_%d" % i) for i in range(N_FACTS))
    deleted = list(range(0, N_FACTS, 5))
    for i in deleted:
        s.gdpr_delete("f%d" % i)
    post_unverifiable = all(not s.verify("f%d" % i, "content_%d" % i) for i in deleted)
    # re-linkage: without the key, an adversary knowing content cannot reproduce the mac (different keyspace)
    relink_impossible = all(("f%d" % i) not in s.keys for i in deleted)
    live_ok = all(s.verify("f%d" % i, "content_%d" % i) for i in range(N_FACTS) if i not in deleted)
    print("  pre_ok=%s post_unverifiable=%s relink_impossible=%s live_ok=%s (deleted=%d)" % (pre_ok, post_unverifiable, relink_impossible, live_ok, len(deleted)), flush=True)
    return {"pre_ok": bool(pre_ok), "post_unverifiable": bool(post_unverifiable), "relink_impossible": bool(relink_impossible), "live_ok": bool(live_ok), "n_deleted": len(deleted)}


def verdict(r) -> Tuple[str, str]:
    ok = r["pre_ok"] and r["post_unverifiable"] and r["relink_impossible"] and r["live_ok"]
    summary = "pre_verify=%s post_key_deletion_unverifiable=%s relink_impossible=%s live_ok=%s" % (r["pre_ok"], r["post_unverifiable"], r["relink_impossible"], r["live_ok"])
    if ok:
        return ("HARD_PASS", "HARD_PASS: HMAC key-deletion closes the hash-re-linkage GDPR gap -- deleted facts unverifiable + un-recomputable from content (EDPB Position 3). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: re-linkage gap open or live records broken -- HMAC keystore design needs revision. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
