"""exp_grounding_readout_known_answer_v1 -- WHAT IS THE READ-OUT'S QUALITY, AND WHAT IS ITS FLOOR?

PRE-REG: preregs/2026-08-14_grounding_readout_known_answer_v1.md, COMMITTED BEFORE this cell was
run. Every arm, floor, band and gate is frozen there.

WHY THIS CELL EXISTS
C3 (reading-grounding MEANINGFUL rate) is quoted at 1-3% with NO RECORDED FLOOR, and it gates
knowledge-base growth for the whole project. Two prior attempts gated on a HAND-SCORED MEANINGFUL
DELTA and were arithmetically undecidable at that base rate:
  MEASURED@data/exp_grounding_quality_readout_v1/blind_sample.json -- 100 blind rows, 3 MEANINGFUL
  CITED@notes/SUBSTRATE_STRATEGY.md STEP 1 -- dispatched 3x, never resolved to a quality number
This cell does NOT gate on a hand-scored delta. It uses KNOWN-ANSWER RECALL against WordNet 3.0
gold meaning sets WITH A MEASURED FLOOR, plus a 2AFC arm whose chance level is 0.50 BY CONSTRUCTION
(two candidates, pure argmax) and therefore cannot be floor-pinned.

NOTHING UNDER hdlab/ IS MODIFIED. ConceptSpace, context_vector_masked and canonicalize_fast (the
read-out itself) are hdlab's own objects, imported and called.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint via tools/exp_checkpoint (arm x chunk), resume-safe, sorted(set()) only
# - arms-must-differ: sha256 over each arm's correctness vector
# - floors are ARMS, not assertions: A2/A3 (stage A) and B2/B3/B6 (stage B) are measured
# - discriminator range by construction: stage B chance = 0.50 (2 candidates, thresh=-1.0)
# - positive control SELF_RETRIEVAL >= 0.70 or stage B is VOID_PLUMBING (no quality claim)
# - power: MIN_ITEMS=200 -> MDE_95 ~ 0.069 < the 0.10 band width; below that, no read
# - all numbers in comments tagged MEASURED@ / CITED@ / HYPOTHESIZED@
ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import (numpy sizes its pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

# HD_GRADED_COMPARATOR must be set BEFORE hdlab is imported (the module reads it once, at import).
# Parsed from argv by hand for exactly that reason -- NEVER as an inline shell env prefix.
_GRADED_ARG = "1"
for _i, _a in enumerate(sys.argv):
    if _a == "--graded" and _i + 1 < len(sys.argv):
        _GRADED_ARG = sys.argv[_i + 1]
    elif _a.startswith("--graded="):
        _GRADED_ARG = _a.split("=", 1)[1]
os.environ["HD_GRADED_COMPARATOR"] = _GRADED_ARG

import argparse
import bisect
import hashlib
import inspect
import json
import platform
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import wordnet as wn                                          # noqa: E402

from hdlab.reading_grounding_loop import (                                     # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, canonicalize_fast, content_lemmas,
    context_vector_masked, normalize_lemma,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_grounding_readout_known_answer_v1"
PREREG_PATH = "preregs/2026-08-14_grounding_readout_known_answer_v1.md"

BANKED_DIR = os.path.join(REPO_ROOT, "data", "exp_grounding_quality_readout_v1")
BANKED_ARMS = ("PBV_BASE", "PBV_F1F3")

MASTER_SEED = 20260814
N_BOOTSTRAP = 5000

MIN_LEMMA_COUNT = 8          # corpus sentence-count floor for a lemma to become an anchor
MIN_LEMMA_LEN = 3
K_SENT_TOTAL = 90            # sentences kept per lemma
N_PROFILE = 60               # of those, the first N_PROFILE build the anchor; rest are held out
FOIL_RATIO_BAND = (0.5, 2.0)
MAX_ITEMS = 4000
MIN_ITEMS = 200              # HARD power gate (FULL only)
SMOKE_LIMIT_PER_SEGMENT = 400
SELF_RETRIEVAL_FLOOR = 0.70
CHANCE = 0.50

STAGE_A_ARMS = ("A1_REAL", "A2_SCRAMBLE", "A3_POPULARITY")
STAGE_B_ARMS = ("B1_ACCUM_REAL", "B2_ACCUM_SCRAMBLE", "B3_FREQUENCY", "B4_SENTENCE_REAL")
REVIVAL_MEANINGFUL_MIN = 0.10       # CITED@notes/SUBSTRATE_STRATEGY.md PART 1 (C3 gate)
REVIVAL_TAUTOLOGY_MAX = 0.10
HP_A_DELTA = 0.05
HP_B_ACC = 0.60


# ------------------------------------------------------------------ durability plumbing
def _out_dir(run_mode: str) -> str:
    suffix = "" if run_mode == "full" else "_" + run_mode.upper()
    graded = "" if os.environ.get("HD_GRADED_COMPARATOR", "1") not in ("0", "false", "no") else "_G0"
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix + graded)


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"),
                 {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                  "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                  "graded_comparator": GRADED_COMPARATOR})
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _seed_for(key: str) -> int:
    """Deterministic seed from a string. hashlib, NEVER builtin hash()."""
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


def _digest(vec: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(vec, dtype=np.uint8).tobytes()).hexdigest()


# ------------------------------------------------------------------ gold standard
_GOLD_CACHE: Dict[str, frozenset] = {}


def gold_meaning_set(word: str) -> frozenset:
    """Pre-reg sec 3. Deliberately GENEROUS: synonyms + hypernyms (2 up) + sisters + hyponyms,
    over ALL synsets of the word, any POS. A generous gold makes a HIT EASIER, so a null is
    conservative."""
    w = word.lower()
    if w in _GOLD_CACHE:
        return _GOLD_CACHE[w]
    g = set()
    for s in wn.synsets(w):
        for l in s.lemma_names():
            g.add(l.lower())
        for h in s.hypernyms() + s.instance_hypernyms():
            for l in h.lemma_names():
                g.add(l.lower())
            for hh in h.hypernyms():
                for l in hh.lemma_names():
                    g.add(l.lower())
            for sis in h.hyponyms():                       # sister terms
                for l in sis.lemma_names():
                    g.add(l.lower())
        for hy in s.hyponyms():
            for l in hy.lemma_names():
                g.add(l.lower())
    g.discard(w)
    g = {x for x in g if not _is_variant(x, w)}
    out = frozenset(g)
    _GOLD_CACHE[w] = out
    return out


def _is_variant(tok: str, word: str) -> bool:
    """Deliberately OVER-inclusive morphological-variant test; a leak control should over-remove."""
    if tok == word:
        return True
    if normalize_lemma(tok) == normalize_lemma(word):
        return True
    if tok.startswith(word) and 0 < len(tok) - len(word) <= 3:
        return True
    if word.startswith(tok) and 0 < len(word) - len(tok) <= 3 and len(tok) >= 4:
        return True
    return False


def _is_tautology(subject: str, obj: str) -> bool:
    return normalize_lemma(str(subject).lower()) == normalize_lemma(str(obj).lower())


# ------------------------------------------------------------------ paired bootstrap
def paired_bootstrap(correct: Dict[str, np.ndarray], arms: Sequence[str], deltas: Sequence[tuple],
                     n_boot: int, seed: int, chance_arm: Optional[str] = None) -> dict:
    keys = list(arms)
    mat = np.stack([correct[k].astype(np.float64) for k in keys], axis=0)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    acc_boot = np.empty((n_boot, len(keys)), dtype=np.float64)
    done = 0
    while done < n_boot:
        m = min(500, n_boot - done)
        idx = rng.integers(0, n, size=(m, n))
        acc_boot[done:done + m] = mat[:, idx].mean(axis=2).T
        done += m
    out = {"n_boot": n_boot, "seed": seed, "n_items": int(n), "arm_acc_ci": {}, "deltas": {}}
    for j, k in enumerate(keys):
        lo, hi = np.percentile(acc_boot[:, j], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": round(float(mat[j].mean()), 6),
                                "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
                                "sd": round(float(acc_boot[:, j].std()), 6)}
    for name, a, b in deltas:
        d = acc_boot[:, keys.index(a)] - acc_boot[:, keys.index(b)]
        point = float(mat[keys.index(a)].mean() - mat[keys.index(b)].mean())
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"][name] = {"delta": round(point, 6), "ci_lo": round(float(lo), 6),
                               "ci_hi": round(float(hi), 6), "sd": round(float(d.std()), 6),
                               "mde_95": round(float(1.96 * d.std()), 6),
                               "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0)}
    if chance_arm is not None:
        d = acc_boot[:, keys.index(chance_arm)] - CHANCE
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"]["d_%s_minus_CHANCE" % chance_arm] = {
            "delta": round(float(mat[keys.index(chance_arm)].mean() - CHANCE), 6),
            "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
            "sd": round(float(d.std()), 6), "mde_95": round(float(1.96 * d.std()), 6),
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0)}
    return out


def _derangement(n: int, conflict) -> List[int]:
    """Deterministic derangement: donor[i] != i and conflict(i, donor) is False."""
    if n < 2:
        return list(range(n))
    off = n // 2 + 1
    donors = []
    for i in range(n):
        j = (i + off) % n
        tries = 0
        while tries < n and (j == i or conflict(i, j)):
            j = (j + 1) % n
            tries += 1
        donors.append(j)
    return donors


# ------------------------------------------------------------------ STAGE A
def stage_a(output_dir: str) -> dict:
    """Known-answer audit of the ALREADY-BANKED facts, with a measured floor (pre-reg sec 4)."""
    per_arm = {}
    for banked in BANKED_ARMS:
        path = os.path.join(BANKED_DIR, "arm_%s_provenance.json" % banked)
        if not os.path.exists(path):
            per_arm[banked] = {"error": "banked provenance missing: %s" % path}
            continue
        with open(path, encoding="utf-8") as f:
            prov = json.load(f)
        pairs = sorted(set((str(r["subject"]).lower(), str(r["object"]).lower()) for r in prov))
        n_taut_all = sum(1 for s, o in pairs if _is_tautology(s, o))
        ev = [(s, o) for s, o in pairs if wn.synsets(s)]
        n = len(ev)
        if n == 0:
            per_arm[banked] = {"error": "no WordNet-evaluable facts"}
            continue
        subs = [s for s, _o in ev]
        objs = [o for _s, o in ev]

        a1 = np.array([o in gold_meaning_set(s) for s, o in ev], dtype=bool)
        donors = _derangement(n, lambda i, j: objs[j] == objs[i])
        a2 = np.array([objs[donors[i]] in gold_meaning_set(subs[i]) for i in range(n)], dtype=bool)
        rng = np.random.default_rng(MASTER_SEED + 1)
        obj_counts = Counter(objs)
        pool = sorted(obj_counts)
        probs = np.array([obj_counts[o] for o in pool], dtype=np.float64)
        probs = probs / probs.sum()
        drawn = [pool[int(k)] for k in rng.choice(len(pool), size=n, p=probs)]
        a3 = np.array([drawn[i] in gold_meaning_set(subs[i]) for i in range(n)], dtype=bool)

        correct = {"A1_REAL": a1, "A2_SCRAMBLE": a2, "A3_POPULARITY": a3}
        bs = paired_bootstrap(correct, STAGE_A_ARMS,
                              [("d_A1_minus_A2", "A1_REAL", "A2_SCRAMBLE"),
                               ("d_A1_minus_A3", "A1_REAL", "A3_POPULARITY")],
                              N_BOOTSTRAP, MASTER_SEED)
        per_arm[banked] = {
            "n_facts_total": len(pairs), "n_wordnet_evaluable": n,
            "evaluable_fraction": round(n / len(pairs), 6),
            "tautology_rate_all_facts": round(n_taut_all / len(pairs), 6),
            "n_tautology_all_facts": n_taut_all,
            "gold_hit": {k: bs["arm_acc_ci"][k] for k in STAGE_A_ARMS},
            "bootstrap": bs,
            "arm_digests": {k: _digest(v) for k, v in correct.items()},
            "examples_hit": [f"{s}->{o}" for (s, o), h in zip(ev, a1) if h][:20],
        }
        print("[stageA] %s n_eval=%d GOLD_HIT real=%.4f scramble=%.4f popularity=%.4f "
              "d=%.4f CI=[%.4f,%.4f]" % (
                  banked, n, bs["arm_acc_ci"]["A1_REAL"]["acc"],
                  bs["arm_acc_ci"]["A2_SCRAMBLE"]["acc"], bs["arm_acc_ci"]["A3_POPULARITY"]["acc"],
                  bs["deltas"]["d_A1_minus_A2"]["delta"], bs["deltas"]["d_A1_minus_A2"]["ci_lo"],
                  bs["deltas"]["d_A1_minus_A2"]["ci_hi"]), flush=True)
        record_unit(output_dir, unit_key("stageA", banked), per_arm[banked])

    verdict, notes = decide_stage_a(per_arm)
    return {"per_banked_arm": per_arm, "verdict": verdict, "notes": notes,
            "banked_provenance_note":
                "facts banked 2026-08-12 by exp_grounding_quality_readout_v1 (FULL, "
                "STRUCTURAL_PASS_PENDING_B3), i.e. BEFORE the HD_GRADED_COMPARATOR default flip "
                "(38f7a0d5c, 2026-08-14). No cross-setting comparison is drawn from stage A."}


def decide_stage_a(per_arm: dict) -> Tuple[str, List[str]]:
    usable = {k: v for k, v in per_arm.items() if "error" not in v}
    if not usable:
        return "NO_BANKED_DATA", ["no banked provenance could be scored"]
    # the read-out's own default arm is PBV_BASE; the verdict is taken on it.
    key = "PBV_BASE" if "PBV_BASE" in usable else sorted(usable)[0]
    v = usable[key]
    hit = v["gold_hit"]["A1_REAL"]["acc"]
    flo = v["gold_hit"]["A2_SCRAMBLE"]["acc"]
    pop = v["gold_hit"]["A3_POPULARITY"]["acc"]
    d = v["bootstrap"]["deltas"]["d_A1_minus_A2"]
    notes = ["arm=%s GOLD_HIT=%.4f floor_scramble=%.4f floor_popularity=%.4f d=%.4f CI=[%.4f,%.4f]"
             % (key, hit, flo, pop, d["delta"], d["ci_lo"], d["ci_hi"])]
    if d["delta"] < 0 and d["ci_excludes_zero"]:
        return "HARD_FAIL_BELOW_FLOOR", notes
    if not d["ci_excludes_zero"]:
        return "AT_FLOOR", notes + ["the banked meanings are statistically indistinguishable from a "
                                    "random re-pairing of the same object words"]
    if hit >= REVIVAL_MEANINGFUL_MIN and d["delta"] >= HP_A_DELTA and hit > pop:
        return "HARD_PASS_A", notes
    return "SIGNAL_ABOVE_FLOOR", notes + ["beats its floor but does NOT clear the recorded revival "
                                          "criterion of %.2f" % REVIVAL_MEANINGFUL_MIN]


# ------------------------------------------------------------------ corpus + space
def build_corpus(run_mode: str) -> List[str]:
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode != "full" else None
    return [s for _seg, s in load_corpus_v5(limit, lineaware=True)]


def build_buckets(sents: List[str]) -> Tuple[Dict[str, List[int]], Counter]:
    lem_of: List[List[str]] = []
    counts: Counter = Counter()
    for s in sents:
        lems = sorted(set(l for l in content_lemmas(s)
                          if l.isalpha() and len(l) >= MIN_LEMMA_LEN))
        lem_of.append(lems)
        counts.update(lems)
    buckets: Dict[str, List[int]] = defaultdict(list)
    for i, lems in enumerate(lem_of):
        for l in lems:
            if counts[l] >= MIN_LEMMA_COUNT and len(buckets[l]) < K_SENT_TOTAL:
                buckets[l].append(i)
    return {k: v for k, v in buckets.items() if counts[k] >= MIN_LEMMA_COUNT}, counts


def build_space(sents: List[str], buckets: Dict[str, List[int]], output_dir: str) -> ConceptSpace:
    """The substrate's OWN anchor construction: hdlab ConceptSpace accumulating hdlab
    context_vector_masked over each lemma's PROFILE sentences. No new mechanism."""
    sp = ConceptSpace(d=CTX_D)
    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:N_PROFILE]:
            sp.observe(w, context_vector_masked(sents[i], w))
        if k % 500 == 0 or k == len(lemmas) - 1:
            print("[space] %d/%d lemmas elapsed=%.1fs" % (k + 1, len(lemmas), time.time() - t0),
                  flush=True)
            _heartbeat(output_dir, {"phase": "space", "lemma_idx": k + 1, "n_lemmas": len(lemmas)})
    return sp


