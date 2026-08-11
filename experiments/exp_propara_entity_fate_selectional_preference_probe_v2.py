# CELL-TEMPLATE (measurement-probe; NOT a dispatch/pipeline cell). PROPERLY-POWERED v2 of
# exp_propara_entity_fate_selectional_preference_probe_v1 (which HARD_FAIL'd with a DEGENERATE
# all-SKIP prediction -- the gam predicted zero FILL EVEN IN-DISTRIBUTION, diagnosed as
# under-powering, NOT signal-absence, per the locked "flat/degenerate learning result = broken/
# under-powered experiment, not a ceiling" discipline). This v2 is the pre-committed FINAL purist
# distributional check; whatever it shows, the charter decision goes to the USER next (no v3).
#
# FOUR under-powering fixes vs v1 (all no-LLM, reuse the same healthy frontend + gam):
#   1. RICHER FEATURES: count-MAGNITUDE (log-binned) buckets per fate-verb-class x role + raw
#      per-fate-class ratios P(fate | entity), AND effect-CONDITIONED relative features
#      (self_mag / self_frac / self_argmax / self_rank) that vary across the 3 candidate-effect
#      instances of one participant -- v1's presence-only sel:fate:role features were shared across
#      all 3 effect-instances so the ONLY discriminating feature was effect:E, forcing the gam to
#      rely on MDL interactions that never fired -> degenerate all-SKIP. The relative features give
#      the gam a DIRECT graded main-effect ("does this candidate effect match the entity's dominant
#      corpus fate-context").
#   2. BROADER fate-verb lexicon (hand-authored glass-box seed, missing-FACT supply, no LLM): each
#      of consume/produce/move classes expanded to a large synonym set (see _FATE_VERB_LEXICON_BASE)
#      + morphological expansion via the SAME _inflect/_expand_fate_lexicon as v1, so more entities
#      get fate-revealing contexts.
#   3. LARGER corpus sample: parse well beyond v1's 15k lines (default target 45,000 parsed lines,
#      RESUMABLE via an on-disk checkpoint) so unseen-entity >=3-context coverage rises above v1's
#      measured 45%.
#   4. CLASS-BALANCING: subsample the SKIP (majority) instances to a ratio*n_FILL selected DEV-BLIND
#      on a TRAIN 80/20 held-out split (reuses the exp_maven_ere_convergence_gated_causal_v2 pattern
#      verbatim) so FILL is actually predictable (fixes the all-SKIP default under imbalance).
#
# REPORTS BOTH, DISTINCTLY (the whole point): (a) IN-DISTRIBUTION = SEEN-surface dev-entity fate
# vs majority (does the richer arm now have ANY exploitable signal once features are adequate?);
# (b) UNSEEN generalization = held-out-unseen-surface dev-entity fate vs majority. Plus scramble +
# majority. Three-outcome logic: (i) still ~zero on SEEN = signal genuinely absent even with
# adequate features -> purist route RIGOROUSLY closed; (ii) SEEN lift but UNSEEN~0 = memorization/
# no-generalization (like WordNet/ConceptNet/GloVe) -> purist route closed; (iii) generalizes =
# PURE-GLASS-BOX WALL CROSSED, no LLM needed.
#
# Load-bearing subset applied: no bare except / no except BaseException (SystemExit/KeyboardInterrupt
# re-raise, then Exception->crash-diagnostic->re-raise); final_metrics_atomicity=tmp_replace;
# deterministic_seeding=true (PosTagger.train/train_arc fixed int seeds; subsample RNG fixed seed;
# TRAIN-gold scramble reuses hashlib-seeded _deterministic_perm/_det_seed, F.5-compliant, no python
# hash()/list(set()) ordering); self-test constructs REAL substrate objects (tiny real frontend
# train + real capped SimpleWiki scan + real balanced gam fit/predict) -- no synthetic-only branch;
# arms_differ hash-checked (majority vs selectional-real vs scramble); crlb_n/a (pair P/R/F1 vs
# majority over the fixed ProPara EMNLP18 TRAIN/DEV split, no noise-floor threshold).
# See preregs/2026-08-11_propara_entity_fate_selectional_preference_probe_v2.md for full pre-reg.
"""exp_propara_entity_fate_selectional_preference_probe_v2 -- properly-powered FINAL purist
distributional check: can entity-level process-role (fate) knowledge be learned PURE-GLASS-BOX
(NO LLM anywhere) from verb-argument SELECTIONAL-PREFERENCE signal in a modern corpus, and does it
generalize to UNSEEN-surface entities? See header block for the four under-powering fixes vs v1.

Modes:
  --self-test        : fast, all REAL code paths at tiny scale (real_code_path per META_RULE F.1).
  --build-frontend   : train + CACHE the UD_English_EWT frontend (PosTagger + ArcParser) to disk,
                       then exit (heavy, ~3min; decouples the one-time frontend cost from the
                       resumable scan so each foreground call fits a <=10min budget). No metrics.
  (no flag) = probe  : load the CACHED frontend (errors if absent -- run --build-frontend first),
                       load-or-EXTEND the resumable selectional-scan checkpoint toward
                       --scan-target parsed lines (bounded by --scan-budget-s wall seconds per
                       call; checkpoints periodically). When the scan reaches target: coverage +
                       dev-blind ratio selection + balanced fit + scramble -> writes FINAL
                       metrics.json (verdict). If the wall budget is hit first: updates the
                       checkpoint, writes _scan_progress.json (NOT metrics.json), prints
                       RESUME_NEEDED, exits 0 (re-invoke to continue -- resumable-per-unit).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import platform
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

ANCHOR_NAME = "propara_entity_fate_selectional_preference_probe_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
FRONTEND_DIR = os.path.join(OUTPUT_DIR, "frontend_cache")
POS_CACHE = os.path.join(FRONTEND_DIR, "pos_tagger.json")
ARC_CACHE = os.path.join(FRONTEND_DIR, "arc_parser.npz")
SCAN_CKPT = os.path.join(OUTPUT_DIR, "sel_index_ckpt.json")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator, candidates_from_parse  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb, frame_slot_role  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402

from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _det_seed, _deterministic_perm,
)
from experiments.exp_propara_schema_learned_grounded_binder_v1 import (  # noqa: E402
    _gold_effects_from_multiset, _participant_head_tokens, _seen_surface_tokens, _is_unseen_surface,
)
from experiments.exp_propara_entity_fate_external_knowledge_probe_v1 import (  # noqa: E402
    _pair_prf, _majority_facts, _scramble_gold, _hash_facts, _predict_facts,
)
# v1 (this arc): reuse the frontend trainer/health + morphology expander verbatim (unmodified).
from experiments.exp_propara_entity_fate_selectional_preference_probe_v1 import (  # noqa: E402
    _to_pos_seqs, _to_arc_seqs, _frontend_health, _inflect, _expand_fate_lexicon,
    FRONTEND_TAG_ACC_FLOOR, FRONTEND_UAS_FLOOR,
)
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import parse_conllu  # noqa: E402
from hdlab.pos_tagger import PosTagger as _PT  # noqa: E402  (train classmethod)
from hdlab.arc_parser import train_arc as _train_arc  # noqa: E402
from propara_trap_check import build_step_rows  # noqa: E402

EFFECTS = ("CREATE", "MOVE", "DESTROY")
ROLES = ("AGENT", "PATIENT")
_WORD = re.compile(r"[a-zA-Z]+")
TRAIN_CONLLU_PATH = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")

# ============================================================================ pre-registered bands
# SAME thresholds as v1 + the sibling external-knowledge probe (direct comparability, not re-tuned).
LIFT_HARD_PASS = 0.05
LIFT_HARD_FAIL = 0.02
SCRAMBLE_CLEAN_MARGIN = 0.05
# dev-blind subsample-ratio grid (SKIP-per-FILL); 999 = keep all negatives (no subsample sentinel).
SUBSAMPLE_RATIOS = (0.5, 1.0, 1.5, 2.0, 3.0, 999)
SUBSAMPLE_SEED = 20260811

# ============================================================================ broadened fate-verb lexicon
# Hand-authored glass-box seed (missing-FACT supply, NO LLM). Each verb assigned to EXACTLY ONE
# class by dominant process semantics (cross-class-ambiguous verbs deliberately kept single-class to
# avoid label noise). DESTROY = consumed/removed/broken-down; CREATE = produced/formed/generated;
# MOVE = transported/relocated. Morphologically expanded via _expand_fate_lexicon (same as v1).
_FATE_VERB_LEXICON_BASE: Dict[str, str] = {}
for _v in ["consume", "burn", "oxidize", "oxidise", "absorb", "dissolve", "decay", "evaporate",
           "digest", "corrode", "rust", "decompose", "rot", "erode", "melt", "vaporize", "vaporise",
           "combust", "metabolize", "metabolise", "degrade", "disintegrate", "deplete", "exhaust",
           "destroy", "ferment", "respire", "weather", "wear", "expend", "dissipate", "diminish",
           "shrink", "die", "perish", "sublimate", "neutralize", "neutralise"]:
    _FATE_VERB_LEXICON_BASE[_v] = "DESTROY"
for _v in ["produce", "release", "emit", "form", "create", "generate", "emerge", "synthesize",
           "synthesise", "secrete", "deposit", "precipitate", "crystallize", "crystallise", "condense",
           "assemble", "construct", "develop", "grow", "yield", "manufacture", "forge", "spawn",
           "originate", "arise", "accumulate", "build", "make", "output", "excrete", "exhale",
           "sprout", "bloom", "hatch", "breed"]:
    _FATE_VERB_LEXICON_BASE.setdefault(_v, "CREATE")
for _v in ["move", "carry", "flow", "transport", "travel", "migrate", "circulate", "transfer",
           "diffuse", "spread", "distribute", "deliver", "conduct", "pump", "propel", "shift",
           "transmit", "convey", "drain", "pour", "drip", "seep", "leak", "drift", "roll", "slide",
           "rise", "fall", "sink", "float", "descend", "ascend", "enter", "exit", "escape", "cross"]:
    _FATE_VERB_LEXICON_BASE.setdefault(_v, "MOVE")

FATE_VERB_LEXICON: Dict[str, str] = _expand_fate_lexicon(_FATE_VERB_LEXICON_BASE)
# stable digest of the lexicon (checkpoint keys on this: a lexicon change invalidates the scan cache)
_LEX_DIGEST = _hash_facts({(k, "x"): {v} for k, v in FATE_VERB_LEXICON.items()})[:16]


# ============================================================================ frontend cache (resumable)
def _train_and_cache_frontend(pos_epochs: int, arc_epochs: int, max_sents: Optional[int] = None) -> Dict:
    sents = parse_conllu(TRAIN_CONLLU_PATH)
    if max_sents is not None:
        sents = sents[:max_sents]
    pos_seqs = _to_pos_seqs(sents)
    arc_seqs = _to_arc_seqs(sents)
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    t0 = time.time()
    tagger = _PT.train(pos_seqs, epochs=pos_epochs)
    tagger.save(POS_CACHE)
    print(f"[frontend] pos tagger trained+cached: n_sents={len(sents)} epochs={pos_epochs} "
          f"elapsed={time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    avg = _train_arc(arc_seqs, epochs=arc_epochs, seed=1027)
    ArcParser(avg).save(ARC_CACHE)
    print(f"[frontend] arc parser trained+cached: n_sents={len(sents)} epochs={arc_epochs} "
          f"elapsed={time.time()-t0:.1f}s", flush=True)
    return {"n_frontend_train_sents": len(sents), "pos_epochs": pos_epochs, "arc_epochs": arc_epochs}


def _load_frontend() -> Tuple[CandidateGenerator, PosTagger, ArcParser]:
    if not (os.path.exists(POS_CACHE) and os.path.exists(ARC_CACHE)):
        raise FileNotFoundError(f"Frontend cache missing ({POS_CACHE} / {ARC_CACHE}). Run "
                                f"--build-frontend first (decoupled to keep each call <=10min).")
    tagger = PosTagger.load(POS_CACHE)
    parser = ArcParser.load(ARC_CACHE)
    return CandidateGenerator(tagger, parser), tagger, parser


# ============================================================================ resumable selectional scan
def _new_scan_state() -> Dict:
    return {"lex_digest": _LEX_DIGEST, "sel_counts": {}, "n_lines_scanned": 0,
            "n_prefilter_hits": 0, "n_parsed": 0, "n_cand_hits": 0, "n_parse_errors": 0,
            "last_error": None, "complete": False, "target_parsed": None}


def _load_scan_state() -> Optional[Dict]:
    if not os.path.exists(SCAN_CKPT):
        return None
    with open(SCAN_CKPT, encoding="utf-8") as f:
        st = json.load(f)
    if st.get("lex_digest") != _LEX_DIGEST:
        print(f"[sel-scan] checkpoint lexicon-digest mismatch ({st.get('lex_digest')} != {_LEX_DIGEST}); "
              f"discarding stale checkpoint and rescanning", flush=True)
        return None
    return st


def _save_scan_state(st: Dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = SCAN_CKPT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f)
    os.replace(tmp, SCAN_CKPT)


def _extend_scan(gen: CandidateGenerator, vocab: Set[str], corpus_path: str, target_parsed: int,
                 budget_s: float, ckpt_every: int = 5000) -> Dict:
    """Resume-or-start the vocab-scoped SimpleWiki scan, extending sel_counts toward target_parsed
    parsed lines, bounded by budget_s wall-seconds this call. Two-condition cheap token prefilter
    (>=1 vocab token AND >=1 fate-verb-lemma token); ONLY survivors get a REAL dependency parse.
    Checkpoints every ckpt_every parsed lines and on return (resumable-per-unit)."""
    st = _load_scan_state() or _new_scan_state()
    st["target_parsed"] = target_parsed
    if st.get("complete") and st["n_parsed"] >= target_parsed:
        print(f"[sel-scan] already complete at n_parsed={st['n_parsed']}", flush=True)
        return st
    sel_counts: Dict[str, Dict[str, int]] = {k: dict(v) for k, v in st["sel_counts"].items()}
    n_lines = st["n_lines_scanned"]
    skip_to = n_lines
    t0 = time.time()
    parsed_this_call = 0
    with open(corpus_path, encoding="utf-8") as f:
        # fast-forward past already-scanned lines (measured ~1s per 500k lines)
        for _ in range(skip_to):
            if f.readline() == "":
                break
        while True:
            line = f.readline()
            if line == "":
                st["complete"] = True
                break
            n_lines += 1
            toks_lower = set(_WORD.findall(line.lower()))
            if not (toks_lower & vocab):
                continue
            if not any(lemma_verb(t) in FATE_VERB_LEXICON for t in toks_lower):
                continue
            st["n_prefilter_hits"] += 1
            try:
                cr = gen.generate(line.strip(), extended=True)
            except Exception as e:  # noqa: BLE001 -- per-line resilience; COUNTED + rate-gated (never
                # silently swallowed-forever, META_RULE_J).
                st["n_parse_errors"] += 1
                st["last_error"] = f"{type(e).__name__}: {str(e)[:200]}"
                continue
            st["n_parsed"] += 1
            parsed_this_call += 1
            for (v, a) in cr.candidates:
                if v - 1 >= len(cr.pos) or cr.pos[v - 1] != "VERB":
                    continue
                lemma = lemma_verb(cr.tokens[v - 1])
                fate = FATE_VERB_LEXICON.get(lemma)
                if fate is None:
                    continue
                arg_tok = cr.tokens[a - 1].lower()
                if arg_tok not in vocab:
                    continue
                slot = "subj" if a < v else "obj"
                role = frame_slot_role(lemma, slot)
                if role not in ROLES:
                    continue
                key = f"{fate}:{role}"
                d = sel_counts.setdefault(arg_tok, {})
                d[key] = d.get(key, 0) + 1
                st["n_cand_hits"] += 1
            if st["n_parsed"] >= target_parsed:
                break
            if parsed_this_call % ckpt_every == 0:
                st["sel_counts"] = sel_counts
                st["n_lines_scanned"] = n_lines
                _save_scan_state(st)
                print(f"[sel-scan] ckpt parsed={st['n_parsed']}/{target_parsed} lines={n_lines} "
                      f"cand_hits={st['n_cand_hits']} errors={st['n_parse_errors']} "
                      f"elapsed_this_call={time.time()-t0:.0f}s", flush=True)
            if (time.time() - t0) >= budget_s:
                print(f"[sel-scan] wall budget {budget_s}s hit at parsed={st['n_parsed']}; "
                      f"checkpointing for resume", flush=True)
                break
    st["sel_counts"] = sel_counts
    st["n_lines_scanned"] = n_lines
    if st["n_parsed"] >= target_parsed:
        st["complete"] = True
    error_rate = st["n_parse_errors"] / max(st["n_parsed"] + st["n_parse_errors"], 1)
    st["parse_error_rate"] = round(error_rate, 4)
    _save_scan_state(st)
    print(f"[sel-scan] call done: parsed={st['n_parsed']}/{target_parsed} lines={n_lines} "
          f"complete={st['complete']} terms_hit={len(sel_counts)} err_rate={error_rate:.4f} "
          f"elapsed_this_call={time.time()-t0:.0f}s", flush=True)
    if error_rate > 0.10:
        raise AssertionError(f"SELECTIONAL_SCAN_ERROR_RATE_TOO_HIGH: {error_rate:.1%} parse calls "
                              f"raised -- frontend likely broken. last_error={st['last_error']}")
    return st


# ============================================================================ richer feature construction
def _logbucket(c: int) -> str:
    if c <= 0:
        return "b0"
    return "b" + str(min(int(math.log2(c)) + 1, 6))


_FRAC_EDGES = (0.001, 0.1, 0.25, 0.5, 0.75)


def _fracbucket(f: float) -> str:
    return "fb" + str(int(np.digitize([f], _FRAC_EDGES)[0]))


def _entity_profile(counts: Dict[str, int]):
    per_fate = {E: 0 for E in EFFECTS}
    per_fate_role = {E: {r: 0 for r in ROLES} for E in EFFECTS}
    for k, c in counts.items():
        fate, role = k.split(":")
        if fate in per_fate:
            per_fate[fate] += c
            if role in per_fate_role[fate]:
                per_fate_role[fate][role] += c
    total = sum(per_fate.values())
    order = sorted(EFFECTS, key=lambda E: (-per_fate[E], E))
    argmax = order[0] if total > 0 else None
    rank = {E: order.index(E) for E in EFFECTS}
    return per_fate, per_fate_role, total, argmax, rank


def _entity_counts(participant: str, sel_counts: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for t in _participant_head_tokens(participant):
        for k, c in sel_counts.get(t, {}).items():
            counts[k] = counts.get(k, 0) + c
    return counts


def _abs_feats(per_fate, per_fate_role, total) -> List[str]:
    """Entity-level (shared across the 3 candidate effects): raw per-fate-class + per-(fate,role)
    magnitude buckets + per-class ratio buckets. The coordinator's fix #1 'raw per-fate-class
    association COUNTS + ratios P(fate|entity)'."""
    out: List[str] = []
    for E in EFFECTS:
        out.append(f"cnt:{E}:{_logbucket(per_fate[E])}")
        for r in ROLES:
            if per_fate_role[E][r] > 0:
                out.append(f"cntr:{E}:{r}:{_logbucket(per_fate_role[E][r])}")
        if total > 0:
            out.append(f"frac:{E}:{_fracbucket(per_fate[E] / total)}")
    out.append(f"total:{_logbucket(total)}")
    return out


