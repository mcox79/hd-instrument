#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_frame_induction_oov_psych_v1

OOV VERB-FRAME INDUCTION (OOV-ACQUISITION ONLY). Does the substrate INDUCE a novel psych verb's
thematic frame (subj = EXPERIENCER, not the DEFAULT_FRAME -> AGENT) from the CONSTRUCTIONS it
appears in? Gleitman (1990, CITED) syntactic bootstrapping. Config-only EXPAND of hdlab/learner
via hdlab/frame_induction.py (feature encoder) + registry.learn/apply. ZERO edits to
core.py/registry.py/plugins (audit notes/research_oov_verb_frame_induction_learner_expand_audit_2026-08-04.md).

SUPPLIED vs EARNED (honest): the role VOCABULARY (AGENT/EXPERIENCER) is supplied; the
construction->frame MAPPING is EARNED (induced by the learner, MDL-auto-selected, transferred to
unseen verbs by CONSTRUCTION overlap -- the verb lemma is NEVER a feature).

DATA: psych-construction gold is genuinely SPARSE (the recurring blocker). This cell uses the real
srl_corpus / McGuffey psych examples as construction templates and instantiates a principled,
templated exposure corpus over the supplied PSYCH_VERBS / _PLAIN_TRANSITIVE lemma pools (verb lemma
never enters a feature). This is a MECHANISM test (can the learner induce + transfer a
construction->frame rule), NOT a real-corpus capability claim -- the corpus is templated and this is
reported straight (synthetic-toy outcomes can be construction-determined; USER-LOCKED).

EVAL (the falsifier): LEMMA-LEVEL split. Held-out ENTIRELY = cherish/loathe/crave/covet (all OOV:
absent from VERB_FRAMES) + agentive novel verbs; they appear in ZERO training episodes. PRIMARY
METRIC = experiencer-axis accuracy on the HELD-OUT NOVEL psych verbs (subj predicted EXPERIENCER).

BASELINES: DEFAULT_FRAME (OOV -> AGENT = 0.0 on the experiencer axis by construction);
POSITION-MAJORITY (predict the majority gold class conditioned on order -- the audit's biggest-risk
"position-majority in disguise" foil).

CONTROLS: SCRAMBLE (permute construction->frame association; induced experiencer-acc MUST collapse)
+ CONSTRUCTION-SIGNAL-NOT-POSITION (induction must beat the position-majority rule on held-out).

PRE-REGISTERED BANDS: HARD_PASS = held-out-novel experiencer-axis acc >= 0.55 AND scramble collapses
AND induction beats position-majority. HARD_FAIL = acc < 0.35 OR scramble does not collapse.
MIDDLE = 0.35-0.55 or one control weak (right-mechanism/underpowered) -- reported honestly, NOT
forced to a pass on sparse data.

