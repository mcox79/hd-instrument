# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BOW/UNGROUNDED/GROUNDED/SCRAMBLE hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (cosine-gap discrimination measurement; no capacity/noise-floor CRLB threshold)
# - HP_SCOPE: {grounded_structured: [HARD_PASS/HARD_FAIL bands], scramble: [collapse check]}
#   BOW / UNGROUNDED_STRUCTURED are RE-MEASURED reference arms, not gated.
# - cardinality_ok: EXPECTED_N_UNITS = len(sample) instances
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (HYPERNYM_DEPTH/DECAY fixed before running;
#   see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL EventBundleCodec / extract_events / wordnet objects (real_code_path)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_focus_encode_grounded_event_discrimination_realprose_v1.md for the full pre-reg.
"""exp_focus_encode_grounded_event_discrimination_realprose_v1 -- E3 binding-constraint gate.

Does GROUNDING hdlab.event_bundle.EventBundleCodec's symbol layer (fillers = real semantic-similarity
vectors instead of a fresh random hypervector per new surface string) make the structured
{PRED,AGENT,PATIENT,TENSE} situation-model event representation discriminate same-scenario vs
different-scenario REAL MCScript2.0 dev narratives BETTER than (a) plain bag-of-words and (b) today's
ungrounded-random-filler structured baseline?

Design pointer: notes/research_e3_realprose_extraction_feasibility_scope_2026-08-10.md Section 4 (the
scoping drill that designed this gate after finding, live on real MCScript2.0 text, that the structured
FHRR event register discriminates WORSE (gap 0.028) than plain bag-of-words (gap 0.153) -- "structure
without grounding is actively worse than no structure at all"). Full implementation decisions (exact
grounding mechanism, n_dim, hypernym depth/decay, sample selection) in
preregs/2026-08-10_focus_encode_grounded_event_discrimination_realprose_v1.md.

FOUR arms per instance, all measured in-cell on the SAME extracted role_events (not cited):
  BOW                  : hdlab.event_bundle.EventBundleCodec.encode_bag_of_args over all content
                         words in the narrative, no role structure, ungrounded random fillers.
  UNGROUNDED_STRUCTURED: per-clause encode_event({PRED,AGENT,PATIENT,TENSE}), fillers = random on
                         first sight (today's EventBundleCodec production default), events
                         aggregated (bipolar sum + quantize) across the narrative.
  GROUNDED_STRUCTURED  : identical structured pipeline, fillers sourced via a TIERED grounding lookup
                         (Tier 1 hdlab.lexical_similarity 89-concept lexicon; Tier 2 NEW WordNet
                         hypernym-chain bipolar bag, open-vocabulary; Tier 3 random fallback).
  SCRAMBLE             : GROUNDED pipeline with role<->filler binding destroyed via a fixed
                         derangement (mandatory control -- discrimination must collapse if the gain
                         is genuinely role-structural, not just vocabulary co-occurrence).

Discriminator: matched-pair (same-scenario) mean cosine minus wrong-pair (different-scenario) mean
cosine, over all pairwise instance comparisons in the sample -- identical metric to the scoping drill's
own Stage-1b/1c measurements.

ONE tokenizer throughout (deliberate simplification vs the scoping drill's sketch of composing
CandidateGenerator's arc-parse with extract_events' own tagger -- avoids a real cross-tokenizer
token-index alignment risk; B2 arc-parse robustness was already independently confirmed in the
MCScript2.0 arc and is not the variable under test here). See prereg "Design" section for the full
rationale.

Modes:
  --self-test  Real-code-path check: SIMPLE_PRESENT patch fires additively + reproduces base
               extract_events bit-for-bit elsewhere; grounding tiers fire; same-lemma pair grounds to
               cosine 1.0; arms-must-differ on a tiny synthetic corpus. No queue dispatch.
  --smoke      Small real MCScript2.0 sample (<=15 instances, >=5 scenarios), SAME mechanism as full.
  --full       Full real MCScript2.0 sample (<=60 instances, >=12 scenarios).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import base64
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES  # noqa: E402
from hdlab.role_slot_summarizer import (  # noqa: E402
    _bipolar_bind,
    _bipolar_quantize,
    _bipolar_random,
)
import hdlab.lexical_similarity as _ls  # noqa: E402
from hdlab.mcscript_extraction import parse_mcscript_xml, split_sentences  # noqa: E402
from experiments._temporal_ordering import (  # noqa: E402
    extract_events as _base_extract_events,
    Event,
    AUX_LEMMAS,
    TENSE_SIMPLE_PAST,
)
from tools import exp_checkpoint as _ckpt  # noqa: E402

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ANCHOR_NAME = "focus_encode_grounded_event_discrimination_realprose_v1"
REPO_ROOT = Path(_REPO)
CORPUS_PATH = REPO_ROOT / "data" / "corpora" / "mcscript2" / "extracted" / "dev-data.xml"
OUTPUT_DIR = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"

N_DIM = 8192
SEED = 7
TENSE_SIMPLE_PRESENT = "SIMPLE_PRESENT"
HYPERNYM_DEPTH = 3          # self synset + up to 3 ancestor hypernyms; calibrated at design time
                             # (manual chain inspection) to avoid over-genericity collapse (see prereg)
DECAY = 0.7                 # decaying bind-weight per hypernym hop (closer concept dominates)
NOMINAL_TAGS = frozenset({"NN", "NNS", "NNP", "NNPS", "PRP"})
SCRAMBLE_PERM = [1, 2, 3, 0]  # fixed derangement over (PRED, AGENT, PATIENT, TENSE)
NONE_FILLER = "_NONE_"

N_SCENARIOS_FULL = 15
MAX_PER_SCENARIO_FULL = 4
N_SCENARIOS_SMOKE = 5
MAX_PER_SCENARIO_SMOKE = 3

# Pre-registered bands (preregs/2026-08-10_focus_encode_grounded_event_discrimination_realprose_v1.md),
# adopted unchanged from the scoping drill's Section 4 design.
HARD_PASS_BOW_MATCH = 0.153     # HYPOTHESIZED@notes/research_e3_realprose_extraction_feasibility_scope_2026-08-10.md
HARD_PASS_LIFT_MULT = 3.0
HARD_PASS_SCRAMBLE_CEIL = 0.02
HARD_FAIL_GROUNDED_FLOOR = 0.05
HARD_FAIL_SCRAMBLE_FRAC = 0.5


# =====================================================================================
# Tense-fix: cell-local ADDITIVE patch (Section 3(ii)/Section 5 fix), held identical
# across all 4 arms so grounding remains the ONE variable under test.
# =====================================================================================
def extract_events_present_patched(text: str) -> Tuple[List[Event], list]:
    """extract_events + a SIMPLE_PRESENT branch for VBP/VBZ (mirrors the five existing
    branches). ADDITIVE ONLY: never alters an event the base function already found."""
    events, tagged = _base_extract_events(text)
    have_idx = {e.idx for e in events}
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    for i, (low, pos) in enumerate(zip(lows, poss)):
        if i in have_idx or low in AUX_LEMMAS:
            continue
        if pos in ("VBP", "VBZ"):
            events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_SIMPLE_PRESENT, is_pp=False))
    events.sort(key=lambda e: e.idx)
    return events, tagged


def assign_roles(tagged: list, event_idx: int) -> Tuple[Optional[str], Optional[str]]:
    """Positional nearest-nominal AGENT (pre-verbal)/PATIENT (post-verbal), closest-to-verb
    tie-break -- mirrors hdlab.mcscript_extraction.extract_args's convention, executed on the
    SAME single tokenizer extract_events already uses (see prereg 'Design' for rationale)."""
    agent = None
    for j in range(event_idx - 1, -1, -1):
        if tagged[j][2] in NOMINAL_TAGS:
            agent = tagged[j][1]
            break
    patient = None
    for j in range(event_idx + 1, len(tagged)):
        if tagged[j][2] in NOMINAL_TAGS:
            patient = tagged[j][1]
            break
    return agent, patient


def build_instance_role_events(text: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """Per-instance: list of {PRED,AGENT,PATIENT,TENSE} role-filler dicts (one per extracted
    clause event; AGENT/PATIENT default to the shared NONE_FILLER placeholder when absent) +
    the bag of content words (all VB*/nominal tokens, aux excluded) across the narrative."""
    role_events: List[Dict[str, str]] = []
    content_words: List[str] = []
    for s in split_sentences(text):
        events, tagged = extract_events_present_patched(s)
        for e in events:
            agent, patient = assign_roles(tagged, e.idx)
            role_events.append({
                "PRED": e.lemma,
                "AGENT": agent if agent is not None else NONE_FILLER,
                "PATIENT": patient if patient is not None else NONE_FILLER,
                "TENSE": e.tense,
            })
        for (_surf, low, pos) in tagged:
            if (pos.startswith("VB") or pos in NOMINAL_TAGS) and low not in AUX_LEMMAS:
                content_words.append(low)
    return role_events, content_words


# =====================================================================================
# Grounding: TIERED lookup (Tier 1 REUSE hdlab.lexical_similarity; Tier 2 NEW WordNet
# hypernym-chain bipolar bag; Tier 3 random fallback == ungrounded arm's behavior).
# =====================================================================================
def _synset_seed_vec(synset_name: str, n_dim: int) -> torch.Tensor:
    """Deterministic bipolar vector for a WordNet synset name (hashlib, NEVER python hash())."""
    h = hashlib.sha256(("WNSYN::" + synset_name).encode("ascii")).digest()
    seed = int.from_bytes(h[:8], "big") % (2**31 - 1)
    gen = torch.Generator().manual_seed(seed)
    return _bipolar_random((n_dim,), gen)


_wn_cache: Dict[Tuple[str, str, int], Optional[torch.Tensor]] = {}
_lemmatizer = None


def _lemma(word: str, wn_pos: str) -> str:
    global _lemmatizer
    if _lemmatizer is None:
        from nltk.stem import WordNetLemmatizer
        _lemmatizer = WordNetLemmatizer()
    return _lemmatizer.lemmatize(word.lower(), pos=wn_pos)


def wordnet_hypernym_vec(word: str, wn_pos: str, n_dim: int) -> Optional[torch.Tensor]:
    """Tier-2 grounding: decay-weighted bag of {synset, hypernym-chain} bipolar bundle.
    None if `word` is OOV of WordNet at the given POS."""
    from nltk.corpus import wordnet as wn

    key = (word, wn_pos, n_dim)
    if key in _wn_cache:
        return _wn_cache[key]
    synsets = wn.synsets(word, pos=wn_pos)
    if not synsets:
        _wn_cache[key] = None
        return None
    syn = synsets[0]
    chain = [syn]
    cur = syn
    for _ in range(HYPERNYM_DEPTH):
        hyp = cur.hypernyms()
        if not hyp:
            break
        cur = hyp[0]
        chain.append(cur)
    acc = torch.zeros(n_dim, dtype=torch.float32)
    for depth, s in enumerate(chain):
        w = DECAY ** depth
        acc = acc + w * _synset_seed_vec(s.name(), n_dim)
    v = _bipolar_quantize(acc)
    _wn_cache[key] = v
    return v


def grounded_vec(word: str, role: str, n_dim: int) -> Tuple[Optional[torch.Tensor], str]:
    """Tiered grounding lookup for a filler word given its ROLE (PRED -> verb POS hint,
    AGENT/PATIENT -> noun POS hint). Returns (vector_or_None, tier_used)."""
    from nltk.corpus import wordnet as wn

    w = word.lower()
    if w == NONE_FILLER.lower():
        return None, "none_filler"
    wn_pos = wn.VERB if role == "PRED" else wn.NOUN
    if n_dim == _ls.N_DIM and _ls.in_lexicon(w):
        cv = _ls.concept_vector(w)  # complex64, N_DIM=8192
        bip = torch.sign(torch.real(cv))
        bip[bip == 0] = 1.0
        return bip.to(torch.float32), "lexical_similarity"
    lemma = _lemma(w, wn_pos)
    v = wordnet_hypernym_vec(lemma, wn_pos, n_dim)
    if v is not None:
        return v, "wordnet_hypernym"
    v2 = wordnet_hypernym_vec(w, wn_pos, n_dim)
    if v2 is not None:
        return v2, "wordnet_hypernym_surface"
    return None, "oov_random_fallback"


def build_grounded_codec(n_dim: int, seed: int, pred_words: Sequence[str],
                          arg_words: Sequence[str]) -> Tuple[EventBundleCodec, dict]:
    """Pre-inject grounded vectors for every symbol grounding covers; ungrounded symbols are
    left for EventBundleCodec's own lazy `_bipolar_random` fallback (Tier 3, identical to the
    ungrounded arm's behavior)."""
    grounded: Dict[str, torch.Tensor] = {}
    tier_counts = {"lexical_similarity": 0, "wordnet_hypernym": 0,
                  "wordnet_hypernym_surface": 0, "oov_random_fallback": 0, "none_filler": 0}
    for w in sorted(set(pred_words)):
        v, tier = grounded_vec(w, "PRED", n_dim)
        tier_counts[tier] += 1
        if v is not None and w not in grounded:
            grounded[w] = v
    for w in sorted(set(arg_words)):
        if w in grounded:
            continue
        v, tier = grounded_vec(w, "AGENT", n_dim)
        tier_counts[tier] += 1
        if v is not None:
            grounded[w] = v
    syms = sorted(grounded.keys())
    vecs = torch.stack([grounded[s] for s in syms], 0) if syms else torch.empty((0, n_dim), dtype=torch.float32)
    codec = EventBundleCodec(n_dim=n_dim, seed=seed, symbols=syms, symbol_codebook=vecs)
    coverage = {
        "n_pred_words": len(set(pred_words)), "n_arg_words": len(set(arg_words)),
        "n_grounded_total": len(grounded), "tier_counts": tier_counts,
    }
    return codec, coverage


# =====================================================================================
# Encoding / aggregation.
# =====================================================================================
def encode_instance_structured(role_events: List[Dict[str, str]], codec: EventBundleCodec,
                                scrambled: bool = False) -> Optional[torch.Tensor]:
    if not role_events:
        return None
    acc = torch.zeros(codec.n_dim, dtype=torch.float32)
    for rf in role_events:
        if scrambled:
            acc = acc + codec.encode_scrambled_event(rf, SCRAMBLE_PERM)
        else:
            acc = acc + codec.encode_event(rf)
    return _bipolar_quantize(acc)


def encode_instance_bow(content_words: List[str], codec: EventBundleCodec) -> Optional[torch.Tensor]:
    if not content_words:
        return None
    return codec.encode_bag_of_args(content_words)


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    na = a.norm().item()
    nb = b.norm().item()
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(torch.dot(a, b).item() / (na * nb))


def matched_wrong_gap(vecs: Dict[str, Optional[torch.Tensor]], scenario_by_id: Dict[str, str]):
    ids = sorted([i for i in vecs if vecs[i] is not None])
    matched, wrong = [], []
    for a_i in range(len(ids)):
        for b_i in range(a_i + 1, len(ids)):
            ia, ib = ids[a_i], ids[b_i]
            c = cosine(vecs[ia], vecs[ib])
            (matched if scenario_by_id[ia] == scenario_by_id[ib] else wrong).append(c)
    mm = sum(matched) / len(matched) if matched else float("nan")
    mw = sum(wrong) / len(wrong) if wrong else float("nan")
    return {"matched_mean": mm, "wrong_mean": mw, "gap": mm - mw,
            "n_matched_pairs": len(matched), "n_wrong_pairs": len(wrong),
            "n_instances_scored": len(ids)}


def _hash_vec(v: Optional[torch.Tensor]) -> str:
    if v is None:
        return "NONE"
    return hashlib.sha256(v.numpy().tobytes()).hexdigest()


def _arms_must_differ(per_arm_vecs: Dict[str, Dict[str, Optional[torch.Tensor]]]) -> dict:
    """META_RULE_AF: pairwise hash-differ across arms, checked on the CONCATENATION of all
    instance vectors per arm (order-stable, sorted by instance id)."""
    digests = {}
    for arm, vecs in per_arm_vecs.items():
        ids = sorted(vecs.keys())
        h = hashlib.sha256()
        for i in ids:
            h.update(_hash_vec(vecs[i]).encode("ascii"))
        digests[arm] = h.hexdigest()
    names = sorted(digests.keys())
    all_differ = True
    pairs = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            same = digests[a] == digests[b]
            pairs[f"{a}__vs__{b}"] = "IDENTICAL" if same else "DIFFERS"
            if same:
                all_differ = False
    return {"all_differ": all_differ, "digests": digests, "pairs": pairs}


# =====================================================================================
# Sample selection (deterministic; sorted(), no hash()/list(set()) per PROT-023).
# =====================================================================================
def select_sample(corpus_path: Path, n_scenarios: int, max_per_scenario: int) -> List[dict]:
    insts = parse_mcscript_xml(str(corpus_path))
    by_scn: Dict[str, List[dict]] = {}
    for inst in insts:
        by_scn.setdefault(inst["scenario"], []).append(inst)
    multi = {k: v for k, v in by_scn.items() if len(v) >= 2}
    ranked = sorted(multi.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    chosen = ranked[:n_scenarios]
    sample: List[dict] = []
    for _scn, lst in chosen:
        lst_sorted = sorted(lst, key=lambda d: d["id"])
        sample.extend(lst_sorted[:max_per_scenario])
    sample.sort(key=lambda d: d["id"])
    return sample


def _vec_to_b64(v: torch.Tensor) -> str:
    arr = v.to(torch.int8).numpy()
    return base64.b64encode(arr.tobytes()).decode("ascii")


def _b64_to_vec(s: str, n_dim: int) -> torch.Tensor:
    import numpy as np
    arr = np.frombuffer(base64.b64decode(s), dtype=np.int8)
    return torch.from_numpy(arr.copy()).to(torch.float32)


# =====================================================================================
# Main pipeline: pass 1 (extraction, checkpointed) -> grounding table -> pass 2 (encode).
# =====================================================================================
def run_pipeline(sample: List[dict], output_dir: Path, n_dim: int = N_DIM,
                  seed: int = SEED) -> dict:
    output_dir = Path(output_dir)
    scenario_by_id = {inst["id"]: inst["scenario"] for inst in sample}

    # ---- pass 1: extraction (checkpointed per instance) ----
    done = _ckpt.completed_units(str(output_dir))
    for inst in sample:
        key = _ckpt.unit_key("extract", inst["id"])
        if key in done:
            continue
        role_events, content_words = build_instance_role_events(inst["text"])
        _ckpt.record_unit(str(output_dir), key,
                          {"instance_id": inst["id"], "scenario": inst["scenario"],
                           "role_events": role_events, "content_words": content_words})
        print(f"[pass1] instance={inst['id']} scenario={inst['scenario']!r} "
              f"n_events={len(role_events)} n_content_words={len(content_words)}", flush=True)
    units = _ckpt.load_units(str(output_dir))
    extracted = {}
    for inst in sample:
        key = _ckpt.unit_key("extract", inst["id"])
        if key in units:
            extracted[inst["id"]] = units[key]

    n_extraction_miss = sum(1 for v in extracted.values() if not v["role_events"])
    print(f"[pass1] done: {len(extracted)}/{len(sample)} instances "
          f"({n_extraction_miss} with zero events)", flush=True)

    # ---- grounding table (global vocab, sorted deterministic) ----
    pred_words, arg_words = [], []
    for v in extracted.values():
        for rf in v["role_events"]:
            pred_words.append(rf["PRED"])
            if rf["AGENT"] != NONE_FILLER:
                arg_words.append(rf["AGENT"])
            if rf["PATIENT"] != NONE_FILLER:
                arg_words.append(rf["PATIENT"])
    codec_grounded, coverage = build_grounded_codec(n_dim, seed, pred_words, arg_words)
    codec_ungrounded = EventBundleCodec(n_dim=n_dim, seed=seed)
    print(f"[grounding] coverage={coverage}", flush=True)

    # ---- pass 2: encode 4 arms per instance ----
    bow_vecs, ungr_vecs, gnd_vecs, scr_vecs = {}, {}, {}, {}
    for iid, v in extracted.items():
        bow_vecs[iid] = encode_instance_bow(v["content_words"], codec_ungrounded)
        ungr_vecs[iid] = encode_instance_structured(v["role_events"], codec_ungrounded, scrambled=False)
        gnd_vecs[iid] = encode_instance_structured(v["role_events"], codec_grounded, scrambled=False)
        scr_vecs[iid] = encode_instance_structured(v["role_events"], codec_grounded, scrambled=True)

    # NaN/Inf defensive check (should never fire; bipolar quantize is always finite).
    for name, vecs in (("BOW", bow_vecs), ("UNGROUNDED_STRUCTURED", ungr_vecs),
                      ("GROUNDED_STRUCTURED", gnd_vecs), ("SCRAMBLE", scr_vecs)):
        for iid, v in vecs.items():
            if v is not None and not torch.isfinite(v).all():
                raise RuntimeError(f"NON_FINITE_VECTOR arm={name} instance={iid}")

    gap_bow = matched_wrong_gap(bow_vecs, scenario_by_id)
    gap_ungr = matched_wrong_gap(ungr_vecs, scenario_by_id)
    gap_gnd = matched_wrong_gap(gnd_vecs, scenario_by_id)
    gap_scr = matched_wrong_gap(scr_vecs, scenario_by_id)

    per_arm_vecs = {"BOW": bow_vecs, "UNGROUNDED_STRUCTURED": ungr_vecs,
                    "GROUNDED_STRUCTURED": gnd_vecs, "SCRAMBLE": scr_vecs}
    diff = _arms_must_differ(per_arm_vecs)

    # concrete example passages: first matched-pair (same scenario) with events + cosines.
    examples = []
    scn_groups: Dict[str, List[str]] = {}
    for iid, scn in scenario_by_id.items():
        if iid in extracted:
            scn_groups.setdefault(scn, []).append(iid)
    for scn in sorted(scn_groups):
        ids = sorted(scn_groups[scn])
        if len(ids) >= 2 and gnd_vecs.get(ids[0]) is not None and gnd_vecs.get(ids[1]) is not None:
            a, b = ids[0], ids[1]
            examples.append({
                "scenario": scn, "instance_a": a, "instance_b": b,
                "text_a_snippet": next(inst["text"] for inst in sample if inst["id"] == a)[:200],
                "text_b_snippet": next(inst["text"] for inst in sample if inst["id"] == b)[:200],
                "role_events_a": extracted[a]["role_events"][:3],
                "role_events_b": extracted[b]["role_events"][:3],
                "cos_bow": cosine(bow_vecs[a], bow_vecs[b]),
                "cos_ungrounded": cosine(ungr_vecs[a], ungr_vecs[b]),
                "cos_grounded": cosine(gnd_vecs[a], gnd_vecs[b]),
            })
        if len(examples) >= 3:
            break

    return {
        "n_sample": len(sample), "n_extracted": len(extracted),
        "n_extraction_miss": n_extraction_miss,
        "cardinality_ok": len(extracted) == len(sample),
        "coverage": coverage,
        "gap_bow": gap_bow, "gap_ungrounded_structured": gap_ungr,
        "gap_grounded_structured": gap_gnd, "gap_scramble": gap_scr,
        "arms_differ_check": diff, "arms_differ_verified": diff["all_differ"],
        "examples": examples,
    }


# =====================================================================================
# Verdict logic.
# =====================================================================================
def apply_bands(result: dict) -> Tuple[str, str]:
    gap_gnd = result["gap_grounded_structured"]["gap"]
    gap_ungr = result["gap_ungrounded_structured"]["gap"]
    gap_bow = result["gap_bow"]["gap"]
    gap_scr = result["gap_scramble"]["gap"]
    if not result["cardinality_ok"]:
        return "HARD_FAIL", f"CARDINALITY_BREACH: extracted {result['n_extracted']}/{result['n_sample']}"
    if not result["arms_differ_verified"]:
        return "HARD_FAIL", f"ARMS_IDENTICAL: {result['arms_differ_check']['pairs']}"
    import math
    if any(math.isnan(x) for x in (gap_gnd, gap_ungr, gap_bow, gap_scr)):
        return "HARD_FAIL", "NAN_GAP: insufficient matched or wrong pairs in sample"

    hard_pass = (gap_gnd >= HARD_PASS_BOW_MATCH and
                gap_ungr > 0 and gap_gnd >= HARD_PASS_LIFT_MULT * gap_ungr and
                gap_scr <= HARD_PASS_SCRAMBLE_CEIL)
    hard_fail = (gap_gnd < HARD_FAIL_GROUNDED_FLOOR or
                (gap_gnd > 0 and gap_scr > HARD_FAIL_SCRAMBLE_FRAC * gap_gnd))
    if hard_pass:
        msg = (f"HARD_PASS: gap_grounded={gap_gnd:.4f} >= bow={gap_bow:.4f} threshold "
              f"{HARD_PASS_BOW_MATCH:.3f} AND >= {HARD_PASS_LIFT_MULT}x ungrounded "
              f"({gap_ungr:.4f}) AND scramble={gap_scr:.4f} <= {HARD_PASS_SCRAMBLE_CEIL}")
        return "HARD_PASS", msg
    if hard_fail:
        msg = (f"HARD_FAIL: gap_grounded={gap_gnd:.4f} (floor {HARD_FAIL_GROUNDED_FLOOR}) "
              f"scramble={gap_scr:.4f} vs {HARD_FAIL_SCRAMBLE_FRAC}x-grounded="
              f"{HARD_FAIL_SCRAMBLE_FRAC * gap_gnd:.4f}")
        return "HARD_FAIL", msg
    msg = (f"MIDDLE_BAND: gap_grounded={gap_gnd:.4f} gap_ungrounded={gap_ungr:.4f} "
          f"gap_bow={gap_bow:.4f} gap_scramble={gap_scr:.4f}")
    return "MIDDLE_BAND", msg


# =====================================================================================
# Self-test.
# =====================================================================================
def self_test() -> dict:
    checks = {}

    # (1) SIMPLE_PRESENT patch fires additively.
    text_present = "He places the cup on the table ."
    ev_present, _ = extract_events_present_patched(text_present)
    fired = any(e.tense == TENSE_SIMPLE_PRESENT for e in ev_present)
    assert fired, f"SIMPLE_PRESENT patch did not fire on present-tense text: {ev_present}"
    checks["simple_present_fires"] = True

    # (2) reproduces base extract_events bit-for-bit on past-tense text (additive-only proof).
    text_past = "He placed the cup on the table ."
    ev_past, _ = extract_events_present_patched(text_past)
    base_ev, _ = _base_extract_events(text_past)
    same = [(e.lemma, e.idx, e.tense) for e in ev_past] == [(e.lemma, e.idx, e.tense) for e in base_ev]
    assert same, f"patch altered past-tense behavior: {ev_past} vs base {base_ev}"
    checks["additive_only_verified"] = True
    assert any(e.tense == TENSE_SIMPLE_PAST for e in ev_past), "SIMPLE_PAST branch broke"

    # (3) Tier-1 grounding fires at n_dim=8192 (real hdlab.lexical_similarity call).
    v1, tier1 = grounded_vec("happy", "AGENT", _ls.N_DIM)
    assert v1 is not None and tier1 == "lexical_similarity", f"Tier-1 did not fire: {tier1}"
    checks["tier1_lexical_similarity_fires"] = True

    # (4) Tier-2 WordNet grounding fires on open-vocabulary real words; total OOV -> None.
    v2, tier2 = grounded_vec("crack", "PRED", 512)
    assert v2 is not None and tier2.startswith("wordnet_hypernym"), f"Tier-2 did not fire: {tier2}"
    v3, tier3 = grounded_vec("zzznotarealwordzzzxx", "PRED", 512)
    assert v3 is None and tier3 == "oov_random_fallback", f"OOV should be None/fallback: {tier3}"
    checks["tier2_wordnet_fires_and_oov_safe"] = True

    # (5) same-lemma pair grounds to cosine 1.0 (deterministic mechanism-fires floor).
    va, ta = grounded_vec("places", "PRED", 512)
    vb, tb = grounded_vec("placed", "PRED", 512)
    assert va is not None and vb is not None
    cos_same = cosine(va, vb)
    assert cos_same > 0.999, f"same-lemma pair (places/placed) cosine {cos_same} not ~1.0"
    checks["same_lemma_cosine"] = round(cos_same, 4)

    # (6) arms-must-differ on a tiny synthetic 4-instance / 2-scenario corpus (real code path).
    synth = [
        {"id": "s0", "scenario": "cooking", "text": "I cracked the egg . I poured the mixture ."},
        {"id": "s1", "scenario": "cooking", "text": "She broke the egg . She stirred the batter ."},
        {"id": "s2", "scenario": "sports", "text": "He kicked the ball . He scored a goal ."},
        {"id": "s3", "scenario": "sports", "text": "They passed the ball . They won the match ."},
    ]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res = run_pipeline(synth, Path(td), n_dim=512, seed=SEED)
    checks["synthetic_arms_differ"] = res["arms_differ_check"]
    assert res["arms_differ_verified"], f"arms did not differ on synthetic corpus: {res['arms_differ_check']}"
    checks["synthetic_cardinality_ok"] = res["cardinality_ok"]
    assert res["cardinality_ok"]

    # (7) real-code-path: WordNet-hypernym vec + EventBundleCodec injection roundtrip is finite.
    codec, coverage = build_grounded_codec(512, SEED, ["crack", "pour"], ["egg", "mixture"])
    assert coverage["n_grounded_total"] >= 1, f"no words grounded in tiny real vocab: {coverage}"
    ev = codec.encode_event({"PRED": "crack", "AGENT": "_NONE_", "PATIENT": "egg", "TENSE": "SIMPLE_PAST"})
    assert torch.isfinite(ev).all()
    checks["grounded_codec_roundtrip_finite"] = True
    checks["tiny_real_vocab_coverage"] = coverage

    return checks


# =====================================================================================
# Metrics write.
# =====================================================================================
def _write_metrics(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    import traceback
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME,
        "pid": os.getpid(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2, default=str)
    os.replace(tmp, final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        checks = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "checks": checks}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = Path(str(OUTPUT_DIR) + "_smoke") if args.smoke else OUTPUT_DIR
    n_scn = N_SCENARIOS_SMOKE if args.smoke else N_SCENARIOS_FULL
    max_per = MAX_PER_SCENARIO_SMOKE if args.smoke else MAX_PER_SCENARIO_FULL

    t0 = time.time()
    sample = select_sample(CORPUS_PATH, n_scn, max_per)
    n_scenarios_actual = len({inst["scenario"] for inst in sample})
    print(f"[{run_mode}] sample: {len(sample)} instances across {n_scenarios_actual} scenarios",
          flush=True)

    result = run_pipeline(sample, output_dir, n_dim=N_DIM, seed=SEED)
    verdict, msg = apply_bands(result)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM, "seed": SEED, "hypernym_depth": HYPERNYM_DEPTH, "decay": DECAY,
        "n_scenarios_actual": n_scenarios_actual,
        "expected_n_units": len(sample), "cardinality_ok": result["cardinality_ok"],
        "n_extracted": result["n_extracted"], "n_extraction_miss": result["n_extraction_miss"],
        "coverage": result["coverage"],
        "gap_bow": result["gap_bow"], "gap_ungrounded_structured": result["gap_ungrounded_structured"],
        "gap_grounded_structured": result["gap_grounded_structured"],
        "gap_scramble": result["gap_scramble"],
        "arms_differ_verified": result["arms_differ_verified"],
        "arms_differ_check": result["arms_differ_check"],
        "examples": result["examples"],
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "cosine-gap discrimination measurement on real narrative text; bands drawn from "
                    "a prior real measurement on the same corpus, not a synthetic capacity envelope",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: HYPERNYM_DEPTH=3/DECAY=0.7 fixed "
                            "before running smoke/full",
        "progress_logging": "print_flush_true",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("examples",)},
                     indent=2, default=str))
    print(json.dumps({"examples": metrics["examples"]}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
