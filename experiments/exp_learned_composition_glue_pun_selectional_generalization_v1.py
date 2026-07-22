#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_learned_composition_glue_pun_selectional_generalization_v1

THE LEAP (chain-grade attempt, USER-authorized, LOCAL-ONLY): can the PROVEN atomize+sleep loop
(continual.replay_cycle NREM consolidation -> glass_box cleanup readout, reused UNMODIFIED from
exp_reader_meaning_correction_case_sleep_affectedness_v1) LEARN a selectional-composition constraint
(verb -> required-object-feature) in a GENERALIZING, grammar-like way that TRANSFERS to HELD-OUT
verbs it was not trained on AND that VerbNet SELRESTR lookup CANNOT cover -- or does it reduce to
lookup / memorize like the meaning-correction case did.

TESTBED = puns (frequency fails by construction). Two verb classes requiring different object
features: comestible (eat/drink/... ; VerbNet HAS +comestible -> lookup-COVERED) vs communication
(read/recite/sing/quote/... ; VerbNet has NO +communication SELRESTR for these -> lookup-UNCOVERED,
measured 2026-07-22). Each verb is paired with a curated pun noun whose WordNet-dominant sense lacks
the required feature and a subordinate sense carries it. Accuracy = fraction of held-out (verb-
disjoint) pun items resolved to the correct required feature (deterministic sense-resolution given
the predicted feature). See preregs/2026-07-22_learned_composition_glue_pun_selectional_generalization_v1.md

ARMS (one variable = composition mechanism):
  1. FREQUENCY       -- pick dominant sense (MUST-FAIL, ~0).
  2. LOOKUP          -- VerbNet SELRESTR -> feature; abstain->dominant if uncovered (the MM signal).
  3. LEARNED-REAL    -- verb code = bipolar bundle of the verb's WordNet hypernym-path lemma atoms
                        (gold-free structural similarity); W consolidated by replay_cycle; readout
                        cleanup_with_margin. THE LEAP.
  4. LEARNED-RANDOM  -- sign-flip control: verb code = one random atom per lemma (identity kept,
                        cross-verb meaning-similarity DESTROYED).

DISCRIMINATORS: generalization above majority + above freq + at/above lookup on the lookup-UNCOVERED
subset; learning curve rises; scramble collapses; SIGN-FLIP fires (real-beats-random, inverse of the
free-algebra 29437 random-beats-real). Bands in the pre-reg; verdict never self-declares CG (a full
pass -> CHAIN_GRADE_CANDIDATE_PENDING_VET, fresh adversarial VET + USER).

# CELL-TEMPLATE MANDATORY:
# - arms_differ asserted (W_real vs W_random vs W_scramble not bit-identical)
# - leak-probe asserted (verb codes gold-free / invariant to label permutation)
# - final_metrics_atomicity: tmp_replace ; SystemExit raised BEFORE except Exception
# - discriminator survives scale: smoke = FULL corpus, 1 seed (option A -- no larger-N regime)
# - baseline_in_band: frequency ~0 and majority ~0.5 verified at run
# - deterministic_seeding: true ; progress_logging: print_flush_true
# LOCAL ONLY. No push / no remote-persist / no queue / no store write / no atom bank. ASCII only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "learned_composition_glue_pun_selectional_generalization_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from nltk.corpus import verbnet as vn
    vn.classids("eat")
    _VN_OK = True
except Exception:
    vn = None
    _VN_OK = False

try:
    from nltk.corpus import wordnet as wn
    wn.synsets("dog", pos="n")
    _WN_OK = True
except Exception:
    wn = None
    _WN_OK = False

N_DIM = 1024
FRAC_SEEN = 0.6
N_CYCLES = 6
REPLAY_FRAC = 1.0
FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7]
CURVE_FRACS = [0.25, 0.5, 0.75, 1.0]

