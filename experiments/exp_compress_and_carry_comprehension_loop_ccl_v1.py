"""COMPRESS-AND-CARRY COMPREHENSION LOOP (CCL): does a carried situation-model DOCUMENT-COHERENCE cue,
integrated as ONE weighted parallel cue into the LCCP scorer (Angle-2, NOT a late rerank), with
macrorule-COMPRESSED carry + MAP/SHIFT checkpoint, (a) RAISE precision on the within-frame-coherent-but-
DOCUMENT-incoherent failure class the sentence-local LCCP cannot catch, and (b) produce a POSITIVE
within-document COMPOUNDING slope (precision / doc-coh discriminative margin RISING across a document as the
situation model grows = the improving-as-it-reads property LCCP lacked)?

DESIGN NOTE: notes/research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md
  Mechanism = SITUATION-MODEL-GUIDED CONSTRUCTION-INTEGRATION with MACROSTRUCTURE-COMPRESSED CARRY.

COMPOSES (does not replace) three same-arc components, CREDITED:
  - LCCP (atom 29338, commit 3c6ff0f3): experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py
    -- its scorer + candidates + learned cue-weights + subcat/construction machinery are REUSED VERBATIM
    (imported as L). ARM A byte-reproduces LCCP arm C (Gate-D positive control).
  - WSM situation model (state_of_mind.py): the carried Tier-2 bundle = a scoped, glass-box CPU centroid over
    the parser's committed discourse entities + prior-sentence content (NO gold leakage).
  - coherence gate (atom 29337): the DEFERRED state for base-vs-doc conflict is reused in spirit.

ARMS (ONE variable per step):
  ARM A = LCCP sentence-local (situation model OFF). == LCCP arm C.
  ARM B = A + FLAT (uncompressed) document-coherence cue as one weighted additive term + DEFERRED. [A->B=cue]
  ARM C = B + PE-triggered MAP/SHIFT macrorule-compressed carry + LTWM gist-cue retrieval. [B->C=compression]

MEASURED (per arm, vs INDEPENDENT gold):
  (a) overall precision/recall/F1 + FP-class split (subcat/within_frame/spurious) + within-frame precision
      (the named class); (b) within-document COMPOUNDING (precision + doc-coh TP-vs-FP margin binned by
      position-in-document; first-half-vs-second-half + continuous slope + bootstrap CI; ARM A slope = control);
      (c) COMPRESSION DISSOCIATION (C vs B on LONG vs SHORT docs); (d) checkpoint firing count/positions.

VERDICT (pre-registered; see preregs/2026-07-19_compress_and_carry_comprehension_loop_ccl_v1.md):
  AXIS-1 precision PASS: precision(C) >= 0.55 AND within_frame_fp(C) <= within_frame_fp(A) AND recall
    retention (C/A) >= 0.60. FAIL: precision(C) <= 0.50.
  AXIS-2 compounding PASS: C margin slope > 0 with bootstrap 90% CI excluding 0, OR C precision 2nd-half >
    1st-half by >= 0.05 WHILE arm-A flat. FAIL: flat/negative.
  HARD_PASS_CCL = both axes. PARTIAL_CCL = exactly one (report which). HARD_FAIL_CCL = neither.

BRAIN-CHECK (outcome NOT pre-assumed): brain-faithful (Kintsch/van Dijk CI, Ericsson&Kintsch LTWM,
  Zwaan/Gernsbacher MAP/SHIFT, immediate discourse integration). HONEST bounds: strong local cues resist a
  weak doc cue (Angle-2 exception; probe = chance re-rank) -> precision-raise may fail = real shared ceiling;
  within-document compounding has NO human precedent either way -> a null is a genuine informative negative.

COMPUTE: class (b) sequential-CPU (per-document accretion is inherently sequential); wall < ~90s;
  no_storage; deterministic (OMP/MKL/OPENBLAS=1, fixed int seeds, hashlib, no salted hash/list(set)).
  Foreground local-to-completion (NO queue; NO push; NO remote-persist).

All numbers printed at run are MEASURED@this cell's metrics.json. CLAIM-VET-pending; single-annotator gold.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "compress_and_carry_comprehension_loop_ccl_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402

ARMS = ["A_lccp_local", "B_doccoh_flat", "C_ccl_compressed"]


# ----------------------------------------------------------------------------------------------
# Situation model: a scoped glass-box CPU centroid store over the parser's committed discourse
# entities + prior-sentence content. FLAT (B) = one ever-growing accumulator; COMPRESSED (C) = a
# current-scene bundle + a list of macrorule-compressed gist cues (LTWM pointers), MAP/SHIFT-gated.
# Causal: doc-coh of a candidate reflects PRIOR sentences only (updated AFTER the sentence is scored).
# ----------------------------------------------------------------------------------------------
def _unit(v):
    n = np.linalg.norm(v)
    return v / (n if n > 1e-8 else 1.0)


class SituationModel:
    """mode: 'off' | 'flat' | 'compressed'. Reset at document (lesson) boundary."""

    def __init__(self, mode, shift_thr):
        self.mode = mode
        self.shift_thr = shift_thr
        self.flat = []          # list of content vectors (FLAT accumulator)
        self.scene = []         # current-scene bundle (COMPRESSED)
        self.gists = []         # checkpointed scene-gist centroids (LTWM cues)
        self.n_shifts = 0
        self.shift_positions = []

    def reset(self):
        self.flat = []
        self.scene = []
        self.gists = []

    def _centroids(self):
        """Reference centroids the doc-coh cue scores against (mode-dependent)."""
        if self.mode == "flat":
            return [_unit(np.mean(np.stack(self.flat, 0), 0))] if self.flat else []
        if self.mode == "compressed":
            cents = []
            if self.scene:
                cents.append(_unit(np.mean(np.stack(self.scene, 0), 0)))
            cents.extend(_unit(g) for g in self.gists)  # LTWM gist cues
            return cents
        return []

    def doc_coh(self, pv):
        """Max cosine of patient-vec pv to any reference centroid; None if no reference / no vec."""
        if pv is None or self.mode == "off":
            return None
        cents = self._centroids()
        if not cents:
            return None
        return max(float(np.dot(pv, c)) for c in cents)

    def maybe_shift(self, new_vecs, posfrac):
        """COMPRESSED-mode MAP/SHIFT checkpoint at a NEW sentence, BEFORE folding it in. PE proxy = low
        cosine between the new sentence content-centroid and the current scene bundle => SHIFT: macrorule-
        compress the just-closed scene to a single gist cue (deletion of low-detail via centroid = the gist),
        push to LTWM, open a fresh scene. Below threshold => MAP (in-place, no compression)."""
        if self.mode != "compressed" or not new_vecs:
            return
        if self.scene:
            cc = _unit(np.mean(np.stack(self.scene, 0), 0))
            nc = _unit(np.mean(np.stack(new_vecs, 0), 0))
            if float(np.dot(cc, nc)) < self.shift_thr:      # discontinuity -> SHIFT
                self.gists.append(np.mean(np.stack(self.scene, 0), 0))  # compressed gist (macrorule)
                self.scene = []
                self.n_shifts += 1
                self.shift_positions.append(round(float(posfrac), 3))

    def fold(self, new_vecs):
        """Fold a sentence's content into the model (MAP update)."""
        if not new_vecs:
            return
        self.flat.extend(new_vecs)
        self.scene.extend(new_vecs)