def build_items(space: ConceptSpace, buckets: Dict[str, List[int]], counts: Counter,
                max_items: int) -> Tuple[List[dict], dict]:
    anchors = sorted(set(space.anchors()))
    anchor_set = set(anchors)
    by_count = sorted(anchors, key=lambda w: (counts[w], w))
    count_axis = [counts[w] for w in by_count]
    rm: Counter = Counter()
    items: List[dict] = []
    for L in sorted(buckets):
        if L not in anchor_set:
            rm["removed_L_not_anchor"] += 1
            continue
        if not wn.synsets(L):
            rm["removed_L_not_in_wordnet"] += 1
            continue
        gold = gold_meaning_set(L)
        cands = sorted(g for g in gold if g in anchor_set and g != L and not _is_variant(g, L))
        if not cands:
            rm["removed_no_gold_anchor"] += 1
            continue
        G = max(cands, key=lambda w: (counts[w], w))       # best-estimated gold anchor
        # foil: nearest corpus count to G, excluded from L's gold set and symmetric-excluded
        target = counts[G]
        pos = bisect.bisect_left(count_axis, target)
        F = None
        for step in range(len(by_count)):
            for idx in (pos + step, pos - step - 1):
                if not (0 <= idx < len(by_count)):
                    continue
                cand = by_count[idx]
                if cand in (L, G) or cand in gold:
                    continue
                if _is_variant(cand, L) or _is_variant(cand, G):
                    continue
                if L in gold_meaning_set(cand):
                    continue
                ratio = counts[cand] / max(1.0, float(counts[G]))
                if not (FOIL_RATIO_BAND[0] <= ratio <= FOIL_RATIO_BAND[1]):
                    continue
                F = cand
                break
            if F is not None:
                break
        if F is None:
            rm["removed_no_frequency_matched_foil"] += 1
            continue
        if space.bundle(L) is None or space.bundle(G) is None or space.bundle(F) is None:
            rm["removed_missing_bundle"] += 1
            continue
        # held-out sentence for B4: an EVAL sentence of L free of G/F and their variants
        sent_idx = None
        for i in buckets[L][N_PROFILE:]:
            sent_idx = i
            break
        items.append({"item_id": "%s|%s|%s" % (L, G, F), "L": L, "G": G, "F": F,
                      "sent_idx": sent_idx, "count_G": int(counts[G]), "count_F": int(counts[F])})
    items.sort(key=lambda it: it["item_id"])
    n_before = len(items)
    if max_items is not None and len(items) > max_items:
        items = items[:max_items]
    diag = {"n_anchors": len(anchors), "n_items_before_cap": n_before, "n_items": len(items),
            "removals": dict(sorted(rm.items())),
            "n_items_with_heldout_sentence": sum(1 for it in items if it["sent_idx"] is not None)}
    return items, diag