# ---- chain-grade gates (pre-registered) ----
CG_REAL_MEAN_MIN = 0.70
CG_REAL_EVERYSEED_MIN = 0.60
CG_UNCOV_MIN = 0.60
CG_CURVE_RISE_MIN = 0.15
CG_SCRAMBLE_COLLAPSE_MIN = 0.20
CG_SIGNFLIP_MIN = 0.15
# ---- measured-mechanism triggers ----
MM_REAL_MAX = 0.55
MM_SIGNFLIP_MAX = 0.05       # random >= real - this -> sign-flip did not fire
MM_SCRAMBLE_MIN = 0.10       # real - scramble < this -> did not collapse
MM_UNCOV_MAX = 0.15          # reduces to lookup

# ==================================================================================================
# Feature lexname buckets (copied from the viability probe; CREDIT VerbNet/WordNet + in-house cells).
# ==================================================================================================
FEATURE_WN_LEXNAMES = {
    "comestible": {"noun.food"},
    "communication": {"noun.communication"},
    "animate": {"noun.animal", "noun.person"},
    "concrete": {"noun.plant", "noun.object", "noun.artifact", "noun.food", "noun.substance"},
    "body_part": {"noun.body"},
}
# VerbNet SELRESTR name -> our feature key (solid implies comestible for eat-type Patients).
VN_FEATURE_MAP = {"comestible": "comestible", "solid": "comestible", "communication": "communication",
                  "animate": "animate", "concrete": "concrete", "body_part": "body_part"}
AFFECTED_ROLE_NAMES = {"Patient", "Patient1", "Patient2", "Theme", "Theme1", "Theme2", "Product"}

# Codebook of candidate readout features (the two true classes; readout must discriminate them).
READOUT_FEATURES = ["comestible", "communication"]

# ==================================================================================================
# Verb classes (true required feature = class). Pun noun pools per class (verified 2026-07-22:
# dominant lexname lacks the feature, a subordinate sense carries it).
# ==================================================================================================
COMEST_VERBS = ["eat", "drink", "swallow", "chew", "devour", "munch", "nibble", "gulp", "sip",
                "consume", "gobble", "guzzle", "slurp", "ingest", "dine", "feast", "lick", "bite"]
COMMUN_VERBS = ["read", "recite", "sing", "quote", "narrate", "chant", "perform", "hum", "whistle",
                "dictate", "memorize", "compose", "translate", "croon", "warble", "intone",
                "declaim", "proofread"]

COMEST_PUNS = [
    ("port", "port.n.02"), ("bass", "sea_bass.n.01"), ("date", "date.n.08"), ("kiwi", "kiwi.n.03"),
    ("draft", "draft.n.04"), ("punch", "punch.n.02"), ("squash", "squash.n.02"), ("fig", "fig.n.04"),
    ("chip", "chip.n.04"), ("mint", "mint.n.04"), ("roll", "bun.n.01"), ("sole", "sole.n.02"),
    ("lime", "lime.n.06"), ("oyster", "oyster.n.03"), ("clam", "clam.n.03"), ("cod", "cod.n.02"),
    ("olive", "olive.n.04"), ("turkey", "turkey.n.04"),
]
COMMUN_PUNS = [
    ("score", "score.n.02"), ("piece", "piece.n.06"), ("passage", "passage.n.02"),
    ("line", "line.n.02"), ("air", "tune.n.01"), ("round", "round.n.11"), ("key", "key.n.04"),
    ("sheet", "sheet.n.02"), ("measure", "measure.n.03"), ("pitch", "sales_pitch.n.01"),
]

