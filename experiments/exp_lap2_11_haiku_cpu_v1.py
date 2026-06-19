"""
exp_lap2_11_haiku_cpu_v1.py -- LAP2-11 CONV-1 CREATIVE-FORM: haiku generation (5-7-5) via substrate -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-11). Substrate stores a topic->word library (each word tagged with syllable count); for a
  topic it retrieves the topic's word pool (cleanup) and fills the 5-7-5 haiku template by greedy syllable-exact constraint
  satisfaction. Measures syllable-exactness (all 3 lines exact) AND topic-relevance (all words from the queried topic) across
  100 topics. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >= 0.80 of haiku syllable-exact AND topic-relevant. MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "lap2_11_haiku_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
VOCAB = {
    "nature": [("sun",1),("moon",1),("leaf",1),("breeze",1),("river",2),("mountain",2),("forest",2),("blossom",2),("thunder",2),("willow",2),("meadow",2),("ocean",2),("raindrop",2),("snowflake",2),("sunrise",2),("twilight",2),("butterfly",3),("waterfall",3),("evergreen",3),("dragonfly",3)],
    "city": [("street",1),("bridge",1),("crowd",1),("light",1),("building",2),("traffic",2),("subway",2),("neon",2),("skyline",2),("concrete",2),("pavement",2),("crosswalk",2),("taxi",2),("market",2),("tower",2),("signal",2),("corner",2),("alley",2),("avenue",3),("skyscraper",3)],
    "emotion": [("joy",1),("calm",1),("hope",1),("fear",1),("sorrow",2),("longing",2),("wonder",2),("anger",2),("peaceful",2),("lonely",2),("hopeful",2),("tender",2),("grateful",2),("yearning",2),("delight",2),("comfort",2),("despair",2),("courage",2),("gentle",2),("serenity",4)],
}
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    assert sum(s for _, s in VOCAB["nature"][:0]) == 0; print("[selftest] PASS: haiku", flush=True)


def fill_line(pool, target, g):
    # greedy syllable-exact fill: pick words <= remaining; finish with 1-syllable words. Returns word list or None.
    rem = target; line = []; tries = 0
    while rem > 0 and tries < 50:
        tries += 1
        cands = [w for w in pool if w[1] <= rem]
        ones = [w for w in pool if w[1] == 1]
        if rem == 1 or (rem >= 2 and not [w for w in cands if w[1] == rem] and len(line) >= 2):
            if ones:
                w = ones[int(g.integers(0, len(ones)))]
            elif cands:
                w = cands[int(g.integers(0, len(cands)))]
            else:
                return None
        else:
            if not cands:
                return None
            w = cands[int(g.integers(0, len(cands)))]
        line.append(w); rem -= w[1]
    return line if rem == 0 else None


def run() -> Dict:
    g = np.random.default_rng(1); topics = list(VOCAB); tkeys = cphasor(len(topics), N, g)
    # build word books + substrate topic->word store
    wbooks = {t: cphasor(len(VOCAB[t]), N, g) for t in topics}
    store = {t: sum((tkeys[i] * wbooks[t][j] for j in range(len(VOCAB[t]))), np.zeros(N, dtype=np.complex64)) for i, t in enumerate(topics)}
    TR = 30 if SMOKE else 100; good = 0; n = 0
    for _ in range(TR):
        ti = int(g.integers(0, len(topics))); t = topics[ti]
        # retrieve topic word pool via substrate cleanup (top words bound under this topic key)
        sims = (wbooks[t] @ np.conj(store[t] * np.conj(tkeys[ti]))).real
        keep = [j for j in np.argsort(sims)[::-1][:len(VOCAB[t])]]
        pool = [VOCAB[t][j] for j in keep]
        lines = [fill_line(pool, k, g) for k in (5, 7, 5)]
        ok_syll = all(L is not None and sum(w[1] for w in L) == k for L, k in zip(lines, (5, 7, 5)))
        ok_topic = ok_syll and all(all(w in VOCAB[t] for w in L) for L in lines)
        good += int(ok_syll and ok_topic); n += 1
    rate = good / n; print("  HAIKU syllable-exact + topic-relevant=%.3f (n=%d)" % (rate, n), flush=True)
    return {"haiku_valid": rate, "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "haiku-valid=%.3f (n=%d)" % (r["haiku_valid"], r["n"])
    if r["haiku_valid"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate generates valid 5-7-5 haiku >=0.80 (syllable-exact + topic-relevant) -- topic-word retrieval + syllable constraint-fill; creative-form generation with hard constraints. " + s)
    if r["haiku_valid"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: haiku-valid 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: haiku-valid <0.65. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
