# CELL-TEMPLATE (measurement-probe; NOT a dispatch/pipeline cell -- runs once, locally, to
# completion, then STOP+report per Director's spawn contract. Lighter than a queue-dispatch
# cell (no smoke/full escalation, no remote ship), but still applies the load-bearing subset:
# - no bare except / no except BaseException (except SystemExit/KeyboardInterrupt: raise, then
#   except Exception -> crash-diagnostic -> re-raise)
# - final_metrics_atomicity: tmp_replace (os.replace at the end)
# - deterministic_seeding: true (hashlib-seeded permutation reused verbatim from
#   exp_propara_decisive_inference_arm1_oracle_v1._det_seed/_deterministic_perm; F.5-compliant,
#   no hash()/list(set()) ordering)
# - self-test constructs REAL WordNet + REAL ConceptNet-index-scan (capped line count) + a REAL
#   tiny gam fit/predict at N~12 paragraphs; ONLY the embedding KV is mocked in self-test
#   (115s to load the real 400k-vocab GloVe offline -- same mock-KV precedent already
#   established in experiments/exp_encoder_word2vec_substrate_bind_v1.py's own self-test, "T7:
#   pretrained arm with TINY synthetic KV (no network)")
# - arms_differ: majority baseline vs each source's real/scramble predictions hash-compared;
#   soft-logged (not hard-crash) since incidental ties at a floor-collapsed scramble are
#   legitimate, but a total collapse (ALL 6 non-majority arms identical to majority) hard-fails
#   as a pipeline bug
# - crlb_n/a: pair-level P/R/F1 vs a majority baseline over a fixed real corpus (ProPara
#   EMNLP18 TRAIN/DEV); no noise-floor threshold applies to this measurement
# See preregs/2026-08-11_propara_entity_fate_external_knowledge_probe_v1.md for the full pre-reg
# (PASS/FAIL bands, per-source verdict logic).
"""exp_propara_entity_fate_external_knowledge_probe_v1 -- DECISIVE MEASUREMENT (not a pipeline
build): does ANY accessible EXTERNAL knowledge source supply the entity-level process-role
grounding that a learned glass-box binder HARD_FAILED to learn from coarse WordNet supersense
(exp_propara_schema_learned_grounded_binder_v1, HARD_FAIL_LEARNED_BINDER_DOES_NOT_BEAT_
PROMISCUOUS: heldout_surface learned_unseen pair_f1=0.0, n=29 unseen participants -- the binder
MEMORIZED, it did not generalize) -- in a way that GENERALIZES to entities whose SURFACE STRING
was never seen at fit time?

THE QUESTION (verbatim from the decisive-probe spawn): for ProPara (participant, process) pairs
with gold fates (CREATE/MOVE/DESTROY, from the SAME oracle event-multiset every prior arm uses --
experiments.exp_propara_decisive_inference_arm1_oracle_v1._oracle_event_multiset +
exp_propara_schema_learned_grounded_binder_v1._gold_effects_from_multiset, reused verbatim, NO
gold ever touches DEV features/labels), can an EXTERNAL knowledge source predict entity fate, and
does that prediction survive the EXACT held-out-surface control that killed the learned binder
(exp_propara_schema_learned_grounded_binder_v1._seen_surface_tokens /
_is_unseen_surface, reused verbatim -- 29/175 DEV participants are surface-unseen at TRAIN)?

SOURCES TESTED (each independently, own arm, own scramble control -- NOT aggregated):
  1. WORDNET-RICH: full hypernym-chain (depth<=6) + meronym/holonym + topic/usage-domain +
     lexname tokens on the participant head (owned nltk.wordnet access, SAME corpus
     hdlab.animacy_lexicon + the binder's _wn_lexname use -- but richer than the binder's
     flat top-lexname-only feature, which is what made wood/oxygen/ash collapse to the same
     noun.substance bucket).
  2. CONCEPTNET-RICH: typed KEEP_RELS edges (PartOf/MadeOf/HasA/UsedFor/IsA/CapableOf/
     HasProperty/AtLocation/Causes/... -- the full relation set from
     tools/benchmark_trap_check/build_propara_conceptnet_index_v1.py, NOT the narrower
     CO_PART_RELS subset the coparticipation cell used) on the participant head, sourced from
     the SAME local ConceptNet 5.7.0 assertions dump already ingested for this project
     (data/conceptnet/conceptnet-assertions-5.7.0.csv.gz). NOTE: the EXISTING scoped index
     (data/benchmark_trap_check/propara_conceptnet_index_v1.json) was built over DEV+TEST
     vocabulary only (see tools/benchmark_trap_check/build_propara_conceptnet_index_v1.py
     build_vocab(): `for split in ("dev", "test")`) -- TRAIN participant heads are almost all
     MISSING from it (checked: wood/ash/lava/log all absent). Fitting on TRAIN would starve the
     gam of ConceptNet signal entirely. This cell builds a SEPARATE TRAIN+DEV-scoped index
     (_build_cn_index_traindev / _load_or_build_cn_index_traindev, cached to
     data/benchmark_trap_check/propara_conceptnet_index_traindev_v1.json) by re-scanning the
     SAME local gz with the SAME KEEP_RELS/_cn_term/_toks/_singularize helpers (imported from
     the existing build script, not reimplemented) -- TEST stays untouched (no split/leak
     changes to the reader pipeline's own TEST discipline).
  3. EMBEDDING-RICH: offline GloVe-300d (gensim-cached, data/gensim_cache/glove-wiki-gigaword-
     300, no network) cosine similarity from the participant-head centroid to 3 hand-picked
     anchor-word centroids (CREATE/MOVE/DESTROY -- e.g. create/form/produce/grow/generate/
     emerge), bucketed. Reuses experiments.exp_encoder_word2vec_substrate_bind_v1._load_gensim_kv
     verbatim (same offline-cache loader already used for the K2 x cfrpe compose arm).

METHOD: ONE clean split for all 3 sources -- fit on TRAIN (391 paragraphs, 1500 (para,
participant) keys), evaluate on DEV (43 paragraphs, 175 keys, 29 surface-unseen) -- reused
verbatim from the schema binder's own TRAIN->DEV convention (avoids peeking at TEST, matches
"Modes: --self-test / --smoke (DEV) / --full (TEST); this build STOPS at smoke" project-wide
discipline). Per source: build ONE glass-box gam instance per (para, participant, candidate
effect in {CREATE, MOVE, DESTROY}) with features = [f"effect:{E}"] + source_features(participant
head tokens) (reused: experiments.exp_propara_schema_learned_grounded_binder_v1.
_participant_head_tokens) -- NO raw surface-identity feature is ever included (unlike the
binder's "surf:" memorization channel), so ANY held-out signal can ONLY come from the KB content
itself, not from memorized entity strings. Reuses hdlab.learner.plugins.gam_plugin (additive
log-odds + MDL-gated pairwise interactions) verbatim -- SAME learner the binder used, so a
positive result here directly implicates KNOWLEDGE SOURCING (not the learner) as the missing
piece, and a negative result directly implicates the SOURCE (not the learner).

CONTROLS (per source): (a) MAJORITY baseline -- constant "always predict the single most
TRAIN-frequent effect" (ignores entity identity entirely; a real, non-degenerate baseline,
pair_f1 ~0.40 on all-DEV, computed once, shared reference for all 3 sources). (b) SCRAMBLE --
deterministically (F.5-compliant, hashlib-seeded, no python hash()) permute the TRAIN
entity->fate mapping before fitting; the source's fit must NOT beat majority on held-out-unseen
after scrambling, or its "signal" is spurious/leaky, not real KB content.

VERDICT (per source, HP_SCOPE): HARD_PASS_GENERALIZES iff (real_unseen_pair_f1 -
majority_unseen_pair_f1) >= LIFT_HARD_PASS AND scramble_unseen_pair_f1 <= majority_unseen_pair_f1
+ SCRAMBLE_CLEAN_MARGIN. HARD_FAIL_NO_GENERALIZATION iff lift < LIFT_HARD_FAIL.
HARD_FAIL_SCRAMBLE_LEAK iff scramble not clean regardless of lift. Else MIDDLE_BAND. OVERALL:
HARD_PASS if >=1 source HARD_PASS_GENERALIZES (knowledge foundation is externally buildable);
HARD_FAIL if ALL 3 sources HARD_FAIL (entity-role knowledge is not in these accessible
structured sources at this coverage -- corpus-scale distributional learning or LLM-scale is
needed); else MIDDLE_BAND (report per-source honestly, no aggregation).

Modes: --self-test only (fast, mocked embedding KV, capped ConceptNet scan, tiny gam fit). No
mode flag = the REAL probe, foreground-to-completion (est. ~5min: ConceptNet full-vocab gz scan
~1-3min one-time cached + GloVe cold load ~115s + 6 fast gam fits).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                        "data", "gensim_cache"))

import argparse
import functools
import gzip
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

ANCHOR_NAME = "propara_entity_fate_external_knowledge_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CN_GZ = os.path.join(REPO_ROOT, "data", "conceptnet", "conceptnet-assertions-5.7.0.csv.gz")
CN_INDEX_TRAINDEV_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check",
                                       "propara_conceptnet_index_traindev_v1.json")

from hdlab.learner.plugins import gam_plugin  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _det_seed, _deterministic_perm,
)
from experiments.exp_propara_schema_learned_grounded_binder_v1 import (  # noqa: E402
    _gold_effects_from_multiset, _participant_head_tokens, _seen_surface_tokens, _is_unseen_surface,
)
from propara_trap_check import build_step_rows  # noqa: E402
from experiments.exp_encoder_word2vec_substrate_bind_v1 import _load_gensim_kv  # noqa: E402
import build_propara_conceptnet_index_v1 as _cn_builder  # noqa: E402

EFFECTS = ("CREATE", "MOVE", "DESTROY")
GENSIM_MODEL = "glove-wiki-gigaword-300"

# ============================================================================ pre-registered bands
LIFT_HARD_PASS = 0.05          # real_unseen_f1 - majority_unseen_f1 >= this -> meaningful generalization
LIFT_HARD_FAIL = 0.02          # below this -> no meaningful lift
SCRAMBLE_CLEAN_MARGIN = 0.05   # scramble_unseen_f1 must not exceed majority_unseen_f1 by more than this


# ============================================================================ source 1: WordNet-rich
@functools.lru_cache(maxsize=8192)
def _wn_rich_feats(word: str) -> Tuple[str, ...]:
    """Full hypernym chain (depth<=6) + meronym/holonym + topic/usage domain + lexname. Richer
    than the binder's flat top-lexname-only feature (the thing that collapsed wood/oxygen/ash to
    the same noun.substance bucket)."""
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(word, pos="n")
    except Exception:  # noqa: BLE001 -- optional grounded feature; absent-on-failure, never phantom
        return tuple()
    if not syns:
        return tuple()
    s0 = syns[0]
    feats = [f"lex:{s0.lexname()}"]
    seen = {s0.name()}
    frontier = [s0]
    depth = 0
    while frontier and depth < 6:
        nxt = []
        for s in frontier:
            for h in s.hypernyms():
                if h.name() not in seen:
                    seen.add(h.name())
                    feats.append(f"hyper:{h.name()}")
                    nxt.append(h)
        frontier = nxt
        depth += 1
    for m in (s0.part_meronyms() + s0.substance_meronyms() + s0.member_meronyms()):
        feats.append(f"mero:{m.name()}")
    for h in (s0.part_holonyms() + s0.substance_holonyms() + s0.member_holonyms()):
        feats.append(f"holo:{h.name()}")
    for d in (s0.topic_domains() + s0.usage_domains()):
        feats.append(f"dom:{d.name()}")
    return tuple(feats)


def _wn_source_feats(participant: str) -> List[str]:
    out: Set[str] = set()
    for t in _participant_head_tokens(participant):
        out.update(_wn_rich_feats(t))
    return sorted(out)


# ============================================================================ source 2: ConceptNet-rich
def _propara_vocab(paragraphs: List[Dict]) -> Set[str]:
    vocab: Set[str] = set()
    for p in paragraphs:
        for part in p["participants"]:
            for t in _cn_builder._toks(part):
                vocab.add(t)
                vocab.add(_cn_builder._singularize(t))
        for s in p["sentence_texts"]:
            for t in _cn_builder._toks(s):
                vocab.add(t)
                vocab.add(_cn_builder._singularize(t))
    return vocab


def _build_cn_index_traindev(vocab: Set[str], max_lines: Optional[int] = None) -> Dict:
    """Re-scan the SAME local ConceptNet 5.7.0 gz with the EXISTING build script's helpers
    (KEEP_RELS/_cn_term/_toks/_singularize, imported not reimplemented), scoped to TRAIN+DEV
    vocab (the shipped index is DEV+TEST-scoped and misses almost all TRAIN participant heads --
    see module docstring). max_lines caps the scan for self-test (real code path, tiny scale);
    None = full 34M-line scan (the real probe)."""
    edges: Dict[str, List] = {}
    n_lines = 0
    n_kept = 0
    t0 = time.time()
    with gzip.open(CN_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if max_lines is not None and n_lines > max_lines:
                break
            if n_lines % 4_000_000 == 0:
                print(f"[cn-index-build] {n_lines/1e6:.0f}M lines, {n_kept} kept, "
                      f"{time.time()-t0:.0f}s", flush=True)
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            rel = parts[1].split("/")[2] if parts[1].startswith("/r/") else None
            if rel not in _cn_builder.KEEP_RELS:
                continue
            start = _cn_builder._cn_term(parts[2])
            end = _cn_builder._cn_term(parts[3])
            if start is None or end is None:
                continue
            start_toks = _cn_builder._toks(start)
            end_toks = _cn_builder._toks(end)
            if not ((start_toks & vocab) or (end_toks & vocab)):
                continue
            weight = 1.0
            try:
                meta = json.loads(parts[4]) if len(parts) > 4 else {}
                weight = float(meta.get("weight", 1.0))
            except Exception:
                weight = 1.0
            for a_toks, b in ((start_toks, end), (end_toks, start)):
                for at in (a_toks & vocab):
                    edges.setdefault(at, []).append([rel, b, round(weight, 3)])
            n_kept += 1
    for term in list(edges.keys()):
        seen: Dict[Tuple[str, str], list] = {}
        for rel, other, w in edges[term]:
            key = (rel, other)
            if key not in seen or w > seen[key][2]:
                seen[key] = [rel, other, w]
        edges[term] = sorted(seen.values(), key=lambda e: -e[2])[:200]
    return {"_meta": {"source": "conceptnet-assertions-5.7.0", "relations": sorted(_cn_builder.KEEP_RELS),
                       "n_vocab_terms": len(vocab), "n_terms_with_edges": len(edges),
                       "n_edges_scanned_kept": n_kept, "n_lines": n_lines,
                       "split_scope": "train+dev (TEST untouched)", "capped": max_lines is not None},
            "edges": edges}


def _load_or_build_cn_index_traindev(train_paragraphs, dev_paragraphs) -> Dict[str, List]:
    if os.path.exists(CN_INDEX_TRAINDEV_PATH):
        with open(CN_INDEX_TRAINDEV_PATH, encoding="utf-8") as f:
            d = json.load(f)
        print(f"[cn-index] loaded cached: {d['_meta']}", flush=True)
        return d["edges"]
    vocab = _propara_vocab(train_paragraphs) | _propara_vocab(dev_paragraphs)
    print(f"[cn-index-build] vocab={len(vocab)} terms (train+dev); scanning {CN_GZ} ...", flush=True)
    out = _build_cn_index_traindev(vocab, max_lines=None)
    tmp = CN_INDEX_TRAINDEV_PATH + ".tmp"
    os.makedirs(os.path.dirname(CN_INDEX_TRAINDEV_PATH), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(tmp, CN_INDEX_TRAINDEV_PATH)
    print(f"[cn-index-build] done: {out['_meta']}", flush=True)
    return out["edges"]


def _cn_rich_feats(word: str, cn_edges: Dict[str, List], top_k: int = 8) -> List[str]:
    edges = cn_edges.get(word, [])
    edges_sorted = sorted(edges, key=lambda e: -e[2])[:top_k]
    return [f"cn:{rel}:{str(other).replace(' ', '_')}" for rel, other, _w in edges_sorted]


def _cn_source_feats(participant: str, cn_edges: Dict[str, List]) -> List[str]:
    out: Set[str] = set()
    for t in _participant_head_tokens(participant):
        out.update(_cn_rich_feats(t, cn_edges))
    return sorted(out)


# ============================================================================ source 3: offline embedding-rich
ANCHOR_WORDS = {
    "CREATE": ["create", "form", "produce", "grow", "generate", "emerge"],
    "MOVE": ["move", "flow", "travel", "transport", "carry", "enter"],
    "DESTROY": ["destroy", "consume", "burn", "dissolve", "absorb", "decay", "evaporate"],
}
EMB_BUCKETS = (0.15, 0.25, 0.35)   # MEASURED@ ad-hoc GloVe cosine spread check (this session,
# 20 ProPara-domain nouns vs anchor centroids ranged ~0.02-0.48; edges chosen to spread buckets)


def _emb_centroids(kv) -> Dict[str, np.ndarray]:
    cents = {}
    for cls, words in ANCHOR_WORDS.items():
        vecs = [np.asarray(kv[w]) for w in words if w in kv]
        assert vecs, f"EMB_ANCHOR_MISSING: no anchor words for {cls} present in embedding vocab"
        cents[cls] = np.mean(vecs, axis=0)
    return cents


def _cos(a, b) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _bucket(x: float) -> str:
    idx = int(np.digitize([x], EMB_BUCKETS)[0])
    return ["neg", "lo", "mid", "hi"][idx]


def _emb_source_feats(participant: str, kv, centroids: Dict[str, np.ndarray]) -> List[str]:
    heads = _participant_head_tokens(participant)
    vecs = [np.asarray(kv[t]) for t in heads if t in kv]
    if not vecs:
        return []
    v = np.mean(vecs, axis=0)
    return [f"emb:{cls}:{_bucket(_cos(v, c))}" for cls, c in centroids.items()]


# ============================================================================ instance construction / fit / eval
def _build_instances(paragraphs: List[Dict], gold_effects: Optional[Dict[Tuple, Set[str]]],
                     source_fn) -> List[Dict]:
    """source_fn(participant) -> List[str]. ONE instance per (pid, participant, candidate effect).
    NO raw-surface feature ever included -- any held-out signal is 100% source-content-derived."""
    out = []
    for para in paragraphs:
        pid = str(para["para_id"])
        for participant in para["participants"]:
            sfeats = source_fn(participant)
            for e in EFFECTS:
                feats = [f"effect:{e}"] + sfeats
                inst = {"pid": pid, "participant": participant, "effect": e, "feats": feats}
                if gold_effects is not None:
                    ge = gold_effects.get((pid, participant), set())
                    inst["gold_class"] = "FILL" if e in ge else "SKIP"
                out.append(inst)
    return out


def _fit_source(train_instances: List[Dict]) -> Tuple[Dict, Dict]:
    """Fit the SAME glass-box gam the schema binder used (reused, not hand-rolled)."""
    spec = {"classes": ["FILL", "SKIP"], "label_fn": lambda ep: ep["gold_class"],
            "min_coverage": 3, "max_singles_for_pairing": 60, "max_interactions": 40, "alpha": 1.0}
    res = gam_plugin.learn(train_instances, lambda ep: ep["feats"], spec, prior=None)
    meta = {"n_train_instances": len(train_instances),
            "n_fill_train": sum(1 for e in train_instances if e["gold_class"] == "FILL"),
            "compression_ratio": round(res.compression_ratio, 4),
            "n_main_keys": res.metrics.get("n_main_keys"),
            "n_interaction_keys": res.metrics.get("n_interaction_keys"),
            "is_episodic": res.is_episodic}
    return res.hypothesis, meta


def _predict_facts(hypothesis: Dict, dev_instances: List[Dict]) -> Dict[Tuple, Set[str]]:
    facts: Dict[Tuple, Set[str]] = {}
    for inst in dev_instances:
        key = (inst["pid"], inst["participant"])
        facts.setdefault(key, set())
        if gam_plugin.apply(hypothesis, inst["feats"]) == "FILL":
            facts[key].add(inst["effect"])
    return facts


def _pair_prf(gold_by_key: Dict[Tuple, Set[str]], pred_by_key: Dict[Tuple, Set[str]],
             keyset: Set[Tuple]) -> Dict:
    tp = fp = fn = 0
    for k in keyset:
        g = gold_by_key.get(k, set())
        p = pred_by_key.get(k, set())
        tp += len(g & p)
        fp += len(p - g)
        fn += len(g - p)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"pair_precision": round(prec, 4), "pair_recall": round(rec, 4), "pair_f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn, "n_keys": len(keyset)}


def _majority_facts(train_gold: Dict[Tuple, Set[str]], all_keys: Set[Tuple]) -> Dict[Tuple, Set[str]]:
    """Constant baseline: always predict the single TRAIN-most-frequent effect for every entity
    (ignores entity identity entirely; a non-degenerate reference -- NOT a strawman)."""
    cnt = Counter()
    for v in train_gold.values():
        for e in v:
            cnt[e] += 1
    top_effect = max(EFFECTS, key=lambda e: cnt.get(e, 0)) if cnt else EFFECTS[0]
    return {k: {top_effect} for k in all_keys}


def _scramble_gold(gold: Dict[Tuple, Set[str]], key_order: List[Tuple]) -> Dict[Tuple, Set[str]]:
    """Deterministic (F.5-compliant, hashlib-seeded, NO python hash()) permutation of the TRAIN
    entity->fate mapping -- breaks true entity-fate correspondence while keeping the label
    marginal distribution identical."""
    values = [gold.get(k, set()) for k in key_order]
    perm = _deterministic_perm("entity_fate_probe_scramble_v1", len(key_order))
    assert perm != list(range(len(key_order))), "SCRAMBLE_DEGENERATE: identity permutation (re-seed)"
    return {key_order[i]: values[perm[i]] for i in range(len(key_order))}


def _hash_facts(facts: Dict[Tuple, Set[str]]) -> str:
    rows = sorted((f"{k[0]}|{k[1]}", sorted(v)) for k, v in facts.items())
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()


# ============================================================================ probe orchestration
def run_probe(cn_max_lines: Optional[int] = None, cn_index_path: Optional[str] = None,
             mock_kv=None) -> Dict:
    """cn_max_lines/cn_index_path/mock_kv are self-test-only overrides (real probe: all None)."""
    t0 = time.time()
    train = _load_split("train")
    dev = _load_split("dev")
    print(f"[probe] train={len(train)} paragraphs, dev={len(dev)} paragraphs", flush=True)
    train_steps = build_step_rows(train)
    dev_steps = build_step_rows(dev)
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(train_steps))
    dev_gold = _gold_effects_from_multiset(_oracle_event_multiset(dev_steps))

    seen_tokens = _seen_surface_tokens(train)
    dev_keys = set(dev_gold.keys())
    unseen_keys = {k for k in dev_keys if _is_unseen_surface(k[1], seen_tokens)}
    seen_keys = dev_keys - unseen_keys
    print(f"[probe] dev_keys={len(dev_keys)} seen={len(seen_keys)} unseen={len(unseen_keys)}", flush=True)

    train_key_order = sorted(train_gold.keys())
    scrambled_train_gold = _scramble_gold(train_gold, train_key_order)

    majority_pred = _majority_facts(train_gold, dev_keys)
    majority_scores = {
        "all": _pair_prf(dev_gold, majority_pred, dev_keys),
        "seen": _pair_prf(dev_gold, majority_pred, seen_keys),
        "unseen": _pair_prf(dev_gold, majority_pred, unseen_keys),
    }
    print(f"[probe] majority baseline: {majority_scores}", flush=True)

    cn_path = cn_index_path or CN_INDEX_TRAINDEV_PATH
    if cn_index_path is not None or cn_max_lines is not None:
        vocab = _propara_vocab(train) | _propara_vocab(dev)
        cn_edges = _build_cn_index_traindev(vocab, max_lines=cn_max_lines)["edges"]
    else:
        cn_edges = _load_or_build_cn_index_traindev(train, dev)
    print(f"[probe] conceptnet index: {len(cn_edges)} terms", flush=True)

    if mock_kv is not None:
        kv = mock_kv
    else:
        print(f"[probe] loading {GENSIM_MODEL} (offline cache) ...", flush=True)
        kv = _load_gensim_kv(GENSIM_MODEL)
    centroids = _emb_centroids(kv)
    print(f"[probe] embedding kv ready", flush=True)

    sources = {
        "wordnet": lambda p: _wn_source_feats(p),
        "conceptnet": lambda p: _cn_source_feats(p, cn_edges),
        "embedding": lambda p: _emb_source_feats(p, kv, centroids),
    }

    results: Dict = {"majority_baseline": majority_scores}
    arms_hashes = {"majority": _hash_facts(majority_pred)}
    per_source_verdict: Dict[str, str] = {}

    for name, fn in sources.items():
        t_s = time.time()
        n_nonempty = sum(1 for para in dev for p in para["participants"] if fn(p))
        n_total = sum(len(para["participants"]) for para in dev)
        coverage_dev = round(n_nonempty / max(n_total, 1), 4)

        train_inst_real = _build_instances(train, train_gold, fn)
        dev_inst = _build_instances(dev, None, fn)
        hyp_real, meta_real = _fit_source(train_inst_real)
        pred_real = _predict_facts(hyp_real, dev_inst)

        train_inst_scr = _build_instances(train, scrambled_train_gold, fn)
        hyp_scr, meta_scr = _fit_source(train_inst_scr)
        pred_scr = _predict_facts(hyp_scr, dev_inst)

        arms_hashes[f"{name}_real"] = _hash_facts(pred_real)
        arms_hashes[f"{name}_scramble"] = _hash_facts(pred_scr)

        real_scores = {"all": _pair_prf(dev_gold, pred_real, dev_keys),
                       "seen": _pair_prf(dev_gold, pred_real, seen_keys),
                       "unseen": _pair_prf(dev_gold, pred_real, unseen_keys)}
        scr_scores = {"all": _pair_prf(dev_gold, pred_scr, dev_keys),
                      "seen": _pair_prf(dev_gold, pred_scr, seen_keys),
                      "unseen": _pair_prf(dev_gold, pred_scr, unseen_keys)}

        maj_unseen_f1 = majority_scores["unseen"]["pair_f1"]
        real_unseen_f1 = real_scores["unseen"]["pair_f1"]
        scr_unseen_f1 = scr_scores["unseen"]["pair_f1"]
        lift = round(real_unseen_f1 - maj_unseen_f1, 4)
        scramble_clean = scr_unseen_f1 <= maj_unseen_f1 + SCRAMBLE_CLEAN_MARGIN
        if lift >= LIFT_HARD_PASS and scramble_clean:
            verdict = "HARD_PASS_GENERALIZES"
        elif not scramble_clean:
            verdict = "HARD_FAIL_SCRAMBLE_LEAK"
        elif lift < LIFT_HARD_FAIL:
            verdict = "HARD_FAIL_NO_GENERALIZATION"
        else:
            verdict = "MIDDLE_BAND"
        per_source_verdict[name] = verdict

        results[name] = {
            "coverage_dev": coverage_dev,
            "fit_meta_real": meta_real,
            "fit_meta_scramble": meta_scr,
            "real": real_scores,
            "scramble": scr_scores,
            "lift_unseen_vs_majority": lift,
            "scramble_clean": scramble_clean,
            "verdict": verdict,
            "elapsed_s": round(time.time() - t_s, 2),
        }
        print(f"[probe] source={name} verdict={verdict} lift_unseen={lift} "
              f"real_unseen_f1={real_unseen_f1} scr_unseen_f1={scr_unseen_f1} "
              f"maj_unseen_f1={maj_unseen_f1} coverage_dev={coverage_dev} "
              f"elapsed={time.time()-t_s:.1f}s", flush=True)

    non_majority_hashes = [v for k, v in arms_hashes.items() if k != "majority"]
    all_collapsed_to_majority = all(h == arms_hashes["majority"] for h in non_majority_hashes)
    if all_collapsed_to_majority:
        raise AssertionError("ARMS_DID_NOT_DIFFER: all 6 non-majority arms hash-identical to the "
                              "majority baseline -- pipeline bug (no source is doing anything)")

    n_hard_pass = sum(1 for v in per_source_verdict.values() if v == "HARD_PASS_GENERALIZES")
    n_hard_fail = sum(1 for v in per_source_verdict.values() if v.startswith("HARD_FAIL"))
    if n_hard_pass >= 1:
        overall_verdict = "HARD_PASS"
        overall_msg = ("HARD_PASS: >=1 external source generalizes to unseen-surface entities "
                       "above majority, scramble-clean -- entity-role knowledge IS externally "
                       "sourceable (fork A/B viable)")
    elif n_hard_fail == len(per_source_verdict):
        overall_verdict = "HARD_FAIL"
        overall_msg = ("HARD_FAIL: no external source generalizes to unseen-surface entities -- "
                       "entity-level process-role knowledge is NOT in these accessible structured "
                       "sources (corpus-scale distributional learning or LLM-scale needed)")
    else:
        overall_verdict = "MIDDLE_BAND"
        overall_msg = "MIDDLE_BAND: mixed per-source results, no clean overall call"

    elapsed = time.time() - t0
    verdict_msg = (
        overall_msg
        + " | per_source_verdict=" + json.dumps(per_source_verdict)
        + " | lift_unseen=" + json.dumps({k: results[k]["lift_unseen_vs_majority"] for k in sources})
        + " | scramble_clean=" + json.dumps({k: results[k]["scramble_clean"] for k in sources})
        + " | majority_unseen_f1=" + str(majority_scores["unseen"]["pair_f1"])
    )
    return {
        "verdict": overall_verdict,
        "verdict_msg": verdict_msg,
        "summary": overall_msg,
        "elapsed_s": round(elapsed, 2),
        "run_mode": "probe",
        "anchor_name": ANCHOR_NAME,
        "n_train_paragraphs": len(train),
        "n_dev_paragraphs": len(dev),
        "n_dev_keys": len(dev_keys),
        "n_unseen_keys": len(unseen_keys),
        "n_seen_keys": len(seen_keys),
        "results": results,
        "arms_hashes": arms_hashes,
        "arms_differ_verified": not all_collapsed_to_majority,
        "per_source_verdict": per_source_verdict,
    }


# ============================================================================ metrics I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ============================================================================ self-test
class _MockKV:
    """TINY synthetic KeyedVectors-like object (dict-based). Mocks ONLY the embedding source for
    self-test speed (real GloVe load = 115s offline; same mock-KV precedent already established
    in experiments/exp_encoder_word2vec_substrate_bind_v1.py "T7"). WordNet + ConceptNet self-
    tests exercise REAL objects (capped scan for ConceptNet, full nltk corpus for WordNet)."""
    def __init__(self, dim=16):
        self.dim = dim
        rng = np.random.default_rng(20260811)
        self._vecs = {}
        vocab = (["create", "form", "produce", "grow", "generate", "emerge",
                  "move", "flow", "travel", "transport", "carry", "enter",
                  "destroy", "consume", "burn", "dissolve", "absorb", "decay", "evaporate"]
                 + ["wood", "rock", "water", "magma", "lava", "gas", "cloud", "seed"])
        for w in vocab:
            self._vecs[w] = rng.standard_normal(dim).astype(np.float32)

    def __contains__(self, w):
        return w in self._vecs

    def __getitem__(self, w):
        return self._vecs[w]


def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}

    # (1) REAL WordNet: two different words must produce non-empty, DIFFERING rich feature sets
    f_wood = _wn_source_feats("wood")
    f_metal = _wn_source_feats("metal")
    assert f_wood, "WORDNET_EMPTY: no rich features for 'wood' (real nltk corpus)"
    assert f_metal, "WORDNET_EMPTY: no rich features for 'metal'"
    assert any(f.startswith("hyper:") for f in f_wood), "no hypernym-chain feature emitted for 'wood'"
    assert set(f_wood) != set(f_metal), "WordNet rich features identical for 'wood' vs 'metal' (no discrimination)"
    out["checks"]["wordnet_real"] = {"n_feats_wood": len(f_wood), "n_feats_metal": len(f_metal),
                                     "differ": True}
    print(f"[self-test] wordnet OK: wood={len(f_wood)} feats, metal={len(f_metal)} feats", flush=True)

    # (2) REAL ConceptNet: capped real gz scan (real code path, tiny scale -- not the full 34M-line
    # scan, which belongs to the actual probe run and is cached to disk once there)
    tiny_vocab = {"water", "rock", "carbon", "energy"}
    cn_out = _build_cn_index_traindev(tiny_vocab, max_lines=800_000)
    assert cn_out["_meta"]["n_lines"] <= 800_001, "cn cap not respected"
    assert cn_out["_meta"]["capped"] is True
    n_terms_hit = len(cn_out["edges"])
    out["checks"]["conceptnet_real"] = {"capped_lines": cn_out["_meta"]["n_lines"],
                                        "n_terms_with_edges": n_terms_hit}
    print(f"[self-test] conceptnet capped-scan OK: {cn_out['_meta']['n_lines']} lines, "
          f"{n_terms_hit} terms hit", flush=True)

    # (3) MOCK embedding KV (documented exception; real GloVe load deferred to the probe run)
    mock_kv = _MockKV()
    centroids = _emb_centroids(mock_kv)
    feats_wood = _emb_source_feats("wood", mock_kv, centroids)
    assert feats_wood and all(f.startswith("emb:") for f in feats_wood), "embedding source produced no feats on mock KV"
    out["checks"]["embedding_mock"] = {"n_feats": len(feats_wood), "sample": feats_wood}
    print(f"[self-test] embedding (mock KV) OK: {feats_wood}", flush=True)

    # (4) REAL gam fit/predict at tiny scale (N~12 paragraphs), REAL substrate loaders
    train = _load_split("train")[:8]
    dev = _load_split("dev")[:4]
    train_steps = build_step_rows(train)
    dev_steps = build_step_rows(dev)
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(train_steps))
    dev_gold = _gold_effects_from_multiset(_oracle_event_multiset(dev_steps))
    train_inst = _build_instances(train, train_gold, _wn_source_feats)
    dev_inst = _build_instances(dev, None, _wn_source_feats)
    assert train_inst and dev_inst, "REAL_CODE_PATH_EMPTY: tiny-scale instance construction produced nothing"
    hyp, meta = _fit_source(train_inst)
    pred = _predict_facts(hyp, dev_inst)
    assert isinstance(pred, dict)
    out["checks"]["gam_real_code_path"] = {"n_train_inst": len(train_inst), "n_dev_inst": len(dev_inst),
                                           "fit_meta": meta, "n_pred_keys": len(pred)}
    print(f"[self-test] gam tiny-scale fit/predict OK: {meta}", flush=True)

    # (5) arms-must-differ sanity: majority vs wordnet-real predictions must differ on this subset
    dev_keys = set(dev_gold.keys())
    majority_pred = _majority_facts(train_gold, dev_keys)
    h_maj = _hash_facts(majority_pred)
    h_wn = _hash_facts(pred)
    out["checks"]["arms_differ"] = {"majority_hash": h_maj, "wordnet_hash": h_wn, "differ": h_maj != h_wn}
    print(f"[self-test] arms_differ (tiny subset) = {h_maj != h_wn}", flush=True)

    # (6) scramble determinism + non-degeneracy
    key_order = sorted(train_gold.keys())
    scr1 = _scramble_gold(train_gold, key_order)
    scr2 = _scramble_gold(train_gold, key_order)
    assert scr1 == {k: v for k, v in scr2.items()}, "SCRAMBLE_NONDETERMINISTIC: two calls produced different permutations"
    out["checks"]["scramble_deterministic"] = True
    print("[self-test] scramble determinism OK", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = "SELFTEST_PASS: wordnet real-differ + conceptnet real-capped-scan + " \
                          "embedding mock-KV + gam real tiny-scale fit/predict + arms-differ + " \
                          "scramble-determinism all OK"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


# ============================================================================ main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()

    run_mode = "self_test" if args.self_test else "probe"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)

    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run_probe()
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics to {os.path.join(out_dir, 'metrics.json')} "
              f"verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