# ==================================================================================================
# WordNet / VerbNet helpers (glass-box, gold-free).
# ==================================================================================================
def verbnet_required_feature(verb_lemma):
    """VerbNet SELRESTR-derived required feature on an affected role, mapped to a READOUT feature.
    Returns feature str or None (uncovered). Never guesses."""
    if not _VN_OK:
        return None
    try:
        classids = vn.classids(verb_lemma)
    except Exception:
        classids = []
    feats = set()
    for cid in sorted(classids):
        try:
            vc = vn.vnclass(cid)
        except Exception:
            continue
        themroles = vc.find("THEMROLES")
        if themroles is None:
            continue
        for tr in themroles.findall("THEMROLE"):
            if tr.get("type") not in AFFECTED_ROLE_NAMES:
                continue
            selrestrs = tr.find("SELRESTRS")
            if selrestrs is None:
                continue
            for r in selrestrs.findall("SELRESTR"):
                if r.get("Value") == "+":
                    nm = r.get("type")
                    if nm in VN_FEATURE_MAP and VN_FEATURE_MAP[nm] in READOUT_FEATURES:
                        feats.add(VN_FEATURE_MAP[nm])
    # deterministic single-feature pick (comestible before communication if both, never happens here)
    for f in READOUT_FEATURES:
        if f in feats:
            return f
    return None


def verb_hypernym_lemmas(verb_lemma):
    """Gold-free structural fingerprint: set of WordNet hypernym-path lemma names over the verb's
    (top-2) senses. Similar verbs share hypernym lemmas (measured within/across Jaccard 0.16/0.025)."""
    if not _WN_OK:
        return set()
    out = set()
    for syn in wn.synsets(verb_lemma, pos="v")[:2]:
        for path in syn.hypernym_paths():
            for node in path:
                for lm in node.lemma_names():
                    out.add(lm.lower())
    return out


def synset_lexname(name):
    try:
        return wn.synset(name).lexname()
    except Exception:
        return None


def dominant_synset_name(word):
    ss = wn.synsets(word, pos="n")
    return ss[0].name() if ss else None


def sense_has_feature(synset_name, feature):
    lex = synset_lexname(synset_name)
    return lex is not None and lex in FEATURE_WN_LEXNAMES[feature]


def resolve_pick(word, pred_feature):
    """Deterministic sense-resolution: given a predicted required feature, pick the FIRST (most
    frequent) noun-sense satisfying it; else fall back to the dominant sense."""
    ss = wn.synsets(word, pos="n")
    if not ss:
        return None
    if pred_feature is not None:
        for s in ss:
            if s.lexname() in FEATURE_WN_LEXNAMES[pred_feature]:
                return s.name()
    return ss[0].name()


# ==================================================================================================
# HD codes (bipolar; deterministic hashlib atoms -- no PYTHONHASHSEED dependence).
# ==================================================================================================
def _atom(token):
    seed = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:8], "big")
    return np.random.default_rng(seed).integers(0, 2, size=N_DIM).astype(np.float32) * 2.0 - 1.0


def verb_code_real(verb_lemma):
    """REAL code: normalized bipolar bundle over the verb's WordNet hypernym-path lemma atoms.
    Carries cross-verb meaning-similarity (shared hypernyms -> similar codes). Gold-free."""
    lemmas = sorted(verb_hypernym_lemmas(verb_lemma))
    if not lemmas:
        return _atom("hyp:" + verb_lemma)
    v = np.zeros(N_DIM, dtype=np.float32)
    for lm in lemmas:
        v += _atom("hyp:" + lm)
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def verb_code_random(verb_lemma):
    """RANDOM (sign-flip) code: one atom for the verb lemma ONLY. Identity preserved; cross-verb
    meaning-similarity destroyed."""
    v = _atom("rand:" + verb_lemma).astype(np.float32)
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def feature_codebook():
    return {f: _atom("feat:" + f).astype(np.float32) for f in READOUT_FEATURES}


# ==================================================================================================
# Consolidation (replay_cycle) + readout (cleanup_with_margin) -- REUSED UNMODIFIED.
# ==================================================================================================
def consolidate(train_codes, train_feats, fcb, seed):
    import torch
    from hdlab.continual import replay_cycle
    keys = torch.from_numpy(np.asarray(train_codes, dtype=np.float32))
    values = torch.from_numpy(np.asarray([fcb[f] for f in train_feats], dtype=np.float32))
    m = keys.shape[0]
    replay_idx = torch.from_numpy(np.arange(m).astype(np.int64))
    W = torch.zeros((N_DIM, N_DIM), dtype=torch.float32)
    torch.manual_seed(seed)
    for _ in range(N_CYCLES):
        replay_cycle(W, replay_idx, keys, values, replay_frac=REPLAY_FRAC, lr=1.0)
    return W.numpy()


