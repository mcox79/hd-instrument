#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_reader_meaning_correction_case_sleep_affectedness_v1

MEANING-CORRECTION case+sleep loop: apply the PROVEN grammar CLS machinery (fast hippocampal
one-shot case + NREM-replay sleep consolidation) to VERB-AFFECTEDNESS lexicon errors. When the
who-is-affected GATE (VerbNet lemma-modal backend) mis-decides an instance (under-fires a
genuinely-affecting verb, or over-fires a non-affecting one), log a CASE (signature -> correction);
a SLEEP pass generalizes accrued cases into a schema store; measure whether the schema fixes
HELD-OUT (NEVER-CASED, verb-DISJOINT) gate errors. = the read-drives-knowledge loop made online.

ADAPTS the certified template experiments/exp_reader_selfimprove_case_sleep_udewt_v1.py (grammar
arc-labeler surface, atom 29405) to the MEANING/verb-affectedness surface. See
preregs/2026-07-21_reader_meaning_correction_case_sleep_affectedness_v1.md for the full pre-reg.

FAILURE SURFACE (oracle = INDEPENDENT blind-annotator gold; non-circular):
  Combined who-is-affected gold (6-class taxonomy), BINARY collapse gold_yes = type in
  {patient, transfer, effected}:
    - data/ud_ewt_semantic_affectedness_gold_v1/gold.json (56; blind to gate lexicon)
    - data/mcguffey_whoaffected_oracle_gold_v1/gold.json (34)
    - data/mcguffey_whoaffected_oracle_gold_v2_heldout/gold.json (38)
  BASELINE (loop OFF) = the REAL v2 gate full_gate(...,"baseline") (negation -> hand copula/
  stative/light -> VerbNet lemma-modal graded<0.35 -> force NONE), reused UNCHANGED. base gate
  decision = (not base_force_none); base ERROR = (decision != gold_yes).

HONEST CAVEAT (designed-around): meaning corrections are ORACLE-DEPENDENT (no text-internal
  self-supervised signal). Pre-measured: a build-time VerbNet-aggregation oracle (max per-sense
  affecting score) agrees with the blind gold only ~0.46 -> corrections MUST come from the gold,
  surface is small (oracle-scarce), generalization is a GENUINE can-fail question. Small-N noise
  floor (1/n_heldout_err) reported explicitly.

SIGNATURE (glass-box, GOLD-FREE, mutation-probed): dense bipolar HD bundle of the verb's VerbNet
  structural fingerprint (vn_class / affectedness_type / levin / predicate across ALL senses;
  modal type; n_senses bucket; modal-score bucket) + argument-context (parse frame sig, object
  animacy, negation, locative-obl) -- from the reader's OWN parse + the lexicon, NEVER the gold.
  The base gate uses only the MODAL score; the corrector may lean on the FULL per-sense structure
  the modal aggregation discarded (a legitimate structural cue, NOT a gold leak). Mutation-probe:
  permute gold type+affected across instances -> every signature byte-identical (asserted).

MECHANISM (RECOMBINATION of certified primitives; NO hdlab or production-lexicon mutation):
  FAST  = hdlab.hippocampal_encoder.HippocampalEncoder (DG+CA3 one-shot; SEEN recall sanity).
  SLEEP = dense Hebbian W [role x sig] via hdlab.continual.replay_cycle (NREM re-Hebb) over
          (signature, binary-correction) case pairs.
  SCHEMA= hdlab.schema_exemplar_bayes.SchemaExemplarBayesIndex (coherence/purity of the errors).
  GATE  = hdlab.glass_box_loop.cleanup_with_margin -> override base decision iff margin >= tau.
          tau = ONE KNOB (ART-vigilance), calibrated on SEEN only to max SEEN net_gain (the
          regression constraint sets vigilance).

MUST-FAIL CONTROLS (BOTH; must FIRE at smoke):
  (a) SCRAMBLE case<->correction -> held-out fix collapses (coherent - scramble >= 0.15).
  (b) REGRESSION GUARD (vigilance): held-out regressions on the CORRECT-set at calibrated tau vs
      a BLIND override (tau=0, always apply store readout). Guard HOLDS iff reg_at_tau <= 0.20 AND
      reg_at_tau <= reg_blind - 0.10 (vigilance demonstrably bounds over-broad rules).

