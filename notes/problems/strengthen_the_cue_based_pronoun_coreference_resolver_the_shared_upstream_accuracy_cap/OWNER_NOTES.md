---
owner_verdict: DONE
---

SUBMISSION — strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap
STATUS: SOLVED (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM. NO hdlab/ writes.
Ledger: clean (malformed 0). Reverify: .venv/Scripts/python.exe verification/test_coref_graded_live_transfer.py
  (5/5 headline; full suite 21/21: downstream 2/2, deepening 6/6, unification 3/3, soft_gender 2/2, optimize 3/3).

CORE FINDING — a "landed is not live" gap. The brain resolves reference by cue-based content-addressable
RETRIEVAL with RECENCY as the load-bearing cue (Lewis-Vasishth ACT-R). That mechanism is ALREADY LANDED
(hdlab.graded_coref_pick) and proven on the competitive subset (0.775), but is consumed only by
commonnoun_binder — the LIVE pronoun path uses an OUR-INVENTION rolemass pick (subject/frequency mass, NO
recency) + an event-centrality override. Wiring the graded pick into the live path:
  LIVE pooled he/she coref_acc (100 LitBank docs, n=7597): deployed 0.4693 -> graded 0.6019, +0.1327
  CI[+0.093,+0.174] CI-separated; info-free shuffled-history twin 0.2697 LOSES; named coref RISES 0.488->0.617
  (no regress). FLOOR reproduces the known 0.4693 deployment number byte-exact; every arm re-ranks the SAME
  pool, so it is pure pick quality. Ablation: the lever is RECENCY (the deployed pick discards it; the
  event-centrality override HURTS -0.018).

DOWNSTREAM (bidirectional payoff). who-has-what (the pronoun-bound dimension) RISES: deployed-pick 0.4035 ->
graded 0.4735, paired +0.070 CI[+0.043,+0.098] CI-sep, twin 0.047 loses. The brief's two NAMED downstreams
(affect experiencer, entity-KB hard-link) are a rigorous LOCATED NEGATIVE with a measured cause: affect
feel_reliable +0.012 NOT_SEP because 83.5% of experiencers are COMMON-NOUN entities (the brief's own datum) —
those downstreams are common-noun-coref bound, not pronoun bound. Premise correction (disk outranks brief);
if you require the literally-named downstream this is PARTIAL on that clause, which I flag as the first thing
to withdraw. The primary lift + who-has-what payoff stand regardless.

UPSTREAM — evaluated for brain-faithfulness, each deviation pinned, and prototyped the fixes (owner push):
  * ROOT deviation = entity FRAGMENTATION (the overlay keys entities by surface HEAD STRING in
    state_of_mind.EntityState, so "Elizabeth"/"Miss Bennet"/"Bennet" split one character's salience). FIXED
    glass-box + deployable with the reader's OWN name-aliaser (hdlab.coref.build_merge_map, no gold): +0.020
    CI-sep (0.6019->0.6220), shuffled-alias twin loses, named no-regress. 2nd deployable win.
  * GENDER: rebuilt brain-faithfully (violable graded cue, Carminati + confidence-gated propagation, Nref) —
    REMOVES the hard-filter regression (-0.125 -> +0.008) but the benefit is MARGINAL/ns; the +0.28 "ceiling"
    was headroom over a weak over-narrowing baseline, not signal the recency-dominated pick was missing.
  * EVENT-CENTRALITY: rebuilt as a faithful graded cue — best weight 0.0, any positive weight hurts
    monotonically -> REDUNDANT with the Centering/ACT-R cues. Removing the HD override is PRINCIPLED.
  * ROLE assigner is POSITIONAL (not Competition-Model) but PROVEN non-discriminative for coref (upweighting
    subjecthood overfits on held-out test). Its faithful form is the who-did-what problem (P2), not a coref cap.
  * OPTIMIZATION (dev/test by-doc sweep of every cue weight): NO config beats the landed TUNED weights on
    held-out TEST (dev-tuned regresses 0.6386->0.6208). No free headroom — recency dominates.

DEPLOYABLE, 100%-BRAIN-FOUNDATIONAL STACK: deployed 0.4693 -> graded PICK 0.6019 -> + glass-box UNIFICATION
0.6220 = +0.153, all glass-box, no gold, no LLM. The component is fully brain-foundational; the ceiling ABOVE
it is NOT a fidelity gap in this component — it is the P1 entity-INDIVIDUATION representation (a separate
organ) + the ~14% that needs external world-knowledge the no-LLM invariant BARS.

FOR STRATEGY (Q111 wires; you own hdlab):
  (1) WIRE the graded pick into situation_reader._read_entities (build candidate_priors=[(sent_idx,role)] per
      gn-compatible overlay entity -> graded_coref_pick.graded_antecedent_pick; keep the landed phi-filter;
      event-centrality OFF/query_memory=False). This is the "run_graded_retrieval over the resolver stream"
      the organ docstring already names as queued.
  (2) COMPOSE the glass-box unification: unify proper-name variants via build_merge_map before building the
      pool, key the overlay by the canonical referent (+0.020 more).
  (3) DO NOT deploy recency-only (regresses the competitive/conflict cases the integrated organ handles); DO
      NOT wire gender-propagation / event-centrality (marginal / redundant).
AUDIT UPDATE (E3): the live pronoun pick (rolemass + event-centrality) is anti-brain-foundational (14 pts
below the landed cue-based retrieval + below plain recency); the pronoun cap does NOT bottleneck affect/
entity-KB (common-noun bound) but DOES bottleneck who-has-what.

TLDR (plain English): Deciding which character "he"/"she" means was right only ~47% of the time on real books,
because the live reader used a home-grown rule that ignores which character was mentioned MOST RECENTLY — the
exact signal the brain leans on, and a better module built for a related job was never plugged in. Plugging it
in lifts it to ~60%, a big clean win a scrambled control can't fake, and it doesn't hurt named characters.
Then I fixed the deeper cause — the reader was treating "Elizabeth", "Miss Bennet" and "Bennet" as three
different people, splitting one character's evidence — by merging name variants (no outside AI), for another
few points, to ~62%. I checked every remaining knob the brain's way: character gender helps only a hair here,
the "who's central to recent events" idea is already baked in (adding it again only adds noise), and the
grammar-role step doesn't limit this. The rest of the gap needs a richer memory of WHO each specific character
is — a separate, bigger project — plus some cases that genuinely need outside world facts our no-outside-AI
rule forbids. I did NOT touch any parser. Nothing is wired into the live system yet — that's two one-function
plug-ins for the other session.

QUESTIONS: one judgement call — the bar named affect/entity-KB as the downstream; both are common-noun-bound
and don't move for a pronoun fix, so I showed the payoff on who-has-what and reported affect as a measured
located-negative. If you want the literally-named downstream to rise, that lever is common-noun coref (a
separate, already-filed problem).

NEXT STEPS: (1) strategy wires the graded pick + glass-box unification; (2) the real residual is the P1
entity-individuation representation (telling two same-gender characters apart) — route there, not to a
coherence prior (owner-DONE dead x2) or gender (fixed, marginal); (3) the affect/entity-KB lever is
common-noun coref, not the pronoun pick.