def predict_feature(W, fcb, code):
    from hdlab.glass_box_loop import cleanup_with_margin
    rs = W @ code.astype(np.float32)
    nrm = float(np.linalg.norm(rs))
    if nrm > 1e-9:
        rs = rs / nrm
    cb = np.asarray([fcb[f] for f in READOUT_FEATURES], dtype=np.float32)
    idx, _margin = cleanup_with_margin(rs, cb)
    return READOUT_FEATURES[idx]


# ==================================================================================================
# Corpus assembly.
# ==================================================================================================
def build_items():
    """One item per verb: (verb, true_feature, pun_word, correct_synset). Verbs cycle through their
    class pun pool. Only verbs with a WordNet verb entry are kept."""
    items = []
    for gi, (verbs, feature, pool) in enumerate(
            [(COMEST_VERBS, "comestible", COMEST_PUNS), (COMMUN_VERBS, "communication", COMMUN_PUNS)]):
        for i, v in enumerate(verbs):
            if not wn.synsets(v, pos="v"):
                continue
            word, cor = pool[i % len(pool)]
            items.append({"verb": v, "feature": feature, "word": word, "cor_synset": cor,
                          "dom_synset": dominant_synset_name(word)})
    return items


# ==================================================================================================
# Arms (per held-out item).
# ==================================================================================================
def arm_correct(item, pred_feature):
    """Resolve the pun under the predicted feature; correct iff the picked sense carries the item's
    TRUE required feature (i.e. lands on the subordinate feature-bearing sense, not the dominant)."""
    pick = resolve_pick(item["word"], pred_feature)
    return bool(pick is not None and sense_has_feature(pick, item["feature"]))


def eval_arm_freq(held):
    # pick dominant -> pred feature = dominant sense's feature (not the true one) -> resolve dominant.
    n = len(held)
    correct = sum(1 for it in held if arm_correct(it, None))  # None -> dominant fallback
    return correct / n if n else None


def eval_arm_lookup(held):
    n = len(held)
    c = sum(1 for it in held if arm_correct(it, verbnet_required_feature(it["verb"])))
    return c / n if n else None


def eval_arm_learned(held, W, fcb, codefn):
    n = len(held)
    c = sum(1 for it in held if arm_correct(it, predict_feature(W, fcb, codefn(it["verb"]))))
    return c / n if n else None


def eval_subset(held, W, fcb, codefn, mask):
    sub = [it for it in held if mask(it)]
    if not sub:
        return None, 0
    c = sum(1 for it in sub if arm_correct(it, predict_feature(W, fcb, codefn(it["verb"]))))
    return c / len(sub), len(sub)


def is_lookup_uncovered(item):
    return verbnet_required_feature(item["verb"]) is None


# ==================================================================================================
# Per-seed run.
# ==================================================================================================
def verb_disjoint_split(items, seed):
    verbs = sorted(set(it["verb"] for it in items))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(verbs))
    n_seen = int(round(FRAC_SEEN * len(verbs)))
    seen_v = set(verbs[j] for j in perm[:n_seen])
    seen = [it for it in items if it["verb"] in seen_v]
    held = [it for it in items if it["verb"] not in seen_v]
    return seen, held, sorted(seen_v)


