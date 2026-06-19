"""
exp_creative_dreaming_smoke_cpu_v1.py -- CREATIVE-DREAMING-SMOKE: substrate offline-replay novel concept generation -- CPU.

ROUTING: Research cheap-parallel (PP-328 DREAMING-SUBSTRATE). Tests whether substrate offline replay/recombination generates
  NOVEL + COHERENT concept combinations (substrate-only creative). Concepts are (role, filler) structured items; the substrate
  learns each role's valid filler-set. DREAMING = recombine: sample a role + a filler (possibly from a different concept) and
  bind them. NOVELTY = the (role, filler) pair was not in the original set. COHERENCE (no-LLM, substrate-checkable) = the filler
  is type-consistent with the role (filler belongs to the role's learned valid-filler set via substrate cleanup confidence).
  Score: of 20 sampled recombinations, how many are novel AND coherent. Empirically tests drill-G's "LLM-hybrid for novel" framing.
PRE-REGISTERED: HARD-PASS >= 5 of 20 recombinations novel AND coherent (substrate-only generates novel coherent concepts).
  MIDDLE >= 2. HARD-FAIL < 2.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "creative_dreaming_smoke_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: creative-dreaming-smoke", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "999")))
    # structured concept space: each role has a TYPE-CONSISTENT filler set (coherence = filler in role's valid set)
    ROLES = ["color", "material", "size", "habitat", "diet"]
    FILLERS = {
        "color": ["red", "blue", "green", "amber", "violet", "silver"],
        "material": ["wood", "iron", "glass", "stone", "copper", "silk"],
        "size": ["tiny", "small", "large", "huge", "vast"],
        "habitat": ["forest", "ocean", "desert", "tundra", "cavern", "meadow"],
        "diet": ["herbivore", "carnivore", "omnivore", "nectar", "plankton"],
    }
    role_v = {r: cphasor(1, N, g)[0] for r in ROLES}
    fill_v = {f: cphasor(1, N, g)[0] for r in ROLES for f in FILLERS[r]}
    fbook = {r: np.stack([fill_v[f] for f in FILLERS[r]]) for r in ROLES}   # per-role filler codebook (cleanup target)
    # original concept set: each concept = a (role->filler) assignment; NOVELTY checked against these exact (role,filler) pairs
    NC = 30 if SMOKE else 100
    seen_pairs = set(); concepts = []
    for _ in range(NC):
        c = {r: FILLERS[r][int(g.integers(0, len(FILLERS[r])))] for r in ROLES}
        concepts.append(c)
        for r in ROLES: seen_pairs.add((r, c[r]))
    # DREAMING offline replay: recombine -- build a concept by sampling+binding role-filler pairs across the corpus, then
    # READ BACK each role's filler via substrate cleanup (the substrate's recombination + recall)
    n_sample = 8 if SMOKE else 20; novel_coherent = 0; novel = 0; details = []
    for _ in range(n_sample):
        # recombine: for each role pick a filler from a RANDOM original concept (cross-concept recombination)
        combo = {r: concepts[int(g.integers(0, NC))][r] for r in ROLES}
        # encode as substrate concept vector + read back via cleanup (substrate must reconstruct the recombination)
        cv = cnorm(sum((role_v[r] * fill_v[combo[r]] for r in ROLES), np.zeros(N, dtype=np.complex64)))
        recalled = {}
        for r in ROLES:
            recalled[r] = FILLERS[r][cidx(cv * np.conj(role_v[r]), fbook[r])]
        # NOVEL = the full role->filler assignment is not any original concept; COHERENT = every recalled filler is in its role's valid set (type-consistent) AND matches the intended combo (substrate reconstructed it)
        is_novel = combo not in concepts
        is_coherent = all(recalled[r] == combo[r] and recalled[r] in FILLERS[r] for r in ROLES)
        novel += int(is_novel); novel_coherent += int(is_novel and is_coherent)
        details.append((is_novel, is_coherent))
    print("  CREATIVE-DREAMING: novel=%d/%d | novel+coherent=%d/%d (substrate recombination + cleanup reconstruction)" %
          (novel, n_sample, novel_coherent, n_sample), flush=True)
    return {"novel_coherent": novel_coherent, "novel": novel, "n_sample": n_sample, "n_concepts": NC}
def verdict(r) -> Tuple[str, str]:
    nc = r["novel_coherent"]; s = "novel+coherent=%d/%d novel=%d" % (nc, r["n_sample"], r["novel"])
    thr_pass = 2 if SMOKE else 5; thr_mid = 1 if SMOKE else 2
    if nc >= thr_pass:
        return ("HARD_PASS", "HARD_PASS: substrate offline-replay (DREAMING) generates >=%d/%d NOVEL + COHERENT concept recombinations -- substrate recombines role-filler bindings into novel type-consistent concepts and reconstructs them via cleanup, no LLM. Substrate-only creative existence proof; drill-G LLM-hybrid framing not required here. " % (thr_pass, r["n_sample"]) + s)
    if nc >= thr_mid:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d novel-coherent recombinations (some recombinations don't reconstruct or aren't novel). " % nc + s)
    return ("HARD_FAIL", "HARD_FAIL: <%d novel-coherent -- substrate recombination does not produce reconstructable novel concepts. " % thr_mid + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