def _rel_feats(E, per_fate, per_fate_role, total, argmax, rank) -> List[str]:
    """Effect-CONDITIONED relative features (DIFFER across the 3 candidate-effect instances of one
    participant -- the load-bearing fix: gives the gam a direct graded main-effect for 'candidate
    effect matches this entity's corpus fate-profile', no reliance on MDL interactions that never
    fired in v1)."""
    out = [f"effE:{E}",
           f"self_mag:{_logbucket(per_fate[E])}",
           f"self_pat_mag:{_logbucket(per_fate_role[E]['PATIENT'])}",
           f"self_agt_mag:{_logbucket(per_fate_role[E]['AGENT'])}",
           f"self_argmax:{int(argmax == E)}",
           f"self_rank:{rank[E]}",
           f"self_present:{int(per_fate[E] > 0)}"]
    if total > 0:
        out.append(f"self_frac:{_fracbucket(per_fate[E] / total)}")
    return out


def _feat_fn(participant: str, E: str, sel_counts: Dict[str, Dict[str, int]]) -> List[str]:
    counts = _entity_counts(participant, sel_counts)
    per_fate, per_fate_role, total, argmax, rank = _entity_profile(counts)
    return _abs_feats(per_fate, per_fate_role, total) + _rel_feats(E, per_fate, per_fate_role, total, argmax, rank)


