"""
COREF AGREEMENT + POSSESSIVE FIX: does fixing the overlay AGREEMENT enforcement + the possessive
re-resolution bug move COREF off the floor on REAL 2nd-reader text? Targeted confirm-or-refute of the
diagnosed bottleneck (coref-failure diagnostic 8a6892e25, VET-confirmed redirect chain).

WHY (diagnostic 8a6892e25):
  v4 HARD_FAIL -> oracle-mention test REFUTED mention-detection as the bottleneck (gold mentions did
  not recover coref) -> coref-failure diagnostic categorized the REAL-text coref failures:
    AGREEMENT = 7 (dominant; 10 with number cases), SALIENCE_RANK = 4, SELECTIONAL_PREF = 0.
  ROOT of the AGREEMENT failures: the overlay (hdlab.state_of_mind.WorkingOverlay) as WIRED by the v4
  reader gendered ONLY proper NAMES (common person-nouns gender-unknown), enforced NO animacy, and
  mis-set plural NOUNS to singular so plural pronouns (they/them) collapsed to None. SEPARATELY, a
  POSSESSIVE RE-RESOLUTION bug (the reader re-resolves a possessive pronoun's owner in a second pass
  AFTER the whole sentence -- including the possessive's OWN head noun -- is observed) makes "his
  father" resolve his->father instead of his->owner; that is what zeros the comprehension Qs (v4
  reference-acc 0.548 but CC/CO Q-acc 0.000).

THE TWO FIXES (this cell):
  FIX_AGREEMENT (overlay, opt-in prefer_agreement path -- additive, witness bit-identical):
    (a) GENDER common person-nouns via grounding cues (mother/sister->fem, father/brother->masc ...),
        not just proper names -> he->mother / she->father blocked by the hard compatible() filter;
    (b) ANIMACY: a gendered (he/she) pronoun PREFERS an animate person/animal antecedent when one
        exists (blocks he->wagon);
    (c) NUMBER: recognize plural nouns via POS (NNS/NNPS) so they/them require a PLURAL antecedent
        (kittens/cents stop collapsing to singular);
    (d) prefer a KNOWN-gender match over a gender-UNKNOWN competitor (her->Mary[known-fem] not the
        recent gender-unknown Dash).
  FIX_POSSESSIVE (reader): use the CORRECTLY-TIMED first-pass resolution of a possessive pronoun
    (resolved at its stream position, BEFORE its head noun is observed) for the poss() emission,
    instead of re-resolving after the head noun is in the overlay.

ISOLATE COREF: mention set is FIXED = GOLD (oracle mentions) in every arm (the oracle cell already
proved mentions are near-perfect); the ONE variable across arms is the coref fix, so this measures the
coref machinery, not mention detection. Downstream (learned role-assigner, relation emission, RELF1
scorer, comprehension Q engine) is byte-identical to the oracle/v4 pipeline (imported verbatim).

ARMS (attribution -- one toggle each; can-fail):
  baseline            : current overlay, maintained coref, possessive re-resolution bug  [THE FLOOR]
  fix_agreement_only  : + prefer_agreement (gender/animacy/number/known-match); poss bug PRESENT
  fix_possessive_only : + possessive timing fix; agreement OFF
  fix_both            : + prefer_agreement AND possessive timing fix                     [THE FULL FIX]

DESIGN-GATE (verified at self-test/smoke BEFORE the full run; USER: fair tests every time):
  (1) POSITIVE-CONTROL: baseline arm reproduces the imported oracle extract_passage store BYTE-IDENTICAL
      per passage (proves baseline = the real current-overlay floor, not a strawman);
  (2) REAL baseline (current overlay floor) -- measured, not assumed;
  (3) CAN-FAIL: HARD-FAIL if fix_both leaves CC AND CO at the floor -> agreement/possessive was NOT the
      bottleneck (diagnostic refuted) or salience-rank/deeper dominates -> localize;
  (4) DIFFICULTY-ON: real multi-competitor grade-2 passages (people+animals+names), competitive coref,
      the plural (they/them) cases;
  (5) ONE variable per attribution arm (agreement toggle OR possessive toggle);
  (6) TELEMETRY-SENSITIVE: swapping the config MUST move the metrics (ARMS-MUST-DIFFER hash gate);
  (7) INDEPENDENT gold: coref gold antecedents + comprehension gold hand-annotated by the linguistic
      reading, anti-circular; self-test asserts the gold pronoun sequence matches the tokenizer output;
  (8) determinism OMP=1, fixed seed, sorted(set); overlay witness verify_state_of_mind_overlay.py PASSES.

BRANCHES:
  HARD-PASS = fix_both moves CC AND CO meaningfully OFF the floor + reference-acc rises over baseline
    -> the diagnosed AGREEMENT+POSSESSIVE gap WAS (part of) the bottleneck (empirical confirmation) =
    a real coref-on-real-text improvement (first step of the redirected reader capability).
  HARD-FAIL = CC/CO stay at floor with both fixes -> agreement/possessive was not enough -> SALIENCE_RANK
    (#2) or deeper is next; localize.

Glass-box (grounding-based gender/animacy/number lookup; NO external LLM; NO torch/GPU). Local /
foreground-to-completion. NO push / NO remote-persist. Reported CLAIM-VET-pending (NOT self-declared
chain-grade). Determinism OMP=1, fixed seed.

ANCHOR: coref_agreement_possessive_fix_v1
COREF-DIAGNOSTIC context: 8a6892e25 (VET-confirmed redirect chain).
CORPUS: reuses the oracle cell's REAL McGuffey second-reader passages + gold (verbatim import).
COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic coref/query); wall < 120s; no HD.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - discriminator CAN-FAIL (fix_both can stay at floor)        [design-gate]
# - POSITIVE-CONTROL: baseline reproduces oracle store (tol=0) [reproduce_prior]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay (prefer_agreement path) +
#   the REAL oracle extract pipeline on the REAL passages  [F.1]
# - substrate_signature: binds WorkingOverlay/observe/resolve_pronoun sigs (incl new kwargs)  [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; v4 floor CITED@diagnostic
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

ANCHOR_NAME = "coref_agreement_possessive_fix_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 12345

# ---- Pre-registered bands (set BEFORE the final run; HYPOTHESIZED@this prereg) ----------------------
# Baseline (current overlay + possessive bug) is the FLOOR to beat. CITED context from diagnostic
# 8a6892e25: baseline CC=CO=0.000, reference-acc=0.548. This cell RE-MEASURES the floor (does not
# assume it). fix_both HARD-PASS = CC and CO both move meaningfully off the floor + ref-acc rises.
FIX_CO_OFFFLOOR = 0.34     # fix_both CO must clear ~1/3 (off the 0.000 floor) for HARD-PASS
FIX_CC_OFFFLOOR = 0.20     # fix_both CC must clear this (off the 0.000 floor) for HARD-PASS
REF_ACC_RISE_MIN = 0.05    # fix_both reference-acc must exceed baseline by at least this
STUCK_CC = 0.10            # HARD-FAIL if fix_both CC below this (still at floor)
STUCK_CO = 0.20            # HARD-FAIL if fix_both CO below this (still at floor)
TELEMETRY_MIN_MOVE = 0.05  # swapping baseline->fix_both must move at least one primary metric by this
POSITIVE_CONTROL_TOL = 0   # baseline store must reproduce oracle store BYTE-IDENTICAL

# =======================================================================================
# INDEPENDENT GOLD coref antecedents (hand-annotated by the linguistic reading; anti-circular; NOT
# derived from the extractor). Per passage: ordered (pronoun_surface_lower, gold_head) in TOKEN order
# over the resolvable third-person pronouns (subj/obj + possessive; 1st/2nd person excluded). The
# self-test asserts this ordered surface sequence matches what the tokenizer/clause-splitter actually
# produces for each passage (catches annotation drift). reference-acc = fraction matching gold.
GOLD_ANTECEDENTS = {
    "L5_dogs":  [("his", "dogs"), ("his", "james"), ("he", "james"), ("he", "james")],
    "L5b_dodger": [("he", "dodger")],
    "L18_king": [("he", "kingbird"), ("he", "kingbird"), ("his", "kingbird")],
    "L14_henry": [("his", "henry"), ("his", "henry"), ("he", "henry")],
    "L23_doll": [("her", "mary"), ("she", "mary"), ("she", "mary"), ("him", "dash")],
    "L2_cat":   [],
    "L21_bee":  [],
    "L60_geo":  [("he", "george"), ("it", "ball"), ("him", "james")],
    "L28_sam":  [("his", "man"), ("his", "man"), ("him", "man"),
                 ("them", "cents"), ("them", "cents")],
    "L8_puss":  [("her", "puss"), ("them", "kittens")],
    "L26_patty": [("she", "patty"), ("her", "patty")],
    "L57_laura": [("her", "laura"), ("it", "kitten")],
    "L32_tiger": [("she", "tigress"), ("her", "tigress"), ("it", "kitten")],
    "L35_willie": [("his", "willie"), ("his", "willie")],
}

# Third-person resolvable pronouns we score (1st/2nd person excluded -- no discourse antecedent).
_RESOLVABLE_POSS = ORC.PRONOUNS_POSS - {"my", "your", "our"}          # his, her, its, their
_RESOLVABLE_SO = ORC.PRONOUNS_SUBJ_OBJ - {"i", "you", "we", "us", "me"}  # he,him,she,her,it,they,them
_RESOLVABLE = _RESOLVABLE_POSS | _RESOLVABLE_SO


def _agreement_attrs(low, pos, is_name):
    """Grounding-fed agreement attributes for the FIX_AGREEMENT observe path (glass-box; no LLM).
      gender  : names -> curated NAME_GENDER; common nouns -> gendered-noun cue (infer_nominal_gender)
                so mother/sister->fem, father/brother->masc (was None under the v4 wiring).
      number  : POS-driven -- NNS/NNPS -> plural (was mis-set to singular for most plural nouns).
      animacy : grounding category PERSON/ANIMAL -> 'animate', else 'inanimate'."""
    if is_name:
        gender = ORC.NAME_GENDER.get(low, None)
    else:
        gender = infer_nominal_gender([low])   # gendered-noun cue; None when not a gendered noun
    number = "plural" if pos in ("NNS", "NNPS") else "singular"
    animacy = "animate" if ORC.is_animate(low) else "inanimate"
    return gender, number, animacy


def extract_passage_cfg(passage_text, clf, pid, fix_possessive, agreement):
    """Coref pass + role assignment + relation emission on ONE real passage, with the two fixes as
    independent toggles. mention set is FIXED = GOLD (oracle) to isolate coref. Returns
    (sorted_rels, res_by_pos) where res_by_pos[global_token_index] = (pronoun_surface, resolved_head)
    for every third-person pronoun, recording the resolution ACTUALLY USED by this config.

    fix_possessive=False AND agreement=False MUST reproduce ORC.extract_passage byte-identically
    (positive control) -- the baseline arm is the real current-overlay floor."""
    mention_mode = "oracle"
    gold_heads = ORC.GOLD_MENTIONS.get(pid, frozenset())
    coref_strategy = ORC.FIXED_COREF_STRATEGY  # 'maintained' (v4 claim; not tuned)
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
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy, prefer_agreement=pref)
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
                    # BASELINE BUG: re-resolve here, AFTER the whole sentence (incl. the head noun) is
                    # in the overlay -> the head noun often wins (his father -> his->father). Verbatim v4.
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy, prefer_agreement=pref)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                # record the resolution ACTUALLY USED for this possessive (config-dependent)
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
# Arm runner: RELF1 + Q-slices + reference-acc for one config.
# =======================================================================================
CONFIGS = {
    "baseline":            dict(fix_possessive=False, agreement=False),
    "fix_agreement_only":  dict(fix_possessive=False, agreement=True),
    "fix_possessive_only": dict(fix_possessive=True,  agreement=False),
    "fix_both":            dict(fix_possessive=True,  agreement=True),
}


def run_config(cfg_name, clf):
    """Returns dict(store, correct, relf1, slices, ref_acc, ref_detail, answers)."""
    fp = CONFIGS[cfg_name]["fix_possessive"]
    ag = CONFIGS[cfg_name]["agreement"]
    store = {}
    res_by_pos = {}
    for pid, text in ORC.TEST_PASSAGES.items():
        rels, rbp = extract_passage_cfg(text, clf, pid, fp, ag)
        store[pid] = rels
        res_by_pos[pid] = rbp
    # comprehension Qs
    correct = []
    answers = []
    for q in ORC.TEST_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = ORC._relf1_for_store(store)
    slices = ORC._slices(correct)
    # reference-resolution accuracy vs independent gold antecedents
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
# Self-test (design-gate): real code path + positive-control + gold-surface alignment.
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL WorkingOverlay + oracle pipeline ...")
    # F.2 substrate_signature: bind the new kwargs against the live signatures.
    import inspect
    obs_params = set(inspect.signature(WorkingOverlay.observe).parameters)
    assert {"animacy"} <= obs_params, "observe() must accept animacy kwarg"
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement"} <= rp_params, "resolve_pronoun() must accept prefer_agreement kwarg"

    # F.1 real_code_path: exercise the REAL overlay prefer_agreement path on a tiny discourse.
    ov = WorkingOverlay()
    ov.observe("mary", is_proper_name=True, gender="fem", animacy="animate")
    ov.observe("dash", is_proper_name=True, gender=None, animacy="animate")  # gender unknown, recent
    plain = ov.resolve_pronoun("her", strategy="maintained")
    pref = ov.resolve_pronoun("her", strategy="maintained", prefer_agreement=True)
    assert plain is not None and plain.head == "dash", \
        f"baseline maintained should pick recent gender-unknown dash, got {plain and plain.head}"
    assert pref is not None and pref.head == "mary", \
        f"prefer_agreement should pick known-fem mary over unknown dash, got {pref and pref.head}"
    print(f"[self-test] agreement lever fires: her plain->{plain.head} prefer_agreement->{pref.head}")

    # number lever: they/them require a plural antecedent.
    ov2 = WorkingOverlay()
    ov2.observe("cat", gender=None, number="singular", animacy="animate")
    ov2.observe("kittens", gender=None, number="plural", animacy="animate")
    them = ov2.resolve_pronoun("them", strategy="maintained")
    assert them is not None and them.head == "kittens", \
        f"'them' (plural) must resolve to plural kittens not singular cat, got {them and them.head}"
    print(f"[self-test] number lever fires: them->{them.head}")

    # FIT the shared learned role-assigner (REAL training pipeline).
    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    # POSITIVE CONTROL (Gate D reproduce_prior): baseline arm == oracle extract_passage BYTE-IDENTICAL.
    n_pass = 0
    for pid, text in ORC.TEST_PASSAGES.items():
        mine, _ = extract_passage_cfg(text, clf, pid, fix_possessive=False, agreement=False)
        gold_store, _ = ORC.extract_passage(text, "learned", clf, ORC.FIXED_COREF_STRATEGY,
                                             "oracle", ORC.GOLD_MENTIONS.get(pid, frozenset()))
        assert mine == gold_store, (
            f"POSITIVE-CONTROL FAIL {pid}: baseline arm diverges from oracle extract_passage\n"
            f"  mine={mine}\n  oracle={gold_store}")
        n_pass += 1
    print(f"[self-test] POSITIVE-CONTROL: baseline == oracle store byte-identical on {n_pass} passages")

    # GOLD-SURFACE ALIGNMENT: the annotated pronoun surface sequence matches the tokenizer output.
    for pid in ORC.TEST_PASSAGES:
        _, rbp = extract_passage_cfg(ORC.TEST_PASSAGES[pid], clf, pid,
                                     fix_possessive=True, agreement=True)
        pred_surf = [rbp[k][0] for k in sorted(rbp.keys())]
        gold_surf = [s for (s, _h) in GOLD_ANTECEDENTS.get(pid, [])]
        assert pred_surf == gold_surf, (
            f"GOLD-SURFACE MISMATCH {pid}: annotated pronoun sequence != tokenizer output\n"
            f"  gold={gold_surf}\n  pred={pred_surf}")
    print("[self-test] gold pronoun surface sequences match tokenizer output on all passages")

    # determinism: two runs identical.
    r1 = run_config("fix_both", clf)
    r2 = run_config("fix_both", clf)
    assert r1["correct"] == r2["correct"] and r1["ref_acc"] == r2["ref_acc"], "non-deterministic run"
    print("[self-test] deterministic (two fix_both runs identical)")
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

    # ARMS-MUST-DIFFER (telemetry-sensitivity): the four configs must not all be bit-identical.
    digests = _arms_must_differ({name: results[name]["answers"] for name in CONFIGS})

    base = results["baseline"]
    both = results["fix_both"]
    ag = results["fix_agreement_only"]
    po = results["fix_possessive_only"]

    def slc(r, s):
        return r["slices"][s]

    # primary metrics
    base_cc, base_co = slc(base, "CC"), slc(base, "CO")
    both_cc, both_co = slc(both, "CC"), slc(both, "CO")
    base_ref, both_ref = base["ref_acc"], both["ref_acc"]
    base_relf1 = base["relf1"]["micro_f1"]
    both_relf1 = both["relf1"]["micro_f1"]

    # telemetry-sensitivity
    moves = [abs(both_cc - base_cc), abs(both_co - base_co), abs(both_ref - base_ref),
             abs(both_relf1 - base_relf1), abs(slc(both, "CMP") - slc(base, "CMP"))]
    telemetry_ok = max(moves) >= TELEMETRY_MIN_MOVE

    # verdict logic
    off_floor = (both_cc >= FIX_CC_OFFFLOOR and both_co >= FIX_CO_OFFFLOOR)
    ref_rose = (both_ref - base_ref) >= REF_ACC_RISE_MIN
    stuck = (both_cc < STUCK_CC and both_co < STUCK_CO)

    if not telemetry_ok:
        verdict = "INVALID_TELEMETRY_INSENSITIVE"
        vmsg = (f"config swap moved primary metrics < {TELEMETRY_MIN_MOVE} "
                f"(max move {max(moves):.3f}); mechanism vacuous")
    elif off_floor and ref_rose:
        verdict = "HARD_PASS_COREF_OFF_FLOOR"
        vmsg = (f"fix_both moved coref OFF the floor: CC {base_cc:.3f}->{both_cc:.3f}, "
                f"CO {base_co:.3f}->{both_co:.3f}, ref-acc {base_ref:.3f}->{both_ref:.3f}; "
                f"agreement+possessive gap WAS (part of) the bottleneck")
    elif stuck:
        verdict = "HARD_FAIL_COREF_STILL_STUCK"
        vmsg = (f"fix_both left coref at floor: CC={both_cc:.3f} CO={both_co:.3f} "
                f"(base CC={base_cc:.3f} CO={base_co:.3f}); agreement+possessive not enough "
                f"-> salience-rank(#2)/deeper is next; localize")
    else:
        verdict = "PARTIAL_COREF_MOVED"
        vmsg = (f"fix_both moved coref but did not clear both bands: CC {base_cc:.3f}->{both_cc:.3f} "
                f"(need>={FIX_CC_OFFFLOOR}), CO {base_co:.3f}->{both_co:.3f} (need>={FIX_CO_OFFFLOOR}), "
                f"ref-acc {base_ref:.3f}->{both_ref:.3f}; localize residual")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: CC {base_cc:.3f}->{both_cc:.3f} | CO {base_co:.3f}->{both_co:.3f} | "
                 f"ref-acc {base_ref:.3f}->{both_ref:.3f} | RELF1 {base_relf1:.3f}->{both_relf1:.3f}"),
        elapsed_s=round(elapsed, 2),
        ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
        seed=SEED,
        bands=dict(FIX_CC_OFFFLOOR=FIX_CC_OFFFLOOR, FIX_CO_OFFFLOOR=FIX_CO_OFFFLOOR,
                   REF_ACC_RISE_MIN=REF_ACC_RISE_MIN, STUCK_CC=STUCK_CC, STUCK_CO=STUCK_CO,
                   TELEMETRY_MIN_MOVE=TELEMETRY_MIN_MOVE),
        telemetry_ok=telemetry_ok, arms_differ_digests=digests,
        # per-config headline metrics
        arms={name: dict(slices=results[name]["slices"],
                         ref_acc=results[name]["ref_acc"],
                         ref_ok=results[name]["ref_ok"], ref_n=results[name]["ref_n"],
                         relf1_micro_f1=results[name]["relf1"]["micro_f1"],
                         relf1_micro_precision=results[name]["relf1"]["micro_precision"],
                         relf1_micro_recall=results[name]["relf1"]["micro_recall"])
              for name in CONFIGS},
        # attribution (agreement alone vs possessive alone vs both)
        attribution=dict(
            baseline=dict(CC=base_cc, CO=base_co, ref_acc=base_ref, relf1=base_relf1,
                          CMP=slc(base, "CMP"), NC=slc(base, "NC"), all=base["slices"]["all"]),
            fix_agreement_only=dict(CC=slc(ag, "CC"), CO=slc(ag, "CO"), ref_acc=ag["ref_acc"],
                                    relf1=ag["relf1"]["micro_f1"], CMP=slc(ag, "CMP"),
                                    NC=slc(ag, "NC"), all=ag["slices"]["all"]),
            fix_possessive_only=dict(CC=slc(po, "CC"), CO=slc(po, "CO"), ref_acc=po["ref_acc"],
                                     relf1=po["relf1"]["micro_f1"], CMP=slc(po, "CMP"),
                                     NC=slc(po, "NC"), all=po["slices"]["all"]),
            fix_both=dict(CC=both_cc, CO=both_co, ref_acc=both_ref, relf1=both_relf1,
                          CMP=slc(both, "CMP"), NC=slc(both, "NC"), all=both["slices"]["all"]),
        ),
        cited_context=dict(diagnostic="8a6892e25", v4_reference_acc=0.548, v4_CC=0.0, v4_CO=0.0,
                           note="v4/diagnostic floor CITED (context); this cell RE-MEASURES the floor"),
        reference_detail={name: results[name]["ref_detail"] for name in CONFIGS},
        n_pronouns_scored=base["ref_n"], n_questions=len(ORC.TEST_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("attribution:", json.dumps(metrics["attribution"], indent=2))
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
