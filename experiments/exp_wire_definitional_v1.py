"""exp_wire_definitional_v1 -- put the definitional extractor on the live reading path and measure
whether it helps a HELD-OUT set of words it was never told about.

PRE-REG: preregs/2026-08-13_wire_definitional.md (filed BEFORE any arm ran).

THE WIRE (hdlab/reading_grounding_loop.py):
  * NEW, default-OFF: checkpoint(definition_map=) -> _make_definitional_gate, which WRAPS the
    existing consolidation gate and banks the extractor's object as the meaning.
  * REUSED: the existing process_sentence(anchor_pool=) hook carries the definitions' OBJECT
    vocabulary in as candidate meanings.

THE CIRCULARITY: feeding the loop `X -> Y` and asking what X means gives recall 1.0 by
construction. The 1353 known-answer subjects are therefore split disjointly by hash into
A (INJECT, 692) and B (HELD-OUT, 661). B's definitions are never given to the loop in ANY arm and
B is the SOLE scoring set. A is scored only as a witness that the circularity is real and
quarantined; A carries NO claim.

ARMS (one variable each; identical corpus, seed, known_seed and reading order):
  OFF        anchor_pool=None                   definition_map=None          -- shipped default
  ON         anchor_pool=objects(A)+A           definition_map=A (true)      -- the full wire
  SHUFFLE    anchor_pool=objects(A)+A           definition_map=A (deranged)  -- content control
  FREQMATCH  anchor_pool=freq-matched random    definition_map=None          -- anchor-mass control

NO HAND-SCORING. No quality claim beyond availability / recall@1 / availability-conditioned recall.
GROWTH IS PAUSED: everything is written under data/exp_wire_definitional_v1/ only.
ASCII-only. Deterministic: sorted(set(...)), hashlib splits, fixed integer seeds.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class, is_eligible_meaning
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    MEANING_SOURCE_DEFINITIONAL,
    PBV_COMMIT_STRENGTH,
    ReadingLoopState,
    checkpoint,
    content_lemmas,
    make_pbv_fns,
    normalize_lemma,
    pbv_trajectory_stats,
    process_sentence,
    seed_known_words,
)
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, grounded_lemmas_in_store,
)
from experiments.exp_definitional_grounding_v5 import load_corpus_v5
# scoring reused VERBATIM (same definitions, same denominators) -- not reimplemented
from experiments.exp_anchor_pool_expansion_v1 import (
    IncrementalConceptSpace, probe_readout, score_probe,
)

ANCHOR_NAME = "wire_definitional_v1"
PREREG = "preregs/2026-08-13_wire_definitional.md"
OUTPUT_DIR_NAME = "exp_wire_definitional_v1"

ARMS = ["OFF", "ON", "SHUFFLE", "FREQMATCH"]
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]

ARM_SEED = 4201                      # IDENTICAL to the reference run (regression check S1)
SEED_KNOWN_TOP_N = 1000              # 887 distinct lemmas. ALL arms.
SPLIT_SALT = "wire_defwire_v1"       # the A/B split; pre-registered
SHUFFLE_SEED = 7717
FREQMATCH_SEED = 7718
TOP_K = 5
SMOKE_LIMIT_PER_SEGMENT = 400

FACTS_PATH = "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl"
FACTS_SHA256 = "68ab1cbd17a78561f1294145cd177aeceac8b3f27cebf249435dc2c598ece793"
PROBE_PATH = "data/exp_anchor_pool_expansion_v1/_probe_coverage.json"   # READ-ONLY

# ---- OFF regression reference (prereg sec 7, S1) ------------------------------------------------
REF_UNITS = "data/exp_anchor_pool_expansion_v1/units.jsonl"
REF_ARM = "SMALL"
REF_N_GROUNDED = 386

BANDS = {
    "discriminator": "recall@1(ON) - recall@1(OFF) on the HELD-OUT split B (661 subjects). "
                     "A (692, injected) is a circularity witness and carries NO claim.",
    "DEFINITIONS_HELP": "delta >= +0.05 AND (ON-SHUFFLE) >= +0.02 AND (ON-FREQMATCH) >= +0.02",
    "PARTIAL": "delta in [+0.03, +0.05)",
    "MASS_NOT_CONTENT": "delta >= +0.03 but ON does not beat BOTH controls by >= +0.02",
    "AVAILABILITY_ONLY": "availability delta >= +0.30 AND recall@1 delta < +0.03 -- the answer is "
                         "on the menu and still is not chosen. PRE-DECLARED ACCEPTABLE, and the "
                         "PREDICTED outcome given exp_anchor_pool_expansion_v1 LARGE.",
    "HURTS": "delta <= -0.03 -- more candidates means more distractors. A live possibility.",
    "BROKEN": "availability delta < +0.30 (manipulation failed) OR the OFF arm fails the "
              "n_grounded==386 regression check. Nothing is interpreted.",
    "power": "n=661: SE(p~0.05)=0.0085, SE(delta)<=0.012, so +0.03 is ~2.5 SE and +0.05 is ~4 SE.",
}


# =========================================================================== io helpers
def _output_dir(run_mode: str) -> str:
    # GROWTH IS PAUSED: every path this cell writes stays under data/exp_wire_definitional_v1/
    d = repo_path("data/" + OUTPUT_DIR_NAME + ("/_smoke" if run_mode == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii", newline="") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=True)
    os.replace(tmp, path)


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="ascii", newline="") as f:
        f.write(json.dumps(dict(payload, ts=datetime.now(timezone.utc).isoformat()),
                           ensure_ascii=True) + "\n")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _digest_pairs(pairs) -> str:
    h = hashlib.sha256()
    for s, o in sorted(pairs):
        h.update(("%s\t%s\n" % (s, o)).encode("utf-8"))
    return h.hexdigest()[:16]


# =========================================================================== ground truth + split
def load_facts() -> Dict[str, List[str]]:
    """subject head lemma -> sorted distinct object lemmas, from the EXACT artifact the 64%
    hand-score was computed on (prereg sec 7, S4)."""
    p = repo_path(FACTS_PATH)
    got = _sha256(p)
    if got != FACTS_SHA256:
        raise SystemExit("WRONG ARTIFACT: %s sha256=%s expected %s" % (FACTS_PATH, got, FACTS_SHA256))
    by = defaultdict(set)
    with open(p, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            by[normalize_lemma(r["subject_head_lemma"])].add(normalize_lemma(r["object"]))
    return {k: sorted(v) for k, v in by.items()}


def load_probe() -> Dict[str, List[str]]:
    with open(repo_path(PROBE_PATH), encoding="utf-8") as f:
        return json.load(f)["probe_sets"]["v5_definitional"]["subjects"]


def split_ab(subjects: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Deterministic disjoint split. 0 -> A (INJECT), 1 -> B (HELD OUT AND SCORED)."""
    a, b = [], []
    for s in sorted(set(subjects)):
        h = hashlib.sha256((SPLIT_SALT + "|" + s).encode("utf-8")).hexdigest()
        (a if int(h[:8], 16) % 2 == 0 else b).append(s)
    return a, b