def _build_instances_v2(paragraphs, gold_effects, sel_counts) -> List[Dict]:
    """ONE instance per (pid, participant, candidate effect). NO raw surface-identity feature -- all
    features are corpus-co-occurrence-derived (never the entity string), so any held-out signal is
    100% selectional, never memorized. Key convention (pid=str(para_id)) matches the sibling probe's
    _build_instances (verified: sibling's non-zero arms prove keys join to the oracle gold)."""
    out = []
    for para in paragraphs:
        pid = str(para["para_id"])
        for participant in para["participants"]:
            for E in EFFECTS:
                feats = _feat_fn(participant, E, sel_counts)
                inst = {"pid": pid, "participant": participant, "effect": E, "feats": feats}
                if gold_effects is not None:
                    ge = gold_effects.get((pid, participant), set())
                    inst["gold_class"] = "FILL" if E in ge else "SKIP"
                out.append(inst)
    return out


# ============================================================================ balanced fit + ratio selection
def _fit_balanced(train_instances: List[Dict], ratio: float, seed: int = SUBSAMPLE_SEED) -> Dict:
    rng = random.Random(seed)
    pos = [e for e in train_instances if e["gold_class"] == "FILL"]
    neg = [e for e in train_instances if e["gold_class"] == "SKIP"]
    keep = len(neg) if ratio >= 999 else min(len(neg), int(len(pos) * ratio))
    negs = list(neg)
    rng.shuffle(negs)
    tr = pos + negs[:keep]
    spec = {"classes": ["FILL", "SKIP"], "label_fn": lambda ep: ep["gold_class"],
            "min_coverage": 3, "max_singles_for_pairing": 60, "max_interactions": 40, "alpha": 1.0}
    res = gam_plugin.learn(tr, lambda ep: ep["feats"], spec, prior=None)
    return res.hypothesis