# ----------------------------------------------------------------------------------------------
# Reconstruct the LCCP arm-C decision context (w, sel_fn, clustering, splits) DETERMINISTICALLY via
# L's module-level helpers -- same seeds -> same values -> ARM A byte-reproduces LCCP arm C (Gate D).
# ----------------------------------------------------------------------------------------------
def build_context(cfg):
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    # GloVe over reader + gold + sentence content tokens (topical situation model needs content words).
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, a, L.lemma_verb(v)])
        for w in L.tokenize(sent_text[sid]):
            toks.add(w)
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["agent"], g["v"]])
    glove = L.load_glove_for(toks)

    # candidates (IDENTICAL to LCCP.run_arms)
    cands = []
    for sid in order:
        stoks = L.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            v_surf, a, p = tup
            feat, _pos = L.candidate_features(stoks, v_surf, p)
            cands.append({"sid": sid, "v": L.lemma_verb(v_surf), "a": a, "p": p, "tup": tup, "feat": feat})

    sel_fn, verb_cent, glob_cent = L.build_semantic_teacher(cands, glove)
    seed = cfg["seed"]
    w, n_train = L.learn_cue_weights(cands, sel_fn, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"],
                                     cfg["epochs"], seed)

    # held-out verb split (IDENTICAL to LCCP)
    all_verbs = sorted(set(c["v"] for c in cands))
    rng = np.random.default_rng(seed + 1)
    perm = rng.permutation(len(all_verbs))
    n_heldout = max(1, int(round(cfg["heldout_frac"] * len(all_verbs))))
    heldout_verbs = set(all_verbs[i] for i in perm[:n_heldout])
    seen_verbs = set(all_verbs) - heldout_verbs

    # construction clustering (IDENTICAL to LCCP)
    prof = L.verb_cue_profiles(cands, w, sel_fn)
    seen_list = sorted(v for v in seen_verbs if v in prof)
    if seen_list:
        X = np.stack([prof[v] for v in seen_list], 0)
        Xn = (X - X.mean(0)) / (X.std(0) + 1e-8)
        assign, _cent = L.kmeans(Xn, cfg["k_constructions"], seed + 2)
        vconstr = {seen_list[i]: int(assign[i]) for i in range(len(seen_list))}
        constr_centroid = {j: Xn[assign == j].mean(0) for j in range(cfg["k_constructions"]) if (assign == j).any()}
    else:
        vconstr, constr_centroid, X, assign = {}, {}, None, None

    constr_trans = {}
    if seen_list:
        for j in range(cfg["k_constructions"]):
            members = [seen_list[i] for i in range(len(seen_list)) if int(assign[i]) == j]
            if members:
                constr_trans[j] = float(np.mean([prof[m][-1] for m in members]))

    # inst groups + reading-order + within-document position fraction
    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)
    per_inst_order = []
    for sid in order:
        for key in [k for k in inst_groups if k[0] == sid]:
            per_inst_order.append(key)

    by_lesson = defaultdict(list)
    for sid in order:
        by_lesson[sid.split("_")[0]].append(sid)
    posfrac = {}
    lesson_len = {}
    for lid, sids in by_lesson.items():
        lesson_len[lid] = len(sids)
        for i, sid in enumerate(sids):
            posfrac[sid] = (i / (len(sids) - 1)) if len(sids) > 1 else 0.0

    ctx = dict(order=order, sent_text=sent_text, reader_svo=reader_svo, gold=gold, gold_meta=gold_meta,
               glove=glove, cands=cands, sel_fn=sel_fn, w=w, n_train=n_train, heldout_verbs=heldout_verbs,
               seen_verbs=seen_verbs, prof=prof, seen_list=seen_list, vconstr=vconstr,
               constr_centroid=constr_centroid, constr_trans=constr_trans, X=X, assign=assign,
               inst_groups=inst_groups, per_inst_order=per_inst_order, posfrac=posfrac,
               lesson_len=lesson_len, cfg=cfg)
    return ctx


