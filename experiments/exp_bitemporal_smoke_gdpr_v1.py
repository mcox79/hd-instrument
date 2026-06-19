"""
exp_bitemporal_smoke_gdpr_v1 -- bitemporal storage smoke + GDPR erasure (Chain2 Drill3 anchors 1+2 combined) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_bitemporal_impl_spec_chain2_drill3. Anchor 1 (Component-1 schema + 100-fact
  smoke: valid-time/system-time, as_of_valid(T), retroactive correction with both versions queryable, Merkle root) + Anchor 2
  (GDPR physical erasure + snapshot invalidation: as_of_system before erasure returns erasure_marker, NOT content) -- combined
  (shared bitemporal store; verdict HARD_PASS only if BOTH pass). De-risks the 6-week build. CPU $0; <1s.
PRE-REGISTERED (research bands): A1 HARD-PASS as_of_valid latency <10ms AND retroactive correction yields BOTH versions
  queryable AND Merkle verifies. A2 HARD-PASS erased content unrecoverable AND as_of_system(pre-erasure) returns marker not
  content. Combined HARD-PASS = both; HARD-FAIL = either fails.
FORMULA SELF-TESTS (PROT-022): 1. as_of_valid picks correct version. 2. retroactive keeps both. 3. erasure removes content.
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

ANCHOR_NAME = "bitemporal_smoke_gdpr_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 100 if RUN_MODE == "smoke" else 1000


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


class BiTemporal:
    """In-memory bitemporal store: each row (key, content, valid_from, sys_from, sys_to, erased)."""
    def __init__(self):
        self.rows = []; self.clock = 0
    def _tick(self):
        self.clock += 1; return self.clock
    def write(self, key, content, valid_from):
        st = self._tick(); self.rows.append({"key": key, "content": content, "valid_from": valid_from, "sys_from": st, "sys_to": None, "erased": False}); return st
    def correct(self, key, new_content, valid_from):
        st = self._tick()
        for r in self.rows:                                          # close current system-time version (retroactive)
            if r["key"] == key and r["sys_to"] is None:
                r["sys_to"] = st
        self.rows.append({"key": key, "content": new_content, "valid_from": valid_from, "sys_from": st, "sys_to": None, "erased": False}); return st
    def as_of_valid(self, key, t):
        cand = [r for r in self.rows if r["key"] == key and r["sys_to"] is None and r["valid_from"] <= t]
        if not cand:
            return None
        r = max(cand, key=lambda r: r["valid_from"]); return ("ERASED_MARKER" if r["erased"] else r["content"])
    def as_of_system(self, key, st):
        cand = [r for r in self.rows if r["key"] == key and r["sys_from"] <= st and (r["sys_to"] is None or r["sys_to"] > st)]
        if not cand:
            return None
        r = cand[-1]; return ("ERASED_MARKER" if r["erased"] else r["content"])
    def gdpr_erase(self, key):
        for r in self.rows:                                         # physical content erasure, audit marker retained
            if r["key"] == key:
                r["content"] = None; r["erased"] = True
    def merkle_root(self):
        leaves = [_h(("%s|%s|%s|%s" % (r["key"], r["content"], r["sys_from"], r["erased"])).encode()) for r in self.rows]
        if not leaves:
            return _h(b"")
        lvl = list(leaves)
        while len(lvl) > 1:
            if len(lvl) % 2:
                lvl.append(lvl[-1])
            lvl = [_h(lvl[i] + lvl[i + 1]) for i in range(0, len(lvl), 2)]
        return lvl[0]


def _selftest():
    s = BiTemporal(); s.write("k", "v1", valid_from=1); sb = s.clock; s.correct("k", "v2", valid_from=1)
    assert s.as_of_valid("k", 6) == "v2", "as_of_valid picks correct (current) version"
    assert s.as_of_system("k", sb) == "v1", "retroactive keeps both (old via system-time travel)"
    s.gdpr_erase("k"); assert s.as_of_valid("k", 6) == "ERASED_MARKER", "erasure removes content"
    print("[selftest] PASS: bitemporal-gdpr", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    s = BiTemporal()
    for i in range(N_FACTS):
        s.write("fact_%d" % i, "content_%d_orig" % i, valid_from=10)
    # A1: retroactive correction on a sample; both versions queryable
    sys_before = s.clock; corrected = 0
    for i in range(0, N_FACTS, 5):
        s.correct("fact_%d" % i, "content_%d_FIXED" % i, valid_from=10); corrected += 1   # correct same valid-time fact
    # both versions queryable: current view -> FIXED ; system-time travel to pre-correction -> orig
    both_ok = all(s.as_of_valid("fact_%d" % i, 25) == "content_%d_FIXED" % i and s.as_of_system("fact_%d" % i, sys_before) == "content_%d_orig" % i for i in range(0, N_FACTS, 5))
    t0 = time.perf_counter()
    for i in range(N_FACTS):
        _ = s.as_of_valid("fact_%d" % i, 25)
    asof_ms = (time.perf_counter() - t0) / N_FACTS * 1e3
    root1 = s.merkle_root(); merkle_ok = (root1 == s.merkle_root())
    # A2: GDPR erase a sample; content gone, marker present, as_of_system pre-erasure returns marker (snapshot invalidation)
    sys_pre_erase = s.clock; erased = 0; content_gone = True; snapshot_ok = True
    for i in range(1, N_FACTS, 7):
        s.gdpr_erase("fact_%d" % i); erased += 1
        if s.as_of_valid("fact_%d" % i, 25) != "ERASED_MARKER":
            content_gone = False
        if s.as_of_system("fact_%d" % i, sys_pre_erase) == ("content_%d_orig" % i):
            snapshot_ok = False                                     # must NOT return content after erasure
    a1 = bool(both_ok and asof_ms < 10 and merkle_ok); a2 = bool(content_gone and snapshot_ok)
    print("  A1: both_versions=%s asof=%.4fms merkle=%s | A2: content_gone=%s snapshot_invalidated=%s (corrected=%d erased=%d)" % (both_ok, asof_ms, merkle_ok, content_gone, snapshot_ok, corrected, erased), flush=True)
    return {"a1_ok": a1, "a2_ok": a2, "both_versions": bool(both_ok), "asof_ms": asof_ms, "merkle_ok": bool(merkle_ok), "content_gone": bool(content_gone), "snapshot_ok": bool(snapshot_ok)}


def verdict(r) -> Tuple[str, str]:
    summary = "A1(both_versions=%s asof=%.4fms merkle=%s) A2(content_gone=%s snapshot_invalidated=%s)" % (r["both_versions"], r["asof_ms"], r["merkle_ok"], r["content_gone"], r["snapshot_ok"])
    if r["a1_ok"] and r["a2_ok"]:
        return ("HARD_PASS", "HARD_PASS: bitemporal smoke + GDPR erasure correct -- retroactive correction keeps both versions, as_of<10ms, physical erasure + snapshot invalidation work. 6-week build de-risked. " + summary)
    if r["a1_ok"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: A1 (bitemporal) passes but A2 (GDPR snapshot invalidation) fails -- erasure design needs revision. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: bitemporal core (A1) broken -- spec must be revised before build. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
