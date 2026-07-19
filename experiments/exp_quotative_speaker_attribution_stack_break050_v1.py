"""QUOTATIVE SPEAKER-ATTRIBUTION lever + the honest STACK re-measure: does a glass-box quotative-frame
classifier SUPPRESS the dominant residual class (person-fillers mis-attached as PATIENT on report verbs --
'said papa', 'told james/son/charles/him') that LCCP arm-C still licenses, WITHOUT hurting true patients,
measured on the TRUE stacked baseline (LCCP + categorial arg/adjunct) rather than vs LCCP-alone?

QUESTION (the VET-localized DOMINANT break-0.50 residual, per the arg/adjunct cell 868b02fd2 + VET a6f6efd7):
  LCCP arm-C (patient precision 0.50 vs independent gold) mis-licenses PERSON fillers on REPORT verbs as the
  PATIENT. These are QUOTATIVE speech participants -- the SPEAKER (inversion 'said papa' -> papa=speaker) or
  the ADDRESSEE ('told his son that ...' -> son=addressee) -- never a direct patient. This is the SINGLE
  BIGGEST residual class (7+ FPs per the arg/adjunct VET). The earlier coref-integration (405dfe6f3,
  HARD_FAIL) failed because the residual heads were lost UPSTREAM at candidate generation; the NP-head-finder
  (29342 / commit f98c49525, HARD_PASS) FIXED candidate-gen so the correct post-verbal speech-agent head is
  now proposed -- the quotative frame can NOW resolve the speaker at the right layer.

THE STACK (methodological bookkeeping fix -- report the TRUE stacked precision, DO NOT conflate levers):
  ARM A = LCCP arm-C alone (the original 0.500 patient-precision baseline; still licenses say/papa).
  ARM S = A + categorial arg/adjunct suppression (the arg/adjunct cell's B1 cascade; the honest POST-
    structural-fixes baseline the quotative lever should build on). On the PATIENT lens the NP-head-finder is
    a DECLARED no-op (it rewrites AGENT heads; the patient-precision scorer keys on (v_lemma, patient), agent
    not in the key) -- its stacked contribution lives on the AGENT lens (reported separately + CITED HARD_PASS
    f98c49525), and is EXERCISED on the exact quotative agent-attribution below.
  ARM Q = S + QUOTATIVE speaker-attribution: for a kept patient whose verb is a REPORT verb AND whose filler
    is a PERSON AND the clause carries a QUOTATIVE FRAME (inversion-quote 'said X' OR a reported clausal
    complement after the filler 'told X that/to ...'), SUPPRESS the filler as patient (it is a speech
    participant: SPEAKER via inversion or ADDRESSEE via report) and CLASSIFY its discourse role.

THE PRECISION PROTECTORS (the can-fail gates; analogous to the arg/adjunct bare-form guard):
  (1) REPORT-verb closed class (say/tell/cry/exclaim/ask/answer/retort/speak/call/reply/... ) -- EXCLUDES
      TRANSFER communication verbs (thank/teach/show/invite/give/send) that take a genuine PERSON patient
      ('mother thanked the man'). A naive WordNet verb.communication gate OVER-FIRES onto these (measured by
      the Q_broad_control arm -- reported, NOT the verdict arm; the head-finder's B2_hardveto analog).
  (2) QUOTATIVE-FRAME requirement -- a report verb with a person filler but NO quote and NO reported clause
      (predicate nominal 'are called trappers', plain ditransitive 'told him the name') is NOT quotative ->
      KEPT (tightly scoped to the quotative frame, not all ditransitive recipients).

MEASURED (decisive, per arm, vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json):
  PATIENT LENS (primary; the 0.50 wall): precision/recall/F1 + FP class split A vs S vs Q; the QUOTATIVE-
    TARGET RESIDUAL (arm-S FPs that ARE report-verb+person+frame) and the fraction Q suppresses; the
    TRANSITIVE-RECALL RETENTION (true patients each arm keeps -- must be zero cost); the S->Q isolated
    contribution; the TRUE stacked residual re-classification (what dominates AFTER all structural fixes).
  AGENT LENS (secondary; the head-finder-unlock witness / 'coref-at-the-right-layer'): for each suppressed
    quotative case, the discourse ROLE (SPEAKER via inversion / ADDRESSEE via report) + whether the resolved
    agent matches gold -- INVERSION speaker resolved ('said papa' -> papa == gold agent) vs ADDRESSEE agent
    preserved (reader agent already correct, NOT wrongly re-assigned to the addressee).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baselines = LIVE LCCP arm-C recompute (P~0.500) AND ARM S (A + categorial; the honest stacked
       baseline, reported not conflated). Both reproduced, not cited.
  (G2) baseline_in_band: 0.05 < P_A < 0.95 AND 0.05 < P_S < 0.95 (real, un-saturated wall).
  (G3) CAN-FAIL-BOTH-WAYS: HARD_PASS (Q suppresses >=50% of the quotative-target residual AND recall cost
       <=0.05 AND precision_Q >= precision_S = the coref-at-the-right-layer works NOW that candidate-gen is
       fixed) OR HARD_FAIL (recall cost >0.10 = the report-verb/frame gate over-fires onto true patients, the
       precision protector failed; OR <15% of the target suppressed = residual NOT frame-separable, lost
       deeper -- gold-granularity / LCCP split-sentence) OR MIDDLE_BAND_PARTIAL in between.
  (G4) discriminator fires: Q suppresses >0 arm-S patients AND kept sets differ across A/S/Q.
  (G5) ONE VARIABLE: S->Q = the quotative lever ONLY (the categorial cascade held IDENTICAL A->S).

VERDICT BANDS (pre-registered):
  quot_reduction_frac = |Q suppressed among quotative-target residual| / |quotative-target residual|
  recall_cost_S_to_Q  = recall_S - recall_Q  (patient-level, gold-pos)
  residual_share       = |quotative-target residual| / total_FP_S  (how much of the wall is quotative)
  HARD_PASS_QUOTATIVE_BREAKS_050: quot_reduction_frac >= 0.50 AND recall_cost_S_to_Q <= 0.05 AND
    precision_Q >= precision_S. (quotative frame cleanly separates speech-participant from patient at the
    RIGHT layer, zero recall cost -- the coref-integration the head-finder unlocked.)
  HARD_FAIL_QUOTATIVE_BITES: recall_cost_S_to_Q > 0.10 (gate over-prunes TRUE patients -- protector failed)
    OR quot_reduction_frac < 0.15 (residual NOT frame-separable; heads lost deeper / gold granularity).
  MIDDLE_BAND_PARTIAL: in between.
  SCOPE TAG (independent magnitude honesty): MATERIAL_SHARE if residual_share >= 0.15 (quotative is the
    DOMINANT single structural residual class, per the arg/adjunct VET claim); LOW_CEILING_CORPUS_SPARSE
    otherwise.
  AGENT-LENS TAG: HEADFINDER_UNLOCKS_QUOTATIVE if n_inversion>0 AND all inversion speakers resolve to gold
    agent AND all addressee agents preserved; GOLD_GRANULARITY_OR_SPLIT_BOUND if an inversion speaker mis-
    resolves or an addressee agent is wrongly re-assigned (the deeper localization the earlier coref hit).

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): quotative speaker-attribution (said X -> X=agent;
  a report verb frames a discourse-participant not a patient) is brain-faithful -- discourse-participant
  tracking / deixis anchoring (state_of_mind.py note_turn/speaker, atom 29326). The question is whether
  fixing candidate-gen (the head-finder proposes the correct post-verbal head) UNLOCKS the quotative
  resolution that the earlier coref-integration could not reach (HARD_FAIL 405dfe6f3, heads lost upstream),
  OR whether the residual is gold-granularity-bound (gold speakers as bare pronouns 'he' vs resolved names)
  / LCCP-split-sentence mis-resolve -- a same-limit the brain also faces at low bandwidth. brain-does-it =
  the fix works now (partial or full); same-limit = accept + localize deeper.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- one live LCCP arm-C recompute
  (~30-60s) + the arg/adjunct categorial cascade + a glass-box quotative-frame check (tokenize + report-verb
  membership + WordNet person typing + reported-clause / inversion-quote detection) over ~114 sentences;
  wall < ~90s. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage
  (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds (LCCP's), deterministic
  hashlib + deterministic WordNet synset order; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (A vs S vs Q kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < P_A < 0.95 AND 0.05 < P_S < 0.95)
- discriminator fires at smoke (Q suppresses >0; kept sets differ)
- scaffold-free witness: a REAL 'said papa' the quotative frame suppresses as patient AND resolves as
  SPEAKER=papa matching gold (that LCCP-alone licensed); a true patient 'thank the man' the report-verb
  class KEEPS (protector); a plain 'called trappers' the frame requirement KEEPS (tight scope)
- deterministic seeding; numbers tagged MEASURED@ (printed at run) / CITED@ (0.50 LCCP arm-C atom 29338;
  head-finder HARD_PASS commit f98c49525 / atom 29342)
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402
import experiments.exp_arg_adjunct_role_eligibility_categorial_break050_v1 as ARG  # noqa: E402

ANCHOR_NAME = "quotative_speaker_attribution_stack_break050_v1"
CITED_LCCP_ARMC_PRECISION = 0.50   # CITED@ atom 29338 / LCCP arm-C independent-gold patient precision
CITED_HEADFINDER = "HARD_PASS candidate-gen NP-head-finder, commit f98c49525 / atom 29342"
ARMS = ["A_lccp_armC", "S_stacked_categorial", "Q_quotative"]

# ---- WordNet grounded typing (person filler; report-verb sanity; broad-control communication class).
_WN = None
_WN_OK = False
_WN_ERR = None
try:
    from nltk.corpus import wordnet as _wnmod
    _ = _wnmod.synsets("table")  # force-load; raises if corpus absent
    _WN = _wnmod
    _WN_OK = True
except Exception as _e:  # NOT BaseException; explicit, non-silent (flagged in metrics)
    _WN_ERR = f"{type(_e).__name__}: {str(_e)[:200]}"

# REPORT verbs: a principled closed lexical class of speech/report verbs that frame a reported turn (direct
# or indirect speech). The filler person is a SPEAKER (inversion) or ADDRESSEE (report), never a patient.
# This DELIBERATELY EXCLUDES transfer/benefactive communication verbs (thank/teach/show/invite/give/send/
# promise/offer) that take a genuine person PATIENT -- that exclusion is the recall protector.
REPORT_VERBS = {"say", "tell", "cry", "exclaim", "ask", "answer", "reply", "retort", "speak", "call",
                "shout", "whisper", "mutter", "declare", "remark", "observe", "respond", "inquire",
                "venture", "add", "continue", "repeat", "begin"}
# Transfer/benefactive communication verbs that DO take a person patient -- explicitly NOT report verbs.
TRANSFER_COMM = {"thank", "teach", "show", "invite", "give", "send", "promise", "offer", "pay", "bring"}
# Animate personal pronouns (a nominal, speech-participant-eligible closed class).
ANIMATE_PRON = {"i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them"}
# Clause / reported-complement starters (a complementizer or a clause-subject after the filler).
COMP_STARTERS = {"to", "that", "if", "how", "whether", "what", "why", "when", "where", "who", "which",
                 "it", "he", "she", "they", "i", "you", "we"}
# Straight + curly double-quote characters (ASCII source; curly via escapes).
_DQ = ('"', "“", "”")


def is_person(token, cap):
    """PERSON test: animate personal pronoun OR WordNet dominant noun.person sense OR proper-noun
    capitalization (for OOV names, e.g. joe/hetty). Deterministic; structural, not a gold cast list."""
    t = (token or "").lower().strip(".,'\"!?;:")
    if t in ANIMATE_PRON:
        return True
    if _WN_OK:
        ns = _WN.synsets(t, pos="n")
        if ns and ns[0].lexname() == "noun.person":
            return True
    return bool(cap)


def is_communication_verb(v_lemma):
    """Broad WordNet verb.communication membership (first-3 synsets) -- used ONLY by the Q_broad_control arm
    to MEASURE the over-firing the tight report-verb class avoids (NOT the verdict arm)."""
    if not _WN_OK:
        return False
    syns = _WN.synsets((v_lemma or "").lower(), pos="v")[:3]
    return any(s.lexname() == "verb.communication" for s in syns)


def _patient_is_capitalized(sent, p):
    """Proper-noun test: does the patient token appear title-cased (mid-sentence proper noun) in raw text?"""
    for w in sent.split():
        wc = w.strip('.,"\'!?;:')
        if wc.lower() == (p or "").lower() and wc[:1].isupper():
            return True
    return False


def quotative_frame(sid, sent_text, v_surf, p):
    """Classify the quotative frame around a (verb, person-filler): returns (frame, cap) where frame is
    'INV_QUOTE' (inversion: quote-adjacent report, post-verbal filler = SPEAKER), 'REP_CLAUSE' (a reported
    clausal complement follows the filler = ADDRESSEE), or None (not quotative -> keep). Glass-box, structural."""
    sent = sent_text[sid]
    tk = LCCP.tokenize(sent)
    iv, ip = LCCP.find_pair_positions(tk, v_surf, p)
    raw_dq = any(q in sent for q in _DQ)
    cap = _patient_is_capitalized(sent, p)
    if ip is None:
        # positions unresolved (surface/tokenize mismatch): a report verb inside a quoted sentence is an
        # inversion signal ('said he,'), otherwise unknown.
        return (("INV_QUOTE", cap) if raw_dq else (None, cap))
    after = tk[ip + 1] if ip + 1 < len(tk) else None
    if after in COMP_STARTERS:
        return "REP_CLAUSE", cap
    # inversion: quoted sentence with the filler POST-verbal and no pre-verbal nominal subject in the clause
    if raw_dq and iv is not None and ip > iv:
        pre_nominal = [t for t in tk[:iv]
                       if t not in LCCP.FUNCWORD and t not in LCCP.PREPS and len(t) > 1 and t.isalpha()]
        # a bare inversion ('...,' said papa) has the pre-verb tokens as quote-content, not a clause subject.
        if len(pre_nominal) == 0 or ip == iv + 1:
            return "INV_QUOTE", cap
    return None, cap


def load_gold_raw(slice_lessons):
    """Raw gold agents per (sid, v_lemma) from pos + nopat (load_gold drops nopat agents to a lemma set)."""
    with open(LCCP.GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    agent = {}
    for sid, rec in obj["gold"].items():
        if sid.split("_")[0] not in slice_lessons:
            continue
        for r in rec.get("pos", []):
            agent.setdefault((sid, LCCP.lemma_verb(r["v"])), r["agent"].lower())
        for r in rec.get("nopat", []):
            agent.setdefault((sid, LCCP.lemma_verb(r["v"])), r["agent"].lower())
    return agent


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# The quotative arm over the stacked (S) kept set.
# ----------------------------------------------------------------------------------------------
def build_quotative_arm(kept_S, sent_text, gold_agent):
    """Return (kept_Q, per_instance). Suppress report-verb + person + quotative-frame patients; classify role."""
    kept_Q, per_instance = [], []
    for sid, tup in kept_S:
        v_surf, a, p = tup
        vl = LCCP.lemma_verb(v_surf)
        frame, cap = quotative_frame(sid, sent_text, v_surf, p)
        person = is_person(p, cap)
        quot = bool(vl in REPORT_VERBS and person and frame is not None)
        role = None
        resolved_agent = None
        agent_ok = None
        if quot:
            g_agent = gold_agent.get((sid, vl))
            if frame == "INV_QUOTE":
                role = "SPEAKER"
                resolved_agent = p                      # post-verbal inversion head (the head-finder unlock)
                agent_ok = (g_agent is not None and resolved_agent == g_agent)
            else:
                role = "ADDRESSEE"
                resolved_agent = a                      # reader's pre-verbal subject; NOT re-assigned to filler
                agent_ok = (g_agent is not None and resolved_agent == g_agent)
        else:
            kept_Q.append((sid, tup))
        per_instance.append({
            "sid": sid, "v": vl, "patient": p, "reader_agent": a, "is_person": bool(person),
            "report_verb": bool(vl in REPORT_VERBS), "transfer_comm": bool(vl in TRANSFER_COMM),
            "quot_frame": frame, "suppressed_Q": quot, "discourse_role": role,
            "resolved_agent": resolved_agent, "gold_agent": gold_agent.get((sid, vl)),
            "agent_correct": agent_ok,
        })
    return kept_Q, per_instance


def quotative_target_residual(kept_S, gold, sent_text, gold_agent):
    """arm-S FALSE POSITIVES that ARE report-verb + person + quotative-frame (the addressable quotative class)."""
    target = []
    for sid, tup in kept_S:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None:
            continue  # a TRUE patient, not a residual FP
        frame, cap = quotative_frame(sid, sent_text, tup[0], p)
        if v in REPORT_VERBS and is_person(p, cap) and frame is not None:
            cls = "SUBCAT" if v in rec["nopat"] else ("WITHIN" if v in rec["pos_verbs"] else "SPURIOUS")
            role = "SPEAKER" if frame == "INV_QUOTE" else "ADDRESSEE"
            target.append({"sid": sid, "v": v, "patient": p, "frame": frame, "role": role, "fp_class": cls})
    return target


def broad_control_arm(kept_S, sent_text, gold):
    """NEGATIVE CONTROL (reported, NOT the verdict arm): naive WordNet verb.communication + person gate with
    NO report-verb restriction and NO frame requirement. MEASURES the over-firing onto true patients that the
    tight gate avoids (the head-finder's B2_hardveto analog). Returns (kept, true_patients_lost)."""
    kept, lost = [], []
    for sid, tup in kept_S:
        v_surf, a, p = tup; vl = LCCP.lemma_verb(v_surf)
        cap = _patient_is_capitalized(sent_text[sid], p)
        if is_communication_verb(vl) and is_person(p, cap):
            rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
            if LCCP.match_pos(vl, p, rec["pos"]) is not None:
                lost.append({"sid": sid, "v": vl, "patient": p})
            # suppressed by the broad gate (whether FP or true)
        else:
            kept.append((sid, tup))
    return kept, lost


def suppressed_true_patients(kept_from, kept_to, gold):
    """gold-pos patients present in kept_from but removed in kept_to (the RECALL COST of the suppression)."""
    to_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in kept_to)
    lost = []
    for sid, tup in kept_from:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None and (sid, v, p) not in to_set:
            lost.append({"sid": sid, "v": v, "patient": p})
    return lost