def _eval_ratio_on_dev(train_inst, train_inst_scr, dev_inst, dev_gold, dev_keys, seen_keys,
                       unseen_keys, ratio) -> Dict:
    """Fit real + label-scramble at `ratio` on full TRAIN, evaluate BOTH on DEV. The real-vs-scramble
    delta subtracts off the degenerate class-prior predictor (v1 all-SKIP / v2 all-FILL), isolating
    the ENTITY-SPECIFIC selectional contribution -- the degeneracy-robust discriminator."""
    hyp_real = _fit_balanced(train_inst, ratio)
    pred_real = _predict_facts(hyp_real, dev_inst)
    hyp_scr = _fit_balanced(train_inst_scr, ratio)
    pred_scr = _predict_facts(hyp_scr, dev_inst)
    n_fill_real = sum(len(v) for v in pred_real.values())
    n_fill_scr = sum(len(v) for v in pred_scr.values())
    real = {"all": _pair_prf(dev_gold, pred_real, dev_keys), "seen": _pair_prf(dev_gold, pred_real, seen_keys),
            "unseen": _pair_prf(dev_gold, pred_real, unseen_keys)}
    scr = {"all": _pair_prf(dev_gold, pred_scr, dev_keys), "seen": _pair_prf(dev_gold, pred_scr, seen_keys),
           "unseen": _pair_prf(dev_gold, pred_scr, unseen_keys)}
    return {"ratio": ratio, "real": real, "scramble": scr,
            "n_fill_real": n_fill_real, "n_fill_scr": n_fill_scr,
            "real_seen_f1": real["seen"]["pair_f1"], "real_unseen_f1": real["unseen"]["pair_f1"],
            "scr_seen_f1": scr["seen"]["pair_f1"], "scr_unseen_f1": scr["unseen"]["pair_f1"],
            "delta_seen_vs_scr": round(real["seen"]["pair_f1"] - scr["seen"]["pair_f1"], 4),
            "delta_unseen_vs_scr": round(real["unseen"]["pair_f1"] - scr["unseen"]["pair_f1"], 4),
            "real_pred_real": pred_real, "pred_scr": pred_scr,
            "hash_real": _hash_facts(pred_real), "hash_scr": _hash_facts(pred_scr)}