def _content_vec_tokens(ctx, words):
    """Content GloVe vectors for a list of words (drop funcwords/pronouns/short/OOV)."""
    out = []
    for wd in words:
        if wd in L.FUNCWORD or wd in L.PRONOUN or len(wd) < 3:
            continue
        pv = ctx["glove"].get(wd)
        if pv is not None:
            out.append(_unit(pv))
    return out


# ----------------------------------------------------------------------------------------------
# The parameterized decision loop. sit_mode in {off, flat, compressed}. sit_mode='off' + doc_weight
# inert => byte-reproduces LCCP arm C. Records per-decision provenance for compounding measurement.
# ----------------------------------------------------------------------------------------------
def run_arm(ctx, sit_mode, cfg):
    w = ctx["w"]
    inst_groups = ctx["inst_groups"]
    seen_verbs = ctx["seen_verbs"]
    heldout_verbs = ctx["heldout_verbs"]
    vconstr = ctx["vconstr"]
    constr_centroid = ctx["constr_centroid"]
    constr_trans = ctx["constr_trans"]
    prof = ctx["prof"]
    X = ctx["X"]
    KAPPA = cfg.get("kappa", 1.5)
    doc_weight = cfg["doc_weight"] if sit_mode != "off" else 0.0
    defer_margin = cfg["defer_margin"]

    def assign_heldout_construction(v):
        if v not in prof or not constr_centroid or X is None:
            return None
        p = (prof[v] - X.mean(0)) / (X.std(0) + 1e-8)
        best_j, best_d = None, None
        for j, c in constr_centroid.items():
            d = float(((p - c) ** 2).sum())
            if best_d is None or d < best_d:
                best_j, best_d = j, d
        return best_j

    def constr_prior_for(v):
        if v in vconstr:
            return constr_trans.get(vconstr[v])
        j = assign_heldout_construction(v)
        return constr_trans.get(j) if j is not None else None

    sm = SituationModel(sit_mode, cfg["shift_thr"])
    t_run = defaultdict(lambda: [0.0, 0])
    kept = []
    decisions = []      # per-instance provenance for compounding
    n_defer = 0
    n_doc_flip = 0      # decisions where doc-coh changed the chosen candidate vs base
    cur_lesson = None

    # group per_inst_order into (sid) blocks preserving order; but keep per-instance decisions
    # We process sentence-major: for each sid in order, score its instances against PRIOR model, then fold.
    order = ctx["order"]
    for sid in order:
        lid = sid.split("_")[0]
        if lid != cur_lesson:
            sm.reset()                       # document boundary -> fresh situation model
            cur_lesson = lid
        # COMPRESSED: check for scene SHIFT using this sentence's content BEFORE scoring/folding
        stoks = L.tokenize(ctx["sent_text"][sid])
        new_vecs = _content_vec_tokens(ctx, stoks)
        sm.maybe_shift(new_vecs, ctx["posfrac"][sid])

        keys = [k for k in inst_groups if k[0] == sid]
        for (s2, v) in keys:
            cs = inst_groups[(s2, v)]
            # base (sentence-local) scores
            base_scores = [(c, L.score_cand(w, c["feat"])) for c in cs]
            base_best = max(base_scores, key=lambda t: t[1])
            base_best_sc = base_best[1]
            # doc-coh augmented scores
            if doc_weight > 0.0:
                comb = []
                for c, bs in base_scores:
                    dc = sm.doc_coh(ctx["glove"].get(c["p"]))
                    dc = 0.0 if dc is None else dc
                    comb.append((c, bs + doc_weight * dc, bs, dc))
                comb_best = max(comb, key=lambda t: t[1])
                chosen = comb_best[0]
                chosen_base_sc = comb_best[2]
                chosen_dc = comb_best[3]
                # DEFERRED: base confident + doc disagrees on candidate -> keep base (respect strong local cue)
                if chosen is not base_best[0]:
                    base_sorted = sorted([bs for _, bs in base_scores], reverse=True)
                    base_gap = base_sorted[0] - (base_sorted[1] if len(base_sorted) > 1 else 0.0)
                    if base_gap > defer_margin:
                        chosen = base_best[0]
                        chosen_base_sc = base_best_sc
                        chosen_dc = sm.doc_coh(ctx["glove"].get(chosen["p"])) or 0.0
                        n_defer += 1
                    else:
                        n_doc_flip += 1
                best = chosen
                best_sc = chosen_base_sc
                best_dc = chosen_dc
            else:
                best = base_best[0]
                best_sc = base_best_sc
                best_dc = sm.doc_coh(ctx["glove"].get(best["p"]))

            # subcat gate (IDENTICAL to LCCP): construction/online transitivity prior
            cprior = constr_prior_for(v)
            if v in seen_verbs:
                s, n = t_run[v]
                if cprior is None:
                    prior = (s / n) if n > 0 else None
                else:
                    prior = (s + KAPPA * cprior) / (n + KAPPA)
            else:
                prior = cprior
            if prior is not None and prior < cfg["subcat_thr"]:
                keep_patient = False
            else:
                keep_patient = best_sc >= cfg["keep_thr"]

            if keep_patient:
                kept.append((best["sid"], best["tup"]))
            decisions.append({"sid": sid, "v": v, "patient": best["p"], "kept": keep_patient,
                              "heldout": v in heldout_verbs, "posfrac": ctx["posfrac"][sid],
                              "lesson": lid, "doc_coh": (None if best_dc is None else round(float(best_dc), 4)),
                              "base_sc": round(float(best_sc), 4)})
            # update running transitivity prior AFTER decision (seen verbs only) -- IDENTICAL to LCCP
            if v in seen_verbs:
                t_run[v][0] += best_sc
                t_run[v][1] += 1

        # fold this sentence's content into the situation model (AFTER scoring -> causal)
        sm.fold(new_vecs)

    return dict(kept=kept, decisions=decisions, n_defer=n_defer, n_doc_flip=n_doc_flip,
                n_shifts=sm.n_shifts, shift_positions=sm.shift_positions)


