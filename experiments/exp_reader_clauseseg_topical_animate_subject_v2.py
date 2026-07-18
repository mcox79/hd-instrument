"""
CLAUSE-SEG w/ TOPICAL-ANIMATE HELD SUBJECT (the VET-recomputed clean version). Completes the clause-seg
parser component by replacing the v1 LAST-ACTIVE held subject (which over-fires precision BELOW the
do-nothing floor because it can hold a STALE INANIMATE noun, e.g. "time") with a CENTERING-THEORY
TOPICAL-ANIMATE held subject sourced from the discourse overlay (_topical_ranked, animate-filtered).

Brain-faithful (Centering Theory / drill a9c6465a): across a coordinating "and" the brain does NOT hold the
last-active noun; it holds the ANIMATE topical PROTAGONIST (the backward-looking center). So a coordinated
bare-VP gets the animate protagonist, not whatever noun was most recently parsed as an agent.

WHY (VET acc75e96 on the v1 CLAUSE_SEG_UNLOCK 775c6085c): v1's overlay-held LAST-ACTIVE propagation
RECOVERS composition (CMP 0.333->0.667) + orphaned-relation recall (RELF1-recall 0.800->0.933) to the gold
ceiling (proven), but strict precision 0.465 < orphan-floor 0.514 < gold 0.526 -- it OVER-fires below the
do-nothing floor. The VET decomposed the excess FPs: the REAL clause-seg error is ONE injection (L34_geo2
"wished for a cool place ..." held the STALE INANIMATE "time" as subject -> 4 FALSE relations). Holding the
TOPICAL-ANIMATE protagonist ("george") instead removes exactly those "time" FPs, restoring precision to
~floor (precision-NEUTRAL) while KEEPING the composition+recall ceiling recovery. (The other v1 over-firing,
L67_susie2 "thought she would eat her lunch"->"susie", has a CORRECT animate subject; its residual FP is a
downstream complement mis-parse = a DIFFERENT workstream, NOT the held-subject source; topical keeps it.)

MECHANISM (ONE variable vs v1 = the held-subject SOURCE; everything else identical):
  held-subject source per bare-VP COORD conjunct =
    learned_lastactive : ACTIVE_SUBJECT = resolved agent head of the most recent explicit-subject clause
                         [the v1 775c6085c version -- the arm to improve on precision]
    learned_topical    : TOPICAL-ANIMATE protagonist = among the overlay's ANIMATE entities (grounded
                         animacy via ORC.is_animate), the WorkingOverlay._topical_ranked backward-looking
                         center = max by (frequency count, then FIRST-MENTION primacy). None if no animate
                         entity is held (-> do NOT inject; naturally suppresses the inanimate over-fire).
  Boundaries byte-identical to the hand-rule splitter (asserted); the cheap wins (self-loop + role-fix) ON
  for the 3 comparison arms; coref/role unchanged. The ONLY difference across learned_lastactive vs
  learned_topical is which subject the bare-VP conjunct inherits.

ARMS:
  envelope_floor     : cheap wins OFF, seg=orphan            [POSITIVE CONTROL -> byte-reproduces envelope 3rd store]
  handrule_orphan    : cheap wins ON,  seg=orphan            [FLOOR for the segmenter comparison (no recovery)]
  learned_lastactive : cheap wins ON,  seg=learned_lastactive [v1 BASELINE: recovery yes, precision below floor]
  learned_topical    : cheap wins ON,  seg=learned_topical    [MECHANISM: topical-animate held subject]
  gold_clauseseg     : cheap wins ON,  seg=gold              [CEILING = oracle INJECT_SUBJ]

MEASURE per arm: RELF1 micro P/R/F1, comprehension all/NC/CO/CMP, ref_acc, strict PRECISION + fp/tp/extracted
(INDEPENDENT COMPLETE_TRUTH, reused verbatim from the oracle cell), N5-relation (svo killed wolf sheep) +
N5 answer. Propagation telemetry vs the gold oracle INJECT_SUBJ (correct / over-prop / under-detect /
wrong-subject) for BOTH learned arms; and a learned_topical-vs-learned_lastactive delta (what the topical
source changed). Inanimate-over-fire count = over-firings whose held subject is NOT animate (ORC.is_animate).

REGRESSION GUARD (the held-subject-source change must not break the VET-confirmed controls):
  - ORC.score_passive(role_fixed) == 1.00 and ORC.score_reversal(role_fixed) == 1.00.
  - ref_acc IDENTICAL across all arms (the segmenter must not move coref).
  - the packaged state-of-mind overlay witness (verification/verify_state_of_mind_overlay.py) exits 0.

BRANCHES (decisive, genuinely can-fail):
  CLAUSE_SEG_CLEAN        = learned_topical KEEPS the recovery (N5 relation + CMP & RELF1-recall reach the
                            gold ceiling) AND restores precision to ~floor (strict precision within
                            PREC_NEUTRAL_TOL of the orphan floor; NO longer below floor) AND no inanimate
                            over-fire remains AND no control regression -> the clean clause-seg component
                            (composition + recall recovery, precision-NEUTRAL) = fold-ready first parser
                            component. NP-head + argument-structure remain the next (precision-GAIN) components.
  PARTIAL_LOST_RECOVERY   = topical fixes precision but LOSES the recovery (the animate protagonist was NOT
                            the right subject for some coordinated verb; e.g. holds the wrong animate entity
                            at the N5 site) -> localize; is _topical_ranked the wrong held subject there?
  PARTIAL_PRECISION_STUCK = topical keeps recovery but precision still below floor (another inanimate/stale
                            over-fire, or the susie-class downstream mis-parse dominates) -> localize + deflate.
  REGRESSION              = a control regressed (passive/reversal/coref/overlay-witness) -> revert + localize.
  INVALID_POSITIVE_CONTROL_FAIL = envelope_floor / gold ceiling do not reproduce their known state.

FAIRNESS / anti-circular (design-gate; USER: fair tests every time):
  - Same REAL grade-3 McGuffey passages + independent gold, imported VERBATIM from the envelope cell.
  - COMPLETE_TRUTH (precision eval) + INJECT_SUBJ (gold ceiling) reused verbatim from the oracle cell.
  - orphan/gold arms of MY extract byte-reproduce CFX.extract_passage_fixed at matched config
    (anti-copy-divergence self-test) -> the ONLY new behavior is the two learned modes; boundaries identical.
  - REAL baseline = handrule_orphan (the do-nothing floor, precision 0.514) AND learned_lastactive (v1
    recovery-but-precision-below-floor) -- both real arms, not strawman.
  - ONE variable across the two learned arms = held-subject source. Discriminator CAN-FAIL (topical can lose
    recovery or fail to fix precision). Difficulty is ON (real over-firing exists at the floor).
  - Determinism OMP=1, fixed seed, sorted(set). No salted-hash-seeded randomness (no randomness at all).

Glass-box (POS + averaged perceptron + symbolic coref/overlay animacy grounding; NO external LLM; NO
torch/GPU at runtime). Local / foreground-to-completion. NO push / NO remote-persist. CLAIM-VET-pending
(NOT self-declared chain-grade); strategic read = hypothesis pending landed-VET.

ANCHOR: reader_clauseseg_topical_animate_subject_v2
BASELINE: v1 clause-seg unlock (775c6085c; VET acc75e96) + cheap wins (VET a5ef7435) + gold clause-seg
ceiling (oracle b85422616; VET a220d138) + envelope 3rd store (00c6688b6; VET a7ecb244). COMPUTE:
sequential-CPU; wall < 120s.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                        [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate (4-way strict; the two learned arms MAY coincide -> exempted
#   pair reported as telemetry, not crashed -- a coincidence is a real PARTIAL, not an arm-impl bug) [META_RULE_AF]
# - discriminator CAN-FAIL (lose recovery / precision stuck below floor / control regress)
# - POSITIVE-CONTROL: envelope_floor byte-reproduces the envelope 3rd store [reproduce_prior / Gate D]
# - anti-copy-divergence: my extract(orphan|gold) == CFX.extract_passage_fixed byte-identical      [F.1]
# - deterministic seeding (fixed int seed, fixed order, sorted set; NO randomness)             [F.5/PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL perceptron + POS tagger + overlay animacy on
#   REAL 3rd-reader passages; runs the REAL passive/reversal controls + the REAL overlay witness           [F.1]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; envelope floor CITED@envelope metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import re
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

# Reuse the confirmed reader pipeline + REAL passages/gold + independent COMPLETE_TRUTH + the cheap
# wins (self-loop guard + RECIPIENT role fix) + the gold clause-seg ceiling, all VERBATIM.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_grade3_envelope_readtogrow_v1 as ENV         # noqa: E402
from experiments import exp_reader_oracle_parser_upperbound_v1 as ORA           # noqa: E402
from experiments import exp_reader_cheapfix_selfloop_rolefix_v1 as CFX          # noqa: E402
from experiments.exp_reader_mention_source_gold_vs_handrule_corefixed_v1 import (  # noqa: E402
    _prefers_topical, _agreement_attrs, _RESOLVABLE, _RESOLVABLE_SO, _RESOLVABLE_POSS)
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE      # noqa: E402

ANCHOR_NAME = "reader_clauseseg_topical_animate_subject_v2"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 12345

# REAL 3rd-reader passages + independent gold, imported VERBATIM.
G3_PASSAGES = ENV.G3_PASSAGES
G3_GOLD_ANTECEDENTS = ENV.G3_GOLD_ANTECEDENTS
G3_QS = ENV.G3_QS

# INDEPENDENT per-relation truth + the gold clause-seg ceiling map, reused verbatim from the oracle cell.
COMPLETE_TRUTH = ORA.COMPLETE_TRUTH
_TRUTH_UNION = ORA._TRUTH_UNION
INJECT_SUBJ = ORA.INJECT_SUBJ            # {passage: {orphaned-clause-substring: gold shared subject}}

# The cheap wins (banked; VET a5ef7435) reused verbatim -> they COMPOSE with clause-seg.
apply_role_fix = CFX.apply_role_fix
is_self_loop = CFX.is_self_loop

# The N5 target relation (wolf-killed-sheep) + its passage.
N5_PID = "L13_wolf2"
N5_REL = ("svo", "killed", "wolf", "sheep")

# ---- Envelope floor (CITED@ENV metrics arms.third_reader; positive control) ----------------------
FLOOR = dict(all=0.7333, NC=0.8333, CO=0.8333, CMP=0.3333, ref_acc=0.8333,
             RELF1_recall=0.8, RELF1_f1=0.522, n_relations=36, qLB=0.387)

# ---- v1 reference (CITED@v1 metrics; the arm to improve on precision) ----------------------------
V1_STRICT_PREC_LEARNED = 0.4651   # CITED@data/exp_reader_learned_clauseseg_shared_subject_v1/metrics.json
V1_ORPHAN_FLOOR_PREC = 0.5143     # CITED@ same (handrule_orphan strict precision)
V1_GOLD_CEILING_PREC = 0.5263     # CITED@ same (gold ceiling strict precision)

# ---- Pre-registered bands (HYPOTHESIZED@this cell; set BEFORE the final run; can-fail) ------------
GOLD_CLAUSES = {(pid, clause) for pid, mp in INJECT_SUBJ.items() for clause in mp}  # the 2 oracle sites
PREC_NEUTRAL_TOL = 0.005       # learned_topical strict precision >= orphan floor - 0.005 (at-floor = neutral)
CMP_CEILING_TOL = 1e-6         # learned_topical CMP must reach the gold CMP ceiling
RECALL_CEILING_TOL = 1e-6      # learned_topical RELF1-recall must reach the gold ceiling
PASSIVE_FLOOR = 1.0
REVERSAL_FLOOR = 1.0

_COORD_WORDS = {"and", "but", "or"}
_LEARNED_MODES = ("learned_lastactive", "learned_topical")


# =======================================================================================
# GLASS-BOX CLAUSE-SEG: boundary-aware re-segmentation (byte-aligned with ORC.split_sentences)
# =======================================================================================
def segment_clauses_with_boundaries(text):
    """Return [(clause_stripped, boundary_kind)] where boundary_kind in {START, SENT, COORD, SUBORD}.
    Uses the SAME hand-rule split regex (ORC._CLAUSE_SPLIT) via finditer so the clause TEXTS are
    byte-identical to ORC.split_sentences (asserted in self-test); only the boundary label is new."""
    parts = []
    last = 0
    prev = "START"
    for m in ORC._CLAUSE_SPLIT.finditer(text):
        parts.append((text[last:m.start()], prev))
        d = m.group(0).strip()
        if re.fullmatch(r"[.!?;:]+", d):
            prev = "SENT"
        else:
            w = re.sub(r"[^a-z]", "", d.lower())   # ", and"->"and"; " but "->"but"; ", which"->"which"
            prev = "COORD" if w in _COORD_WORDS else "SUBORD"
        last = m.end()
    parts.append((text[last:], prev))
    return [(p.strip(), k) for (p, k) in parts if p and p.strip()]


def _is_bare_vp(tagged):
    """A clause is a bare VP when it has a main verb but NO argument candidate before it. candidate_indices
    (handrule) already counts subject pronouns, so 'he stopped' has a candidate and is NOT bare."""
    vi, _v, _p = ORC.find_main_verb(tagged)
    if vi is None:
        return False
    pre = [j for j in ORC.candidate_indices_mode(tagged, "handrule", frozenset()) if j < vi]
    return len(pre) == 0


def _topical_animate_head(ov):
    """CENTERING backward-looking-center: the TOPICAL ANIMATE protagonist held in working memory. Among the
    overlay's ANIMATE entities (grounded animacy via _agreement_attrs / ORC.is_animate) pick the topical
    protagonist = WorkingOverlay._topical_ranked = max by (frequency count, then FIRST-mention primacy).
    Returns the head string, or None when no animate entity is held (-> do NOT inject)."""
    animate = [e for e in ov.entities() if e.animacy == "animate"]
    best = WorkingOverlay._topical_ranked(animate)
    return best.head if best is not None else None


# =======================================================================================
# Extract (COPY of CFX.extract_passage_fixed + clause_seg mode). clause_seg:
#   'orphan'             -> no propagation (baseline)          (byte-reproduces CFX inject_map={})
#   'gold'               -> oracle INJECT_SUBJ propagation     (byte-reproduces CFX inject_map=INJECT_SUBJ)
#   'learned_lastactive' -> v1 overlay-held LAST-ACTIVE agent head propagation on detected bare-VP COORD
#   'learned_topical'    -> Centering TOPICAL-ANIMATE held-subject propagation (the mechanism)
# active_subject tracking + _topical_animate_head are inert for orphan/gold (only READ in the learned
# branches) -> byte-identity to CFX kept.
# =======================================================================================
def extract_passage_cs(passage_text, clf, pid, passages_dict, mention_mode, clause_seg,
                       role_fix, self_loop_guard):
    """Returns (sorted_rels, res_by_pos, removed_self_loops, injections)."""
    gold_heads = frozenset()
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    fix_possessive = True
    agreement = True
    topical = True
    pref = bool(agreement)
    injects = INJECT_SUBJ.get(pid, {}) if clause_seg == "gold" else {}
    bounds = segment_clauses_with_boundaries(passage_text) if clause_seg in _LEARNED_MODES else None

    known = set()
    for txt in list(passages_dict.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    injections = []
    active_subject = None
    offset = 0
    for ci, sent in enumerate(ORC.split_sentences(passage_text)):
        tagged = ORC.pos_tag_sentence(sent)
        subj = None
        if clause_seg == "gold":
            subj = injects.get(sent.strip())
        elif clause_seg == "learned_lastactive":
            kind = bounds[ci][1]
            if kind == "COORD" and active_subject is not None and _is_bare_vp(tagged):
                subj = active_subject
        elif clause_seg == "learned_topical":
            kind = bounds[ci][1]
            if kind == "COORD" and _is_bare_vp(tagged):
                held = _topical_animate_head(ov)   # ov reflects clauses 0..ci-1 (the held state of mind)
                if held is not None:
                    subj = held
        if subj is not None:
            tagged = [(subj.capitalize(), subj, "NNP")] + tagged
            injections.append((pid, sent.strip(), subj))
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

        # HOLD the subject in working memory: update ACTIVE_SUBJECT to this clause's explicit agent
        # (resolved head). Used ONLY by learned_lastactive (v1); inert for topical (which reads the overlay).
        if agents:
            active_subject = head_of(agents[0])

        offset += len(tagged)

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
    return sorted_rels, res_by_pos, removed, injections


# =======================================================================================
# Run one arm -> store + all scores (downstream reuses ENV / ORA / ORC helpers verbatim).
# =======================================================================================
def run_arm(clf, clause_seg, role_fix, self_loop_guard):
    store, res_by_pos, injections = {}, {}, []
    for pid, text in G3_PASSAGES.items():
        rels, rbp, _rem, inj = extract_passage_cs(text, clf, pid, G3_PASSAGES, "handrule",
                                                  clause_seg, role_fix, self_loop_guard)
        store[pid] = rels
        res_by_pos[pid] = rbp
        injections.extend(inj)
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
    return dict(store=store, correct=correct, answers=answers, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_ok=n_ok, ref_n=n_tot, foundation=fnd, strict=strict,
                n5_relation=n5_relation, n5_answer=n5_answer,
                injections=[list(x) for x in injections],
                per_q=[dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=answers[i],
                            ok=bool(correct[i])) for i, q in enumerate(G3_QS)])


# =======================================================================================
# Propagation telemetry: an arm's injections vs the gold oracle INJECT_SUBJ + inanimate-over-fire count.
# =======================================================================================
def _prop_telemetry(arm, gold_arm):
    learned = {(pid, clause): subj for pid, clause, subj in arm["injections"]}
    gold = {(pid, clause): subj for pid, clause, subj in gold_arm["injections"]}
    correct, over, under, wrong_subj = [], [], [], []
    for k, subj in learned.items():
        if k in gold:
            if gold[k] == subj:
                correct.append([k[0], k[1], subj])
            else:
                wrong_subj.append([k[0], k[1], subj, gold[k]])
        else:
            over.append([k[0], k[1], subj])
    for k, subj in gold.items():
        if k not in learned:
            under.append([k[0], k[1], subj])
    over_fp = arm["strict"]["fp"] - gold_arm["strict"]["fp"]
    # inanimate/stale over-firing = an over-prop (or wrong-subject) whose held subject is NOT animate.
    inanimate_overfire = [op for op in over if not ORC.is_animate(op[2])]
    inanimate_overfire += [[w[0], w[1], w[2], w[3]] for w in wrong_subj if not ORC.is_animate(w[2])]
    return dict(correct=correct, over_prop=over, wrong_subject=wrong_subj, under_detect=under,
                n_correct=len(correct), n_over=len(over), n_under=len(under), n_wrong=len(wrong_subj),
                inanimate_overfire=inanimate_overfire, n_inanimate_overfire=len(inanimate_overfire),
                learned_fp=arm["strict"]["fp"], gold_fp=gold_arm["strict"]["fp"],
                over_prop_fp_delta=over_fp)


def _learned_delta(topical_arm, lastactive_arm):
    """What the topical-animate source CHANGED vs the v1 last-active source (per injection site)."""
    la = {(pid, clause): subj for pid, clause, subj in lastactive_arm["injections"]}
    tp = {(pid, clause): subj for pid, clause, subj in topical_arm["injections"]}
    changed_subject, only_lastactive, only_topical = [], [], []
    for k in sorted(set(la) | set(tp)):
        a = la.get(k)
        b = tp.get(k)
        if a is not None and b is not None and a != b:
            changed_subject.append([k[0], k[1], a, b])
        elif a is not None and b is None:
            only_lastactive.append([k[0], k[1], a])
        elif a is None and b is not None:
            only_topical.append([k[0], k[1], b])
    identical = (la == tp)
    return dict(changed_subject=changed_subject, only_lastactive=only_lastactive,
                only_topical=only_topical, learned_arms_identical=identical)


# =======================================================================================
# Regression controls (the held-subject-source change must not break role/coref behavior).
# =======================================================================================
def _make_assigner(clf, role_fix):
    def a(tagged):
        roles, vi, v, ps, cand = ORC.assign_roles_learned(tagged, clf, "handrule", frozenset())
        if role_fix:
            roles = apply_role_fix(tagged, roles, vi, cand)
        return roles, vi, v, ps, cand
    return a


def _role_controls(clf):
    pass_fix, pass_per = ORC.score_passive(_make_assigner(clf, True))
    rev_fix, rev_per = ORC.score_reversal(_make_assigner(clf, True))
    return dict(passive_rolefix=round(pass_fix, 4), reversal_rolefix=round(rev_fix, 4),
                passive_per=pass_per, reversal_per=rev_per)


def _run_overlay_witness():
    path = os.path.join(REPO, "verification", "verify_state_of_mind_overlay.py")
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=180)
        tail = (p.stdout + p.stderr).strip().splitlines()
        return (p.returncode == 0), (tail[-1] if tail else "")
    except Exception as e:
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


def _arms_must_differ(named_outputs, exempt_pairs=frozenset()):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pair = tuple(sorted((names[i], names[j])))
            if pair in exempt_pairs:
                continue
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


def _fit_clf():
    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)
    return clf


def _store_json(arm):
    return {p: [list(r) for r in arm["store"][p]] for p in G3_PASSAGES}


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL reader pipeline (overlay animacy + perceptron + POS tagger) ...")
    clf = _fit_clf()

    # (A) BOUNDARY SEGMENTATION byte-aligns with ORC.split_sentences on all passages.
    n_coord = 0
    for pid, text in G3_PASSAGES.items():
        seg = segment_clauses_with_boundaries(text)
        ref = ORC.split_sentences(text)
        assert [c for c, _k in seg] == ref, f"SEG-DIVERGENCE {pid}:\n {[c for c,_ in seg]}\n {ref}"
        n_coord += sum(1 for _c, k in seg if k == "COORD")
    assert n_coord >= 3, f"expected >=3 COORD boundaries across corpus, got {n_coord}"
    print(f"[self-test] boundary seg byte-aligns with split_sentences; {n_coord} COORD boundaries")

    # (F.1) ANTI-COPY-DIVERGENCE: my extract(orphan|gold) == CFX.extract_passage_fixed byte-identical.
    for pid, text in G3_PASSAGES.items():
        for seg, cfx_map in (("orphan", {}), ("gold", INJECT_SUBJ)):
            mine, mrbp, mrem, _inj = extract_passage_cs(text, clf, pid, G3_PASSAGES, "handrule",
                                                        seg, role_fix=True, self_loop_guard=True)
            ref, rrbp, rrem = CFX.extract_passage_fixed(text, clf, pid, G3_PASSAGES, "handrule",
                                                        cfx_map, role_fix=True, self_loop_guard=True)
            assert mine == ref, f"COPY-DIVERGENCE {pid}/{seg}:\n {mine}\n {ref}"
            assert mrbp == rrbp and mrem == rrem, f"COPY-DIVERGENCE aux {pid}/{seg}"
    print("[self-test] anti-copy-divergence: extract(orphan|gold) == CFX.extract_passage_fixed")

    # POSITIVE CONTROL: envelope_floor (cheap wins OFF, orphan) reproduces the envelope floor + N5 missing.
    ef = run_arm(clf, "orphan", role_fix=False, self_loop_guard=False)
    assert ef["foundation"]["n_relations"] == FLOOR["n_relations"], \
        f"POS-CTRL n_rel {ef['foundation']['n_relations']} != {FLOOR['n_relations']}"
    assert abs(ef["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002, "POS-CTRL CMP"
    assert abs(ef["ref_acc"] - FLOOR["ref_acc"]) <= 0.002, "POS-CTRL ref_acc"
    assert abs(ef["relf1"]["micro_recall"] - FLOOR["RELF1_recall"]) <= 0.01, "POS-CTRL RELF1 recall"
    assert not ef["n5_relation"], "POS-CTRL: envelope floor unexpectedly already has N5"
    print(f"[self-test] POS-CTRL envelope_floor reproduces envelope (n_rel={ef['foundation']['n_relations']} "
          f"CMP={ef['slices']['CMP']:.3f} ref={ef['ref_acc']:.3f} RELF1r={ef['relf1']['micro_recall']:.3f}); N5 missing")

    floor = run_arm(clf, "orphan", role_fix=True, self_loop_guard=True)
    lastactive = run_arm(clf, "learned_lastactive", role_fix=True, self_loop_guard=True)
    topical = run_arm(clf, "learned_topical", role_fix=True, self_loop_guard=True)
    gold = run_arm(clf, "gold", role_fix=True, self_loop_guard=True)

    # DISCRIMINATOR FIRES: topical must inject on >=2 bare-VP COORD conjuncts (telemetry-active).
    assert len(topical["injections"]) >= 2, \
        f"topical fired {len(topical['injections'])} injections (<2): discriminator vacuous"
    # floor stays orphaned; gold ceiling recovers N5 relation.
    assert not floor["n5_relation"], "FLOOR (orphan) unexpectedly has N5"
    assert gold["n5_relation"], "GOLD ceiling did NOT recover the N5 relation (ceiling broken)"
    # v1 reference reproduces (last-active recovers N5, precision below floor).
    assert lastactive["n5_relation"], "v1 last-active did NOT recover N5 (v1 reference broken)"
    print(f"[self-test] floor N5={floor['n5_relation']} | lastactive inj={len(lastactive['injections'])} "
          f"N5={lastactive['n5_relation']} prec={lastactive['strict']['strict_precision']:.4f} | "
          f"topical inj={len(topical['injections'])} N5={topical['n5_relation']} "
          f"prec={topical['strict']['strict_precision']:.4f} | gold N5={gold['n5_relation']} "
          f"prec={gold['strict']['strict_precision']:.4f}")

    tel_tp = _prop_telemetry(topical, gold)
    tel_la = _prop_telemetry(lastactive, gold)
    delta = _learned_delta(topical, lastactive)
    print(f"[self-test] topical vs gold: correct={tel_tp['n_correct']} over={tel_tp['n_over']} "
          f"under={tel_tp['n_under']} wrong={tel_tp['n_wrong']} inanimate_overfire={tel_tp['n_inanimate_overfire']}")
    print(f"[self-test]   topical over={tel_tp['over_prop']} inanimate={tel_tp['inanimate_overfire']}")
    print(f"[self-test]   lastactive inanimate_overfire={tel_la['n_inanimate_overfire']} {tel_la['inanimate_overfire']}")
    print(f"[self-test]   held-subject delta (topical vs lastactive): changed={delta['changed_subject']} "
          f"only_la={delta['only_lastactive']} only_tp={delta['only_topical']}")

    # REGRESSION: role controls hold; coref ref_acc identical across all arms; overlay witness green.
    ctrl = _role_controls(clf)
    assert ctrl["passive_rolefix"] >= PASSIVE_FLOOR, f"role_fix REGRESSED passive {ctrl['passive_rolefix']}"
    assert ctrl["reversal_rolefix"] >= REVERSAL_FLOOR, f"role_fix REGRESSED reversal {ctrl['reversal_rolefix']}"
    for nm, a in (("floor", floor), ("lastactive", lastactive), ("topical", topical), ("gold", gold)):
        assert a["ref_acc"] == ef["ref_acc"], f"{nm} moved ref_acc {ef['ref_acc']}->{a['ref_acc']} (coref regression)"
    print(f"[self-test] controls: passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f}; "
          f"ref_acc {ef['ref_acc']:.3f} identical across arms")

    # ARMS-MUST-DIFFER (4-way strict; the two learned arms are exempted from the mutual crash-assert
    # because a topical==lastactive coincidence is a real PARTIAL outcome, reported as telemetry).
    _arms_must_differ(dict(envelope_floor=_store_json(ef), handrule_orphan=_store_json(floor),
                           learned_topical=_store_json(topical), gold_clauseseg=_store_json(gold)))
    # topical must differ from the floor (mechanism fired) -- assert explicitly.
    assert _store_json(topical) != _store_json(floor), "topical store == floor store (mechanism did not fire)"

    # DETERMINISM.
    topical2 = run_arm(clf, "learned_topical", role_fix=True, self_loop_guard=True)
    assert topical2["strict"] == topical["strict"] and topical2["correct"] == topical["correct"] \
        and topical2["injections"] == topical["injections"], "non-deterministic"

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

    ef = run_arm(clf, "orphan", role_fix=False, self_loop_guard=False)          # envelope floor (control)
    floor = run_arm(clf, "orphan", role_fix=True, self_loop_guard=True)         # handrule_orphan floor
    lastactive = run_arm(clf, "learned_lastactive", role_fix=True, self_loop_guard=True)  # v1 baseline
    topical = run_arm(clf, "learned_topical", role_fix=True, self_loop_guard=True)        # MECHANISM
    gold = run_arm(clf, "gold", role_fix=True, self_loop_guard=True)            # gold ceiling
    arms = dict(envelope_floor=ef, handrule_orphan=floor, learned_lastactive=lastactive,
                learned_topical=topical, gold_clauseseg=gold)

    digests = _arms_must_differ({k: _store_json(v) for k, v in arms.items()},
                                exempt_pairs=frozenset({tuple(sorted(("learned_lastactive", "learned_topical")))}))
    mech_fired = _store_json(topical) != _store_json(floor)
    ctrl = _role_controls(clf)
    witness_ok, witness_tail = _run_overlay_witness()
    tel = _prop_telemetry(topical, gold)              # topical (mechanism) vs gold oracle
    tel_la = _prop_telemetry(lastactive, gold)        # v1 last-active vs gold oracle (reference)
    delta = _learned_delta(topical, lastactive)       # what the topical source changed

    def _sp(a): return a["strict"]["strict_precision"]

    # positive control
    pc_ok = (ef["foundation"]["n_relations"] == FLOOR["n_relations"] and
             abs(ef["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002 and
             abs(ef["ref_acc"] - FLOOR["ref_acc"]) <= 0.002 and
             abs(ef["relf1"]["micro_recall"] - FLOOR["RELF1_recall"]) <= 0.01 and
             not ef["n5_relation"] and gold["n5_relation"] and lastactive["n5_relation"])

    passive_ok = ctrl["passive_rolefix"] >= PASSIVE_FLOOR
    reversal_ok = ctrl["reversal_rolefix"] >= REVERSAL_FLOOR
    coref_ok = all(a["ref_acc"] == ef["ref_acc"] for a in (floor, lastactive, topical, gold))
    no_regression = passive_ok and reversal_ok and coref_ok and witness_ok and mech_fired

    # PRIMARY: does topical KEEP recovery AND fix precision to ~floor (precision-neutral)?
    n5_recovered = topical["n5_relation"]
    cmp_reaches_ceiling = topical["slices"]["CMP"] >= gold["slices"]["CMP"] - CMP_CEILING_TOL
    recall_reaches_ceiling = topical["relf1"]["micro_recall"] >= gold["relf1"]["micro_recall"] - RECALL_CEILING_TOL
    keeps_recovery = n5_recovered and cmp_reaches_ceiling and recall_reaches_ceiling

    precision_neutral = _sp(topical) >= _sp(floor) - PREC_NEUTRAL_TOL
    precision_regresses_below_floor = _sp(topical) < _sp(floor) - 1e-9
    no_inanimate_overfire = (tel["n_inanimate_overfire"] == 0)

    # recovery-fraction telemetry (topical vs floor->gold gap)
    cmp_gap = gold["slices"]["CMP"] - floor["slices"]["CMP"]
    cmp_recovered_frac = ((topical["slices"]["CMP"] - floor["slices"]["CMP"]) / cmp_gap) if abs(cmp_gap) > 1e-9 else 1.0
    recall_gap = gold["relf1"]["micro_recall"] - floor["relf1"]["micro_recall"]
    recall_recovered_frac = ((topical["relf1"]["micro_recall"] - floor["relf1"]["micro_recall"]) / recall_gap) \
        if abs(recall_gap) > 1e-9 else 1.0
    # precision improvement over the v1 last-active baseline.
    prec_delta_vs_v1 = _sp(topical) - _sp(lastactive)

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"positive control failed: envelope_floor n_rel={ef['foundation']['n_relations']} "
                f"CMP={ef['slices']['CMP']:.3f} ref={ef['ref_acc']:.3f} RELF1r={ef['relf1']['micro_recall']:.3f} "
                f"N5={ef['n5_relation']}; gold N5={gold['n5_relation']}; v1 lastactive N5={lastactive['n5_relation']}. "
                f"Basis broken.")
    elif not no_regression:
        verdict = "REGRESSION"
        vmsg = (f"the held-subject-source change regressed a control: passive {ctrl['passive_rolefix']:.2f} "
                f"reversal {ctrl['reversal_rolefix']:.2f} coref_ok={coref_ok} overlay_witness={witness_ok} "
                f"mech_fired={mech_fired}. The topical change is more than a boundary-preserving held-subject "
                f"swap -- revert + localize.")
    elif keeps_recovery and precision_neutral and no_inanimate_overfire:
        verdict = "CLAUSE_SEG_CLEAN"
        vmsg = (f"THE TOPICAL-ANIMATE HELD SUBJECT COMPLETES THE CLAUSE-SEG COMPONENT. Sourcing the held "
                f"subject from the overlay's Centering backward-looking-center (topical ANIMATE protagonist "
                f"via _topical_ranked) instead of the v1 last-active agent KEEPS the ceiling recovery AND "
                f"restores precision to the do-nothing floor (precision-NEUTRAL). Recovery kept: N5 "
                f"(svo killed wolf sheep) relation={topical['n5_relation']}; CMP {floor['slices']['CMP']:.3f}->"
                f"{topical['slices']['CMP']:.3f} (ceiling {gold['slices']['CMP']:.3f}); RELF1-recall "
                f"{floor['relf1']['micro_recall']:.3f}->{topical['relf1']['micro_recall']:.3f} (ceiling "
                f"{gold['relf1']['micro_recall']:.3f}). Precision RESTORED: topical strict precision "
                f"{_sp(topical):.4f} vs orphan floor {_sp(floor):.4f} (v1 last-active was {_sp(lastactive):.4f}, "
                f"BELOW floor); regress_below_floor={precision_regresses_below_floor}; delta_vs_v1="
                f"{prec_delta_vs_v1:+.4f}. Held-subject delta vs v1: {delta['changed_subject']} (the stale "
                f"inanimate 'time' hold is gone: inanimate_overfire {tel_la['n_inanimate_overfire']}->"
                f"{tel['n_inanimate_overfire']}). NO control regression (passive {ctrl['passive_rolefix']:.2f} "
                f"reversal {ctrl['reversal_rolefix']:.2f} coref identical overlay green). This is the clean, "
                f"fold-ready clause-seg parser component (composition + orphaned-relation recall reach the "
                f"ceiling; precision-neutral). NP-head + argument-structure remain the next (precision-GAIN) "
                f"components. HYPOTHESIS pending landed-VET.")
    elif not keeps_recovery:
        verdict = "PARTIAL_LOST_RECOVERY"
        vmsg = (f"topical FIXED precision but LOST the recovery. Precision {_sp(topical):.4f} vs floor "
                f"{_sp(floor):.4f} (neutral={precision_neutral}) BUT N5 relation={topical['n5_relation']} "
                f"CMP {topical['slices']['CMP']:.3f} (ceiling {gold['slices']['CMP']:.3f}) RELF1-recall "
                f"{topical['relf1']['micro_recall']:.3f} (ceiling {gold['relf1']['micro_recall']:.3f}); topical "
                f"vs gold under={tel['n_under']} wrong={tel['n_wrong']} ({tel['under_detect']}+{tel['wrong_subject']}). "
                f"The topical-animate protagonist was NOT the right subject for some coordinated verb (held the "
                f"wrong animate entity, or none). DEFLATE + localize: is _topical_ranked mis-ranking the held "
                f"subject at the N5/gold sites? HYPOTHESIS pending landed-VET.")
    elif keeps_recovery and not precision_neutral:
        verdict = "PARTIAL_PRECISION_STUCK"
        vmsg = (f"topical KEEPS recovery but precision still below floor. N5={topical['n5_relation']} CMP "
                f"{topical['slices']['CMP']:.3f} RELF1-recall {topical['relf1']['micro_recall']:.3f} (both at "
                f"ceiling) BUT strict precision {_sp(topical):.4f} < floor {_sp(floor):.4f} "
                f"(regress_below_floor={precision_regresses_below_floor}); topical over={tel['n_over']} "
                f"inanimate_overfire={tel['n_inanimate_overfire']} ({tel['over_prop']}). The topical source did "
                f"not remove enough over-firing FPs -- another inanimate/stale hold, or the residual susie-class "
                f"downstream complement mis-parse (a different workstream) dominates. DEFLATE + localize. "
                f"HYPOTHESIS pending landed-VET.")
    else:
        verdict = "PARTIAL"
        vmsg = (f"SPLIT. keeps_recovery={keeps_recovery} precision_neutral={precision_neutral} "
                f"no_inanimate_overfire={no_inanimate_overfire}; N5={topical['n5_relation']} CMP "
                f"{topical['slices']['CMP']:.3f} RELF1-recall {topical['relf1']['micro_recall']:.3f}; strict prec "
                f"topical {_sp(topical):.4f} floor {_sp(floor):.4f} v1 {_sp(lastactive):.4f} gold {_sp(gold):.4f}. "
                f"See telemetry + arms.")

    def _arm_summary(a):
        return dict(slices=a["slices"], ref_acc=a["ref_acc"], ref_ok=a["ref_ok"], ref_n=a["ref_n"],
                    relf1_micro_f1=a["relf1"]["micro_f1"], relf1_micro_precision=a["relf1"]["micro_precision"],
                    relf1_micro_recall=a["relf1"]["micro_recall"],
                    foundation_n_relations=a["foundation"]["n_relations"],
                    foundation_quality_lb=a["foundation"]["quality_precision_lower_bound"],
                    strict=a["strict"], n5_relation=a["n5_relation"], n5_answer=a["n5_answer"],
                    injections=a["injections"], per_q=a["per_q"])

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: N5 floor={floor['n5_relation']} lastactive={lastactive['n5_relation']} "
                 f"topical={topical['n5_relation']} gold={gold['n5_relation']} | CMP floor "
                 f"{floor['slices']['CMP']:.3f} -> topical {topical['slices']['CMP']:.3f} -> gold "
                 f"{gold['slices']['CMP']:.3f} | RELF1-recall floor {floor['relf1']['micro_recall']:.3f} -> "
                 f"topical {topical['relf1']['micro_recall']:.3f} -> gold {gold['relf1']['micro_recall']:.3f} | "
                 f"strict_prec floor {_sp(floor):.4f} v1_lastactive {_sp(lastactive):.4f} topical {_sp(topical):.4f} "
                 f"gold {_sp(gold):.4f} | topical inanimate_overfire {tel['n_inanimate_overfire']} "
                 f"(v1 {tel_la['n_inanimate_overfire']}) | passive {ctrl['passive_rolefix']:.2f} reversal "
                 f"{ctrl['reversal_rolefix']:.2f} coref_ok={coref_ok} overlay={witness_ok}"),
        elapsed_s=round(elapsed, 2), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        one_variable=("held-subject SOURCE across the two learned arms: last-active agent head (v1) vs "
                      "topical-animate protagonist (_topical_ranked, animate-filtered); cheap wins ON + "
                      "boundaries byte-identical + coref/role identical for the comparison arms"),
        positive_control_ok=pc_ok,
        mechanism_fired=mech_fired,
        primary=dict(n5_recovered=n5_recovered, cmp_reaches_ceiling=cmp_reaches_ceiling,
                     recall_reaches_ceiling=recall_reaches_ceiling, keeps_recovery=keeps_recovery,
                     precision_neutral=precision_neutral,
                     precision_regresses_below_floor=precision_regresses_below_floor,
                     no_inanimate_overfire=no_inanimate_overfire,
                     cmp_recovered_frac=round(cmp_recovered_frac, 4),
                     recall_recovered_frac=round(recall_recovered_frac, 4),
                     strict_prec_topical=round(_sp(topical), 4),
                     strict_prec_v1_lastactive=round(_sp(lastactive), 4),
                     strict_prec_orphan_floor=round(_sp(floor), 4),
                     strict_prec_gold_ceiling=round(_sp(gold), 4),
                     prec_delta_vs_v1=round(prec_delta_vs_v1, 4),
                     n_inanimate_overfire_topical=tel["n_inanimate_overfire"],
                     n_inanimate_overfire_v1=tel_la["n_inanimate_overfire"]),
        propagation_telemetry_topical=tel,
        propagation_telemetry_v1_lastactive=tel_la,
        learned_source_delta=delta,
        regression=dict(passive_rolefix=ctrl["passive_rolefix"], reversal_rolefix=ctrl["reversal_rolefix"],
                        passive_ok=passive_ok, reversal_ok=reversal_ok, coref_ok=coref_ok,
                        overlay_witness_ok=witness_ok, overlay_witness_tail=witness_tail,
                        mechanism_fired=mech_fired, no_regression=no_regression,
                        passive_per=ctrl["passive_per"], reversal_per=ctrl["reversal_per"]),
        arms_differ_digests=digests,
        bands=dict(PREC_NEUTRAL_TOL=PREC_NEUTRAL_TOL, CMP_CEILING_TOL=CMP_CEILING_TOL,
                   RECALL_CEILING_TOL=RECALL_CEILING_TOL, PASSIVE_FLOOR=PASSIVE_FLOOR,
                   REVERSAL_FLOOR=REVERSAL_FLOOR, gold_shared_subject_clauses=sorted(list(GOLD_CLAUSES))),
        arms=dict(envelope_floor=_arm_summary(ef), handrule_orphan=_arm_summary(floor),
                  learned_lastactive=_arm_summary(lastactive), learned_topical=_arm_summary(topical),
                  gold_clauseseg=_arm_summary(gold)),
        cited_floor=dict(source="data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json:arms.third_reader",
                         commit="00c6688b6", vet="a7ecb244", **FLOOR),
        cited_v1=dict(source="data/exp_reader_learned_clauseseg_shared_subject_v1/metrics.json",
                      commit="775c6085c", vet="acc75e96", strict_prec_learned=V1_STRICT_PREC_LEARNED,
                      strict_prec_orphan_floor=V1_ORPHAN_FLOOR_PREC, strict_prec_gold_ceiling=V1_GOLD_CEILING_PREC),
        note=("Glass-box Centering-Theory topical-animate held subject: at a COORD-boundary bare-VP conjunct, "
              "prepend the overlay's topical ANIMATE protagonist (max by frequency then first-mention primacy "
              "among grounded-animate entities) as a pre-verb AGENT -- sourced from working memory, animate-"
              "filtered so a stale inanimate noun (e.g. 'time') is never held. Boundaries byte-identical; the "
              "ONE variable vs v1 is the held-subject source (last-active agent -> topical-animate protagonist)."),
        scope_caveat=("Same mostly-in-vocab 3rd-reader narrative slice (n_questions=15, n_relations~36 -> modestly "
                      "powered). COMPLETE_TRUTH is a single-annotator hand annotation reused from the oracle cell; a "
                      "correctly-propagated subject that yields a semantically-true-but-unannotated relation scores as "
                      "an FP (annotation incompleteness, not a mechanism error). 'Precision-NEUTRAL' = restored to the "
                      "do-nothing floor, NOT a precision GAIN; the precision GAIN needs NP-head + argument-structure "
                      "(separate deferred workstreams). CLAIM-VET-pending; strategic read = hypothesis pending "
                      "landed-VET."),
        n_passages=len(G3_PASSAGES), n_questions=len(G3_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("topical vs gold telemetry:", json.dumps(tel))
    print("learned source delta:", json.dumps(delta))
    for k in ("envelope_floor", "handrule_orphan", "learned_lastactive", "learned_topical", "gold_clauseseg"):
        a = arms[k]
        print(f"  {k:18s} strict_prec={a['strict']['strict_precision']:.4f} fp={a['strict']['fp']:2d}/"
              f"{a['strict']['n_extracted']:2d} tp={a['strict']['tp']:2d} | all={a['slices']['all']:.3f} "
              f"NC={a['slices']['NC']:.3f} CO={a['slices']['CO']:.3f} CMP={a['slices']['CMP']:.3f} | "
              f"ref={a['ref_acc']:.3f} | RELF1 R={a['relf1']['micro_recall']:.3f} | N5rel={a['n5_relation']} "
              f"| inj={len(a['injections'])}")
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
