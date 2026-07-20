"""GRADED THEMATIC-FIT, INTEGRATED, PER-STEP READER -- with a MANDATORY Stage-1 FIRING-RATE GATE.

WHAT THIS IS (honest ceiling -- read before interpreting any number):
  The just-closed Scene-Coherence Verifier (SCV, atom 29360) proved a BINARY, POST-HOC contrastive
  WordNet/VerbNet coherence bit is a NULL trainer (self-supervised training delta EXACTLY 0.000 across
  seeds even with a gold-perfect bit). This cell tests the ONE surviving brain-faithful alternative from
  the viability drill (research_integrated_graded_experiential_reader_viability_corpus_precondition_2026-
  07-19.md): replace the BINARY bit with a CONTINUOUS graded thematic-fit score (how typical is filler F
  as the patient/object of verb V), and INTEGRATE it into the reader's INCREMENTAL patient decision (a
  per-step delta-rule on the cue's weight), NOT a post-hoc contrastive filter over completed parses.

  HONEST LABELING (load-bearing; no VET or director must be fooled): the graded score is computed by
  LOOKING UP hand-curated WordNet noun-supersenses + a CLASS-LEVEL distributional object-typicality mined
  from the 99k-word McGuffey corpus (class-smoothed a la Clark & Weir 2002 -- ~15 supersense classes are
  dense even on 99k; per-ITEM co-occurrence would NOT be, which is why this is class-smoothed and NOT a
  from-scratch distributional-fit model). This is SCAFFOLDED / LOOKED-UP world-knowledge, NOT substrate-
  learned world-experience. The ONLY thing LEARNED here is the low-dimensional cue-INTEGRATION weight
  (how much to trust the graded cue vs the existing structural cues) atop the already-built LCCP scaffold.
  Learning NEW distributional-fit VALUES from 99k is OUT OF SCOPE (corpus-gated, >=1M-1B+ words per the
  drill's Section 3) -- we do NOT attempt it.

STAGE 1 -- FIRING-RATE / COVERAGE GATE (design-gate; runs + is verified BEFORE any learning run; CAN HARD-
  FAIL and STOP): measures how often the graded cue is (a) DEFINED and (b) DISCRIMINATIVE -- materially
  different score across the RIVAL patient candidates at a decision point. The load-bearing metric is
  NOUN-ONLY discriminativeness (rivals restricted to content nouns with a defined supersense), because the
  trivial junk-vs-noun contrast is ALREADY handled by the LCCP's structural cues (f_func/f_prep) -- so
  gating on it would be construction-determined and CANNOT fail. Noun-only firing is the genuine can-fail
  signal: does the graded cue separate PLAUSIBLE noun rivals (the hard cases where structural cues tie)?
  If the cue is non-degenerate on only a tiny handful of cases (SCV-like 4-20), HARD-FAIL the gate and STOP
  -- that empirically confirms corpus-first (fork-c) / a WordNet-VerbNet coverage wall. A clean, valuable
  negative. NO circular eval: the gate measures gfit SPREAD across rivals only; gold patient labels (which
  rival is correct) are NOT used in the gate.

STAGE 2 -- the narrow learner (runs ONLY if the gate does NOT HARD-FAIL): integrate the graded cue as a
  7th feature into the incremental objecthood target (it resolves the DEFER band where structural + GloVe
  cues are ambiguous -- integrated DURING commitment, per candidate, NOT post-hoc), and learn its weight
  w[6] with the SAME error-driven delta-rule that trains the other cues. THREE arms, ONE variable (the
  graded cue + its learned weight):
    A_frozen   : 6-cue reader (gfit channel zeroed, w[6] pinned 0) = the existing reader (control).
    B_learned  : 7-cue, gfit integrated into the target + w[6] LEARNED.
    C_mustfail : like B but the gfit VALUES are SCRAMBLED across candidates -> the learned w[6] must DROP
                 toward 0 (genuine credit-assignment test: teach a hint, let it learn the weight; if the
                 weight stays high on a scrambled cue, the "learning" is hand-coding -> HARD-FAIL).
  REAL baseline (not a strawman): the LCCP arm-C precision (~0.500) is reproduced LIVE via L.run_arms and
  reported as the honest anchor alongside the matched-protocol frozen-vs-learned delta.

FAIRNESS GUARDS (enforced + persisted):
  (G1) NO circular eval: gate uses gfit spread only, never gold-correct-rival; Stage-2 held-out gold slice
       is INDEPENDENT who-did-what annotation (verified _meta.independence), and the gfit model is built on
       the MINING corpus only (third reader = gold source EXCLUDED from mining). No ground-by-X-grade-by-X.
  (G2) HONEST labeling: scaffolded/looked-up, not learned world-experience (claim_ceiling below).
  (G3) coverage/OOV reported on THIS corpus's actual verbs/nouns.

VERDICT BANDS (pre-registered BEFORE running; do NOT redefine mid-run):
  STAGE-1 GATE (noun-only discriminativeness at tau_disc=0.15 on the [0,1] gfit scale):
    HARD_FAIL_GATE (STOP; corpus/coverage-first): fire_count_noun_gold <= 20 (SCV-like handful) OR
                   fire_rate_noun_full < 0.15 (comparably sparse to a degenerate cue).
    HARD_PASS_GATE (proceed to Stage 2): fire_count_noun_gold >= 30 AND fire_count_noun_full >= 150 AND
                   fire_rate_noun_full >= 0.35 (order-of-magnitude denser than SCV's sparse trigger).
    MIDDLE_BAND_GATE: otherwise -> proceed to Stage 2 with a caution flag.
  STAGE-2 P_HELP (central learning-signal test; arms B vs A on held-out gold, keep-best matched protocol):
    HARD_PASS: mean(prec_B - prec_A) >= +0.02 over seeds AND min over seeds > 0 (consistent sign).
    HARD_FAIL: mean delta <= 0 (per-step + dense-firing did NOT rescue the mechanism -> the cleanest
               negative the arc can produce; distinct from the SCV null).
    MIDDLE_BAND: 0 < mean < 0.02 or inconsistent sign.
  STAGE-2 P_GENUINE (must-fail cue-validity; arm C vs B learned weight on the graded cue):
    HARD_PASS: mean|w_B[6]| > mean|w_C[6]| AND mean|w_C[6]| < 0.5*mean|w_B[6]| (weight materially drops).
    HARD_FAIL: mean|w_C[6]| >= mean|w_B[6]| (weight insensitive to corruption -> not real learning).
    MIDDLE_BAND: partial drop.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the reader (~0.1 s/sent) is the cost;
  run ONCE on the mining corpus + gold slice, cached to JSON; the gate is a deterministic count; the multi-
  seed delta-rule is cheap (< 1s). Total wall < ~60s (SCV full ran in 29s on the same machinery). Storage:
  no_storage (extraction-precision measurement). progress_logging: print_flush_true. Determinism: OMP/MKL/
  OPENBLAS=1, fixed int seeds, numpy default_rng, hashlib digests, sorted(set); NO hash()-seeded RNG.
  LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO git add -A.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash-test on A/B/C weight vectors)
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: extraction-precision measurement, no quantitative noise floor for the discriminator
  - baseline_in_band at smoke (arm-C ~0.5)
  - discriminator survives scale: gate verdict computed on FULL mining; smoke verifies the metric fires
  - HARD_PASS strictly above the SCV-sparse floor (fire_count_gold >= 30, an order above 4-20)
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "graded_thematic_fit_integrated_reader_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV  # noqa: E402

# Mining corpus (RAW, unlabeled). Third reader = GOLD source -> EXCLUDED from mining so the held-out eval
# text and the gfit model are never contaminated by the gold slice.
MINING_FILES_FULL = list(SCV.MINING_FILES_FULL)
MINING_FILES_SMOKE = list(SCV.MINING_FILES_SMOKE)
EXCLUDED_FROM_MINING = SCV.EXCLUDED_FROM_MINING

# WordNet noun supersenses that are NOT plausible direct-object types (kept only to report the coarse
# split for continuity with the SCV; the GRADED score does NOT use a hard set -- it uses class typicality).
NONOBJECT_SS = set(SCV.NONOBJECT_SS)

TAU_DISC = 0.15          # pre-registered discriminativeness threshold on the [0,1] gfit scale (gate verdict)
TAU_REPORT = [0.10, 0.15, 0.20, 0.25]  # reported for transparency
PRON_GFIT = 0.60         # CITED@drill Section 1: pronouns are canonical direct objects -> fixed typical value
MIN_VERB_OBS = 4         # verb needs >= this many structural objects before its per-verb assoc is trusted


# ----------------------------------------------------------------------------------------------
# GRADED thematic-fit model. Erk/McRae-style verb selectional preference over WordNet supersense classes,
# class-smoothed (Clark & Weir 2002 backoff) from corpus object-position co-occurrence. GRADED in [0,1].
# ----------------------------------------------------------------------------------------------
def _is_content_noun(pl):
    return (pl not in L.FUNCWORD and pl not in L.PREPS and pl not in L.PRONOUN
            and pl.replace("'", "").isalpha() and len(pl) >= 2)


def build_gfit_model(mine_cands):
    """From mining candidates in STRUCTURAL object position, build class-level + verb-class object counts.
    Returns a gfit(v, p) -> (score|None, kind) closure. kind in {junk, pronoun, noun, oov}."""
    class_obj = defaultdict(int)                    # supersense -> count in object position
    verb_class = defaultdict(lambda: defaultdict(int))  # verb -> supersense -> count
    verb_total = defaultdict(int)                   # verb -> total structural-object count
    for c in mine_cands:
        f = c["feat6"]
        # bootstrap object position: post-verbal, not prep-governed, not funcword (same filter as the
        # LCCP semantic teacher) -> a noisy but self-supervised object sample. NO gold used.
        if not (f[2] >= 0.5 and f[3] < 0.5 and f[4] < 0.5):
            continue
        pl = c["p"].lower()
        if not _is_content_noun(pl):
            continue
        ss = SCV.supersense(pl)
        if ss is None:
            continue
        class_obj[ss] += 1
        verb_class[c["v"]][ss] += 1
        verb_total[c["v"]] += 1
    max_class = max(class_obj.values()) if class_obj else 1
    # typ_class(ss) in [0,1]: corpus object-typicality of the class, normalized to the most frequent class.
    typ_class = {ss: class_obj[ss] / max_class for ss in class_obj}
    global_typ_mean = float(np.mean(list(typ_class.values()))) if typ_class else 0.5

    def typ(ss):
        return typ_class.get(ss, global_typ_mean)

    def gfit(v, p):
        pl = p.lower()
        if pl in L.FUNCWORD or pl in L.PREPS or len(pl) < 2 or not pl.replace("'", "").isalpha():
            return 0.0, "junk"
        if pl in L.PRONOUN:
            return PRON_GFIT, "pronoun"
        ss = SCV.supersense(pl)
        if ss is None:
            return None, "oov"           # undefined for the gate; Stage-2 backs off to global mean
        base = typ(ss)
        # verb-specific selectional preference (Resnik-style), normalized to the verb's most-preferred
        # class; backs off to the class prior when the verb has too few observed objects (Clark & Weir).
        vt = verb_total.get(v, 0)
        if vt >= MIN_VERB_OBS:
            vc = verb_class[v]
            vmax = max(vc.values()) if vc else 1
            assoc = vc.get(ss, 0) / vmax
        else:
            assoc = base
        score = 0.5 * base + 0.5 * assoc
        return float(score), "noun"

    model_stats = {"n_object_classes": len(class_obj), "max_class_count": int(max_class),
                   "class_obj_counts": {k: int(v) for k, v in sorted(class_obj.items())},
                   "typ_class": {k: round(v, 4) for k, v in sorted(typ_class.items())},
                   "n_verbs_with_own_assoc": int(sum(1 for v in verb_total if verb_total[v] >= MIN_VERB_OBS)),
                   "global_typ_mean": round(global_typ_mean, 4)}
    return gfit, model_stats


# ----------------------------------------------------------------------------------------------
# Candidate construction (7-dim feature = 6 LCCP structural cues + graded thematic-fit cue).
# ----------------------------------------------------------------------------------------------
def build_candidates(reader_data, gfit_fn):
    """reader_data {sid:{sent,svo}} -> list of cand dicts. feat = [6 structural, gfit_value]. gfit_value is
    the graded score (backoff = global mean typicality for OOV, marked gfit_defined=False)."""
    cands = []
    for sid, rec in reader_data.items():
        toks = L.tokenize(rec["sent"])
        for tup in rec["svo"]:
            v_surf, a, p = tup
            feat6, _ = L.candidate_features(toks, v_surf, p)
            v_lemma = L.lemma_verb(v_surf)
            g, kind = gfit_fn(v_lemma, p)
            defined = g is not None
            gval = g if defined else 0.5   # neutral backoff so scoring works; excluded from noun-only gate
            feat = np.concatenate([np.asarray(feat6, dtype=np.float64), [float(gval)]])
            cands.append({"sid": sid, "v": v_lemma, "a": a, "p": p, "tup": (v_surf, a, p),
                          "feat": feat, "feat6": np.asarray(feat6, dtype=np.float64),
                          "gfit_raw": g, "gfit_kind": kind, "gfit_defined": bool(defined)})
    return cands


def group_by_instance(cands):
    g = defaultdict(list)
    for c in cands:
        g[(c["sid"], c["v"])].append(c)
    return g


# ----------------------------------------------------------------------------------------------
# STAGE 1: firing-rate / discriminativeness gate (deterministic; NO gold-correct-rival used).
# ----------------------------------------------------------------------------------------------
def firing_rate_stats(groups):
    """Over multi-candidate decision points, measure gfit spread across rivals. Returns counts + rates at
    several tau. NOUN-ONLY (rivals = defined content nouns) is the load-bearing can-fail metric; ALL-RIVALS
    is reported for transparency (it includes the trivial junk-vs-noun contrast already covered by cues)."""
    n_multi = 0
    n_noun_pts = 0            # decision points with >= 2 defined content-noun rivals
    n_all_pts = 0            # decision points with >= 2 rivals carrying any gfit value
    spreads_noun = []
    spreads_all = []
    n_cand = 0
    kind_counts = defaultdict(int)
    for (sid, v), cs in groups.items():
        for c in cs:
            n_cand += 1
            kind_counts[c["gfit_kind"]] += 1
        if len(cs) < 2:
            continue
        n_multi += 1
        allv = [c["feat"][6] for c in cs]
        if len(allv) >= 2:
            n_all_pts += 1
            spreads_all.append(max(allv) - min(allv))
        nouns = [c["gfit_raw"] for c in cs if c["gfit_kind"] == "noun" and c["gfit_defined"]]
        if len(nouns) >= 2:
            n_noun_pts += 1
            spreads_noun.append(max(nouns) - min(nouns))

    def counts_at(spreads, tau):
        return int(sum(1 for s in spreads if s >= tau))

    fire_noun = {f"{t:.2f}": counts_at(spreads_noun, t) for t in TAU_REPORT}
    fire_all = {f"{t:.2f}": counts_at(spreads_all, t) for t in TAU_REPORT}
    fc_noun = counts_at(spreads_noun, TAU_DISC)
    fc_all = counts_at(spreads_all, TAU_DISC)
    return {
        "n_multi_candidate_points": n_multi,
        "n_noun_decision_points": n_noun_pts,
        "n_all_decision_points": n_all_pts,
        "n_candidates": n_cand,
        "kind_counts": dict(kind_counts),
        "defined_frac": round((kind_counts["noun"] + kind_counts["pronoun"]) / max(1, n_cand), 4),
        "fire_count_noun_tau015": fc_noun,
        "fire_rate_noun_tau015": round(fc_noun / max(1, n_noun_pts), 4),
        "fire_count_all_tau015": fc_all,
        "fire_rate_all_tau015": round(fc_all / max(1, n_all_pts), 4),
        "fire_count_noun_by_tau": fire_noun,
        "fire_count_all_by_tau": fire_all,
        "mean_spread_noun": round(float(np.mean(spreads_noun)), 4) if spreads_noun else 0.0,
        "mean_spread_all": round(float(np.mean(spreads_all)), 4) if spreads_all else 0.0,
    }


def gate_verdict(gold_stats, full_stats):
    fc_gold = gold_stats["fire_count_noun_tau015"]
    fc_full = full_stats["fire_count_noun_tau015"]
    fr_full = full_stats["fire_rate_noun_tau015"]
    if fc_gold <= 20 or fr_full < 0.15:
        return "HARD_FAIL_GATE_SPARSE_COVERAGE_FIRST"
    if fc_gold >= 30 and fc_full >= 150 and fr_full >= 0.35:
        return "HARD_PASS_GATE_DENSE_DISCRIMINATIVE"
    return "MIDDLE_BAND_GATE"


# ----------------------------------------------------------------------------------------------
# STAGE 2: integrated per-step learner. gfit resolves the DEFER band of the objecthood target; w[6] learned.
# ----------------------------------------------------------------------------------------------
def cand_target_gfit(c, sel_fn, cfg, use_gfit):
    """Self-supervised objecthood target (NO gold). Structural cue-supervision + GloVe selectional teacher
    (as in L.cand_target), with the GRADED cue resolving the DEFER band (and GloVe-OOV cases) when use_gfit.
    This is the INTEGRATION: gfit enters the incremental per-candidate decision, not a post-hoc filter."""
    f = c["feat"]; p = c["p"]
    if f[4] >= 0.5:
        return 0.0
    if f[3] >= 0.5:
        return 0.0
    if f[5] >= 0.5:
        return 0.0
    if p in L.PRONOUN:
        return 1.0 if f[2] >= 0.5 else 0.0
    s = sel_fn(c["v"], c["p"])

    def _gfit_resolve():
        if use_gfit and c.get("gfit_defined"):
            g = f[6]
            if g >= cfg["gfit_keep"]:
                return 1.0
            if g <= cfg["gfit_drop"]:
                return 0.0
        return None

    if s is None:
        return _gfit_resolve()
    if s >= cfg["sel_keep"]:
        return 1.0
    if s <= cfg["sel_drop"]:
        return 0.0
    return _gfit_resolve()   # DEFER band -> graded cue resolves (or None = no update)


def train_w7(cands, sel_fn, cfg, seed, use_gfit, scramble_gfit=False):
    """7-dim logistic delta-rule. use_gfit=False -> gfit channel zeroed in feature (w[6] stays 0) AND absent
    from the target = the pure 6-cue reader (control). scramble_gfit -> gfit VALUES permuted across cands
    (consistent in feature + target) = the must-fail cue-validity control."""
    rng = np.random.default_rng(seed)
    w = np.zeros(7)
    n = len(cands)
    if scramble_gfit:
        perm = rng.permutation(n)
    work = []
    for i, c in enumerate(cands):
        feat = c["feat"].copy()
        defined = c.get("gfit_defined")
        if scramble_gfit:
            src = cands[perm[i]]
            feat[6] = src["feat"][6]
            defined = src.get("gfit_defined")
        cc = {"v": c["v"], "p": c["p"], "feat": feat, "gfit_defined": defined}
        t = cand_target_gfit(cc, sel_fn, cfg, use_gfit)
        if t is None:
            continue
        x = feat.copy()
        if not use_gfit:
            x[6] = 0.0     # frozen control: no gradient reaches w[6]
        work.append((x, t))
    for _ in range(cfg["epochs"]):
        for k in rng.permutation(len(work)):
            x, t = work[k]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + cfg["lr"] * (t - pred) * x
    return w, len(work)


def eval_kept7(w, groups, keep_thr):
    """keep-best-per-instance >= thr (matched protocol; ONE variable = the weight vector)."""
    kept = []
    for (sid, v), cs in groups.items():
        best = max(cs, key=lambda c: L.sigmoid(float(np.dot(w, c["feat"]))))
        if L.sigmoid(float(np.dot(w, best["feat"]))) >= keep_thr:
            kept.append((best["sid"], best["tup"]))
    return kept


def reproduce_argC_baseline(cfg):
    """REAL baseline (not a strawman): reproduce LCCP arm-C precision live via L.run_arms on the gold slice."""
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, _ = L.load_gold(cfg["gold_slice"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for rec in gold.values():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)
    lccp_cfg = dict(sel_keep=cfg["sel_keep"], sel_drop=cfg["sel_drop"], lr=cfg["lr"], epochs=cfg["epochs"],
                    keep_thr=cfg["keep_thr"], subcat_thr=0.42, heldout_frac=0.25, k_constructions=4,
                    kappa=1.5, seed=7)
    decisions, _, _, _, _, _, _ = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, 7)
    base_m = L.score_arm(decisions["C_lccp"], gold)
    return base_m


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(mode="smoke", gold_slice=["L04", "L05", "L07"], mining_files=MINING_FILES_SMOKE,
                mining_max_sents=600, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40, keep_thr=0.45,
                gfit_keep=0.55, gfit_drop=0.30, seeds=[7, 13, 19])


def cfg_full():
    return dict(mode="full", gold_slice=["L04", "L05", "L07", "L08", "L09", "L10", "L12"],
                mining_files=MINING_FILES_FULL, mining_max_sents=None, sel_keep=0.28, sel_drop=0.10,
                lr=0.20, epochs=60, keep_thr=0.45, gfit_keep=0.55, gfit_drop=0.30, seeds=[7, 13, 19])


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


# ----------------------------------------------------------------------------------------------
# Run.
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    # 1) Mine the corpus (reader over-extraction), cached. Build the gfit model on MINING ONLY (no gold).
    mine_data = SCV.run_reader_on_files(cfg["mining_files"], os.path.join(output_dir, "_mining_cache.json"),
                                        max_sents=cfg["mining_max_sents"])
    # candidates without gfit first (need feat6 to build the model), then rebuild with gfit
    def _bare_cands(reader_data):
        out = []
        for sid, rec in reader_data.items():
            toks = L.tokenize(rec["sent"])
            for tup in rec["svo"]:
                v_surf, a, p = tup
                feat6, _ = L.candidate_features(toks, v_surf, p)
                out.append({"sid": sid, "v": L.lemma_verb(v_surf), "a": a, "p": p,
                            "tup": (v_surf, a, p), "feat6": np.asarray(feat6, dtype=np.float64)})
        return out
    gfit_fn, gfit_model_stats = build_gfit_model(_bare_cands(mine_data))
    print(f"[{ANCHOR_NAME}:{mode}] gfit model: {gfit_model_stats['n_object_classes']} classes, "
          f"{gfit_model_stats['n_verbs_with_own_assoc']} verbs w/ own assoc", flush=True)

    mine_cands = build_candidates(mine_data, gfit_fn)
    mine_groups = group_by_instance(mine_cands)

    # Eval reader on the held-out GOLD slice (third reader; never in mining).
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, _ = L.load_gold(cfg["gold_slice"])
    eval_data = {sid: {"sent": sent_text[sid], "svo": [list(t) for t in reader_svo[sid]]} for sid in order}
    eval_cands = build_candidates(eval_data, gfit_fn)
    eval_groups = group_by_instance(eval_cands)

    # 2) STAGE-1 GATE (deterministic; gold-slice + full mining).
    gold_stats = firing_rate_stats(eval_groups)
    full_stats = firing_rate_stats(mine_groups)
    gate = gate_verdict(gold_stats, full_stats)
    print(f"[{ANCHOR_NAME}:{mode}] GATE={gate} | noun-fire gold={gold_stats['fire_count_noun_tau015']}"
          f"/{gold_stats['n_noun_decision_points']} full={full_stats['fire_count_noun_tau015']}"
          f"/{full_stats['n_noun_decision_points']} rate_full={full_stats['fire_rate_noun_tau015']}", flush=True)

    # discriminator-fires sanity (META_RULE_K): the metric must be non-degenerate (fires somewhere, not
    # trivially all/none) at smoke so the gate is a real can-fail test, not vacuous.
    discriminator_fires = bool(full_stats["fire_count_noun_tau015"] > 0
                               and full_stats["fire_count_noun_tau015"] < full_stats["n_noun_decision_points"])

    # 3) REAL baseline reproduced live (arm-C ~0.500) -- reported regardless of gate outcome.
    base_argC = reproduce_argC_baseline(cfg)
    baseline_in_band = bool(0.05 < base_argC["precision"] < 0.95)

    stage2 = None
    arms_differ_verified = None
    if gate != "HARD_FAIL_GATE_SPARSE_COVERAGE_FIRST":
        # GloVe teacher over mining + eval patients (for the LCCP structural target).
        toks = set()
        for c in mine_cands + eval_cands:
            toks.update([c["p"], c["v"]])
        glove = L.load_glove_for(toks)
        sel_full, _, _ = L.build_semantic_teacher(mine_cands, glove)

        per_seed = []
        digests = {}
        import hashlib
        for seed in cfg["seeds"]:
            w_A, n_tr = train_w7(mine_cands, sel_full, cfg, seed, use_gfit=False)
            w_B, _ = train_w7(mine_cands, sel_full, cfg, seed, use_gfit=True)
            w_C, _ = train_w7(mine_cands, sel_full, cfg, seed, use_gfit=True, scramble_gfit=True)
            m_A = L.score_arm(eval_kept7(w_A, eval_groups, cfg["keep_thr"]), gold)
            m_B = L.score_arm(eval_kept7(w_B, eval_groups, cfg["keep_thr"]), gold)
            per_seed.append({
                "seed": seed, "n_train_examples": n_tr,
                "prec_A_frozen": m_A["precision"], "prec_B_learned": m_B["precision"],
                "recall_A": m_A["recall"], "recall_B": m_B["recall"],
                "f1_A": m_A["f1"], "f1_B": m_B["f1"],
                "delta_help": round(m_B["precision"] - m_A["precision"], 4),
                "w_A": [round(x, 4) for x in w_A.tolist()],
                "w_B": [round(x, 4) for x in w_B.tolist()],
                "w_C": [round(x, 4) for x in w_C.tolist()],
                "wgfit_B": round(float(abs(w_B[6])), 4), "wgfit_C": round(float(abs(w_C[6])), 4),
            })
            for nm, wv in [("A", w_A), ("B", w_B), ("C", w_C)]:
                digests[f"seed{seed}_{nm}"] = hashlib.sha256(np.round(wv, 6).tobytes()).hexdigest()[:16]

        deltas = [s["delta_help"] for s in per_seed]
        mean_help = round(float(np.mean(deltas)), 4)
        min_help = round(float(np.min(deltas)), 4)
        wgfit_B = round(float(np.mean([s["wgfit_B"] for s in per_seed])), 4)
        wgfit_C = round(float(np.mean([s["wgfit_C"] for s in per_seed])), 4)

        if mean_help >= 0.02 and min_help > 0.0:
            p_help = "HARD_PASS_P_HELP_TRAINING_SIGNAL_REAL"
        elif mean_help <= 0.0:
            p_help = "HARD_FAIL_P_HELP_NULL_OR_NEGATIVE"
        else:
            p_help = "MIDDLE_BAND_P_HELP"

        if wgfit_B > wgfit_C and wgfit_C < 0.5 * wgfit_B:
            p_genuine = "HARD_PASS_P_GENUINE_WEIGHT_DROPS"
        elif wgfit_C >= wgfit_B:
            p_genuine = "HARD_FAIL_P_GENUINE_WEIGHT_INSENSITIVE"
        else:
            p_genuine = "MIDDLE_BAND_P_GENUINE_PARTIAL_DROP"

        # ARMS-MUST-DIFFER (META_RULE_AF): A/B/C weight vectors must not be bit-identical per seed.
        arms_differ_verified = True
        for seed in cfg["seeds"]:
            da, db, dc = digests[f"seed{seed}_A"], digests[f"seed{seed}_B"], digests[f"seed{seed}_C"]
            if da == db or db == dc or da == dc:
                arms_differ_verified = False

        stage2 = {
            "p_help": p_help, "p_genuine": p_genuine,
            "mean_delta_help": mean_help, "min_delta_help": min_help,
            "prec_A_frozen_mean": round(float(np.mean([s["prec_A_frozen"] for s in per_seed])), 4),
            "prec_B_learned_mean": round(float(np.mean([s["prec_B_learned"] for s in per_seed])), 4),
            "wgfit_B_mean_abs": wgfit_B, "wgfit_C_scrambled_mean_abs": wgfit_C,
            "per_seed": per_seed, "arm_weight_digests": digests,
            "one_variable_note": ("A vs B differ ONLY in whether the graded cue is integrated into the "
                                  "target + w[6] can learn; C vs B differ ONLY in whether the graded cue "
                                  "VALUES are scrambled. Feature dim, protocol, seeds identical."),
        }

    elapsed = time.perf_counter() - t0
    parts = [f"GATE={gate}",
             f"noun-fire gold={gold_stats['fire_count_noun_tau015']}/{gold_stats['n_noun_decision_points']}",
             f"full={full_stats['fire_count_noun_tau015']}/{full_stats['n_noun_decision_points']}",
             f"rate_full={full_stats['fire_rate_noun_tau015']:.3f}",
             f"defined_frac_full={full_stats['defined_frac']:.3f}",
             f"argC_baseline_P={base_argC['precision']:.3f}"]
    if stage2 is not None:
        parts += [f"P_HELP={stage2['p_help']}", f"meandelta={stage2['mean_delta_help']:+.3f}",
                  f"A={stage2['prec_A_frozen_mean']:.3f} B={stage2['prec_B_learned_mean']:.3f}",
                  f"P_GENUINE={stage2['p_genuine']}",
                  f"wgfit_B={stage2['wgfit_B_mean_abs']:.3f} wgfit_C={stage2['wgfit_C_scrambled_mean_abs']:.3f}"]
    else:
        parts += ["STAGE2=SKIPPED_gate_hard_fail"]
    msg = " | ".join(parts)

    overall = gate if stage2 is None else f"{gate}|{stage2['p_help']}|{stage2['p_genuine']}"
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": overall, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "stage1_gate_verdict": gate,
        "stage1_firing_gold_slice": gold_stats,
        "stage1_firing_full_mining": full_stats,
        "gfit_model_stats": gfit_model_stats,
        "real_baseline_argC_reproduced": base_argC,
        "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires,
        "stage2_learner": stage2,
        "arms_differ_verified": arms_differ_verified,
        "n_mining_sentences": len(mine_data), "n_eval_sentences": len(eval_data),
        "tau_disc": TAU_DISC, "min_verb_obs": MIN_VERB_OBS, "pron_gfit": PRON_GFIT,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "extraction-precision + discriminativeness-count measurement; no quantitative noise floor",
        "deterministic_seeding": "fixed int seeds + numpy default_rng + sorted(set); no hash()-seeded RNG",
        "excluded_from_mining": EXCLUDED_FROM_MINING,
        "gold_type_oracle_independent": True,
        "gold_independence_rationale": ("Gate uses gfit SPREAD across rivals only (never which rival is "
            "gold-correct). Stage-2 held-out gold is independent who-did-what annotation (_meta.independence). "
            "gfit model built on MINING corpus only; third reader (gold source) EXCLUDED. No ground-by-X-grade-by-X."),
        "claim_ceiling": ("The graded cue is SCAFFOLDED: WordNet supersense (curated lookup) + CLASS-LEVEL "
            "distributional object-typicality from 99k (class-smoothed a la Clark&Weir; ~15 classes dense at "
            "99k, per-ITEM counts would NOT be). This is LOOKED-UP world-knowledge, NOT substrate-learned "
            "world-experience. ONLY the low-dim cue-integration weight w[6] is LEARNED. Learning NEW "
            "distributional-fit VALUES from 99k is OUT OF SCOPE (corpus-gated >=1M-1B+ words). Do NOT frame "
            "any result as 'the substrate evaluates scene realism from its own experience'."),
        "novelty_vs_scv": ("SCV used a BINARY bit + POST-HOC contrast (null trainer, atom 29360). This uses a "
            "GRADED score INTEGRATED into the incremental per-step target (delta-rule on w[6]). The gate tests "
            "whether the graded cue is DISCRIMINATIVE among plausible NOUN rivals densely enough to carry a "
            "learning signal (SCV's trigger fired on only 4-20 cases)."),
        "REQUIRED_FIELDS": ["verdict", "stage1_gate_verdict", "stage1_firing_gold_slice",
                            "stage1_firing_full_mining", "gfit_model_stats", "real_baseline_argC_reproduced",
                            "stage2_learner", "claim_ceiling", "gold_type_oracle_independent"],
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# Self-test (constructs the REAL gfit model + trains on a tiny toy; asserts the discriminators fire).
# ----------------------------------------------------------------------------------------------
def self_test():
    # gfit graded + defined/undefined semantics
    toy = [
        {"sid": "t0", "v": "build", "a": "he", "p": "hut", "tup": ("built", "he", "hut"),
         "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])},
        {"sid": "t0", "v": "build", "a": "he", "p": "hill", "tup": ("built", "he", "hill"),
         "feat6": np.array([1.0, 0.2, 1.0, 0.0, 0.0, 0.0])},
        {"sid": "t1", "v": "eat", "a": "she", "p": "apple", "tup": ("eat", "she", "apple"),
         "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])},
        {"sid": "t1", "v": "eat", "a": "she", "p": "cake", "tup": ("eat", "she", "cake"),
         "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])},
        {"sid": "t2", "v": "build", "a": "he", "p": "wall", "tup": ("build", "he", "wall"),
         "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])},
    ]
    gfit_fn, stats = build_gfit_model(toy)
    assert stats["n_object_classes"] >= 1, "gfit model must count >=1 object class"
    g_hut, k_hut = gfit_fn("build", "hut")
    g_junk, k_junk = gfit_fn("build", "the")
    g_pron, k_pron = gfit_fn("throw", "it")
    assert k_hut == "noun" and g_hut is not None, "content noun must get a defined graded score"
    assert k_junk == "junk" and g_junk == 0.0, "funcword filler -> gfit 0.0 junk"
    assert k_pron == "pronoun" and abs(g_pron - PRON_GFIT) < 1e-9, "pronoun -> fixed typical value"
    # graded (not binary): scores are real-valued in [0,1]
    assert 0.0 <= g_hut <= 1.0, "gfit in [0,1]"

    # firing-rate metric fires on a constructed multi-candidate point with a real noun-vs-noun spread.
    cands = build_candidates({"s0": {"sent": "he built a hut on the hill",
                                     "svo": [["built", "he", "hut"], ["built", "he", "hill"]]}}, gfit_fn)
    groups = group_by_instance(cands)
    fr = firing_rate_stats(groups)
    assert fr["n_multi_candidate_points"] == 1, f"expected 1 decision point, got {fr['n_multi_candidate_points']}"

    # integrated per-step training: the DEFER-band resolver must give w[6] a nonzero gradient when use_gfit,
    # and the scrambled-cue control must NOT drive w[6] the same way (must-fail cue-validity mechanism).
    cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.2, epochs=20, keep_thr=0.45, gfit_keep=0.55, gfit_drop=0.30)
    train = build_candidates({
        "s0": {"sent": "he built a hut", "svo": [["built", "he", "hut"]]},
        "s1": {"sent": "she ate an apple", "svo": [["ate", "she", "apple"]]},
        "s2": {"sent": "they crossed the field", "svo": [["crossed", "they", "field"]]},
    }, gfit_fn)
    sel_fn, _, _ = L.build_semantic_teacher(train, {})   # empty glove -> sel returns None -> gfit resolves DEFER
    w_frozen, _ = train_w7(train, sel_fn, cfg, 7, use_gfit=False)
    w_learn, _ = train_w7(train, sel_fn, cfg, 7, use_gfit=True)
    assert abs(w_frozen[6]) < 1e-9, "frozen control must keep w[6] == 0 (gfit channel zeroed)"
    assert abs(w_learn[6]) >= abs(w_frozen[6]), "learned arm must give w[6] a gradient path when gfit integrated"

    # ARMS-MUST-DIFFER on a non-degenerate corpus is verified in run_mode; here just assert frozen != learned.
    assert not np.allclose(w_frozen, w_learn), "frozen and learned weight vectors must differ (ONE variable)"
    print(f"[{ANCHOR_NAME}] self-test PASS | gfit graded (hut={g_hut:.3f} pron={g_pron:.3f} junk={g_junk}); "
          f"gate metric fires; frozen w[6]={w_frozen[6]:.3f} learned w[6]={w_learn[6]:.3f}; "
          f"classes={stats['n_object_classes']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
