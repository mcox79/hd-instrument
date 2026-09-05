---
owner_verdict: DONE
---

SUBMISSION -- form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref
STATUS: PARTIAL (WIP until owner_verdict: DONE). Glass-box, NO external LLM. Solver scope: experiments/ +
verification/ + own notes only; proposed hdlab diff below for strategy (Q111). Ledger clean.

REVERIFY:  .venv/Scripts/python.exe verification/test_commonnoun_referent_former.py   (7/7)

WHAT THE BRIEF ASKED vs WHAT'S TRUE (disk outranks the brief):
- Brief: build a glass-box common-noun referent former to recover the +0.43 gold-coref headroom and lift the
  character-bound dimensions. Premise is PARTLY WRONG on disk: the reader ALREADY clusters common nouns
  (surface-head grouping, character-cluster CoNLL 0.605, +0.27 over a proper-name-centric baseline, CI-sep) --
  the character registers just don't consume them; and the "+0.43 headroom" is partly a gold-LABEL-SPACE
  artifact (the affect reference was built from gold coref labels).

THE RESULT (LitBank 100 docs, proper CoNLL MUC/B3/CEAFe, character clusters, doc bootstrap):
1) LOCATED NEGATIVE (a sanctioned full pass): a FAITHFUL cue-based former (ACT-R retrieval extended from
   pronouns to definite descriptions, reusing hdlab.graded_coref_pick) does NOT beat the reader's surface-head
   floor CI-separated (+0.0008, CI[-0.008,+0.009]). Quantified cause: head-match recall 0.341 (66% of literary
   common-noun links use shifting epithets, not the same head); 82% of links have 2-3 competing active persons;
   over-merge errors are 91% content-IDENTICAL. WordNet bridging tags only 7.8% of links.
2) LANDABLE WIN (witnessed, CI-sep, no-regress): the DEPLOYABLE former = head-match-gated + modifier-split
   ("the old man" != "the young man") + wide window + the EVENT-CENTRALITY situation gate (reusing the landed
   hdlab.event_centrality_coref, extended from pronouns) BEATS surface_head +0.0128 CoNLL (CI[+0.006,+0.020]),
   CEAFe 0.469->0.510, info-free twin LOSES (+0.258), no-regress on named (+0.0000). Small but real; generalizes
   (zero fitted params; stable on held-out even/odd halves).
3) THE REAL CAPABILITY, built + proven correct: the proper brain mechanism (research-PINNED: Kintsch/Zwaan/
   Sanford-Garrod/Heim-DRT) is to QUERY an accumulated ENTITY WORLD-MODEL (file cards: type/role/relation/
   event/presence) restricted to the foregrounded set -- NOT weight surface cues. Built it + the confidence
   gate (graded_coref_pick abstain). It CROSSES given records: ambiguous-link resolution 0.255 -> 0.540
   (union-oracle 0.615 -> the facts ARE in the narrative). BUT deployment hits a BOOTSTRAPPING/IDENTIFIABILITY
   wall: self-built records give only +0.006 CoNLL, and 2-pass consolidation + confidence-gating do NOT cross
   it -- you can't build correct entity records without already resolving reference. The brain breaks this with
   a PRIOR WORLD KNOWLEDGE (who "the master" is, who Elizabeth's father is) -- the external prior the no-LLM
   invariant bars, exactly what SOTA imports from a pretrained LM.
DOWNSTREAM (affect experiencer subpop, 160 mentions): name_only ~ surface_head ~ former ~ 0.90 (already
near-ceiling); no downstream dimension rises CI-sep -- the affect loss is label-consistency + pronoun
resolution, not common-noun clustering.

PROPOSED hdlab CHANGE (Q111 -- strategy lands):
(a) LAND the deployable situation-gated former (verbatim body: exp_commonnoun_situation_gated_binder_v1.
    situation_predict(headmatch_gate=True, window=16)) as the reader's common-noun clustering, replacing the
    blind transitive same-head merge. Default-safe (witness is the gate); impact-analyse + turn on if net-positive.
(b) WIRE the reader's common-noun clusters into the character-bound canonicalizers (affect/goal/world-state/
    make_canonicalizer) with a stable head-lemma label -- the +0.27 recovery is computed and currently dropped.
    Pair with the pronoun graded resolver (the downstream residual is pronoun + label-consistency).

NEXT STEPS FOR OPTIMIZATION (ranked): (1) land the deployable former (a); (2) wire common-noun referents to the
registers (b); (3) THE REAL CAPABILITY = an entity-world-model resolver SEEDED BY A WORLD-KNOWLEDGE PRIOR --
file a Phase-1 program: a static offline scenario/role + kinship KB to seed the entity records so the BUILT
resolver realizes its 0.54 ceiling (lifts this + the affect/WSD located negatives together). DO NOT REDO as
coref heuristics (all measured-capped): WordNet bridging, presence/locality (~0.26 gold-oracle ceiling),
possessor-relational binder (+0.0006), 2-pass consolidation (+0.0045), confidence-gating (+0.0056).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md 2b): COREF/common-noun. The reader DOES form common-noun referents
(surface-head, 0.605); the brief's "forms none" is true only at the CONSUMER level (registers are proper-name-
centric). The brain's actual mechanism = QUERY an accumulated entity world-model, not weight surface cues; it
resolves 0.255->0.540 given records but is blocked deployed by an identifiability wall broken only by a
world-knowledge prior. Flag: the affect "+0.43 gold-coref headroom" is partly a gold-label-space artifact.

KEY REALIZATIONS: (1) Ask whether it could succeed FIRST -- the diagnostic (head-match recall 0.341, over-merge
91% content-identical) predicted the negative before any build. (2) The brain re-identifies the ENTITY, not the
WORD -- extend the landed ACT-R op, don't reinvent. (3) Audit the ruler -- the +0.43 headroom is partly a
label-space artifact. (4) The right mechanism (entity-world-model query) CROSSES given records (0.255->0.540);
the true wall is IDENTIFIABILITY (can't bootstrap correct records without a world-knowledge prior), which
precisely names the Phase-1 dependency.

TLDR (plain English): When a story calls someone "the man" or "the master" instead of by name, the reader has
to recognise later mentions as the same person. Two-thirds of the time old novels use DIFFERENT words each time
("the old man"->"the poor fellow"->"her father"), and when the SAME words come back they usually mean a
DIFFERENT person -- so no word-matching rule can tell them apart. The method the brain actually uses is a
running notecard per character (their role, relations, where they are, what they just did) that it looks
things up in; I built that, and it works well WHEN the notecards are right (more than doubling accuracy on the
hard cases). The catch: you can't fill in correct notecards without already knowing who's who -- a chicken-and-
egg the brain solves with outside world knowledge it brings to the story. Built entirely from the reader's own
machinery plus standard word-lists; no outside AI. A small, safe tidy-up to the reader's grouping is ready to
ship; the big win needs a world-knowledge starter kit, which is the clear next project.

QUESTIONS: none.
