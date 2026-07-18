"""
COREF SALIENCE-RANK / TOPICALITY (#2 cue): does prioritizing the TOPICAL protagonist over a merely-
RECENT competitor recover the remaining ordinary-coref failures on REAL 2nd-reader text, ON TOP of the
VET-confirmed agreement fix? Targeted confirm-or-refute of the diagnosed RESIDUAL (agreement-fix cell
0775bc894 / VET a63a1e9670 = CONFIRMED MM: CC 0->0.6, CO 0->0.333, ref-acc 0.294->0.765, RELF1 0.257->
0.522; the residual CO failures localize to SALIENCE_RANK).

WHY (VET-confirmed residual):
  The agreement fix moved coref off the floor but left CO (ordinary coref) at 0.333 (1/3). The residual
  reference failures under the agreement-fixed overlay (MEASURED@exp_coref_agreement_possessive_fix_v1/
  metrics.json:reference_detail.fix_both) are:
    L18_king: he/he/his -> ROBIN (gold KINGBIRD)  x3
    L14_henry: his/he  -> FATHER (gold HENRY)     x2
  In each, a RECENT same-gender / gender-unknown competitor (robin, father) outranks the TOPICAL
  protagonist (kingbird, henry) because the maintained-salience resolver's recency tie-break lets the
  merely-recent entity win when frequency counts tie. Agreement cannot rescue a same-gender competitor.

BRAIN-FAITHFUL MECHANISM (Centering Theory; Grosz-Joshi-Weinstein 1995 CITED):
  The backward-looking center (Cb) -- the topical / most-central entity, typically the discourse SUBJECT
  -- is the PREFERRED pronoun antecedent; a subject/possessor pronoun tends to MAINTAIN the center
  (Continue transition) rather than jump to a recently-introduced non-topic. The forward-looking-center
  ranking is by grammatical role (SUBJECT > OBJECT > OBLIQUE), so a GENDERED pronoun in the SUBJECT /
  POSSESSOR slot should prefer the animate protagonist, while a pronoun in the OBJECT slot -- or a
  NEUTER 'it' (an inanimate referent is not a discourse protagonist) -- may legitimately pick up a
  recent non-topic / recent inanimate entity. Case+gender give the slot almost for free: gendered
  nominative (he/she) + gendered possessive (his / possessive her) -> TOPICAL; accusative (him/them),
  neuter (it/its), plural (they/their) -> keep RECENCY. This CASE+GENDER ROUTING is load-bearing: it
  prevents regressing the correct recency picks "it missed HIM" -> james (object, recent) AND "...sent
  a ball... IT missed" -> ball (recent inanimate) in L60_geo while fixing the gendered subject cases.

THE FIX (overlay, opt-in prefer_topical path -- additive; witness bit-identical, default OFF):
  WorkingOverlay.resolve(prefer_topical=True): among the already agreement-narrowed candidates, select
  the TOPICAL protagonist by (frequency count, then FIRST-MENTION primacy = earliest introduced) with
  NO recency tie-break -- recency is exactly the "merely-recent" lever this path overrides. The CELL
  routes prefer_topical per pronoun by grammatical case (nominative/possessive -> True; accusative ->
  False). This is a WEIGHTING change (topicality beats recency in the subject/possessor slot), not a
  new hard filter; the hard compatible()/agreement narrowing is unchanged.

ISOLATE THE ONE VARIABLE: mention set is FIXED = GOLD (oracle) in every arm; agreement + possessive
fixes are ON in both the floor and the mechanism arm; the ONE toggle that differs between
agreement_baseline and topical is prefer_topical. Downstream (learned role-assigner, relation emission,
RELF1 scorer, comprehension-Q engine) is byte-identical to the oracle/agreement-fix pipeline (imported).

ARMS:
  baseline_raw       : current overlay, NO fixes (positive control -> reproduces oracle store byte-id)
  agreement_baseline : + prefer_agreement + possessive-timing fix (= the prior fix_both) [THE FLOOR]
  topical            : agreement_baseline + prefer_topical (case-routed)                 [THE MECHANISM]

DESIGN-GATE (verified at self-test/smoke BEFORE the full run; USER: fair tests every time):
  (1) POSITIVE-CONTROL: baseline_raw reproduces ORC.extract_passage BYTE-IDENTICAL per passage;
  (2) REAL baseline = the agreement-fixed overlay (CC 0.6, CO 0.333), RE-MEASURED not assumed -- the
      floor to beat (topical must NOT regress CC);
  (3) CAN-FAIL two ways: HARD-FAIL if topical CO stays at the agreement_baseline floor (salience-rank
      does not help) OR if topical CC REGRESSES below the agreement_baseline (topicality over-applied
      broke an agreement win). Both genuinely reachable;
  (4) DIFFICULTY-ON: the real topical-competitor cases (henry/father, kingbird/robin) -- same-gender /
      gender-unknown recent competitors agreement cannot separate;
  (5) ONE variable: prefer_topical (agreement + possessive held ON in both floor and mechanism);
  (6) TELEMETRY-SENSITIVE: toggling prefer_topical MUST move the metrics (ARMS-MUST-DIFFER hash gate);
  (7) INDEPENDENT gold: coref gold antecedents hand-annotated by the linguistic reading (anti-circular);
      self-test asserts the annotated pronoun surface sequence matches the tokenizer output;
  (8) NO-REGRESSION WITNESS: self-test asserts L60_geo "him" -> james STILL resolves correctly under the
      topical arm (the case-routing guard against over-applying topicality to the object slot);
  (9) determinism OMP=1, fixed seed, sorted(set); overlay witness verify_state_of_mind_overlay.py PASSES.

BRANCHES:
  HARD-PASS = topical moves CO meaningfully OFF the agreement floor (recovers the henry/kingbird topical
    cases) WITHOUT regressing CC + reference-acc rises -> the #2 cue (SALIENCE_RANK) CONFIRMED; coref
    further improved on real text (agreement + salience = the two diagnosed cues, both fixed).
  HARD-FAIL = CO stuck at the agreement floor OR CC regresses -> topicality-vs-agreement tension ->
    localize the tradeoff -> a proper weighted multi-cue integration (Competition Model) is next, not a
    simple case-routed override.

Glass-box (case routing + frequency/first-mention topicality; NO external LLM; NO torch/GPU). Local /
foreground-to-completion. NO push / NO remote-persist. Reported CLAIM-VET-pending (NOT self-declared
chain-grade). Determinism OMP=1, fixed seed.

ANCHOR: coref_salience_rank_topicality_v1
RESIDUAL context: agreement-fix cell 0775bc894 (VET a63a1e9670 CONFIRMED MM); diagnostic 8a6892e25.
CORPUS: reuses the oracle cell's REAL McGuffey second-reader passages + gold (verbatim import).
COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic coref/query); wall < 120s; no HD.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - discriminator CAN-FAIL (topical CO can stay at floor; CC can regress) [design-gate]
# - POSITIVE-CONTROL: baseline_raw reproduces oracle store (tol=0) [reproduce_prior]
# - NO-REGRESSION witness: L60 him->james preserved under topical  [design-gate #8]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay (prefer_topical path) +
#   the REAL oracle extract pipeline on the REAL passages  [F.1]
# - substrate_signature: binds WorkingOverlay/resolve_pronoun sigs (incl new prefer_topical kwarg)  [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; agreement floor CITED@prior cell / VET
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import hashlib
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the oracle cell's REAL passages + gold + downstream pipeline VERBATIM (byte-identical downstream).
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402
from hdlab.state_of_mind import (  # noqa: E402
    WorkingOverlay, SetKnownBase, PRONOUN_SCOPE, infer_nominal_gender,
)

ANCHOR_NAME = "coref_salience_rank_topicality_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 12345

# ---- Pre-registered bands (set BEFORE the final run; HYPOTHESIZED@this prereg) ----------------------
# The agreement_baseline arm is THE FLOOR (re-measured, not assumed). CITED context (prior cell
# 0775bc894 / VET a63a1e9670): fix_both CC=0.600, CO=0.333, ref-acc=0.765. HARD-PASS = the topical arm
# moves CO meaningfully off that floor WITHOUT regressing CC + ref-acc rises.
CO_RISE_MIN = 0.30       # topical CO must exceed agreement_baseline CO by at least this (>= +1 of 3 Qs)
REF_RISE_MIN = 0.05      # topical ref-acc must exceed agreement_baseline ref-acc by at least this
NO_CC_REGRESS_EPS = 0.0  # topical CC must be >= agreement_baseline CC (no regression; strict)
TELEMETRY_MIN_MOVE = 0.05  # toggling prefer_topical must move at least one primary metric by this
POSITIVE_CONTROL_TOL = 0   # baseline_raw store must reproduce oracle store BYTE-IDENTICAL

# The specific residual cases this cue must recover (target-case witness in the topical arm).
TARGET_CASES = {
    "L18_king": "kingbird",   # he/he/his gold kingbird (was robin under agreement_baseline)
    "L14_henry": "henry",     # his/he gold henry (was father under agreement_baseline)
}
# The correct RECENCY pick the case-routing must NOT regress (object-slot pronoun).
NO_REGRESS_CASE = ("L60_geo", "him", "james")

# =======================================================================================
# INDEPENDENT GOLD coref antecedents (hand-annotated by the linguistic reading; anti-circular; NOT
# derived from the extractor). Identical annotation as the agreement-fix cell (same passages/gold).
GOLD_ANTECEDENTS = {
    "L5_dogs":  [("his", "dogs"), ("his", "james"), ("he", "james"), ("he", "james")],
    "L5b_dodger": [("he", "dodger")],
    "L18_king": [("he", "kingbird"), ("he", "kingbird"), ("his", "kingbird")],
    "L14_henry": [("his", "henry"), ("his", "henry"), ("he", "henry")],
    "L23_doll": [("her", "mary"), ("she", "mary"), ("she", "mary"), ("him", "dash")],
    "L2_cat":   [],
    "L21_bee":  [],
    "L60_geo": [("he", "george"), ("it", "ball"), ("him", "james")],
    "L28_sam": [("his", "man"), ("his", "man"), ("him", "man"),
                ("them", "cents"), ("them", "cents")],
    "L8_puss": [("her", "puss"), ("them", "kittens")],
    "L26_patty": [("she", "patty"), ("her", "patty")],
    "L57_laura": [("her", "laura"), ("it", "kitten")],
    "L32_tiger": [("she", "tigress"), ("her", "tigress"), ("it", "kitten")],
    "L35_willie": [("his", "willie"), ("his", "willie")],
}

# Third-person resolvable pronouns we score (1st/2nd person excluded -- no discourse antecedent).
_RESOLVABLE_POSS = ORC.PRONOUNS_POSS - {"my", "your", "our"}          # his, her, its, their
_RESOLVABLE_SO = ORC.PRONOUNS_SUBJ_OBJ - {"i", "you", "we", "us", "me"}  # he,him,she,her,it,they,them
_RESOLVABLE = _RESOLVABLE_POSS | _RESOLVABLE_SO

# Pronoun grammatical-case routing for the salience-rank cue (Centering Cf-ranking by role).
# The Centering protagonist-continuity cue applies to the ANIMATE GENDERED discourse protagonist in the
# SUBJECT / POSSESSOR slot: gendered nominative (he/she) + gendered possessive (his/her-poss) -> prefer
# the TOPICAL protagonist. Everything else keeps RECENCY:
#   - accusative object (him/her-obj/them) -> object slot may pick up a recent NON-topic entity;
#   - neuter 'it'/'its' -> an inanimate referent is NOT a discourse protagonist; the recent inanimate
#     referent is usually right ("...sent a BALL... it missed him" -> ball, recency). Routing 'it' as
#     topical REGRESSES it (measured: L60 it->ball became it->dollar), so 'it' keeps recency;
#   - plural they/their -> no gendered singular protagonist; keep recency (conservative; not exercised).
_OBJECT_PRONOUNS = {"him", "them", "us", "me"}


def _prefers_topical(low, pos):
    """Route prefer_topical by grammatical case + gender (glass-box; Centering Cf-ranking of the animate
    gendered protagonist). Topical iff a GENDERED (masc/fem) pronoun in the SUBJECT (he/she) or POSSESSOR
    (his / possessive her) slot; accusative objects, neuter it/its, and plural they/their keep recency.
    'her' is disambiguated by POS (PRP$ possessive -> topical; PRP object -> recency)."""
    if low in _OBJECT_PRONOUNS:
        return False                      # accusative object slot -> recency
    sc = PRONOUN_SCOPE.get(low)
    if sc is None or sc["gender"] not in ("masc", "fem"):
        return False                      # neuter (it/its) / plural (they/their) -> recency (no protagonist)
    if low == "her":
        return pos == "PRP$"              # possessive her -> topical; object her -> recency
    return True                           # he / she (nominative) or his (possessive) -> topical protagonist


def _agreement_attrs(low, pos, is_name):
    """Grounding-fed agreement attributes for the FIX_AGREEMENT observe path (glass-box; no LLM).
    Identical to the agreement-fix cell: names -> curated NAME_GENDER; common nouns -> gendered-noun cue;
    POS-driven number (NNS/NNPS -> plural); grounding animacy (PERSON/ANIMAL -> animate)."""
    if is_name:
        gender = ORC.NAME_GENDER.get(low, None)
    else:
        gender = infer_nominal_gender([low])
    number = "plural" if pos in ("NNS", "NNPS") else "singular"
    animacy = "animate" if ORC.is_animate(low) else "inanimate"
    return gender, number, animacy


def extract_passage_cfg(passage_text, clf, pid, fix_possessive, agreement, topical):
    """Coref pass + role assignment + relation emission on ONE real passage with three independent
    toggles. mention set is FIXED = GOLD (oracle). topical routes prefer_topical per pronoun by case.
    fix_possessive=False AND agreement=False AND topical=False MUST reproduce ORC.extract_passage
    byte-identically (positive control)."""
    mention_mode = "oracle"
    gold_heads = ORC.GOLD_MENTIONS.get(pid, frozenset())
    coref_strategy = ORC.FIXED_COREF_STRATEGY  # 'maintained' (validated; not tuned)
    pref = bool(agreement)

    # Known base built over ALL passages' grounded heads -- identical to ORC.extract_passage.
    known = set()
    for txt in list(ORC.TEST_PASSAGES.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    offset = 0
    for sent in ORC.split_sentences(passage_text):
        tagged = ORC.pos_tag_sentence(sent)
        pron_res = {}   # local i -> resolved head (first-pass, correctly-timed)
        # ---- observe entities + resolve pronouns left-to-right (feeds coref) ----
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:  # any 3p pronoun (subj/obj/poss) -> reference
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass  # 1st/2nd-person possessive (my/your/our) handled structurally below
            else:
                if not ORC.observe_as_mention(low, pos, mention_mode, gold_heads):
                    continue
                is_name = (low in ORC.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                if agreement:
                    g, num, anim = _agreement_attrs(low, pos, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name, animacy=anim)
                else:
                    g, num = ORC.grounded_gender_number(low, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        # ---- role assignment (learned; mention gate = oracle) ----
        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, gold_heads)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or ORC.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))

        # ---- structural (POS-driven): possessive 's, possessive-pronoun, color ----
        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    # FIX: use the correctly-timed first-pass resolution (owner resolved at the
                    # possessive's stream position, BEFORE its own head noun entered the overlay).
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    # BASELINE BUG: re-resolve here, AFTER the whole sentence is in the overlay.
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                if low in _RESOLVABLE:
                    res_by_pos[offset + i] = (low, owner if owner != low else None)
        # color attribute
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        # record subj/obj pronoun resolutions (first-pass; identical across possessive toggle)
        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        offset += len(tagged)

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos


# =======================================================================================
# Arm runner.
# =======================================================================================
CONFIGS = {
    "baseline_raw":       dict(fix_possessive=False, agreement=False, topical=False),
    "agreement_baseline": dict(fix_possessive=True,  agreement=True,  topical=False),
    "topical":            dict(fix_possessive=True,  agreement=True,  topical=True),
}


def run_config(cfg_name, clf):
    """Returns dict(store, correct, relf1, slices, ref_acc, ref_detail, answers)."""
    fp = CONFIGS[cfg_name]["fix_possessive"]
    ag = CONFIGS[cfg_name]["agreement"]
    tp = CONFIGS[cfg_name]["topical"]
    store = {}
    res_by_pos = {}
    for pid, text in ORC.TEST_PASSAGES.items():
        rels, rbp = extract_passage_cfg(text, clf, pid, fp, ag, tp)
        store[pid] = rels
        res_by_pos[pid] = rbp
    correct = []
    answers = []
    for q in ORC.TEST_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = ORC._relf1_for_store(store)
    slices = ORC._slices(correct)
    n_tot = 0
    n_ok = 0
    ref_detail = {}
    for pid in ORC.TEST_PASSAGES:
        gold = GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        det = []
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
            det.append(dict(surf=g_surf, gold=g_head, pred=p_head, ok=ok,
                            surf_match=(p_surf == g_surf)))
        ref_detail[pid] = det
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    return dict(store=store, correct=correct, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_n=n_tot, ref_ok=n_ok,
                ref_detail=ref_detail, answers=answers)


def _pred_for(ref_detail, pid, surf, gold):
    """Return the predicted head for the FIRST gold pronoun in pid matching (surf, gold)."""
    for d in ref_detail.get(pid, []):
        if d["surf"] == surf and ORC.normalize(d["gold"]) == ORC.normalize(gold):
            return d["pred"]
    return None


def _target_cases_resolved(ref_detail):
    """All annotated pronouns in the TARGET_CASES passages resolve to the topical protagonist head."""
    detail = {}
    ok_all = True
    for pid, gold_head in TARGET_CASES.items():
        rows = ref_detail.get(pid, [])
        oks = [(d["surf"], d["pred"], d["ok"]) for d in rows]
        this_ok = all(d["ok"] for d in rows) and len(rows) > 0
        detail[pid] = dict(gold=gold_head, rows=oks, resolved=this_ok)
        ok_all = ok_all and this_ok
    return ok_all, detail


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _arms_must_differ(named_outputs):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL WorkingOverlay + oracle pipeline ...")
    import inspect
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement", "prefer_topical"} <= rp_params, \
        "resolve_pronoun() must accept prefer_agreement + prefer_topical kwargs"
    rs_params = set(inspect.signature(WorkingOverlay.resolve).parameters)
    assert {"prefer_topical"} <= rs_params, "resolve() must accept prefer_topical kwarg"

    # F.1 real_code_path: exercise the REAL overlay prefer_topical path on the kingbird micro-case.
    # kingbird (subject, first) then robin (oblique, recent); tied count -> maintained/recency picks
    # the recent robin; prefer_topical must pick the topical protagonist kingbird.
    ov = WorkingOverlay()
    ov.observe("kingbird", gender=None, number="singular", animacy="animate")
    ov.observe("robin", gender=None, number="singular", animacy="animate")  # recent, tied count
    plain = ov.resolve_pronoun("he", strategy="maintained", prefer_agreement=True)
    topical = ov.resolve_pronoun("he", strategy="maintained", prefer_agreement=True, prefer_topical=True)
    assert plain is not None and plain.head == "robin", \
        f"agreement_baseline (maintained) should pick recent robin, got {plain and plain.head}"
    assert topical is not None and topical.head == "kingbird", \
        f"prefer_topical should pick topical protagonist kingbird, got {topical and topical.head}"
    print(f"[self-test] topical lever fires: he plain->{plain.head} prefer_topical->{topical.head}")

    # NO-REGRESSION micro: an OBJECT pronoun (him) must keep recency (george subj first, james recent).
    ov2 = WorkingOverlay()
    ov2.observe("george", is_proper_name=True, gender="masc", animacy="animate")
    ov2.resolve_pronoun("he", strategy="maintained", prefer_agreement=True, prefer_topical=True)  # ->george
    ov2.observe("james", is_proper_name=True, gender="masc", animacy="animate")  # recent
    # 'him' is routed prefer_topical=False by case (object slot) -> recency keeps james.
    assert _prefers_topical("him", "PRP") is False, "him (object) must route recency, not topical"
    him = ov2.resolve_pronoun("him", strategy="maintained", prefer_agreement=True,
                              prefer_topical=_prefers_topical("him", "PRP"))
    assert him is not None and him.head == "james", \
        f"object 'him' must keep recency (recent james), got {him and him.head}"
    print(f"[self-test] no-regression case-routing: object him->{him.head} (recency preserved)")

    # case-routing table sanity (topical iff gendered subject/possessor; else recency).
    assert _prefers_topical("he", "PRP") and _prefers_topical("she", "PRP")
    assert _prefers_topical("his", "PRP$") and _prefers_topical("her", "PRP$")
    assert not _prefers_topical("them", "PRP") and not _prefers_topical("her", "PRP")
    assert not _prefers_topical("it", "PRP") and not _prefers_topical("its", "PRP$"), \
        "neuter it/its must keep recency (inanimate referent is not a discourse protagonist)"
    assert not _prefers_topical("they", "PRP") and not _prefers_topical("their", "PRP$"), \
        "plural they/their keep recency (conservative; no gendered singular protagonist)"

    # FIT the shared learned role-assigner (REAL training pipeline).
    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    # POSITIVE CONTROL: baseline_raw arm == oracle extract_passage BYTE-IDENTICAL.
    n_pass = 0
    for pid, text in ORC.TEST_PASSAGES.items():
        mine, _ = extract_passage_cfg(text, clf, pid, fix_possessive=False, agreement=False, topical=False)
        gold_store, _ = ORC.extract_passage(text, "learned", clf, ORC.FIXED_COREF_STRATEGY,
                                             "oracle", ORC.GOLD_MENTIONS.get(pid, frozenset()))
        assert mine == gold_store, (
            f"POSITIVE-CONTROL FAIL {pid}: baseline_raw diverges from oracle extract_passage\n"
            f"  mine={mine}\n  oracle={gold_store}")
        n_pass += 1
    print(f"[self-test] POSITIVE-CONTROL: baseline_raw == oracle store byte-identical on {n_pass} passages")

    # GOLD-SURFACE ALIGNMENT: annotated pronoun surface sequence matches the tokenizer output.
    for pid in ORC.TEST_PASSAGES:
        _, rbp = extract_passage_cfg(ORC.TEST_PASSAGES[pid], clf, pid,
                                     fix_possessive=True, agreement=True, topical=True)
        pred_surf = [rbp[k][0] for k in sorted(rbp.keys())]
        gold_surf = [s for (s, _h) in GOLD_ANTECEDENTS.get(pid, [])]
        assert pred_surf == gold_surf, (
            f"GOLD-SURFACE MISMATCH {pid}: annotated pronoun sequence != tokenizer output\n"
            f"  gold={gold_surf}\n  pred={pred_surf}")
    print("[self-test] gold pronoun surface sequences match tokenizer output on all passages")

    # END-TO-END NO-REGRESSION witness on the REAL passage: L60 him->james under the topical arm.
    topo = run_config("topical", clf)
    pid_n, surf_n, gold_n = NO_REGRESS_CASE
    pred_n = _pred_for(topo["ref_detail"], pid_n, surf_n, gold_n)
    assert ORC.normalize(pred_n) == ORC.normalize(gold_n), \
        f"NO-REGRESSION FAIL: {pid_n} {surf_n} -> {pred_n} (must stay {gold_n}) under topical arm"
    print(f"[self-test] no-regression (real passage): {pid_n} {surf_n}->{pred_n} preserved")

    # determinism: two runs identical.
    r1 = run_config("topical", clf)
    r2 = run_config("topical", clf)
    assert r1["correct"] == r2["correct"] and r1["ref_acc"] == r2["ref_acc"], "non-deterministic run"
    print("[self-test] deterministic (two topical runs identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=len(CONFIGS))

    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    results = {name: run_config(name, clf) for name in CONFIGS}

    digests = _arms_must_differ({name: results[name]["answers"] for name in CONFIGS})

    ab = results["agreement_baseline"]   # THE FLOOR
    tp = results["topical"]              # THE MECHANISM
    raw = results["baseline_raw"]

    def slc(r, s):
        return r["slices"][s]

    ab_cc, ab_co = slc(ab, "CC"), slc(ab, "CO")
    tp_cc, tp_co = slc(tp, "CC"), slc(tp, "CO")
    ab_ref, tp_ref = ab["ref_acc"], tp["ref_acc"]
    ab_relf1 = ab["relf1"]["micro_f1"]
    tp_relf1 = tp["relf1"]["micro_f1"]

    # telemetry-sensitivity (agreement_baseline -> topical must move a primary metric)
    moves = [abs(tp_cc - ab_cc), abs(tp_co - ab_co), abs(tp_ref - ab_ref),
             abs(tp_relf1 - ab_relf1), abs(slc(tp, "CMP") - slc(ab, "CMP"))]
    telemetry_ok = max(moves) >= TELEMETRY_MIN_MOVE

    # target-case + regression witnesses (topical arm)
    targets_ok, targets_detail = _target_cases_resolved(tp["ref_detail"])
    pid_n, surf_n, gold_n = NO_REGRESS_CASE
    no_regress_pred = _pred_for(tp["ref_detail"], pid_n, surf_n, gold_n)
    no_regress_ok = (ORC.normalize(no_regress_pred) == ORC.normalize(gold_n))

    # verdict logic
    co_rose = (tp_co - ab_co) >= CO_RISE_MIN
    ref_rose = (tp_ref - ab_ref) >= REF_RISE_MIN
    cc_regressed = (tp_cc + 1e-9) < (ab_cc - NO_CC_REGRESS_EPS)
    co_stuck = (tp_co <= ab_co)

    if not telemetry_ok:
        verdict = "INVALID_TELEMETRY_INSENSITIVE"
        vmsg = (f"prefer_topical toggle moved primary metrics < {TELEMETRY_MIN_MOVE} "
                f"(max move {max(moves):.3f}); mechanism vacuous")
    elif cc_regressed:
        verdict = "HARD_FAIL_CC_REGRESSION"
        vmsg = (f"topicality REGRESSED CC: {ab_cc:.3f}->{tp_cc:.3f} (agreement win broken); "
                f"topicality-vs-agreement tension -> weighted multi-cue integration is next")
    elif co_stuck:
        verdict = "HARD_FAIL_CO_STUCK"
        vmsg = (f"topical left CO at the agreement floor: {ab_co:.3f}->{tp_co:.3f}; salience-rank did "
                f"not recover the topical cases -> localize (deeper than case-routed override)")
    elif co_rose and (not cc_regressed) and ref_rose and targets_ok and no_regress_ok:
        verdict = "HARD_PASS_SALIENCE_RANK_CONFIRMED"
        vmsg = (f"topical recovered the topical cases WITHOUT regressing CC: CO {ab_co:.3f}->{tp_co:.3f}, "
                f"CC {ab_cc:.3f}->{tp_cc:.3f}, ref-acc {ab_ref:.3f}->{tp_ref:.3f}; henry/kingbird resolved; "
                f"L60 him->james preserved; #2 cue (SALIENCE_RANK) CONFIRMED")
    else:
        verdict = "PARTIAL_TOPICAL_MOVED"
        vmsg = (f"topical moved coref but did not clear all HARD-PASS gates: CO {ab_co:.3f}->{tp_co:.3f} "
                f"(need +{CO_RISE_MIN}), CC {ab_cc:.3f}->{tp_cc:.3f}, ref-acc {ab_ref:.3f}->{tp_ref:.3f}, "
                f"targets_ok={targets_ok}, no_regress_ok={no_regress_ok}; localize residual")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: CO {ab_co:.3f}->{tp_co:.3f} | CC {ab_cc:.3f}->{tp_cc:.3f} | "
                 f"ref-acc {ab_ref:.3f}->{tp_ref:.3f} | RELF1 {ab_relf1:.3f}->{tp_relf1:.3f}"),
        elapsed_s=round(elapsed, 2),
        ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
        seed=SEED,
        bands=dict(CO_RISE_MIN=CO_RISE_MIN, REF_RISE_MIN=REF_RISE_MIN,
                   NO_CC_REGRESS_EPS=NO_CC_REGRESS_EPS, TELEMETRY_MIN_MOVE=TELEMETRY_MIN_MOVE),
        telemetry_ok=telemetry_ok, arms_differ_digests=digests,
        targets_ok=targets_ok, targets_detail=targets_detail,
        no_regress_case=dict(passage=pid_n, surf=surf_n, gold=gold_n, pred=no_regress_pred,
                             ok=no_regress_ok),
        arms={name: dict(slices=results[name]["slices"],
                         ref_acc=results[name]["ref_acc"],
                         ref_ok=results[name]["ref_ok"], ref_n=results[name]["ref_n"],
                         relf1_micro_f1=results[name]["relf1"]["micro_f1"],
                         relf1_micro_precision=results[name]["relf1"]["micro_precision"],
                         relf1_micro_recall=results[name]["relf1"]["micro_recall"])
              for name in CONFIGS},
        attribution=dict(
            baseline_raw=dict(CC=slc(raw, "CC"), CO=slc(raw, "CO"), ref_acc=raw["ref_acc"],
                              relf1=raw["relf1"]["micro_f1"], CMP=slc(raw, "CMP"),
                              NC=slc(raw, "NC"), all=raw["slices"]["all"]),
            agreement_baseline=dict(CC=ab_cc, CO=ab_co, ref_acc=ab_ref, relf1=ab_relf1,
                                    CMP=slc(ab, "CMP"), NC=slc(ab, "NC"), all=ab["slices"]["all"]),
            topical=dict(CC=tp_cc, CO=tp_co, ref_acc=tp_ref, relf1=tp_relf1,
                         CMP=slc(tp, "CMP"), NC=slc(tp, "NC"), all=tp["slices"]["all"]),
        ),
        cited_context=dict(prior_cell="0775bc894", vet="a63a1e9670",
                           agreement_baseline_CC=0.600, agreement_baseline_CO=0.333,
                           agreement_baseline_ref_acc=0.765,
                           note="agreement floor CITED (context); this cell RE-MEASURES the floor"),
        reference_detail={name: results[name]["ref_detail"] for name in CONFIGS},
        n_pronouns_scored=ab["ref_n"], n_questions=len(ORC.TEST_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("attribution:", json.dumps(metrics["attribution"], indent=2))
    print("targets_detail:", json.dumps(targets_detail, indent=2))
    print("no_regress:", json.dumps(metrics["no_regress_case"], indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    return build_verdict(OUTPUT_DIR, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