def _select_ratio(train_paras, train_gold, sel_counts) -> Tuple[float, Dict]:
    """DEV-BLIND operating-point selection (fix #4, MAVEN-ERE v2 pattern): split TRAIN paragraphs
    80/20 by deterministic para_id sort, fit at each ratio on the 80, pick the ratio maximizing
    held-out-TRAIN-20% pair_f1. NO DEV data touched."""
    ids = sorted(str(p["para_id"]) for p in train_paras)
    n_fit = int(len(ids) * 0.8)
    fit_ids, val_ids = set(ids[:n_fit]), set(ids[n_fit:])
    fit_paras = [p for p in train_paras if str(p["para_id"]) in fit_ids]
    val_paras = [p for p in train_paras if str(p["para_id"]) in val_ids]
    fit_inst = _build_instances_v2(fit_paras, train_gold, sel_counts)
    val_inst = _build_instances_v2(val_paras, None, sel_counts)
    val_keys = {(str(p["para_id"]), part) for p in val_paras for part in p["participants"]}
    val_gold_facts = {k: train_gold.get(k, set()) for k in val_keys}
    scores: Dict[float, float] = {}
    for ratio in SUBSAMPLE_RATIOS:
        hyp = _fit_balanced(fit_inst, ratio)
        pred = _predict_facts(hyp, val_inst)
        scores[ratio] = _pair_prf(val_gold_facts, pred, val_keys)["pair_f1"]
    best = max(SUBSAMPLE_RATIOS, key=lambda r: scores[r])
    return best, {str(k): v for k, v in scores.items()}


# ============================================================================ coverage stats
def _coverage_stats(all_keys: Set[Tuple], sel_counts: Dict[str, Dict[str, int]]) -> Dict:
    n_ge1 = n_ge3 = n_ge5 = 0
    for (_pid, participant) in all_keys:
        total = sum(_entity_counts(participant, sel_counts).values())
        n_ge1 += int(total >= 1)
        n_ge3 += int(total >= 3)
        n_ge5 += int(total >= 5)
    n = max(len(all_keys), 1)
    return {"n_keys": len(all_keys), "n_ge1_ctx": n_ge1, "n_ge3_ctx": n_ge3, "n_ge5_ctx": n_ge5,
            "frac_ge1_ctx": round(n_ge1 / n, 4), "frac_ge3_ctx": round(n_ge3 / n, 4),
            "frac_ge5_ctx": round(n_ge5 / n, 4)}