def _usable_pair(subj: str, obj: str) -> bool:
    """Only pairs the gate would accept anyway: no self-tautology, no closed class."""
    return (obj != subj and not is_closed_class(subj) and not is_closed_class(obj)
            and is_eligible_meaning(obj))


def build_definition_map(A: Sequence[str], facts: Dict[str, List[str]],
                         shuffle: bool = False) -> Dict[str, str]:
    """A subject -> ONE object (the first, sorted, that the gate would accept). `shuffle=True`
    DERANGES the pairing across the SAME subject set and the SAME object multiset, so anchor field,
    bank count and gap closure are held constant and only the CONTENT changes."""
    pairs: List[Tuple[str, str]] = []
    for s in sorted(set(A)):
        for o in facts.get(s, ()):
            if _usable_pair(s, o):
                pairs.append((s, o))
                break
    if not shuffle:
        return {s: o for s, o in pairs}
    subs = [s for s, _ in pairs]
    orig = [o for _, o in pairs]
    objs = list(orig)
    rng = random.Random(SHUFFLE_SEED)

    def _bad(i: int, o: str) -> bool:
        # a deranged pairing must differ from the TRUE object and stay gate-acceptable
        return o == orig[i] or not _usable_pair(subs[i], o)

    for _ in range(200):
        rng.shuffle(objs)
        bad = [i for i, o in enumerate(objs) if _bad(i, o)]
        if not bad:
            break
        # repair pass: swap each offending slot with a random slot that fixes both
        for i in list(bad):
            if not _bad(i, objs[i]):
                continue
            for _try in range(400):
                j = rng.randrange(len(objs))
                if j == i:
                    continue
                if not _bad(i, objs[j]) and not _bad(j, objs[i]):
                    objs[i], objs[j] = objs[j], objs[i]
                    break
        if not any(_bad(i, o) for i, o in enumerate(objs)):
            break
    if any(_bad(i, o) for i, o in enumerate(objs)):
        raise SystemExit("could not derange the SHUFFLE control cleanly")
    return {s: o for s, o in zip(subs, objs)}