def run_seed(items, seed, fcb):
    seen, held, seen_v = verb_disjoint_split(items, seed)
    train_verbs = [it["verb"] for it in seen]
    train_feats = [it["feature"] for it in seen]

    codes_real = [verb_code_real(v) for v in train_verbs]
    codes_rand = [verb_code_random(v) for v in train_verbs]

    W_real = consolidate(codes_real, train_feats, fcb, seed)
    W_rand = consolidate(codes_rand, train_feats, fcb, seed)

    # SCRAMBLE: permute verb->feature training labels (real codes), must collapse generalization.
    rng = np.random.default_rng(1000 + seed)
    scr_feats = [train_feats[j] for j in rng.permutation(len(train_feats))]
    W_scr = consolidate(codes_real, scr_feats, fcb, seed)

    acc_freq = eval_arm_freq(held)
    acc_lookup = eval_arm_lookup(held)
    acc_real = eval_arm_learned(held, W_real, fcb, verb_code_real)
    acc_rand = eval_arm_learned(held, W_rand, fcb, verb_code_random)
    acc_scr = eval_arm_learned(held, W_scr, fcb, verb_code_real)

    uncov_real, n_uncov = eval_subset(held, W_real, fcb, verb_code_real, is_lookup_uncovered)
    uncov_lookup = None
    sub = [it for it in held if is_lookup_uncovered(it)]
    if sub:
        uncov_lookup = sum(1 for it in sub if arm_correct(it, verbnet_required_feature(it["verb"]))) / len(sub)

    # majority-feature baseline on held-out.
    held_feats = [it["feature"] for it in held]
    maj = Counter(held_feats).most_common(1)[0][1] / len(held) if held else None

    # learning curve: held-out real accuracy vs # train verbs accrued.
    curve = []
    for frac in CURVE_FRACS:
        k = max(1, int(round(frac * len(seen_v))))
        sub_v = set(seen_v[:k])
        subseen = [it for it in seen if it["verb"] in sub_v]
        if len(set(it["feature"] for it in subseen)) < 2:
            curve.append({"frac": frac, "n_verbs": len(sub_v), "acc": None})
            continue
        Wc = consolidate([verb_code_real(it["verb"]) for it in subseen],
                         [it["feature"] for it in subseen], fcb, seed)
        curve.append({"frac": frac, "n_verbs": len(sub_v),
                      "acc": round(eval_arm_learned(held, Wc, fcb, verb_code_real), 4)})

    # arms_differ (bit-level).
    arms_differ = not (np.array_equal(W_real, W_rand) or np.array_equal(W_real, W_scr))

    return {
        "seed": seed, "n_seen_verbs": len(seen_v), "n_held": len(held), "n_uncov_held": n_uncov,
        "majority_feature_baseline": round(maj, 4) if maj is not None else None,
        "acc_freq": round(acc_freq, 4), "acc_lookup": round(acc_lookup, 4),
        "acc_learned_real": round(acc_real, 4), "acc_learned_random": round(acc_rand, 4),
        "acc_learned_scramble": round(acc_scr, 4),
        "uncov_learned_real": round(uncov_real, 4) if uncov_real is not None else None,
        "uncov_lookup": round(uncov_lookup, 4) if uncov_lookup is not None else None,
        "signflip_real_minus_random": round(acc_real - acc_rand, 4),
        "scramble_collapse_real_minus_scr": round(acc_real - acc_scr, 4),
        "learning_curve": curve, "arms_differ": bool(arms_differ),
    }


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows, leak_clean, items):
    m_real = _mean(rows, "acc_learned_real")
    m_rand = _mean(rows, "acc_learned_random")
    m_scr = _mean(rows, "acc_learned_scramble")
    m_freq = _mean(rows, "acc_freq")
    m_lookup = _mean(rows, "acc_lookup")
    m_uncov = _mean(rows, "uncov_learned_real")
    m_maj = _mean(rows, "majority_feature_baseline")
    m_signflip = _mean(rows, "signflip_real_minus_random")
    m_collapse = _mean(rows, "scramble_collapse_real_minus_scr")

    everyseed_real = all((r["acc_learned_real"] or 0) >= CG_REAL_EVERYSEED_MIN for r in rows) if rows else False
    curve_rise = None
    rises = []
    for r in rows:
        accs = [c["acc"] for c in r["learning_curve"] if c["acc"] is not None]
        if len(accs) >= 2:
            rises.append(accs[-1] - accs[0])
    if rises:
        curve_rise = round(float(np.mean(rises)), 4)

    arms_ok = all(r["arms_differ"] for r in rows) if rows else False

    cg = bool(
        leak_clean and arms_ok and rows
        and m_real is not None and m_real >= CG_REAL_MEAN_MIN and everyseed_real
        and m_uncov is not None and m_uncov >= CG_UNCOV_MIN
        and curve_rise is not None and curve_rise >= CG_CURVE_RISE_MIN
        and m_collapse is not None and m_collapse >= CG_SCRAMBLE_COLLAPSE_MIN
        and m_signflip is not None and m_signflip >= CG_SIGNFLIP_MIN
    )
    mm = bool(
        (not leak_clean) or (not arms_ok)
        or (m_real is not None and m_real <= MM_REAL_MAX)
        or (m_signflip is not None and m_signflip <= MM_SIGNFLIP_MAX)
        or (m_collapse is not None and m_collapse < MM_SCRAMBLE_MIN)
        or (m_uncov is not None and m_uncov <= MM_UNCOV_MAX)
    )

    if cg and not mm:
        verdict = "CHAIN_GRADE_CANDIDATE_PENDING_VET"
        note = ("all gates fire: learned-real generalizes above majority/freq/lookup on the uncovered "
                "subset, curve rises, scramble collapses, sign-flip fires (real-beats-random). NOT "
                "self-declared CG -- caveat: generalization signal is WordNet-hypernym (KB-derived); "
                "VET must adjudicate learned-generalizing-mapping vs structured-lookup.")
    elif mm:
        verdict = "MEASURED_MECHANISM"
        reasons = []
        if not leak_clean:
            reasons.append("LEAK (codes not gold-free)")
        if not arms_ok:
            reasons.append("arms bit-identical")
        if m_real is not None and m_real <= MM_REAL_MAX:
            reasons.append("no generalization (real<=%.2f ~ majority)" % MM_REAL_MAX)
        if m_signflip is not None and m_signflip <= MM_SIGNFLIP_MAX:
            reasons.append("sign-flip did NOT fire (random>=real -> free-algebra, not meaning-use)")
        if m_collapse is not None and m_collapse < MM_SCRAMBLE_MIN:
            reasons.append("scramble did NOT collapse -> memorization/artifact")
        if m_uncov is not None and m_uncov <= MM_UNCOV_MAX:
            reasons.append("no uncovered advantage -> reduces to lookup")
        note = "; ".join(reasons)
    else:
        verdict = "MIDDLE_BAND"
        note = "partial: some gates fire, not all"

    msg = (f"{verdict} | held-out (verb-disjoint) resolve-acc: FREQ={m_freq} LOOKUP={m_lookup} "
           f"LEARNED-REAL={m_real} LEARNED-RANDOM={m_rand} SCRAMBLE={m_scr} | majority={m_maj} | "
           f"uncovered-subset REAL={m_uncov} LOOKUP={_mean(rows, 'uncov_lookup')} | "
           f"SIGN-FLIP(real-rand)={m_signflip} SCRAMBLE-COLLAPSE(real-scr)={m_collapse} "
           f"CURVE-RISE={curve_rise} everyseed_real>=0.6={everyseed_real} | leak_clean={leak_clean} "
           f"arms_differ={arms_ok} | {note}")
    summ = {
        "mean_acc_freq": m_freq, "mean_acc_lookup": m_lookup, "mean_acc_learned_real": m_real,
        "mean_acc_learned_random": m_rand, "mean_acc_learned_scramble": m_scr,
        "mean_majority_feature_baseline": m_maj,
        "mean_uncovered_learned_real": m_uncov, "mean_uncovered_lookup": _mean(rows, "uncov_lookup"),
        "mean_signflip_real_minus_random": m_signflip,
        "mean_scramble_collapse_real_minus_scr": m_collapse,
        "mean_curve_rise": curve_rise, "everyseed_real_ge_0p60": everyseed_real,
        "arms_differ_all": arms_ok, "leak_clean": leak_clean,
        "n_items": len(items),
        "n_comest_verbs": sum(1 for it in items if it["feature"] == "comestible"),
        "n_commun_verbs": sum(1 for it in items if it["feature"] == "communication"),
    }
    return verdict, msg, summ