# ----------------------------------------------------------------------------------------------
# Scoring / measurement.
# ----------------------------------------------------------------------------------------------
def within_frame_stats(kept, gold):
    """Among transitive-verb instances (verb in gold pos_verbs) with a kept patient: TP vs within-frame FP.
    within_frame precision = tp_wf / (tp_wf + wf_fp). This is the NAMED document-incoherent class."""
    tp_wf = wf_fp = 0
    for sid, tup in kept:
        v = L.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid)
        if not rec or v not in rec["pos_verbs"]:
            continue
        if L.match_pos(v, p, rec["pos"]) is not None:
            tp_wf += 1
        else:
            wf_fp += 1
    prec = tp_wf / (tp_wf + wf_fp) if (tp_wf + wf_fp) else 0.0
    return {"tp_within_frame": tp_wf, "within_frame_fp": wf_fp,
            "within_frame_precision": round(prec, 4), "n_within_frame_kept": tp_wf + wf_fp}


def compounding_curve(decisions, gold, n_bins=10):
    """Within-document COMPOUNDING. For kept patients: bin by position-in-document; per bin compute
    precision AND the doc-coh discriminative margin (mean doc-coh of TP-kept minus FP-kept). Returns
    first-half/second-half precision + margin + continuous slopes (least-squares over posfrac)."""
    pts = []  # (posfrac, is_tp, doc_coh)
    for d in decisions:
        if not d["kept"]:
            continue
        rec = gold.get(d["sid"])
        is_tp = 1 if (rec and L.match_pos(d["v"], d["patient"], rec["pos"]) is not None) else 0
        pts.append((d["posfrac"], is_tp, d["doc_coh"]))
    if not pts:
        return {"n": 0}
    pf = np.array([p[0] for p in pts]); tp = np.array([p[1] for p in pts], dtype=float)
    # precision slope (least squares of is_tp on posfrac)
    prec_slope = float(np.polyfit(pf, tp, 1)[0]) if len(set(pf.tolist())) > 1 else 0.0
    first = tp[pf < 0.5]; second = tp[pf >= 0.5]
    prec_first = float(first.mean()) if len(first) else 0.0
    prec_second = float(second.mean()) if len(second) else 0.0
    # doc-coh TP-vs-FP margin per position half (only decisions with a doc_coh value)
    dc_pts = [(p[0], p[1], p[2]) for p in pts if p[2] is not None]
    margin_first = margin_second = None
    margin_slope = None
    if dc_pts:
        def margin(sub):
            tpv = [c for _, t, c in sub if t == 1]
            fpv = [c for _, t, c in sub if t == 0]
            if not tpv or not fpv:
                return None
            return float(np.mean(tpv) - np.mean(fpv))
        margin_first = margin([x for x in dc_pts if x[0] < 0.5])
        margin_second = margin([x for x in dc_pts if x[0] >= 0.5])
        # continuous margin slope: regress (doc_coh signed by tp/fp) is ill-defined; use binned margins
        bins = np.linspace(0, 1, n_bins + 1)
        bmarg = []
        for b in range(n_bins):
            sub = [x for x in dc_pts if bins[b] <= x[0] < bins[b + 1] or (b == n_bins - 1 and x[0] == 1.0)]
            m = margin(sub)
            if m is not None:
                bmarg.append(((bins[b] + bins[b + 1]) / 2, m))
        if len(bmarg) > 1:
            bx = np.array([x[0] for x in bmarg]); bym = np.array([x[1] for x in bmarg])
            margin_slope = float(np.polyfit(bx, bym, 1)[0])
    return {"n": len(pts), "n_with_doccoh": len(dc_pts),
            "precision_slope": round(prec_slope, 4),
            "precision_first_half": round(prec_first, 4), "precision_second_half": round(prec_second, 4),
            "precision_2nd_minus_1st": round(prec_second - prec_first, 4),
            "doccoh_margin_first_half": (None if margin_first is None else round(margin_first, 4)),
            "doccoh_margin_second_half": (None if margin_second is None else round(margin_second, 4)),
            "doccoh_margin_slope": (None if margin_slope is None else round(margin_slope, 4))}