# ----------------------------------------------------------------------------------------------
# Config + run.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    # smoke slice MUST fire the quotative discriminator: L04 (say papa, inversion) + L10 (tell son/him/charles,
    # report-clause) both carry quotative FPs; L10 also carries the categorial came/home + see/see (S fires).
    return dict(slice_lessons=["L04", "L10"], div_thr=3, seed=7)


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], div_thr=3, seed=7)


def run_lccp_armC(slice_lessons, seed):
    """Live LCCP arm-C recompute (G1 real baseline; reproduced not cited)."""
    lcfg = dict(slice_lessons=slice_lessons, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60,
                keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=seed)
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(slice_lessons)
    gold, gold_meta = LCCP.load_gold(slice_lessons)
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, LCCP.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = LCCP.load_glove_for(toks)
    decisions, artifacts, subcat_dec, ho, seen, inst_groups, w = LCCP.run_arms(
        order, reader_svo, sent_text, glove, lcfg, seed)
    return order, sent_text, reader_svo, gold, gold_meta, decisions["C_lccp"]


def run_config(cfg):
    order, sent_text, reader_svo, gold, gold_meta, keptC = run_lccp_armC(cfg["slice_lessons"], cfg["seed"])
    gold_agent = load_gold_raw(cfg["slice_lessons"])
    # ARM S = A + categorial arg/adjunct cascade (B1). Head-finder is a DECLARED no-op on the patient lens.
    kA, kB1, kB2, arg_per, verb_div, cmeta = ARG.build_cascade(order, sent_text, reader_svo, keptC, cfg["div_thr"])
    kept_A, kept_S = kA, kB1
    # ARM Q = S + quotative
    kept_Q, per_instance = build_quotative_arm(kept_S, sent_text, gold_agent)
    decisions = {"A_lccp_armC": kept_A, "S_stacked_categorial": kept_S, "Q_quotative": kept_Q}

    arm_metrics = {arm: LCCP.score_arm(decisions[arm], gold) for arm in ARMS}
    target = quotative_target_residual(kept_S, gold, sent_text, gold_agent)
    q_keep_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in kept_Q)
    q_supp_target = [t for t in target if (t["sid"], t["v"], t["patient"]) not in q_keep_set]
    recall_cost_S_to_Q = suppressed_true_patients(kept_S, kept_Q, gold)

    # AGENT lens
    supp = [d for d in per_instance if d["suppressed_Q"]]
    inv = [d for d in supp if d["discourse_role"] == "SPEAKER"]
    addr = [d for d in supp if d["discourse_role"] == "ADDRESSEE"]
    inv_correct = [d for d in inv if d["agent_correct"]]
    addr_correct = [d for d in addr if d["agent_correct"]]

    # broad negative control (reported)
    kept_broad, broad_lost = broad_control_arm(kept_S, sent_text, gold)
    m_broad = LCCP.score_arm(kept_broad, gold)

    A = arm_metrics["A_lccp_armC"]; S = arm_metrics["S_stacked_categorial"]; Q = arm_metrics["Q_quotative"]
    n_target = len(target)
    quot_reduction_frac = (len(q_supp_target) / n_target) if n_target else 0.0
    recall_cost_pts = round(S["recall"] - Q["recall"], 4)
    residual_share = round(n_target / S["total_fp"], 4) if S["total_fp"] else 0.0

    attribution = {
        "quotative_target_residual": target, "n_quotative_target": n_target,
        "Q_suppressed_targets": q_supp_target, "quot_reduction_frac": round(quot_reduction_frac, 4),
        "S_to_Q_recall_cost_pts": recall_cost_pts, "S_to_Q_true_patients_lost": recall_cost_S_to_Q,
        "residual_share_of_S_FP": residual_share,
        "suppressed_instances": [(d["sid"], d["v"], d["patient"], d["quot_frame"], d["discourse_role"],
                                  d["resolved_agent"], d["gold_agent"], d["agent_correct"]) for d in supp],
        "n_suppressed": len(supp),
        "agent_lens": {
            "n_inversion": len(inv), "n_inversion_speaker_correct": len(inv_correct),
            "n_addressee": len(addr), "n_addressee_agent_preserved": len(addr_correct),
            "inversion_cases": [(d["sid"], d["v"], d["patient"], d["resolved_agent"], d["gold_agent"],
                                 d["agent_correct"]) for d in inv],
            "addressee_cases": [(d["sid"], d["v"], d["patient"], d["reader_agent"], d["gold_agent"],
                                 d["agent_correct"]) for d in addr],
        },
        "broad_control": {"n_true_patients_lost": len(broad_lost), "true_patients_lost": broad_lost,
                          "precision": m_broad["precision"], "recall": m_broad["recall"],
                          "recall_cost_vs_S": round(S["recall"] - m_broad["recall"], 4)},
    }
    return arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order