BANDS: REAL_IMPROVING_PROPERTY = scramble collapse>=0.15 AND mean net_gain>0 AND every-seed
  net_gain>0 AND rescue_precision>=0.60 AND regression-guard holds AND leak-clean.
  MEMORIZATION_OR_NO_TRANSFER = held-out fix<0.10 OR collapse<0.05 OR net_gain<=0 OR guard fails.
  MIDDLE_BAND = between. (A MIDDLE/NEGATIVE is a VALID informative outcome, not a cell bug.)

COMPUTE: class (b) sequential-CPU (justified: ~128 gold rows through persisted glass-box front-end
  + tiny numpy/torch matmuls, 3 seeds, wall < ~180s; not a GPU candidate). Storage: sharded
  episodic (hippocampal) + dense superposition (cortical W). LOCAL-only foreground; NO queue, NO
  push, NO remote-persist, NO git add of store, NO hdlab mutation, NO production-lexicon mutation
  (read-only; the additive-map-lexicon fold is the in-cell Hebbian W), NO atom bank. Deterministic:
  OMP/MKL/OPENBLAS=1, fixed int seeds, default_rng, hashlib feature codes (no hash()-seeded RNG),
  sorted(set) splits. progress_logging: print_flush_true.

# CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke (coherent vs scramble store readouts differ; base vs loop differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: generalization fix-rate; small-N noise floor reported = 1/n_heldout_err
# - baseline_in_band: base_gate_acc in (0.05,0.95) verified at run
# - discriminator survives scale: smoke = FULL combined surface (N~128), 1 seed (option A)
# - cardinality_ok: EXPECTED per-seed rows = len(seeds); verdict counts len(per_seed)
# - calibration_check: adaptive_with_discriminator_gate (tau on SEEN net_gain; controls verify fire)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - deterministic_seeding: true; progress_logging: print_flush_true
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import copy
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_meaning_correction_case_sleep_affectedness_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the reader front-end + the REAL v2 gate (read-only imports; NO mutation, NO fork)
from experiments.exp_mcguffey_whoaffected_wsd_frame_selectional_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH,
    parse_frame, arg_animacy, _parse_full, full_gate, verb_is_negated_clauseaware,
    find_verb_index, AFFECTED_TYPES, NONE_TYPES,
)
from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (  # noqa: E402
    reader_pass, base_pick,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402

VN_LEX_PATH = os.path.join(REPO_ROOT, "data", "verbnet_affectedness_lexicon_v1", "lexicon.json")
GOLD_SOURCES = [
    ("ud", os.path.join(REPO_ROOT, "data", "ud_ewt_semantic_affectedness_gold_v1", "gold.json")),
    ("mcg1", os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v1", "gold.json")),
    ("mcg2", os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v2_heldout", "gold.json")),
]

N_SIG = 512
DG_DIM = 2048
SPARSITY = 0.02
ROLES = ("AFFECTED", "NONE")

_VN_LEX = None


def vn_lex():
    global _VN_LEX
    if _VN_LEX is None:
        with open(VN_LEX_PATH, encoding="utf-8") as f:
            _VN_LEX = json.load(f)["lexicon"]
    return _VN_LEX


def _lemmatize_simple(v):
    """Cheap lemma lookup against the VerbNet lexicon keys (surface -> stripped forms)."""
    lex = vn_lex()
    v = (v or "").lower().strip().split()[0] if v else ""
    cands = [v]
    if v.endswith("ed"):
        cands += [v[:-2], v[:-1], v[:-2] + "e"]
    if v.endswith("ing"):
        cands += [v[:-3], v[:-3] + "e"]
    if v.endswith("s") and len(v) > 3:
        cands += [v[:-1]]
    for c in cands:
        if c and c in lex:
            return c
    return v


# ------------------------------------------------------------------------------------------------
# Signature: GOLD-FREE dense bipolar HD bundle. Deterministic hashlib codes (no PYTHONHASHSEED).
# ------------------------------------------------------------------------------------------------
_FEAT_CACHE = {}


def _feat_code(f):
    v = _FEAT_CACHE.get(f)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(f.encode("utf-8")).digest()[:8], "big")
        v = (np.random.default_rng(seed).integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0)
        _FEAT_CACHE[f] = v
    return v


def _verb_feats(verb_surface):
    """GOLD-FREE VerbNet structural fingerprint tokens of the verb lemma (never reads the gold)."""
    lem = _lemmatize_simple(verb_surface)
    e = vn_lex().get(lem)
    feats = ["lemma:" + lem]
    if e is None:
        feats.append("oov:1")
        return feats
    feats.append("modal:" + str(e.get("affectedness_type")))
    n_sen = int(e.get("n_senses", len(e.get("per_sense", []))))
    feats.append("nsenses:" + ("1" if n_sen <= 1 else "2-3" if n_sen <= 3 else "4+"))
    gs = float(e.get("graded_score", 0.5))
    feats.append("gradedbucket:" + ("lo" if gs < 0.2 else "mid" if gs < 0.35 else "hi"))
    for ps in e.get("per_sense", []):
        if ps.get("vn_class"):
            feats.append("vn:" + str(ps["vn_class"]))
        if ps.get("affectedness_type"):
            feats.append("vntype:" + str(ps["affectedness_type"]))
        det = ps.get("detail", "") or ""
        if "levin=" in det:
            feats.append("levin:" + det.split("levin=")[1].split("(")[0].split(" ")[0].strip())
        if "pred=" in det:
            feats.append("pred:" + det.split("pred=")[1].split(" ")[0].strip())
    return feats


def _ctx_feats(parse_sig, obj_anim, neg, has_loc):
    return ["frame:" + str(parse_sig), "objanim:" + str(obj_anim),
            "neg:" + ("1" if neg else "0"), "hasloc:" + ("1" if has_loc else "0")]


def build_signature(verb_surface, parse_sig, obj_anim, neg, has_loc):
    feats = _verb_feats(verb_surface) + _ctx_feats(parse_sig, obj_anim, neg, has_loc)
    v = np.zeros(N_SIG, dtype=np.float32)
    for f in feats:
        v += _feat_code(f)
    return v


# ------------------------------------------------------------------------------------------------
# Load the combined gold surface + run the real front-end + real base gate on each instance.
# ------------------------------------------------------------------------------------------------
def _load_gold():
    insts = []
    for src, path in GOLD_SOURCES:
        if not os.path.exists(path):
            print(f"[{ANCHOR_NAME}] WARN gold source missing: {path}", flush=True)
            continue
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        rows = d["gold"] if isinstance(d, dict) else d
        for g in rows:
            gt = g["type"]
            assert gt in (AFFECTED_TYPES | NONE_TYPES), "unexpected gold type %r" % gt
            insts.append({"src": src, "id": g["id"], "text": g["text"], "verb": g["verb"],
                          "gtype": gt, "gold_yes": gt in AFFECTED_TYPES})
    return insts


def _score_instances(insts, tagger, parser, labeler):
    """Attach signature + base gate decision to each instance. Returns list of dicts."""
    out = []
    for inst in insts:
        text, gverb = inst["text"], inst["verb"]
        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, _pm = find_verb_index(tokens, pos, gverb)
        _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
        pframe = parse_frame(tokens, _pos2, heads, labels, vidx)
        obj_aidx = pframe["obj_aidx"]
        obj_anim = arg_animacy(tokens[obj_aidx - 1], _pos2[obj_aidx - 1]) if obj_aidx else None
        neg = verb_is_negated_clauseaware(tokens, vidx)
        base_force_none, base_src = full_gate(gverb, pframe, obj_anim, neg, "baseline")
        gate_yes = (not base_force_none)                      # base gate decision (lexicon fact)
        sig = build_signature(gverb, pframe["sig"], obj_anim, neg, pframe["has_loc_obl"])
        out.append({
            **inst, "vlem": _lemmatize_simple(gverb),
            "sig": sig, "parse_sig": pframe["sig"], "obj_anim": obj_anim, "neg": neg,
            "has_loc": pframe["has_loc_obl"], "base_force_none": base_force_none, "base_src": base_src,
            "base_gate_yes": gate_yes, "is_fail": bool(gate_yes != inst["gold_yes"]),
            "gold_role": "AFFECTED" if inst["gold_yes"] else "NONE",
            "base_role": "AFFECTED" if gate_yes else "NONE",
        })
    return out


# ------------------------------------------------------------------------------------------------
# Verb-DISJOINT split.
# ------------------------------------------------------------------------------------------------
def verb_split(arcs, seed, frac_seen=0.6):
    verbs = sorted(set(a["vlem"] for a in arcs))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(verbs))
    n_seen = int(round(frac_seen * len(verbs)))
    seen_v = set(verbs[j] for j in perm[:n_seen])
    seen = [a for a in arcs if a["vlem"] in seen_v]
    held = [a for a in arcs if a["vlem"] not in seen_v]
    return seen, held, seen_v


# ------------------------------------------------------------------------------------------------
# Cortical superposition store W [role x sig] via continual.replay_cycle (NREM re-Hebb).
# ------------------------------------------------------------------------------------------------
def build_role_codebook(roles, seed=1234):
    rng = np.random.default_rng(seed)
    return {r: (rng.integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0) for r in roles}


def consolidate_store(case_sigs, case_roles, role_codebook, *, n_cycles, replay_frac, seed=7):
    import torch
    from hdlab.continual import replay_cycle
    keys = torch.from_numpy(np.asarray(case_sigs, dtype=np.float32))
    values = torch.from_numpy(np.asarray([role_codebook[r] for r in case_roles], dtype=np.float32))
    m = keys.shape[0]
    replay_idx = torch.from_numpy(np.arange(m).astype(np.int64))
    W = torch.zeros((N_SIG, N_SIG), dtype=torch.float32)
    torch.manual_seed(seed)
    for _ in range(int(n_cycles)):
        replay_cycle(W, replay_idx, keys, values, replay_frac=replay_frac, lr=1.0)
    return W.numpy()


def store_predict(W, role_codebook, roles, sig):
    """Cortical readout: role_space = W @ sig; cleanup vs role codebook -> (role, margin)."""
    from hdlab.glass_box_loop import cleanup_with_margin
    rs = (W @ sig.astype(np.float32))
    nrm = float(np.linalg.norm(rs))
    if nrm > 1e-9:
        rs = rs / nrm
    codebook = np.asarray([role_codebook[r] for r in roles], dtype=np.float32)
    idx, margin = cleanup_with_margin(rs, codebook)
    return roles[idx], margin


# ------------------------------------------------------------------------------------------------
# Evaluate the loop on a held-out set at a given tau: override the base gate decision with the
# store prediction iff margin >= tau. Report fix/break/net + collateral (regressions).
# ------------------------------------------------------------------------------------------------
def eval_heldout(W, role_codebook, roles, held, tau):
    preds = [store_predict(W, role_codebook, roles, a["sig"]) for a in held]
    fixes = breaks = base_correct = loop_correct = overrides = 0
    n_fail = sum(1 for a in held if a["is_fail"])
    n_corr = len(held) - n_fail
    for a, (rhat, margin) in zip(held, preds):
        base_ok = (a["base_role"] == a["gold_role"])
        base_correct += int(base_ok)
        net = a["base_role"]
        if margin >= tau and rhat != a["base_role"]:
            net = rhat
            overrides += 1
        net_ok = (net == a["gold_role"])
        loop_correct += int(net_ok)
        if (not base_ok) and net_ok:
            fixes += 1
        if base_ok and (not net_ok):
            breaks += 1
    n = len(held)
    return {
        "n_heldout": n, "n_heldout_fail": n_fail, "n_heldout_correct": n_corr,
        "base_acc": round(base_correct / n, 4) if n else None,
        "loop_acc": round(loop_correct / n, 4) if n else None,
        "net_gain": round((loop_correct - base_correct) / n, 4) if n else None,
        "fixes": fixes, "breaks": breaks, "overrides": overrides,
        "heldout_fix_rate": round(fixes / n_fail, 4) if n_fail else None,
        "collateral_rate": round(breaks / n_corr, 4) if n_corr else None,
        "rescue_precision": round(fixes / (fixes + breaks), 4) if (fixes + breaks) else None,
    }


def calibrate_tau(W, role_codebook, roles, seen):
    """ART-vigilance: tau on SEEN only. Sweep percentiles of SEEN margins; max SEEN net_gain (the
    regression constraint sets vigilance); ties -> higher tau (tighter)."""
    margins = np.asarray([store_predict(W, role_codebook, roles, a["sig"])[1] for a in seen],
                         dtype=np.float64)
    if margins.size == 0:
        return 0.0
    cand = sorted(set(float(np.percentile(margins, p))
                      for p in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90)))
    best_tau, best_gain = cand[0], -1e9
    for tau in cand:
        r = eval_heldout(W, role_codebook, roles, seen, tau)
        g = r["net_gain"] if r["net_gain"] is not None else -1e9
        if g >= best_gain:
            best_gain, best_tau = g, tau
    return round(best_tau, 6)


