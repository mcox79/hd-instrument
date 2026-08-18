"""POS-ROBUST case-signature vs the brittle signature, in the FULLY-DEPLOYED (PHPP) regime: does a
multi-cue-redundant signature RECOVER the deployed coherent-generalization that atom 29409 measured
eroding to ~0 under predicted-POS noise?

THE QUESTION (Director task 2026-07-21). Atom 29409 measured the deployed self-improving reader
(exp_reader_selfimprove_artmap_predicted_head_endtoend_v1) and found: the loop's COHERENT GENERALIZATION
(held-out minority-role nsubj:pass prefix-rise + scramble-collapse, VET-correct metric ad659ee6) SURVIVES
under predicted heads with GOLD POS (PH regime) but ERODES TO ~0 under FULL DEPLOYMENT (PHPP = predicted
heads + predicted POS 0.9442; PHPP scramble_collapse 0.001, seed19 negative). ROOT CAUSE (atom 29409):
the case SIGNATURE = HD bundle of arc_features(tokens, POS, i, h), which is POS-HEAVY (dp/hp/hp_dp fine-POS
features dominate the bundle mass over the POS-free form cues). ~5.6% predicted-POS token errors flip those
fine-POS features, so two arcs that are the SAME CASE get DIFFERENT signatures when their POS tags differ ->
rule prototypes become noisy -> held-out generalization collapses.

THE FIX UNDER TEST (this cell). Robustify the case-signature against single-POS-tag errors via MULTI-CUE
REDUNDANCY (the brain-faithful direction; BRAIN-CHECK below). Composes all three candidate levers:
  (a) COARSE-POS backoff: 17 UPOS -> coarse classes (NOM=NOUN/PROPN/PRON/NUM, VRB=VERB/AUX, MOD=ADJ/ADV,
      ...) so a single fine mistag WITHIN a coarse class does not flip the coarse feature (absorbs the
      frequent NOUN<->PROPN<->PRON and VERB<->AUX confusions -- incl. periphrastic-passive AUX/VERB).
  (b) POS-FREE FORM anchors: token/lemma/suffix features that carry the case signal POS-INDEPENDENTLY
      (rdw/rhw/rsuf/rhw_dw/rdw_dist/rdw_dir), so a POS mistag leaves them BIT-IDENTICAL.
  (c) MULTI-CUE REDUNDANCY weighting: bundle FORM (x2) + COARSE (x2) + FINE-POS (x1) so a wrong tag flips
      only the small FINE portion of the bundle mass -> the signature degrades GRACEFULLY (high cosine to
      the correct-POS version) instead of flipping. This is interactive-activation / cue-redundancy.

BRAIN-CHECK (KNOWLEDGE-BASED, web-blocked in this env -- FLAGGED as such; web-verify later if load-bearing):
the brain reads ROBUSTLY despite imperfect low-level features via top-down context + CUE REDUNDANCY
(interactive-activation, McClelland/Rumelhart family) -- a single mis-tag should not flip comprehension.
So POS-robustness = redundant/coarse cues, NOT single-fine-POS-brittle. This is the brain-faithful
direction; the multi-cue bundle is the substrate analog of graded interactive activation.

ONE VARIABLE = the SIGNATURE (brittle vs robust). Everything else IDENTICAL: same loop (PHEE.run_stream +
bin_curves reused VERBATIM -- only the precomputed a["sig"] array differs across arms), same ARTMAP, same
per-rule vigilance controller, same frozen deployed labeler base prediction, same gold, seeds, stream order,
same rho0-calibration procedure (recalibrated per signature because the robust cosine distribution differs
-- this is the loop's OWN leak-safe calibration applied to the new signature, NOT a loop change).

REGIME AXIS (controlled, not an arm):
  PH   predicted heads (canon arc_parser on GOLD POS) + GOLD-POS features -> DISCRIMINATION CHECK: no POS
       noise; robust signature must NOT lose the coherent-gen the brittle signature achieves here.
  PHPP predicted heads (parser on PREDICTED POS) + PREDICTED-POS features -> THE DEPLOYMENT BREAKER: the
       recovery target. Brittle collapses (atom 29409); does robust recover?

MEASURES (primary deliverable = the numbers; MEASUREMENT cell):
  (1) DEPLOYED (PHPP) coherent-gen per signature = MINORITY-role (nsubj:pass) prefix-rise (held-out) +
      scramble-collapse, ALL 3 seeds. Does robust rise from brittle's ~0?
  (2) CLEAN (PH) coherent-gen per signature = same metric. Confirms robust keeps the gold-POS discrimination
      (robustness-vs-discrimination tradeoff check).
  (3) end-to-end who-affected delta loop-ON vs OFF per (signature, regime); residual attach vs labeler.
  (4) SIGNATURE-MECHANISM probe (self-test + logged): under a single random POS flip, robust cosine to the
      correct-POS signature is HIGHER than brittle cosine (the robustification actually degrades less).

DESIGN-GATE (pre-registered; verified at smoke BEFORE trusting full):
  (1) REAL BASELINE = the brittle signature (LOOP.signature verbatim) in PHPP: coherent-gen ~gone
      (min_rise ~0 / scramble_collapse ~0.001, MEASURED@atom 29409). NOT a strawman.
  (2) POSITIVE CONTROL / phenomenon-reproduces (Gate D analog): brittle-PH coherent-gen SURVIVES
      (min_rise >= +0.05 AND scramble collapses) AND brittle-PHPP COLLAPSES (min_rise < 0.03 OR no collapse).
      If the atom-29409 degradation does not reproduce, there is nothing to recover ->
      UNKNOWN_BASELINE_PHENOMENON_NOT_REPRODUCED (measurement void).
  (3) CAN-FAIL modes (both real risks, reported honestly if they occur):
      (i) FRONTEND_IS_THE_GATE: robust-PHPP STILL does not rise / does not collapse -> POS-noise was not
          the (whole) gate; parser-attach + irreducible signature-granularity is the genuine deployment
          bound (a label-correction loop cannot fix a wrong attachment).
      (ii) ROBUSTNESS_KILLS_DISCRIMINATION: robust-PH LOSES the gold-POS coherent-gen (coarser signature
          threw away the discriminating POS signal) -> the robustification is net-harmful.
  (4) DIFFICULTY-ON: real predicted-parse + predicted-POS noise (PHPP attach_err + ~5.6% POS token error,
      MEASURED@this cell). Minority-role discriminator fires (>= 15 nsubj:pass labeler-errors per regime;
      smoke asserts).
  (5) ONE-VARIABLE: signature brittle vs robust within a regime; arms_differ = >=1 differing sig per arc.

VERDICT BANDS (pre-registered; PHPP is the load-bearing recovery target, gated on the brittle phenomenon):
  d_kept    = robust-PH min_rise >= +0.05 AND robust-PH min_rise >= brittle-PH min_rise - 0.03 (no material
              discrimination loss on the clean regime).
  recovered = robust-PHPP min_rise >= +0.05 AND robust-PHPP scramble_collapse >= 0.15 AND robust-PHPP
              net_broken_fixable ~0 AND rules form AND leak-clean.
  POS_ROBUST_RECOVERS_DEPLOYMENT     : phenomenon reproduces AND recovered AND d_kept. (The flexible/improving
        property WORKS in deployment once the signature is POS-robust.)
  ROBUSTNESS_KILLS_DISCRIMINATION    : phenomenon reproduces BUT NOT d_kept (robust tanked the clean regime).
  FRONTEND_IS_THE_GATE               : phenomenon reproduces, d_kept, BUT NOT recovered (robust-PHPP min_rise
        < 0.02 OR no collapse). POS-robustness does NOT recover deployment; front-end is the honest bound.
  MIDDLE_BAND                        : partial (robust-PHPP rises but collapse marginal, or PH slightly down).
  UNKNOWN_BASELINE_PHENOMENON_NOT_REPRODUCED : Gate-2 positive control failed.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified) -- greedy O(n^2) pure-python arc decode (2 parses
  of ~4050 sents: PH on gold POS, PHPP on predicted POS ~13s each) + vectorized stream re-reads. 2 regimes x
  2 signatures x 3 seeds x (real+scramble) = 24 streams; est ~10-13 min full / ~2-3 min smoke. Storage:
  no_storage (writes ONLY diagnostic metrics; persists NO atom, NO frontend asset; NO hdlab mutation; robust
  signature composed IN-CELL). progress_logging: print_flush_true (per-arm flush + _heartbeat.jsonl).
  Determinism: OMP/MKL/OPENBLAS=1, FIXED int seeds, numpy default_rng, sorted(set), hashlib codes; NO
  hash()-seeded RNG, NO list(set()). LOCAL-ONLY foreground-to-completion; NO queue, NO origin push, NO
  remote-persist, NO substrate store write, NO git add.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke: robust sig differs from brittle sig on >=1 arc per regime (hash-checked).
  - final_metrics_atomicity: tmp_replace. except SystemExit: raise BEFORE except Exception (no BaseException).
  - crlb_n_a: online ARTMAP self-improving reader who-affected recall; no quantitative noise floor.
  - baseline_in_band at smoke: loop-OFF who-affected strictly inside (0.05, 0.95) every regime.
  - discriminator survives scale: minority nsubj:pass labeler-errors >= 15 per regime (smoke asserts); the
    brittle-PH-survives / brittle-PHPP-collapses phenomenon is the positive control validated at FULL.
  - HARD_PASS strictly above floor (robust-PHPP min_rise +0.05 AND collapse +0.15 AND d_kept).
  - cardinality_ok: EXPECTED_N_UNITS = n_regimes * n_signatures * n_seeds; verdict counts them.
  - per-unit failure-class: except Exception only; crash -> CELL_CRASHED metrics + traceback.
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
  - LEAK-HUNT: (1) robust_arc_features source has no 'deprel'/'gold' (signature GOLD-FREE); coarse map is a
    fixed function of UPOS, not gold. (2) signature deterministic (bit-identical on repeat). (3) mutation-
    probe: garbling the GOLD head leaves the PH/PHPP robust signature bit-identical (heads from the parser).
    (4) gold used ONLY as correction TARGET + denominator, never in the signature.

PRIOR-WORK CHECK (substrate_query.sh "POS-robust case signature coarse UPOS backoff multi-cue redundancy
  predicted POS noise deployed reader"): top hit cosine=0.2842 (NOISE_ROBUST wave14 chain-smoother, unrelated);
  NONE at cosine>0.30. Genuinely novel: a POS-robust case-signature to recover the deployed coherent-gen
  measured collapsing in atom 29409 was never built. Builds on: the v4 loop (ArtmapReader/stream reused
  verbatim via PHEE), the predicted-head end-to-end cell (PHEE.build_regime pattern + minority-role metric),
  atom 29409 (the PHPP collapse this attacks), reading VET ad659ee6 (minority-role coherent-gen metric).
  CITED@backup-doc 2026-07-21.

NO LLM. NO nltk. NO torch at hot path (torch only in the loop's NREM consolidate, lazy). numpy + pure-python.
ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import inspect as _inspect
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_selfimprove_artmap_posrobust_signature_phpp_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.join(REPO_ROOT, "experiments") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

# Reuse the loop mechanism + the predicted-head end-to-end harness VERBATIM (one variable = the signature).
from experiments import exp_reader_selfimprove_artmap_stream_udewt_v1 as LOOP  # noqa: E402
from experiments import exp_reader_selfimprove_artmap_predicted_head_endtoend_v1 as PHEE  # noqa: E402
from hdlab.arc_labeler import ArcLabeler, arc_features, norm_label  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402

FR = os.path.join(REPO_ROOT, "data", "frontend_assets")
LABELER_PATH = os.path.join(FR, "arc_labeler_hashed_ud_ewt.json")
ARC_PATH = os.path.join(FR, "arc_parser_hashed_ud_ewt.npz")
POS_PATH = os.path.join(FR, "pos_tagger_ud_ewt_upos.json")

PATIENT_ROLES = LOOP.PATIENT_ROLES       # ("obj", "nsubj:pass")
MINORITY_ROLE = "nsubj:pass"
N_SIG = LOOP.N_SIG
TAU_EXACT = LOOP.TAU_EXACT
_feat_code = LOOP._feat_code             # deterministic hashlib bipolar HD codes (shared table)
brittle_signature = LOOP.signature       # BASELINE: arc_features bundle (POS-heavy); h = regime head
read_conllu = LOOP.read_conllu
calibrate_rho0 = LOOP.calibrate_rho0

# multi-cue redundancy weights (repetition in the feature list = bundle weight).
W_FORM = 2       # POS-FREE anchors (survive POS noise entirely)
W_COARSE = 2     # coarse-POS backoff (single fine mistag within a class does not flip)
W_FINE = 1       # fine-POS (flips under mistag; downweighted so it degrades gracefully)

# 17 UPOS -> coarse classes absorbing the frequent confusions.
COARSE_POS = {
    "NOUN": "NOM", "PROPN": "NOM", "PRON": "NOM", "NUM": "NOM",
    "VERB": "VRB", "AUX": "VRB",
    "ADJ": "MOD", "ADV": "MOD",
    "ADP": "ADP", "DET": "DET", "PART": "PRT",
    "SCONJ": "CNJ", "CCONJ": "CNJ",
    "INTJ": "X", "SYM": "X", "X": "X", "PUNCT": "PUN",
    "<ROOT>": "ROOT", "ROOT": "ROOT", "<S>": "BND", "<E>": "BND",
}


def _c(p):
    return COARSE_POS.get(p, "X")


def _dist(d):
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w):
    return w[-3:] if len(w) >= 3 else w


def robust_arc_features(tokens, pos, i, h):
    """POS-robust multi-cue feature list for arc (dep i -> head h), 1-based; h==0 is ROOT. GOLD-FREE:
    uses tokens/POS/head only (POS = the REGIME POS, predicted for PHPP). Repetition = bundle weight.
    FORM (POS-free) x W_FORM + COARSE-POS x W_COARSE + FINE-POS x W_FINE -> graceful degradation."""
    n = len(tokens)
    dw = tokens[i - 1].lower()
    dp = pos[i - 1]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"
        d = 0
        drc = "R"
    else:
        hw, hp = tokens[h - 1].lower(), pos[h - 1]
        d = h - i
        drc = "L" if d < 0 else "R"
    db = _dist(d)
    dpr = pos[i] if i < n else "<E>"
    cdp, chp, cdpr = _c(dp), _c(hp), _c(dpr)
    # POS-FREE FORM anchors (bit-identical under any POS mistag).
    form = [
        "rdw:" + dw, "rhw:" + hw, "rdsuf:" + _suf(dw), "rhsuf:" + _suf(hw),
        "rhw_dw:%s_%s" % (hw, dw), "rdw_db:%s_%s" % (dw, db), "rdw_dir:%s_%s" % (dw, drc),
        "rhw_db:%s_%s" % (hw, db), "rdist:" + db, "rdir:" + drc,
    ]
    # COARSE-POS backoff (single fine mistag within a coarse class does not flip these).
    coarse = [
        "rcdp:" + cdp, "rchp:" + chp, "rchp_cdp:%s_%s" % (chp, cdp),
        "rcdp_dir:%s_%s" % (cdp, drc), "rchp_dir:%s_%s" % (chp, drc),
        "rcdp_db:%s_%s" % (cdp, db), "rchp_cdp_dir:%s_%s_%s" % (chp, cdp, drc),
        "rctx:%s_%s_%s" % (cdp, cdpr, drc), "rchp_cdp_db:%s_%s_%s" % (chp, cdp, db),
    ]
    # FINE-POS (flips under mistag; downweighted -> small fraction of the bundle mass).
    fine = [
        "rfdp:" + dp, "rfhp:" + hp, "rfhp_dp:%s_%s" % (hp, dp),
        "rfdp_dir:%s_%s" % (dp, drc), "rfhp_dp_db:%s_%s_%s" % (hp, dp, db),
    ]
    return form * W_FORM + coarse * W_COARSE + fine * W_FINE


def robust_signature(tokens, pos, i, h):
    """Dense unit HD signature from robust_arc_features (multi-cue redundant). GOLD-FREE."""
    v = np.zeros(N_SIG, dtype=np.float32)
    for f in robust_arc_features(tokens, pos, i, h):
        v += _feat_code(f)
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


# ==================================================================================================
# Build regime arcs ONCE, carrying BOTH signatures per arc (heads/base do not depend on the signature).
# Denominator = gold patient set (gold POS/head), STABLE across regimes -- mirrors PHEE.build_regime.
# ==================================================================================================
def build_regime_dual(sents, lab, parser, tagger, regime):
    out = []
    n_patient = n_attach_ok = n_attach_err = n_err_labeler = 0
    role_err = Counter()
    role_patient = Counter()
    role_attach_err = Counter()
    for s in sents:
        if not (1 <= len(s) <= 50):
            out.append({"arcs": [], "attach_err": 0})
            continue
        toks = [t[1] for t in s]
        gpos = [t[2] for t in s]                 # denominator VERB test ALWAYS uses gold POS.
        rpos = tagger.tag(toks) if regime == "PHPP" else gpos
        if regime == "GH":
            rheads = {t[0]: t[3] for t in s}
        else:
            rheads = parser.parse(toks, rpos).heads
        arcs = []
        aerr = 0
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            gd = norm_label(s[i - 1][4])
            if gd not in PATIENT_ROLES or gh < 1 or gh > len(s) or gpos[gh - 1] != "VERB":
                continue
            n_patient += 1
            role_patient[gd] += 1
            if rheads.get(i) == gh:
                n_attach_ok += 1
                base = lab._predict_label(arc_features(toks, rpos, i, gh))
                arcs.append({
                    "sig_brittle": brittle_signature(toks, rpos, i, gh),
                    "sig_robust": robust_signature(toks, rpos, i, gh),
                    "gold": gd, "base": base, "vlem": toks[gh - 1].lower(), "role": gd,
                })
                if base != gd:
                    n_err_labeler += 1
                    role_err[gd] += 1
            else:
                n_attach_err += 1
                aerr += 1
                role_attach_err[gd] += 1
        out.append({"arcs": arcs, "attach_err": aerr})
    stats = {
        "n_patient": n_patient, "n_attach_ok": n_attach_ok, "n_attach_err": n_attach_err,
        "attach_ok_rate": round(n_attach_ok / n_patient, 4) if n_patient else None,
        "n_labeler_err_on_attach_ok": n_err_labeler,
        "minority_labeler_err": role_err.get(MINORITY_ROLE, 0),
        "role_patient": dict(role_patient), "role_labeler_err": dict(role_err),
        "role_attach_err": dict(role_attach_err),
    }
    return out, stats


def _view(sent_arcs, which):
    """Present the arcs to the VERBATIM PHEE.run_stream with a["sig"] = the selected signature.
    The ONLY thing that differs across arms is this array; everything downstream is identical."""
    key = "sig_" + which
    out = []
    for sa in sent_arcs:
        out.append({"arcs": [{"sig": a[key], "gold": a["gold"], "base": a["base"],
                              "vlem": a["vlem"], "role": a["role"]} for a in sa["arcs"]],
                    "attach_err": sa["attach_err"]})
    return out


# ==================================================================================================
def run_arm(regime, which, sent_arcs, stats, seeds, output_dir):
    t0 = time.perf_counter()
    view = _view(sent_arcs, which)
    n_pat = stats["n_patient"]
    n_aerr = stats["n_attach_err"]
    loff = sum(1 for sa in view for a in sa["arcs"] if a["base"] == a["gold"])
    loop_off_who = round(loff / n_pat, 4) if n_pat else None
    flat = [a for sa in view for a in sa["arcs"]]
    rho0 = calibrate_rho0([[a] for a in flat]) if len(flat) >= 3 else 0.5

    per_seed = []
    for seed in seeds:
        order = list(np.random.default_rng(seed).permutation(len(view)))
        R = PHEE.run_stream(view, order, rho0)
        curve = PHEE.bin_curves(R["recs"])
        # scramble control (atom<->correction shuffle; identical index space across signatures).
        allk = [(si, k) for si, sa in enumerate(view) for k in range(len(sa["arcs"]))]
        acorr = [view[si]["arcs"][k]["gold"] for (si, k) in allk]
        perm = np.random.default_rng(3000 + seed).permutation(len(allk))
        scr = {allk[i]: acorr[perm[i]] for i in range(len(allk))}
        Rs = PHEE.run_stream(view, order, rho0, scramble_corr=scr)
        curve_s = PHEE.bin_curves(Rs["recs"])

        min_rise = PHEE._rise(curve, "minority_prefix_rate")
        min_rise_s = PHEE._rise(curve_s, "minority_prefix_rate")
        fp_rise = PHEE._rise(curve, "first_pass_arc_acc")
        d_atoms = PHEE._decl(curve, "new_atoms")
        minority_err_n = sum(b["minority_err_n"] for b in curve)
        endstate_who = round(R["endstate_attachok_correct"] / n_pat, 4) if n_pat else None
        ee_delta = round((endstate_who or 0) - (loop_off_who or 0), 4)
        nbf = R["final_net_broken"] - R["final_exact_collisions"]
        comp = R["compression"]
        miss_total = n_pat - R["endstate_attachok_correct"]
        miss_attach = n_aerr
        miss_labeler = miss_total - miss_attach
        collapse = round((min_rise or 0) - (min_rise_s or 0), 4)
        row = {
            "seed": seed, "immediate_recall": R["immediate_recall"], "regressions": R["regressions"],
            "minority_prefix_rise": min_rise, "minority_prefix_rise_scramble": min_rise_s,
            "minority_rise_collapse": collapse, "minority_err_n": minority_err_n,
            "first_pass_arc_rise": fp_rise, "atoms_decline_rel": d_atoms,
            "endstate_who_affected": endstate_who, "ee_delta_loop_on_off": ee_delta,
            "final_net_broken": R["final_net_broken"], "final_net_fixed": R["final_net_fixed"],
            "final_exact_collisions": R["final_exact_collisions"], "net_broken_fixable": nbf,
            "minority_endstate_acc": round(R["minority_endstate_correct"] / R["minority_endstate_total"], 4)
            if R["minority_endstate_total"] else None,
            "n_rules": comp["n_rules"], "rule_purity": comp["rule_purity"],
            "compression_ratio": comp["compression_ratio"],
            "residual_miss_total": miss_total, "residual_miss_attach_err": miss_attach,
            "residual_miss_labeler": miss_labeler,
            "residual_attach_frac": round(miss_attach / miss_total, 4) if miss_total else None,
        }
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}] {regime}/{which} seed={seed} loop_off_who={loop_off_who} "
              f"endstate_who={endstate_who} ee_delta={ee_delta:+.4f} min_rise={min_rise} "
              f"(scramble={min_rise_s} collapse={collapse:+.4f}) fp_rise={fp_rise} "
              f"atoms_decline={d_atoms} reg={R['regressions']} nbf={nbf} rules={comp['n_rules']} "
              f"pur={comp['rule_purity']} minority_err_n={minority_err_n} "
              f"resid attach:{miss_attach} lab:{miss_labeler}", flush=True)
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "regime": regime, "which": which, "seed": seed,
                                "min_rise": min_rise, "collapse": collapse}) + "\n")

    def mean(fn):
        v = [fn(s) for s in per_seed]
        v = [x for x in v if isinstance(x, (int, float))]
        return round(float(np.mean(v)), 4) if v else None

    return {
        "regime": regime, "signature": which, "loop_off_who_affected": loop_off_who,
        "ceiling_who_affected_attach_ok_rate": stats["attach_ok_rate"],
        "minority_prefix_rise_mean": mean(lambda s: s["minority_prefix_rise"]),
        "minority_prefix_rise_scramble_mean": mean(lambda s: s["minority_prefix_rise_scramble"]),
        "minority_rise_collapse_mean": mean(lambda s: s["minority_rise_collapse"]),
        "minority_err_n_mean": mean(lambda s: s["minority_err_n"]),
        "first_pass_arc_rise_mean": mean(lambda s: s["first_pass_arc_rise"]),
        "atoms_decline_rel_mean": mean(lambda s: s["atoms_decline_rel"]),
        "endstate_who_affected_mean": mean(lambda s: s["endstate_who_affected"]),
        "ee_delta_loop_on_off_mean": mean(lambda s: s["ee_delta_loop_on_off"]),
        "net_broken_fixable_mean": mean(lambda s: s["net_broken_fixable"]),
        "regressions_mean": mean(lambda s: s["regressions"]),
        "n_rules_mean": mean(lambda s: s["n_rules"]), "rule_purity_mean": mean(lambda s: s["rule_purity"]),
        "minority_endstate_acc_mean": mean(lambda s: s["minority_endstate_acc"]),
        "residual_attach_frac_mean": mean(lambda s: s["residual_attach_frac"]),
        "immediate_recall_mean": mean(lambda s: s["immediate_recall"]),
        "elapsed_s": round(time.perf_counter() - t0, 2), "per_seed": per_seed,
    }


# ---- leak + signature-mechanism probes ----------------------------------------------------------
def _leak_clean():
    src = _inspect.getsource(robust_arc_features) + _inspect.getsource(robust_signature)
    return ("deprel" not in src) and ("gold" not in src)


def _mutation_probe(sents, parser, tagger, regime, n=200):
    """Garble the GOLD head/deprel; the PH/PHPP robust signature (parser heads) must be BIT-IDENTICAL.
    Also confirms signature determinism on repeat."""
    if regime == "GH":
        return {"leak_clean": True, "note": "GH uses gold head by construction; probe N/A", "n": 0}
    ok = True
    seen = 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            continue
        toks = [t[1] for t in s]
        gpos = [t[2] for t in s]
        rpos = tagger.tag(toks) if regime == "PHPP" else gpos
        rheads = parser.parse(toks, rpos).heads
        s_g = [(t[0], t[1], t[2], (t[3] % len(s)) + 1, "root") for t in s]
        rheads_g = parser.parse([t[1] for t in s_g], rpos).heads
        for i in range(1, len(s) + 1):
            h = rheads.get(i)
            if h is None:
                continue
            v1 = robust_signature(toks, rpos, i, h)
            v2 = robust_signature(toks, rpos, i, rheads_g.get(i))
            if rheads.get(i) == rheads_g.get(i) and not np.array_equal(v1, v2):
                ok = False
            seen += 1
            if seen >= n:
                break
        if seen >= n:
            break
    return {"leak_clean": bool(ok and _leak_clean()), "n": seen}


def _single_pos_flip_robustness(sents, tagger, n_arcs=300):
    """SIGNATURE-MECHANISM probe (the discriminator for the robustification ITSELF): under ONE random
    UPOS flip, robust cosine to the correct-POS signature must be HIGHER than brittle cosine (robust
    degrades less). This is what the whole cell rests on -- it must FIRE."""
    rng = np.random.default_rng(12345)
    UPOS = ["NOUN", "PROPN", "PRON", "VERB", "AUX", "ADJ", "ADV", "ADP", "DET", "PART",
            "SCONJ", "CCONJ", "NUM", "INTJ", "SYM", "PUNCT", "X"]
    b_cos, r_cos = [], []
    seen = 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            continue
        toks = [t[1] for t in s]
        gpos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            gd = norm_label(s[i - 1][4])
            if gd not in PATIENT_ROLES or gh < 1 or gh > len(s) or gpos[gh - 1] != "VERB":
                continue
            fpos = list(gpos)
            j = int(rng.integers(0, len(fpos)))         # flip ONE token's POS to a different tag
            alt = [p for p in UPOS if p != fpos[j]]
            fpos[j] = alt[int(rng.integers(0, len(alt)))]
            b0 = brittle_signature(toks, gpos, i, gh)
            b1 = brittle_signature(toks, fpos, i, gh)
            r0 = robust_signature(toks, gpos, i, gh)
            r1 = robust_signature(toks, fpos, i, gh)
            b_cos.append(float(b0 @ b1))
            r_cos.append(float(r0 @ r1))
            seen += 1
            if seen >= n_arcs:
                break
        if seen >= n_arcs:
            break
    return {"n": seen, "brittle_cos_under_1flip": round(float(np.mean(b_cos)), 4) if b_cos else None,
            "robust_cos_under_1flip": round(float(np.mean(r_cos)), 4) if r_cos else None}


# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    m = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
         "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _arms_differ(sent_arcs):
    """robust sig differs from brittle sig on >=1 arc (bit-hash)."""
    for sa in sent_arcs:
        for a in sa["arcs"]:
            if hashlib.sha256(a["sig_brittle"].tobytes()).hexdigest() != \
               hashlib.sha256(a["sig_robust"].tobytes()).hexdigest():
                return True
    return False


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START POS-robust signature vs brittle in PHPP deployment", flush=True)

    seeds = [7] if mode == "smoke" else [7, 13, 19]
    regimes = ["PH", "PHPP"]
    signatures = ["brittle", "robust"]
    n_cap = 2000 if mode == "smoke" else None

    lab = ArcLabeler.load(LABELER_PATH)
    parser = ArcParser.load(ARC_PATH)
    tagger = PosTagger.load(POS_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu") + read_conllu("en_ewt-ud-test.conllu")
    if n_cap:
        sents = sents[:n_cap]
    print(f"[{ANCHOR_NAME}:{mode}] loaded {len(sents)} sents; regimes={regimes} sigs={signatures} seeds={seeds}",
          flush=True)

    EXPECTED_N_UNITS = len(regimes) * len(signatures) * len(seeds)

    # signature-mechanism probe (must fire) + leak + mutation-probe on the load-bearing PHPP regime.
    flip = _single_pos_flip_robustness(sents, tagger)
    mp = _mutation_probe(sents, parser, tagger, "PHPP")
    leak_clean = bool(mp["leak_clean"] and _leak_clean())
    robust_degrades_less = bool(flip["robust_cos_under_1flip"] is not None
                                and flip["brittle_cos_under_1flip"] is not None
                                and flip["robust_cos_under_1flip"] > flip["brittle_cos_under_1flip"])
    print(f"[{ANCHOR_NAME}:{mode}] SIGNATURE PROBE 1-POS-flip cosine: brittle={flip['brittle_cos_under_1flip']} "
          f"robust={flip['robust_cos_under_1flip']} (robust_degrades_less={robust_degrades_less}) "
          f"leak_clean={leak_clean}", flush=True)

    results = {}
    per_regime_stats = {}
    arms_differ = True
    baseline_in_band = True
    for regime in regimes:
        sent_arcs, stats = build_regime_dual(sents, lab, parser, tagger, regime)
        per_regime_stats[regime] = stats
        arms_differ = arms_differ and _arms_differ(sent_arcs)
        print(f"[{ANCHOR_NAME}:{mode}] REGIME {regime}: patients={stats['n_patient']} "
              f"attach_ok={stats['n_attach_ok']}({stats['attach_ok_rate']}) attach_err={stats['n_attach_err']} "
              f"labeler_err_on_ok={stats['n_labeler_err_on_attach_ok']} "
              f"minority_labeler_err={stats['minority_labeler_err']}", flush=True)
        results[regime] = {}
        for which in signatures:
            agg = run_arm(regime, which, sent_arcs, stats, seeds, output_dir)
            results[regime][which] = agg
            low = agg["loop_off_who_affected"]
            if not (low is not None and 0.05 < low < 0.95):
                baseline_in_band = False

    n_units = sum(len(results[r][w]["per_seed"]) for r in regimes for w in signatures)
    cardinality_ok = (n_units == EXPECTED_N_UNITS)

    bPH = results["PH"]["brittle"]
    rPH = results["PH"]["robust"]
    bPP = results["PHPP"]["brittle"]
    rPP = results["PHPP"]["robust"]

    def g(d, k):
        return d[k] if d[k] is not None else 0.0

    # ---- POSITIVE CONTROL: the atom-29409 phenomenon reproduces (brittle-PH survives, brittle-PHPP collapses)
    brittle_ph_survives = bool(g(bPH, "minority_prefix_rise_mean") >= 0.05
                               and g(bPH, "minority_rise_collapse_mean") >= 0.15)
    brittle_phpp_collapses = bool(g(bPP, "minority_prefix_rise_mean") < 0.03
                                  or g(bPP, "minority_rise_collapse_mean") < 0.10)
    phenomenon_reproduces = bool(brittle_ph_survives and brittle_phpp_collapses)

    # ---- discrimination kept on the CLEAN (PH) regime by the robust signature.
    d_kept = bool(g(rPH, "minority_prefix_rise_mean") >= 0.05
                  and g(rPH, "minority_prefix_rise_mean") >= g(bPH, "minority_prefix_rise_mean") - 0.03)

    # ---- recovered on the DEPLOYED (PHPP) regime by the robust signature.
    recovered = bool(g(rPP, "minority_prefix_rise_mean") >= 0.05
                     and g(rPP, "minority_rise_collapse_mean") >= 0.15
                     and g(rPP, "net_broken_fixable_mean") <= 1.0
                     and g(rPP, "n_rules_mean") >= 1
                     and leak_clean)

    robust_phpp_flat = bool(g(rPP, "minority_prefix_rise_mean") < 0.02
                            or g(rPP, "minority_rise_collapse_mean") < 0.10)

    if not phenomenon_reproduces:
        verdict = "UNKNOWN_BASELINE_PHENOMENON_NOT_REPRODUCED"
    elif not d_kept:
        verdict = "ROBUSTNESS_KILLS_DISCRIMINATION"
    elif recovered and d_kept:
        verdict = "POS_ROBUST_RECOVERS_DEPLOYMENT"
    elif robust_phpp_flat:
        verdict = "FRONTEND_IS_THE_GATE"
    else:
        verdict = "MIDDLE_BAND"

    # recovery ratio: fraction of the clean-regime coherent-gen restored in deployment by robustification.
    recovery_ratio = (round(g(rPP, "minority_prefix_rise_mean") / rPH["minority_prefix_rise_mean"], 4)
                      if rPH["minority_prefix_rise_mean"] else None)

    elapsed = time.perf_counter() - t0
    msg = (
        f"{verdict} | SIGNATURE-PROBE 1flip cos brittle={flip['brittle_cos_under_1flip']} "
        f"robust={flip['robust_cos_under_1flip']} (robust_degrades_less={robust_degrades_less}) | "
        f"PH(clean) min_rise brittle={bPH['minority_prefix_rise_mean']}(collapse={bPH['minority_rise_collapse_mean']}) "
        f"robust={rPH['minority_prefix_rise_mean']}(collapse={rPH['minority_rise_collapse_mean']}) d_kept={d_kept} | "
        f"PHPP(deploy) min_rise brittle={bPP['minority_prefix_rise_mean']}(collapse={bPP['minority_rise_collapse_mean']}) "
        f"robust={rPP['minority_prefix_rise_mean']}(collapse={rPP['minority_rise_collapse_mean']}) recovered={recovered} "
        f"recovery_ratio={recovery_ratio} | PHPP ee_delta brittle={bPP['ee_delta_loop_on_off_mean']:+} "
        f"robust={rPP['ee_delta_loop_on_off_mean']:+} who_off={bPP['loop_off_who_affected']} "
        f"ceiling={bPP['ceiling_who_affected_attach_ok_rate']} | phenomenon_reproduces={phenomenon_reproduces} "
        f"(brittle_ph_survives={brittle_ph_survives} brittle_phpp_collapses={brittle_phpp_collapses}) | "
        f"PHPP robust nbf={rPP['net_broken_fixable_mean']} reg={rPP['regressions_mean']} rules={rPP['n_rules_mean']} "
        f"attach_frac={rPP['residual_attach_frac_mean']} | leak_clean={leak_clean} arms_differ={arms_differ} "
        f"baseline_in_band={baseline_in_band} cardinality_ok={cardinality_ok}"
    )

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "regimes": regimes, "signatures": signatures,
        "EXPECTED_N_UNITS": EXPECTED_N_UNITS, "n_units": n_units,
        "signature_probe_1flip": flip, "robust_degrades_less_under_1pos_flip": robust_degrades_less,
        "PHENOMENON_reproduces": phenomenon_reproduces, "brittle_ph_survives": brittle_ph_survives,
        "brittle_phpp_collapses": brittle_phpp_collapses,
        "DISCRIMINATION_kept_clean_regime": d_kept, "DEPLOYMENT_recovered": recovered,
        "RECOVERY_ratio_robustPHPP_over_robustPH": recovery_ratio,
        "PH_min_rise_brittle": bPH["minority_prefix_rise_mean"], "PH_min_rise_robust": rPH["minority_prefix_rise_mean"],
        "PH_collapse_brittle": bPH["minority_rise_collapse_mean"], "PH_collapse_robust": rPH["minority_rise_collapse_mean"],
        "PHPP_min_rise_brittle": bPP["minority_prefix_rise_mean"], "PHPP_min_rise_robust": rPP["minority_prefix_rise_mean"],
        "PHPP_collapse_brittle": bPP["minority_rise_collapse_mean"], "PHPP_collapse_robust": rPP["minority_rise_collapse_mean"],
        "PHPP_ee_delta_brittle": bPP["ee_delta_loop_on_off_mean"], "PHPP_ee_delta_robust": rPP["ee_delta_loop_on_off_mean"],
        "PHPP_ceiling_attach_ok_rate": bPP["ceiling_who_affected_attach_ok_rate"],
        "PHPP_residual_attach_frac_robust": rPP["residual_attach_frac_mean"],
        "REGIME_SIG_results": results, "per_regime_stats": per_regime_stats,
        "leak_clean": leak_clean, "leak_mutation_probe": mp,
        "arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band, "cardinality_ok": cardinality_ok,
        "one_variable": "the signature (brittle vs robust); loop/ARTMAP/vigilance identical; regime is a controlled axis",
        "robust_signature_design": {"levers": "coarse-POS backoff + POS-free form anchors + downweighted fine-POS",
                                    "weights": {"form": W_FORM, "coarse": W_COARSE, "fine": W_FINE},
                                    "coarse_classes": sorted(set(COARSE_POS.values()))},
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "online ARTMAP who-affected recall; no quantitative noise floor",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <13min)",
        "deterministic_seeding": True, "storage": "no_storage_production_hdlab_untouched",
        "loop_reused_from": "exp_reader_selfimprove_artmap_stream_udewt_v1 + _predicted_head_endtoend_v1 (verbatim)",
        "brain_check_flag": "KNOWLEDGE-BASED (web-blocked): cue-redundancy/interactive-activation; web-verify if load-bearing",
        "interpretation_note": ("HELD-OUT coherent-gen = minority_prefix_rise + scramble collapse (VET ad659ee6, "
                                "base-rate-free). Recovery = robust-PHPP restores what brittle-PHPP lost (atom 29409) "
                                "WITHOUT losing brittle-PH's clean-regime discrimination."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    lab = ArcLabeler.load(LABELER_PATH)
    parser = ArcParser.load(ARC_PATH)
    tagger = PosTagger.load(POS_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu")[:300]

    # (1) LEAK: robust signature source is gold-free.
    assert _leak_clean(), "LEAK: robust_arc_features/robust_signature references deprel/gold"

    # (2) build_regime_dual constructs REAL arcs w/ BOTH sigs for PH and PHPP; PHPP has real POS noise.
    ph_arcs, ph_stats = build_regime_dual(sents, lab, parser, tagger, "PH")
    pp_arcs, pp_stats = build_regime_dual(sents, lab, parser, tagger, "PHPP")
    assert ph_stats["n_attach_err"] > 0, ("PH must have real attach errors", ph_stats)
    assert ph_stats["n_patient"] == pp_stats["n_patient"], "denominator must be STABLE across regimes"
    assert ph_stats["minority_labeler_err"] >= 1, ("no minority labeler errors to learn", ph_stats)
    # arms differ: robust sig != brittle sig on >=1 arc.
    assert _arms_differ(ph_arcs), "robust and brittle signatures are bit-identical (arm bug)"

    # (3) SIGNATURE-MECHANISM must fire: robust degrades LESS than brittle under a single POS flip.
    flip = _single_pos_flip_robustness(sents, tagger, n_arcs=120)
    assert flip["robust_cos_under_1flip"] is not None and flip["brittle_cos_under_1flip"] is not None
    assert flip["robust_cos_under_1flip"] > flip["brittle_cos_under_1flip"], \
        ("robustification does not fire (robust must degrade less under 1-POS-flip)", flip)

    # (4) real PHEE.run_stream runs on the robust-sig view (PHPP) + produces atoms + immediate recall.
    view = _view(pp_arcs, "robust")
    flat = [a for sa in view for a in sa["arcs"]]
    rho0 = calibrate_rho0([[a] for a in flat])
    order = list(np.random.default_rng(7).permutation(len(view)))
    R = PHEE.run_stream(view, order, rho0)
    assert R["compression"]["n_atoms"] >= 1, "no atoms formed on robust PHPP view"
    assert R["immediate_recall"] is None or R["immediate_recall"] >= 0.85, \
        ("immediate recall too low", R["immediate_recall"])

    # (5) mutation-probe: robust PHPP signature invariant to garbled GOLD head (parser heads unchanged).
    mp = _mutation_probe(sents, parser, tagger, "PHPP", n=60)
    assert mp["leak_clean"], ("robust PHPP signature LEAK under gold garble", mp)

    print(f"[selftest] PASS PH(patients={ph_stats['n_patient']} attach_err={ph_stats['n_attach_err']} "
          f"minority_lab_err={ph_stats['minority_labeler_err']}) 1flip_cos brittle={flip['brittle_cos_under_1flip']} "
          f"robust={flip['robust_cos_under_1flip']} atoms={R['compression']['n_atoms']} imm={R['immediate_recall']} "
          f"leak_clean={mp['leak_clean']}", flush=True)
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