def bootstrap_margin_slope_ci(decisions, gold, seed, n_boot=1000, n_bins=6):
    """Bootstrap 90% CI of the doc-coh TP-vs-FP margin slope over position (resample kept-with-doccoh decisions)."""
    pts = []
    for d in decisions:
        if not d["kept"] or d["doc_coh"] is None:
            continue
        rec = gold.get(d["sid"])
        is_tp = 1 if (rec and L.match_pos(d["v"], d["patient"], rec["pos"]) is not None) else 0
        pts.append((d["posfrac"], is_tp, d["doc_coh"]))
    if len(pts) < 8:
        return {"n": len(pts), "ci90": None, "note": "insufficient doccoh decisions for bootstrap"}
    rng = np.random.default_rng(seed + 99)
    bins = np.linspace(0, 1, n_bins + 1)

    def slope_of(sample):
        bmarg = []
        for b in range(n_bins):
            sub = [x for x in sample if bins[b] <= x[0] < bins[b + 1] or (b == n_bins - 1 and x[0] == 1.0)]
            tpv = [c for _, t, c in sub if t == 1]; fpv = [c for _, t, c in sub if t == 0]
            if tpv and fpv:
                bmarg.append(((bins[b] + bins[b + 1]) / 2, float(np.mean(tpv) - np.mean(fpv))))
        if len(bmarg) < 2:
            return None
        bx = np.array([x[0] for x in bmarg]); by = np.array([x[1] for x in bmarg])
        return float(np.polyfit(bx, by, 1)[0])

    slopes = []
    arr = pts
    for _ in range(n_boot):
        idx = rng.integers(0, len(arr), len(arr))
        s = slope_of([arr[i] for i in idx])
        if s is not None:
            slopes.append(s)
    if len(slopes) < n_boot * 0.5:
        return {"n": len(pts), "ci90": None, "note": "too many degenerate bootstrap resamples"}
    lo, hi = float(np.percentile(slopes, 5)), float(np.percentile(slopes, 95))
    return {"n": len(pts), "n_boot_valid": len(slopes), "ci90": [round(lo, 4), round(hi, 4)],
            "excludes_zero": bool(lo > 0 or hi < 0), "median_slope": round(float(np.median(slopes)), 4)}