def _majority_base_rate(held):
    fails = [a for a in held if a["is_fail"]]
    if not fails:
        return None
    maj = Counter(a["gold_role"] for a in fails).most_common(1)[0][0]
    return round(sum(1 for a in fails if a["gold_role"] == maj) / len(fails), 4)


def _fast_seen_recall(seen_fail):
    if len(seen_fail) < 2:
        return None
    from hdlab.hippocampal_encoder import HippocampalEncoder
    X = np.asarray([a["sig"] for a in seen_fail], dtype=np.float32)
    enc = HippocampalEncoder(input_dim=N_SIG, dg_dim=DG_DIM, sparsity=SPARSITY, seed=7)
    codes = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    hits = sum(int(int(np.argmax(codes @ ret[i])) == i) for i in range(len(seen_fail)))
    return round(hits / len(seen_fail), 4)


def _schema_report(seen_fail):
    if len(seen_fail) < 6:
        return {"n": len(seen_fail), "note": "too few for schema clustering"}
    from hdlab.schema_exemplar_bayes import SchemaExemplarBayesIndex
    X = np.asarray([a["sig"] for a in seen_fail], dtype=np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    idx = SchemaExemplarBayesIndex(compression_ratio=5, seed=7).fit(Xn)
    st = idx.stats()
    purities = []
    for c, fidxs in idx.schema_to_facts.items():
        rs = [seen_fail[j]["gold_role"] for j in fidxs]
        purities.append(Counter(rs).most_common(1)[0][1] / len(rs))
    return {"n_schemas": st["n_schemas"], "mean_role_purity": round(float(np.mean(purities)), 4),
            "compression": round(st["compression_ratio_effective"], 2)}


# ================================================================================================
def cfg_smoke():
    return dict(mode="smoke", seeds=[7], n_cycles=3, replay_frac=0.5, frac_seen=0.6,
                curve_fracs=[0.25, 0.5, 1.0], subset=None)


def cfg_full():
    return dict(mode="full", seeds=[7, 13, 19], n_cycles=6, replay_frac=0.5, frac_seen=0.6,
                curve_fracs=[0.1, 0.25, 0.5, 0.75, 1.0], subset=None)


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


def _leak_probe(insts, tagger, parser, labeler):
    """Mutation-probe: permute gold type across instances -> every signature byte-identical
    (signature never reads the gold). Also src-scan the signature builders for gold refs."""
    import inspect as _insp
    src = _insp.getsource(build_signature) + _insp.getsource(_verb_feats) + _insp.getsource(_ctx_feats)
    src_clean = ("gtype" not in src) and ("gold_yes" not in src) and ("gold_role" not in src)
    sub = insts[:40]
    scored = _score_instances(sub, tagger, parser, labeler)
    perm = list(range(len(sub)))
    np.random.default_rng(999).shuffle(perm)
    mut = [dict(sub[i], gtype=sub[perm[i]]["gtype"], gold_yes=sub[perm[i]]["gold_yes"]) for i in range(len(sub))]
    scored_mut = _score_instances(mut, tagger, parser, labeler)
    ok = all(np.array_equal(a["sig"], b["sig"]) for a, b in zip(scored, scored_mut))
    return bool(ok and src_clean)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START meaning-correction case+sleep on verb-affectedness", flush=True)

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    insts = _load_gold()
    print(f"[{ANCHOR_NAME}:{mode}] combined gold N={len(insts)} "
          f"(srcs={dict(Counter(i['src'] for i in insts))})", flush=True)

    arcs = _score_instances(insts, tagger, parser, labeler)
    n_fail = sum(1 for a in arcs if a["is_fail"])
    base_acc_all = round(1 - n_fail / len(arcs), 4) if arcs else None
    err_verbs = defaultdict(list)
    for a in arcs:
        if a["is_fail"]:
            err_verbs[a["vlem"]].append(a["gold_role"])
    census = {
        "n_instances": len(arcs), "n_base_errors": n_fail, "base_gate_acc_all": base_acc_all,
        "n_error_verbs": len(err_verbs),
        "err_dir": dict(Counter(("under_fire" if a["gold_yes"] else "over_fire")
                                for a in arcs if a["is_fail"])),
        "by_src_err": {s: sum(1 for a in arcs if a["src"] == s and a["is_fail"]) for s in ("ud", "mcg1", "mcg2")},
    }
    print(f"[{ANCHOR_NAME}:{mode}] CENSUS N={len(arcs)} base_errors={n_fail} base_acc={base_acc_all} "
          f"err_verbs={len(err_verbs)} dir={census['err_dir']}", flush=True)

    roles = list(ROLES)
    role_codebook = build_role_codebook(roles)
    leak_clean = _leak_probe(insts, tagger, parser, labeler)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-CLEAN (signature gold-free, mutation-invariant): {leak_clean}", flush=True)

    per_seed = []
    for seed in cfg["seeds"]:
        seen, held, seen_v = verb_split(arcs, seed, cfg["frac_seen"])
        seen_fail = [a for a in seen if a["is_fail"]]
        held_fail = [a for a in held if a["is_fail"]]
        held_corr = [a for a in held if not a["is_fail"]]
        base_rate = _majority_base_rate(held)
        fast_recall = _fast_seen_recall(seen_fail)
        schema = _schema_report(seen_fail)

        case_sigs = [a["sig"] for a in seen_fail]
        case_roles = [a["gold_role"] for a in seen_fail]

        if len(case_sigs) < 2:
            row = {"seed": seed, "n_seen_verbs": len(seen_v), "n_seen_fail": len(seen_fail),
                   "n_heldout_fail": len(held_fail), "skipped": "too_few_seen_cases"}
            per_seed.append(row)
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} SKIP (seen_fail<2)", flush=True)
            continue

        # ---- COHERENT store (case -> true correction) ----
        W = consolidate_store(case_sigs, case_roles, role_codebook,
                              n_cycles=cfg["n_cycles"], replay_frac=cfg["replay_frac"], seed=seed)
        tau = calibrate_tau(W, role_codebook, roles, seen)
        coherent = eval_heldout(W, role_codebook, roles, held, tau)

        # ---- MUST-FAIL (a): SCRAMBLE case<->correction ----
        rng = np.random.default_rng(1000 + seed)
        scr_roles = [case_roles[j] for j in rng.permutation(len(case_roles))]
        W_scr = consolidate_store(case_sigs, scr_roles, role_codebook,
                                  n_cycles=cfg["n_cycles"], replay_frac=cfg["replay_frac"], seed=seed)
        scramble = eval_heldout(W_scr, role_codebook, roles, held, tau)

        # ---- MUST-FAIL (b): REGRESSION GUARD (vigilance vs blind tau=0) ----
        blind = eval_heldout(W, role_codebook, roles, held, 0.0)   # always override = blind
        reg_at_tau = coherent["collateral_rate"] or 0.0
        reg_blind = blind["collateral_rate"] or 0.0
        guard_holds = bool(reg_at_tau <= 0.20 and reg_at_tau <= reg_blind - 0.10)

        # ---- LEARNING CURVE: held-out fix-rate vs #SEEN cases (verbs) accrued ----
        curve = []
        verbs_seen = sorted(seen_v)
        for frac in cfg["curve_fracs"]:
            k = max(1, int(round(frac * len(verbs_seen))))
            sub_v = set(verbs_seen[:k])
            sub = [a for a in seen_fail if a["vlem"] in sub_v]
            if len(sub) < 2:
                curve.append({"frac": frac, "n_cases": len(sub), "heldout_fix_rate": None})
                continue
            Wc = consolidate_store([a["sig"] for a in sub], [a["gold_role"] for a in sub], role_codebook,
                                   n_cycles=cfg["n_cycles"], replay_frac=cfg["replay_frac"], seed=seed)
            rc = eval_heldout(Wc, role_codebook, roles, held, tau)
            curve.append({"frac": frac, "n_cases": len(sub), "n_seen_verbs": k,
                          "heldout_fix_rate": rc["heldout_fix_rate"], "net_gain": rc["net_gain"],
                          "rescue_precision": rc["rescue_precision"]})

        gain_collapse_scramble = round((coherent["heldout_fix_rate"] or 0) - (scramble["heldout_fix_rate"] or 0), 4)
        noise_floor = round(1.0 / len(held_fail), 4) if held_fail else None
        row = {"seed": seed, "n_seen_verbs": len(seen_v), "n_seen_fail": len(seen_fail),
               "n_heldout": len(held), "n_heldout_fail": len(held_fail), "n_heldout_correct": len(held_corr),
               "heldout_noise_floor": noise_floor, "base_rate_majority": base_rate, "tau": tau,
               "fast_seen_recall": fast_recall, "schema": schema,
               "coherent": coherent, "scramble": scramble, "blind_override": blind,
               "gain_collapse_scramble": gain_collapse_scramble,
               "reg_at_tau": reg_at_tau, "reg_blind": reg_blind, "guard_holds": guard_holds,
               "learning_curve": curve}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} seen_fail={len(seen_fail)} held_fail={len(held_fail)} "
              f"base_rate={base_rate} tau={tau} | COHERENT fix={coherent['heldout_fix_rate']} "
              f"gain={coherent['net_gain']} prec={coherent['rescue_precision']} | SCRAMBLE fix={scramble['heldout_fix_rate']} "
              f"(collapse={gain_collapse_scramble}) | GUARD reg_tau={reg_at_tau} reg_blind={reg_blind} "
              f"holds={guard_holds} | fast_recall={fast_recall}", flush=True)

    scored = [s for s in per_seed if "coherent" in s]

    def mean(path):
        vals = []
        for s in scored:
            v = s
            for p in path:
                v = v[p] if isinstance(v, dict) else None
            if isinstance(v, (int, float)):
                vals.append(v)
        return round(float(np.mean(vals)), 4) if vals else None

    m_fix = mean(["coherent", "heldout_fix_rate"])
    m_scr = mean(["scramble", "heldout_fix_rate"])
    m_gain = mean(["coherent", "net_gain"])
    m_prec = mean(["coherent", "rescue_precision"])
    m_base = mean(["base_rate_majority"])
    m_collapse = mean(["gain_collapse_scramble"])
    m_recall = mean(["fast_seen_recall"])
    m_reg_tau = mean(["reg_at_tau"])
    m_reg_blind = mean(["reg_blind"])
    base_acc = mean(["coherent", "base_acc"])
    baseline_in_band = bool(base_acc is not None and 0.05 < base_acc < 0.95)

    all_seeds_gain_pos = bool(scored) and all((s["coherent"]["net_gain"] or -1) > 0 for s in scored)
    all_guard_hold = bool(scored) and all(s["guard_holds"] for s in scored)
    scramble_collapses = (m_collapse is not None and m_collapse >= 0.15)
    net_gain_pos = (m_gain is not None and m_gain > 0.0)
    prec_ok = (m_prec is not None and m_prec >= 0.60)
    guard_fails = not all_guard_hold
    memorization = ((m_fix is not None and m_fix < 0.10)
                    or (m_collapse is not None and m_collapse < 0.05)
                    or (m_gain is not None and m_gain <= 0.0)
                    or guard_fails)

    if not scored:
        verdict = "INSUFFICIENT_SURFACE"
    elif scramble_collapses and net_gain_pos and all_seeds_gain_pos and prec_ok and all_guard_hold and leak_clean:
        verdict = "REAL_IMPROVING_PROPERTY"
    elif memorization or (not leak_clean):
        verdict = "MEMORIZATION_OR_NO_TRANSFER"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | combined who-affected gold N={census['n_instances']}, base_gate_errors="
           f"{census['n_base_errors']} (base_acc={base_acc_all}, err_verbs={census['n_error_verbs']}, "
           f"dir={census['err_dir']}); held-out (verb-disjoint) generalization: COHERENT fix_rate={m_fix} "
           f"(base_rate={m_base}, net_gain={m_gain}, rescue_prec={m_prec}) vs SCRAMBLE fix={m_scr} "
           f"(collapse={m_collapse}) | REGRESSION-GUARD reg_tau={m_reg_tau} reg_blind={m_reg_blind} "
           f"holds_all={all_guard_hold} | fast_seen_recall={m_recall} | leak_clean={leak_clean} "
           f"baseline_in_band={baseline_in_band} (base_acc={base_acc}) | scramble_collapses={scramble_collapses}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "expected_n_seed_rows": len(cfg["seeds"]), "n_seed_rows": len(per_seed),
        "cardinality_ok": bool(len(per_seed) == len(cfg["seeds"])),
        "census": census,
        "PRIMARY_heldout_fix_rate_coherent": m_fix, "base_rate_majority": m_base,
        "heldout_net_gain_coherent": m_gain, "rescue_precision_coherent": m_prec,
        "MUSTFAIL_a_scramble_fix_rate": m_scr, "MUSTFAIL_a_scramble_gain_collapse": m_collapse,
        "MUSTFAIL_b_regression_guard_reg_at_tau": m_reg_tau, "MUSTFAIL_b_regression_guard_reg_blind": m_reg_blind,
        "MUSTFAIL_b_regression_guard_holds_all_seeds": all_guard_hold,
        "fast_seen_recall_mean": m_recall,
        "leak_clean": leak_clean, "baseline_in_band": baseline_in_band, "baseline_heldout_acc": base_acc,
        "scramble_collapses_gain": scramble_collapses, "all_seeds_net_gain_positive": all_seeds_gain_pos,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "generalization fix-rate; noise floor=1/n_heldout_err",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <180s)",
        "calibration_check": "adaptive_with_discriminator_gate (tau on SEEN net_gain; scramble+guard verify fire)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "production_lexicon_mutated": False,
        "additive_store_note": "Hebbian superposition consolidated by continual.replay_cycle (NOT AdditiveKGMap)",
        "oracle_caveat": "meaning corrections oracle-dependent; VerbNet-aggregation-vs-gold agreement ~0.46 (pre-measured)",
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== meaning-correction case+sleep self-test (real code paths) ===", flush=True)
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    insts = _load_gold()
    assert len(insts) >= 100, "combined gold too small: %d" % len(insts)
    assert all(i["gtype"] in (AFFECTED_TYPES | NONE_TYPES) for i in insts)

    sub = insts[:24]
    scored = _score_instances(sub, tagger, parser, labeler)
    assert all("sig" in a and a["sig"].shape == (N_SIG,) for a in scored)
    assert all(a["base_role"] in ROLES and a["gold_role"] in ROLES for a in scored)

    # (1) signature deterministic + gold-free
    a = scored[0]
    s2 = build_signature(a["verb"], a["parse_sig"], a["obj_anim"], a["neg"], a["has_loc"])
    assert np.array_equal(a["sig"], s2), "signature not deterministic"
    import inspect as _insp
    bsrc = _insp.getsource(build_signature) + _insp.getsource(_verb_feats)
    assert "gtype" not in bsrc and "gold_yes" not in bsrc, "LEAK: signature builder references gold"

    # (1b) mutation-probe: permute gold -> signatures byte-identical
    perm = list(range(len(sub)))
    np.random.default_rng(7).shuffle(perm)
    mut = [dict(sub[i], gtype=sub[perm[i]]["gtype"], gold_yes=sub[perm[i]]["gold_yes"]) for i in range(len(sub))]
    scored_mut = _score_instances(mut, tagger, parser, labeler)
    assert all(np.array_equal(x["sig"], y["sig"]) for x, y in zip(scored, scored_mut)), \
        "LEAK: signature changed under gold permutation"

    # (2) label-tracking (non-tautological): inverting gold_role flips base_correct exactly
    prim = scored
    orig_acc = sum(1 for r in prim if r["base_role"] == r["gold_role"]) / len(prim)
    inv_acc = sum(1 for r in prim if r["base_role"] != r["gold_role"]) / len(prim)
    assert abs(inv_acc - (1 - orig_acc)) < 1e-9, (inv_acc, orig_acc)

    # (3) real store path: replay_cycle + glass_box cleanup + hippocampal recall
    roles = list(ROLES)
    rcb = build_role_codebook(roles)
    sf = [a for a in scored if a["is_fail"]]
    if len(sf) >= 2:
        W = consolidate_store([a["sig"] for a in sf], [a["gold_role"] for a in sf], rcb,
                              n_cycles=2, replay_frac=1.0)
        assert W.shape == (N_SIG, N_SIG)
        r, m = store_predict(W, rcb, roles, sf[0]["sig"])
        assert r in roles and isinstance(m, float)
        ev = eval_heldout(W, rcb, roles, scored, 0.0)
        assert set(("fixes", "breaks", "heldout_fix_rate", "collateral_rate")).issubset(ev)
        fr = _fast_seen_recall(sf)
        assert fr is None or 0.0 <= fr <= 1.0

        # (4) SCRAMBLE control fires (mechanically): scramble store readout differs from coherent
        rng = np.random.default_rng(3)
        scr = [(sf[j]["gold_role"]) for j in rng.permutation(len(sf))]
        W_scr = consolidate_store([a["sig"] for a in sf], scr, rcb, n_cycles=2, replay_frac=1.0)
        assert not np.array_equal(W, W_scr) or len(set(scr)) == 1, "scramble store identical to coherent"

        # (5) REGRESSION-GUARD tightens: overrides at high tau < overrides at tau=0 (vigilance works)
        ov0 = eval_heldout(W, rcb, roles, scored, 0.0)["overrides"]
        ovH = eval_heldout(W, rcb, roles, scored, 1e9)["overrides"]
        assert ovH <= ov0, "vigilance does not reduce overrides (guard broken)"
        assert ovH == 0, "tau=inf should suppress all overrides"
    print("[selftest] PASS: gold-free mutation-invariant signature + label-tracking + real "
          "replay_cycle store + glass-box gate + hippocampal recall + scramble + vigilance-guard exercised",
          flush=True)
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
