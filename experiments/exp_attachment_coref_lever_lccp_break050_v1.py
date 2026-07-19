"""ATTACHMENT/COREF LEVER: does integrating the BUILT deixis + coref (WorkingOverlay) into the LCCP
parser RAISE precision on the attachment/coref residual of the 0.489/0.50 reading-axis cap, vs
LCCP-alone, against INDEPENDENT gold?

QUESTION (the second break-0.50 lever; VET adce417f / atom 29340):
  The reading-axis membership precision is PARSER-CAPPED at 0.489 (assembled reading-axis cell,
  exp_role_filler_factorization_assembled_reading_axis_v1). 48/94 memberships are gold-WRONG; the
  residual splits ~52% ATTACHMENT/COREF (speech/report verbs say/tell/call + character-name/pronoun
  agent fillers) and ~48% subcat-licensing. THIS cell attacks the ATTACHMENT/COREF half by integrating
  the ALREADY-BUILT + VET'd deixis (atom 29326: speaker-attribution 'said X -> X=speaker' + 1st/2nd-
  person bind to speaker/addressee) and coref (atom 29327: agreement/salience prefer_agreement +
  prefer_topical) from hdlab.state_of_mind.WorkingOverlay + the deixis cell's quotative-frame parser
  (exp_read_deixis_participant_tracking_third_reader_v1.parse_quotative_frame), byte-identical.

THE FAIR LENS (why a plain membership re-score would be RIGGED to fail):
  The assembled cell's membership scoring (build_gold_membership_sets) credits ONLY pos-verb agents;
  speech/report verbs (say/tell/call) are NOPAT in this gold, so they have ZERO gold membership and
  NO coref fix could ever make a (say, X) membership gold-true. Scoring the coref lever ONLY on that
  membership view would DECLARE-FAIL BY CONSTRUCTION. So the DECISIVE arm scores AGENT-HEAD ATTRIBUTION
  PER VERB-INSTANCE against the gold agent surface set (pos {agent}|refs UNION nopat {agent}) -- this is
  the lens where the deixis 'said X -> X=speaker' can actually be CREDITED (the gold records the speaker
  as the nopat agent). The MEMBERSHIP lens (0.489) is ALSO reported for continuity (A vs B), but flagged
  as construction-capped for the speech class.

ARMS (ONE VARIABLE: deixis/coref resolution of the agent head OFF vs ON; IDENTICAL LCCP parse + gold):
  ARM A (LCCP-alone)   = LCCP arm-C agent attributions as-is (the 0.489/0.50 baseline front-end).
  ARM B (+deixis/coref)= for each arm-C verb-instance, resolve the AGENT head via the built overlay:
    (1) speech/report verb -> the quotative-frame SPEAKER ('said X'/'X said' -> X);
    (2) 1st/2nd-person deictic agent -> resolve_deixis (speaker/addressee);
    (3) 3rd-person pronoun agent -> resolve_pronoun(prefer_agreement, prefer_topical) topical antecedent;
    (4) junk / non-entity agent (funcword/prep/verb token) -> UNCHANGED (coref has nothing to resolve;
        flagged CANDIDATE_GEN_JUNK -- localizes to LCCP candidate generation, NOT coref).
  Then re-score A vs B against the SAME gold.

MEASURED (decisive, vs INDEPENDENT gold):
  primary = AGENT-attribution precision on the ATTACHMENT/COREF residual class (parser instances A gets
  wrong whose verb is speech OR whose agent is a name/pronoun) A vs B; OVERALL agent precision A vs B;
  the RECALL COST (correct-in-A instances B breaks); a per-residual LOCALIZATION dump (CANDIDATE_GEN_JUNK
  vs RESOLVABLE, and which B fixed) for VET re-annotation; the membership-lens (0.489) A vs B for context.

DESIGN-GATE (pre-registered; verified at smoke):
  (G1) REAL baseline = LCCP arm-C alone vs INDEPENDENT gold (membership 0.489; agent-lens measured live).
  (G2) baseline_in_band: 0.05 < overall agent precision A < 0.95 (real, un-saturated).
  (G3) CAN-FAIL-BOTH-WAYS: HARD_PASS (B corrects >=0.40 of the attachment/coref residual, recall cost
       <=0.05) OR PARTIAL (0.10-0.40 corrected = a real partial break-0.50 step) OR HARD_FAIL (<0.10
       corrected -> the residuals are NOT coref-resolvable / lost at candidate generation) -- all reachable.
  (G4) discriminator fires: B rewrites >0 agent heads AND the resolved-head set differs from A.
  (G5) ONE VARIABLE: deixis/coref agent resolution OFF (A) vs ON (B); LCCP parse + gold IDENTICAL.

VERDICT BANDS (pre-registered; class_correct_frac_B = corrected residuals / |attachment-coref residual|):
  HARD_PASS_COREF_BREAKS_050_ON_ATTACH_CLASS: class_correct_frac_B >= 0.40 AND recall_cost <= 0.05 AND
    overall agent precision B - A >= 0.05.
  PARTIAL_COREF_RAISES_ATTACH_CLASS: 0.10 <= class_correct_frac_B < 0.40 AND recall_cost <= 0.10 (a real
    but partial break-0.50 step; the second subcat-licensing lever remains).
  HARD_FAIL_ATTACH_RESIDUAL_NOT_COREF_RESOLVABLE: class_correct_frac_B < 0.10 OR recall_cost > 0.10 ->
    localizes: the residual heads were lost at LCCP candidate generation OR the gold granularity does not
    credit nopat speech agents; coref is a real capability mis-matched to this residual.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): speaker-attribution + coref for argument-head
  resolution is brain-faithful (distinct discourse-participant + agreement mechanisms; Kintsch situation
  model; Centering Theory). Q: does integrating them fix the say/tell + character-name mis-attachments,
  or are the residual heads irreducibly lost upstream (candidate generation) / unscoreable (nopat gold
  granularity)? Same-limit (nothing to resolve) = accept + localize; fixes-it (partial or full) = the
  lever works. The brain likewise cannot resolve a referent that its parse never proposed.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- a live LCCP arm-C
  recompute (~20s) + a glass-box POS tag + quotative-frame parse + symbolic overlay over ~114 sentences;
  wall < ~60s. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage
  (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic
  hashlib; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (A vs B resolved-agent hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < overall agent precision A < 0.95)
- discriminator fires at smoke (B rewrites >0 agents; resolved set differs)
- scaffold-free witness: a REAL speech/name residual the deixis/coref addresses + a REAL junk residual it
  correctly leaves unchanged (localization visible)
- deterministic seeding; numbers tagged MEASURED@ (printed at run) / CITED@ (0.489 assembled cell)
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402
import experiments.exp_role_filler_factorization_assembled_reading_axis_v1 as ASM  # noqa: E402
import experiments.exp_read_deixis_participant_tracking_third_reader_v1 as DEIXIS  # noqa: E402
import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402
from hdlab.state_of_mind import SetKnownBase, WorkingOverlay, PRONOUN_SCOPE, deixis_person  # noqa: E402

ANCHOR_NAME = "attachment_coref_lever_lccp_break050_v1"
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")

# Speech / report verbs (nopat in this gold; the agent = the quotative-frame SPEAKER).
SPEECH_VERBS = {"say", "tell", "cry", "exclaim", "ask", "answer", "retort", "call",
                "speak", "reply", "inquire", "shout", "whisper", "add", "continue"}
THIRD_PRON = {"he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their"}
FUNC_JUNK = LCCP.FUNCWORD | LCCP.PREPS | LCCP.COMPLEMENTIZERS
CITED_MEMBERSHIP_CEILING = 0.489  # CITED@data/exp_role_filler_factorization_assembled_reading_axis_v1/metrics.json


# ----------------------------------------------------------------------------------------------
# Gold agent-surface sets keyed per (sid, verb-instance): pos {agent}|refs UNION nopat {agent}.
# ----------------------------------------------------------------------------------------------
def load_gold_agentsets(slice_lessons):
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    gold_ag = defaultdict(set)     # (sid, v_lemma) -> acceptable agent surfaces (pos + nopat)
    frame_kind = {}                # (sid, v_lemma) -> 'pos' | 'nopat' (for reporting)
    for sid, rec in obj["gold"].items():
        if sid.split("_")[0] not in slice_lessons:
            continue
        for r in rec.get("pos", []):
            v = LCCP.lemma_verb(r["v"])
            s = {r["agent"].lower()} | set(x.lower() for x in r.get("refs", []))
            gold_ag[(sid, v)] |= s
            frame_kind.setdefault((sid, v), "pos")
        for r in rec.get("nopat", []):
            v = LCCP.lemma_verb(r["v"])
            gold_ag[(sid, v)] |= {r["agent"].lower()} | set(x.lower() for x in r.get("refs", []))
            frame_kind.setdefault((sid, v), "nopat")
    return gold_ag, frame_kind


def is_junk_agent(a):
    """Non-entity token the coref/deixis overlay has NOTHING to resolve (candidate-generation loss)."""
    if not a or not a.isalpha() or len(a) < 2:
        return True
    if a in FUNC_JUNK:
        return True
    # a known verb surface mis-attached as an agent (e.g. 'tell') and not a pronoun.
    if a in LCCP._LEMMA and a not in PRONOUN_SCOPE:
        return True
    return False


# ----------------------------------------------------------------------------------------------
# Build the per-lesson symbolic overlay pass; snapshot the current speaker/addressee per sentence and
# resolve each arm-C verb-instance's agent head via the BUILT deixis/coref (byte-identical reuse).
# ----------------------------------------------------------------------------------------------
def resolve_agents(order, sent_text, keptC, seed):
    """Return {(sid, idx_in_kept): (resolved_head, method)} for every arm-C tuple; A_agent unchanged.
    idx_in_kept is the position in keptC (each tuple resolved once)."""
    # group kept tuples by sid (in kept order)
    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))

    resolved = {}
    n_rewritten = 0
    # process lessons independently (speaker state resets at lesson boundary)
    lessons = []
    seen = set()
    for sid in order:
        lid = sid.split("_")[0]
        if lid not in seen:
            seen.add(lid)
            lessons.append(lid)
    for lid in lessons:
        ov = WorkingOverlay(SetKnownBase())
        quote_open = False
        sids = [sid for sid in order if sid.split("_")[0] == lid]
        for sid in sids:
            raw = sent_text[sid]
            tagged = ORC.pos_tag_sentence(raw)
            # quotative frame + deixis anchor (byte-identical reuse of the built parser)
            ranges, quote_open = DEIXIS._inquote_char_ranges(raw, quote_open)
            starts = DEIXIS._token_char_starts(tagged, raw)
            inquote = [DEIXIS._in_quote(starts[i], ranges) for i in range(len(tagged))]
            frame = DEIXIS.parse_quotative_frame(tagged, raw, ov, inquote=inquote)
            if frame is not None and frame["speaker"] is not None:
                ov.note_turn(frame["speaker"], frame["addressee"])
            sid_speaker = ov.speaker
            sid_addressee = ov.addressee
            # observe tokens so entities exist for 3rd-person resolution
            for i, (surf, low, pos) in enumerate(tagged):
                ov.observe_surface(surf, at_sentence_start=(i == 0))
            # resolve each arm-C agent for this sentence
            for kidx, t in kept_by_sid.get(sid, []):
                v = LCCP.lemma_verb(t[0])
                a = str(t[1]).lower()
                r, method = a, "identity"
                if v in SPEECH_VERBS and sid_speaker is not None:
                    r, method = sid_speaker, "speaker_frame"
                else:
                    dp = deixis_person(a)
                    if dp == "first" and sid_speaker is not None:
                        r, method = sid_speaker, "deixis_first"
                    elif dp == "second" and sid_addressee is not None:
                        r, method = sid_addressee, "deixis_second"
                    elif a in THIRD_PRON:
                        try:
                            ent = ov.resolve_pronoun(a, prefer_agreement=True, prefer_topical=True)
                        except ValueError:
                            ent = None
                        if ent is not None:
                            r, method = ent.head, "coref_topical"
                if r != a:
                    n_rewritten += 1
                resolved[(sid, kidx)] = (r, method)
    return resolved, n_rewritten


# ----------------------------------------------------------------------------------------------
# Agent-attribution scoring (the DECISIVE lens): per verb-instance, agent in gold agent set?
# ----------------------------------------------------------------------------------------------
def score_agent_lens(keptC, gold_ag, frame_kind, resolved):
    """Return per-instance A/B correctness + residual class metrics + localization dump."""
    n_frame = 0
    a_ok = 0
    b_ok = 0
    # attachment/coref residual class = A-wrong instances whose verb is speech OR agent is name/pronoun
    class_items = []          # (sid, v, a_agent, b_head, goldset, junk, b_fixed, method)
    recall_break = 0          # correct-in-A that B breaks
    n_correct_A = 0
    per_instance = []
    for kidx, (sid, t) in enumerate(keptC):
        v = LCCP.lemma_verb(t[0])
        a = str(t[1]).lower()
        key = (sid, v)
        goldset = gold_ag.get(key)
        if not goldset:
            continue  # verb-instance not in gold at this sid (no frame) -> out of scope
        n_frame += 1
        r, method = resolved.get((sid, kidx), (a, "identity"))
        okA = a in goldset
        okB = r in goldset
        a_ok += int(okA)
        b_ok += int(okB)
        if okA:
            n_correct_A += 1
            if not okB:
                recall_break += 1
        per_instance.append({"sid": sid, "v": v, "a_agent": a, "b_head": r, "method": method,
                             "gold": sorted(goldset), "okA": okA, "okB": okB,
                             "frame": frame_kind.get(key)})
        # residual class membership
        is_speech = v in SPEECH_VERBS
        agent_is_entity = (a in PRONOUN_SCOPE) or (a.isalpha() and not is_junk_agent(a))
        if (not okA) and (is_speech or agent_is_entity or (a in PRONOUN_SCOPE)):
            junk = is_junk_agent(a)
            class_items.append({"sid": sid, "v": v, "a_agent": a, "b_head": r, "method": method,
                               "gold": sorted(goldset), "junk": junk, "b_fixed": bool(okB),
                               "is_speech": is_speech})
    n_class = len(class_items)
    n_class_fixed = sum(1 for c in class_items if c["b_fixed"])
    n_class_junk = sum(1 for c in class_items if c["junk"])
    n_class_resolvable = n_class - n_class_junk
    n_resolvable_fixed = sum(1 for c in class_items if c["b_fixed"] and not c["junk"])
    return {
        "n_frame": n_frame,
        "precision_A": round(a_ok / n_frame, 4) if n_frame else 0.0,
        "precision_B": round(b_ok / n_frame, 4) if n_frame else 0.0,
        "n_correct_A": n_correct_A, "recall_break_count": recall_break,
        "recall_cost": round(recall_break / n_correct_A, 4) if n_correct_A else 0.0,
        "attach_coref_residual": {
            "n_class": n_class, "n_fixed_by_B": n_class_fixed,
            "class_correct_frac_B": round(n_class_fixed / n_class, 4) if n_class else 0.0,
            "n_candidate_gen_junk": n_class_junk, "n_resolvable": n_class_resolvable,
            "n_resolvable_fixed_by_B": n_resolvable_fixed,
            "resolvable_fixed_frac": round(n_resolvable_fixed / n_class_resolvable, 4) if n_class_resolvable else 0.0,
        },
        "class_items": class_items, "per_instance": per_instance,
    }


# ----------------------------------------------------------------------------------------------
# Membership lens (continuity with 0.489): rewrite arm-C agent surfaces via B, re-run assembled score.
# ----------------------------------------------------------------------------------------------
def score_membership_lens(keptC, gold, resolved):
    gold_obj, gold_subj = ASM.build_gold_membership_sets(gold)

    def ceiling(kept):
        css = ASM.parser_content_memberships(kept)
        # gold-true fraction over content memberships (min density = all)
        n_mem = 0
        n_true = 0
        for c, slots in css.items():
            for (v, role) in slots:
                n_mem += 1
                gt = (v, c) in gold_obj if role == "OBJ" else (v, c) in gold_subj
                n_true += int(gt)
        return n_true, n_mem

    kept_B = []
    for kidx, (sid, t) in enumerate(keptC):
        r, _m = resolved.get((sid, kidx), (str(t[1]).lower(), "identity"))
        kept_B.append((sid, (t[0], r, t[2])))
    tA, mA = ceiling(keptC)
    tB, mB = ceiling(kept_B)
    return {"A_n_true": tA, "A_n_mem": mA, "A_precision": round(tA / mA, 4) if mA else 0.0,
            "B_n_true": tB, "B_n_mem": mB, "B_precision": round(tB / mB, 4) if mB else 0.0}


# ----------------------------------------------------------------------------------------------
def scaffold_free_witness(agent_lens):
    """A REAL speech/name residual the deixis/coref addresses + a REAL junk residual it leaves alone."""
    speech_or_name = None
    junk_unchanged = None
    for c in agent_lens["class_items"]:
        if speech_or_name is None and not c["junk"] and (c["is_speech"] or c["method"] != "identity"):
            speech_or_name = c
        if junk_unchanged is None and c["junk"] and c["method"] == "identity" and c["b_head"] == c["a_agent"]:
            junk_unchanged = c
    return {"resolvable_residual_addressed": speech_or_name,
            "candidate_gen_junk_left_unchanged": junk_unchanged,
            "witness": "PASS" if (speech_or_name is not None and junk_unchanged is not None) else "PARTIAL"}


def build_verdict(agent_lens):
    res = agent_lens["attach_coref_residual"]
    frac = res["class_correct_frac_B"]
    recall_cost = agent_lens["recall_cost"]
    dprec = agent_lens["precision_B"] - agent_lens["precision_A"]
    if frac >= 0.40 and recall_cost <= 0.05 and dprec >= 0.05:
        v = "HARD_PASS_COREF_BREAKS_050_ON_ATTACH_CLASS"
    elif frac >= 0.10 and recall_cost <= 0.10:
        v = "PARTIAL_COREF_RAISES_ATTACH_CLASS"
    else:
        v = "HARD_FAIL_ATTACH_RESIDUAL_NOT_COREF_RESOLVABLE"
    return {"verdict": v, "class_correct_frac_B": frac, "recall_cost": recall_cost,
            "overall_agent_precision_delta_B_minus_A": round(dprec, 4),
            "n_attach_coref_residual": res["n_class"], "n_fixed_by_B": res["n_fixed_by_B"],
            "n_candidate_gen_junk": res["n_candidate_gen_junk"], "n_resolvable": res["n_resolvable"]}


def kept_agent_hash(keptC, resolved, use_b):
    items = []
    for kidx, (sid, t) in enumerate(keptC):
        a = str(t[1]).lower()
        if use_b:
            a = resolved.get((sid, kidx), (a, ""))[0]
        items.append(f"{sid}|{LCCP.lemma_verb(t[0])}|{a}")
    return hashlib.sha256("\n".join(sorted(items)).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
def run_config(cfg):
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    gold, _gmeta = LCCP.load_gold(cfg["slice_lessons"])
    am, tn, lc, p3, meta, dec, ho, sn = LCCP.run_config(cfg)
    keptC = [(sid, tuple(t)) for sid, t in dec["C_lccp"]]

    gold_ag, frame_kind = load_gold_agentsets(cfg["slice_lessons"])
    resolved, n_rewritten = resolve_agents(order, sent_text, keptC, cfg["seed"])

    agent_lens = score_agent_lens(keptC, gold_ag, frame_kind, resolved)
    membership_lens = score_membership_lens(keptC, gold, resolved)
    return {
        "keptC": keptC, "agent_lens": agent_lens, "membership_lens": membership_lens,
        "n_rewritten": n_rewritten, "resolved": resolved,
        "lccp_summary": {"A_precision_lccp": am["A_handrule"]["all"]["precision"],
                         "C_precision_lccp": am["C_lccp"]["all"]["precision"],
                         "n_keptC": len(keptC), "n_reader_svo": meta["n_reader_svo"]},
    }


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=7)


def cfg_full():
    return LCCP.cfg_full()


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    out = run_config(cfg)
    al = out["agent_lens"]
    ml = out["membership_lens"]
    vd = build_verdict(al)
    witness = scaffold_free_witness(al)

    hA = kept_agent_hash(out["keptC"], out["resolved"], use_b=False)
    hB = kept_agent_hash(out["keptC"], out["resolved"], use_b=True)
    arms_differ = hA != hB
    baseline_in_band = bool(0.05 < al["precision_A"] < 0.95)
    discriminator_fires = bool(out["n_rewritten"] > 0 and arms_differ)
    elapsed = time.perf_counter() - t0
    res = al["attach_coref_residual"]

    msg = (f"{vd['verdict']} | slice={'+'.join(cfg['slice_lessons'])} n_keptC={out['lccp_summary']['n_keptC']} "
           f"| AGENT-lens P A={al['precision_A']:.3f} B={al['precision_B']:.3f} (dP={vd['overall_agent_precision_delta_B_minus_A']:+.3f}) "
           f"n_frame={al['n_frame']} recall_cost={al['recall_cost']:.3f} ({al['recall_break_count']}/{al['n_correct_A']}) "
           f"| ATTACH-COREF residual n={res['n_class']} fixedB={res['n_fixed_by_B']} "
           f"frac={res['class_correct_frac_B']:.3f} (junk={res['n_candidate_gen_junk']} resolvable={res['n_resolvable']} "
           f"resolvable_fixed={res['n_resolvable_fixed_by_B']}) "
           f"| MEMBERSHIP-lens P A={ml['A_precision']:.3f} B={ml['B_precision']:.3f} (cited0.489) "
           f"| n_rewritten={out['n_rewritten']} arms_differ={arms_differ} base_in_band={baseline_in_band} discrim={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": vd["verdict"], "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "verdict_detail": vd, "agent_lens": {k: v for k, v in al.items() if k not in ("class_items", "per_instance")},
        "membership_lens": ml, "lccp_summary": out["lccp_summary"], "n_agent_heads_rewritten": out["n_rewritten"],
        "arms_differ_verified": arms_differ, "arms_differ_hashes": {"A": hA, "B": hB},
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "attach_coref_residual_dump": al["class_items"],
        "agent_lens_per_instance_dump": al["per_instance"],
        "independent_gold_source": ("data/gold_mcguffey_lccp_argstruct_v1.json -- single-annotator gold; "
                                    "AGENT lens = gold pos {agent}|refs UNION nopat {agent} per (sid, verb) "
                                    "(credits speech-verb speaker attribution); MEMBERSHIP lens = the "
                                    "assembled cell's content-membership ceiling (0.489, speech-class capped)."),
        "reused_components": {
            "lccp_parser": "exp_learned_argstruct_parser_lccp_independent_gold_v1 (arm-C, byte-identical)",
            "deixis": "hdlab.state_of_mind.WorkingOverlay note_turn/resolve_deixis/speaker (atom 29326)",
            "coref": "WorkingOverlay resolve_pronoun prefer_agreement/prefer_topical (atom 29327)",
            "quotative_frame": "exp_read_deixis_participant_tracking_third_reader_v1.parse_quotative_frame (byte-identical)",
            "membership_scorer": "exp_role_filler_factorization_assembled_reading_axis_v1 (atom 29340)",
        },
        "REQUIRED_FIELDS": ["verdict", "verdict_detail", "agent_lens", "membership_lens",
                            "attach_coref_residual_dump", "scaffold_free_witness"],
        "notes": ("Attachment/coref break-0.50 lever: integrate BUILT deixis+coref into LCCP arm-C agent "
                  "attribution vs INDEPENDENT gold. HARD_PASS = B corrects >=0.40 of the attach/coref "
                  "residual (recall_cost<=0.05); PARTIAL = 0.10-0.40 (real partial step); HARD_FAIL = <0.10 "
                  "-> residual heads lost at LCCP candidate generation OR unscoreable at nopat gold "
                  "granularity (localizes AWAY from coref). This is ONE of TWO balanced levers (~52% coref / "
                  "~48% subcat); NOT expected to break 0.50 to high ALONE. CLAIM-VET-pending; single-annotator "
                  "gold caveated; per-residual dump provided for VET re-annotation."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  LCCP: A_P={out['lccp_summary']['A_precision_lccp']:.3f} C_P={out['lccp_summary']['C_precision_lccp']:.3f} "
          f"n_keptC={out['lccp_summary']['n_keptC']} n_reader_svo={out['lccp_summary']['n_reader_svo']}", flush=True)
    print(f"  AGENT-lens: n_frame={al['n_frame']} P_A={al['precision_A']:.3f} P_B={al['precision_B']:.3f} "
          f"recall_cost={al['recall_cost']:.3f}", flush=True)
    print(f"  ATTACH-COREF residual: n={res['n_class']} fixed_by_B={res['n_fixed_by_B']} "
          f"frac={res['class_correct_frac_B']:.3f} | candidate_gen_junk={res['n_candidate_gen_junk']} "
          f"resolvable={res['n_resolvable']} resolvable_fixed={res['n_resolvable_fixed_by_B']} "
          f"(frac={res['resolvable_fixed_frac']:.3f})", flush=True)
    print(f"  MEMBERSHIP-lens (cited ceiling 0.489): P_A={ml['A_precision']:.3f} P_B={ml['B_precision']:.3f} "
          f"({ml['A_n_true']}/{ml['A_n_mem']} -> {ml['B_n_true']}/{ml['B_n_mem']})", flush=True)
    print("  --- attachment/coref residual dump (sid, v, parser_agent -> B_head [method], gold, junk, fixed) ---", flush=True)
    for c in al["class_items"]:
        print(f"    {c['sid']} {c['v']:>8} {c['a_agent']:>10} -> {c['b_head']:<10} [{c['method']:<13}] "
              f"gold={c['gold']} junk={c['junk']} fixed={c['b_fixed']}", flush=True)
    print(f"  [witness] resolvable_addressed={witness['resolvable_residual_addressed']}", flush=True)
    print(f"  [witness] junk_unchanged={witness['candidate_gen_junk_left_unchanged']} -> {witness['witness']}", flush=True)
    return payload


def self_test():
    assert is_junk_agent("down") and is_junk_agent("tell") and is_junk_agent("then")
    assert not is_junk_agent("charles") and not is_junk_agent("papa")
    assert deixis_person("i") == "first" and deixis_person("you") == "second"
    cfg = cfg_smoke()
    out = run_config(cfg)
    al = out["agent_lens"]
    vd = build_verdict(al)
    assert al["n_frame"] > 0, "self-test: no gold-framed instances"
    hA = kept_agent_hash(out["keptC"], out["resolved"], use_b=False)
    hB = kept_agent_hash(out["keptC"], out["resolved"], use_b=True)
    print(f"[{ANCHOR_NAME}] self-test: verdict={vd['verdict']} P_A={al['precision_A']:.3f} P_B={al['precision_B']:.3f} "
          f"residual_n={al['attach_coref_residual']['n_class']} fixed={al['attach_coref_residual']['n_fixed_by_B']} "
          f"n_rewritten={out['n_rewritten']} arms_differ={hA != hB} n_keptC={len(out['keptC'])}", flush=True)


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