def build_verdict(arm_metrics, attribution):
    A = arm_metrics["A_lccp_armC"]; S = arm_metrics["S_stacked_categorial"]; Q = arm_metrics["Q_quotative"]
    frac = attribution["quot_reduction_frac"]
    recall_cost = attribution["S_to_Q_recall_cost_pts"]
    prec_nondecr = Q["precision"] >= S["precision"]
    n_target = attribution["n_quotative_target"]
    if recall_cost > 0.10 or (n_target > 0 and frac < 0.15):
        verdict = "HARD_FAIL_QUOTATIVE_BITES"
    elif n_target > 0 and frac >= 0.50 and recall_cost <= 0.05 and prec_nondecr:
        verdict = "HARD_PASS_QUOTATIVE_BREAKS_050"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
    scope = "MATERIAL_SHARE" if attribution["residual_share_of_S_FP"] >= 0.15 else "LOW_CEILING_CORPUS_SPARSE"
    ag = attribution["agent_lens"]
    unlocked = (ag["n_inversion"] > 0 and ag["n_inversion_speaker_correct"] == ag["n_inversion"]
                and ag["n_addressee_agent_preserved"] == ag["n_addressee"])
    agent_tag = "HEADFINDER_UNLOCKS_QUOTATIVE" if unlocked else "GOLD_GRANULARITY_OR_SPLIT_BOUND"
    return {"verdict": verdict, "scope_tag": scope, "agent_lens_tag": agent_tag,
            "quot_reduction_frac": frac, "S_to_Q_recall_cost_pts": recall_cost,
            "precision_A": A["precision"], "precision_S": S["precision"], "precision_Q": Q["precision"],
            "S_to_Q_precision_delta": round(Q["precision"] - S["precision"], 4),
            "A_to_Q_precision_delta": round(Q["precision"] - A["precision"], 4),
            "residual_share_of_S_FP": attribution["residual_share_of_S_FP"],
            "n_inversion_correct": f"{ag['n_inversion_speaker_correct']}/{ag['n_inversion']}",
            "n_addressee_preserved": f"{ag['n_addressee_agent_preserved']}/{ag['n_addressee']}",
            "broad_control_recall_cost": attribution["broad_control"]["recall_cost_vs_S"]}


