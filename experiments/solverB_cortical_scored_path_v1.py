"""SOLVER-B (problem cortical_read_has_no_scored_path): a clean scored path for the cortical read,
adding the two floors the brief marks MANDATORY, and fixing a held-out leak found in the Aug-19 cell.

WHAT THE DISK ALREADY SAYS, AND IT OUTRANKS THE BRIEF.
The brief (2026-08-22) says the cortical read "has never been scored". It has:
`experiments/exp_cortical_read_consolidated_v1.py` ran FULL, 3 seeds, n=300 items, ~430-480
consolidated candidates, on 2026-08-19 (data/exp_cortical_read_consolidated_v1/metrics.json).
Its verdict, on all 3 seeds and all 5 values of k: the cortical read READS ITS CUE (beats a
content-scrambled donor sentence) but does NOT clear the strongest floor (first-order
co-occurrence counting over the read split) at ANY k -- CONTEXT_clears=False, BOTH_clears=False
in all 15 seed x k cells. That is the cell's own pre-committed READING (B): "the route exists and
carries nothing."

THREE THINGS THIS CELL ADDS.
  1. CONC_floor    -- rank the SAME candidate set by concreteness (grounded_similarity Conc.M
                      z-score), never looking at the cue. The last hypothesis on this organ died
                      to a concreteness-matched floor; the brief marks it mandatory. In a cloze
                      over the consolidated pool the candidates are ALL consolidated (hence all
                      concrete), so concreteness is matched WITHIN the candidate set by
                      construction -- this floor tests whether the read is merely a concreteness
                      ranker.
  2. RANDOM_twin   -- rank the candidates by a per-item random permutation. The information-free
                      twin. It MUST lose; if it wins, the metric cannot fail safely.
  3. A CLEAN HELD-OUT SPLIT. The Aug-19 cell built held_out = pool[n_read:], but the substrate
     reads ~600 sentences PAST n_read via its own cursor (max_patches overshoot), so ~600
     held-out sentences were already read. This cell draws held_out from pool[total:] where
     `total` is the substrate's ACTUAL read count, and MEASURES the Aug-19-style overlap so the
     leak is quantified rather than argued. It also builds COOC/FREQ over the EXACT text the
     substrate read (a fair floor), and SAVES THE SCORED POPULATION.

The leak favours the CORTICAL arm (its profiles saw the leaked sentences; COOC did not count
them), so removing it can only make the cortical read look worse relative to the floor -- the
negative verdict is robust to it either way. This cell does NOT touch hdlab/.

Run: python experiments/solverB_cortical_scored_path_v1.py --mode smoke
     python experiments/solverB_cortical_scored_path_v1.py --mode full   [--seeds 3]
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
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.corpus_registry import CorpusRegistry
from hdlab.cortical_recall import build_cortical_index, cue_vector
from hdlab.grounded_similarity import grounded_vector
from hdlab.reading_grounding_loop import content_lemmas, context_vector_masked
from hdlab.substrate import CONTEXT_DIM, Substrate

CELL = "solverB_cortical_scored_path_v1"
# SH-7 migration (integration, 2026-08-23). One line, so this landed result can be RE-VERIFIED
# without overwriting itself. Without it, `HDI_FRESH_RUN` is ignored, a re-run writes straight into
# the landed directory, and re-stamps `metrics.json` -- which is how 54 landed records were silently
# re-dated once already. `fresh_run_output_dir` returns the path UNCHANGED when the variable is
# unset, so ordinary runs are byte-identical to before.
from experiments.fresh_recompute import fresh_run_output_dir  # noqa: E402

OUTPUT_DIR = fresh_run_output_dir(os.path.join(_REPO, "data", CELL))
SPEC = "v1_clean_split_conc_random_floors"
KS = (1, 5, 10, 25, 50)
CORPUS = "simplewiki"
SEEDS = (20260819, 7, 101)
N_BOOT = 2000
MIN_ITEMS = 200
MIN_CANDIDATES = 50


def _boot_ci(x: np.ndarray, rng: np.random.Generator) -> Tuple[float, float, float]:
    if x.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, x.size, size=(N_BOOT, x.size))
    m = x[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(lo), float(hi), float((hi - lo) / 2.0)


def _donor(cues: Sequence[str], i: int, rng: random.Random) -> str:
    """SCRAMBLE control: an UNRELATED sentence, target kept. Destroy content, not word order."""
    if len(cues) < 2:
        return cues[0]
    j = i
    while j == i:
        j = rng.randrange(len(cues))
    return cues[j]


def _conc_z(word: str) -> Optional[float]:
    v = grounded_vector(word)
    return None if v is None else float(v[11])   # index 11 = Conc.M z-score (12-dim vector)


def _select_items(held: Sequence[str], cand_set: set, n_items: int,
                  rng: random.Random) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for sent in held:
        present = [l for l in content_lemmas(sent) if l in cand_set]
        if not present:
            continue
        items.append((sent, rng.choice(sorted(set(present)))))
        if len(items) >= n_items:
            break
    return items


def _run(seed: int, n_read: int, n_items: int, chunk: int) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)

    reg = CorpusRegistry()
    # Headroom for the substrate's per-call overshoot (up to ~chunk past n_read) PLUS enough
    # clean held-out to draw n_items from. Kept strictly under simplewiki's 20,000 ceiling so
    # take() never returns short and shrinks the held-out split (a documented failure here).
    want = min(n_read + 2 * chunk + 6 * n_items, 19400)
    pool = reg.handles[CORPUS].take(want)

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

    # Reconstruct EXACTLY the sentences the substrate read, from an independent registry, and
    # assert the two registries agree in order (determinism). read_text is what the floors see.
    reg2 = CorpusRegistry()
    read_text = reg2.handles[CORPUS].take(total)
    read_set = set(read_text)
    det_ok = bool(read_text == pool[:total])          # same source, same order -> leak is real

    # CLEAN held-out: sentences strictly past what the substrate read. Provably not seen.
    held_clean = pool[total:]
    # AUG-19-style held-out: pool[n_read:], which OVERLAPS the substrate read by (total - n_read).
    held_aug19 = pool[n_read:]

    cons = sub.consolidated()
    cands = sorted(cons)
    cand_set = set(cands)
    profiles = sub.profile()

    idx = {}
    for space in ("context", "spoke", "both"):
        try:
            idx[space] = build_cortical_index(cons, profiles, space=space)
        except Exception:
            idx[space] = {}
    order = {sp: sorted(v) for sp, v in idx.items()}
    mats = {sp: (np.stack([v[n] for n in order[sp]]) if order[sp] else np.zeros((0, 1)))
            for sp, v in idx.items()}
    posn = {sp: {n: i for i, n in enumerate(order[sp])} for sp in idx}

    # Floors over the EXACT text the substrate read.
    freq: collections.Counter = collections.Counter()
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for sent in read_text:
        lems = content_lemmas(sent)
        for l in lems:
            if l in cand_set:
                freq[l] += 1
        for a in lems:
            for b in lems:
                if a != b and a in cand_set:
                    cooc[b][a] += 1
    freq_rank = [w for w, _ in freq.most_common()]
    conc_vals = {w: _conc_z(w) for w in cands}
    n_no_conc = sum(1 for w in cands if conc_vals[w] is None)
    conc_rank = sorted(cands, key=lambda w: (conc_vals[w] is None, -(conc_vals[w] or 0.0), w))

    def rank_cortical(space: str, sent: str, tgt: str) -> Optional[int]:
        M, P = mats.get(space), posn.get(space, {})
        if M is None or M.shape[0] == 0 or tgt not in P:
            return None
        q = cue_vector(content_lemmas(sent), profiles, space=space, exclude=[tgt],
                       context_vec=context_vector_masked(sent, tgt, d=CONTEXT_DIM))
        if q is None or q.shape[0] != M.shape[1]:
            return None
        sims = M @ q
        return int(np.sum(sims > sims[P[tgt]])) + 1

    def _cooc_counter(sent: str, tgt: str) -> collections.Counter:
        c: collections.Counter = collections.Counter()
        cue = [l for l in content_lemmas(sent) if l != tgt]
        for l in cue:
            c.update(cooc.get(l, {}))
        for w in cue:
            c.pop(w, None)
        return c

    def rank_cooc(sent: str, tgt: str) -> Optional[int]:
        c = _cooc_counter(sent, tgt)
        if not c:
            return None
        ranked = [w for w, _ in c.most_common() if w in cand_set]
        return (ranked.index(tgt) + 1) if tgt in ranked else len(cands)

    def cooc_saw_target(sent: str, tgt: str) -> bool:
        """BRAIN-FOUNDATIONAL PARTITION. True iff the target co-occurred with >=1 cue word in the
        read text. On the FALSE (unseen) subset, first-order co-occurrence counting has NO signal
        for the target -- so a cortical read that retrieves THERE is doing the CLS-distinctive
        thing (generalising beyond raw co-occurrence), which the episodic/hippocampal route cannot."""
        return tgt in _cooc_counter(sent, tgt)

    def rank_freq(tgt: str) -> Optional[int]:
        return (freq_rank.index(tgt) + 1) if tgt in freq_rank else len(cands)

    def rank_conc(tgt: str) -> Optional[int]:
        return (conc_rank.index(tgt) + 1) if tgt in conc_rank else len(cands)

    def rank_random(i: int, tgt: str) -> int:
        rr = random.Random((seed << 16) ^ (i * 2654435761 & 0xFFFFFFFF))
        perm = cands[:]
        rr.shuffle(perm)
        return perm.index(tgt) + 1

    def top1_episodic(sent: str, tgt: str) -> Tuple[Optional[str], bool]:
        for lem, _ in sub.recall_sentence(sent, target=tgt, top_k=200):
            if lem in cand_set and lem != tgt:
                return lem, True
        return None, False

    def score_set(items: List[Tuple[str, str]], donor_rng: random.Random,
                  with_episodic: bool) -> dict:
        cue_sents = [s for s, _ in items]
        donors = [_donor(cue_sents, i, donor_rng) for i in range(len(items))]
        rank_arms: Dict[str, List[Optional[int]]] = {}
        for space in ("context", "spoke", "both"):
            rank_arms["RANK_" + space.upper()] = [rank_cortical(space, s, t) for s, t in items]
        rank_arms["RANK_SCRAMBLE"] = [rank_cortical("context", donors[i], t)
                                      for i, (_, t) in enumerate(items)]
        rank_arms["RANK_COOC_floor"] = [rank_cooc(s, t) for s, t in items]
        rank_arms["RANK_FREQ_floor"] = [rank_freq(t) for _, t in items]
        rank_arms["RANK_CONC_floor"] = [rank_conc(t) for _, t in items]
        rank_arms["RANK_RANDOM_twin"] = [rank_random(i, t) for i, (_, t) in enumerate(items)]

        def _hitk(rank_arms: Dict[str, List[Optional[int]]],
                  mask: Optional[List[bool]] = None) -> Dict[str, Dict]:
            hk: Dict[str, Dict] = {}
            for name, ranks in rank_arms.items():
                rr = ranks if mask is None else [r for r, m in zip(ranks, mask) if m]
                block: Dict = {}
                for k in KS:
                    x = np.asarray([int(r is not None and r <= k) for r in rr], dtype=np.float64)
                    lo, hi, hw = _boot_ci(x, nprng)
                    block["hit@%d" % k] = float(x.mean()) if x.size else None
                    block["ci_lo@%d" % k] = lo
                    block["ci_hi@%d" % k] = hi
                got = [r for r in rr if r is not None]
                block["median_rank"] = float(np.median(got)) if got else None
                block["n_scored"] = len(got)
                hk[name] = block
            return hk

        hitk = _hitk(rank_arms)

        floor_names = ("RANK_COOC_floor", "RANK_FREQ_floor", "RANK_CONC_floor")
        beat = {}
        for k in KS:
            strongest = max(floor_names, key=lambda f: hitk[f]["hit@%d" % k])
            bar = hitk[strongest]["ci_hi@%d" % k]
            best_cort = max(("RANK_CONTEXT", "RANK_SPOKE", "RANK_BOTH"),
                            key=lambda a: hitk[a]["hit@%d" % k])
            beat["k=%d" % k] = {
                "strongest_floor": strongest,
                "floor_hit": hitk[strongest]["hit@%d" % k],
                "credible_bar": bar,
                "CONTEXT_clears": bool(hitk["RANK_CONTEXT"]["ci_lo@%d" % k] > bar),
                "BOTH_clears": bool(hitk["RANK_BOTH"]["ci_lo@%d" % k] > bar),
                "best_cortical_arm": best_cort,
                "best_cortical_clears": bool(hitk[best_cort]["ci_lo@%d" % k] > bar),
                "cortical_beats_random_twin": bool(
                    hitk["RANK_CONTEXT"]["ci_lo@%d" % k]
                    > hitk["RANK_RANDOM_twin"]["ci_hi@%d" % k]),
                "cortical_beats_scramble": bool(
                    hitk["RANK_CONTEXT"]["ci_lo@%d" % k] > hitk["RANK_SCRAMBLE"]["ci_hi@%d" % k]),
            }
        # BRAIN-FOUNDATIONAL STRATIFICATION. Partition items by whether raw co-occurrence counting
        # had ANY signal for the target. On the UNSEEN subset it does not, so this isolates the
        # CLS-distinctive question: does the cortical read generalise beyond co-occurrence?
        seen_mask = [cooc_saw_target(s, t) for s, t in items]
        unseen_mask = [not m for m in seen_mask]
        n_seen = int(sum(seen_mask))
        n_unseen = int(sum(unseen_mask))
        hitk_seen = _hitk(rank_arms, seen_mask) if n_seen else {}
        hitk_unseen = _hitk(rank_arms, unseen_mask) if n_unseen else {}

        def _unseen_verdict() -> dict:
            # On unseen items, the fair floors are FREQ/CONC/RANDOM/SCRAMBLE (COOC has no signal).
            v = {"n_unseen": n_unseen}
            if n_unseen < 30:
                v["verdict"] = "UNDERPOWERED_unseen_subset"
                return v
            noncooc = ("RANK_FREQ_floor", "RANK_CONC_floor", "RANK_RANDOM_twin", "RANK_SCRAMBLE")
            per_k = {}
            for k in KS:
                bar = max(hitk_unseen[f]["ci_hi@%d" % k] or 0.0 for f in noncooc)
                best = max(("RANK_CONTEXT", "RANK_BOTH", "RANK_SPOKE"),
                           key=lambda a: hitk_unseen[a]["hit@%d" % k] or 0.0)
                per_k["k=%d" % k] = {
                    "best_cortical_arm": best,
                    "best_cortical_hit": hitk_unseen[best]["hit@%d" % k],
                    "strongest_noncooc_floor_upper": bar,
                    "cortical_clears": bool((hitk_unseen[best]["ci_lo@%d" % k] or 0.0) > bar),
                    "cooc_hit": hitk_unseen["RANK_COOC_floor"]["hit@%d" % k],
                }
            v["per_k"] = per_k
            v["cortical_generalises_at_any_k"] = any(
                per_k["k=%d" % k]["cortical_clears"] for k in KS)
            return v

        res = {"hit_at_k": hitk, "clears_strongest_floor_per_k": beat, "n_items": len(items),
               "reads_cue_hit1": bool(hitk["RANK_CONTEXT"]["hit@1"]
                                      > hitk["RANK_SCRAMBLE"]["hit@1"]),
               "brain_foundational_generalization": {
                   "n_seen_cooccurrence": n_seen, "n_unseen_cooccurrence": n_unseen,
                   "hit_at_k_seen": hitk_seen, "hit_at_k_unseen": hitk_unseen,
                   "unseen_verdict": _unseen_verdict()}}
        if with_episodic:
            epi = [top1_episodic(s, t) for s, t in items]
            x = np.asarray([int(e[0] == t) for e, (s, t) in zip(epi, items)], dtype=np.float64)
            lo, hi, hw = _boot_ci(x, nprng)
            res["EPISODIC_FILTERED"] = {"hit@1": float(x.mean()), "hits": int(x.sum()),
                                        "ci_lo": lo, "ci_hi": hi,
                                        "items_surfacing_any_candidate": int(sum(e[1] for e in epi))}
        return res

    # PRIMARY: clean split. SECONDARY: aug19-style split (leaky), same pipeline, to show the
    # verdict does not depend on the leak. Independent rng streams so neither perturbs the other.
    items_clean = _select_items(held_clean, cand_set, n_items, rng)
    items_aug19 = _select_items(held_aug19, cand_set, n_items, random.Random(seed ^ 0xABCDEF))
    if len(items_clean) < 1 or len(items_aug19) < 1:
        raise SystemExit("UNWINNABLE: no held-out sentence mentions a consolidated term.")

    aug19_overlap = int(sum(1 for s, _ in items_aug19 if s in read_set))

    clean = score_set(items_clean, random.Random(seed + 1), with_episodic=True)
    aug19 = score_set(items_aug19, random.Random(seed + 2), with_episodic=False)

    out: dict = {
        "seed": seed, "n_read_requested": n_read, "n_read_actual": total,
        "read_seconds": round(read_s, 1),
        "registries_deterministic": det_ok,
        "n_consolidated": len(cons), "n_candidates_no_concreteness_norm": n_no_conc,
        "chance_at_1": (1.0 / len(cands)) if cands else None,
        "index_sizes": {k: len(v) for k, v in idx.items()},
        "distinct_targets_clean": len({t for _, t in items_clean}),
        "UNDERPOWERED": len(items_clean) < MIN_ITEMS or len(cands) < MIN_CANDIDATES,
        "aug19_style_heldout_overlap_with_read": aug19_overlap,
        "aug19_overlap_note": ("how many aug19-style (pool[n_read:]) item sentences were ALREADY "
                               "read by the substrate; the leak this cell removes. 0 in the clean "
                               "split by construction."),
        "CLEAN": clean,
        "AUG19_STYLE": aug19,
        "scored_population_clean": {"items": items_clean, "consolidated": cands},
    }
    cb = clean["clears_strongest_floor_per_k"]
    gen = clean["brain_foundational_generalization"]
    print("  seed %d read %d cons %d items %d | CLEAN @1: CTX %.4f COOC %.4f FREQ %.4f CONC %.4f "
          "SCRAM %.4f RAND %.4f EPI %.4f | best_cortical_clears_floor(any k)=%s | aug19_overlap=%d"
          % (seed, total, len(cons), clean["n_items"],
             clean["hit_at_k"]["RANK_CONTEXT"]["hit@1"], clean["hit_at_k"]["RANK_COOC_floor"]["hit@1"],
             clean["hit_at_k"]["RANK_FREQ_floor"]["hit@1"], clean["hit_at_k"]["RANK_CONC_floor"]["hit@1"],
             clean["hit_at_k"]["RANK_SCRAMBLE"]["hit@1"], clean["hit_at_k"]["RANK_RANDOM_twin"]["hit@1"],
             clean.get("EPISODIC_FILTERED", {}).get("hit@1", float("nan")),
             any(cb["k=%d" % k]["best_cortical_clears"] for k in KS), aug19_overlap), flush=True)
    print("    BRAIN-FOUND generalization: n_unseen_cooc=%d verdict=%s generalises_any_k=%s"
          % (gen["n_unseen_cooccurrence"], gen["unseen_verdict"].get("verdict", "scored"),
             gen["unseen_verdict"].get("cortical_generalises_at_any_k")), flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--seeds", type=int, default=1)
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    n_read = 2000 if smoke else 16000
    n_items = 60 if smoke else 300
    chunk = 400 if smoke else 800
    seeds = SEEDS[:1] if smoke else SEEDS[:max(1, a.seeds)]

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
            slim = {k: v for k, v in r.items() if k != "scored_population_clean"}
            print(json.dumps(slim, indent=2, default=str)[:3200])
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
        "what_is_scored": ("the CORTICAL read (hdlab/cortical_recall.py) on a CLEAN held-out cloze "
                           "over the consolidated pool, with COOC/FREQ/CONC floors + random twin"),
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
