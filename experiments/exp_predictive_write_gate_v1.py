"""DOES A RESIDUAL-GATED PROFILE RETRIEVE BETTER THAN AN ACCUMULATED ONE? The pinned equation, wired.

WHY THIS CELL. Three independent measurements this session say the ACCUMULATED-CONTEXT
REPRESENTATION is the ceiling, not the read-out: three read-out variants were built, the cortical
route's unique contribution sits BELOW independence at every k, and 0 of 18 floor cells clear.
`notes/ORGAN_MAP.md` G2 records the brain's rule as PINNED -- the residual `x - x_hat` is the
learning signal, precision-weighted -- and our profiles are built by pure accumulation with NO
error signal anywhere. This is that gap, tested.

*** IT IS A WIRING, NOT A BUILD. *** `hdlab/predictive_coding.py` already implements the equation
(`predict`, `residual`, `residual_magnitude`, `threshold_gate`, `gated_write`,
`vanilla_hebbian_write`), self-tests PASS, and a runtime trace shows it is NOT among the 44
`hdlab.*` modules a real `Substrate.read()` loads. The organ existed and was unwired.

*** AND IT IS NON-INVASIVE BY DESIGN. *** The three arms are three PROFILE-CONSTRUCTION RULES
applied to the SAME traces from the SAME read. Nothing in the substrate's write path changes, so
no arm can perturb the data another arm sees, and the comparison is one variable.

THREE ARMS, and the third is the one that makes this honest:
  ACCUMULATE   sum every trace. THIS IS WHAT THE SUBSTRATE DOES TODAY (the organ's own
               `vanilla_hebbian_write` arm).
  GATED        write a trace only when its residual against the profile-so-far clears `thr`.
  RANDOM_SKIP  skip the SAME FRACTION of traces, chosen at random, per term.

*** WHY RANDOM_SKIP IS MANDATORY AND NOT A NICETY. *** Measured before this cell was written
(`scratch/probe_does_the_residual_gate_ever_skip.py`, 16,211 writes): residual magnitudes are
NEARLY CONSTANT -- p10 0.3575, median 0.4648, p90 0.5237 over a 0.024-0.606 range. If the residual
barely varies, gating on it is close to gating AT RANDOM, and any GATED-vs-ACCUMULATE difference
would be attributable to WRITING LESS rather than to WRITING SELECTIVELY. This project broke a
rate-matched control twice already this session, in opposite directions. Not a third time.

*** THE THRESHOLD IS SWEPT, NEVER ADOPTED. *** Same probe: 2.5% of writes skipped at thr=0.25,
76.2% at 0.50, 100% at 0.75. The usable band is a CLIFF, so a single adopted value would be a
parameter masquerading as a finding. "Copy the computation, sweep the parameter."

PRE-COMMITTED READINGS, written before any number exists:
  (A) GATED beats ACCUMULATE **and** beats RANDOM_SKIP at the same threshold, CI-separated ->
      the residual carries information and predictive coding helps. Name the threshold and the
      skip rate together; a gain at one point of a swept cliff is a lead, not a result.
  (B) GATED beats ACCUMULATE but TIES RANDOM_SKIP -> the gain is from WRITING LESS, not from
      writing selectively. Report it that way and do not call it predictive coding.
  (C) GATED ties or loses to ACCUMULATE at every threshold -> the residual gate does not help.
      A real negative about the pinned equation AS WIRED HERE, and it must be reported as one.
  (D) NO arm clears the strongest floor -> whatever happens between the arms, the representation
      is still not competitive, and BOTH facts get reported. This is the likely outcome: COOC
      reaches median rank 15-20 of ~450 and nothing we own has come near it.

Run:  python experiments/exp_predictive_write_gate_v1.py --mode smoke
      python experiments/exp_predictive_write_gate_v1.py --mode full
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import random
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.corpus_registry import CorpusRegistry
from hdlab.predictive_coding import residual_magnitude
from hdlab.reading_grounding_loop import content_lemmas, context_vector_masked
from hdlab.substrate import CONTEXT_DIM, Substrate

CELL = "exp_predictive_write_gate_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
SPEC = "v1_residual_gate"
CORPUS = "simplewiki"
SEEDS = (20260819, 7, 101)
THRESHOLDS = (0.25, 0.40, 0.45, 0.50, 0.55, 0.60)   # SWEPT. The usable band is a cliff near 0.50.
KS = (1, 10, 50)
N_BOOT = 2000
MIN_ITEMS = 200


def _unit(v) -> Optional[np.ndarray]:
    if v is None:
        return None
    v = np.asarray(v, dtype=np.float64).reshape(-1)
    n = float(np.linalg.norm(v))
    return None if n < 1e-12 else v / n


def _boot_ci(x: np.ndarray, rng: np.random.Generator) -> Tuple[float, float]:
    if x.size == 0:
        return (float("nan"),) * 2
    idx = rng.integers(0, x.size, size=(N_BOOT, x.size))
    m = x[idx].mean(axis=1)
    return tuple(float(v) for v in np.percentile(m, [2.5, 97.5]))


def _build_profiles(traces_by_term: Dict[str, List[np.ndarray]], rule: str,
                    thr: float, seed: int) -> Dict[str, np.ndarray]:
    """One profile per term under one construction rule. ONE VARIABLE.

    ACCUMULATE is exactly what the substrate does today. GATED and RANDOM_SKIP drop traces; the
    random arm drops the SAME NUMBER the gate dropped FOR THAT TERM, so the two differ only in
    WHICH traces were dropped, never in HOW MANY.
    """
    rng = random.Random(seed)
    out: Dict[str, np.ndarray] = {}
    for term, traces in traces_by_term.items():
        if not traces:
            continue
        if rule == "ACCUMULATE":
            acc = np.sum(traces, axis=0)
        elif rule == "GATED":
            acc = np.asarray(traces[0], dtype=np.float64).copy()
            for tr in traces[1:]:
                obs = np.asarray(tr, dtype=np.float64)
                pred = _unit(acc)
                if pred is None or residual_magnitude(obs, pred) >= thr:
                    acc = acc + obs
        else:  # RANDOM_SKIP, rate-matched per term to the gate's own skip count
            kept = [np.asarray(traces[0], dtype=np.float64)]
            acc_g = np.asarray(traces[0], dtype=np.float64).copy()
            n_written = 1
            for tr in traces[1:]:
                obs = np.asarray(tr, dtype=np.float64)
                pred = _unit(acc_g)
                if pred is None or residual_magnitude(obs, pred) >= thr:
                    acc_g = acc_g + obs
                    n_written += 1
            rest = [np.asarray(t, dtype=np.float64) for t in traces[1:]]
            take = max(0, n_written - 1)
            rng.shuffle(rest)
            acc = np.sum(kept + rest[:take], axis=0) if take else kept[0]
        u = _unit(acc)
        if u is not None:
            out[term] = u
    return out


def _rank_table(profiles: Dict[str, np.ndarray], items: List[Tuple[str, str]]) -> List[Optional[int]]:
    names = sorted(profiles)
    if not names:
        return [None] * len(items)
    M = np.stack([profiles[n] for n in names])
    pos = {n: i for i, n in enumerate(names)}
    ranks: List[Optional[int]] = []
    for sent, tgt in items:
        if tgt not in pos:
            ranks.append(None)
            continue
        q = _unit(context_vector_masked(sent, tgt, d=CONTEXT_DIM))
        if q is None or q.shape[0] != M.shape[1]:
            ranks.append(None)
            continue
        sims = M @ q
        ranks.append(int(np.sum(sims > sims[pos[tgt]])) + 1)
    return ranks


def _hits(ranks: List[Optional[int]], k: int) -> np.ndarray:
    return np.asarray([int(r is not None and r <= k) for r in ranks], dtype=np.float64)


def _run(seed: int, n_read: int, n_items: int, chunk: int) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)

    reg = CorpusRegistry()
    want = n_read + 6 * n_items
    pool = reg.handles[CORPUS].take(want)
    read_split, held_out = pool[:n_read], pool[n_read:]
    if len(held_out) < n_items:
        raise SystemExit(
            f"UNWINNABLE BY CONSTRUCTION: {CORPUS!r} yielded {len(pool)}; reading {n_read} leaves "
            f"{len(held_out)} held out and {n_items} are required.")

    sub = Substrate(seed=seed)
    t0 = time.time()
    total = 0
    while total < n_read:
        r = sub.read(corpus=CORPUS, n_sentences=chunk, batch=50, max_patches=1,
                     consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences
    read_s = time.time() - t0

    cons = sub.consolidated()
    lib = getattr(sub.state.library, "items", {})
    traces_by_term = {}
    for term in cons:
        item = lib.get(term)
        vecs = [t.context_vec for t in (getattr(item, "traces", None) or [])
                if getattr(t, "context_vec", None) is not None]
        if vecs:
            traces_by_term[term] = vecs
    cand = set(traces_by_term)

    items: List[Tuple[str, str]] = []
    for s in held_out:
        present = [l for l in content_lemmas(s) if l in cand]
        if present:
            items.append((s, rng.choice(sorted(set(present)))))
        if len(items) >= n_items:
            break
    if not items:
        raise SystemExit("UNWINNABLE: no held-out sentence mentions any consolidated term")

    # FLOORS, on the same items and the same candidate set.
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    freq: collections.Counter = collections.Counter()
    for s in read_split:
        ls = content_lemmas(s)
        for l in ls:
            if l in cand:
                freq[l] += 1
        for a in ls:
            for b in ls:
                if a != b and a in cand:
                    cooc[b][a] += 1
    freq_rank = [w for w, _ in freq.most_common()]

    def cooc_ranks() -> List[Optional[int]]:
        out = []
        for s, t in items:
            c: collections.Counter = collections.Counter()
            cue = [l for l in content_lemmas(s) if l != t]
            for l in cue:
                c.update(cooc.get(l, {}))
            for w in cue:
                c.pop(w, None)
            ranked = [w for w, _ in c.most_common() if w in cand]
            out.append((ranked.index(t) + 1) if t in ranked else len(cand))
        return out

    out: dict = {"seed": seed, "n_read": total, "read_seconds": round(read_s, 1),
                 "n_consolidated": len(cons), "n_terms_with_traces": len(traces_by_term),
                 "n_items": len(items), "n_candidates": len(cand),
                 "UNDERPOWERED": len(items) < MIN_ITEMS,
                 "thresholds_swept": list(THRESHOLDS)}

    floors = {"COOC_floor": cooc_ranks(),
              "FREQ_floor": [(freq_rank.index(t) + 1) if t in freq_rank else len(cand)
                             for _, t in items]}
    arms: Dict[str, List[Optional[int]]] = {}
    arms["ACCUMULATE"] = _rank_table(_build_profiles(traces_by_term, "ACCUMULATE", 0.0, seed),
                                     items)
    skip_rates = {}
    for thr in THRESHOLDS:
        gp = _build_profiles(traces_by_term, "GATED", thr, seed)
        rp = _build_profiles(traces_by_term, "RANDOM_SKIP", thr, seed)
        arms["GATED@%.2f" % thr] = _rank_table(gp, items)
        arms["RANDOM_SKIP@%.2f" % thr] = _rank_table(rp, items)
        # Report the actual skip rate at each threshold: a swept parameter whose effect is not
        # stated is a knob, not a sweep.
        tot = kept = 0
        for term, traces in traces_by_term.items():
            acc = np.asarray(traces[0], dtype=np.float64).copy()
            kept += 1
            tot += 1
            for tr in traces[1:]:
                tot += 1
                obs = np.asarray(tr, dtype=np.float64)
                pred = _unit(acc)
                if pred is None or residual_magnitude(obs, pred) >= thr:
                    acc = acc + obs
                    kept += 1
        skip_rates["%.2f" % thr] = round(1.0 - kept / max(tot, 1), 4)
    out["skip_rate_by_threshold"] = skip_rates

    blocks: Dict[str, dict] = {}
    for name, ranks in list(arms.items()) + list(floors.items()):
        b: Dict[str, float] = {}
        for k in KS:
            x = _hits(ranks, k)
            lo, hi = _boot_ci(x, nprng)
            b["hit@%d" % k] = float(x.mean())
            b["ci_lo@%d" % k] = lo
            b["ci_hi@%d" % k] = hi
        got = [r for r in ranks if r is not None]
        b["median_rank"] = float(np.median(got)) if got else None
        blocks[name] = b
    out["arms"] = blocks

    # READINGS IN CODE.
    verdicts = {}
    for thr in THRESHOLDS:
        g, rs = blocks["GATED@%.2f" % thr], blocks["RANDOM_SKIP@%.2f" % thr]
        a = blocks["ACCUMULATE"]
        per_k = {}
        for k in KS:
            beats_acc = g["ci_lo@%d" % k] > a["ci_hi@%d" % k]
            beats_rand = g["ci_lo@%d" % k] > rs["ci_hi@%d" % k]
            strongest = max(("COOC_floor", "FREQ_floor"),
                            key=lambda f: blocks[f]["hit@%d" % k])
            per_k["k=%d" % k] = {
                "GATED_beats_ACCUMULATE": bool(beats_acc),
                "GATED_beats_RANDOM_SKIP": bool(beats_rand),
                "READING_A": bool(beats_acc and beats_rand),
                "clears_strongest_floor": bool(g["ci_lo@%d" % k] > blocks[strongest]["ci_hi@%d" % k]),
                "strongest_floor": strongest,
            }
        verdicts["%.2f" % thr] = per_k
    out["readings"] = verdicts

    print("  seed %d: read %d, terms %d, items %d | ACC hit@10 %.4f | COOC hit@10 %.4f%s"
          % (seed, total, len(traces_by_term), len(items),
             blocks["ACCUMULATE"]["hit@10"], blocks["COOC_floor"]["hit@10"],
             "  [UNDERPOWERED]" if out["UNDERPOWERED"] else ""), flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    n_read = 2000 if smoke else 16000
    n_items = 60 if smoke else 300
    chunk = 400 if smoke else 800
    seeds = SEEDS[:1] if smoke else SEEDS

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for seed in seeds:
        key = unit_key(SPEC, a.mode, seed)
        if key in done:
            print(f"[skip] {key}", flush=True)
            continue
        print(f"[run ] {key}", flush=True)
        r = _run(seed, n_read, n_items, chunk)
        r["unit_key"] = key
        if smoke:
            print(json.dumps(r, indent=2, default=str)[:2500])
        else:
            record_unit(OUTPUT_DIR, key, r)

    if smoke:
        print("SMOKE OK")
        return 0

    units = load_units(OUTPUT_DIR)
    rows = list(units.values()) if isinstance(units, dict) else list(units)
    rows = [u for u in rows if str(u.get("unit_key", "")).startswith(SPEC + "|")]
    metrics = {
        "cell": CELL, "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full", "spec": SPEC, "n_units": len(rows), "corpus": CORPUS,
        "what_is_tested": ("the PINNED brain rule (residual x - x_hat as the learning signal, "
                           "ORGAN_MAP G2) against the pure accumulation the substrate uses today"),
        "wiring_not_build": ("hdlab/predictive_coding.py already implements the equation and "
                             "self-tests PASS; a runtime trace showed it is NOT among the 44 "
                             "hdlab modules a real Substrate.read() loads. The organ was unwired."),
        "random_skip_is_mandatory": (
            "Residual magnitudes are nearly constant (p10 0.3575, median 0.4648, p90 0.5237), so "
            "gating on them is close to gating AT RANDOM. Without a rate-matched random arm any "
            "GATED-vs-ACCUMULATE gain is attributable to WRITING LESS, not to selectivity."),
        "threshold_is_swept_not_adopted": (
            "2.5%% of writes skipped at 0.25, 76.2%% at 0.50, 100%% at 0.75 -- the usable band is "
            "a cliff, so a single adopted value would be a parameter masquerading as a finding."),
        "units": rows,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(rows)} units in {time.time() - t0:.0f}s -> {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