def scaffold_free_witness(per_instance, decisions, gold):
    """A REAL 'said papa' suppressed by Q + resolved SPEAKER==gold; a true 'thank the man' KEPT (report-verb
    protector); a plain 'called X' KEPT (frame requirement)."""
    inv_witness = None
    for d in per_instance:
        if d["suppressed_Q"] and d["discourse_role"] == "SPEAKER":
            inv_witness = [d["sid"], d["v"], d["patient"], d["resolved_agent"], d["gold_agent"], d["agent_correct"]]
            break
    # a transfer-verb true patient KEPT (protector): report_verb False, in kept_Q, is a gold-pos person patient
    q_keep = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["Q_quotative"])
    transfer_kept = None
    for d in per_instance:
        if d["transfer_comm"] and d["is_person"] and (d["sid"], d["v"], d["patient"]) in q_keep:
            rec = gold.get(d["sid"], {"pos": []})
            if LCCP.match_pos(d["v"], d["patient"], rec["pos"]) is not None:
                transfer_kept = [d["sid"], d["v"], d["patient"]]
                break
    # a report verb + person but NO frame KEPT (tight scope): report_verb True, quot_frame None, kept
    noframe_kept = None
    for d in per_instance:
        if d["report_verb"] and d["is_person"] and d["quot_frame"] is None and \
                (d["sid"], d["v"], d["patient"]) in q_keep:
            noframe_kept = [d["sid"], d["v"], d["patient"]]
            break
    return {"inversion_speaker_suppressed_and_resolved": inv_witness,
            "transfer_verb_true_patient_kept_protector": transfer_kept,
            "report_verb_no_frame_kept_tight_scope": noframe_kept,
            "witness": "PASS" if (inv_witness is not None and inv_witness[5]) else "PARTIAL"}


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
    arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order = run_config(cfg)
    vd = build_verdict(arm_metrics, attribution)

    hashes = {arm: kept_hash(decisions[arm]) for arm in ARMS}
    assert hashes["A_lccp_armC"] != hashes["S_stacked_categorial"], "META_RULE_AF: A==S (categorial no-op)"
    assert hashes["S_stacked_categorial"] != hashes["Q_quotative"], "META_RULE_AF: S==Q (quotative no-op)"

    A = arm_metrics["A_lccp_armC"]; S = arm_metrics["S_stacked_categorial"]; Q = arm_metrics["Q_quotative"]
    baseline_in_band = bool(0.05 < A["precision"] < 0.95 and 0.05 < S["precision"] < 0.95)
    n_q_suppressed = len(decisions["S_stacked_categorial"]) - len(decisions["Q_quotative"])
    discriminator_fires = bool(n_q_suppressed > 0 and hashes["S_stacked_categorial"] != hashes["Q_quotative"])
    witness = scaffold_free_witness(per_instance, decisions, gold)
    elapsed = time.perf_counter() - t0

    v = vd["verdict"]
    msg = (f"{v} [{vd['scope_tag']}] [{vd['agent_lens_tag']}] | slice={'+'.join(cfg['slice_lessons'])} "
           f"| A P={A['precision']:.3f} R={A['recall']:.3f} FP={A['total_fp']} "
           f"| S P={S['precision']:.3f} R={S['recall']:.3f} FP={S['total_fp']}(sub={S['subcat_fp']},wf={S['within_frame_fp']},sp={S['spurious_verb_fp']}) "
           f"| Q P={Q['precision']:.3f} R={Q['recall']:.3f} FP={Q['total_fp']}(sub={Q['subcat_fp']},wf={Q['within_frame_fp']},sp={Q['spurious_verb_fp']}) "
           f"| quot_target={attribution['n_quotative_target']} reduced_frac={vd['quot_reduction_frac']:.3f} "
           f"| S->Q dP={vd['S_to_Q_precision_delta']:+.3f} A->Q dP={vd['A_to_Q_precision_delta']:+.3f} "
           f"recall_cost={vd['S_to_Q_recall_cost_pts']:+.3f} residual_share={vd['residual_share_of_S_FP']:.3f} "
           f"| agent inv={vd['n_inversion_correct']} addr={vd['n_addressee_preserved']} "
           f"broad_ctrl_recall_cost={vd['broad_control_recall_cost']:+.3f} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires} wn={_WN_OK}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "verdict_detail": vd, "attribution": attribution,
        "per_instance": per_instance, "kept_hashes": hashes, "arms_differ_verified": True,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "scaffold_free_witness": witness, "wordnet_available": _WN_OK, "wordnet_err": _WN_ERR,
        "final_metrics_atomicity": "tmp_replace",
        "cited_lccp_armC_precision": CITED_LCCP_ARMC_PRECISION, "cited_headfinder": CITED_HEADFINDER,
        "head_finder_patient_lens": ("DECLARED_NO_OP: the NP-head-finder rewrites AGENT heads; the patient-"
                                     "precision scorer keys on (v_lemma, patient) so it cannot move P/R. Its "
                                     "stacked contribution is on the AGENT lens (CITED HARD_PASS f98c49525) "
                                     "and is EXERCISED on the quotative agent-attribution (inversion speaker "
                                     "resolution below)."),
        "independent_gold_source": "data/gold_mcguffey_lccp_argstruct_v1.json (single-annotator; pos + nopat).",
        "gold_meta": gold_meta,
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "verdict_detail", "attribution", "per_instance",
                            "scaffold_free_witness"],
        "notes": ("QUOTATIVE speaker-attribution lever on the TRUE stacked baseline. A=LCCP arm-C (0.500), "
                  "S=A+categorial arg/adjunct (honest stacked baseline), Q=S+quotative (report-verb + person "
                  "+ quotative-frame suppression). HARD_PASS = Q suppresses >=50% of the quotative-target "
                  "residual at recall-cost <=0.05, precision non-decreasing (coref-at-the-right-layer works "
                  "now candidate-gen is fixed). HARD_FAIL = recall cost >0.10 (report-verb/frame protector "
                  "over-fires) OR <15% reduced (lost deeper / gold-granularity). Broad-control arm measures "
                  "the naive verb.communication over-fire the tight gate avoids. Agent lens = the head-finder "
                  "unlock witness (said papa -> papa=speaker=gold). CLAIM-VET-pending; single-annotator gold "
                  "(caveated); the L12_12 'say he' inversion + plain-ditransitive recipients are out-of-scope "
                  "quotative misses (honest); patient-lens is primary, agent-lens is a thin witness (n_inv small)."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for arm in ARMS:
        m = arm_metrics[arm]
        print(f"  [{arm:>20}] P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} "
              f"n_pred={m['n_pred']} tp={m['tp']} FP(sub/wf/sp)={m['subcat_fp']}/{m['within_frame_fp']}/{m['spurious_verb_fp']}", flush=True)
    print(f"  [quotative target residual] n={attribution['n_quotative_target']} : "
          f"{[(t['sid'],t['v'],t['patient'],t['frame'],t['role']) for t in attribution['quotative_target_residual']]}", flush=True)
    print(f"  [Q suppressed instances] {attribution['suppressed_instances']}", flush=True)
    print(f"  [S->Q recall cost] true patients lost: {attribution['S_to_Q_true_patients_lost']}", flush=True)
    print(f"  [agent lens] {attribution['agent_lens']}", flush=True)
    print(f"  [broad control] {attribution['broad_control']}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def self_test():
    # person + report-verb + frame structural invariants (MEASURED at run)
    assert is_person("papa", False) is True, "papa should be noun.person"
    assert is_person("him", False) is True, "him is animate pronoun"
    assert is_person("castle", False) is False, is_person("castle", False)
    assert "say" in REPORT_VERBS and "tell" in REPORT_VERBS
    assert "thank" not in REPORT_VERBS and "teach" not in REPORT_VERBS, "transfer verbs must be excluded"
    assert LCCP.lemma_verb("said") == "say" and LCCP.lemma_verb("told") == "tell"
    # end-to-end smoke
    cfg = cfg_smoke()
    arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order = run_config(cfg)
    vd = build_verdict(arm_metrics, attribution)
    A = arm_metrics["A_lccp_armC"]; S = arm_metrics["S_stacked_categorial"]; Q = arm_metrics["Q_quotative"]
    hA = kept_hash(decisions["A_lccp_armC"]); hS = kept_hash(decisions["S_stacked_categorial"])
    hQ = kept_hash(decisions["Q_quotative"])
    print(f"[{ANCHOR_NAME}] self-test: verdict={vd['verdict']} scope={vd['scope_tag']} agent={vd['agent_lens_tag']} "
          f"A_P={A['precision']:.3f} S_P={S['precision']:.3f} Q_P={Q['precision']:.3f} "
          f"quot_target={attribution['n_quotative_target']} reduced_frac={vd['quot_reduction_frac']:.3f} "
          f"S->Q_dP={vd['S_to_Q_precision_delta']:+.3f} recall_cost={vd['S_to_Q_recall_cost_pts']:+.3f} "
          f"A!=S={hA != hS} S!=Q={hS != hQ} inv={vd['n_inversion_correct']} wn_ok={_WN_OK}", flush=True)
    print(f"[{ANCHOR_NAME}] quot target residual: "
          f"{[(t['sid'],t['v'],t['patient'],t['frame'],t['role']) for t in attribution['quotative_target_residual']]}", flush=True)
    print(f"[{ANCHOR_NAME}] suppressed: {attribution['suppressed_instances']}", flush=True)


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