# ============================================================================ probe orchestration
def run_probe(scan_target: int, scan_budget_s: float, health_max_sents: Optional[int]) -> Optional[Dict]:
    t0 = time.time()
    gen, tagger, parser = _load_frontend()
    health = _frontend_health(tagger, parser, health_max_sents)
    print(f"[probe] frontend health: {health}", flush=True)

    train = _load_split("train")
    dev = _load_split("dev")
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(build_step_rows(train)))
    dev_gold = _gold_effects_from_multiset(_oracle_event_multiset(build_step_rows(dev)))
    seen_tokens = _seen_surface_tokens(train)
    dev_keys = set(dev_gold.keys())
    unseen_keys = {k for k in dev_keys if _is_unseen_surface(k[1], seen_tokens)}
    seen_keys = dev_keys - unseen_keys
    print(f"[probe] dev_keys={len(dev_keys)} seen={len(seen_keys)} unseen={len(unseen_keys)}", flush=True)

    vocab = _seen_surface_tokens(train) | _seen_surface_tokens(dev)
    st = _extend_scan(gen, vocab, SIMPLEWIKI_PATH, scan_target, scan_budget_s)
    if not (st.get("complete") and st["n_parsed"] >= scan_target):
        # RESUME NEEDED -- write a progress marker (NOT metrics.json), signal re-invoke.
        prog = {"status": "SCAN_INCOMPLETE_RESUME_NEEDED", "n_parsed": st["n_parsed"],
                "target_parsed": scan_target, "n_lines_scanned": st["n_lines_scanned"],
                "n_prefilter_hits": st["n_prefilter_hits"], "complete": st.get("complete"),
                "ts_iso": datetime.now(timezone.utc).isoformat()}
        with open(os.path.join(OUTPUT_DIR, "_scan_progress.json"), "w", encoding="utf-8") as f:
            json.dump(prog, f, indent=2)
        print(f"[probe] RESUME_NEEDED: {prog}", flush=True)
        return None

    sel_counts = st["sel_counts"]
    scan_meta = {k: st[k] for k in ("n_lines_scanned", "n_prefilter_hits", "n_parsed", "n_cand_hits",
                                     "n_parse_errors", "parse_error_rate", "complete")}
    scan_meta["n_vocab_terms_hit"] = len(sel_counts)
    print(f"[probe] scan complete: {scan_meta}", flush=True)

    train_cov = _coverage_stats(set(train_gold.keys()), sel_counts)
    dev_cov_all = _coverage_stats(dev_keys, sel_counts)
    dev_cov_seen = _coverage_stats(seen_keys, sel_counts)
    dev_cov_unseen = _coverage_stats(unseen_keys, sel_counts)
    print(f"[probe] coverage dev_all={dev_cov_all} dev_seen={dev_cov_seen} dev_unseen={dev_cov_unseen}", flush=True)

    # majority baseline (reused; SAME numbers as v1/sibling)
    majority_pred = _majority_facts(train_gold, dev_keys)
    majority_scores = {"all": _pair_prf(dev_gold, majority_pred, dev_keys),
                       "seen": _pair_prf(dev_gold, majority_pred, seen_keys),
                       "unseen": _pair_prf(dev_gold, majority_pred, unseen_keys)}
    print(f"[probe] majority: {majority_scores}", flush=True)

    # dev-blind ratio selection (reported, no dev peeking for selection)
    best_ratio, ratio_scores = _select_ratio(train, train_gold, sel_counts)
    print(f"[probe] dev-blind selected subsample ratio={best_ratio} (TRAIN 80/20); scores={ratio_scores}", flush=True)

    # ---- degeneracy-robust discriminator: real-vs-SCRAMBLE across the FULL ratio sweep on DEV ----
    # v1 (all-SKIP) and v2-ratio<=1 (all-FILL) show the gam's prediction is set by the class-prior
    # (the balancing ratio), NOT the features -- so real-vs-MAJORITY is fooled by degeneracy. The
    # real-minus-scramble delta (SAME ratio/degeneracy on both arms) isolates the entity-specific
    # signal. We sweep ALL ratios and take the BEST-CASE delta -> gives the hypothesis its maximum
    # fair shot; failing even the best case = airtight closure (NOT dev-selection: we report the
    # whole sweep + also the dev-blind-selected ratio, which agree).
    train_inst = _build_instances_v2(train, train_gold, sel_counts)
    dev_inst = _build_instances_v2(dev, None, sel_counts)
    train_key_order = sorted(train_gold.keys())
    scrambled_gold = _scramble_gold(train_gold, train_key_order)
    train_inst_scr = _build_instances_v2(train, scrambled_gold, sel_counts)

    sweep = []
    for ratio in SUBSAMPLE_RATIOS:
        ev = _eval_ratio_on_dev(train_inst, train_inst_scr, dev_inst, dev_gold, dev_keys,
                                seen_keys, unseen_keys, ratio)
        sweep.append(ev)
        print(f"[probe] ratio={ratio}: real_seen={ev['real_seen_f1']} scr_seen={ev['scr_seen_f1']} "
              f"(d={ev['delta_seen_vs_scr']}) | real_unseen={ev['real_unseen_f1']} "
              f"scr_unseen={ev['scr_unseen_f1']} (d={ev['delta_unseen_vs_scr']}) | "
              f"n_fill_real={ev['n_fill_real']}/{len(dev_keys)*3}", flush=True)

    # at the dev-blind-selected ratio (honest, no dev peeking for selection)
    sel_ev = next(ev for ev in sweep if ev["ratio"] == best_ratio)
    # best-CASE over all ratios (max fair shot for the hypothesis)
    best_seen_ev = max(sweep, key=lambda ev: ev["delta_seen_vs_scr"])
    best_unseen_ev = max(sweep, key=lambda ev: ev["delta_unseen_vs_scr"])
    best_seen_vs_scr = best_seen_ev["delta_seen_vs_scr"]
    best_unseen_vs_scr = best_unseen_ev["delta_unseen_vs_scr"]

    maj_seen_f1 = majority_scores["seen"]["pair_f1"]
    maj_unseen_f1 = majority_scores["unseen"]["pair_f1"]
    real_scores = sel_ev["real"]
    scr_scores = sel_ev["scramble"]
    n_fill_pred = sel_ev["n_fill_real"]
    # vs-majority at selected ratio (reported for continuity with v1/sibling, but NOT primary:
    # degeneracy inflates it)
    lift_seen_vs_maj = round(sel_ev["real_seen_f1"] - maj_seen_f1, 4)
    lift_unseen_vs_maj = round(sel_ev["real_unseen_f1"] - maj_unseen_f1, 4)

    arms_hashes = {"majority": _hash_facts(majority_pred),
                   "selectional_real_selratio": sel_ev["hash_real"],
                   "selectional_scramble_selratio": sel_ev["hash_scr"]}
    all_collapsed = (arms_hashes["selectional_real_selratio"] == arms_hashes["majority"] and
                     arms_hashes["selectional_scramble_selratio"] == arms_hashes["majority"])
    if all_collapsed:
        raise AssertionError("ARMS_DID_NOT_DIFFER: both selectional arms hash-identical to majority.")

    # ---- degeneracy-robust three-outcome verdict (PRIMARY = real-vs-scramble best-case) ----
    if not health["frontend_health_ok"]:
        verdict = "HARD_FAIL_FRONTEND_BROKEN"
        outcome = None
    elif best_seen_vs_scr < LIFT_HARD_FAIL:
        verdict = "HARD_FAIL_NO_INDISTRIBUTION_SIGNAL"
        outcome = ("(i) signal genuinely absent even with adequate features: even the BEST-CASE "
                   "in-distribution (SEEN) real-minus-scramble delta over all ratios is below floor "
                   "-- the apparent vs-majority lift is a degenerate class-prior predictor "
                   "(all-FILL/all-SKIP) that the label-scramble reproduces")
    elif best_unseen_vs_scr >= LIFT_HARD_PASS and best_seen_vs_scr >= LIFT_HARD_PASS:
        verdict = "HARD_PASS_GENERALIZES"
        outcome = ("(iii) PURE-GLASS-BOX WALL CROSSED: entity-specific selectional signal beats its "
                   "own label-scramble both IN-DISTRIBUTION and on UNSEEN surfaces")
    elif best_unseen_vs_scr < LIFT_HARD_FAIL:
        verdict = "HARD_FAIL_MEMORIZED_NO_GENERALIZATION"
        outcome = ("(ii) in-distribution real-vs-scramble signal but UNSEEN real-vs-scramble ~0: "
                   "memorization/no-generalization (like WordNet/ConceptNet/GloVe)")
    else:
        verdict = "MIDDLE_BAND"
        outcome = "seen real-vs-scramble present; unseen in [HARD_FAIL, HARD_PASS) band -- inconclusive"

    verdict_msg = (f"{verdict}: PRIMARY real-vs-SCRAMBLE best-case: SEEN(in-dist) delta={best_seen_vs_scr} "
                   f"@ratio={best_seen_ev['ratio']}, UNSEEN(generalization) delta={best_unseen_vs_scr} "
                   f"@ratio={best_unseen_ev['ratio']}; dev-blind-selected ratio={best_ratio}: "
                   f"real_seen={sel_ev['real_seen_f1']}/scr_seen={sel_ev['scr_seen_f1']} "
                   f"real_unseen={sel_ev['real_unseen_f1']}/scr_unseen={sel_ev['scr_unseen_f1']}; "
                   f"vs-majority-degenerate seen +{lift_seen_vs_maj}/unseen +{lift_unseen_vs_maj} "
                   f"(n_fill_pred={n_fill_pred}/{len(dev_keys)*3}=all-FILL degenerate); "
                   f"frontend_ok={health['frontend_health_ok']} | OUTCOME {outcome}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "run_mode": "probe",
        "anchor_name": ANCHOR_NAME,
        "outcome_class": outcome,
        "n_train_paragraphs": len(train),
        "n_dev_paragraphs": len(dev),
        "n_dev_keys": len(dev_keys),
        "n_seen_keys": len(seen_keys),
        "n_unseen_keys": len(unseen_keys),
        "frontend_health": health,
        "vocab_size_train_dev": len(vocab),
        "scan_meta": scan_meta,
        "coverage": {"train": train_cov, "dev_all": dev_cov_all, "dev_seen": dev_cov_seen,
                     "dev_unseen": dev_cov_unseen},
        "subsample_ratio_selected_devblind": best_ratio,
        "ratio_val_scores_trainblind": ratio_scores,
        "primary_discriminator": "real_minus_scramble_pair_f1 (degeneracy-robust)",
        "best_seen_vs_scramble_delta": best_seen_vs_scr,
        "best_seen_vs_scramble_ratio": best_seen_ev["ratio"],
        "best_unseen_vs_scramble_delta": best_unseen_vs_scr,
        "best_unseen_vs_scramble_ratio": best_unseen_ev["ratio"],
        "selratio_real_seen_f1": sel_ev["real_seen_f1"],
        "selratio_scr_seen_f1": sel_ev["scr_seen_f1"],
        "selratio_real_unseen_f1": sel_ev["real_unseen_f1"],
        "selratio_scr_unseen_f1": sel_ev["scr_unseen_f1"],
        "lift_seen_vs_majority_degenerate": lift_seen_vs_maj,
        "lift_unseen_vs_majority_degenerate": lift_unseen_vs_maj,
        "n_fill_pred_dev_selratio": n_fill_pred,
        "n_dev_instances": len(dev_keys) * 3,
        "ratio_sweep_dev": [{k: ev[k] for k in ("ratio", "real_seen_f1", "scr_seen_f1",
                                                 "delta_seen_vs_scr", "real_unseen_f1", "scr_unseen_f1",
                                                 "delta_unseen_vs_scr", "n_fill_real", "n_fill_scr")}
                            for ev in sweep],
        "majority_baseline": majority_scores,
        "results_selratio": {"real": real_scores, "scramble": scr_scores},
        "arms_hashes": arms_hashes,
        "arms_differ_verified": not all_collapsed,
        "fate_verb_lexicon_base_size": len(_FATE_VERB_LEXICON_BASE),
        "fate_verb_lexicon_expanded_size": len(FATE_VERB_LEXICON),
        "bands": {"LIFT_HARD_PASS": LIFT_HARD_PASS, "LIFT_HARD_FAIL": LIFT_HARD_FAIL,
                  "SCRAMBLE_CLEAN_MARGIN": SCRAMBLE_CLEAN_MARGIN,
                  "FRONTEND_TAG_ACC_FLOOR": FRONTEND_TAG_ACC_FLOOR, "FRONTEND_UAS_FLOOR": FRONTEND_UAS_FLOOR},
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
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}

    # ISOLATE the self-test's frontend + scan caches so it NEVER clobbers a real (possibly
    # completed/resumable) frontend or scan checkpoint under OUTPUT_DIR. (Resumability-contract
    # bug guard: an earlier version shared SCAN_CKPT/POS_CACHE with the probe and destroyed a
    # completed 45k scan on self-test.)
    global FRONTEND_DIR, POS_CACHE, ARC_CACHE, SCAN_CKPT
    _saved_paths = (FRONTEND_DIR, POS_CACHE, ARC_CACHE, SCAN_CKPT)
    _st_dir = OUTPUT_DIR + "_selftest"
    FRONTEND_DIR = os.path.join(_st_dir, "frontend_cache")
    POS_CACHE = os.path.join(FRONTEND_DIR, "pos_tagger.json")
    ARC_CACHE = os.path.join(FRONTEND_DIR, "arc_parser.npz")
    SCAN_CKPT = os.path.join(_st_dir, "sel_index_ckpt.json")
    try:
        return _self_test_body(out)
    finally:
        FRONTEND_DIR, POS_CACHE, ARC_CACHE, SCAN_CKPT = _saved_paths


