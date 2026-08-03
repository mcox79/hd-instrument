"""Canonical MATCH-OR-ALLOCATE coreference resolver (identity tracking across clauses).

PROMOTION (2026-08-02): consolidates the EARN-COREFERENCE arc's banked, VET-confirmed gains out of
experiments/*.py into ONE durable hdlab module, per the WIRE-DON'T-ISLAND capability-integration gate
(CLAUDE.md "Capability tracking"). Source atoms: 29613 (match-or-allocate fair-test HARD_PASS),
29614 (strict_cb literal-Centering pronoun branch), 29616 (self-confidence calibration signals),
29618 (Binding Principle B fix), 29621 (loop wiring). Nothing here is NEW work: every function below
is a faithful port of the corresponding validated function in the experiment cells named in each
docstring, preserved bit-identical. The experiment cells themselves are left UNTOUCHED (an
independent agent is actively building on them) -- this module is the durable promotion target for a
future refactor pass, not a replacement in place.

MECHANISM (glass-box, no borrowed embeddings, no external coref tool):
  - PRONOUN mentions are resolved by MATCHING an existing tracked entity (never allocate on a
    pronoun): gender/number agreement filter (gn_compatible) narrows candidates, then a pick rule
    selects among them. Two pick rules are provided:
      * salience pick (run_match_or_allocate): frequency+recency Centering salience, reusing
        hdlab.state_of_mind's validated OVERLAY_BETA/OVERLAY_TIEBREAK_LAMBDA formula.
      * strict-Cb pick (run_strict_cb / run_principle_b): literal Centering Theory (Grosz/Joshi/
        Weinstein) backward-looking-center -- a HARD tiered preference for the entity most recently
        holding a grammatically-prominent (agent/subject-like) role, not an additive blend.
  - NAME/NOMINAL mentions are resolved by normalized-token Jaccard overlap against every compatible
    entity's accumulated surface tokens, with a determiner-led "unique compatible antecedent"
    bridging default ("the girl" -> the one active gender/number-compatible entity) when overlap is
    zero. Both pronoun pick rules share this identical name/nominal branch.
  - run_principle_b additionally layers Binding Principle B (a non-reflexive pronoun cannot corefer
    with the AGENT of its own clause) as a candidate-pool filter before the strict-Cb pick -- this is
    the RECOMMENDED canonical resolver (the best-banked mechanism, atom 29618).

CONFIDENCE / FLAG SIGNALS (atom 29616, the metacognitive layer's error-estimate input): each
resolver has an *_instrumented variant that additionally returns, per decision, a MARGIN (decision
confidence in the mechanism's own selection criterion) and n_compatible (raw candidate-pool size).
Both were VET'd (AUC 0.65-0.75) to predict the resolver's own errors -- the signal a metacognitive
"flag unknowns" layer consumes, per hdlab.state_of_mind's surprise-flag precedent.

GLASS-BOX: pure symbolic; no torch, no external LLM, no network. ASCII-only, no em-dashes.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from hdlab.state_of_mind import (
    OVERLAY_BETA,
    OVERLAY_TIEBREAK_LAMBDA,
    PRONOUN_SCOPE,
    infer_nominal_gender,
)

STOPWORDS = frozenset({"the", "a", "an", "his", "her", "its", "their", "this", "that"})

# Which role(s) count as the grammatically-prominent "subject-like" Centering tier. A tiny, explicit,
# glass-box set (no learned/opaque component); this gold's role vocabulary's subject-analog is agent.
SUBJECT_LIKE_ROLES = frozenset({"agent"})

# Sentinel margin for an unambiguous decision (0 or 1 compatible candidates -> nothing to confuse
# with). Matches the value used by the calibration probe so downstream AUC code is unit-consistent.
NO_COMPETITION_MARGIN = 1.0


# ---------------------------------------------------------------------------
# Mention-stream construction (shared by every resolver below).
# ---------------------------------------------------------------------------
def normalize_tokens(text: str) -> Set[str]:
    """Lowercased, punctuation-stripped, stopword-filtered token set of a mention span."""
    toks = text.lower().strip(".,'\"!?;:()").split()
    toks = [t.strip(".,'\"!?;:()") for t in toks]
    return {t for t in toks if t and t not in STOPWORDS}


def is_pronoun_mention(text: str) -> bool:
    """True iff the mention text is a bare pronoun surface (not a possessive-determiner+noun NP)."""
    t = text.lower().strip(".,'\"!?;:()")
    for alt in t.split("/"):
        toks = [p.strip(".,'\"!?;:()") for p in alt.split()]
        toks = [p for p in toks if p]
        if len(toks) == 1 and toks[0] in PRONOUN_SCOPE:
            return True
    return False


def gender_number_for(text: str, is_pron: bool) -> Tuple[Optional[str], Optional[str]]:
    """Gender/number agreement tuple for a mention: pronoun-scope lookup, else nominal-cue inference."""
    if is_pron:
        t = text.lower().strip(".,'\"!?;:()")
        for p in (p.strip() for p in t.replace("/", " ").split()):
            if p in PRONOUN_SCOPE:
                sc = PRONOUN_SCOPE[p]
                return sc["gender"], sc["number"]
        return None, None
    toks = text.replace("/", " ").split()
    return infer_nominal_gender(toks), "singular"


def gn_compatible(t_gender: Optional[str], t_number: Optional[str],
                   e_gender: Optional[str], e_number: Optional[str]) -> bool:
    """Weak agreement filter: compatible unless a KNOWN attribute conflicts."""
    if t_number is not None and e_number is not None and t_number != e_number:
        return False
    if (t_gender is not None and t_gender != "any" and e_gender is not None
            and e_gender != "any" and t_gender != e_gender):
        return False
    return True


def build_mention_stream(passage: dict) -> List[dict]:
    """Flatten passage['entities'] into a clause + textual-position ordered mention list.

    Each record: {gold_entity, clause, mention_text, is_pronoun, gender, number, text_pos,
    has_determiner, role}. Excludes non-surface "(implicit ...)" placeholder mentions. 'role' is the
    gold role string when the source record carries one, else None (resolvers that use role -- the
    strict-Cb pick and Principle B -- degrade gracefully to their role-blind fallback tier)."""
    clauses = passage["clauses"]
    raw: List[dict] = []
    for ent_name, mentions in passage["entities"].items():
        for m in mentions:
            mtxt = m["mention"]
            if mtxt.strip().startswith("("):
                continue
            clause_idx = m["clause"]
            clause_text = clauses[clause_idx].lower()
            first_tok = mtxt.split()[0].lower().strip(".,'\"!?;:()/")
            pos = clause_text.find(first_tok)
            if pos < 0:
                pos = 0
            is_pron = is_pronoun_mention(mtxt)
            gender, number = gender_number_for(mtxt, is_pron)
            first_word = mtxt.strip().split()[0].lower().strip(".,'\"") if mtxt.strip() else ""
            has_determiner = first_word in {"the", "a", "an"}
            raw.append({
                "gold_entity": ent_name, "clause": clause_idx, "mention_text": mtxt,
                "is_pronoun": is_pron, "gender": gender, "number": number, "text_pos": pos,
                "has_determiner": has_determiner, "role": m.get("role"),
            })
    raw.sort(key=lambda r: (r["clause"], r["text_pos"]))
    return raw


# ---------------------------------------------------------------------------
# Tracked entity: unifies match-or-allocate's frequency+recency salience and strict-Cb's per-clause
# role history in one registry object (clause_role is inert to the salience pick, so tracking it
# unconditionally does not change run_match_or_allocate's behavior).
# ---------------------------------------------------------------------------
class TrackedEntity:
    """One coreference-chain entity: accumulated surface tokens + gender/number + mention history."""

    __slots__ = ("eid", "tokens", "gender", "number", "count", "last_pos", "clause_role")

    def __init__(self, eid: int) -> None:
        self.eid = eid
        self.tokens: Set[str] = set()
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.count = 0
        self.last_pos = -1
        self.clause_role: Dict[int, str] = {}

    def salience(self, now: int) -> float:
        """Centering salience = count + beta * exp(-lambda * dist) (frequency-primary, recency tie-break)."""
        return self.count + OVERLAY_BETA * math.exp(-OVERLAY_TIEBREAK_LAMBDA * (now - self.last_pos))

    def most_recent_subject_clause(self, cur_clause: int) -> Optional[int]:
        """Latest clause index < cur_clause at which this entity held a subject-like (agent) role."""
        cands = [c for c, r in self.clause_role.items() if r in SUBJECT_LIKE_ROLES and c < cur_clause]
        return max(cands) if cands else None


def _resolve_name_branch(entities: List[TrackedEntity], next_id: int, gender: Optional[str],
                          number: Optional[str], toks: Set[str],
                          has_determiner: bool) -> Tuple[TrackedEntity, int]:
    """Name/nominal branch shared by every pronoun-pick variant: token-overlap match, else
    determiner-led unique-compatible-antecedent bridging default, else allocate a new entity."""
    compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
    best = None
    best_overlap = 0.0
    for e in compat:
        if not toks and not e.tokens:
            continue
        union = toks | e.tokens
        if not union:
            continue
        ov = len(toks & e.tokens) / len(union)
        if ov > best_overlap:
            best_overlap = ov
            best = e
    if best is None and len(compat) == 1 and has_determiner:
        best = compat[0]
    if best is None:
        best = TrackedEntity(next_id)
        next_id += 1
        entities.append(best)
    return best, next_id


def _pick_strict_cb(compat: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    """Literal-Centering strict-Cb pick: argmax over most-recent subject-like clause < cur_clause;
    ties/no-subject-history broken by pure recency (last_pos). compat must be non-empty."""
    scored = [(e, e.most_recent_subject_clause(cur_clause)) for e in compat]
    with_subject = [(e, c) for e, c in scored if c is not None]
    if with_subject:
        best_c = max(c for _, c in with_subject)
        tied = [e for e, c in with_subject if c == best_c]
        return max(tied, key=lambda e: e.last_pos)
    return max(compat, key=lambda e: e.last_pos)


def _principle_b_filter(compat: List[TrackedEntity], cur_clause: int,
                         cur_role: Optional[str]) -> Tuple[List[TrackedEntity], str]:
    """Binding Principle B candidate filter: exclude the pronoun's own-clause AGENT from its
    candidate pool (a non-reflexive pronoun cannot corefer with a co-argument in its own clause).

    Fires ONLY when the pronoun's own role is a confirmed non-agent role AND exactly one compatible
    candidate holds role==agent in the pronoun's own clause AND excluding it leaves >=1 candidate --
    guards against participial/continued-subject clauses (0 same-clause agents -> abstain) and
    multi-verb/relative clauses (>=2 same-clause agents -> abstain). Returns (filtered, action) where
    action documents which tier fired or abstained (diagnostic / audit trail)."""
    if cur_role is None:
        return compat, "abstain_role_unknown"
    if cur_role in SUBJECT_LIKE_ROLES:
        return compat, "abstain_agent_pronoun"
    same_clause_agents = [e for e in compat if e.clause_role.get(cur_clause) == "agent"]
    if len(same_clause_agents) == 0:
        return compat, "abstain_no_same_clause_agent"
    if len(same_clause_agents) >= 2:
        return compat, "abstain_multi_same_clause_agent"
    excluded = same_clause_agents[0]
    remaining = [e for e in compat if e is not excluded]
    if not remaining:
        return compat, "abstain_only_option"
    return remaining, "fired"


def _observe_pronoun(best: TrackedEntity, pos: int, cur_clause: int, cur_role: Optional[str]) -> None:
    best.count += 1
    best.last_pos = pos
    if cur_role is not None:
        best.clause_role[cur_clause] = cur_role


def _observe_nominal(best: TrackedEntity, pos: int, cur_clause: int, cur_role: Optional[str],
                      gender: Optional[str], number: Optional[str], toks: Set[str]) -> None:
    best.tokens |= toks
    if best.gender is None and gender is not None:
        best.gender = gender
    if best.number is None and number is not None:
        best.number = number
    best.count += 1
    best.last_pos = pos
    if cur_role is not None:
        best.clause_role[cur_clause] = cur_role


def _mention_geometry(rec: dict) -> Tuple[Set[str], bool]:
    toks = normalize_tokens(rec["mention_text"])
    first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
        if rec["mention_text"].strip() else ""
    has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
    return toks, has_determiner


# ---------------------------------------------------------------------------
# Resolvers.
# ---------------------------------------------------------------------------
def run_match_or_allocate(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE baseline: pronoun branch picks by Centering salience (frequency+recency);
    name/nominal branch by token overlap + determiner bridging. Faithful port of
    experiments/exp_earn_coref_match_or_allocate_v1.run_learnable (atom 29613, fair-test HARD_PASS
    vs recency-floor and random on real cross-clause gold). Returns predicted entity-id per mention."""
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = max(compat, key=lambda e: e.salience(pos))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    return assigned