# ------------------------------------------------------------------ STAGE B
def _mask_for(pos: Dict[str, int], n_anchors: int, words: Sequence[str]) -> np.ndarray:
    m = np.zeros(n_anchors, dtype=bool)
    for w in words:
        m[pos[w]] = True
    return m


def stage_b(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    sents = build_corpus(run_mode)
    print("[corpus] n_sentences=%d" % len(sents), flush=True)
    buckets, counts = build_buckets(sents)
    print("[corpus] n_candidate_lemmas=%d" % len(buckets), flush=True)
    space = build_space(sents, buckets, output_dir)
    anchors, _mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, item_diag = build_items(space, buckets, counts, MAX_ITEMS)
    n = len(items)
    print("[items] n=%d %s" % (n, json.dumps(item_diag["removals"])), flush=True)

    if n < 2:
        return {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "n_items": n, "item_diag": item_diag,
                "notes": ["fewer than 2 items -- vacuous"]}
    if run_mode == "full" and n < MIN_ITEMS:
        return {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "n_items": n, "item_diag": item_diag,
                "notes": ["only %d clean items (pre-registered floor %d); STOPPED rather than "
                          "reading underpowered" % (n, MIN_ITEMS)]}

    donors = _derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                              & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)

    correct: Dict[str, np.ndarray] = {k: np.zeros(n, dtype=bool) for k in STAGE_B_ARMS}
    open_pick_real: List[str] = []
    open_pick_scram: List[str] = []
    diag = Counter()
    rng = np.random.default_rng(MASTER_SEED + 3)

    for i, it in enumerate(items):
        L, G, F = it["L"], it["G"], it["F"]
        mask2 = _mask_for(pos, len(anchors), (G, F))
        qL = space.bundle(L)
        qD = space.bundle(items[donors[i]]["L"])

        pick, _c = canonicalize_fast("__slot__", qL, space, thresh=-1.0, eligible_mask=mask2)
        correct["B1_ACCUM_REAL"][i] = (pick == G)
        pick, _c = canonicalize_fast("__slot__", qD, space, thresh=-1.0, eligible_mask=mask2)
        correct["B2_ACCUM_SCRAMBLE"][i] = (pick == G)
        if it["count_G"] == it["count_F"]:
            diag["B3_ties_fell_back_to_coin"] += 1
            correct["B3_FREQUENCY"][i] = bool(rng.integers(2) == 0)
        else:
            correct["B3_FREQUENCY"][i] = it["count_G"] > it["count_F"]
        if it["sent_idx"] is None:
            diag["B4_no_heldout_sentence_fell_back_to_coin"] += 1
            correct["B4_SENTENCE_REAL"][i] = bool(rng.integers(2) == 0)
        else:
            q = context_vector_masked(sents[it["sent_idx"]], L)
            if float(np.linalg.norm(q)) < 1e-9:
                diag["B4_zero_query_fell_back_to_coin"] += 1
                correct["B4_SENTENCE_REAL"][i] = bool(rng.integers(2) == 0)
            else:
                pick, _c = canonicalize_fast("__slot__", q, space, thresh=-1.0,
                                             eligible_mask=mask2)
                correct["B4_SENTENCE_REAL"][i] = (pick == G)

        # OPEN-VOCABULARY read-out (B5/B6): the argmax the reading loop actually performs.
        p_open, _c = canonicalize_fast("__slot__", qL, space, thresh=-1.0)
        open_pick_real.append(str(p_open))
        p_open_s, _c = canonicalize_fast("__slot__", qD, space, thresh=-1.0)
        open_pick_scram.append(str(p_open_s))

        if (i + 1) % 250 == 0 or i == n - 1:
            print("[stageB] item %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)
            _heartbeat(output_dir, {"phase": "stageB", "item": i + 1, "n_items": n})
            record_unit(output_dir, unit_key("stageB_progress", str(i + 1)),
                        {"i": i + 1, "elapsed_s": round(time.time() - t0, 2)})

    # open-vocabulary known-answer hit@1 and TAUTOLOGY rate, with a scramble floor
    open_real_hit = np.array([open_pick_real[i] in gold_meaning_set(items[i]["L"])
                              for i in range(n)], dtype=bool)
    open_scram_hit = np.array([open_pick_scram[i] in gold_meaning_set(items[i]["L"])
                               for i in range(n)], dtype=bool)
    open_taut = np.array([_is_tautology(items[i]["L"], open_pick_real[i]) for i in range(n)],
                         dtype=bool)
    open_bs = paired_bootstrap({"B5_OPEN_REAL": open_real_hit, "B6_OPEN_SCRAMBLE": open_scram_hit},
                               ("B5_OPEN_REAL", "B6_OPEN_SCRAMBLE"),
                               [("d_B5_minus_B6", "B5_OPEN_REAL", "B6_OPEN_SCRAMBLE")],
                               N_BOOTSTRAP, MASTER_SEED + 5)

    # POSITIVE CONTROL -- held-out sentence query, candidates {L, random other anchor}
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    sr_hits, sr_n = 0, 0
    for it in items[:min(300, n)]:
        L = it["L"]
        if it["sent_idx"] is None:
            continue
        other = anchors[int(rng_sr.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or _is_variant(other, L)):
            other = anchors[int(rng_sr.integers(len(anchors)))]
            tries += 1
        if other == L:
            continue
        q = context_vector_masked(sents[it["sent_idx"]], L)
        if float(np.linalg.norm(q)) < 1e-9:
            continue
        pick, _c = canonicalize_fast("__slot__", q, space, thresh=-1.0,
                                     eligible_mask=_mask_for(pos, len(anchors), (L, other)))
        sr_hits += int(pick == L)
        sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 6)
    print("[positive-control] SELF_RETRIEVAL=%.4f (floor %.2f, n=%d)"
          % (self_retrieval, SELF_RETRIEVAL_FLOOR, sr_n), flush=True)

    digests = {k: _digest(v) for k, v in correct.items()}
    dupes = [k for k in sorted(digests) if sorted(digests.values()).count(digests[k]) > 1]
    bs = paired_bootstrap(correct, STAGE_B_ARMS,
                          [("d_B1_minus_B2", "B1_ACCUM_REAL", "B2_ACCUM_SCRAMBLE"),
                           ("d_B1_minus_B3", "B1_ACCUM_REAL", "B3_FREQUENCY"),
                           ("d_B4_minus_B2", "B4_SENTENCE_REAL", "B2_ACCUM_SCRAMBLE")],
                          N_BOOTSTRAP, MASTER_SEED + 7, chance_arm="B1_ACCUM_REAL")

    verdict, notes = decide_stage_b(bs, self_retrieval, sr_n)
    out = {
        "verdict": verdict, "notes": notes, "n_items": n, "item_construction": item_diag,
        "graded_comparator": GRADED_COMPARATOR,
        "self_retrieval": {"acc": self_retrieval, "n": sr_n, "floor": SELF_RETRIEVAL_FLOOR,
                           "ok": self_retrieval >= SELF_RETRIEVAL_FLOOR},
        "twoafc": bs, "arm_digests": digests, "arms_bit_identical": dupes,
        "open_vocabulary_readout": {
            "note": "B5/B6 are the OPEN-VOCABULARY argmax the reading loop actually performs "
                    "(all %d anchors eligible). B5 hit@1 is the closest automated analogue of the "
                    "MEANINGFUL rate; B6 is its floor." % len(anchors),
            "n_anchors": len(anchors),
            "hit_at_1": open_bs["arm_acc_ci"], "delta": open_bs["deltas"],
            "tautology_rate": round(float(open_taut.mean()), 6),
            "n_tautology": int(open_taut.sum()),
            "example_picks": ["%s->%s" % (items[i]["L"], open_pick_real[i])
                              for i in range(min(25, n))],
            "example_gold_hits": ["%s->%s" % (items[i]["L"], open_pick_real[i])
                                  for i in range(n) if open_real_hit[i]][:20]},
        "diagnostics": dict(sorted(diag.items())),
        "elapsed_s": round(time.time() - t0, 2),
    }
    record_unit(output_dir, unit_key("stageB", "done"), {"verdict": verdict, "n_items": n})
    return out


def decide_stage_b(bs: dict, self_retrieval: float, sr_n: int) -> Tuple[str, List[str]]:
    acc = bs["arm_acc_ci"]["B1_ACCUM_REAL"]["acc"]
    d12 = bs["deltas"]["d_B1_minus_B2"]
    d13 = bs["deltas"]["d_B1_minus_B3"]
    dch = bs["deltas"]["d_B1_ACCUM_REAL_minus_CHANCE"]
    notes = ["B1=%.4f (chance 0.50) scramble_floor=%.4f frequency_floor=%.4f d(B1-B2)=%.4f "
             "CI=[%.4f,%.4f]" % (acc, bs["arm_acc_ci"]["B2_ACCUM_SCRAMBLE"]["acc"],
                                 bs["arm_acc_ci"]["B3_FREQUENCY"]["acc"], d12["delta"],
                                 d12["ci_lo"], d12["ci_hi"])]
    if sr_n < 30 or self_retrieval < SELF_RETRIEVAL_FLOOR:
        return "VOID_PLUMBING", notes + [
            "positive control SELF_RETRIEVAL=%.4f (n=%d) below the %.2f floor -- the space or the "
            "read-out is not functioning, so no quality claim is made either way"
            % (self_retrieval, sr_n, SELF_RETRIEVAL_FLOOR)]
    if acc < CHANCE and dch["ci_excludes_zero"]:
        return "HARD_FAIL_B_BELOW_CHANCE", notes
    if not dch["ci_excludes_zero"]:
        return "AT_CHANCE", notes + ["the read-out cannot pick the gold meaning over a "
                                     "frequency-matched foil better than a coin"]
    if acc >= HP_B_ACC and d12["ci_excludes_zero"] and d12["delta"] > 0 and d13["delta"] > 0:
        return "HARD_PASS_B", notes
    return "MIDDLE_BAND_B", notes + ["above chance but short of the %.2f band or a floor gate"
                                     % HP_B_ACC]


# ------------------------------------------------------------------ self-test
def self_test() -> dict:
    t0 = time.time()
    res: dict = {}
    exercised = set()

    for name, obj, kwargs in (
            ("context_vector_masked", context_vector_masked,
             {"sentence": "x", "target_lemma": "x"}),
            ("canonicalize_fast", canonicalize_fast,
             {"new_lemma": "x", "new_raw_sum": None, "space": None, "thresh": 0.0,
              "eligible_mask": None}),
            ("ConceptSpace.observe", ConceptSpace.observe, {"lemma": "x", "ctx_vec": None})):
        try:
            inspect.signature(obj).bind_partial(
                **({"self": None, **kwargs} if name.startswith("ConceptSpace.") else kwargs))
        except TypeError as e:
            raise AssertionError("substrate signature drift on %s: %s" % (name, e))
    res["substrate_signature_checked"] = ["context_vector_masked", "canonicalize_fast",
                                          "ConceptSpace.observe"]

    # S2 -- the GOLD SET fires where it must and does NOT fire where it must not.
    gdog = gold_meaning_set("dog")
    assert "canine" in gdog, "gold set misses the direct hypernym of dog"
    assert "puppy" in gdog, "gold set misses a hyponym of dog"
    assert "democracy" not in gdog, "gold set fires on an unrelated word"
    assert "dog" not in gdog and "dogs" not in gdog, "gold set contains the word itself"
    gcity = gold_meaning_set("city")
    assert "municipality" in gcity or "town" in gcity, "gold set misses city's neighbourhood"
    res["gold_set_selftest"] = {"dog_has_canine": True, "dog_has_puppy": True,
                                "dog_lacks_democracy": True, "n_gold_dog": len(gdog)}

    # S3 -- tautology detector fires on X->X and its morphology, and not otherwise.
    assert _is_tautology("dog", "dog") and _is_tautology("Dogs", "dog")
    assert not _is_tautology("dog", "canine")
    res["tautology_detector_ok"] = True

    # S4 -- REAL CODE PATH: a tiny ConceptSpace + the real read-out, and the read-out MOVES.
    sp = ConceptSpace(d=CTX_D)
    prof = {"poet": ["The poet wrote verses and published a book of poems every winter.",
                     "A famous poet read verses aloud at the library and the school."],
            "river": ["The river flows through the valley and past the bridge each spring.",
                      "Boats travel along the river between the town and the sea."]}
    for w, ss in prof.items():
        for s in ss:
            sp.observe(w, context_vector_masked(s, w))
    exercised.update({"ConceptSpace", "ConceptSpace.observe", "context_vector_masked"})
    anchors, mat = sp.anchor_matrix()
    assert anchors == ["poet", "river"], "anchor order drifted: %r" % anchors
    assert mat.shape == (2, CTX_D) and np.linalg.norm(mat, axis=1).min() > 0
    pos = {a: i for i, a in enumerate(anchors)}
    m = _mask_for(pos, 2, ("poet", "river"))
    q1 = context_vector_masked("She read verses from a book of poems at the library.", "__none__")
    q2 = context_vector_masked("Boats travel through the valley past the bridge to the sea.",
                               "__none__")
    p1, c1 = canonicalize_fast("__slot__", q1, sp, thresh=-1.0, eligible_mask=m)
    p2, c2 = canonicalize_fast("__slot__", q2, sp, thresh=-1.0, eligible_mask=m)
    exercised.add("canonicalize_fast")
    assert p1 != p2, ("READ-OUT CANNOT MOVE: two maximally different queries both picked %r -- the "
                      "discriminator would be analytically pinned" % p1)
    assert np.isfinite(c1) and np.isfinite(c2) and abs(c1) > 1e-9
    res["readout_moves"] = {"poetlike": p1, "riverlike": p2,
                            "cos": [round(float(c1), 4), round(float(c2), 4)]}

    # S5 -- bootstrap calibration: detects a real delta; null false-positive rate <= 1/6.
    rng = np.random.default_rng(3)
    base = rng.random(300) < 0.50
    better = base | (rng.random(300) < 0.30)
    bs = paired_bootstrap({"A1_REAL": better, "A2_SCRAMBLE": base, "A3_POPULARITY": base.copy()},
                          STAGE_A_ARMS, [("d_A1_minus_A2", "A1_REAL", "A2_SCRAMBLE")], 400, 7)
    assert bs["deltas"]["d_A1_minus_A2"]["ci_excludes_zero"], "bootstrap missed a real delta"
    fp = 0
    for s in range(6):
        r2 = np.random.default_rng(1000 + s)
        null = {k: (r2.random(800) < 0.50) for k in STAGE_A_ARMS}
        if paired_bootstrap(null, STAGE_A_ARMS, [("d_A1_minus_A2", "A1_REAL", "A2_SCRAMBLE")],
                            400, 7)["deltas"]["d_A1_minus_A2"]["ci_excludes_zero"]:
            fp += 1
    assert fp <= 1, "bootstrap false-positive rate too high: %d/6" % fp
    res["bootstrap_selftest"] = {"real_delta_detected": True, "null_false_positives": fp}

    # S6 -- every verdict branch of BOTH stages is reachable.
    def _a(hit, flo, pop, ex=True):
        d = hit - flo
        return {"X": {"gold_hit": {"A1_REAL": {"acc": hit}, "A2_SCRAMBLE": {"acc": flo},
                                   "A3_POPULARITY": {"acc": pop}},
                      "bootstrap": {"deltas": {"d_A1_minus_A2": {
                          "delta": d, "ci_lo": d - 0.01 if ex else -abs(d) - 0.01,
                          "ci_hi": d + 0.01, "ci_excludes_zero": ex}}}}}
    seen_a = sorted({decide_stage_a(_a(0.30, 0.05, 0.05))[0],
                     decide_stage_a(_a(0.07, 0.02, 0.02))[0],
                     decide_stage_a(_a(0.03, 0.03, 0.03, ex=False))[0],
                     decide_stage_a(_a(0.01, 0.09, 0.09))[0],
                     decide_stage_a({})[0]})
    want_a = sorted(["HARD_PASS_A", "SIGNAL_ABOVE_FLOOR", "AT_FLOOR", "HARD_FAIL_BELOW_FLOOR",
                     "NO_BANKED_DATA"])
    assert seen_a == want_a, "stage A branches unreachable: %r want %r" % (seen_a, want_a)

    def _b(acc, scr, freq, ex_ch=True, ex_12=True):
        d12, dch = acc - scr, acc - CHANCE
        return {"arm_acc_ci": {"B1_ACCUM_REAL": {"acc": acc}, "B2_ACCUM_SCRAMBLE": {"acc": scr},
                               "B3_FREQUENCY": {"acc": freq}},
                "deltas": {"d_B1_minus_B2": {"delta": d12, "ci_lo": d12 - 0.01 if ex_12 else -1.0,
                                             "ci_hi": d12 + 0.01, "ci_excludes_zero": ex_12},
                           "d_B1_minus_B3": {"delta": acc - freq},
                           "d_B1_ACCUM_REAL_minus_CHANCE": {
                               "delta": dch, "ci_lo": dch - 0.01 if ex_ch else -1.0,
                               "ci_hi": dch + 0.01, "ci_excludes_zero": ex_ch}}}
    seen_b = sorted({decide_stage_b(_b(0.70, 0.50, 0.52), 0.9, 100)[0],
                     decide_stage_b(_b(0.55, 0.50, 0.52), 0.9, 100)[0],
                     decide_stage_b(_b(0.50, 0.50, 0.50, ex_ch=False), 0.9, 100)[0],
                     decide_stage_b(_b(0.40, 0.50, 0.50), 0.9, 100)[0],
                     decide_stage_b(_b(0.70, 0.50, 0.52), 0.4, 100)[0]})
    want_b = sorted(["HARD_PASS_B", "MIDDLE_BAND_B", "AT_CHANCE", "HARD_FAIL_B_BELOW_CHANCE",
                     "VOID_PLUMBING"])
    assert seen_b == want_b, "stage B branches unreachable: %r want %r" % (seen_b, want_b)
    res["verdict_branches_reachable"] = {"stage_a": seen_a, "stage_b": seen_b}

    # S7 -- derangement is a real derangement with disjoint candidates.
    d = _derangement(20, lambda i, j: (j % 5) == (i % 5))
    assert all(d[i] != i for i in range(20)) and sorted(set(d)) == sorted(d)
    res["derangement_ok"] = True

    # S8 -- declared entrypoints were actually exercised here.
    missing = sorted({"ConceptSpace", "ConceptSpace.observe", "context_vector_masked",
                      "canonicalize_fast"} - exercised)
    assert not missing, "real_code_path: declared but NOT exercised: %r" % missing
    res["real_code_path_exercised"] = sorted(exercised)
    res["graded_comparator"] = GRADED_COMPARATOR
    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--stage", choices=["A", "B", "all"], default="all")
    ap.add_argument("--graded", default="1")          # consumed before hdlab import; see top
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return

    output_dir = _out_dir(args.mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.mode)
    t0 = time.time()
    try:
        a = stage_a(output_dir) if args.stage in ("A", "all") else None
        b = stage_b(args.mode, output_dir) if args.stage in ("B", "all") else None
        metrics = {
            "anchor_name": ANCHOR_NAME, "run_mode": args.mode, "prereg": PREREG_PATH,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "graded_comparator": GRADED_COMPARATOR,
            "HD_GRADED_COMPARATOR_env": os.environ.get("HD_GRADED_COMPARATOR"),
            "wire_status": "VET_PENDING",
            "verdict": "%s | %s" % (a["verdict"] if a else "STAGE_A_SKIPPED",
                                    b["verdict"] if b else "STAGE_B_SKIPPED"),
            "verdict_msg": " || ".join(
                ([("STAGE_A(banked known-answer): " + a["verdict"] + " -- " + "; ".join(a["notes"]))]
                 if a else []) +
                ([("STAGE_B(2AFC known-answer, chance 0.50): " + b["verdict"] + " -- "
                   + "; ".join(b["notes"]))] if b else [])),
            "stage_a": a, "stage_b": b,
            "revival_criterion": {
                "recorded": ">=%.2f MEANINGFUL against a recorded floor, tautologies <%.2f"
                            % (REVIVAL_MEANINGFUL_MIN, REVIVAL_TAUTOLOGY_MAX),
                "source": "notes/SUBSTRATE_STRATEGY.md PART 1 (C3)"},
            "config": {"CTX_D": CTX_D, "MIN_LEMMA_COUNT": MIN_LEMMA_COUNT,
                       "K_SENT_TOTAL": K_SENT_TOTAL, "N_PROFILE": N_PROFILE,
                       "FOIL_RATIO_BAND": list(FOIL_RATIO_BAND), "MAX_ITEMS": MAX_ITEMS,
                       "MIN_ITEMS": MIN_ITEMS, "N_BOOTSTRAP": N_BOOTSTRAP,
                       "MASTER_SEED": MASTER_SEED,
                       "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS")},
            "limitations": [
                "GOLD_HIT is a KNOWN-ANSWER PROXY for a human MEANINGFUL judgement, chosen because "
                "it has a floor and the hand-score does not. Convergence with the prior hand-score "
                "is evidence ABOUT THE PROXY, never a substitute for it.",
                "STAGE B is a 2-candidate forced choice; it licenses NO statement about the "
                "open-vocabulary argmax rate. Only STAGE A and the B5/B6 open-vocabulary block do.",
                "L's accumulated bundle may contain sentences where the gold word co-occurs. The "
                "leak is left IN on purpose (co-occurrence IS the mechanism) and biases TOWARDS "
                "the treatment, so a null is conservative.",
                "STAGE A re-scores facts banked 2026-08-12, BEFORE the HD_GRADED_COMPARATOR "
                "default flip. STAGE B's setting is reported in graded_comparator.",
            ],
            "elapsed_s": round(time.time() - t0, 2),
        }
        _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
        print(json.dumps({"verdict": metrics["verdict"], "verdict_msg": metrics["verdict_msg"]},
                         indent=2), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(output_dir, "_crash_diagnostic.json"),
                     {"anchor_name": ANCHOR_NAME, "run_mode": args.mode,
                      "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise


if __name__ == "__main__":
    main()
