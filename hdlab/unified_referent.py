"""unified_referent -- ONE unified discourse referent per entity (Heim/Kamp DRT file-change).

Faithful port of experiments/exp_unified_referent_gum_v1.py::Resolver (arm='unified', DEFAULT config)
onto the LIVE coref mention-dict schema (hdlab.coref.parse_litbank_conll). Forms ONE file card per
discourse entity -- OPENED on first mention, UPDATED (never re-created) by every later name/common/
pronoun mention -- and resolves each pronoun by ACT-R base-level activation (hdlab.salience_binder,
decay d=2.0, Centering Cf role prominence) over the RECALL-SAFE gender/number-compatible unified
referents.

  * NAME  -> canonical id via the proven incremental hdlab.coref.EntityAliaser.assign (variant merger,
    family/gender guard, abstain-when-ambiguous) UNION a blind exact-surface-head fallback (dominates
    both -> no-regress on named coref).
  * COMMON -> head-lemma + most-recent same-head (Ariel Accessibility: definite NP resolves by recency,
    NOT the salience cue that resolves pronouns; the salience-on-nominal guardrail is OFF).
  * PRONOUN -> ACT-R argmax over recall-safe-gn-compatible referents; the resolved pronoun WRITES BACK
    into its antecedent's card (cross-type history: gender/salience learned from a name flow to a later
    pronoun and vice-versa).

Guardrails OFF (all measured net-negative / redundant by the solver; matching Resolver's default config):
graded Nref write, confidence-gated writeback, hard working-memory bound, animacy phi-feature,
salience-cue-on-nominal, gender propagation of the neuter (it) axis. The load-bearing gender completion
is the animate he/she axis (the ablation lever) -- only masc/fem propagate into a referent, matching the
reference's measured behaviour (GUM 'it' carries no reliable Gender feat).

SCORING is INTRINSIC to the referent: each card records the gold clusters of its merged mentions and the
resolved cluster is the card's DOMINANT gold cluster (== the reference dominant_eid). No surface-head ->
cluster map is needed, so the fragmentation the wire removes cannot mis-key the score (this is the
head_to_cluster reconciliation: a merged referent scores against its own dominant cluster, never a stale
surface-head lookup). Gold clusters are used ONLY to score correctness, NEVER to make the pick.

REUSE only (EntityAliaser + salience_binder), glass-box, NO external LLM at inference. ASCII only.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

import numpy as np

from hdlab.coref import EntityAliaser, name_content_tokens, sent_dist_bucket
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.state_of_mind import PRONOUN_SCOPE, compatible

# PINNED ACT-R base-level decay (Resolver default == salience_binder held-out d*). The one swept parameter
# (d=1.5 is a kb-only refinement that trades -0.02 on the pronoun pick -> NOT adopted globally).
UNIFIED_DECAY = DEFAULT_DECAY   # 2.0

# gender/number completion (file-change writeback): only the animate he/she axis + explicit number are
# durable features (the ablation-identified load-bearing gender-completion cue). 'any'/'neuter'/None do
# not overwrite an unknown feature (neuter comes only from 'it', which the reference does not reliably
# propagate on GUM).
_KNOWN_GENDER = ("masc", "fem")
_KNOWN_NUMBER = ("singular", "plural")


def _role_from_rank(rank: int) -> str:
    """Live grammatical-role signal (sent_role_rank) -> Centering Cf role token. Byte-faithful to the live
    graded pick's _role_str (hdlab.event_centrality_coref): rank 0 = subject, 1 = object, else other."""
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


class UnifiedRef:
    """One DRT file card = one persistent discourse referent (faithful to Resolver.Ref, live schema)."""

    __slots__ = ("rid", "gender", "number", "heads", "name_tokens", "has_name",
                 "history", "clusters", "last_time", "last_role", "canon_head")

    def __init__(self, rid: int) -> None:
        self.rid = rid
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.heads: set = set()            # common-noun head lemmas seen
        self.name_tokens: set = set()      # name content tokens (variant aliasing)
        self.has_name = False
        self.history: List = []            # [(order, role)] across ALL merged mentions (the ACT-R input)
        self.clusters: List[int] = []      # gold clusters of merged mentions (SCORING ONLY -- never the pick)
        self.last_time = -1
        self.last_role = "OTHER"
        self.canon_head: Optional[str] = None   # representative surface head (first mention) for downstream

    def update(self, order: int, role: str, *, gender, number, mtype: str, head: str,
               name_toks, cluster: int) -> None:
        """File-change: append this mention to the ONE card (history + gold cluster), fill a newly-known
        feature. Called for EVERY mention type incl. the resolved pronoun (cross-type writeback)."""
        self.history.append((order, role))
        self.last_time = order
        self.last_role = role
        self.clusters.append(cluster)
        if self.canon_head is None:
            self.canon_head = head
        if mtype == "name":
            self.has_name = True
            self.name_tokens |= set(name_toks)
        elif mtype == "common":
            self.heads.add(head)
        if gender in _KNOWN_GENDER and self.gender is None:
            self.gender = gender
        if number in _KNOWN_NUMBER and self.number is None:
            self.number = number

    def dominant_cluster(self) -> int:
        """The card's dominant gold cluster (== reference dominant_eid): the entity this referent scores as."""
        return Counter(self.clusters).most_common(1)[0][0]