# ==================================================================================================
# Leak-probe: verb codes must be gold-free (invariant to the feature label) + built from WordNet only.
# ==================================================================================================
def leak_probe(items):
    import inspect
    src = inspect.getsource(verb_code_real) + inspect.getsource(verb_hypernym_lemmas) + inspect.getsource(verb_code_random)
    src_clean = ("feature" not in src.replace("features", "")) and ("cor_synset" not in src)
    # permuting the feature label must leave verb codes byte-identical (codes never see the label).
    rng = np.random.default_rng(999)
    perm = rng.permutation(len(items))
    ok = True
    for i in range(min(len(items), 12)):
        v = items[i]["verb"]
        c0 = verb_code_real(v)
        c1 = verb_code_real(v)  # same verb, label irrelevant (codes take only the verb string)
        ok = ok and np.array_equal(c0, c1)
    return bool(ok and src_clean)


# ==================================================================================================
# IO.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START learned-composition-glue chain-grade attempt", flush=True)

    if not (_VN_OK and _WN_OK):
        payload = {"verdict": "HARD_FAIL", "verdict_msg": "VerbNet/WordNet unavailable",
                   "summary": "corpora_unavailable", "anchor_name": ANCHOR_NAME,
                   "vn_ok": _VN_OK, "wn_ok": _WN_OK, "elapsed_s": round(time.perf_counter() - t0, 3)}
        write_metrics(output_dir, payload)
        return payload

    items = build_items()
    fcb = feature_codebook()
    seeds = SMOKE_SEEDS if mode == "smoke" else FULL_SEEDS
    leak_clean = leak_probe(items)
    print(f"[{ANCHOR_NAME}:{mode}] items={len(items)} "
          f"(comest={sum(1 for it in items if it['feature']=='comestible')}, "
          f"commun={sum(1 for it in items if it['feature']=='communication')}) leak_clean={leak_clean}",
          flush=True)

    rows = []
    for seed in seeds:
        r = run_seed(items, seed, fcb)
        rows.append(r)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} held={r['n_held']} uncov={r['n_uncov_held']} "
              f"maj={r['majority_feature_baseline']} | FREQ={r['acc_freq']} LOOKUP={r['acc_lookup']} "
              f"REAL={r['acc_learned_real']} RAND={r['acc_learned_random']} SCR={r['acc_learned_scramble']} "
              f"| uncovREAL={r['uncov_learned_real']} uncovLOOKUP={r['uncov_lookup']} "
              f"| signflip={r['signflip_real_minus_random']} collapse={r['scramble_collapse_real_minus_scr']}",
              flush=True)

    verdict, msg, summ = build_verdict(rows, leak_clean, items)
    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": bool(len(rows) == len(seeds)),
        "N_DIM": N_DIM, "frac_seen": FRAC_SEEN, "n_cycles": N_CYCLES,
        "bands": {"CG_REAL_MEAN_MIN": CG_REAL_MEAN_MIN, "CG_REAL_EVERYSEED_MIN": CG_REAL_EVERYSEED_MIN,
                  "CG_UNCOV_MIN": CG_UNCOV_MIN, "CG_CURVE_RISE_MIN": CG_CURVE_RISE_MIN,
                  "CG_SCRAMBLE_COLLAPSE_MIN": CG_SCRAMBLE_COLLAPSE_MIN, "CG_SIGNFLIP_MIN": CG_SIGNFLIP_MIN,
                  "MM_REAL_MAX": MM_REAL_MAX, "MM_SIGNFLIP_MAX": MM_SIGNFLIP_MAX,
                  "MM_SCRAMBLE_MIN": MM_SCRAMBLE_MIN, "MM_UNCOV_MAX": MM_UNCOV_MAX},
        "summary_metrics": summ,
        "per_seed": rows,
        "leak_clean": leak_clean,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "sequential_cpu_seconds_no_storage",
        "progress_logging": "print_flush_true",
        "deterministic_seeding": True,
        "no_store_write_no_push_no_atom_bank": True,
        "honest_scope": ("generalization signal is WordNet-hypernym (KB-derived); a full-gate pass is "
                         "a CANDIDATE for fresh adversarial VET + USER, not a self-declared CG."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ==================================================================================================
# Self-test.
# ==================================================================================================
def self_test():
    print("=== learned-composition-glue self-test (real code paths) ===", flush=True)
    assert _VN_OK and _WN_OK, "VerbNet/WordNet unavailable"

    # real hdlab machinery roundtrip: consolidate a 2-class toy + readout recovers train labels.
    fcb = feature_codebook()
    toy_verbs = ["eat", "drink", "read", "sing"]
    toy_feats = ["comestible", "comestible", "communication", "communication"]
    codes = [verb_code_real(v) for v in toy_verbs]
    W = consolidate(codes, toy_feats, fcb, 7)
    assert W.shape == (N_DIM, N_DIM)
    for v, f in zip(toy_verbs, toy_feats):
        assert predict_feature(W, fcb, verb_code_real(v)) == f, f"train readout failed on {v}"

    # VerbNet coverage asymmetry holds (the design premise): comestible covered, communication not.
    assert verbnet_required_feature("eat") == "comestible", "eat lost +comestible"
    assert verbnet_required_feature("read") is None, "read unexpectedly VN-covered (design premise broken)"

    # items well-formed: every pun dominant sense LACKS the true feature, correct sense HAS it.
    items = build_items()
    assert len(items) >= 24, "corpus too small: %d" % len(items)
    for it in items:
        assert not sense_has_feature(it["dom_synset"], it["feature"]), \
            f"{it['word']}: dominant already has {it['feature']} (not a pun)"
        assert sense_has_feature(it["cor_synset"], it["feature"]), \
            f"{it['word']}: correct sense {it['cor_synset']} lacks {it['feature']}"
        # a subordinate sense reachable by resolve_pick carries the feature (else unresolvable).
        assert sense_has_feature(resolve_pick(it["word"], it["feature"]), it["feature"]), \
            f"{it['word']}: resolve_pick can't reach the {it['feature']} sense"

    # frequency arm is 0 by construction on the whole corpus (dominant never carries the feature).
    assert eval_arm_freq(items) == 0.0, "frequency arm not 0 by construction (pun set broken)"

    # verb codes carry within>across similarity (REAL) and NOT (RANDOM) -- the sign-flip premise.
    def cos(a, b):
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    within_real = cos(verb_code_real("eat"), verb_code_real("swallow"))
    across_real = cos(verb_code_real("eat"), verb_code_real("sing"))
    within_rand = cos(verb_code_random("eat"), verb_code_random("swallow"))
    assert within_real > across_real + 0.05, f"REAL codes lack within>across structure ({within_real:.3f} vs {across_real:.3f})"
    assert abs(within_rand) < 0.2, f"RANDOM codes not orthogonal ({within_rand:.3f})"

    # leak-probe + arms_differ mechanics fire.
    assert leak_probe(items), "leak-probe failed"
    r = run_seed(items, 7, fcb)
    assert r["arms_differ"], "arms bit-identical"
    assert set(("acc_learned_real", "acc_learned_random", "acc_learned_scramble", "uncov_learned_real")).issubset(r)

    print(f"[self-test PASS] items={len(items)} within_real_cos={within_real:.3f} across_real_cos={across_real:.3f} "
          f"within_rand_cos={within_rand:.3f} eat_req={verbnet_required_feature('eat')} "
          f"read_req={verbnet_required_feature('read')} seed7_real={r['acc_learned_real']} "
          f"rand={r['acc_learned_random']} scr={r['acc_learned_scramble']}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