NOTE: this is OOV-ACQUISITION ONLY. The downstream cue-conflict (an induced EXPERIENCER frame being
overridden by a position prior in the role-assignment perceptron) is a SEPARATE unfixed bug (re-VET
criterion #1), NOT addressed here.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, closed-form counting/rule-search/bounded-DSL only
(no matmul, no torch). Wall time sub-second. LOCAL-ONLY, foreground-to-completion; NO queue, NO
push, NO remote-persist, NO hdlab mutation, NO atom bank. Deterministic: thread-pins + fixed int
seeds + sorted(set()); NO hash()-seeded RNG or ordering (PROT-023).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import random
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "frame_induction_oov_psych_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import frame_induction as FI  # noqa: E402
from hdlab.thematic_role_labeler import PSYCH_VERBS, _PLAIN_TRANSITIVE, VERB_FRAMES  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- Pre-registered bands ----
HP_EXPERIENCER_ACC_MIN = 0.55
HF_EXPERIENCER_ACC_MAX = 0.35
SCRAMBLE_COLLAPSE_DELTA_MIN = 0.25   # induced acc must drop >= this under scramble
POSITION_BEAT_MARGIN_MIN = 0.15      # induction must beat position-majority by >= this on held-out

SPLIT_SEED = 8040804        # fixed int, NOT hash()-derived
SCRAMBLE_SEED = 20260804    # fixed int
EPS = 1e-9

# Held-out NOVEL verbs (lemma-level split; appear in ZERO training episodes). The 4 psych verbs are
# the re-VET's own demo failures and are ALL OOV (absent from VERB_FRAMES).
HELDOUT_PSYCH = ["cherish", "loathe", "crave", "covet"]
HELDOUT_AGENTIVE = ["hurl", "clutch", "shove", "forge"]

# Simple animate subjects + inanimate stimuli/objects (surface only; never featurized).
SUBJECTS = ["he", "she", "mary", "john", "herbert", "anna", "the child", "the sailor"]
STIMULI = ["storm", "kitten", "winter", "dress", "ring", "song", "garden", "letter", "castle", "coin"]


def _verb_ing(v):
    """Surface -ing form (rough; used only to build progressive tokens)."""
    if v.endswith("e") and not v.endswith("ee"):
        return v[:-1] + "ing"
    if len(v) > 2 and v[-1] not in "aeiouwxy" and v[-2] in "aeiou" and v[-3] not in "aeiou":
        return v + v[-1] + "ing"  # crude doubling (run -> running); fine for detector purposes
    return v + "ing"


def _sentence(subj, verb, obj, construction):
    """Return (tokens, v_idx, subj_idx). subj is 1 token slot (may be a 2-word phrase -> we join
    the phrase into a single surface token so indexing stays simple and order:pre is well-defined)."""
    subj_tok = subj.replace(" ", "_")
    if construction == "bare":
        toks = [subj_tok, verb, "the", obj, "."]
        return toks, 1, 0
    if construction == "scomp":
        toks = [subj_tok, verb, "that", "the", obj, "was", "near", "."]
        return toks, 1, 0
    if construction == "degree":
        toks = [subj_tok, verb, "the", obj, "very", "much", "."]
        return toks, 1, 0
    if construction == "progressive":
        toks = [subj_tok, "was", _verb_ing(verb), "the", obj, "."]
        return toks, 2, 0
    raise ValueError("unknown construction %r" % construction)


# Construction distribution per verb class (Gleitman: psych verbs disproportionately appear in
# informative CP/degree frames; agentive verbs in bare/progressive frames). Bare is the shared,
# UNINFORMATIVE frame both classes use -- so position/order alone cannot separate them.
PSYCH_CONSTRUCTIONS = ["bare", "scomp", "degree"]
AGENTIVE_CONSTRUCTIONS = ["bare", "bare2", "progressive"]  # bare2 = 2nd bare occurrence (diff obj)


def _gen_verb_episodes(verb, verb_class, rng):
    """Generate the templated occurrences for ONE verb. gold subj role = EXPERIENCER (psych) /
    AGENT (agentive). Returns list of episodes (feats never contain the verb)."""
    eps = []
    role = "EXPERIENCER" if verb_class == "psych" else "AGENT"
    constructions = PSYCH_CONSTRUCTIONS if verb_class == "psych" else AGENTIVE_CONSTRUCTIONS
    for k, cons in enumerate(constructions):
        subj = SUBJECTS[rng.randrange(len(SUBJECTS))]
        obj = STIMULI[rng.randrange(len(STIMULI))]
        real_cons = "bare" if cons == "bare2" else cons
        toks, v_idx, subj_idx = _sentence(subj, verb, obj, real_cons)
        ep = FI.build_episode(toks, v_idx, subj_idx, role)
        ep["verb"] = verb
        ep["verb_class"] = verb_class
        ep["construction"] = cons
        eps.append(ep)
    return eps


def build_corpus():
    """Train on IN-VOCAB verbs; held-out NOVEL verbs never appear in training. Returns
    (train_eps, heldout_psych_eps, heldout_agentive_eps)."""
    rng = random.Random(SPLIT_SEED)
    # Train psych: supplied PSYCH_VERBS minus any that collide with held-out (none do).
    train_psych = [v for v in sorted(set(PSYCH_VERBS)) if v not in HELDOUT_PSYCH]
    # Train agentive: supplied plain-transitive pool minus held-out.
    train_agentive = sorted(set(v for v in _PLAIN_TRANSITIVE
                                if v not in HELDOUT_AGENTIVE and v not in set(PSYCH_VERBS)))

    train_eps = []
    for v in train_psych:
        train_eps.extend(_gen_verb_episodes(v, "psych", rng))
    for v in train_agentive:
        train_eps.extend(_gen_verb_episodes(v, "agentive", rng))

    heldout_psych_eps = []
    for v in HELDOUT_PSYCH:
        assert FI.is_oov(v), "held-out psych verb %r is NOT OOV (leak)" % v
        heldout_psych_eps.extend(_gen_verb_episodes(v, "psych", rng))
    heldout_agentive_eps = []
    for v in HELDOUT_AGENTIVE:
        heldout_agentive_eps.extend(_gen_verb_episodes(v, "agentive", rng))

    # Leakage guard: no held-out verb appears in any training episode's verb field.
    train_verbs = {ep["verb"] for ep in train_eps}
    for v in HELDOUT_PSYCH + HELDOUT_AGENTIVE:
        assert v not in train_verbs, "LEAK: held-out verb %r present in training" % v
    return train_eps, heldout_psych_eps, heldout_agentive_eps, len(train_psych), len(train_agentive)


def experiencer_axis_acc(preds, eps):
    """Experiencer-axis accuracy: fraction of held-out PSYCH occurrences whose SUBJ is correctly
    predicted EXPERIENCER."""
    assert len(preds) == len(eps)
    if not eps:
        return None
    correct = sum(1 for p, ep in zip(preds, eps) if p == ep["gold_class"])
    return correct / len(eps)


def position_majority_fit(train_eps):
    """The audit's 'position-majority in disguise' foil: learn the majority gold class conditioned
    ONLY on order (pre/post). No construction cue used."""
    buckets = {"pre": Counter(), "post": Counter()}
    for ep in train_eps:
        order = "pre" if "order_pre" in ep["feats"] else "post"
        buckets[order][ep["gold_class"]] += 1
    table = {}
    for order, c in buckets.items():
        table[order] = c.most_common(1)[0][0] if c else "AGENT"
    return table


def position_majority_predict(table, eps):
    out = []
    for ep in eps:
        order = "pre" if "order_pre" in ep["feats"] else "post"
        out.append(table.get(order, "AGENT"))
    return out


def scramble_train(train_eps, seed=SCRAMBLE_SEED):
    """Permute the construction->frame association: map each gold class to a DERANGED class and
    relabel training episodes. Breaks the true construction->frame mapping while preserving the
    feature distribution -- a load-bearing induced hypothesis must collapse on the (unchanged)
    held-out gold."""
    classes = sorted({ep["gold_class"] for ep in train_eps})
    rng = random.Random(seed)
    perm = classes[:]
    rng.shuffle(perm)
    if perm == classes:  # force a derangement (binary -> swap)
        perm = perm[::-1]
    cmap = dict(zip(classes, perm))
    out = []
    for ep in train_eps:
        ne = dict(ep)
        ne["feats"] = list(ep["feats"])
        ne["gold_class"] = cmap[ep["gold_class"]]
        out.append(ne)
    return out, cmap


def _predict_all(chosen_name, hypothesis, eps):
    return [FI.predict_subj_role(chosen_name, hypothesis, ep["feats"], default="AGENT") for ep in eps]


def _arms_differ_hash(pred_dict):
    digests = {}
    for name, preds in pred_dict.items():
        b = ("|".join(preds)).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    identical = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))
                 if digests[names[i]] == digests[names[j]]]
    return digests, identical


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_pipeline(run_mode):
    t0 = time.perf_counter()

    train_eps, held_psych, held_agent, n_train_psych, n_train_agent = build_corpus()
    assert len(train_eps) > 0 and len(held_psych) > 0

    # ---- Induce (MDL-auto-select) ----
    chosen_name, chosen, all_results = FI.induce(train_eps)
    induced_hyp = chosen.hypothesis if chosen is not None else None

    # ---- Predict on held-out NOVEL psych verbs (construction cues only) ----
    preds_psych = _predict_all(chosen_name, induced_hyp, held_psych)
    acc_experiencer = experiencer_axis_acc(preds_psych, held_psych)

    # Per-held-out-verb + per-construction breakdown (glass-box).
    per_verb = {}
    for ep, p in zip(held_psych, preds_psych):
        d = per_verb.setdefault(ep["verb"], {"n": 0, "correct": 0, "by_construction": {}})
        d["n"] += 1
        d["correct"] += int(p == ep["gold_class"])
        d["by_construction"][ep["construction"]] = {"pred": p, "gold": ep["gold_class"]}
    for v, d in per_verb.items():
        d["acc"] = d["correct"] / d["n"] if d["n"] else None

    # ---- Baseline 1: DEFAULT_FRAME (OOV -> AGENT). 0.0 on experiencer axis by construction. ----
    preds_default = ["AGENT"] * len(held_psych)
    acc_default = experiencer_axis_acc(preds_default, held_psych)

    # ---- Baseline 2 (biggest-risk foil): POSITION-MAJORITY ----
    pos_table = position_majority_fit(train_eps)
    preds_position = position_majority_predict(pos_table, held_psych)
    acc_position = experiencer_axis_acc(preds_position, held_psych)

    # ---- Control: SCRAMBLE construction->frame; induced acc must collapse ----
    scr_train, scramble_map = scramble_train(train_eps)
    scr_name, scr_chosen, _scr_all = FI.induce(scr_train)
    scr_hyp = scr_chosen.hypothesis if scr_chosen is not None else None
    preds_scr = _predict_all(scr_name, scr_hyp, held_psych)
    acc_experiencer_scrambled = experiencer_axis_acc(preds_scr, held_psych)
    scramble_delta = (acc_experiencer - acc_experiencer_scrambled) if (
        acc_experiencer is not None and acc_experiencer_scrambled is not None) else None
    scramble_collapses = bool(scramble_delta is not None and scramble_delta >= SCRAMBLE_COLLAPSE_DELTA_MIN - EPS)

    # ---- Construction-signal-not-position: induction must beat position-majority on held-out ----
    beats_position = bool(acc_experiencer is not None and acc_position is not None and
                          (acc_experiencer - acc_position) >= POSITION_BEAT_MARGIN_MIN - EPS)
    beats_default = bool(acc_experiencer is not None and acc_default is not None and
                         acc_experiencer > acc_default + EPS)

    # ---- Held-out agentive sanity (should NOT regress: subj=AGENT) ----
    preds_agent = _predict_all(chosen_name, induced_hyp, held_agent)
    acc_agentive = sum(1 for p, ep in zip(preds_agent, held_agent)
                       if p == ep["gold_class"]) / len(held_agent) if held_agent else None

    digests, identical = _arms_differ_hash({
        "induced": preds_psych, "default": preds_default, "position": preds_position, "scramble": preds_scr})

    # ---- Verdict ----
    if acc_experiencer is None:
        overall, msg = "CELL_CRASHED", "no held-out psych predictions"
    elif acc_experiencer >= HP_EXPERIENCER_ACC_MIN - EPS and scramble_collapses and beats_position and beats_default:
        overall = "HARD_PASS"
        msg = ("HARD_PASS: held-out-novel experiencer-axis acc=%.3f (>=%.2f), beats default-AGENT "
               "(%.3f) + position-majority (%.3f), scramble collapses (delta=%.3f). Induced=%s. "
               "Construction signal, not position." % (
                   acc_experiencer, HP_EXPERIENCER_ACC_MIN, acc_default, acc_position, scramble_delta, chosen_name))
    elif acc_experiencer < HF_EXPERIENCER_ACC_MAX or not scramble_collapses:
        overall = "HARD_FAIL"
        why = "acc<%.2f" % HF_EXPERIENCER_ACC_MAX if acc_experiencer < HF_EXPERIENCER_ACC_MAX else "scramble did NOT collapse (position-majority in disguise)"
        msg = ("HARD_FAIL (%s): held-out-novel experiencer-axis acc=%.3f, scramble_delta=%s, "
               "beats_position=%s. Induced=%s." % (
                   why, acc_experiencer, scramble_delta, beats_position, chosen_name))
    else:
        overall = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND (right-mechanism/underpowered): experiencer-axis acc=%.3f in [%.2f,%.2f), "
               "or a control weak (scramble_collapses=%s beats_position=%s beats_default=%s). "
               "Induced=%s. Reported honestly on sparse psych data; NOT forced to a pass." % (
                   acc_experiencer, HF_EXPERIENCER_ACC_MAX, HP_EXPERIENCER_ACC_MIN,
                   scramble_collapses, beats_position, beats_default, chosen_name))

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": overall, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "scope_note": ("OOV-ACQUISITION ONLY. Downstream cue-conflict (induced frame overridden by "
                       "position prior in the role-assignment perceptron) is a SEPARATE unfixed bug "
                       "(re-VET criterion #1), NOT addressed here."),
        "supplied_vs_earned": ("role vocabulary (AGENT/EXPERIENCER) SUPPLIED; construction->frame "
                               "MAPPING EARNED (induced, lemma never a feature); corpus is templated "
                               "(mechanism test, not a real-corpus capability claim)."),
        "config_only_expand": True,
        "induced_plugin": chosen_name,
        "induced_hypothesis": induced_hyp,
        "all_plugin_compression_ratios": {
            n: (r.compression_ratio if (r.description_bits > 0 or r.null_bits > 0) else None)
            for n, r in all_results.items()},
        "n_train_episodes": len(train_eps),
        "n_train_psych_verbs": n_train_psych,
        "n_train_agentive_verbs": n_train_agent,
        "heldout_psych_verbs": HELDOUT_PSYCH,
        "n_heldout_psych_verbs": len(HELDOUT_PSYCH),
        "n_heldout_psych_episodes": len(held_psych),
        "acc_experiencer_axis_heldout": acc_experiencer,
        "acc_default_frame_heldout": acc_default,
        "acc_position_majority_heldout": acc_position,
        "acc_experiencer_axis_scrambled": acc_experiencer_scrambled,
        "scramble_delta": scramble_delta,
        "scramble_collapses": scramble_collapses,
        "scramble_class_map": scramble_map,
        "beats_default_agent": beats_default,
        "beats_position_majority": beats_position,
        "construction_signal_not_position": bool(beats_position and scramble_collapses),
        "position_majority_table": pos_table,
        "acc_agentive_heldout_sanity": acc_agentive,
        "per_heldout_verb": per_verb,
        "arms_differ": {"digests": digests, "identical_pairs": identical},
        "arms_differ_verified": bool(len(identical) == 0),
        "arms_differ_exempted": (
            [{"pair": p, "rationale": "default-AGENT and position-majority may coincide when the "
              "order-conditioned majority is AGENT (both predict all-AGENT on held-out psych); this "
              "is the reported finding (position cannot recover EXPERIENCER), not an arm bug."}
             for p in identical] if identical else []),
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "accuracy measurement over a discrete 2-class axis; no capacity/CRLB floor",
        "baseline_in_band": "n/a (DEFAULT_FRAME + POSITION_MAJORITY are the discriminating baselines under test)",
        "cardinality_ok": True, "expected_n_units": 1,
        "calibration_check": "default_ok_for_this_regime",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
    }
    return metrics


def _instrumentation_selftest():
    FI._selftest()
    train_eps, held_psych, held_agent, ntp, nta = build_corpus()
    assert ntp >= 20, "train psych verb count too low: %d" % ntp
    assert len(held_psych) == len(HELDOUT_PSYCH) * len(PSYCH_CONSTRUCTIONS)
    # No held-out verb leaks into training.
    tv = {ep["verb"] for ep in train_eps}
    assert not (set(HELDOUT_PSYCH) & tv) and not (set(HELDOUT_AGENTIVE) & tv)


_instrumentation_selftest()


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR, metrics)
    print("[self_test] verdict=%s" % metrics["verdict"], flush=True)
    print("[self_test] " + metrics["verdict_msg"], flush=True)
    return metrics["verdict"] != "CELL_CRASHED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["full", "self_test"], default="full")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]), flush=True)
    print("[%s] %s" % (args.run_mode, metrics["verdict_msg"]), flush=True)
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("induced_hypothesis", "arms_differ", "per_heldout_verb")}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