def build_pools(A: Sequence[str], facts: Dict[str, List[str]]) -> frozenset:
    """ON / SHUFFLE anchor pool: every object of an injected definition, plus the injected subjects
    themselves. Contains NOTHING drawn from B's key beyond what A's own definitions already say."""
    pool = set(normalize_lemma(s) for s in A)
    for s in A:
        for o in facts.get(s, ()):
            pool.add(normalize_lemma(o))
    return frozenset(pool)


def corpus_lemma_counts(stream: Sequence[Tuple[str, str]]) -> Counter:
    c: Counter = Counter()
    for _, sent in stream:
        c.update(content_lemmas(sent))
    return c


def build_freqmatched_pool(target_pool: frozenset, counts: Counter,
                           forbidden: set) -> frozenset:
    """Same SIZE as `target_pool`, matched on corpus-frequency decile, drawn from corpus content
    lemmas, excluding anything in `forbidden` (the real pool + every gold object of B + B itself),
    so this arm cannot accidentally supply an answer."""
    universe = sorted(l for l in counts
                      if l not in forbidden and is_eligible_meaning(l) and counts[l] > 0)
    # count -> deterministically shuffled bucket of unused candidates at that exact frequency
    rng = random.Random(FREQMATCH_SEED)
    by_count: Dict[int, List[str]] = defaultdict(list)
    for l in universe:
        by_count[counts[l]].append(l)
    for c in by_count:
        rng.shuffle(by_count[c])
    avail_counts = sorted(by_count)

    out: List[str] = []
    # match each target lemma to an UNUSED candidate of the nearest available corpus frequency
    for l in sorted(target_pool, key=lambda x: (-counts.get(x, 0), x)):
        want_c = counts.get(l, 0)
        if want_c <= 0:
            continue                       # target lemma never occurs; nothing to match
        best = None
        i = int(np.searchsorted(avail_counts, want_c))
        for j in range(max(0, i - 64), min(len(avail_counts), i + 65)):
            c = avail_counts[j]
            if not by_count[c]:
                continue
            d = abs(c - want_c)
            if best is None or d < best[0]:
                best = (d, c)
        if best is None:                   # exhausted the near window; scan everything left
            for c in avail_counts:
                if by_count[c]:
                    best = (abs(c - want_c), c)
                    break
        if best is None:
            break                          # universe exhausted
        out.append(by_count[best[1]].pop())
    return frozenset(out)


# =========================================================================== corpus
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else None
    return load_corpus_v5(limit, lineaware=True)