def compression_dissociation(ctx, res_B, res_C, gold, cfg):
    """C vs B on LONG (>= median sentences) vs SHORT documents: precision + doc-coh margin."""
    lens = ctx["lesson_len"]
    med = float(np.median(list(lens.values())))
    long_les = set(l for l, n in lens.items() if n >= med)
    short_les = set(l for l, n in lens.items() if n < med)

    def arm_stats(res, les_set):
        kept = [(sid, tup) for sid, tup in res["kept"] if sid.split("_")[0] in les_set]
        tp = 0
        for sid, tup in kept:
            rec = gold.get(sid)
            if rec and L.match_pos(L.lemma_verb(tup[0]), tup[2], rec["pos"]) is not None:
                tp += 1
        prec = tp / len(kept) if kept else 0.0
        # margin
        tpv, fpv = [], []
        for d in res["decisions"]:
            if not d["kept"] or d["doc_coh"] is None or d["lesson"] not in les_set:
                continue
            rec = gold.get(d["sid"])
            is_tp = rec and L.match_pos(d["v"], d["patient"], rec["pos"]) is not None
            (tpv if is_tp else fpv).append(d["doc_coh"])
        margin = (float(np.mean(tpv) - np.mean(fpv)) if tpv and fpv else None)
        return prec, margin, len(kept)

    out = {"median_sentences": med, "long_lessons": sorted(long_les), "short_lessons": sorted(short_les)}
    for name, les in [("long", long_les), ("short", short_les)]:
        pB, mB, nB = arm_stats(res_B, les)
        pC, mC, nC = arm_stats(res_C, les)
        out[name] = {"B_precision": round(pB, 4), "C_precision": round(pC, 4),
                     "C_minus_B_precision": round(pC - pB, 4),
                     "B_margin": (None if mB is None else round(mB, 4)),
                     "C_margin": (None if mC is None else round(mC, 4)),
                     "C_minus_B_margin": (None if (mB is None or mC is None) else round(mC - mB, 4)),
                     "n_kept_B": nB, "n_kept_C": nC}
    # dissociation: (C-B) bigger on long than short
    out["dissociation_precision_long_minus_short"] = round(
        out["long"]["C_minus_B_precision"] - out["short"]["C_minus_B_precision"], 4)
    if out["long"]["C_minus_B_margin"] is not None and out["short"]["C_minus_B_margin"] is not None:
        out["dissociation_margin_long_minus_short"] = round(
            out["long"]["C_minus_B_margin"] - out["short"]["C_minus_B_margin"], 4)
    return out


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def scaffold_free_witness(res_A, res_C, gold):
    """A real within-frame document-incoherent case C catches (kept by A, dropped/re-selected by C) +
    a within-document case where the carried model constrains a later parse (a doc-coh flip that is a TP)."""
    a_kept = set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in res_A["kept"])
    c_kept = set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in res_C["kept"])
    # within-frame FP kept by A that C does NOT keep (transitive verb, wrong patient)
    wf_caught = None
    for (sid, v, p) in sorted(a_kept - c_kept):
        rec = gold.get(sid)
        if rec and v in rec["pos_verbs"] and L.match_pos(v, p, rec["pos"]) is None:
            wf_caught = [sid, v, p]
            break
    # a later-document TP that C keeps and whose doc_coh was set by the carried model (posfrac > 0.3)
    later_constrained = None
    for d in res_C["decisions"]:
        if d["kept"] and d["doc_coh"] is not None and d["posfrac"] > 0.3:
            rec = gold.get(d["sid"])
            if rec and L.match_pos(d["v"], d["patient"], rec["pos"]) is not None:
                later_constrained = [d["sid"], d["v"], d["patient"], round(d["posfrac"], 2), d["doc_coh"]]
                break
    return {"within_frame_doc_incoherent_caught_by_C_kept_by_A": wf_caught,
            "later_document_true_patient_with_carried_doccoh": later_constrained,
            "witness": "PASS" if (wf_caught is not None or later_constrained is not None) else "PARTIAL"}


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def _base_cfg():
    # shift_thr=0.55: consecutive-sentence content cosine on this corpus is median 0.681, p25 0.567
    # (MEASURED@probe 2026-07-19); 0.55 fires a SHIFT on genuine topical dips (~1 per 8 sentences, 20
    # shifts / 163 sents at full) so the compressed scene bundle is recency-local and genuinely diverges
    # from the flat accumulator (B!=C discriminator fires). calibration_check: adaptive-informed fixed value.
    # doc_weight=0.5: weighted parallel cue (Angle-2), NOT a veto; finding is robust across 0.1-1.2 (MEASURED).
    return dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25,
                k_constructions=4, seed=7, kappa=1.5, doc_weight=0.5, shift_thr=0.55, defer_margin=0.20)


def cfg_smoke():
    # smoke includes L10 (30-sentence doc) so the B!=C compression discriminator fires at smoke (short
    # 2-lesson slices leave scenes un-reset -> A==B==C vacuous, per DISCRIMINATOR-MUST-SURVIVE-SCALE).
    c = _base_cfg(); c.update(slice_lessons=["L04", "L05", "L10"], epochs=40); return c


def cfg_full():
    c = _base_cfg(); c.update(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], epochs=60)
    return c