def resolve_unified_stream(mentions: List[dict], targets: List[dict], *,
                           decay: float = UNIFIED_DECAY) -> List[dict]:
    """Reproduce Resolver(arm='unified').resolve_doc on the live mention stream.

    Returns per-target records (the EventCentralityReader.resolve_stream record schema) aligned 1:1 with
    `targets` in reading order, so _read_entities' zip(recs_ec, targets) stays valid. Each record:
      {resolved_head, resolved_cluster, attempted, correct, target_midx, gold_cluster, sent_dist, bucket,
       pool_empty, suppressed_any, topical_fired, mem_changed, n_cands, n_pool}
    """
    target_by_midx = {t["target"]["midx"]: t for t in targets}
    refs: List[UnifiedRef] = []
    canon2ref: Dict[str, UnifiedRef] = {}
    name_surf: Dict[str, UnifiedRef] = {}
    aliaser = EntityAliaser()               # proven name-variant merger (REUSE, not reimplemented)
    records: List[dict] = []

    for order, m in enumerate(mentions):
        role = _role_from_rank(m.get("sent_role_rank", 99))
        head = m["head"]
        cluster = m["cluster"]

        # ------------- PRONOUN: ACT-R salience pick over gn-compatible unified referents -------------
        if m["is_pronoun"]:
            sc = PRONOUN_SCOPE.get(head)
            pg = sc["gender"] if sc else m.get("gender")
            pn = sc["number"] if sc else m.get("number")
            cands = [r for r in refs if r.last_time < order
                     and compatible(pg, pn, r.gender, r.number)]     # recall-safe: unknown never excludes
            picked = None
            if cands:
                acts = [actr_activation(r.history, float(order), decay=decay,
                                        role_prominence=ROLE_PROMINENCE) for r in cands]
                acts = [a if a != float("-inf") else -1e9 for a in acts]
                picked = cands[int(np.argmax(acts))]                 # first-max on ties (== reference np.argmax)
            # record ONLY for scored targets (gendered-singular he/she anaphora with a prior mention)
            if m["midx"] in target_by_midx:
                tinfo = target_by_midx[m["midx"]]
                if picked is None:
                    rec = dict(resolved_head=None, resolved_cluster=None, attempted=False, correct=False)
                else:
                    rc = picked.dominant_cluster()
                    rec = dict(resolved_head=picked.canon_head, resolved_cluster=rc, attempted=True,
                               correct=bool(rc == cluster))
                rec.update(target_midx=m["midx"], gold_cluster=cluster,
                           sent_dist=tinfo["sent_dist"], bucket=sent_dist_bucket(tinfo["sent_dist"]),
                           pool_empty=(not cands), suppressed_any=False, topical_fired=False,
                           mem_changed=False, n_cands=sum(1 for r in refs if r.last_time < order),
                           n_pool=len(cands))
                records.append(rec)
            # cross-type writeback: the resolved pronoun updates its antecedent's card (file-change)
            if picked is not None:
                picked.update(order, role, gender=pg, number=pn, mtype="pronoun",
                              head=head, name_toks=(), cluster=cluster)
            continue

        # ------------- NAME / COMMON: canonical keying + file-change merge -------------
        name_toks = name_content_tokens(m.get("span_toks", [head]))
        if name_toks:   # NAME -> EntityAliaser canonical id UNION blind exact-surface fallback (no-regress)
            eff_gender = m.get("gender") or m.get("name_gender")
            canon = aliaser.assign(m.get("span_toks", [head]), eff_gender)
            if canon is not None and canon in canon2ref:
                picked = canon2ref[canon]                            # aliaser cross-variant merge
            elif head in name_surf:
                picked = name_surf[head]                             # blind exact-surface attach
            else:
                picked = UnifiedRef(len(refs))
                refs.append(picked)
                if canon is not None:
                    canon2ref[canon] = picked
                name_surf[head] = picked
            picked.update(order, role, gender=eff_gender, number=m.get("number"), mtype="name",
                          head=head, name_toks=name_toks, cluster=cluster)
        else:           # COMMON -> head-lemma + recency (Ariel: definite NP by recency, not salience)
            cg, cn = m.get("gender"), m.get("number")
            cands = [r for r in refs if r.last_time < order and head in r.heads
                     and compatible(cg, cn, r.gender, r.number)]
            if cands:
                picked = max(cands, key=lambda r: r.last_time)       # most-recent same-head
            else:
                picked = UnifiedRef(len(refs))
                refs.append(picked)
            picked.update(order, role, gender=cg, number=cn, mtype="common",
                          head=head, name_toks=(), cluster=cluster)
    return records


__all__ = ["resolve_unified_stream", "UnifiedRef", "UNIFIED_DECAY"]