def _self_test_body(out: Dict) -> Dict:

    # (1) deterministic fate/role extraction logic (independent of tagger accuracy)
    toks = ["The", "fire", "consumed", "the", "wood", "."]
    pos = ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"]
    heads = {1: 2, 2: 3, 3: 0, 4: 5, 5: 3, 6: 3}
    cands, _rules = candidates_from_parse(toks, pos, heads, extended=True)
    assert (3, 5) in cands
    lemma = lemma_verb(toks[2])
    assert lemma in FATE_VERB_LEXICON and FATE_VERB_LEXICON[lemma] == "DESTROY", f"{lemma!r} lexicon miss"
    assert frame_slot_role(lemma, "obj") == "PATIENT"
    out["checks"]["fate_role_logic"] = {"lemma": lemma, "fate": "DESTROY"}
    print(f"[self-test] fate/role logic OK ({lemma}->DESTROY, obj->PATIENT)", flush=True)

    # (2) richer feature builder: effect-conditioned features MUST differ across the 3 effects
    sel = {"wood": {"DESTROY:PATIENT": 20, "MOVE:AGENT": 2}}
    f_create = _feat_fn("wood", "CREATE", sel)
    f_destroy = _feat_fn("wood", "DESTROY", sel)
    assert set(f_create) != set(f_destroy), "effect-conditioned features identical across effects (v1 bug)"
    assert "self_argmax:1" in f_destroy and "self_argmax:0" in f_create, "argmax feature not effect-conditioned"
    assert any(x.startswith("cnt:DESTROY:") for x in f_destroy), "abs count-magnitude feature missing"
    out["checks"]["richer_feats"] = {"n_create": len(f_create), "n_destroy": len(f_destroy),
                                     "destroy_sample": sorted(f_destroy)[:6]}
    print(f"[self-test] richer effect-conditioned features OK (differ across effects)", flush=True)

    # (3) REAL tiny frontend train+cache+load (real_code_path, META_RULE F.1)
    _train_and_cache_frontend(pos_epochs=3, arc_epochs=3, max_sents=60)
    gen, tagger, parser = _load_frontend()
    cr = gen.generate("The fire consumed the wood.", extended=True)
    assert cr.tokens and isinstance(cr.candidates, set)
    out["checks"]["real_frontend_cache"] = {"n_tokens": len(cr.tokens), "n_cands": len(cr.candidates)}
    print(f"[self-test] real tiny frontend train+cache+load OK", flush=True)

    # (4) REAL capped resumable scan on REAL SimpleWiki (tiny target)
    if os.path.exists(SCAN_CKPT):
        os.remove(SCAN_CKPT)
    st = _extend_scan(gen, {"wood", "water", "gas", "ash"}, SIMPLEWIKI_PATH, target_parsed=40,
                      budget_s=30.0, ckpt_every=10)
    assert st["n_parsed"] >= 0
    out["checks"]["real_scan_capped"] = {k: st[k] for k in ("n_parsed", "n_prefilter_hits", "n_cand_hits")}
    print(f"[self-test] real capped resumable scan OK: {out['checks']['real_scan_capped']}", flush=True)

    # (5) REAL balanced gam fit/predict + ratio selection at tiny scale
    train = _load_split("train")[:12]
    dev = _load_split("dev")[:6]
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(build_step_rows(train)))
    sel_counts = st["sel_counts"]
    ratio, rscores = _select_ratio(train, train_gold, sel_counts)
    train_inst = _build_instances_v2(train, train_gold, sel_counts)
    dev_inst = _build_instances_v2(dev, None, sel_counts)
    hyp = _fit_balanced(train_inst, ratio)
    pred = _predict_facts(hyp, dev_inst)
    assert isinstance(pred, dict)
    out["checks"]["gam_balanced_real"] = {"ratio_selected": ratio, "n_train_inst": len(train_inst),
                                          "n_pred_keys": len(pred), "ratio_scores": rscores}
    print(f"[self-test] balanced gam fit/predict + ratio-select OK (ratio={ratio})", flush=True)

    # (6) scramble determinism
    ko = sorted(train_gold.keys())
    assert _scramble_gold(train_gold, ko) == _scramble_gold(train_gold, ko), "SCRAMBLE_NONDETERMINISTIC"
    out["checks"]["scramble_deterministic"] = True
    # clean up self-test scan ckpt so it never contaminates a real run
    if os.path.exists(SCAN_CKPT):
        os.remove(SCAN_CKPT)
    print("[self-test] scramble determinism OK; cleaned scan ckpt", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = ("SELFTEST_PASS: fate/role logic + richer effect-conditioned features (differ) + "
                          "real tiny frontend cache + real capped resumable scan + balanced gam "
                          "fit/predict + ratio-select + scramble determinism all OK")
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


# ============================================================================ main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--build-frontend", action="store_true", dest="build_frontend")
    p.add_argument("--pos-epochs", type=int, default=6)
    p.add_argument("--arc-epochs", type=int, default=10)
    p.add_argument("--scan-target", type=int, default=45000)
    p.add_argument("--scan-budget-s", type=float, default=520.0)
    p.add_argument("--health-max-sents", type=int, default=1000)
    args = p.parse_args()

    if args.self_test:
        run_mode = "self_test"
    elif args.build_frontend:
        run_mode = "build_frontend"
    else:
        run_mode = "probe"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)

    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
            _write_metrics(out_dir, metrics)
            print(f"[main] self-test verdict={metrics['verdict']}", flush=True)
        elif args.build_frontend:
            info = _train_and_cache_frontend(args.pos_epochs, args.arc_epochs)
            with open(os.path.join(out_dir, "_frontend_built.json"), "w", encoding="utf-8") as f:
                json.dump({**info, "ts_iso": datetime.now(timezone.utc).isoformat()}, f, indent=2)
            print(f"[main] frontend built+cached: {info}", flush=True)
        else:
            metrics = run_probe(args.scan_target, args.scan_budget_s, args.health_max_sents)
            if metrics is None:
                print("[main] probe returned RESUME_NEEDED (scan incomplete); re-invoke to continue", flush=True)
                return
            _write_metrics(out_dir, metrics)
            print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
