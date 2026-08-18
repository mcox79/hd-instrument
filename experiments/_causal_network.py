"""Reusable CAUSAL-NETWORK module: identify the CAUSE of a narrative outcome
("why did X happen?") by building a running causal network over event bundles, and
bind the cause->effect edges into the substrate's KGStore (glass-box in-substrate
causal graph; on-chain vs dead-end = reachable-to-outcome).

Brain grounding (Trabasso & van-den-Broek CAUSAL-NETWORK model of discourse):
events on the causal chain from opening -> outcome are recalled 2-3x more than
dead-end events; "why?"-answerable == on-chain. Readers link cause->effect via
(a) CONNECTIVES (because/so/therefore/since/thus), (b) temporal-contiguity +
selectional PLAUSIBILITY, (c) FORCE-DYNAMICS (Talmy CAUSE/ENABLE/PREVENT). Readers
BRIDGE unstated causal links to keep coherence ("He dropped the glass. It shattered.").

THE DISCRIMINATOR (inverse of the coref-locality lesson): for coref the true
antecedent is the NEAREST mention (locality wins). For causation the true CAUSE is
often NOT the most-recent event -- the causal link jumps back over intervening
dead-end events. A naive MOST-RECENT baseline (cause == the immediately-preceding
event / prior sentence) therefore FAILS where cause != most-recent. A pure
CONNECTIVE-ONLY baseline FAILS on BRIDGING cases (no explicit because/so). Only a
causal-network reader that combines connective + plausibility clears BOTH.

Reuse: extract_events from experiments._temporal_ordering (content-verb events with
tense); hdlab.kg_traversal.KGStore (multi-value Hebbian (s,p,o) store) for the
in-substrate causal graph + one-hop / n-hop causal traversal (the P12 chain-grade
primitive). ASCII-only, deterministic given a fixed codebook seed.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_ordering as T  # noqa: E402  (extract_events, Event)
from hdlab.kg_traversal import KGStore  # noqa: E402

# Causal connectives (SUPPLIED closed classes = structure supplied, the throughline).
# CAUSE_FIRST: "A. So/Therefore B" -> the earlier clause is the CAUSE, later the EFFECT.
CONNECTIVE_CAUSE_FIRST = {"so", "therefore", "thus", "hence", "consequently", "accordingly"}
# EFFECT_FIRST: "B because/since A" -> the clause AFTER the connective is the CAUSE.
CONNECTIVE_EFFECT_FIRST = {"because", "since"}
CAUSAL_CONNECTIVES = CONNECTIVE_CAUSE_FIRST | CONNECTIVE_EFFECT_FIRST

# Force-dynamics closed classes for BRIDGING inference (Talmy CAUSE). An ACTION verb
# (an agonist exerting force) followed by a RESULT change-of-state verb of the
# affected entity = an inferred CAUSE link when no connective is present.
FORCE_ACTION = {
    "caught", "slipped", "stopped", "threw", "struck", "pushed", "hit", "shouted",
    "dropped", "seized", "grabbed", "knocked", "kicked", "flung", "tripped", "shoved",
    "hurled", "swung", "plunged", "dashed", "hurtled",
}
RESULT_STATE = {
    "fell", "started", "shattered", "broke", "burst", "flared", "spilled", "crashed",
    "tumbled", "toppled", "snapped", "rolled", "collapsed", "staggered", "reeled",
}

REL_CAUSES = 0  # single relation index in the KGStore: (effect) --CAUSES--> (cause)


@dataclass
class CausalItem:
    """One 'why did OUTCOME happen?' gold instance over a REAL narrative passage."""
    subset: str            # NONADJ | BRIDGE | CONTROL
    source: str            # verbatim source citation
    text: str              # verbatim passage
    outcome_lemma: str     # the event to explain
    cause_lemma: str       # gold cause (from MEANING; non-circular)


# ---------------------------------------------------------------------------
# Extraction (SHARED across all arms).
# ---------------------------------------------------------------------------
def extract(text, tagger=None):
    """Return (events, token_lowers). events = content-verb Events with token idx."""
    ev, tagged = T.extract_events(text, tagger=tagger)
    return ev, [t[1] for t in tagged]


def _connective_positions(toks):
    """List of (token_idx, kind, word) for every causal connective in the passage."""
    out = []
    for k, w in enumerate(toks):
        if w in CONNECTIVE_CAUSE_FIRST:
            out.append((k, "CAUSE_FIRST", w))
        elif w in CONNECTIVE_EFFECT_FIRST:
            out.append((k, "EFFECT_FIRST", w))
    return out


def _find_event(events, lemma):
    """First event whose lemma matches (gold outcome/cause lookup)."""
    for e in events:
        if e.lemma == lemma:
            return e
    return None


# ---------------------------------------------------------------------------
# The three cue mechanisms (each returns a cause Event or None).
# ---------------------------------------------------------------------------
def most_recent_prior(events, outcome):
    """BASELINE 1 (naive-adjacency / locality): the most-recent event strictly before
    the outcome in text = 'the immediately-preceding event / prior sentence'. This is
    the inverse-of-coref control; it FAILS when the true cause is not the recent event."""
    prior = [e for e in events if e.idx < outcome.idx]
    return prior[-1] if prior else None


def connective_cause(events, toks, outcome):
    """BASELINE 2 (also the mechanism's no-bridge P2 ablation): follow an explicit
    causal connective. EFFECT_FIRST -> first event after the connective; CAUSE_FIRST ->
    most-recent event before the connective. Picks the connective nearest the outcome.
    ABSTAINS (None) when no causal connective is present -> FAILS on bridging cases."""
    cps = _connective_positions(toks)
    if not cps:
        return None
    for ci, kind, _w in sorted(cps, key=lambda c: abs(c[0] - outcome.idx)):
        if kind == "EFFECT_FIRST":
            after = sorted((e for e in events if e.idx > ci), key=lambda e: e.idx)
            if after:
                return after[0]
        else:  # CAUSE_FIRST
            before = [e for e in events if e.idx < ci and e.idx != outcome.idx]
            if before:
                return before[-1]
    return None


def bridge_cause(events, outcome):
    """BRIDGING plausibility (Talmy force-dynamics): if the outcome is a change-of-state
    RESULT, the inferred cause is the nearest preceding FORCE/ACTION event whose force
    brings that state about. Recovers UNSTATED causal links (no connective)."""
    if outcome.lemma not in RESULT_STATE:
        return None
    acts = [e for e in events if e.idx < outcome.idx and e.lemma in FORCE_ACTION]
    return acts[-1] if acts else None


def causal_net_cause(events, toks, outcome):
    """MECHANISM: causal-network reader. Connective link first (structure supplied);
    else bridging force-dynamics plausibility (unstated link); else fall back to the
    most-recent prior event. Returns the DIRECT cause Event (parent of outcome on the
    causal chain)."""
    c = connective_cause(events, toks, outcome)
    if c is not None:
        return c, "connective"
    b = bridge_cause(events, outcome)
    if b is not None:
        return b, "bridge"
    f = most_recent_prior(events, outcome)
    return f, "fallback"


def predict_cause(arm, events, toks, outcome):
    """Dispatch a cause prediction for a named arm. Returns Event or None."""
    if arm == "MOST_RECENT":
        return most_recent_prior(events, outcome)
    if arm == "CONNECTIVE_ONLY":
        return connective_cause(events, toks, outcome)
    if arm == "CAUSAL_NET":
        return causal_net_cause(events, toks, outcome)[0]
    raise ValueError(f"unknown arm {arm}")


# ---------------------------------------------------------------------------
# Full causal-network build over ALL event pairs (for on-chain vs dead-end).
# ---------------------------------------------------------------------------
def build_causal_edges(events, toks):
    """Infer ALL cause->effect edges in a passage (a running causal network).

    For each event treated as a candidate EFFECT, attach its direct cause via the
    mechanism (connective / bridge). Returns list of (cause_lemma, effect_lemma) and
    the per-effect source tag. Edges point cause -> effect.
    """
    edges = []
    tags = {}
    for eff in events:
        c = connective_cause(events, toks, eff)
        tag = "connective"
        if c is None:
            c = bridge_cause(events, eff)
            tag = "bridge"
        if c is not None and c.lemma != eff.lemma:
            edges.append((c.lemma, eff.lemma))
            tags[(c.lemma, eff.lemma)] = tag
    return edges, tags


def on_chain_events(edges, outcome_lemma):
    """Trabasso on-chain set: events reachable to the OUTCOME by following cause->effect
    edges forward (i.e., ancestors of the outcome). Everything else is a DEAD-END."""
    # adjacency cause -> [effects]
    fwd = {}
    for c, e in edges:
        fwd.setdefault(c, set()).add(e)
    # an event is on-chain if outcome is reachable from it
    memo = {}

    def reaches(node, seen):
        if node == outcome_lemma:
            return True
        if node in memo:
            return memo[node]
        if node in seen:
            return False
        seen.add(node)
        ok = any(reaches(nxt, seen) for nxt in fwd.get(node, ()))
        memo[node] = ok
        return ok

    on = set()
    nodes = set([c for c, _ in edges] + [e for _, e in edges])
    for n in nodes:
        if n != outcome_lemma and reaches(n, set()):
            on.add(n)
    return on


# ---------------------------------------------------------------------------
# Substrate glass-box: bind cause->effect edges into a KGStore and recover the cause
# by one-hop traversal from the effect (in-substrate causal recall). REUSES KGStore.
# ---------------------------------------------------------------------------
def build_kgstore(lemmas, n_dim, seed):
    """A KGStore over event-lemma entities with a single CAUSES relation."""
    lemmas = sorted(set(lemmas))
    idx = {lem: i for i, lem in enumerate(lemmas)}
    g = torch.Generator().manual_seed(seed)
    kg = KGStore(n_ent=len(lemmas), n_rel=1, n_dim=n_dim, generator=g, init_entities=True)
    return kg, idx, lemmas


def ingest_edges(kg, idx, edges):
    """Hebbian-write (effect --CAUSES--> cause) so predict_one_hop(effect) recovers cause."""
    if not edges:
        return 0
    triples = torch.tensor(
        [[idx[eff], REL_CAUSES, idx[cause]] for (cause, eff) in edges if cause in idx and eff in idx],
        dtype=torch.long,
    )
    if triples.numel() == 0:
        return 0
    kg.ingest_triples(triples)
    return int(triples.shape[0])


def substrate_recall_cause(kg, idx, lemmas, effect_lemma):
    """Glass-box: one-hop substrate causal recall -- what does the KG say caused effect?"""
    pred = kg.predict_one_hop(idx[effect_lemma], REL_CAUSES)
    return lemmas[pred]
