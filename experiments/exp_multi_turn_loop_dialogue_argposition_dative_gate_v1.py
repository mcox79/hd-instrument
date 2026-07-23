"""exp_multi_turn_loop_dialogue_argposition_dative_gate_v1 -- does a STRUCTURAL argument-position /
dative-frame signal CATCH the DIALOGUE role-misassignment error class (29469) that broke the trustworthy
gate's generalization, TRANSFER (fires on the dative structure, corpus-general), and NOT break narrative?

CONTEXT (the 29469 wall): the COMPLETE trustworthy gate (coref-margin OR conflict OR NP-head + correct-to-
head; 29468) gives halluc=0.000 on TWO narrative testbeds but FAILS on DIALOGUE. The residual:
    "Is this the promise that you made your mother?"  q="what did you make?" (theme)  gold "promise"
    the reader answers "mother" -- the RECIPIENT argument, a valid HEAD noun, high coref confidence, no
    match conflict -> EVERY existing gate signal KEEPS it. This is a theta-ROLE misassignment (recipient
    grabbed for a theme query) invisible to the surface/lexical signals.

BRAIN GROUND (dative alternation; Levin dative-verb class): for a dative verb the surface FRAME fixes
recipient vs theme -- double-object "V NP1 NP2" (NP1 recipient, NP2 theme); prepositional "V NP2 to/for
NP1" (NP2 theme); extracted-theme "the NP2 that SUBJ V NP1" (postverbal NP1 = recipient, relative head
NP2 = theme). STRUCTURAL, so the DETECTOR is designed to TRANSFER exactly as the NP-head signal did.

THIS IS A DETECTOR, NOT A SOLVER: the goal is NOT to solve role assignment (the mapped-roles ceiling); it
is to DETECT when a role assignment is structurally uncertain and ABSTAIN (the trustworthy-gate approach).

THE ONE NEW VARIABLE (UNION abstention on the frozen complete gate; the signal = _arg_position_signal.py,
POS-only, gold-free, imported not re-typed):
    complete gate (29468): keep = is_answered AND coref>FIXED_TH AND NOT conflict AND np_head_consistent
                                   (on an NP non-head, return the recovered head)
    ARG gate (this)      : keep = complete_keep AND NOT arg_position_misassigned
      arg_position_misassigned = (theme query) AND (dative verb) AND (answer sits in the RECIPIENT slot and
      NOT the theme slot). Positive detection only (conservative; never fires on a theme-slot answer).

CORPORA (one NEW dialogue role-ambiguity test + TWO frozen narrative controls):
  DIALOGUE (NEW; n=20 dative-alternation constructions; 1 VERBATIM tinyshakespeare anchor x1 + 19
    realistically-constructed dative dialogue lines. Gold = the linguistically-correct THEME, independent
    of the pipeline. NOT gate-friendly: includes CORRECT-answer controls (canonical double-object,
    prepositional, simple-transitive) the signal must NOT abstain -- a position-blind baseline CAN-fail).
  NARRATIVE controls (frozen; the "does not break narrative" test): McGuffey (ORC.TEST_QS, n=31) + LitBank
    (LB verbatim window set, n=21) -- both have complete-gate halluc=0.000 CITED; arg-gate must keep it 0.

ARMS: NO_GATE | PRIOR_GATE (coref OR conflict, 29466) | COMPLETE_GATE (+NP-head + correct-to-head, 29468;
  the POSITION-BLIND baseline that FAILS on dialogue) | ARG_GATE (+arg-position abstention; THE MECHANISM).
Anti-cheat controls (dialogue): RANDOM_ABSTAIN (matched-count random abstention of complete-kept answers)
  + INVERTED_POSITION (abstain the THEME slot instead of the recipient slot -- targeted-but-wrong-slot; if
  the reduction survives inversion, the signal is a construction artifact not position-keyed).

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total, per corpus):
  HARD_PASS (structural arg-position DETECTS + TRANSFERS + does not break narrative):
      DIALOGUE assessable (NO_GATE n_answered>=5 AND n_wrong>=1) AND
      COMPLETE-gate dialogue halluc > 0.05 (the position-blind baseline GENUINELY FAILS; can-fail real) AND
      ARG-gate dialogue halluc <= 0.05 AND arg-gate dialogue coverage > 0 (not abstain-all) AND
      ZERO false-abstain of a correct dialogue answer AND
      POSITION load-bearing: arg-gate dialogue halluc < BOTH the inverted-position AND random-abstain
        halluc (the reduction comes specifically from the recipient-slot detection) AND
      NARRATIVE (McGuffey AND LitBank): arg-gate halluc stays 0.000 AND ZERO false-abstain (coverage of
        correct answers not collapsed).
  HARD_FAIL (a real, honest outcome):
      COMPLETE-gate dialogue fails but ARG-gate dialogue halluc still > 0.05 (role-misassignment NOT
        structurally detectable -> needs semantic role SOLVING = the mapped-roles ceiling), OR
      arg-gate false-abstains >=1 CORRECT answer on ANY narrative corpus (breaks narrative), OR
      arg-gate introduces a narrative error (narrative arg-gate halluc > 0.000), OR
      arg-gate collapses dialogue coverage to abstain-all (coverage == 0), OR
      the reduction survives INVERSION (inverted halluc <= arg halluc -> construction artifact, not
        position-keyed).
  MIDDLE otherwise (partial -- dialogue halluc lowered but not to <=0.05; some residual in unparseable
    frames survives -> a smaller mapped-roles residual).

WHY GENUINELY CAN-FAIL: the detector is POS-frame-limited. If the reader misassigns in a frame the POS
parse mislabels (tagger noise: e.g. a postverbal noun mis-tagged as a verb truncates the object region ->
signal has no opinion -> the confabulation survives), OR if a construction has no relativizer / second
noun / preposition to fix the frame, the signal cannot fire and dialogue halluc stays > 0.05 -> HARD_FAIL
(needs semantic solving). If the signal over-fires it false-abstains a correct theme answer -> breaks
narrative. The data decides whether STRUCTURE detects this role-uncertainty class or it needs role-solving.

DESIGN-GATE (verified at self-test): (1) VERBATIM anchor x1 (substring of tinyshakespeare.txt); (2) FROZEN
th inherited from GN (== v3 McGuffey op-point; NO re-tune); (3) COMPLETE gate BYTE-IDENTICAL (imported
29468 GN._build + CC.run_correct); (4) NO answer leakage (gold token never in its spec); (5) real code path
(GN._build builds the REAL perceptron + POS + coref + NP-head); (6) DIALOGUE assessable + COMPLETE-gate
dialogue halluc > 0.05 (position-blind baseline can-fail); (7) arg-signal is a pure fn of (ans, verb,
passage) reading NO gold; (8) narrative false-abstain == 0 (arg-signal inert on McGuffey + LitBank); (9)
INVERTED-position does NOT achieve the reduction (position load-bearing); (10) determinism (OMP=1, fixed
seed, sorted set, no hash()-seeding).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                    [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check (NO_GATE/PRIOR/COMPLETE/ARG differ on dialogue)  [META_RULE_AF]
# - discriminator CAN-FAIL (unparseable frame residual survives) AND FIRES (complete-gate keeps the
#   recipient-grabs; arg-gate catches them)                         [design-gate / META_RULE_AG]
# - FROZEN threshold; COMPLETE gate IDENTICAL to 29468 (imported not re-typed)
# - baseline_in_band: COMPLETE-gate dialogue halluc > 0.05 (position-blind can-fail); NO_GATE commits wrong
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))   [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - crlb_n/a: symbolic glass-box; halluc (truthfulness invariant) is the reported quantity
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule, FROZEN (no re-tune).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import statistics
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# ORC supplies the McGuffey narrative control. IMPORTANT ORDER: importing GN installs the LitBank corpus by
# MUTATING the shared oracle's TEST_QS/TEST_PASSAGES IN PLACE -- and ORC shares that singleton, so
# ORC.TEST_QS/TEST_PASSAGES would read as LitBank (21) AFTER the GN import. So DEEP-COPY the McGuffey set
# (31) HERE, before the gate stack loads.
import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC
MCGUFFEY_PASSAGES = {pid: txt for pid, txt in ORC.TEST_PASSAGES.items()}
MCGUFFEY_QS = [dict(q) for q in ORC.TEST_QS]

# GN = the 29468 base gate module (owns O, FIXED_TH, SEED, N_SCRAMBLE_SEEDS, _build, prior/np/conflict
#      predicates, _gate_metrics). CC = the shared complete-gate (correct-to-head) logic (byte-identical to
#      the 29468/29469 cells). AP = the NEW structural argument-position / dative-frame signal.
import experiments.exp_multi_turn_loop_litbank_ood_nphead_gate_v1 as GN
import experiments._np_head_correct_common as CC
import experiments._arg_position_signal as AP

O = GN.O
ANCHOR_NAME = "multi_turn_loop_dialogue_argposition_dative_gate_v1"
FIXED_TH = GN.FIXED_TH  # 0.490995, inherited + frozen

# Snapshot the LitBank narrative control (what GN just installed into the shared O) at import.
LITBANK_PASSAGES = {pid: txt for pid, txt in O.TEST_PASSAGES.items()}
LITBANK_QS = [dict(q) for q in O.TEST_QS]

# CITED narrative complete-gate operating points (the 0.000-halluc baselines this cell must not break).
LITBANK_COMPLETE_HALLUC = 0.0    # CITED@exp_multi_turn_loop_litbank_ood_nphead_correct_v1 (complete gate)
MCGUFFEY_COMPLETE_HALLUC = 0.0   # CITED@exp_multi_turn_loop_realtext_nphead_correct_v1 (complete gate)

MIN_ASSESS_ATTEMPTS = 5
CANFAIL_COMPLETE_HALLUC_MIN = 0.05   # COMPLETE-gate dialogue halluc must EXCEED this (baseline genuinely fails)
HP_DIALOGUE_HALLUC_MAX = 0.05
HP_NARRATIVE_HALLUC_MAX = 0.0
N_SCRAMBLE_SEEDS = GN.N_SCRAMBLE_SEEDS

SHAKES = REPO / "data" / "corpora" / "tinyshakespeare.txt"

# ============================================================================================
# DIALOGUE role-ambiguity corpus (n=20). x1 is VERBATIM from tinyshakespeare (self-test asserts substring);
# x2..x20 are realistically-constructed dative-alternation dialogue lines. spec = (relation, verb, subject);
# gold = the linguistically-correct THEME (never in the spec -> no leakage). Mix of MISASSIGN cases (the
# signal must FIRE) and CORRECT controls (canonical double-object / prepositional / simple-transitive -- the
# signal must stay SILENT), so a position-blind baseline can-fail and the signal must DISCRIMINATE.
# ============================================================================================
DIALOGUE = {
    # EXTRACTED-THEME (theme is the relative head; postverbal noun = recipient). Reader grabs the recipient.
    "x1": ("Is this the promise that you made your mother?", ("svo_patient", "made", "you"), "promise"),
    "x2": ("Here is the gift that you gave your mother.", ("svo_patient", "gave", "you"), "gift"),
    "x3": ("This is the story that he told the king.", ("svo_patient", "told", "he"), "story"),
    "x4": ("That is the letter that she sent her father.", ("svo_patient", "sent", "she"), "letter"),
    "x5": ("This is the sword that I brought the captain.", ("svo_patient", "brought", "i"), "sword"),
    "x6": ("Where is the book that you showed the teacher?", ("svo_patient", "showed", "you"), "book"),
    "x7": ("This is the purse that he offered the beggar.", ("svo_patient", "offered", "he"), "purse"),
    "x8": ("Here is the crown that they promised the prince.", ("svo_patient", "promised", "they"), "crown"),
    "x9": ("This is the message that I sent the queen.", ("svo_patient", "sent", "i"), "message"),
    "x10": ("That is the ring that she paid the merchant.", ("svo_patient", "paid", "she"), "ring"),
    # DOUBLE-OBJECT (recipient first). Mixed: reader mostly correct (theme = NP2), but can misassign.
    "x11": ("You gave your mother a gift.", ("svo_patient", "gave", "you"), "gift"),
    "x12": ("He told the king a story.", ("svo_patient", "told", "he"), "story"),
    "x13": ("She sent her father a letter.", ("svo_patient", "sent", "she"), "letter"),
    "x14": ("I promised the prince a crown.", ("svo_patient", "promised", "i"), "crown"),
    # PREPOSITIONAL (theme adjacent to verb; recipient after to/for). Reader correct.
    "x15": ("You gave a gift to your mother.", ("svo_patient", "gave", "you"), "gift"),
    "x16": ("He told a story to the king.", ("svo_patient", "told", "he"), "story"),
    "x17": ("She read a letter to the child.", ("svo_patient", "read", "she"), "letter"),
    # SIMPLE TRANSITIVE (single bare object = theme; no recipient). Reader correct.
    "x18": ("You made a promise.", ("svo_patient", "made", "you"), "promise"),
    "x19": ("He told a story.", ("svo_patient", "told", "he"), "story"),
    "x20": ("She wrote a letter.", ("svo_patient", "wrote", "she"), "letter"),
}

CORPORA = [
    ("DIALOGUE", "dialogue_dative_role_ambiguity", DIALOGUE, True),           # NEW; goal-relevant
    ("MCGUFFEY", "mcguffey_first_reader", None, False),                        # narrative control 1
    ("LITBANK", "litbank_verbatim_windows", None, False),                     # narrative control 2
]


def _install_dialogue():
    O.TEST_PASSAGES = {pid: txt for pid, (txt, _spec, _gold) in DIALOGUE.items()}
    qs = [dict(qid=pid, p=pid, slice="NC", atype="X", spec=spec, gold=gold, text="")
          for pid, (_txt, spec, gold) in DIALOGUE.items()]
    O.TEST_QS = qs
    return qs


def _install_narrative(passages, qs):
    O.TEST_PASSAGES = {pid: txt for pid, txt in passages.items()}
    O.TEST_QS = [dict(q) for q in qs]
    return list(O.TEST_QS)


# ============================================================================================
# infra: out-dir / markers / metrics / crash (atomic).
# ============================================================================================
def _out_dir(run_mode):
    sub = ANCHOR_NAME + ("_smoke" if run_mode == "smoke" else "")
    d = REPO / "data" / ("exp_" + sub)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(out_dir, diag)


# ============================================================================================
# arg-position abstention over the complete-gate answers.
# ============================================================================================
def _misassigned(r, ans):
    """True if the complete-gate answer `ans` for record r sits in the RECIPIENT slot of a dative theme
    query (POS-only, gold-free). O.TEST_PASSAGES must be the current corpus (installed before this call)."""
    spec = r["q"]["spec"]
    rel = spec[0]
    vb = spec[1] if len(spec) > 1 else None
    txt = O.TEST_PASSAGES[r["q"]["p"]]
    return AP.arg_position_misassigned(ans, rel, vb, txt, O.pos_tag_sentence, O.split_sentences)


def _frame_debug(r, ans):
    spec = r["q"]["spec"]
    vb = spec[1] if len(spec) > 1 else None
    txt = O.TEST_PASSAGES[r["q"]["p"]]
    fr, recip, theme = AP.arg_frame_debug(ans, vb, txt, O.pos_tag_sentence, O.split_sentences)
    return {"frame": fr, "recipient": recip, "theme": theme}


def run_corpus(corpus_label, is_dialogue):
    """Install the corpus, build via the REAL 29468 pipeline, run the COMPLETE gate, then apply the arg-
    position UNION abstention. Returns complete-gate + arg-gate metrics + anti-cheat controls + residual."""
    clf = GN.V1.build_clf()
    qs = list(O.TEST_QS)
    recs, _stores, scale = GN._build(clf, qs)
    res = CC.run_correct(GN, recs, scale)
    recs_by_qid = {r["q"]["qid"]: r for r in recs}

    no_gate = res["baseline"]
    complete = res["operating_point"]
    n_total = complete["n_total"]

    # ARG gate = complete gate + arg-position abstention.
    arg_kept = 0
    arg_wrong = 0
    arg_false_abstain = 0            # abstained a CORRECT complete-gate answer (breaks coverage)
    caught_wrong = []               # abstained a WRONG complete-gate answer (the target)
    arg_residual = []               # wrong that SURVIVES arg gate (unparseable frame -> needs semantic)
    arg_answers = []
    per_q = []
    for d in res["_recs_debug"]:
        qid = d["qid"]
        r = recs_by_qid[qid]
        comp_ans = d["correct_gate_ans"]
        comp_corr = d["correct_gate_correct"]
        mis = False
        arg_ans = None
        if comp_ans is not None:
            mis = _misassigned(r, comp_ans)
            if mis:
                arg_ans = None
                if comp_corr == 1:
                    arg_false_abstain += 1
                else:
                    caught_wrong.append(qid)
            else:
                arg_ans = comp_ans
                arg_kept += 1
                if comp_corr == 0:
                    arg_wrong += 1
                    arg_residual.append(qid)
        arg_answers.append(arg_ans)
        pq = {"qid": qid, "p": d["p"], "spec": list(r["q"]["spec"]), "gold": d["gold"],
              "orig_ans": d["orig_ans"], "complete_gate_ans": comp_ans, "complete_gate_correct": comp_corr,
              "arg_misassigned": mis, "arg_gate_ans": arg_ans}
        if is_dialogue:
            pq["arg_frame"] = _frame_debug(r, comp_ans if comp_ans is not None else d["orig_ans"])
        per_q.append(pq)

    arg_halluc = arg_wrong / n_total if n_total else 0.0
    arg_cov = arg_kept / n_total if n_total else 0.0
    arg_prec = (arg_kept - arg_wrong) / arg_kept if arg_kept else 0.0

    out = {
        "corpus": corpus_label, "n_total": n_total,
        "no_gate": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                    "n_answered": no_gate["n_answered"], "n_correct": no_gate["n_correct"],
                    "n_wrong": no_gate["n_wrong"]},
        "prior_gate": {"halluc": res["prior_gate"]["halluc"], "coverage": res["prior_gate"]["coverage"]},
        "complete_gate": {"halluc": complete["halluc"], "coverage": complete["coverage"],
                          "precision_on_answered": complete["precision_on_answered"],
                          "n_answered": complete["n_answered"], "n_wrong_kept": complete["n_wrong_kept"]},
        "arg_gate": {"halluc": round(arg_halluc, 4), "coverage": round(arg_cov, 4),
                     "precision_on_answered": round(arg_prec, 4), "n_answered": arg_kept,
                     "n_wrong_kept": arg_wrong, "n_caught_wrong": len(caught_wrong),
                     "n_false_abstain_correct": arg_false_abstain, "caught_wrong_qids": caught_wrong,
                     "false_abstain_qids": [pq["qid"] for pq in per_q
                                            if pq["arg_misassigned"] and pq["complete_gate_correct"] == 1],
                     "residual_survives_qids": arg_residual},
        "assessable": (no_gate["n_answered"] >= MIN_ASSESS_ATTEMPTS and no_gate["n_wrong"] >= 1),
        "per_question": per_q,
        "_arg_answers": arg_answers,
        "_complete_debug": res["_recs_debug"],
        "_recs_by_qid": recs_by_qid,
    }
    return out


def _anti_cheat_dialogue(dia, recs_by_qid, complete_debug):
    """RANDOM_ABSTAIN (matched-count) + INVERTED_POSITION (abstain the theme slot). Both computed over the
    complete-gate-kept answers; both must be BEATEN by the real arg gate (halluc lower)."""
    n_total = dia["n_total"]
    n_abstained = dia["arg_gate"]["n_caught_wrong"] + dia["arg_gate"]["n_false_abstain_correct"]
    complete_kept = [d for d in complete_debug if d["correct_gate_ans"] is not None]

    # RANDOM_ABSTAIN: abstain n_abstained random of the complete-kept; measure residual halluc.
    rng = random.Random(GN.SEED + 7)
    halls = []
    idxs = list(range(len(complete_kept)))
    for _s in range(N_SCRAMBLE_SEEDS):
        drop = set(rng.sample(idxs, min(n_abstained, len(idxs)))) if n_abstained else set()
        wrong = sum(1 for j, d in enumerate(complete_kept)
                    if j not in drop and d["correct_gate_correct"] == 0)
        halls.append(wrong / n_total if n_total else 0.0)
    random_halluc = round(statistics.mean(halls), 4) if halls else 0.0

    # INVERTED_POSITION: abstain complete-kept answers whose role == 'theme' (the WRONG slot).
    inv_wrong = 0
    inv_kept = 0
    for d in complete_kept:
        r = recs_by_qid[d["qid"]]
        spec = r["q"]["spec"]
        rel = spec[0]
        vb = spec[1] if len(spec) > 1 else None
        txt = O.TEST_PASSAGES[r["q"]["p"]]
        role = AP.arg_role_status(d["correct_gate_ans"], vb, txt, O.pos_tag_sentence, O.split_sentences)
        inv_flag = (rel in AP.THEME_RELATIONS and AP.is_dative_verb(vb) and role == "theme")
        if not inv_flag:
            inv_kept += 1
            if d["correct_gate_correct"] == 0:
                inv_wrong += 1
    inverted_halluc = round(inv_wrong / n_total, 4) if n_total else 0.0

    return {"random_abstain_halluc_mean": random_halluc, "random_abstain_matched_count": n_abstained,
            "inverted_position_halluc": inverted_halluc, "inverted_position_kept": inv_kept,
            "beat_random": round(random_halluc - dia["arg_gate"]["halluc"], 4),
            "beat_inverted": round(inverted_halluc - dia["arg_gate"]["halluc"], 4)}


def _arms_differ(dia):
    """NO_GATE / PRIOR / COMPLETE / ARG must differ on the dialogue answer vectors (the mechanism acted)."""
    complete_answers = [d["correct_gate_ans"] for d in dia["_complete_debug"]]
    no_gate_answers = [d["orig_ans"] for d in dia["_complete_debug"]]
    arg_answers = dia["_arg_answers"]
    digests = {
        "NO_GATE": hashlib.sha256(json.dumps(no_gate_answers, sort_keys=True).encode()).hexdigest(),
        "COMPLETE_GATE": hashlib.sha256(json.dumps(complete_answers, sort_keys=True).encode()).hexdigest(),
        "ARG_GATE": hashlib.sha256(json.dumps(arg_answers, sort_keys=True).encode()).hexdigest(),
    }
    assert digests["NO_GATE"] != digests["COMPLETE_GATE"], "META_RULE_AF: NO_GATE == COMPLETE_GATE"
    assert digests["COMPLETE_GATE"] != digests["ARG_GATE"], \
        "META_RULE_AF: ARG_GATE == COMPLETE_GATE (arg-position abstained nothing -- the one new variable is inert)"
    return digests


# ============================================================================================
# cross-corpus verdict.
# ============================================================================================
def compute_verdict(dia, narratives, anti):
    dia_assessable = dia["assessable"]
    complete_dia_halluc = dia["complete_gate"]["halluc"]
    baseline_can_fail = complete_dia_halluc > CANFAIL_COMPLETE_HALLUC_MIN
    arg_dia = dia["arg_gate"]
    arg_catches = (arg_dia["halluc"] <= HP_DIALOGUE_HALLUC_MAX and arg_dia["coverage"] > 0.0
                   and arg_dia["n_false_abstain_correct"] == 0)
    coverage_collapse = arg_dia["coverage"] == 0.0
    position_loadbearing = (anti["beat_random"] > 0.0 and anti["beat_inverted"] > 0.0)

    narrative_false_abstain = sum(n["arg_gate"]["n_false_abstain_correct"] for n in narratives)
    narrative_new_error = any(n["arg_gate"]["halluc"] > HP_NARRATIVE_HALLUC_MAX
                              and n["arg_gate"]["halluc"] > n["complete_gate"]["halluc"] for n in narratives)
    narrative_intact = (narrative_false_abstain == 0 and not narrative_new_error and
                        all(n["arg_gate"]["coverage"] >= n["complete_gate"]["coverage"] for n in narratives))

    hp = (dia_assessable and baseline_can_fail and arg_catches and position_loadbearing and narrative_intact)
    hf = ((dia_assessable and baseline_can_fail and arg_dia["halluc"] > HP_DIALOGUE_HALLUC_MAX)
          or (narrative_false_abstain >= 1)
          or narrative_new_error
          or coverage_collapse
          or (arg_catches and not position_loadbearing))

    if hp:
        tier = "HARD_PASS"
        outcome = "arg-position-structural-signal-CATCHES-dialogue-role-misassignment-TRANSFERS-narrative-intact"
    elif hf:
        tier = "HARD_FAIL"
        if narrative_false_abstain >= 1 or narrative_new_error:
            outcome = "arg-position-BREAKS-narrative-false-abstain-or-new-error"
        elif coverage_collapse:
            outcome = "arg-position-collapses-dialogue-coverage-to-abstain-all"
        elif arg_catches and not position_loadbearing:
            outcome = "reduction-survives-inversion-signal-is-construction-artifact-not-position-keyed"
        else:
            outcome = "role-misassignment-NOT-structurally-detectable-needs-semantic-role-solving-mapped-ceiling"
    else:
        tier = "MIDDLE_BAND"
        outcome = "partial-dialogue-halluc-lowered-not-to-floor-smaller-mapped-residual"

    localize = []
    if not baseline_can_fail:
        localize.append("COMPLETE-gate dialogue halluc=%.3f <= %.2f -- position-blind baseline did NOT fail; "
                        "the dialogue set does not exercise the role-misassignment class (INCONCLUSIVE)"
                        % (complete_dia_halluc, CANFAIL_COMPLETE_HALLUC_MIN))
    if baseline_can_fail and arg_dia["halluc"] > HP_DIALOGUE_HALLUC_MAX:
        localize.append("ARG-gate dialogue halluc=%.3f still > %.2f: %d confident-wrong SURVIVE the arg-"
                        "position signal (%s) -- unparseable frame / needs SEMANTIC role solving (mapped "
                        "ceiling), not structural detection"
                        % (arg_dia["halluc"], HP_DIALOGUE_HALLUC_MAX, arg_dia["n_wrong_kept"],
                           arg_dia["residual_survives_qids"]))
    if narrative_false_abstain >= 1:
        for n in narratives:
            if n["arg_gate"]["n_false_abstain_correct"] >= 1:
                localize.append("ARG-position FALSE-ABSTAINED %d CORRECT %s answers (breaks narrative): %s"
                                % (n["arg_gate"]["n_false_abstain_correct"], n["corpus"],
                                   n["arg_gate"]["false_abstain_qids"]))
    if arg_catches and not position_loadbearing:
        localize.append("reduction NOT position-keyed: beat_random=%.3f beat_inverted=%.3f (inverting the "
                        "recipient/theme slot achieves the same reduction -> construction artifact)"
                        % (anti["beat_random"], anti["beat_inverted"]))
    if hp and not localize:
        localize.append("STRUCTURAL arg-position CATCHES the dialogue role-misassignment class: COMPLETE-gate "
                        "dialogue halluc %.3f -> ARG-gate %.3f (caught %d recipient-grabs %s, zero false-"
                        "abstain), TRANSFERS with FROZEN th=%.6f, beats random-abstain by %.3f and inverted-"
                        "position by %.3f; McGuffey + LitBank arg-gate halluc stays 0.000 (zero false-abstain)"
                        % (complete_dia_halluc, arg_dia["halluc"], arg_dia["n_caught_wrong"],
                           arg_dia["caught_wrong_qids"], FIXED_TH, anti["beat_random"], anti["beat_inverted"]))

    parts = []
    for c in [dia] + narratives:
        parts.append("%s: NO_GATE h=%.3f -> COMPLETE h=%.3f cov=%.3f -> ARG h=%.3f cov=%.3f (caught=%d "
                     "false-abstain=%d)"
                     % (c["corpus"], c["no_gate"]["halluc"], c["complete_gate"]["halluc"],
                        c["complete_gate"]["coverage"], c["arg_gate"]["halluc"], c["arg_gate"]["coverage"],
                        c["arg_gate"]["n_caught_wrong"], c["arg_gate"]["n_false_abstain_correct"]))
    msg = "%s (%s) | FROZEN th=%.6f NO re-tune | %s || beat_random=%.3f beat_inverted=%.3f" % (
        tier, outcome, FIXED_TH, " || ".join(parts), anti["beat_random"], anti["beat_inverted"])
    return tier, outcome, msg, localize


# ============================================================================================
# self-test: verbatim anchor + frozen th + no leakage + baseline-can-fail + narrative-inert + real path.
# ============================================================================================
def self_test():
    print("[self-test] building REAL 29468 pipeline (perceptron + POS + coref + NP-head) + arg-position ...",
          flush=True)

    # (0) FROZEN threshold inherited from GN.
    assert abs(FIXED_TH - 0.490995) < 1e-6, "FIXED_TH drifted from frozen McGuffey op-point"

    # (1) VERBATIM anchor: x1 is a substring of tinyshakespeare.txt.
    shakes = SHAKES.read_text(encoding="utf-8")
    assert DIALOGUE["x1"][0] in shakes, "PROVENANCE BREACH: x1 not a verbatim substring of tinyshakespeare.txt"

    # (2) NO answer leakage: gold token never appears in its query spec.
    for pid, (_txt, spec, gold) in DIALOGUE.items():
        assert str(gold).lower() not in [str(x).lower() for x in spec], \
            "answer leakage: gold %r in spec %r (%s)" % (gold, spec, pid)

    # (3) arg-signal is a pure fn of (ans, verb, passage) reading NO gold (spot-check).
    r1 = AP.arg_position_misassigned("mother", "svo_patient", "made", DIALOGUE["x1"][0],
                                     O.pos_tag_sentence, O.split_sentences)
    assert r1 is True, "arg-signal must FIRE on x1 'mother' (recipient grabbed for theme query)"
    r2 = AP.arg_position_misassigned("promise", "svo_patient", "made", DIALOGUE["x18"][0],
                                     O.pos_tag_sentence, O.split_sentences)
    assert r2 is False, "arg-signal must NOT fire on x18 'promise' (theme slot, simple transitive)"
    r3 = AP.arg_position_misassigned("observations", "svo_patient", "contain",
                                     "All atoms contain protons.", O.pos_tag_sentence, O.split_sentences)
    assert r3 is False, "arg-signal must be inert on a non-dative verb"

    # (4) real code path + DIALOGUE assessable + baseline can-fail (COMPLETE-gate dialogue halluc > 0.05).
    _install_dialogue()
    dia = run_corpus("DIALOGUE", is_dialogue=True)
    assert dia["assessable"], "DIALOGUE not assessable: NO_GATE answered=%d wrong=%d" % (
        dia["no_gate"]["n_answered"], dia["no_gate"]["n_wrong"])
    assert dia["complete_gate"]["halluc"] > CANFAIL_COMPLETE_HALLUC_MIN, \
        "position-blind baseline did NOT fail on dialogue: COMPLETE halluc=%.3f <= %.2f" % (
            dia["complete_gate"]["halluc"], CANFAIL_COMPLETE_HALLUC_MIN)

    # (5) NO_GATE reproduces O.answer_reader exactly (real code path, no drift) on dialogue.
    _install_dialogue()
    recs, stores, _scale = GN._build(GN.V1.build_clf(), O.TEST_QS)
    for r in recs:
        base = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base, "answer drift on %s: %r vs %r" % (r["q"]["qid"], r["ans"], base)

    # (6a) McGuffey and LitBank are GENUINELY DISTINCT sets (guards the import-order snapshot regression
    #      where a shared-singleton mutation made both read as LitBank).
    assert len(MCGUFFEY_QS) == 31 and len(LITBANK_QS) == 21, \
        "narrative snapshot regression: McGuffey n=%d (want 31), LitBank n=%d (want 21) -- import order" % (
            len(MCGUFFEY_QS), len(LITBANK_QS))
    assert {q["p"] for q in MCGUFFEY_QS}.isdisjoint({q["p"] for q in LITBANK_QS}), \
        "McGuffey and LitBank passage ids overlap -- snapshots collided"

    # (6) narrative controls: arg-position INERT (zero false-abstain) on McGuffey + LitBank.
    _install_narrative(MCGUFFEY_PASSAGES, MCGUFFEY_QS)
    mcg = run_corpus("MCGUFFEY", is_dialogue=False)
    _install_narrative(LITBANK_PASSAGES, LITBANK_QS)
    lit = run_corpus("LITBANK", is_dialogue=False)
    assert mcg["arg_gate"]["n_false_abstain_correct"] == 0, "arg-position false-abstained McGuffey correct(s)"
    assert lit["arg_gate"]["n_false_abstain_correct"] == 0, "arg-position false-abstained LitBank correct(s)"

    print("[self-test] PASS | DIALOGUE NO_GATE halluc=%.3f -> COMPLETE halluc=%.3f (can-fail) -> ARG halluc="
          "%.3f (caught=%d false-abstain=%d) | McGuffey ARG false-abstain=%d | LitBank ARG false-abstain=%d "
          "| FROZEN th=%.6f"
          % (dia["no_gate"]["halluc"], dia["complete_gate"]["halluc"], dia["arg_gate"]["halluc"],
             dia["arg_gate"]["n_caught_wrong"], dia["arg_gate"]["n_false_abstain_correct"],
             mcg["arg_gate"]["n_false_abstain_correct"], lit["arg_gate"]["n_false_abstain_correct"],
             FIXED_TH), flush=True)
    return True


# ============================================================================================
# main run. FULL runs ALL corpora inline to completion.
# ============================================================================================
def run(run_mode):
    out_dir = _out_dir(run_mode)
    corpora = CORPORA if run_mode != "smoke" else CORPORA[:2]  # smoke = dialogue + McGuffey
    n_units = sum(len(DIALOGUE) if lab == "DIALOGUE" else
                  (len(MCGUFFEY_QS) if lab == "MCGUFFEY" else len(LITBANK_QS))
                  for (lab, _c, _p, _g) in corpora)
    _write_start_marker(out_dir, run_mode, expected_n_units=n_units)
    t0 = time.perf_counter()

    results = {}
    for (label, corpus_label, _passages, _goal) in corpora:
        if label == "DIALOGUE":
            _install_dialogue()
        elif label == "MCGUFFEY":
            _install_narrative(MCGUFFEY_PASSAGES, MCGUFFEY_QS)
        else:
            _install_narrative(LITBANK_PASSAGES, LITBANK_QS)
        results[label] = run_corpus(corpus_label, is_dialogue=(label == "DIALOGUE"))

    dia = results["DIALOGUE"]
    narratives = [results[k] for k in ("MCGUFFEY", "LITBANK") if k in results]

    # anti-cheat controls need O installed to the DIALOGUE corpus.
    _install_dialogue()
    # rebuild dialogue recs_by_qid under the reinstalled corpus for the anti-cheat position lookups.
    anti = _anti_cheat_dialogue(dia, dia["_recs_by_qid"], dia["_complete_debug"])
    digests = _arms_differ(dia)

    tier, outcome, msg, localize = compute_verdict(dia, narratives, anti)
    elapsed = time.perf_counter() - t0

    def _clean(c):
        return {k: v for k, v in c.items() if not k.startswith("_")}

    per_corpus_halluc = {results[k]["corpus"]: {"complete": results[k]["complete_gate"]["halluc"],
                                                "arg": results[k]["arg_gate"]["halluc"]} for k in results}
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_corpora": len(results),
        "arms": ["NO_GATE", "PRIOR_GATE(29466)", "COMPLETE_GATE(29468-position-blind)",
                 "ARG_GATE(+arg-position-abstention)"],
        "anti_cheat_controls": ["RANDOM_ABSTAIN(matched-count)", "INVERTED_POSITION(theme-slot)"],
        "threshold_frozen": True, "fixed_threshold": FIXED_TH, "no_retune": True,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point "
                            "(inherited via 29468); FROZEN, NO re-tune (only the arg-position abstention added)",
        "one_variable_vs_complete_gate": "added the STRUCTURAL arg-position/dative-frame UNION abstention "
                                         "(coref-margin OR conflict OR NP-head OR arg-position) to the frozen "
                                         "complete gate; all existing thresholds unchanged",
        "arg_position_rule": "for a THEME query (svo_patient) whose verb is a DATIVE verb, classify the "
                             "answer noun's argument SLOT from the surface frame (double-object / "
                             "prepositional to-for / extracted-theme relative / simple-transitive); ABSTAIN "
                             "iff the answer sits in the RECIPIENT slot and NOT the theme slot. POS-only; "
                             "reads no gold; positive detection only (conservative -- never fires on a theme).",
        "key_question": "does a STRUCTURAL argument-position/dative-frame signal DETECT the dialogue role-"
                        "misassignment class (29469: recipient grabbed for a theme query) and ABSTAIN, "
                        "TRANSFER corpus-general, and NOT break narrative -- OR does role-misassignment need "
                        "SEMANTIC role solving (the mapped-roles ceiling)?",
        "per_corpus_halluc": per_corpus_halluc,
        "dialogue": _clean(dia), "narratives": [_clean(n) for n in narratives],
        "anti_cheat": anti, "arms_differ_digests": digests, "arms_differ_verified": True,
        "narrative_reference": {"mcguffey_complete_halluc": MCGUFFEY_COMPLETE_HALLUC,
                                "litbank_complete_halluc": LITBANK_COMPLETE_HALLUC,
                                "note": "the 2 narrative testbeds the arg-position signal must NOT break"},
        "bands": {"HP_dialogue_halluc_max": HP_DIALOGUE_HALLUC_MAX,
                  "HP_narrative_halluc_max": HP_NARRATIVE_HALLUC_MAX,
                  "canfail_complete_halluc_min": CANFAIL_COMPLETE_HALLUC_MIN,
                  "min_assess_attempts": MIN_ASSESS_ATTEMPTS,
                  "HP_requires": "DIALOGUE assessable AND COMPLETE-gate dialogue halluc>0.05 (baseline can-"
                                 "fail) AND ARG-gate dialogue halluc<=0.05 AND coverage>0 AND zero false-"
                                 "abstain AND arg-gate beats BOTH random-abstain and inverted-position AND "
                                 "narrative (McGuffey+LitBank) arg halluc stays 0.000 with zero false-abstain",
                  "HF_requires": "ARG-gate dialogue halluc>0.05 despite baseline-fail (needs semantic solving) "
                                 "OR narrative false-abstain>=1 OR narrative new error OR dialogue coverage "
                                 "collapses to 0 OR reduction survives position inversion (artifact)"},
        "weakest_interface": localize,
        "gate_threshold_kind": "fixed_interpretable_rule_FROZEN_from_mcguffey_no_retune_plus_structural_flag",
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; halluc (truthfulness invariant) is the reported quantity",
        "fairness": {"frozen_thresholds_no_retune": True, "one_variable_arg_position_only": True,
                     "no_answer_leakage": True, "position_blind_baseline_can_fail": True,
                     "correct_answer_controls_present": True, "anti_cheat_random_and_inverted": True,
                     "narrative_controls_frozen_complete_gate_halluc_zero": True,
                     "dialogue_provenance": "1 VERBATIM tinyshakespeare anchor (x1) + 19 realistically-"
                                            "constructed dative-alternation dialogue lines; gold = the "
                                            "linguistically-correct THEME, independent of the pipeline; NOT "
                                            "gate-friendly (includes correct-answer controls the signal must "
                                            "not abstain)"},
        "reuse_credited": {
            "complete_gate_29468": "exp_multi_turn_loop_litbank_ood_nphead_gate_v1.py (GN: O, FIXED_TH, SEED, "
                                   "_build, prior/conflict/np predicates) + experiments/_np_head_correct_"
                                   "common.py (CC: correct-to-head, run_correct) -- IMPORTED UNCHANGED",
            "arg_position_signal": "experiments/_arg_position_signal.py (NEW; POS-only, gold-free dative-frame "
                                   "argument-position detector -- the one new variable)",
            "narrative_controls": "exp_oracle_mention_upperbound_reader_v1.py (McGuffey TEST_QS) + "
                                  "exp_multi_turn_loop_litbank_ood_fixed_gate_v1.py (LitBank verbatim windows)",
            "dialogue_anchor": "tinyshakespeare.txt (x1 verbatim)"},
        "REQUIRED_FIELDS": ["verdict", "per_corpus_halluc", "dialogue", "narratives", "anti_cheat",
                            "arms_differ_digests", "threshold_frozen", "fixed_threshold", "bands"],
        "notes": ("Structural argument-position / dative-frame DETECTOR for the dialogue role-misassignment "
                  "error class (29469). Added as a UNION abstention to the frozen complete gate (coref OR "
                  "conflict OR NP-head OR arg-position); FROZEN thresholds, corpus swapped. Measures whether "
                  "STRUCTURE detects this role-uncertainty class (transfers, narrative-safe) or it needs "
                  "SEMANTIC role solving (mapped-roles ceiling). CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    for c in [dia] + narratives:
        print("  [%s] %s | NO_GATE halluc=%.3f cov=%.3f (ans=%d correct=%d wrong=%d of %d)"
              % (c["corpus"], "ASSESSABLE" if c["assessable"] else "inconcl",
                 c["no_gate"]["halluc"], c["no_gate"]["coverage"], c["no_gate"]["n_answered"],
                 c["no_gate"]["n_correct"], c["no_gate"]["n_wrong"], c["n_total"]), flush=True)
        print("        COMPLETE(29468) halluc=%.3f cov=%.3f prec=%.3f | +ARG-POSITION halluc=%.3f cov=%.3f "
              "prec=%.3f (caught=%d %s false-abstain=%d %s residual=%s)"
              % (c["complete_gate"]["halluc"], c["complete_gate"]["coverage"],
                 c["complete_gate"]["precision_on_answered"], c["arg_gate"]["halluc"],
                 c["arg_gate"]["coverage"], c["arg_gate"]["precision_on_answered"],
                 c["arg_gate"]["n_caught_wrong"], c["arg_gate"]["caught_wrong_qids"],
                 c["arg_gate"]["n_false_abstain_correct"], c["arg_gate"]["false_abstain_qids"],
                 c["arg_gate"]["residual_survives_qids"]), flush=True)
    print("  [anti-cheat] random-abstain halluc=%.3f (beat=%.3f) | inverted-position halluc=%.3f (beat=%.3f)"
          % (anti["random_abstain_halluc_mean"], anti["beat_random"], anti["inverted_position_halluc"],
             anti["beat_inverted"]), flush=True)
    print("  [weakest] %s" % localize, flush=True)
    print("  [metrics] -> %s" % (out_dir / "metrics.json"), flush=True)
    return tier


def main():
    ap = argparse.ArgumentParser(description=ANCHOR_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()
    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)
    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    run(run_mode)
    sys.exit(0)


if __name__ == "__main__":
    _md = "smoke" if ("--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv)) else \
        ("self_test" if ("--self-test" in sys.argv or ("--run-mode" in sys.argv and "self_test" in sys.argv))
         else "full")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
