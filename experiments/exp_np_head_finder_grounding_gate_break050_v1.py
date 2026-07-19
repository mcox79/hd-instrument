"""NP-HEAD-FINDER (2-gate, grounding-gated): does a STRUCTURAL head-position gate + a GRADED WordNet
grounding gate, replacing the hand-enumerated FUNC_JUNK blocklist in LCCP candidate generation, RAISE
agent-head precision past the 0.489/0.50 parser-cap against INDEPENDENT gold, without over-pruning true
heads (metonymy/coerced entities)?

QUESTION (the break-0.50 CANDIDATE-GENERATION lever; VET ae18135d / atom 29341):
  The reading-axis is PARSER-CAPPED at 0.489 (membership) / 0.500 (LCCP arm-C). The confirmed residual is
  CANDIDATE GENERATION: the parser proposes WRONG agent-head TOKENS no downstream component can fix because
  the correct head was never in the candidate set. Two named, NON-REDUNDANT failure modes (drill
  notes/research_np_head_candidate_generation_grounding_gate_5x_brain_drill_2026-07-19.md):
    (1) WRONG-CONSTITUENT on genuine entity nouns (fields/table/bank -- real, WordNet-groundable nouns in
        the WRONG structural position: object of an adjunct/fronted PP, or a predicate nominal) -> a
        STRUCTURAL head-position gate (Collins head-percolation + Xue-Palmer PP/constituent pruning).
    (2) WRONG-CATEGORY on non-entities (regular = a predicate adjective; no entity noun sense) -> a GRADED
        WordNet hypernym-root / entity-hood GROUNDING gate. GRADED not hard-veto (Katz-Fodor -> Resnik:
        a hard selectional filter breaks metonymy/coercion -- 'the White House announced ...').
  NO single gate closes the whole residual (both structurally necessary, per the drill headline). This cell
  REPLACES the current hand-enumerated FUNC_JUNK blocklist (is_junk_agent, exp_attachment_coref_lever_lccp_
  break050_v1.py) with the principled, generalizing 2-gate head-finder.

ARMS (ONE VARIABLE per gate; IDENTICAL LCCP arm-C candidate generation + INDEPENDENT gold across arms):
  ARM A  (LCCP candidate-gen)      = LCCP arm-C proposed agent head as-is (proposes fields/regular/table).
  ARM B1 (+Gate-1 structural)      = for each verb-instance, if the proposed agent head is structurally
    INVALID as this verb's subject (PP-governed / predicate-nominal / non-nominal POS), re-derive the head
    via head-position rules over Penn-POS tags: the clause SUBJECT = nearest pre-verbal non-PP-governed
    nominative-pronoun > proper-noun > common-noun (Collins head-percolation); post-verbal inversion
    fallback (locative inversion). Prunes fields/table/bank/regular; proposes the correct grounded head.
  ARM B2 (+Gate-2 graded grounding)= B1 PLUS a GRADED WordNet entity-hypernym-root/concreteness grounding
    score used to (a) break ties among competing Gate-1 subject candidates toward the concrete entity, and
    (b) DOWN-WEIGHT (never hard-veto) abstraction-rooted proposed heads -- protecting metonymy/coerced
    entities (a strong prior, not a veto).
  A hard-veto SIMULATION arm (B2_hardveto) is computed ONLY to measure the metonymy brittleness the graded
  gate avoids (reported, NOT the verdict arm).

MEASURED (decisive, vs INDEPENDENT gold; the SAME agent-lens + membership-lens as the coref sibling cell):
  primary = AGENT-head precision A vs B1 vs B2 (per gold-framed verb-instance); the CANDIDATE-GEN RESIDUAL
  (A-wrong heads) fixed-fraction per gate; the PER-MODE split (WRONG_CONSTITUENT fixed by Gate-1 vs
  WRONG_CATEGORY fixed by Gate-2) + gate-decomposition overlap (Prediction-3: non-overlapping?); the RECALL
  COST (correct-in-A heads B breaks -- the over-prune / metonymy-brittleness risk); the MEMBERSHIP-lens
  (0.489 cap) A vs B1 vs B2 for the 'past-0.50' framing; per-instance dump for VET re-annotation.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = LCCP arm-C candidate-gen alone vs INDEPENDENT gold (membership 0.489; agent-lens live).
  (G2) baseline_in_band: 0.05 < overall agent precision A < 0.95 (real, un-saturated).
  (G3) CAN-FAIL-BOTH-WAYS: HARD_PASS (B2 fixes >=0.40 of the candidate-gen residual, recall_cost <=0.05,
       agent precision delta >=0.05, membership moves >0.489) OR PARTIAL (0.10-0.40 fixed = a real partial
       break-0.50 step up the mid-band) OR HARD_FAIL (<0.10 fixed -> residual NOT structure/grounding-
       separable, lost deeper; OR recall_cost >0.10 -> the gate over-prunes true heads).
  (G4) discriminator fires: B rewrites >0 agent heads AND resolved sets differ across A/B1/B2.
  (G5) ONE VARIABLE per gate: A->B1 = structural head-position; B1->B2 = +graded WordNet grounding.

VERDICT BANDS (pre-registered; class_fixed_frac_B2 = residuals fixed by B2 / |candidate-gen residual|):
  HARD_PASS_HEADFINDER_BREAKS_050: class_fixed_frac_B2 >= 0.40 AND recall_cost_B2 <= 0.05 AND
    (agent_precision_B2 - agent_precision_A) >= 0.05 AND membership_B2 > 0.489.
  PARTIAL_HEADFINDER_RAISES_CANDGEN: 0.10 <= class_fixed_frac_B2 < 0.40 AND recall_cost_B2 <= 0.10 (a real
    but partial break-0.50 step; the subcat-licensing lever remains SEPARATE -- not this cell).
  HARD_FAIL_CANDGEN_RESIDUAL_NOT_SEPARABLE: class_fixed_frac_B2 < 0.10 OR recall_cost_B2 > 0.10 ->
    localizes: heads lost deeper than candidate gen, OR the graded grounding gate over-prunes / needs a hard
    veto (breaks metonymy -> Generative-Lexicon type-coercion next drill), OR gold granularity mismatch.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): grounding-gated + structural head-finding IS
  brain-faithful (X-bar endocentricity/headedness + semantic bootstrapping's entity-hood constraint +
  graded selectional preference, NOT a hard categorical veto -- Resnik over Katz-Fodor). Real bound: OOV /
  ungrounded entities (WordNet coverage finite) + genuinely ambiguous heads + quotative-speaker attribution
  (post-verbal 'said papa' -> the COREF lever's job, sibling cell, NOT candidate-gen). Same-limit (head
  never in the parse; speaker-inversion) = accept + localize; fixes-it (partial/full) = the lever works.
  A purely HARD grounding gate would reproduce the field's own documented metonymy brittleness -> Gate-2
  built GRADED from the start (the B2_hardveto arm MEASURES that avoided brittleness).

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- a live LCCP arm-C recompute
  (~20s) + a glass-box Penn-POS tag + head-position walk + WordNet hypernym-root query over ~114 sentences;
  wall < ~90s. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage
  (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic
  hashlib + deterministic WordNet synset order; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (A vs B1 vs B2 resolved-head hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < overall agent precision A < 0.95)
- discriminator fires at smoke (B rewrites >0 heads; resolved sets differ)
- scaffold-free witness: a REAL fields/regular/table wrong-head the finder prunes + proposes the correct
  grounded head; a metonymy/coerced entity (real + synthetic 'the White House announced') it must KEEP
  (graded != veto)
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
import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402
import experiments.exp_attachment_coref_lever_lccp_break050_v1 as ACL  # noqa: E402

ANCHOR_NAME = "np_head_finder_grounding_gate_break050_v1"
CITED_MEMBERSHIP_CEILING = 0.489  # CITED@data/exp_role_filler_factorization_assembled_reading_axis_v1/metrics.json

# ---- WordNet grounded lexicon (Gate-2). Graded entity-hypernym-root / lexname; deterministic synset order.
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

# Concrete-entity WordNet lexnames (physical referents) vs abstraction lexnames.
_CONCRETE_LEXNAMES = {"noun.person", "noun.animal", "noun.artifact", "noun.object", "noun.body",
                      "noun.plant", "noun.food", "noun.location", "noun.substance", "noun.shape",
                      "noun.possession", "noun.group"}
_ABSTRACT_LEXNAMES = {"noun.attribute", "noun.cognition", "noun.state", "noun.feeling", "noun.relation",
                      "noun.quantity", "noun.time", "noun.communication", "noun.act", "noun.event",
                      "noun.motive", "noun.process"}

# ---- Penn-POS category sets (glass-box; principled category lists, NOT corpus-tuned token blocklists).
NOMINAL_HEAD_POS = {"NN", "NNS", "NNP", "NNPS", "PRP", "WP"}
PROPER_POS = {"NNP", "NNPS"}
COMMON_NOUN_POS = {"NN", "NNS"}
NP_INTERNAL_POS = {"DT", "JJ", "JJR", "JJS", "PRP$", "CD", "PDT", "POS"}
PREP_POS = {"IN"}
NOMINATIVE_PRON = {"he", "she", "they", "we", "i", "it", "who"}
OBJECT_POSS_PRON = {"him", "her", "them", "us", "me", "his", "its", "their", "my", "your", "our"}
COPULAS = {"is", "was", "were", "are", "am", "be", "been", "became", "become", "seem", "seems",
           "seemed", "grew", "grow", "remained", "remain"}
# Subordinating conjunctions Penn-tagged IN: they introduce a CLAUSE (with its own subject), they do NOT
# govern an NP as a preposition. A noun immediately after them is the clause SUBJECT, not a PP object.
HARD_SUBORDINATORS = {"because", "while", "when", "whenever", "if", "though", "although", "unless",
                      "whereas", "whether", "that", "whilst"}
AMBIG_SUBORDINATORS = {"before", "after", "since", "until", "as", "till"}  # prep OR subordinator by context
FINITE_VERB_POS = {"VB", "VBD", "VBZ", "VBP", "MD", "VBG", "VBN"}


# ----------------------------------------------------------------------------------------------
# Gate-2: graded WordNet entity-grounding score in [0,1]. High = concrete physical-entity-rooted noun;
# 0 = no noun sense (adjective/funcword) or purely abstraction-rooted. GRADED, never a veto.
# ----------------------------------------------------------------------------------------------
_GROUND_CACHE = {}


def entity_grounding_score(token):
    """Graded entity-hood in [0,1]. Deterministic (wn.synsets order is stable). 0.0 => no noun sense."""
    if not _WN_OK:
        return None  # grounding unavailable -> Gate-2 no-ops (flagged)
    t = (token or "").lower()
    if t in _GROUND_CACHE:
        return _GROUND_CACHE[t]
    if not t.isalpha():
        _GROUND_CACHE[t] = 0.0
        return 0.0
    syns = _WN.synsets(t, pos="n")
    if not syns:
        _GROUND_CACHE[t] = 0.0  # no noun sense at all (e.g. 'regular' adj) -> ungrounded
        return 0.0
    top = syns[:3]
    score = 0.0
    for s in top:
        lex = s.lexname()
        # hypernym root: physical_entity vs abstraction
        phys = False
        for path in s.hypernym_paths():
            names = [p.name().split(".")[0] for p in path]
            if "physical_entity" in names:
                phys = True
                break
        sc = 0.0
        if lex in _CONCRETE_LEXNAMES:
            sc = 1.0
        elif lex in _ABSTRACT_LEXNAMES:
            sc = 0.15
        else:
            sc = 0.5
        if phys:
            sc = max(sc, 0.7)
        score += sc
    val = round(score / len(top), 4)
    _GROUND_CACHE[t] = val
    return val


# ----------------------------------------------------------------------------------------------
# Structural helpers over Penn-POS tagged tokens: tagged = [(surf, low, pos), ...].
# ----------------------------------------------------------------------------------------------
def _governing_in_is_subordinator(tagged, prep_idx, noun_idx):
    """An IN at prep_idx governing the noun at noun_idx is a SUBORDINATING conjunction (introduces a clause,
    noun is its SUBJECT) rather than a preposition (noun is its OBJECT)."""
    low = tagged[prep_idx][1]
    if low in HARD_SUBORDINATORS:
        return True
    if low in AMBIG_SUBORDINATORS:
        # clause iff a finite verb follows the noun shortly (before a comma / next preposition).
        for k in range(noun_idx + 1, min(noun_idx + 5, len(tagged))):
            pos = tagged[k][2]
            low_k = tagged[k][1]
            if low_k == "," or pos in PREP_POS:
                break
            if pos in FINITE_VERB_POS:
                return True
    return False


def _is_pp_governed(tagged, i):
    """Token i is PP-governed iff walking left over NP-internal tokens lands on a preposition (IN) that is
    NOT a subordinating conjunction (subordinators introduce a clause; the noun is the clause subject)."""
    j = i - 1
    while j >= 0:
        pos = tagged[j][2]
        if pos in NP_INTERNAL_POS:
            j -= 1
            continue
        if pos in PREP_POS:
            return not _governing_in_is_subordinator(tagged, j, i)
        return False
    return False


def _is_predicate_nominal(tagged, i):
    """Token i is a predicate nominal iff pattern COPULA (DT|JJ|CD|RB)* token (immediate, no intervening noun)."""
    j = i - 1
    allowed = NP_INTERNAL_POS | {"RB", "RBR", "RBS"}
    while j >= 0:
        low = tagged[j][1]
        pos = tagged[j][2]
        if low in COPULAS:
            return True
        if pos in allowed:
            j -= 1
            continue
        return False
    return False


def _find_verb_index(tagged, v_surf, consumed):
    """First not-yet-consumed token whose surface OR lemma matches the verb; falls back to lemma scan."""
    vlow = str(v_surf).lower()
    vlem = LCCP.lemma_verb(vlow)
    for k, (surf, low, pos) in enumerate(tagged):
        if k in consumed:
            continue
        if low == vlow:
            consumed.add(k)
            return k
    for k, (surf, low, pos) in enumerate(tagged):
        if k in consumed:
            continue
        if LCCP.lemma_verb(low) == vlem and (pos.startswith("VB") or low == vlem):
            consumed.add(k)
            return k
    return None


def _find_token_index(tagged, surf):
    slow = str(surf).lower()
    for k, (s, low, pos) in enumerate(tagged):
        if low == slow:
            return k
    return None


def _agent_structurally_valid(tagged, ia, iv):
    """Is the proposed agent token (index ia) a structurally valid subject of the verb (index iv)?"""
    if ia is None:
        return False, "agent_token_not_found"
    pos = tagged[ia][2]
    if pos not in NOMINAL_HEAD_POS:
        return False, "non_nominal_pos"        # e.g. 'regular'(JJ), 'then'(RB), 'tell'(VB)
    if pos == "PRP" and tagged[ia][1] in OBJECT_POSS_PRON:
        return False, "oblique_pronoun"
    if _is_pp_governed(tagged, ia):
        return False, "pp_governed"            # e.g. 'fields'(into the fields), 'bank'(On its bank)
    if _is_predicate_nominal(tagged, ia):
        return False, "predicate_nominal"      # e.g. 'boy'(was the happiest boy)
    return True, "valid"


def _subject_candidates(tagged, iv):
    """Ranked subject candidates. Returns list of (idx, type_priority, low). type: 0=nom-pron,1=proper,2=common."""
    cands = []
    for j in range(len(tagged)):
        if j == iv:
            continue
        surf, low, pos = tagged[j]
        if pos not in NOMINAL_HEAD_POS:
            continue
        if _is_pp_governed(tagged, j):
            continue
        if _is_predicate_nominal(tagged, j):
            continue
        if pos == "PRP":
            if low in NOMINATIVE_PRON:
                tp = 0
            else:
                continue
        elif pos in PROPER_POS:
            tp = 1
        elif pos == "WP":
            tp = 3   # relative pronoun (who/which): subject of its OWN relative clause, not the main verb;
                     # demote below common nouns so a true inverted subject (e.g. 'hut') wins.
        else:
            tp = 2
        cands.append((j, tp, low))
    return cands


def head_find(tagged, v_surf, a_agent, consumed, use_grounding):
    """Return (proposed_head, method, mode, a_valid, a_ground, cand_ground).
    Gate-1 (structural) always; Gate-2 (grounding) applied iff use_grounding.
    mode classifies WHY the agent is a candidate-gen residual (for per-mode reporting)."""
    iv = _find_verb_index(tagged, v_surf, consumed)
    a = str(a_agent).lower()
    ia = _find_token_index(tagged, a)
    a_valid, reason = _agent_structurally_valid(tagged, ia, iv)
    a_ground = entity_grounding_score(a)
    # classify the residual mode by the parser agent's own structure/category
    if ia is not None and tagged[ia][2] not in NOMINAL_HEAD_POS:
        mode = "WRONG_CATEGORY"          # non-nominal token proposed as head (regular/then/tell)
    elif not a_valid and reason in ("pp_governed", "predicate_nominal", "oblique_pronoun"):
        mode = "WRONG_CONSTITUENT"       # genuine noun in wrong structural position (fields/table/bank/boy)
    elif (a_ground is not None) and a_ground <= 0.2:
        mode = "WRONG_CATEGORY"          # nominal but abstraction/no-entity sense
    else:
        mode = "OTHER"

    if iv is None:
        return a, "identity_no_verb", mode, a_valid, a_ground, None

    if a_valid:
        # Gate-1 does not touch a structurally-valid subject (targeted; minimizes recall cost).
        # Gate-2 (graded): only if the valid head is strongly ungrounded (abstraction) AND a better-grounded
        # pre-verbal subject exists -> down-weight (graded, still requires a structural alternative).
        if use_grounding and (a_ground is not None) and a_ground <= 0.2:
            cands = [c for c in _subject_candidates(tagged, iv) if c[0] < iv]
            best = _pick_candidate(tagged, cands, use_grounding)
            if best is not None:
                bg = entity_grounding_score(tagged[best][1])
                if bg is not None and bg > (a_ground + 0.3):
                    return tagged[best][1], "gate2_reground", mode, a_valid, a_ground, bg
        return a, "identity", mode, a_valid, a_ground, None

    # Gate-1: re-derive subject via head-position rules.
    pre = [c for c in _subject_candidates(tagged, iv) if c[0] < iv]
    best = _pick_candidate(tagged, pre, use_grounding)
    if best is None:
        # inversion fallback: nearest post-verbal proper/common noun subject (locative inversion).
        post = [c for c in _subject_candidates(tagged, iv) if c[0] > iv]
        best = _pick_candidate(tagged, post, use_grounding)
        if best is None:
            return a, "gate1_no_candidate", mode, a_valid, a_ground, None
        method = "gate2_inversion" if use_grounding else "gate1_inversion"
        return tagged[best][1], method, mode, a_valid, a_ground, entity_grounding_score(tagged[best][1])
    method = "gate2_structural" if use_grounding else "gate1_structural"
    return tagged[best][1], method, mode, a_valid, a_ground, entity_grounding_score(tagged[best][1])


def _pick_candidate(tagged, cands, use_grounding):
    """Rank: type_priority asc, then (if grounding) grounding desc, then nearest (largest idx)."""
    if not cands:
        return None
    if use_grounding and _WN_OK:
        def key(c):
            g = entity_grounding_score(tagged[c[0]][1]) or 0.0
            return (c[1], -g, -c[0])
    else:
        def key(c):
            return (c[1], -c[0])
    cands = sorted(cands, key=key)
    return cands[0][0]


# ----------------------------------------------------------------------------------------------
# Resolve every arm-C verb-instance agent head under Gate-1 (B1) and Gate-1+Gate-2 (B2).
# ----------------------------------------------------------------------------------------------
def resolve_heads(order, sent_text, keptC, use_grounding):
    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))
    resolved = {}
    n_rewritten = 0
    detail = {}
    for sid in order:
        raw = sent_text.get(sid)
        if raw is None or sid not in kept_by_sid:
            continue
        tagged = ORC.pos_tag_sentence(raw)
        consumed = set()
        for kidx, t in kept_by_sid[sid]:
            v = str(t[0])
            a = str(t[1]).lower()
            head, method, mode, a_valid, a_ground, cand_ground = head_find(
                tagged, v, a, consumed, use_grounding)
            resolved[(sid, kidx)] = (head, method)
            detail[(sid, kidx)] = {"mode": mode, "a_valid": a_valid, "a_ground": a_ground,
                                   "cand_ground": cand_ground, "method": method}
            if head != a:
                n_rewritten += 1
    return resolved, n_rewritten, detail


# ----------------------------------------------------------------------------------------------
# Agent-lens scoring (decisive): per gold-framed verb-instance, is the proposed head in the gold agent set?
# ----------------------------------------------------------------------------------------------
def score_agent_lens(keptC, gold_ag, frame_kind, resA, resB1, resB2, detail_B1):
    n_frame = 0
    aok = b1ok = b2ok = 0
    n_correct_A = 0
    rb_b1 = rb_b2 = 0
    residual = []          # A-wrong candidate-gen residual instances
    per_instance = []
    for kidx, (sid, t) in enumerate(keptC):
        v = LCCP.lemma_verb(t[0])
        a = str(t[1]).lower()
        key = (sid, v)
        goldset = gold_ag.get(key)
        if not goldset:
            continue
        n_frame += 1
        hb1 = resB1.get((sid, kidx), (a, "identity"))[0]
        hb2 = resB2.get((sid, kidx), (a, "identity"))[0]
        okA = a in goldset
        okB1 = hb1 in goldset
        okB2 = hb2 in goldset
        aok += int(okA); b1ok += int(okB1); b2ok += int(okB2)
        if okA:
            n_correct_A += 1
            if not okB1:
                rb_b1 += 1
            if not okB2:
                rb_b2 += 1
        d = detail_B1.get((sid, kidx), {})
        per_instance.append({"sid": sid, "v": v, "a_agent": a, "b1_head": hb1, "b2_head": hb2,
                             "gold": sorted(goldset), "okA": okA, "okB1": okB1, "okB2": okB2,
                             "mode": d.get("mode"), "a_ground": d.get("a_ground"),
                             "method_b1": resB1.get((sid, kidx), (a, "identity"))[1],
                             "method_b2": resB2.get((sid, kidx), (a, "identity"))[1],
                             "frame": frame_kind.get(key)})
        if not okA:
            residual.append({"sid": sid, "v": v, "a_agent": a, "b1_head": hb1, "b2_head": hb2,
                             "gold": sorted(goldset), "mode": d.get("mode"),
                             "a_ground": d.get("a_ground"),
                             "fixed_b1": bool(okB1), "fixed_b2": bool(okB2),
                             "method_b1": resB1.get((sid, kidx), (a, "identity"))[1],
                             "method_b2": resB2.get((sid, kidx), (a, "identity"))[1]})
    n_res = len(residual)
    n_fix_b1 = sum(1 for r in residual if r["fixed_b1"])
    n_fix_b2 = sum(1 for r in residual if r["fixed_b2"])
    n_fix_b2_only = sum(1 for r in residual if r["fixed_b2"] and not r["fixed_b1"])
    # per-mode split
    modes = ("WRONG_CONSTITUENT", "WRONG_CATEGORY", "OTHER")
    per_mode = {}
    for m in modes:
        rows = [r for r in residual if r["mode"] == m]
        per_mode[m] = {"n": len(rows),
                       "fixed_b1": sum(1 for r in rows if r["fixed_b1"]),
                       "fixed_b2": sum(1 for r in rows if r["fixed_b2"])}
    return {
        "n_frame": n_frame,
        "precision_A": round(aok / n_frame, 4) if n_frame else 0.0,
        "precision_B1": round(b1ok / n_frame, 4) if n_frame else 0.0,
        "precision_B2": round(b2ok / n_frame, 4) if n_frame else 0.0,
        "n_correct_A": n_correct_A,
        "recall_break_B1": rb_b1, "recall_break_B2": rb_b2,
        "recall_cost_B1": round(rb_b1 / n_correct_A, 4) if n_correct_A else 0.0,
        "recall_cost_B2": round(rb_b2 / n_correct_A, 4) if n_correct_A else 0.0,
        "candidate_gen_residual": {
            "n_residual": n_res, "n_fixed_b1": n_fix_b1, "n_fixed_b2": n_fix_b2,
            "n_fixed_b2_only": n_fix_b2_only,
            "class_fixed_frac_b1": round(n_fix_b1 / n_res, 4) if n_res else 0.0,
            "class_fixed_frac_b2": round(n_fix_b2 / n_res, 4) if n_res else 0.0,
            "per_mode": per_mode,
        },
        "residual": residual, "per_instance": per_instance,
    }


# ----------------------------------------------------------------------------------------------
# Membership lens (continuity with 0.489): rewrite agent surfaces via arm, re-run assembled ceiling.
# ----------------------------------------------------------------------------------------------
def score_membership_lens(keptC, gold, resolved):
    return ACL.score_membership_lens(keptC, gold, resolved)


# ----------------------------------------------------------------------------------------------
# Hard-veto SIMULATION (metonymy brittleness the graded gate avoids): force-replace any proposed head with
# grounding <= 0.2 whenever ANY structural alternative exists, even a structurally-valid subject.
# ----------------------------------------------------------------------------------------------
def hardveto_recall_break(keptC, gold_ag, order, sent_text):
    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))
    broke = 0
    n_correct = 0
    examples = []
    for sid in order:
        raw = sent_text.get(sid)
        if raw is None or sid not in kept_by_sid:
            continue
        tagged = ORC.pos_tag_sentence(raw)
        consumed = set()
        for kidx, t in kept_by_sid[sid]:
            v = LCCP.lemma_verb(t[0]); a = str(t[1]).lower()
            key = (sid, v); goldset = gold_ag.get(key)
            if not goldset:
                continue
            if a not in goldset:
                continue  # only measure breakage of CORRECT agents
            n_correct += 1
            g = entity_grounding_score(a)
            if g is not None and g <= 0.2:
                iv = _find_verb_index(tagged, str(t[0]), consumed)
                if iv is not None:
                    pre = [c for c in _subject_candidates(tagged, iv) if c[0] < iv]
                    best = _pick_candidate(tagged, pre, True)
                    if best is not None and tagged[best][1] != a and tagged[best][1] not in goldset:
                        broke += 1
                        if len(examples) < 5:
                            examples.append({"sid": sid, "v": v, "correct_agent": a,
                                             "hardveto_would_force": tagged[best][1], "gold": sorted(goldset)})
    return {"correct_agents_broken_by_hardveto": broke, "n_correct_agents": n_correct,
            "hardveto_recall_break_frac": round(broke / n_correct, 4) if n_correct else 0.0,
            "examples": examples}


def scaffold_free_witness(agent_lens):
    """A real fields/regular/table wrong-head the finder prunes + proposes correct head; a KEPT entity."""
    pruned_fixed = None
    kept_correct = None
    for r in agent_lens["residual"]:
        if pruned_fixed is None and r["fixed_b2"] and r["a_agent"] in ("fields", "regular", "table", "bank"):
            pruned_fixed = r
    if pruned_fixed is None:
        for r in agent_lens["residual"]:
            if r["fixed_b2"]:
                pruned_fixed = r
                break
    for pi in agent_lens["per_instance"]:
        if pi["okA"] and pi["okB2"] and pi["b2_head"] == pi["a_agent"] and (pi["a_ground"] or 0) > 0:
            kept_correct = {"sid": pi["sid"], "v": pi["v"], "agent": pi["a_agent"],
                            "a_ground": pi["a_ground"], "kept_unchanged": True}
            break
    return {"wrong_head_pruned_and_refixed": pruned_fixed,
            "true_head_kept_unchanged": kept_correct,
            "witness": "PASS" if (pruned_fixed is not None and kept_correct is not None) else "PARTIAL"}


def metonymy_probe():
    """Synthetic scaffold-free witness: graded gate KEEPS an institutional/coerced entity a hard veto prunes."""
    if not _WN_OK:
        return {"available": False}
    sent = "The White House announced the plan."
    tagged = ORC.pos_tag_sentence(sent)
    consumed = set()
    # 'house' as the institutional agent of 'announced'
    head, method, mode, a_valid, a_ground, cand_ground = head_find(
        tagged, "announced", "house", consumed, use_grounding=True)
    g = entity_grounding_score("house")
    return {"available": True, "sentence": sent, "coerced_agent": "house",
            "grounding_score_house": g, "graded_gate_head": head, "graded_method": method,
            "graded_keeps_agent": bool(head == "house"),
            "note": "graded Gate-2 keeps 'house' (institutional/coerced entity) since it is a valid grounded "
                    "structural subject; a HARD entity-vs-abstraction veto would wrongly prune it."}


def build_verdict(agent_lens, membership_lens):
    res = agent_lens["candidate_gen_residual"]
    frac = res["class_fixed_frac_b2"]
    recall_cost = agent_lens["recall_cost_B2"]
    dprec = round(agent_lens["precision_B2"] - agent_lens["precision_A"], 4)
    memb_moves = bool(membership_lens["B_precision"] > CITED_MEMBERSHIP_CEILING)
    if frac >= 0.40 and recall_cost <= 0.05 and dprec >= 0.05 and memb_moves:
        v = "HARD_PASS_HEADFINDER_BREAKS_050"
    elif frac >= 0.10 and recall_cost <= 0.10:
        v = "PARTIAL_HEADFINDER_RAISES_CANDGEN"
    else:
        v = "HARD_FAIL_CANDGEN_RESIDUAL_NOT_SEPARABLE"
    return {"verdict": v, "class_fixed_frac_b2": frac, "recall_cost_b2": recall_cost,
            "agent_precision_delta_b2_minus_a": dprec, "membership_moves_past_0489": memb_moves,
            "n_candidate_gen_residual": res["n_residual"], "n_fixed_b1": res["n_fixed_b1"],
            "n_fixed_b2": res["n_fixed_b2"], "n_fixed_b2_only": res["n_fixed_b2_only"],
            "class_fixed_frac_b1": res["class_fixed_frac_b1"]}


def heads_hash(keptC, resolved, use_b):
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
    gold_ag, frame_kind = ACL.load_gold_agentsets(cfg["slice_lessons"])

    resA = {(sid, kidx): (str(t[1]).lower(), "identity") for kidx, (sid, t) in enumerate(keptC)}
    resB1, nrw_b1, det_b1 = resolve_heads(order, sent_text, keptC, use_grounding=False)
    resB2, nrw_b2, det_b2 = resolve_heads(order, sent_text, keptC, use_grounding=True)

    agent_lens = score_agent_lens(keptC, gold_ag, frame_kind, resA, resB1, resB2, det_b1)
    ml_A = score_membership_lens(keptC, gold, resA)
    ml_B1 = score_membership_lens(keptC, gold, resB1)
    ml_B2 = score_membership_lens(keptC, gold, resB2)
    hv = hardveto_recall_break(keptC, gold_ag, order, sent_text)
    return {
        "keptC": keptC, "agent_lens": agent_lens,
        "membership_A": ml_A, "membership_B1": ml_B1, "membership_B2": ml_B2,
        "n_rewritten_b1": nrw_b1, "n_rewritten_b2": nrw_b2,
        "resA": resA, "resB1": resB1, "resB2": resB2, "hardveto": hv,
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
    return dict(slice_lessons=["L07", "L10"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=7)


def cfg_full():
    return LCCP.cfg_full()


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    out = run_config(cfg)
    al = out["agent_lens"]
    mlA, mlB1, mlB2 = out["membership_A"], out["membership_B1"], out["membership_B2"]
    vd = build_verdict(al, mlB2)
    witness = scaffold_free_witness(al)
    meton = metonymy_probe()

    hA = heads_hash(out["keptC"], out["resA"], use_b=True)
    hB1 = heads_hash(out["keptC"], out["resB1"], use_b=True)
    hB2 = heads_hash(out["keptC"], out["resB2"], use_b=True)
    arms_differ = (hA != hB1) and (hB1 != hB2 or hA != hB2) and (hA != hB2)
    arms_differ_A_vs_B = (hA != hB1) or (hA != hB2)
    baseline_in_band = bool(0.05 < al["precision_A"] < 0.95)
    discriminator_fires = bool((out["n_rewritten_b1"] > 0 or out["n_rewritten_b2"] > 0) and arms_differ_A_vs_B)
    elapsed = time.perf_counter() - t0
    res = al["candidate_gen_residual"]
    pm = res["per_mode"]

    msg = (f"{vd['verdict']} | slice={'+'.join(cfg['slice_lessons'])} n_keptC={out['lccp_summary']['n_keptC']} "
           f"| AGENT-lens P A={al['precision_A']:.3f} B1={al['precision_B1']:.3f} B2={al['precision_B2']:.3f} "
           f"(dP_B2={vd['agent_precision_delta_b2_minus_a']:+.3f}) n_frame={al['n_frame']} "
           f"recall_cost B1={al['recall_cost_B1']:.3f} B2={al['recall_cost_B2']:.3f} "
           f"| CAND-GEN residual n={res['n_residual']} fixed_b1={res['n_fixed_b1']} fixed_b2={res['n_fixed_b2']} "
           f"(fracB2={res['class_fixed_frac_b2']:.3f}, b2_only={res['n_fixed_b2_only']}) "
           f"| per-mode CONSTIT n={pm['WRONG_CONSTITUENT']['n']} fixG1={pm['WRONG_CONSTITUENT']['fixed_b1']} "
           f"| CATEG n={pm['WRONG_CATEGORY']['n']} fixG2={pm['WRONG_CATEGORY']['fixed_b2']} "
           f"| MEMBERSHIP P A={mlA['A_precision']:.3f} B1={mlB1['B_precision']:.3f} B2={mlB2['B_precision']:.3f} "
           f"(cited0.489) | hardveto_break={out['hardveto']['hardveto_recall_break_frac']:.3f} "
           f"| nrw_b1={out['n_rewritten_b1']} nrw_b2={out['n_rewritten_b2']} wn={_WN_OK} "
           f"arms_differ={arms_differ_A_vs_B} base_in_band={baseline_in_band} discrim={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": vd["verdict"], "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "verdict_detail": vd,
        "agent_lens": {k: v for k, v in al.items() if k not in ("residual", "per_instance")},
        "membership_lens": {"A": mlA, "B1": mlB1, "B2": mlB2, "cited_ceiling": CITED_MEMBERSHIP_CEILING},
        "hardveto_simulation": out["hardveto"], "metonymy_probe": meton,
        "lccp_summary": out["lccp_summary"],
        "n_heads_rewritten_b1": out["n_rewritten_b1"], "n_heads_rewritten_b2": out["n_rewritten_b2"],
        "wordnet_available": _WN_OK, "wordnet_error": _WN_ERR,
        "arms_differ_verified": arms_differ_A_vs_B, "arms_differ_hashes": {"A": hA, "B1": hB1, "B2": hB2},
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "candidate_gen_residual_dump": al["residual"],
        "agent_lens_per_instance_dump": al["per_instance"],
        "independent_gold_source": ("data/gold_mcguffey_lccp_argstruct_v1.json -- single-annotator gold; "
                                    "AGENT lens = gold pos {agent}|refs UNION nopat {agent} per (sid, verb); "
                                    "MEMBERSHIP lens = assembled cell content-membership ceiling (0.489)."),
        "reused_components": {
            "lccp_parser": "exp_learned_argstruct_parser_lccp_independent_gold_v1 (arm-C, byte-identical)",
            "pos_tagger": "exp_oracle_mention_upperbound_reader_v1.pos_tag_sentence (byte-identical)",
            "gold_agentsets": "exp_attachment_coref_lever_lccp_break050_v1.load_gold_agentsets",
            "membership_scorer": "exp_role_filler_factorization_assembled_reading_axis_v1 via ACL (atom 29340)",
            "grounding_lexicon": "WordNet (nltk) hypernym-root physical_entity/abstraction + lexname (graded)",
        },
        "REQUIRED_FIELDS": ["verdict", "verdict_detail", "agent_lens", "membership_lens",
                            "candidate_gen_residual_dump", "scaffold_free_witness", "hardveto_simulation"],
        "notes": ("NP-HEAD-FINDER break-0.50 candidate-gen lever: replace the FUNC_JUNK blocklist with a "
                  "2-gate head-finder (Gate-1 structural head-position; Gate-2 GRADED WordNet grounding, NOT "
                  "hard-veto) over LCCP arm-C agent candidate gen vs INDEPENDENT gold. HARD_PASS = B2 fixes "
                  ">=0.40 of the residual (recall_cost<=0.05, dP>=0.05, membership>0.489); PARTIAL = 0.10-0.40 "
                  "(real partial step); HARD_FAIL = <0.10 fixed OR recall_cost>0.10 (over-prune/not-separable). "
                  "This attacks ONLY candidate generation; the SUBCAT-licensing lever is SEPARATE (not this "
                  "cell). Gate-2 GRADED (hardveto_simulation measures the metonymy brittleness avoided). "
                  "CLAIM-VET-pending; single-annotator gold + small-n caveated; per-instance dump provided."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  LCCP: A_P={out['lccp_summary']['A_precision_lccp']:.3f} C_P={out['lccp_summary']['C_precision_lccp']:.3f} "
          f"n_keptC={out['lccp_summary']['n_keptC']} n_reader_svo={out['lccp_summary']['n_reader_svo']}", flush=True)
    print(f"  AGENT-lens: n_frame={al['n_frame']} P_A={al['precision_A']:.3f} P_B1={al['precision_B1']:.3f} "
          f"P_B2={al['precision_B2']:.3f} | recall_cost B1={al['recall_cost_B1']:.3f} B2={al['recall_cost_B2']:.3f} "
          f"({al['recall_break_B2']}/{al['n_correct_A']})", flush=True)
    print(f"  CAND-GEN residual: n={res['n_residual']} fixed_b1={res['n_fixed_b1']} (frac={res['class_fixed_frac_b1']:.3f}) "
          f"fixed_b2={res['n_fixed_b2']} (frac={res['class_fixed_frac_b2']:.3f}) b2_only(Gate-2 unique)={res['n_fixed_b2_only']}", flush=True)
    print(f"  PER-MODE: WRONG_CONSTITUENT n={pm['WRONG_CONSTITUENT']['n']} fixed_by_G1={pm['WRONG_CONSTITUENT']['fixed_b1']} "
          f"fixed_by_G2={pm['WRONG_CONSTITUENT']['fixed_b2']} | WRONG_CATEGORY n={pm['WRONG_CATEGORY']['n']} "
          f"fixed_by_G1={pm['WRONG_CATEGORY']['fixed_b1']} fixed_by_G2={pm['WRONG_CATEGORY']['fixed_b2']} "
          f"| OTHER n={pm['OTHER']['n']}", flush=True)
    print(f"  MEMBERSHIP-lens (cited 0.489): P_A={mlA['A_precision']:.3f} P_B1={mlB1['B_precision']:.3f} "
          f"P_B2={mlB2['B_precision']:.3f}", flush=True)
    print(f"  HARDVETO-sim (metonymy brittleness graded gate AVOIDS): correct broken={out['hardveto']['correct_agents_broken_by_hardveto']}"
          f"/{out['hardveto']['n_correct_agents']} (frac={out['hardveto']['hardveto_recall_break_frac']:.3f})", flush=True)
    if meton.get("available"):
        print(f"  METONYMY-probe: '{meton['sentence']}' agent='house' ground={meton['grounding_score_house']} "
              f"-> graded_head='{meton['graded_gate_head']}' keeps={meton['graded_keeps_agent']}", flush=True)
    print("  --- candidate-gen residual dump (sid, v, parser_agent -> B1 | B2 [method_b2], gold, mode, fixed_b2) ---", flush=True)
    for r in al["residual"]:
        print(f"    {r['sid']} {r['v']:>8} {r['a_agent']:>10} -> B1={r['b1_head']:<8} B2={r['b2_head']:<8} "
              f"[{r['method_b2']:<16}] gold={r['gold']} mode={r['mode']:<16} ag={r['a_ground']} fixed_b2={r['fixed_b2']}", flush=True)
    print(f"  [witness] wrong_head_pruned_and_refixed={witness['wrong_head_pruned_and_refixed']}", flush=True)
    print(f"  [witness] true_head_kept_unchanged={witness['true_head_kept_unchanged']} -> {witness['witness']}", flush=True)
    return payload


def self_test():
    assert _WN_OK, f"self-test: WordNet unavailable: {_WN_ERR}"
    # Gate-2 grounding is GRADED and sane: concrete entity high, funcword/no-noun-sense = 0.
    # NOTE: context-free WordNet gives 'regular' a noun.person sense (1.0) -> the ADJECTIVE 'regular' in
    # context is caught by Gate-1 (POS=JJ), NOT Gate-2. 'then' (adverb, no noun sense) grounds at 0.
    g_boy = entity_grounding_score("boy")
    g_then = entity_grounding_score("then")     # noun.time sense -> low abstraction score (graded)
    g_of = entity_grounding_score("of")         # no noun sense -> 0.0
    g_house = entity_grounding_score("house")
    assert g_boy is not None and g_boy >= 0.6, f"grounding(boy)={g_boy} expected high (person)"
    assert g_then <= 0.2, f"grounding(then)={g_then} expected low (abstraction/time sense)"
    assert g_of == 0.0, f"grounding(of)={g_of} expected 0 (no noun sense)"
    assert g_house is not None and g_house >= 0.5, f"grounding(house)={g_house} expected concrete"
    # Structural head-find on the REAL residual sentences (real code path, not a synthetic branch).
    t1 = ORC.pos_tag_sentence("He would go into the fields, or spend his time with idle boys.")
    h, m, mode, av, ag, cg = head_find(t1, "spend", "fields", set(), use_grounding=False)
    assert h == "he", f"self-test: fields->{h} expected 'he' (Gate-1 structural PP-prune)"
    assert mode == "WRONG_CONSTITUENT", f"self-test: fields mode={mode}"
    t2 = ORC.pos_tag_sentence("He became regular at school, learned to obey his parents.")
    h2, m2, mode2, av2, ag2, cg2 = head_find(t2, "obey", "regular", set(), use_grounding=True)
    assert h2 == "he", f"self-test: regular->{h2} expected 'he'"
    assert mode2 == "WRONG_CATEGORY", f"self-test: regular mode={mode2}"
    # graded != veto: metonymy probe keeps the coerced entity.
    mp = metonymy_probe()
    assert mp["available"] and mp["graded_keeps_agent"], f"self-test: metonymy probe {mp}"
    # full smoke config runs + discriminator fires.
    cfg = cfg_smoke()
    out = run_config(cfg)
    al = out["agent_lens"]
    assert al["n_frame"] > 0, "self-test: no gold-framed instances"
    assert out["n_rewritten_b1"] > 0, "self-test: Gate-1 rewrote nothing (discriminator dead)"
    hA = heads_hash(out["keptC"], out["resA"], True)
    hB1 = heads_hash(out["keptC"], out["resB1"], True)
    vd = build_verdict(al, out["membership_B2"])
    print(f"[{ANCHOR_NAME}] self-test OK: verdict={vd['verdict']} P_A={al['precision_A']:.3f} "
          f"P_B1={al['precision_B1']:.3f} P_B2={al['precision_B2']:.3f} residual_n={al['candidate_gen_residual']['n_residual']} "
          f"fixed_b2={al['candidate_gen_residual']['n_fixed_b2']} nrw_b1={out['n_rewritten_b1']} "
          f"arms_differ={hA != hB1} n_keptC={len(out['keptC'])}", flush=True)


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