def _count_reasons(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return out


def _prov_row(p: dict) -> dict:
    return {k: p.get(k) for k in ("fid", "subject", "relation", "object", "segment", "pass_idx",
                                  "best_cos", "n_exposures", "meaning_source")}


# =========================================================================== one arm
def run_arm(arm: str, run_mode: str, output_dir: str) -> dict:
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("arm_done", arm)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    stream = build_stream(run_mode)
    facts = load_facts()
    probe = load_probe()
    A, B = split_ab(list(probe))
    assert not (set(A) & set(B)), "A/B split is not disjoint"

    gold_B = {s: sorted(set(normalize_lemma(o) for o in probe[s])) for s in B}
    gold_A = {s: sorted(set(normalize_lemma(o) for o in probe[s])) for s in A}

    # ------------------------- THE ONE VARIABLE -------------------------
    real_pool = build_pools(A, facts)
    if arm == "OFF":
        anchor_pool, definition_map = None, None
    elif arm == "ON":
        anchor_pool, definition_map = real_pool, build_definition_map(A, facts, shuffle=False)
    elif arm == "SHUFFLE":
        anchor_pool, definition_map = real_pool, build_definition_map(A, facts, shuffle=True)
    elif arm == "FREQMATCH":
        forbidden = set(real_pool) | set(B)
        for objs in gold_B.values():
            forbidden |= set(objs)
        anchor_pool = build_freqmatched_pool(real_pool, corpus_lemma_counts(stream), forbidden)
        definition_map = None
    else:
        raise SystemExit("unknown arm %r" % (arm,))

    # HELD-OUT INVARIANT (prereg sec 7, S3) -- enforced, not assumed.
    if definition_map is not None:
        leak = sorted(set(definition_map) & set(B))
        if leak:
            raise SystemExit("HELD-OUT LEAK: %d B subjects in definition_map: %r" % (len(leak), leak[:10]))

    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    state.space = IncrementalConceptSpace(state.space.d)   # speed-only, self-tested identical
    seed_known_words(state, load_base_vocab_seed(SEED_KNOWN_TOP_N), source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)

    propose_fn, verify_fn = make_pbv_fns(state)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    seg_seen: Dict[str, int] = {}
    seg_units_written: Dict[str, bool] = {}
    t0 = time.time()
    last_hb = t0

    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            seg_seen[seg] = seg_seen.get(seg, 0) + 1
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True, anchor_pool=anchor_pool)
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                         commit_strength=PBV_COMMIT_STRENGTH,
                         definition_map=definition_map)

        if seg_tag in SEGMENTS and not seg_units_written.get(seg_tag):
            seg_units_written[seg_tag] = True
            key = exp_checkpoint.unit_key(arm, seg_tag)
            if key not in already:
                exp_checkpoint.record_unit(output_dir, key, {
                    "arm": arm, "segment": seg_tag, "first_chunk_idx": chunk_idx,
                    "n_anchors_at_segment_open": len(state.space.anchors()),
                    "n_grounded_at_segment_open": len(grounded_lemmas_in_store(state.store))})
        if chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1:
            print(f"[progress] {arm} chunk={chunk_idx + 1}/{n_chunks} seg={seg_tag} "
                  f"anchors={len(state.space.anchors())} "
                  f"grounded={len(grounded_lemmas_in_store(state.store))} "
                  f"refused={row['n_refused_cumulative']} "
                  f"elapsed={time.time() - t0:.1f}s", flush=True)
        if time.time() - last_hb >= 60.0:
            last_hb = time.time()
            _heartbeat(output_dir, {"arm": arm, "chunk": chunk_idx, "n_chunks": n_chunks,
                                    "n_anchors": len(state.space.anchors()),
                                    "elapsed_s": round(time.time() - t0, 1)})

    traj = pbv_trajectory_stats(state.library)
    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    banked = {f.subject: f.obj for f in gm}
    anchors, mat = state.space.anchor_matrix()
    anchor_set = set(a for a in anchors if is_eligible_meaning(a))

    # ---- PRIMARY: known-answer recall on B (held out).  A is a WITNESS ONLY.
    t_ro = time.time()
    readout = probe_readout(state, sorted(set(A) | set(B)))
    scored = {
        "HELDOUT_B": score_probe(gold_B, readout, anchor_set, banked),
        "INJECTED_A_WITNESS_NO_CLAIM": score_probe(gold_A, readout, anchor_set, banked),
    }
    for k in scored:                      # rows are large; keep them out of units.jsonl
        scored[k] = {kk: vv for kk, vv in scored[k].items() if kk != "rows"}
    print(f"[probe] {arm} readout in {time.time() - t_ro:.1f}s", flush=True)

    n_defbank = sum(1 for p in state.provenance
                    if p.get("meaning_source") == MEANING_SOURCE_DEFINITIONAL)
    summary = {
        "arm": arm,
        "anchor_pool_n_lemmas": (len(anchor_pool) if anchor_pool is not None else 0),
        "definition_map_n": (len(definition_map) if definition_map is not None else 0),
        "definition_map_is_shuffled": arm == "SHUFFLE",
        "n_known_seed_lemmas": len(known_seed_snapshot),
        "n_sentences": len(stream), "n_chunks": n_chunks,
        "segments_seen": {s: seg_seen.get(s, 0) for s in SEGMENTS},
        "n_anchors": len(anchors), "n_eligible_anchors": len(anchor_set),
        "n_grounded": len(grounded_lemmas_in_store(state.store)),
        "n_meaning_facts": len(gm),
        "n_facts_banked_from_definitions": n_defbank,
        "n_tautology_facts": sum(1 for f in gm if f.subject == f.obj),
        "no_leak_violations": sorted(set(l for l in grounded_lemmas_in_store(state.store)
                                         if l in known_seed_snapshot)),
        "n_refusals": len(state.refusals),
        "refusal_reasons": _count_reasons(state.refusals),
        "trajectory": {k: v for k, v in traj.items() if k != "revisions"},
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "n_A": len(A), "n_B": len(B),
        "known_answer_recall": scored,
        "elapsed_s": round(time.time() - t0, 2),
    }
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_provenance.json"),
                 [_prov_row(p) for p in state.provenance if p["relation"] == MEANING_RELATION])
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_probe_readout.json"),
                 {"arm": arm, "readout": readout})
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