def run_strict_cb(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE with literal-Centering strict-Cb pronoun pick (hard tiered antecedent
    selection: most-recent-subject-clause, not an additive salience blend). Name/nominal branch
    unchanged. Faithful port of experiments/exp_earn_coref_pronoun_strict_cb_v1.run_learnable_strict_cb
    (atom 29614; corrects agent-vs-agent turn-taking mispicks the salience pick makes). Requires
    stream records to carry 'role' (build_mention_stream); records without a role degrade gracefully
    to the pure-recency fallback tier for that mention."""
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    return assigned


def run_principle_b(stream: List[dict]) -> Tuple[List[int], Dict[str, int]]:
    """RECOMMENDED canonical resolver: run_strict_cb + Binding Principle B candidate filter on the
    pronoun branch (name/nominal branch byte-identical). Faithful port of
    experiments/exp_coref_flag_fix_loop_principle_b_v1.run_loop_principle_b (atom 29618; net-positive
    fix over strict_cb on same-clause co-argument disjoint-reference, participial/multi-agent-guarded
    so it never regresses the cases strict_cb already got right). Returns (assigned, action_counts)
    where action_counts tallies how often the filter fired vs each abstention guard (audit trail)."""
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    actions: Dict[str, int] = {}
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                filtered, action = _principle_b_filter(compat, cur_clause, cur_role)
                actions[action] = actions.get(action, 0) + 1
                best = _pick_strict_cb(filtered, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                actions["abstain_no_compat"] = actions.get("abstain_no_compat", 0) + 1
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
                actions["allocate_new"] = actions.get("allocate_new", 0) + 1
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    return assigned, actions


def run_recency_floor(stream: List[dict]) -> List[int]:
    """Chain every mention to whatever entity absorbed the immediately preceding mention: the
    zero-identity-feature floor a real resolver must beat (fair-test discriminator, atom 29613)."""
    if not stream:
        return []
    assigned = [0]
    for _ in stream[1:]:
        assigned.append(assigned[-1])
    return assigned


def run_random(stream: List[dict], rng, p_new: float = 0.3) -> List[int]:
    """Seeded random assignment: p_new chance of a fresh entity, else uniform over existing ids
    (the second required fair-test floor, atom 29613)."""
    assigned: List[int] = []
    next_id = 0
    seen_ids: List[int] = []
    for _ in stream:
        if not seen_ids or rng.random() < p_new:
            eid = next_id
            next_id += 1
            seen_ids.append(eid)
        else:
            eid = seen_ids[rng.randrange(len(seen_ids))]
        assigned.append(eid)
    return assigned


# ---------------------------------------------------------------------------
# Confidence / flag signals (atom 29616): per-decision margin + n_compatible, the metacognitive
# layer's error-estimate input. NAME margin is shared by every arm (identical name branch); PRONOUN
# margin is mechanism-specific (each pick rule's own selection-criterion gap).
# ---------------------------------------------------------------------------
def _name_overlap_margin(entities: List[TrackedEntity], gender: Optional[str], number: Optional[str],
                          toks: Set[str], has_determiner: bool) -> Tuple[float, int]:
    """Read-only recompute of the name branch's overlap-ranking margin (top overlap - runner-up),
    matching what _resolve_name_branch will act on. Returns (margin, n_compatible)."""
    compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
    overlaps: List[float] = []
    best_overlap = 0.0
    best = None
    for e in compat:
        if not toks and not e.tokens:
            overlaps.append(0.0)
            continue
        union = toks | e.tokens
        if not union:
            overlaps.append(0.0)
            continue
        ov = len(toks & e.tokens) / len(union)
        overlaps.append(ov)
        if ov > best_overlap:
            best_overlap = ov
            best = e
    if best is None and len(compat) == 1 and has_determiner:
        return 0.0, len(compat)  # bridging default (weak evidence)
    if best is None:
        return (NO_COMPETITION_MARGIN if len(compat) == 0 else 0.0), len(compat)
    ov_sorted = sorted(overlaps, reverse=True)
    second = ov_sorted[1] if len(ov_sorted) >= 2 else 0.0
    return ov_sorted[0] - second, len(compat)


def _pronoun_strict_cb_margin(compat: List[TrackedEntity], cur_clause: int) -> float:
    """Margin in strict-Cb's own selection criterion between the chosen candidate and the runner-up
    (>=1 compat guaranteed by caller). 0.0 on a criterion tie -- the known-hard turn-taking-ambiguity
    case the flag signal should catch."""
    def _sc(e: TrackedEntity) -> int:
        c = e.most_recent_subject_clause(cur_clause)
        return c if c is not None else -1
    ranked = sorted(compat, key=lambda e: (_sc(e), e.last_pos), reverse=True)
    if len(ranked) == 1:
        return NO_COMPETITION_MARGIN
    sc_top, sc_run = _sc(ranked[0]), _sc(ranked[1])
    return float(sc_top - sc_run) if sc_top != sc_run else 0.0


def run_strict_cb_instrumented(stream: List[dict]) -> Tuple[List[int], List[dict]]:
    """run_strict_cb, additionally logging a per-decision confidence record:
    {pos, is_pronoun, margin, n_compatible}. Drives assignment through the SAME pick functions as
    run_strict_cb (byte-faithful; the caller may assert the returned assignment matches
    run_strict_cb(stream) exactly). Faithful port of exp_coref_self_confidence_calibration_v2.
    run_learnable_strict_cb_instrumented (atom 29616)."""
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    decisions: List[dict] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
                margin = _pronoun_strict_cb_margin(compat, cur_clause)
                n_compat = len(compat)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                margin, n_compat = 0.0, 0
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
                margin, n_compat = NO_COMPETITION_MARGIN, 0
            decisions.append({"pos": pos, "is_pronoun": True, "margin": margin,
                              "n_compatible": n_compat})
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        margin, n_compat = _name_overlap_margin(entities, gender, number, toks, has_determiner)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        decisions.append({"pos": pos, "is_pronoun": False, "margin": margin, "n_compatible": n_compat})
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    assert len(decisions) == len(stream) == len(assigned)
    return assigned, decisions


def mention_link_wrong(i: int, stream: List[dict], preds: List[int]) -> bool:
    """Clean local link-level (MUC-style) error label, judged only at mention i's decision time
    (uncontaminated by what later mentions do): allocate-new is correct iff no gold-coreferent
    antecedent existed yet; a match is correct iff the most-recent prior mention sharing i's
    predicted cluster is gold-coreferent with i. Faithful port of
    exp_coref_self_confidence_calibration_v1.mention_link_wrong (atom 29616's validated ground-truth
    label; fixing the naive global-purity label from AUC 0.48 to 0.75 on the name path)."""
    gi, pi = stream[i]["gold_entity"], preds[i]
    prior_same_pred = [j for j in range(i) if preds[j] == pi]
    gold_prev = [j for j in range(i) if stream[j]["gold_entity"] == gi]
    if not prior_same_pred:
        return len(gold_prev) > 0
    antecedent = max(prior_same_pred)
    return stream[antecedent]["gold_entity"] != gi


# ---------------------------------------------------------------------------
# B-cubed precision/recall/F1 scoring (per-passage then pooled by mention across the eval set).
# ---------------------------------------------------------------------------
def bcubed(streams_and_preds: List[Tuple[List[dict], List[int]]],
           subset: Optional[str] = None) -> Dict[str, float]:
    """subset in {None, 'name', 'pronoun'} restricts which mentions are AVERAGED over (cluster
    membership is always computed over the full passage's mention set). Faithful port of
    exp_earn_coref_match_or_allocate_v1.bcubed (atom 29613)."""
    prec_sum = 0.0
    rec_sum = 0.0
    n = 0
    for stream, preds in streams_and_preds:
        m = len(stream)
        for i in range(m):
            if subset == "name" and stream[i]["is_pronoun"]:
                continue
            if subset == "pronoun" and not stream[i]["is_pronoun"]:
                continue
            gold_i = stream[i]["gold_entity"]
            pred_i = preds[i]
            p_cluster = [j for j in range(m) if preds[j] == pred_i]
            g_cluster = [j for j in range(m) if stream[j]["gold_entity"] == gold_i]
            inter = len(set(p_cluster) & set(g_cluster))
            prec_sum += inter / len(p_cluster)
            rec_sum += inter / len(g_cluster)
            n += 1
    if n == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n_mentions": 0}
    precision = prec_sum / n
    recall = rec_sum / n
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1, "n_mentions": n}
