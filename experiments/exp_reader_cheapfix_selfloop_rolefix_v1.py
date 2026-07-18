"""
CHEAP READER WINS (VET-triaged): (1) DEGENERATE SELF-LOOP emission guard + (2) ROLE-ASSIGNER
sheep->RECIPIENT frame fix. Capture the cheap foundation-precision + coverage gains the oracle
upper-bound (b85422616 / VET a220d138) bounded, BEFORE the bigger parser build (NP-head /
clause-seg / argument-structure = deferred to USER steer).

WHAT (two cheap fixes, glass-box, on the VET-confirmed grade-3 reader; envelope 00c6688b6):
  FIX #1 SELF-LOOP GUARD (trivial precision): drop at emission ANY relation whose two ENTITY args
    are IDENTICAL -- poss(X,X), svo(V,X,X), loc(X,X), recipient(V,X,X). The baseline reader emits
    junk self-loops (svo(came,man,man), svo(lifting,george,george)); these are always FALSE
    POSITIVES (COMPLETE_TRUTH contains NO self-loop), so the guard can only raise strict precision.
  FIX #2 ROLE-ASSIGNER RECIPIENT REPAIR (glass-box frame rule): the learned averaged-perceptron
    over-weights `far_from_verb` and mislabels a plain post-verbal object as RECIPIENT
    ("killed a great many sheep" -> sheep=RECIPIENT; "admiring his friend's horse" -> horse=
    RECIPIENT). Repair (post-classifier, fully inspectable): a candidate labeled RECIPIENT is a
    genuine recipient ONLY IF (a) governed by a dative "to" preposition, OR (b) it fills the
    canonical double-object slot (immediately after the verb WITH a later PATIENT). Otherwise a
    post-verbal object -- with no intervening finite verb/modal (same clause) -- is the direct
    object => demote to PATIENT. Fixes the underlying FRAME cue, not the word "sheep"; the
    same-clause guard leaves genuine cross-clause subjects ("...he said...How much mother would
    like...") untouched, so it introduces no new false patients.

ARMS (ONE variable per arm; mention_mode=handrule for ALL -> the REAL reader, NOT oracle-injected;
downstream emission/coref/answer-engine byte-identical except the one toggle):
  baseline             : self_loop=F role_fix=F inject=none  [FLOOR / positive control -> byte-
                                                              reproduces the envelope 3rd store]
  self_loop            : self_loop=T role_fix=F inject=none   [precision fix in isolation]
  role_fix             : self_loop=F role_fix=T inject=none   [role fix in isolation]
  both                 : self_loop=T role_fix=T inject=none   [the two CHEAP wins together]
  both_plus_goldclause : self_loop=T role_fix=T inject=GOLD   [DIAGNOSTIC CEILING: the two cheap
                                                              fixes + the DEFERRED clause-seg gold
                                                              shared-subject signal (ORA.INJECT_SUBJ)
                                                              -> confirms role_fix is the necessary
                                                              2nd ingredient for N5 once the orphaned
                                                              wolf-agent is restored. NOT a cheap win;
                                                              uses a deferred-workstream oracle signal.]

MEASURE per arm: foundation strict PRECISION + fp_rate (INDEPENDENT COMPLETE_TRUTH, reused verbatim
from the oracle cell -- same annotation, non-circular) + which relations each fix removes/adds;
RELF1 micro P/R/F1; N5 relation-level recovery (svo(killed,wolf,sheep) in store) AND N5 comprehension
answer; comprehension all/NC/CO/CMP; ref_acc. Attribution: self-loop -> which FPs removed; role-fix
-> which relations changed; joint -> N5.

REGRESSION GUARD (the role fix must not break the VET-confirmed role behavior):
  - ORC.score_passive(role_fixed_assigner) == 1.00 and ORC.score_reversal(role_fixed_assigner) == 1.00
    (passive subject=PATIENT/by-NP=AGENT; dative + double-object recipients preserved).
  - ref_acc IDENTICAL across all arms (neither fix touches coref).
  - the packaged state-of-mind overlay witness (verification/verify_state_of_mind_overlay.py) exits 0.

BRANCHES (decisive, genuinely can-fail):
  CHEAP_WINS_CAPTURED = self-loop lifts strict precision (removing only FPs) AND role_fix recovers a
                        true relation with NO passive/reversal/coref regression AND the joint arm
                        recovers N5 (svo(killed,wolf,sheep)) -> both cheap wins real; role_fix is the
                        necessary 2nd ingredient once clause-seg restores the agent.
  PARTIAL_LOCALIZED   = self-loop precision win holds, but role_fix does NOT recover N5 on the pure
                        handrule reader (the "killed" clause is orphaned of its wolf subject = the
                        DEFERRED clause-seg workstream, NOT the role fix) -> localize: N5 needs
                        clause-seg + role_fix JOINTLY; deflate the "role-fix -> recall" expectation.
  REGRESSION          = a fix regresses a control (passive/reversal/coref down, or self-loop drops a
                        TRUE relation) -> the fix is more than a cheap tweak; localize + revert.

FAIRNESS / anti-circular (design-gate; USER: fair tests every time):
  - Same REAL grade-3 McGuffey passages + independent gold, imported VERBATIM from the envelope cell.
  - COMPLETE_TRUTH (precision eval) reused verbatim from the oracle cell -- SEPARATE from any fix.
  - baseline arm byte-reproduces ENV.extract_passage_ds (anti-copy-divergence self-test, 11 passages).
  - self-loop guard removes ONLY relations with identical entity args (asserted: no TRUE relation is a
    self-loop -> the guard cannot drop a true relation).
  - role_fix only DEMOTES RECIPIENT->PATIENT under the frame rule; genuine recipients (to-dative +
    double-object) preserved (regression guard).
  - Determinism OMP=1, fixed seed, sorted(set).

Glass-box (POS + averaged perceptron + symbolic coref/query; NO external LLM; NO torch/GPU at
runtime). Local / foreground-to-completion. NO push / NO remote-persist. CLAIM-VET-pending (NOT
self-declared chain-grade); strategic read = hypothesis pending landed-VET.

ANCHOR: reader_cheapfix_selfloop_rolefix_v1
BASELINE: envelope 3rd-reader store (commit 00c6688b6; VET a7ecb244). COMPUTE: sequential-CPU; wall < 90s.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                        [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                                  [META_RULE_AF]
# - discriminator CAN-FAIL (role_fix could regress passive/reversal; self-loop could drop a TP)
# - POSITIVE-CONTROL: baseline byte-reproduces the envelope 3rd store    [reproduce_prior / Gate D]
# - anti-copy-divergence: my extract == ENV.extract_passage_ds byte-identical at baseline config [F.1]
# - deterministic seeding (fixed int seed, fixed order, sorted set)      [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL perceptron + REAL POS tagger + REAL
#   overlay on REAL 3rd-reader passages; runs the REAL passive/reversal role controls           [F.1]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - all reported numbers MEASURED@this metrics.json; envelope floor CITED@envelope metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
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
import subprocess
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the confirmed reader pipeline + the REAL 3rd-reader passages/gold + the independent
# COMPLETE_TRUTH annotation, all VERBATIM (NOT re-authored).
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_mention_source_gold_vs_handrule_corefixed_v1 as CFX  # noqa: E402
from experiments import exp_reader_grade3_envelope_readtogrow_v1 as ENV         # noqa: E402
from experiments import exp_reader_oracle_parser_upperbound_v1 as ORA           # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE      # noqa: E402

_prefers_topical = CFX._prefers_topical
_agreement_attrs = CFX._agreement_attrs
_RESOLVABLE = CFX._RESOLVABLE
_RESOLVABLE_SO = CFX._RESOLVABLE_SO
_RESOLVABLE_POSS = CFX._RESOLVABLE_POSS

ANCHOR_NAME = "reader_cheapfix_selfloop_rolefix_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 12345

# REAL 3rd-reader passages + independent gold, imported VERBATIM.
G3_PASSAGES = ENV.G3_PASSAGES
G3_GOLD_RELS = ENV.G3_GOLD_RELS
G3_GOLD_ANTECEDENTS = ENV.G3_GOLD_ANTECEDENTS
G3_QS = ENV.G3_QS

# INDEPENDENT per-relation truth (precision eval) + the deferred clause-seg gold signal, reused
# verbatim from the oracle cell (same annotation; non-circular; already SCHEMA-VET'd there).
COMPLETE_TRUTH = ORA.COMPLETE_TRUTH
_TRUTH_UNION = ORA._TRUTH_UNION
INJECT_SUBJ = ORA.INJECT_SUBJ            # {passage: {orphaned-clause-substring: gold shared subject}}

# The N5 target relation (wolf-killed-sheep) + its passage.
N5_PID = "L13_wolf2"
N5_REL = ("svo", "killed", "wolf", "sheep")

# ---- Envelope floor (CITED@ENV metrics arms.third_reader; positive control) ----------------------
FLOOR = dict(all=0.7333, NC=0.8333, CO=0.8333, CMP=0.3333, ref_acc=0.8333,
             RELF1_recall=0.8, RELF1_f1=0.522, n_relations=36, qLB=0.387)
FLOOR_STRICT_PREC_LO = 0.40   # independent strict precision reproduces the VET ~0.44-0.47
FLOOR_STRICT_PREC_HI = 0.55

# ---- Pre-registered bands (HYPOTHESIZED@this cell; set BEFORE the final run; can-fail) ------------
SELF_LOOP_MIN_REMOVED = 1     # self-loop guard must remove >= 1 degenerate FP on these passages
ROLE_FIX_MIN_CHANGED = 1      # role_fix must change >= 1 emitted relation (telemetry-sensitive)
PASSIVE_FLOOR = 1.0           # role_fix must NOT regress the passive control (VET 1.00)
REVERSAL_FLOOR = 1.0          # role_fix must NOT regress the reversal control (VET 1.00)


# =======================================================================================
# FIX #2 -- glass-box RECIPIENT frame repair (post-classifier; fully inspectable).
# =======================================================================================
_VERB_POS = ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "MD")


def apply_role_fix(tagged, roles, verb_idx, cand):
    """Demote a mislabeled RECIPIENT to PATIENT under the frame rule. A candidate labeled RECIPIENT
    is a genuine recipient ONLY IF (a) governed by dative 'to', OR (b) canonical double-object slot
    (immediately after the verb WITH a later PATIENT). Otherwise a same-clause post-verbal object is
    the direct object -> PATIENT. Same-clause = no intervening finite verb/modal between the main verb
    and the candidate (a cross-clause subject like 'mother' in '...he said...mother would like...' is
    left untouched -> no new false patient)."""
    if verb_idx is None:
        return roles
    roles = dict(roles)
    patients = [j for j in cand if roles.get(j) == "PATIENT"]
    for i in cand:
        if roles.get(i) != "RECIPIENT":
            continue
        pp = ORC.prev_prep(tagged, i)
        if pp in ORC.PREP_TO:
            continue  # (a) genuine dative recipient
        adjacent = (i == verb_idx + 1)
        later_patient = any(j > i for j in patients)
        if adjacent and later_patient:
            continue  # (b) canonical double-object recipient (V recip patient)
        lo, hi = (verb_idx, i) if i > verb_idx else (i, verb_idx)
        intervening_verb = any(tagged[k][2] in _VERB_POS for k in range(lo + 1, hi))
        if intervening_verb:
            continue  # candidate belongs to another clause -> not this verb's argument; leave it
        roles[i] = "PATIENT"
    return roles


# =======================================================================================
# FIX #1 -- degenerate self-loop guard (drop relations with identical entity args).
# =======================================================================================
def is_self_loop(r):
    """True if relation r has two IDENTICAL entity arguments (poss/loc = args[1:3]; svo/recipient =
    agent/patient at [2:4]). attr = ('attr', head, color, 'COLOR') is NOT entity-entity -> never a loop."""
    kind = r[0]
    if kind in ("svo", "recipient"):
        return r[2] == r[3]
    if kind in ("loc", "poss"):
        return r[1] == r[2]
    return False


# =======================================================================================
# Fixed-toggle extract: EXACT copy of ENV.extract_passage_ds (byte-identity asserted at baseline
# config) + (i) optional shared-subject prepend on the orphaned clauses in inject_map, (ii) optional
# role_fix on the assigned roles, (iii) optional self-loop guard at emission. mention_mode=handrule
# throughout (NO gold heads -- that is the separate deferred NP-head workstream).
# =======================================================================================
def extract_passage_fixed(passage_text, clf, pid, passages_dict, mention_mode, inject_map,
                          role_fix, self_loop_guard):
    """ENV.extract_passage_ds body + the two cheap fixes (+ optional gold shared-subject inject).
    Returns (sorted_rels, res_by_pos, removed_self_loops)."""
    gold_heads = frozenset()
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    fix_possessive = True
    agreement = True
    topical = True
    pref = bool(agreement)
    injects = (inject_map or {}).get(pid, {})

    known = set()
    for txt in list(passages_dict.values()):
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
        # optional gold shared-subject prepend (DIAGNOSTIC arm only; boundary unchanged; ONE token).
        subj = injects.get(sent.strip())
        if subj is not None:
            tagged = [(subj.capitalize(), subj, "NNP")] + tagged
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass
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

        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, gold_heads)
        if role_fix:
            roles = apply_role_fix(tagged, roles, verb_idx, cand)

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

        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
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
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        offset += len(tagged)

    # FIX #1: self-loop guard at emission.
    removed = []
    if self_loop_guard:
        kept = []
        for r in rels:
            if is_self_loop(r):
                removed.append(tuple(r))
            else:
                kept.append(r)
        rels = kept

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    removed = sorted(set(removed), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos, removed


# =======================================================================================
# Run one arm -> store + all scores. Downstream (answer_reader, relf1, slices, ref_acc, foundation,
# strict precision) reuses ENV / ORA helpers verbatim.
# =======================================================================================
def run_arm(clf, role_fix, self_loop_guard, inject_map):
    store, res_by_pos, removed = {}, {}, {}
    for pid, text in G3_PASSAGES.items():
        rels, rbp, rem = extract_passage_fixed(text, clf, pid, G3_PASSAGES, "handrule",
                                               inject_map, role_fix, self_loop_guard)
        store[pid] = rels
        res_by_pos[pid] = rbp
        removed[pid] = rem
    correct, answers = [], []
    for q in G3_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = ENV._relf1_g3(store)
    slices = ENV._slices_g3(correct)
    n_tot = n_ok = 0
    for pid in G3_PASSAGES:
        gold = G3_GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    fnd = ENV.build_foundation(store)
    strict = ORA._strict_precision(store)
    n5_relation = tuple(N5_REL) in set(tuple(r) for r in store[N5_PID])
    n5_answer = None
    for i, q in enumerate(G3_QS):
        if q["qid"] == "N5":
            n5_answer = bool(correct[i])
            break
    n_removed = sum(len(removed[pid]) for pid in G3_PASSAGES)
    removed_flat = sorted(set(tuple(r) for pid in G3_PASSAGES for r in removed[pid]),
                          key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return dict(store=store, correct=correct, answers=answers, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_ok=n_ok, ref_n=n_tot, foundation=fnd, strict=strict,
                removed_self_loops=[list(r) for r in removed_flat], n_removed=n_removed,
                n5_relation=n5_relation, n5_answer=n5_answer,
                per_q=[dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=answers[i],
                            ok=bool(correct[i])) for i, q in enumerate(G3_QS)])


# =======================================================================================
# Regression controls (role fix must not break the VET-confirmed role behavior).
# =======================================================================================
def _make_assigner(clf, role_fix):
    def a(tagged):
        roles, vi, v, ps, cand = ORC.assign_roles_learned(tagged, clf, "handrule", frozenset())
        if role_fix:
            roles = apply_role_fix(tagged, roles, vi, cand)
        return roles, vi, v, ps, cand
    return a


def _role_controls(clf):
    pass_base, _ = ORC.score_passive(_make_assigner(clf, False))
    pass_fix, pass_per = ORC.score_passive(_make_assigner(clf, True))
    rev_base, _ = ORC.score_reversal(_make_assigner(clf, False))
    rev_fix, rev_per = ORC.score_reversal(_make_assigner(clf, True))
    return dict(passive_baseline=round(pass_base, 4), passive_rolefix=round(pass_fix, 4),
                reversal_baseline=round(rev_base, 4), reversal_rolefix=round(rev_fix, 4),
                passive_per=pass_per, reversal_per=rev_per)


def _run_overlay_witness():
    """Run the packaged state-of-mind overlay witness as a subprocess; return (ok, tail)."""
    path = os.path.join(REPO, "verification", "verify_state_of_mind_overlay.py")
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=180)
        tail = (p.stdout + p.stderr).strip().splitlines()
        return (p.returncode == 0), (tail[-1] if tail else "")
    except Exception as e:  # subprocess failure is a reportable regression-check failure, not a crash
        return False, f"{type(e).__name__}: {str(e)[:200]}"


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


def _fit_clf():
    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)
    return clf


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL reader pipeline (WorkingOverlay + perceptron + POS tagger) ...")
    import inspect
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement", "prefer_topical"} <= rp_params, "resolve_pronoun sig drift (F.2)"
    clf = _fit_clf()

    # (F.1) ANTI-COPY-DIVERGENCE: baseline config (no fixes, no inject) == ENV.extract_passage_ds
    # byte-identical on the REAL 3rd-reader passages.
    for pid, text in G3_PASSAGES.items():
        mine, mrbp, mrem = extract_passage_fixed(text, clf, pid, G3_PASSAGES, "handrule", {},
                                                 role_fix=False, self_loop_guard=False)
        ref, rrbp = ENV.extract_passage_ds(text, clf, pid, G3_PASSAGES,
                                           {p: frozenset() for p in G3_PASSAGES},
                                           True, True, True, "handrule")
        assert mine == ref, f"COPY-DIVERGENCE {pid}:\n {mine}\n {ref}"
        assert mrbp == rrbp, f"COPY-DIVERGENCE res_by_pos {pid}"
        assert mrem == [], f"baseline emitted removals unexpectedly {pid}: {mrem}"
    print("[self-test] anti-copy-divergence: baseline == ENV.extract_passage_ds on 11 passages")

    # POSITIVE CONTROL: baseline reproduces the envelope floor + strict precision ~VET.
    base = run_arm(clf, role_fix=False, self_loop_guard=False, inject_map={})
    assert base["foundation"]["n_relations"] == FLOOR["n_relations"], \
        f"POS-CTRL n_rel {base['foundation']['n_relations']} != {FLOOR['n_relations']}"
    assert abs(base["foundation"]["quality_precision_lower_bound"] - FLOOR["qLB"]) <= 0.002, "POS-CTRL qLB"
    assert abs(base["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002, "POS-CTRL CMP"
    assert abs(base["ref_acc"] - FLOOR["ref_acc"]) <= 0.002, "POS-CTRL ref_acc"
    assert abs(base["relf1"]["micro_recall"] - FLOOR["RELF1_recall"]) <= 0.01, "POS-CTRL RELF1 recall"
    sp = base["strict"]["strict_precision"]
    assert FLOOR_STRICT_PREC_LO <= sp <= FLOOR_STRICT_PREC_HI, \
        f"POS-CTRL strict precision {sp:.3f} not in [{FLOOR_STRICT_PREC_LO},{FLOOR_STRICT_PREC_HI}]"
    assert not base["n5_relation"], "POS-CTRL: baseline unexpectedly already has N5 relation"
    print(f"[self-test] POS-CTRL: baseline reproduces envelope (n_rel={base['foundation']['n_relations']} "
          f"qLB={base['foundation']['quality_precision_lower_bound']:.3f} CMP={base['slices']['CMP']:.3f} "
          f"ref={base['ref_acc']:.3f} RELF1r={base['relf1']['micro_recall']:.3f}); strict prec {sp:.3f}; N5 missing")
    print(f"[self-test]   baseline FP relations ({base['strict']['fp']}): {base['strict']['fp_relations']}")

    # FIX #1: self-loop guard removes >=1 relation, ALL removed are self-loops AND FPs (never a TP).
    sl = run_arm(clf, role_fix=False, self_loop_guard=True, inject_map={})
    assert sl["n_removed"] >= SELF_LOOP_MIN_REMOVED, f"self-loop removed {sl['n_removed']} < {SELF_LOOP_MIN_REMOVED}"
    for r in sl["removed_self_loops"]:
        assert is_self_loop(tuple(r)), f"removed non-self-loop {r}"
        assert tuple(r) not in _TRUTH_UNION, f"self-loop guard dropped a TRUE relation {r} (REGRESSION)"
    assert sl["strict"]["strict_precision"] > sp, "self-loop guard did not raise strict precision"
    print(f"[self-test] FIX#1 self-loop: removed {sl['n_removed']} self-loops {sl['removed_self_loops']}; "
          f"strict prec {sp:.3f}->{sl['strict']['strict_precision']:.3f} (only FPs removed)")

    # FIX #2: role_fix changes >=1 relation AND does NOT regress passive/reversal.
    rf = run_arm(clf, role_fix=True, self_loop_guard=False, inject_map={})
    base_set = set(tuple(r) for pid in G3_PASSAGES for r in base["store"][pid])
    rf_set = set(tuple(r) for pid in G3_PASSAGES for r in rf["store"][pid])
    changed = base_set ^ rf_set
    assert len(changed) >= ROLE_FIX_MIN_CHANGED, f"role_fix changed {len(changed)} < {ROLE_FIX_MIN_CHANGED} (telemetry)"
    ctrl = _role_controls(clf)
    assert ctrl["passive_baseline"] == PASSIVE_FLOOR, f"passive baseline {ctrl['passive_baseline']} != {PASSIVE_FLOOR}"
    assert ctrl["reversal_baseline"] == REVERSAL_FLOOR, f"reversal baseline {ctrl['reversal_baseline']} != {REVERSAL_FLOOR}"
    assert ctrl["passive_rolefix"] >= PASSIVE_FLOOR, f"role_fix REGRESSED passive {ctrl['passive_rolefix']}"
    assert ctrl["reversal_rolefix"] >= REVERSAL_FLOOR, f"role_fix REGRESSED reversal {ctrl['reversal_rolefix']}"
    assert rf["ref_acc"] == base["ref_acc"], f"role_fix moved ref_acc {base['ref_acc']}->{rf['ref_acc']} (coref regression)"
    print(f"[self-test] FIX#2 role_fix: changed {len(changed)} relations {sorted(changed)}; "
          f"passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} (no regression); "
          f"N5-relation(rolefix-alone)={rf['n5_relation']}")

    # DIAGNOSTIC: both cheap fixes + gold clause-seg -> confirm N5 recovers jointly.
    both = run_arm(clf, role_fix=True, self_loop_guard=True, inject_map={})
    joint = run_arm(clf, role_fix=True, self_loop_guard=True, inject_map=INJECT_SUBJ)
    assert joint["ref_acc"] == base["ref_acc"], "joint arm moved ref_acc (coref regression)"
    print(f"[self-test] DIAGNOSTIC joint (both + gold clause-seg): N5-relation={joint['n5_relation']} "
          f"N5-answer={joint['n5_answer']} strict prec={joint['strict']['strict_precision']:.3f}")

    # ARMS-MUST-DIFFER on the 5 stores.
    _arms_must_differ({k: {p: [list(r) for r in v["store"][p]] for p in G3_PASSAGES}
                       for k, v in dict(baseline=base, self_loop=sl, role_fix=rf,
                                        both=both, both_plus_goldclause=joint).items()})

    # determinism
    rf2 = run_arm(clf, role_fix=True, self_loop_guard=False, inject_map={})
    assert rf2["strict"] == rf["strict"] and rf2["correct"] == rf["correct"], "non-deterministic"

    # overlay witness (coref machinery intact -- neither fix touches hdlab.state_of_mind).
    ok, tail = _run_overlay_witness()
    assert ok, f"overlay witness FAILED: {tail}"
    print(f"[self-test] overlay witness PASS: {tail}")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=5)
    clf = _fit_clf()

    base = run_arm(clf, role_fix=False, self_loop_guard=False, inject_map={})
    sl = run_arm(clf, role_fix=False, self_loop_guard=True, inject_map={})
    rf = run_arm(clf, role_fix=True, self_loop_guard=False, inject_map={})
    both = run_arm(clf, role_fix=True, self_loop_guard=True, inject_map={})
    joint = run_arm(clf, role_fix=True, self_loop_guard=True, inject_map=INJECT_SUBJ)
    arms = dict(baseline=base, self_loop=sl, role_fix=rf, both=both, both_plus_goldclause=joint)

    digests = _arms_must_differ({k: {p: [list(r) for r in v["store"][p]] for p in G3_PASSAGES}
                                 for k, v in arms.items()})
    ctrl = _role_controls(clf)
    witness_ok, witness_tail = _run_overlay_witness()

    def _sp(a): return a["strict"]["strict_precision"]

    b_prec = _sp(base)
    # positive control
    pc_ok = (base["foundation"]["n_relations"] == FLOOR["n_relations"] and
             abs(base["foundation"]["quality_precision_lower_bound"] - FLOOR["qLB"]) <= 0.002 and
             abs(base["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002 and
             abs(base["ref_acc"] - FLOOR["ref_acc"]) <= 0.002 and
             abs(base["relf1"]["micro_recall"] - FLOOR["RELF1_recall"]) <= 0.01 and
             FLOOR_STRICT_PREC_LO <= b_prec <= FLOOR_STRICT_PREC_HI and not base["n5_relation"])

    # attribution
    selfloop_removed = sl["removed_self_loops"]
    selfloop_all_fp = all(tuple(r) not in _TRUTH_UNION for r in selfloop_removed)
    selfloop_prec_gain = round(_sp(sl) - b_prec, 4)
    base_set = set(tuple(r) for pid in G3_PASSAGES for r in base["store"][pid])
    rf_set = set(tuple(r) for pid in G3_PASSAGES for r in rf["store"][pid])
    rolefix_added = sorted(rf_set - base_set, key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    rolefix_removed = sorted(base_set - rf_set, key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    rolefix_added_tp = [list(r) for r in rolefix_added if r in _TRUTH_UNION]
    rolefix_added_fp = [list(r) for r in rolefix_added if r not in _TRUTH_UNION]
    rolefix_prec_delta = round(_sp(rf) - b_prec, 4)

    passive_ok = ctrl["passive_rolefix"] >= PASSIVE_FLOOR
    reversal_ok = ctrl["reversal_rolefix"] >= REVERSAL_FLOOR
    coref_ok = (rf["ref_acc"] == base["ref_acc"] and both["ref_acc"] == base["ref_acc"] and
                joint["ref_acc"] == base["ref_acc"])
    no_regression = passive_ok and reversal_ok and coref_ok and witness_ok

    selfloop_win = (sl["n_removed"] >= SELF_LOOP_MIN_REMOVED and selfloop_all_fp and selfloop_prec_gain > 0)
    n5_rolefix_alone = rf["n5_relation"]
    n5_joint = joint["n5_relation"]

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"baseline did NOT reproduce the envelope floor (n_rel={base['foundation']['n_relations']} "
                f"qLB={base['foundation']['quality_precision_lower_bound']:.3f} CMP={base['slices']['CMP']:.3f} "
                f"ref={base['ref_acc']:.3f} RELF1r={base['relf1']['micro_recall']:.3f} strict={b_prec:.3f} "
                f"N5={base['n5_relation']}); one-variable basis broken.")
    elif not no_regression:
        verdict = "REGRESSION"
        vmsg = (f"a fix regressed a confirmed control: passive {ctrl['passive_rolefix']:.2f} (base "
                f"{ctrl['passive_baseline']:.2f}) reversal {ctrl['reversal_rolefix']:.2f} (base "
                f"{ctrl['reversal_baseline']:.2f}) coref_ok={coref_ok} overlay_witness={witness_ok}. The role "
                f"fix is more than a cheap frame tweak -- revert + localize.")
    elif selfloop_win and n5_joint and not n5_rolefix_alone:
        verdict = "PARTIAL_LOCALIZED"
        vmsg = (f"CHEAP PRECISION WIN CAPTURED + N5 RECALL LOCALIZED TO THE DEFERRED CLAUSE-SEG. Self-loop "
                f"guard removes {sl['n_removed']} degenerate FPs {selfloop_removed} -> strict precision "
                f"{b_prec:.3f}->{_sp(sl):.3f} (all removed are FPs). Role fix corrects the RECIPIENT frame "
                f"with NO passive/reversal/coref regression (passive {ctrl['passive_rolefix']:.2f} reversal "
                f"{ctrl['reversal_rolefix']:.2f}) and adds true relation(s) {rolefix_added_tp} (strict prec "
                f"{b_prec:.3f}->{_sp(rf):.3f}). BUT role fix ALONE does NOT recover N5 (svo killed wolf sheep): "
                f"on the pure hand-rule reader the 'killed a great many sheep' clause is ORPHANED of its wolf "
                f"subject (the DEFERRED clause-seg workstream), so there is no agent to emit svo(killed,wolf,*). "
                f"The DIAGNOSTIC joint arm (both fixes + gold shared-subject) recovers N5-relation={n5_joint} "
                f"(N5-answer={joint['n5_answer']}), CONFIRMING role fix is the necessary 2nd ingredient once "
                f"clause-seg restores the agent -- the two are jointly load-bearing for N5. HYPOTHESIS pending-"
                f"VET: self-loop = cheap precision win (captured); role fix = correct + necessary but its N5 "
                f"RECALL payoff is GATED behind clause-seg. Deflate the drill's 'role-fix -> N5 recall' -> not "
                f"on the pure reader; needs clause-seg + role-fix jointly.")
    elif selfloop_win and n5_rolefix_alone:
        verdict = "CHEAP_WINS_CAPTURED"
        vmsg = (f"BOTH cheap wins captured. Self-loop guard removes {sl['n_removed']} FPs {selfloop_removed} "
                f"(strict precision {b_prec:.3f}->{_sp(sl):.3f}); role fix recovers N5 (svo killed wolf sheep) "
                f"AND adds {rolefix_added_tp} with NO passive/reversal/coref regression. Both cheap, real, "
                f"attributable.")
    else:
        verdict = "PARTIAL"
        vmsg = (f"SPLIT. self-loop precision win={selfloop_win} (removed {sl['n_removed']} FPs, prec "
                f"{b_prec:.3f}->{_sp(sl):.3f}); role fix N5-alone={n5_rolefix_alone} joint-N5={n5_joint}; "
                f"added TP {rolefix_added_tp} FP {rolefix_added_fp}. See attribution + arms.")

    def _arm_summary(a):
        return dict(slices=a["slices"], ref_acc=a["ref_acc"], ref_ok=a["ref_ok"], ref_n=a["ref_n"],
                    relf1_micro_f1=a["relf1"]["micro_f1"], relf1_micro_precision=a["relf1"]["micro_precision"],
                    relf1_micro_recall=a["relf1"]["micro_recall"],
                    foundation_n_relations=a["foundation"]["n_relations"],
                    foundation_n_entities=a["foundation"]["n_entities"],
                    foundation_quality_lb=a["foundation"]["quality_precision_lower_bound"],
                    strict=a["strict"], n5_relation=a["n5_relation"], n5_answer=a["n5_answer"],
                    removed_self_loops=a["removed_self_loops"], per_q=a["per_q"])

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: strict_prec base {b_prec:.3f} -> self_loop {_sp(sl):.3f} -> role_fix {_sp(rf):.3f} "
                 f"-> both {_sp(both):.3f} | N5-relation base={base['n5_relation']} role_fix={rf['n5_relation']} "
                 f"both={both['n5_relation']} joint(+goldclause)={joint['n5_relation']} | passive "
                 f"{ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} coref_ok={coref_ok} "
                 f"overlay={witness_ok}"),
        elapsed_s=round(elapsed, 2), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        one_variable="two cheap fixes toggled independently (self-loop guard / RECIPIENT frame repair); "
                     "mention_mode=handrule + downstream byte-identical; joint arm adds deferred gold clause-seg",
        positive_control_ok=pc_ok,
        regression=dict(passive_baseline=ctrl["passive_baseline"], passive_rolefix=ctrl["passive_rolefix"],
                        reversal_baseline=ctrl["reversal_baseline"], reversal_rolefix=ctrl["reversal_rolefix"],
                        passive_ok=passive_ok, reversal_ok=reversal_ok, coref_ok=coref_ok,
                        overlay_witness_ok=witness_ok, overlay_witness_tail=witness_tail,
                        no_regression=no_regression, passive_per=ctrl["passive_per"],
                        reversal_per=ctrl["reversal_per"]),
        attribution=dict(
            selfloop_removed=selfloop_removed, selfloop_n_removed=sl["n_removed"],
            selfloop_all_removed_are_fp=selfloop_all_fp, selfloop_precision_gain=selfloop_prec_gain,
            rolefix_added_true=rolefix_added_tp, rolefix_added_false=rolefix_added_fp,
            rolefix_removed=[list(r) for r in rolefix_removed], rolefix_precision_delta=rolefix_prec_delta,
            n5_relation_baseline=base["n5_relation"], n5_relation_rolefix_alone=n5_rolefix_alone,
            n5_relation_both_cheap=both["n5_relation"], n5_relation_joint_with_goldclause=n5_joint,
            n5_answer_joint=joint["n5_answer"]),
        arms_differ_digests=digests,
        bands=dict(SELF_LOOP_MIN_REMOVED=SELF_LOOP_MIN_REMOVED, ROLE_FIX_MIN_CHANGED=ROLE_FIX_MIN_CHANGED,
                   PASSIVE_FLOOR=PASSIVE_FLOOR, REVERSAL_FLOOR=REVERSAL_FLOOR,
                   FLOOR_STRICT_PREC_LO=FLOOR_STRICT_PREC_LO, FLOOR_STRICT_PREC_HI=FLOOR_STRICT_PREC_HI),
        arms=dict(baseline=_arm_summary(base), self_loop=_arm_summary(sl), role_fix=_arm_summary(rf),
                  both=_arm_summary(both), both_plus_goldclause=_arm_summary(joint)),
        cited_floor=dict(source="data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json:arms.third_reader",
                         commit="00c6688b6", vet="a7ecb244", **FLOOR),
        note=("self_loop guard = drop relations with identical entity args (only FPs, never a TRUE relation). "
              "role_fix = RECIPIENT frame repair (demote a post-verbal object mislabeled RECIPIENT to PATIENT "
              "unless dative-'to' or canonical double-object; same-clause guarded). both_plus_goldclause uses "
              "the DEFERRED clause-seg gold shared-subject (ORA.INJECT_SUBJ) purely to CONFIRM role_fix enables "
              "N5 once the agent is present -- NOT a cheap-win claim."),
        scope_caveat=("Same mostly-in-vocab 3rd-reader narrative slice (SYNTAX isolated; out-of-vocab / poetry "
                      "/ long sentences UNTESTED). n_questions=15, n_relations~36 -> modestly powered; strict "
                      "precision (per-relation, n~36) is the load-bearing FP signal. COMPLETE_TRUTH is a single-"
                      "annotator hand annotation reused from the oracle cell. CLAIM-VET-pending; strategic read "
                      "= hypothesis pending landed-VET. NP-head + clause-seg + argument-structure remain the "
                      "deferred bigger workstreams (USER steer)."),
        n_passages=len(G3_PASSAGES), n_questions=len(G3_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("attribution:", json.dumps(metrics["attribution"]))
    for k in ("baseline", "self_loop", "role_fix", "both", "both_plus_goldclause"):
        a = arms[k]
        print(f"  {k:22s} strict_prec={a['strict']['strict_precision']:.3f} fp={a['strict']['fp']:2d}/"
              f"{a['strict']['n_extracted']:2d} | all={a['slices']['all']:.3f} NC={a['slices']['NC']:.3f} "
              f"CO={a['slices']['CO']:.3f} CMP={a['slices']['CMP']:.3f} | ref={a['ref_acc']:.3f} | "
              f"RELF1 R={a['relf1']['micro_recall']:.3f} | N5rel={a['n5_relation']} N5ans={a['n5_answer']}")
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