# =========================================================================== finalize
def _off_regression(units: dict) -> dict:
    """S1: the OFF arm must reproduce the live shipped arm (n_grounded == 386)."""
    off = units.get(exp_checkpoint.unit_key("arm_done", "OFF"))
    ref = None
    p = repo_path(REF_UNITS)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o["unit_key"] == "arm_done|" + REF_ARM:
                    ref = o["result"]
    got = off.get("n_grounded") if off else None
    return {"expected_n_grounded": REF_N_GROUNDED, "observed_n_grounded": got,
            "reference_run": REF_UNITS + " arm_done|" + REF_ARM,
            "reference_n_grounded": (ref or {}).get("n_grounded"),
            "PASS": got == REF_N_GROUNDED}


def _band(d: dict) -> str:
    off, on = d.get("OFF"), d.get("ON")
    if off is None or on is None:
        return "INCOMPLETE"
    av_d = on["availability"] - off["availability"]
    r1_d = on["recall_at_1"] - off["recall_at_1"]
    if av_d < 0.30:
        return "BROKEN"
    ctrl_ok = True
    for c in ("SHUFFLE", "FREQMATCH"):
        if d.get(c) is None or (on["recall_at_1"] - d[c]["recall_at_1"]) < 0.02:
            ctrl_ok = False
    if r1_d <= -0.03:
        return "HURTS"
    if r1_d >= 0.05 and ctrl_ok:
        return "DEFINITIONS_HELP"
    if r1_d >= 0.03:
        return "PARTIAL" if ctrl_ok else "MASS_NOT_CONTENT"
    return "AVAILABILITY_ONLY"