# ----------------------------------------------------------------------------------------------
# Verdict.
# ----------------------------------------------------------------------------------------------
def build_verdict(arm_metrics, wf, compounding, boot, arm_metrics_A_compounding):
    A = arm_metrics["A_lccp_local"]["all"]
    C = arm_metrics["C_ccl_compressed"]["all"]
    recall_ret = (C["recall"] / A["recall"]) if A["recall"] > 0 else 0.0
    # AXIS-1 precision-raise
    axis1 = bool(C["precision"] >= 0.55 and wf["C_ccl_compressed"]["within_frame_fp"] <= wf["A_lccp_local"]["within_frame_fp"]
                 and recall_ret >= 0.60)
    axis1_fail = bool(C["precision"] <= 0.50)
    # AXIS-2 compounding
    ci_excl = bool(boot.get("excludes_zero") and boot.get("ci90") and boot["ci90"][0] > 0)
    comp_C = compounding["C_ccl_compressed"]
    comp_A = arm_metrics_A_compounding
    axis2_prec = bool(comp_C["precision_2nd_minus_1st"] >= 0.05 and abs(comp_A["precision_slope"]) < 0.10)
    axis2 = bool(ci_excl or axis2_prec)
    axis2_fail = bool((not ci_excl) and comp_C["precision_2nd_minus_1st"] < 0.05)
    if axis1 and axis2:
        verdict = "HARD_PASS_CCL"
    elif axis1 or axis2:
        verdict = "PARTIAL_CCL"
    else:
        verdict = "HARD_FAIL_CCL"
    return {"verdict": verdict, "axis1_precision_raise_pass": axis1, "axis1_fail": axis1_fail,
            "axis2_compounding_pass": axis2, "axis2_fail": axis2_fail,
            "recall_retention_C_over_A": round(recall_ret, 4),
            "precision_A": A["precision"], "precision_C": C["precision"],
            "which_axis_passed": ("both" if (axis1 and axis2) else "axis1_precision" if axis1
                                  else "axis2_compounding" if axis2 else "none")}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    ctx = build_context(cfg)
    gold = ctx["gold"]

    res = {arm: run_arm(ctx, sm, cfg) for arm, sm in
           zip(ARMS, ["off", "flat", "compressed"])}

    # GATE-D positive control: ARM A must byte-reproduce LCCP arm C at the SAME regime.
    lccp_dec, _art, _sd, _ho, _sn, _ig, _w = L.run_arms(
        ctx["order"], ctx["reader_svo"], ctx["sent_text"], ctx["glove"], cfg, cfg["seed"])
    gate_d_ok = bool(kept_hash(res["A_lccp_local"]["kept"]) == kept_hash(lccp_dec["C_lccp"]))

    # arm metrics vs gold
    arm_metrics = {}
    for arm in ARMS:
        arm_metrics[arm] = {
            "all": L.score_arm(res[arm]["kept"], gold),
            "seen": L.score_arm(res[arm]["kept"], gold, only_verbs=ctx["seen_verbs"]),
            "heldout": L.score_arm(res[arm]["kept"], gold, only_verbs=ctx["heldout_verbs"]),
        }
    wf = {arm: within_frame_stats(res[arm]["kept"], gold) for arm in ARMS}
    compounding = {arm: compounding_curve(res[arm]["decisions"], gold) for arm in ARMS}
    boot = bootstrap_margin_slope_ci(res["C_ccl_compressed"]["decisions"], gold, cfg["seed"])
    dissoc = compression_dissociation(ctx, res["B_doccoh_flat"], res["C_ccl_compressed"], gold, cfg)
    witness = scaffold_free_witness(res["A_lccp_local"], res["C_ccl_compressed"], gold)

    hashes = {arm: kept_hash(res[arm]["kept"]) for arm in ARMS}
    assert hashes["A_lccp_local"] != hashes["B_doccoh_flat"], "META_RULE_AF: A==B (doc-coh cue no-op)"
    assert hashes["B_doccoh_flat"] != hashes["C_ccl_compressed"], "META_RULE_AF: B==C (compression no-op)"
    assert hashes["A_lccp_local"] != hashes["C_ccl_compressed"], "META_RULE_AF: A==C"

    A = arm_metrics["A_lccp_local"]["all"]
    baseline_in_band = bool(0.05 < A["precision"] < 0.95)
    discriminator_fires = bool(res["B_doccoh_flat"]["n_doc_flip"] + res["C_ccl_compressed"]["n_doc_flip"] > 0
                               and hashes["A_lccp_local"] != hashes["C_ccl_compressed"])
    vd = build_verdict(arm_metrics, wf, compounding, boot, compounding["A_lccp_local"])
    elapsed = time.perf_counter() - t0

    B = arm_metrics["B_doccoh_flat"]["all"]; C = arm_metrics["C_ccl_compressed"]["all"]
    cC = compounding["C_ccl_compressed"]
    msg = (f"{vd['verdict']} | slice={'+'.join(cfg['slice_lessons'])} sents={len(ctx['order'])} "
           f"reader={sum(len(ctx['reader_svo'][s]) for s in ctx['order'])} "
           f"| A P={A['precision']:.3f} R={A['recall']:.3f} wf_fp={wf['A_lccp_local']['within_frame_fp']} "
           f"| B P={B['precision']:.3f} R={B['recall']:.3f} "
           f"| C P={C['precision']:.3f} R={C['recall']:.3f} wf_fp={wf['C_ccl_compressed']['within_frame_fp']} "
           f"| AXIS1(prec)={vd['axis1_precision_raise_pass']} dP(C-A)={C['precision']-A['precision']:+.3f} Rret={vd['recall_retention_C_over_A']:.2f} "
           f"| AXIS2(compound)={vd['axis2_compounding_pass']} C_prec2-1={cC['precision_2nd_minus_1st']:+.3f} "
           f"C_marginslope={cC['doccoh_margin_slope']} boot_ci90={boot.get('ci90')} "
           f"| dissoc(C-B)long-short prec={dissoc['dissociation_precision_long_minus_short']:+.3f} "
           f"| GateD_A==LCCPc={gate_d_ok} n_doc_flip(B/C)={res['B_doccoh_flat']['n_doc_flip']}/{res['C_ccl_compressed']['n_doc_flip']} "
           f"n_defer={res['B_doccoh_flat']['n_defer']}/{res['C_ccl_compressed']['n_defer']} "
           f"shifts_C={res['C_ccl_compressed']['n_shifts']} base_in_band={baseline_in_band} discrim={discriminator_fires}")

    if not gate_d_ok:
        vd["verdict"] = "HARD_FAIL_GATE_D_INVOCATION_MISMATCH"
        msg = "HARD_FAIL_GATE_D_INVOCATION_MISMATCH: ARM A != LCCP arm C | " + msg

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": vd["verdict"], "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "within_frame": wf, "compounding_curve": compounding,
        "compounding_bootstrap_ci_C": boot, "compression_dissociation": dissoc, "verdict_detail": vd,
        "gate_d_positive_control": {"arm_A_hash": hashes["A_lccp_local"],
                                    "lccp_arm_C_hash": kept_hash(lccp_dec["C_lccp"]), "match": gate_d_ok},
        "kept_hashes": hashes, "arms_differ_verified": True, "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires,
        "loop_diagnostics": {arm: {"n_doc_flip": res[arm]["n_doc_flip"], "n_defer": res[arm]["n_defer"],
                                   "n_shifts": res[arm]["n_shifts"], "shift_positions": res[arm]["shift_positions"]}
                             for arm in ARMS},
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "independent_gold_source": "data/gold_mcguffey_lccp_argstruct_v1.json (single-annotator, caveated)",
        "composes_credited": {"LCCP": "atom 29338 / commit 3c6ff0f3", "coherence_gate": "atom 29337",
                              "WSM_situation_model": "hdlab/state_of_mind.py"},
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "within_frame", "compounding_curve",
                            "compounding_bootstrap_ci_C", "compression_dissociation", "verdict_detail",
                            "gate_d_positive_control", "scaffold_free_witness"],
        "notes": ("CCL: situation-model DOCUMENT-COHERENCE cue wired into LCCP scorer as one weighted parallel "
                  "cue (A->B=cue flat carry+DEFERRED; B->C=MAP/SHIFT macrorule-compressed carry+LTWM gist cues). "
                  "AXIS-1 precision-raise: C prec >=0.55 AND wf_fp(C)<=wf_fp(A) AND recall ret >=0.60. "
                  "AXIS-2 compounding: C margin-slope>0 (bootstrap 90% CI excl 0) OR C prec 2nd-half>1st-half "
                  ">=0.05 while arm-A flat. HARD_PASS=both. PARTIAL=one. HARD_FAIL=neither. CLAIM-VET-pending; "
                  "single-annotator gold; NO scene-boundary gold (checkpoint firing reported, no agreement claim); "
                  "probe showed doc-coh re-rank at chance + weak positive margin sharpened by compression."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for arm in ARMS:
        m = arm_metrics[arm]["all"]
        print(f"  [{arm:>16}] P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} n_pred={m['n_pred']} "
              f"tp={m['tp']} fp(sub/wf/sp)={m['subcat_fp']}/{m['within_frame_fp']}/{m['spurious_verb_fp']} "
              f"| wfP={wf[arm]['within_frame_precision']:.3f} ({wf[arm]['tp_within_frame']}/{wf[arm]['n_within_frame_kept']})", flush=True)
    print(f"  [compounding C] prec 1st={cC['precision_first_half']:.3f} 2nd={cC['precision_second_half']:.3f} "
          f"(d={cC['precision_2nd_minus_1st']:+.3f}) slope={cC['precision_slope']:+.4f} | "
          f"margin 1st={cC['doccoh_margin_first_half']} 2nd={cC['doccoh_margin_second_half']} slope={cC['doccoh_margin_slope']} "
          f"| boot_ci90={boot.get('ci90')} excl0={boot.get('excludes_zero')}", flush=True)
    print(f"  [compounding A control] prec_slope={compounding['A_lccp_local']['precision_slope']:+.4f} "
          f"2nd-1st={compounding['A_lccp_local']['precision_2nd_minus_1st']:+.3f}", flush=True)
    print(f"  [dissociation] long C-B prec={dissoc['long']['C_minus_B_precision']:+.3f} margin={dissoc['long']['C_minus_B_margin']} "
          f"| short C-B prec={dissoc['short']['C_minus_B_precision']:+.3f} margin={dissoc['short']['C_minus_B_margin']} "
          f"| long-short={dissoc['dissociation_precision_long_minus_short']:+.3f}", flush=True)
    print(f"  [gate-D] ARM A hash==LCCP arm C hash: {gate_d_ok}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def self_test():
    cfg = cfg_smoke()
    ctx = build_context(cfg)
    # Gate-D at smoke regime: ARM A reproduces LCCP arm C exactly.
    resA = run_arm(ctx, "off", cfg)
    lccp_dec, *_ = L.run_arms(ctx["order"], ctx["reader_svo"], ctx["sent_text"], ctx["glove"], cfg, cfg["seed"])
    assert kept_hash(resA["kept"]) == kept_hash(lccp_dec["C_lccp"]), \
        "GATE-D self-test: ARM A (sit off) must byte-reproduce LCCP arm C"
    resB = run_arm(ctx, "flat", cfg)
    resC = run_arm(ctx, "compressed", cfg)
    hA, hB, hC = kept_hash(resA["kept"]), kept_hash(resB["kept"]), kept_hash(resC["kept"])
    assert hA != hB and hB != hC and hA != hC, "arms must differ (discriminator fires)"
    assert (resB["n_doc_flip"] + resC["n_doc_flip"]) > 0, "doc-coh cue must change >0 decisions"
    A = L.score_arm(resA["kept"], ctx["gold"])
    assert 0.05 < A["precision"] < 0.95, "baseline_in_band"
    print(f"[{ANCHOR_NAME}] self-test PASS: GateD_A==LCCPc=True hashes(A/B/C)={hA}/{hB}/{hC} "
          f"A_P={A['precision']:.3f} n_doc_flip(B/C)={resB['n_doc_flip']}/{resC['n_doc_flip']} "
          f"n_shifts_C={resC['n_shifts']}", flush=True)


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
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