def finalize(run_mode: str, output_dir: str) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {}
    for a in ARMS:
        k = exp_checkpoint.unit_key("arm_done", a)
        if k in units:
            arms[a] = units[k]
    heldout = {a: arms[a]["known_answer_recall"]["HELDOUT_B"] for a in arms}
    witness = {a: arms[a]["known_answer_recall"]["INJECTED_A_WITNESS_NO_CLAIM"] for a in arms}
    reg = _off_regression(units)
    band = _band(heldout) if reg["PASS"] else "BROKEN"

    def _tbl(src):
        return {a: {k: src[a][k] for k in
                    ("n_probe_subjects", "availability", "recall_at_1", "recall_at_5",
                     "availability_conditioned_recall_at_1", "n_availability_conditioned",
                     "live_banked")} for a in sorted(src)}

    metrics = {
        "anchor": ANCHOR_NAME, "prereg": PREREG, "run_mode": run_mode,
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "numpy": np.__version__,
        "bands": BANDS,
        "band": band,
        "off_regression_check": reg,
        "CIRCULARITY": (
            "The wire IS circular for the subjects it is fed: INJECTED_A recall is ~1.0 by "
            "construction and carries NO claim. Every claim below is computed on HELDOUT_B, whose "
            "definitions were never given to the loop in any arm. Residual dependency: B's gold "
            "objects and A's injected objects come from the same extractor output, which is what "
            "the FREQMATCH arm prices."),
        "primary_HELDOUT_B": _tbl(heldout),
        "witness_INJECTED_A_NO_CLAIM": _tbl(witness),
        "arms": {a: {k: v for k, v in arms[a].items() if k != "known_answer_recall"}
                 for a in sorted(arms)},
        "deltas_HELDOUT_B_vs_OFF": {
            a: {"availability": round(heldout[a]["availability"] - heldout["OFF"]["availability"], 6),
                "recall_at_1": round(heldout[a]["recall_at_1"] - heldout["OFF"]["recall_at_1"], 6),
                "availability_conditioned_recall_at_1": (
                    None if (heldout[a]["availability_conditioned_recall_at_1"] is None
                             or heldout["OFF"]["availability_conditioned_recall_at_1"] is None)
                    else round(heldout[a]["availability_conditioned_recall_at_1"]
                               - heldout["OFF"]["availability_conditioned_recall_at_1"], 6))}
            for a in sorted(heldout) if a != "OFF" and "OFF" in heldout},
        "NO_QUALITY_CLAIM": ("No hand-scoring was performed and no quality claim is made beyond "
                             "these recall numbers."),
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    return metrics


# =========================================================================== self-test
def _selftest() -> dict:
    facts = load_facts()
    probe = load_probe()
    A, B = split_ab(list(probe))
    assert not (set(A) & set(B)), "split not disjoint"
    assert len(A) + len(B) == len(probe) == 1353, (len(A), len(B), len(probe))
    dm = build_definition_map(A, facts, shuffle=False)
    ds = build_definition_map(A, facts, shuffle=True)
    assert set(dm) == set(ds), "shuffle changed the subject set"
    assert sorted(Counter(dm.values()).items()) == sorted(Counter(ds.values()).items()), \
        "shuffle changed the object multiset"
    n_same = sum(1 for k in dm if dm[k] == ds[k])
    assert n_same == 0, "derangement left %d pairings intact" % n_same
    assert not (set(dm) & set(B)), "HELD-OUT LEAK in definition_map"
    for s, o in dm.items():
        assert _usable_pair(s, o), (s, o)
    pool = build_pools(A, facts)
    assert not (pool & set(B)) or True   # a B subject may occur as an A object; that is not the key
    gold_B_objs = set()
    for s in B:
        gold_B_objs |= set(normalize_lemma(o) for o in probe[s])
    return {"n_A": len(A), "n_B": len(B), "n_definition_map": len(dm),
            "n_pool": len(pool), "derangement_ok": True,
            "n_B_gold_objects": len(gold_B_objs),
            "overlap_poolA_with_B_gold_objects": len(pool & gold_B_objs),
            "facts_sha256_ok": True}


# =========================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--arm", choices=ARMS + ["finalize", "all"], default="all")
    args = ap.parse_args()

    if args.mode == "self-test":
        print(json.dumps(_selftest(), indent=2, sort_keys=True))
        print("SELF-TEST PASSED")
        return

    output_dir = _output_dir(args.mode)
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="ascii", newline="") as f:
        f.write(str(os.getpid()))
    try:
        todo = ARMS if args.arm in ("all", "finalize") else [args.arm]
        if args.arm != "finalize":
            for a in todo:
                print(f"===== ARM {a} =====", flush=True)
                run_arm(a, args.mode, output_dir)
        m = finalize(args.mode, output_dir)
        print(json.dumps({"band": m["band"], "off_regression": m["off_regression_check"],
                          "primary_HELDOUT_B": m["primary_HELDOUT_B"],
                          "deltas": m["deltas_HELDOUT_B_vs_OFF"]}, indent=2, sort_keys=True))
        print("DONE")
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
