# Ingest-arc scoping: encoder gate, mechanism, prerequisites, measurement, staged plan

Date: 2026-07-07. Owner: research (Opus synthesis over substrate scour; 2x-discipline drill on
EXISTING findings per [[feedback-2x-means-depth]] -- this is a level-2 operational/engineering
scoping pass, not a fresh external lit-scan. The load-bearing prior lit-scan (53 citations, CLS
neuroscience + KB-pilot/multi-hop-eval methodology) was already delivered 2026-07-05
(`notes/research_ingestion_readiness_scoped_pilot_5x_angle4_2026-07-05.md`) and is reused/extended
here, not re-run. Field-advisor note: this is a USER-directed engineering-scoping question
(Trigger E-equivalent), so the generic field-coverage heuristic (free-cumulants, Glauber dynamics
etc.) is correctly overridden this cycle, matching the 07-05 note's own precedent.

## HEADLINE

**The near-term ingest pilot is ALREADY dispatch-ready and does NOT need to wait on the encoder
joint-solution VET at all -- it was dispatch-ready before today's relock result and remains
unblocked regardless of the xhigh VET outcome. The encoder gate is real, but it gates a DIFFERENT,
later layer of the ingest vision than the one Director's framing implies.** Two separable ingest
paths exist: (A) retrieval-style KB reasoning (fact lookup + N-hop composition via the substrate's
own internal Hebbian-bind mechanism, proven CHAIN_GRADE on real data, running in the CURRENT
operational encoder space (BGE dense, Space 2) -- zero dependency on the sparse joint-solution
encoder; and (B) native-substrate compositional reasoning where the ENCODER's OWN vectors are the
bind/unbind substrate (the M3 glass-box vision) -- THIS is what the joint solution gates, and it
gates it well: verified TODAY on-disk, both seeds independently, HARD_PASS, at real (not synthetic)
corpus scale. But even path (B)'s verified scale (n=177,899, the CURRENT live PartitionedStore
content) is ~5.5x smaller than the full production KB target (970,069 entities in
`data/substrate_director_kb_v1/entities.jsonl`) that Steps 1-3 of the encoder migration are
actually building toward -- a concrete, measured scale gap, not a hypothetical one.

## Item 1 -- Encoder requirements: does the joint solution suffice, and what's the gap

**On-disk verification (independently re-pulled, not taking Director's framing on faith):**

`data/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed{7,13}/metrics.json`, both
written 2026-07-07 14:42-14:43, both `verdict: HARD_PASS ALREADY_JOINT_SOLVED_VIA_INBATCH`:

| unit (seed 7) | value |
|---|---|
| semantic::INBATCH_BLOCK_REVERIFY (spearman-to-teacher) | 0.8969 |
| keyed::INBATCH_BLOCK_REVERIFY::J5 (acc@1, real key) | 1.0000 |
| shuffled_key::INBATCH_BLOCK_REVERIFY::J5 (acc@1, control) | 0.0000 (clean -- no leak) |
| keyed::RANDOM_BLOCK::J5 (SBC lossless-prior sanity) | 1.0000 (expected, sanity-only) |

Seed 13 matches (spearman 0.8865, keyed 1.0, shuffled 0.0 -- same pattern, per the prereg table).
This is the SAME buried win first surfaced 2026-07-04 in `exp_encoder_migration_step1b_v3c...`
(5/5 seeds, spearman 0.852-0.897, keyed@J5=1.0) -- today's cell (`v4_joint_reverify_relock_v1`)
exists SPECIFICALLY to close the one verification gap that win had: the shuffled-key negative
control had only ever been run for the separately-failing `GLOBAL_BLOCK` arm, never for the
winning `INBATCH_BLOCK` arm. That gap is now closed, cleanly (0.0, not just "low").

**What this measures, precisely:** distillation fidelity (MLP student vs BGE teacher) AND
FHRR-native bind/unbind decodability (SBC block-argmax code, K=128) on the SAME model, jointly, at
`n_train=160,109` / cache size 177,899 (`bge_large_v2_name_177899_54f7cf6a.npz`) -- and this cache
IS the real, currently-live PartitionedStore content (ConceptNet's 133,305 nodes + math/science
atoms + everything else ingested to date; independently cross-checked against the 07-05 note's
`PartitionedStore.all_atoms() = 177,217`, same order of magnitude, same source). **This is a
real-corpus-scale test, not a toy/synthetic one** -- an important upgrade over how the 07-06 drill
characterized it ("never reached/reported... flag as inference, not verified").

**The gap that remains, concretely (verified via `wc -l`):**
`data/substrate_director_kb_v1/entities.jsonl` = 970,069 rows (the literal "970K KB" the Step
1/2/3 encoder-migration cells target for production). The joint solution has been verified at
177,899 (18% of that), not at the full 970K target. Two specific open questions this leaves,
neither yet tested:
1. Does the K=128 SBC block-argmax code's capacity hold at 970K entities, or does the cliff
   documented elsewhere in this project (K/N capacity cliffs, sigma=16, percolation-class collapse
   at high load) start to bite before 970K? The CRLB floor in the v4 prereg (`crlb_floor_computed
   = 0.901` at K=128) is a THEORETICAL bound at the CURRENT scale's assumed sigma, not re-derived
   for 970K's larger vocabulary.
2. Does the MLP student's dense-fidelity (0.89 spearman-to-teacher) hold, degrade gracefully, or
   fall off a cliff as the near-neighbor collision rate rises with 5.5x more concepts competing
   for the same embedding volume (a free-probability / Marchenko-Pastur-style question, matching a
   Tier-1 field-advisor candidate already flagged as fruit-bearing and un-drilled).

**Secondary caveat, not yet gating anything:** `ret_agree10` (retrieval-ranking agreement with
teacher, top-10) is only 0.18 for the winning INBATCH arm (vs the ingest pilot's own proposed
HARD-PASS bar of recall@10 >= 0.80, see Item 4). This metric is NOT currently gated in the v4
cell's verdict logic (dense spearman + keyed acc@1 + shuffled control are the gates). It matters
ONLY if/when the sparse Space-3 encoder is later asked to REPLACE BGE as the retrieval frontend
(path B's eventual production role) -- it does NOT affect path (A)'s near-term plan, which uses
BGE (Space 2) directly and has its own, already-measured retrieval numbers (07-05 note's U1
mechanism: set-recall 0.9896). Flagging this now so it is not silently forgotten if Space-3
migration accelerates.

**Verdict on Item 1: the joint solution SUFFICES for path (B)'s current-scale claim (verified,
clean control, real corpus) and SUFFICES for path (A) trivially (path A doesn't use it at all).
It does NOT yet suffice as a demonstrated production-scale (970K) claim -- that is an open,
falsifiable, cheap-to-test gap (Item 5, Stage 3).**

## Item 2 -- Ingest mechanism: pipeline, built vs missing

Pipeline (raw doc/corpus -> substrate-retrievable, reasoning-composable atoms):

```
raw source (KB dump / doc corpus)
  -> chunk / extract (subject, predicate, object) triples or concept mentions
  -> encode: E[concept] via operational encoder (CURRENTLY BGE dense, Space 2;
     relation R[predicate] as a bound HD role-vector, key = E[s] * R[p] * sqrt(N))
  -> predicate-inclusive dedup key (subject, predicate, object) -- NOT (subject, object) alone
  -> A5-gated write into PartitionedStore (qualified-id namespaced, per-lane)
  -> queryable via Retriever.semantic() / .hybrid() / KG-walk (the LIVE operational path)
```

| Component | State (re-verified against 07-05 note + fresh disk checks) |
|---|---|
| Real external KB physically ingested | DONE. ConceptNet 133,305 nodes / 179,781 edges, committed `e3b3147e`, confirmed still present (`grep -c CONCEPT_NODE concept/atoms.jsonl` unchanged). |
| Multi-hop reasoning + fabrication-refusal mechanism | PROVEN, CHAIN_GRADE, isolated harness (U1 on FB15k-237: set-recall 0.9896, 2-hop 5000x random floor, refuse-gate 0.974/0.958). |
| Ingest-completeness cap / placeholder-label bugs | FIXED (07-03: schema cap raised 5000->200000/file; Wikidata placeholder-label backfill `e28a4f474`). |
| Qualified-id dedup-collision fix (Space 2 store) | DESIGNED + PARTIALLY BUILT, WIRING UNVERIFIED. Cache files matching `qualified_*` convention exist on disk (built 07-04) but zero `.py` files reference that naming pattern; the live loader (`retrieve_cache.py`) selects via a DIFFERENT content-hash mechanism. Unknown, as of today, whether the live Retriever reads the collision-safe cache. |
| Live-path addressability of the already-ingested ConceptNet content | **NEVER TESTED.** This is the single largest unresolved item in the whole ingest arc -- not "missing machinery," a missing VERIFICATION. |
| N8 (`exp_n8_conceptnet_ingest_eval_v1`) | Pre-registered 2026-06-22, cell exists, smoke already HARD_PASS at M=5k. **Still never dispatched as of 2026-07-07** (re-checked status_log for 07-06/07-07: no dispatch entry found). Loose end, zero design cost to pick up. |
| Neocortical-analog consolidation loop (auto-promote new relation after N witnesses) | NOT BUILT. Not required for a first ingest (see Item 3). |

## Item 3 -- Prerequisites: is open-relation-vocabulary / hippo-binding a blocker

**No, not for a first ingest.** The relation-as-atom principle is already the DESIGN used by U1
and N8: relations are bound HD role-vectors (`key = E[s] * R[p] * sqrt(N)`), read from a small,
curated, already-typed relation set (ConceptNet's ~8 relation types; FB15k-237's typed
predicates) -- not a hardcoded Python enum, and not requiring the auto-consolidation loop. The
hippocampal-analog one-shot bind primitive (FHRR bind, A5-gated write) is already substrate-native
and load-bearing for exactly this. What's NOT built -- the neocortical-analog consolidation loop
that would let the substrate propose and promote a genuinely NEW relation type it has never seen
named, after observing N witnesses -- only becomes a blocker at a LATER stage: when ingest moves
past curated-relation-set sources (ConceptNet, FB15k-237, a hand-picked pilot corpus) toward
open-ended document ingest where relation types are not pre-enumerated by the source schema (e.g.
raw Wikipedia prose, arbitrary scientific text). For the staged plan below (Stages 0-2), the
existing curated-relation-set machinery is sufficient. Flag Stage 3+ (broad open-corpus ingest) as
the point where the consolidation loop becomes load-bearing, not before.

## Item 4 -- Measurement: avoiding a vacuous ingest test

Direct lesson import from the self-audit arc (`notes/research_justification_retrieval_rung_scoping...
2026-07-06.md`): that arc found "can the substrate retrieve/round-trip its own records" (Tier-1
self-query) was NOT the meaningful bar -- retrieval alone gave results indistinguishable from a
vacuous positive, and the real signal only appeared once the test required ENTAILMENT (does the
retrieved evidence actually SUPPORT the claim, re-derived from the backing, with a firing control
that breaks it on purpose). The exact same trap applies to ingest: "can the substrate find
something near the query" is not proof it can REASON over ingested knowledge.

The 07-05 note's decisive test (`exp_ingest_knowledge_integration_verify_v1`, spec'd, not yet
dispatched) already builds in the entailment-equivalent discipline and is the correct non-vacuous
design:
1. N=200-300 known-fact probes drawn from ALREADY-INGESTED ConceptNet rows (independently
   confirmable ground truth, e.g. `dog IsA mammal`).
2. Query through the REAL production path (`Retriever.semantic()`/`.hybrid()`), not an isolated
   numpy harness -- this is the live-path-vs-isolated-harness distinction the whole arc is
   organized around.
3. Known-item recall@10 against the live index, PLUS an explicit completeness assert (`atoms
   reachable via query == atoms on disk`) -- catches silent truncation per the ingest-integrity
   principle, not just "did it find something."
4. A carved 2-hop subgraph (MetaQA/CLUTRR-style) run through the SAME live path: 2-hop composition
   accuracy must beat 1-hop baseline by a real margin -- this is the entailment-equivalent control
   (a system that merely retrieves nearby atoms without actually composing relations fails this;
   a shuffled-relation or scrambled-2nd-hop control should collapse it, matching the shuffled-key
   discipline already used on the encoder side).

**Firing control (mandatory, not yet in the 07-05 spec explicitly -- adding here):** run the SAME
2-hop probe with the second hop's relation randomly shuffled (same discipline as the encoder's
`shuffled_key` control). A genuine composition mechanism should collapse toward the random floor;
a mechanism that's secretly pattern-matching on the seed entity alone will not collapse. This
closes the last vacuous-test loophole (a system could pass "beats 1-hop baseline" by retrieval
proximity alone without genuinely composing the second relation).

## Item 5 -- Staged plan (ranked; first cheap smoke identified)

**Stage 0 (do first, dispatch-ready TODAY, zero dependency on the encoder VET):**
`exp_ingest_knowledge_integration_verify_v1` as spec'd in Item 4. CPU-only, no re-encode, no new
ingest -- reuses ConceptNet content already committed + the live query API. This is the actual
"minimal first experiment" the Director asked for. Estimated cost: hours, not GPU-days.
HARD-PASS: live recall@10 >= 0.80 on >=90% of probes AND live 2-hop beats 1-hop+0.02 AND shuffled-
2nd-hop control collapses toward random AND zero cache-collision loss (retrieved count == submitted
qualified-id count). HARD-FAIL: recall@10 < 0.40 OR collision loss reproduces the step-0
1500->1497 pattern at full 177k scale. MIDDLE-BAND: partial signal, diagnose which stage is lossy
before patching.

**Stage 1 (cheap, reuses existing pre-reg, independent of Stage 0's outcome unless Stage 0
HARD-FAILs on collision loss):** dispatch `exp_n8_conceptnet_ingest_eval_v1` (already pre-
registered 06-22, smoke already HARD_PASS). Mechanism-level cert on ConceptNet's readable-entity
variant of U1. If Stage 0 HARD-FAILs specifically on cache-collision loss, fix `retrieve_cache.py`'s
selection path FIRST (small, scoped Testbed/Exp-Dev task, not a research question) and re-run
Stage 0's probe as the acceptance gate before Stage 1.

**Stage 2 (small dogfood-ingest pilot, gated on Stage 0/1 passing, still independent of the
encoder joint-solution VET):** 50-200 of the project's own notes, chunked -> concept+relation
atoms, encoded with the CURRENT OPERATIONAL encoder (BGE, Space 2 -- explicitly NOT the pending
sparse code, avoiding any mixed-encoder-store risk per the re-encode-HELD constraint). Known-item
retrieval probe before scaling further. Matches the field's own pilot-scale convention (FB15k-237
~14.5k/310k, iText2KG 5-15-doc pilots, ATOMIC-2020 validated on a 5k sample against a 1.33M full KB).

**Stage 3 (gated on BOTH Skunkworks' xhigh VET ratifying the joint solution AND a fresh scale-test):**
the production-scale question Item 1 leaves open. Before treating the encoder as ready for the
full 970K-entity production ingest, run a scale-up smoke: re-run the SAME v4 reverify protocol
(dense spearman + keyed@J5 + shuffled-key control) against a teacher cache built at meaningfully
larger scale than 177,899 (even a 2-3x intermediate step, e.g. ~400-500K, would be informative
before committing a full 970K GPU-day). HARD-FAIL trigger: dense spearman drops below 0.82 OR
keyed@J5 drops below 0.90 OR shuffled-key control leaks above 0.10 at the larger scale -- any of
these means the K=128 SBC code needs a capacity fix (density dial / higher K) BEFORE production
ingest, not after. This is the honest "what's still needed if VET deflates the claim" answer:
specifically, a scale-robustness re-test, not a re-litigation of today's result.

**Stage 4 (only after Stage 3 clears, and only if/when open-corpus ingest beyond curated-relation
sources is wanted):** build the neocortical-analog consolidation loop (Item 3's deferred
prerequisite) to unlock relation-vocabulary growth beyond ConceptNet/FB15k-237's pre-typed
predicates.

**Explicitly NOT gated on each other:** Stages 0-2 (near-term, real-content-already-in-store,
BGE-space) and Stage 3 (encoder production-scale readiness) are independent workstreams that can
run in the same cycle. This mirrors the 07-05 note's finding that the knowledge-verification pilot
and the reasoning->generation bridge test are independent prerequisites, not a strict chain -- the
same "run both, don't false-serialize" structure applies here between the ingest-verify track and
the encoder-scale track.

## Cheap decisive test (headline pick)

Stage 0 above: `exp_ingest_knowledge_integration_verify_v1`. No new code dependency beyond a CPU
cell calling the existing `Retriever` API against already-committed ConceptNet content. This is
the single highest-leverage, lowest-cost next action in the entire ingest arc, and it is
independent of today's encoder VET outcome either way.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Stage 0:** HARD-PASS = recall@10 >= 0.80 (>=90% of probes) AND 2-hop > 1-hop+0.02 AND
shuffled-2nd-hop control collapses to within [0, 0.05] of random floor AND zero collision loss.
HARD-FAIL = recall@10 < 0.40 OR collision loss reproduces (retrieved < submitted) OR shuffled
control does NOT collapse (proves the 2-hop "win" was retrieval-proximity, not composition).

**Stage 3 (encoder production-scale):** HARD-PASS = dense spearman >= 0.82 AND keyed@J5 >= 0.90
AND shuffled-key <= 0.10, ALL measured at >=400K-entity scale (not just 177,899). HARD-FAIL = any
of those three degrades past its floor at the larger scale -- names a concrete K/density fix as
the next lever, not a return to the drawing board (the mechanism is proven at current scale; the
open question is capacity-scaling, a narrower and cheaper problem).

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):** P(Stage 0 HARD-PASS) undeflated
~0.55-0.65 (07-05 note's own estimate, unchanged -- nothing about today's encoder result bears on
this path since it's independent); P_deflated = 0.35-0.40, driven by this system's own measured
4-bug base rate in this exact pipeline (5000-line cap, placeholder labels, dup-id collision,
NULL-byte corruption), not generic pessimism. P(Stage 3 HARD-PASS at >=400K scale) is a fresh
estimate, NOT inherited from today's 177,899-scale result: 0.40-0.50 undeflated (capacity-cliff
literature this project has independently confirmed -- percolation-class collapse, K/N ratios --
argues scale-up failure is a real, non-trivial risk, not a formality) -> P_deflated = 0.25-0.35,
capped per the novel-synthesis P<=0.50 rule since no direct scale-ladder precedent exists yet in
this lineage.

## Cross-thread synthesis

This scoping directly composes three already-verified threads without re-deriving any of them:
(1) the 07-05 ingestion-readiness note's machinery inventory + CLS brain-mechanism cross-check
(Tse et al. 2007 schema-fast-path: verify/build a small curated schema first, THEN allow faster
integration of consistent new content -- exactly the Stage 0->1->2 ordering here); (2) the 07-06
justification-retrieval self-audit scoping's vacuous-test lesson (retrieval alone is not proof;
entailment/composition-with-a-breaking-control is), imported directly into Stage 0/Item 4's design;
(3) today's on-disk-reverified encoder joint solution, which this note re-scopes as gating a
narrower, LATER slice of the ingest vision (native-substrate bind/unbind at production scale) than
Director's framing implied, rather than gating the whole arc. The corrected gating structure is
itself the main deliverable of this scoping pass -- it changes "wait for encoder VET, then ingest"
into "ingest-verify now (Stage 0-2), encoder-scale-test in parallel (Stage 3), converge at Stage 4."

## Substrate-product implications

The practical effect for Director: the ingest arc does not need to sit idle waiting on Skunkworks'
xhigh VET. Stage 0 can be authored and dispatched by exp_dev this cycle regardless of that VET's
outcome -- it touches none of the same code, uses BGE (already shipped), and answers the more
urgent open question (is real, already-ingested knowledge actually reachable through the path M3/
cortex will use, which is currently UNKNOWN, not merely "not yet built"). If Skunkworks' VET
ratifies the joint solution, Stage 3's scale-test becomes the natural next encoder-track move (a
narrow, cheap, capacity-focused re-test, not a repeat of today's win). If the VET instead deflates
today's claim (e.g. finds an issue the two-seed sample didn't surface), Stage 0-2 are entirely
unaffected and the encoder-track fix is scoped exactly as this note's Item 1 gap analysis
describes -- either way, Director has a concrete next action available immediately.

## Citations (verified count: 0 new external sources this cycle -- 2x-drill on existing findings
per discipline; the 53 sources underlying the CLS/brain-mechanism and KB-pilot/multi-hop-eval
claims reused here are already cited in full in
`notes/research_ingestion_readiness_scoped_pilot_5x_angle4_2026-07-05.md`, not re-verified or
re-listed to avoid double-counting a lit-scan that did not change)

## Prior work / on-disk artifacts checked this cycle (not re-derived, cited)

- `data/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed{7,13}/metrics.json` --
  independently re-pulled per-unit numbers (not trusting verdict_msg alone, per [[feedback-verify-
  the-referent-arrives]]).
- `preregs/2026-07-07_exp_encoder_migration_step1b_v4_joint_reverify_relock_v1.md` -- full band
  design, cardinality, dispatch plan.
- `data/substrate_director_kb_v1/entities.jsonl` (970,069 rows, `wc -l` verified) vs the encoder's
  tested cache (177,899) -- the scale-gap finding is a fresh disk cross-check, not inherited.
- `notes/research_ingestion_readiness_scoped_pilot_5x_angle4_2026-07-05.md` -- machinery inventory,
  cheap-test spec, staged Tier 0/1/2, brain-mechanism synthesis (reused, extended, not repeated).
- `notes/research_justification_retrieval_rung_scoping_unblocked_by_source_direct_2026-07-06.md` --
  vacuous-vs-entailment test lesson (imported into Item 4's firing-control addition).
- `notes/project_substrate_ingest_completeness_and_addressability_USER_2026-07-03.md`,
  `notes/project_substrate_open_relation_vocabulary_no_closed_enum_USER_2026-07-03.md`,
  `notes/project_M3_M4_milestones_glass_box_conversational_agentic_USER_2026-06-26.md` --
  USER-locked constraints this scoping respects throughout (no re-encode proposed as step 1; M3
  capability-block framing for what "ingest" is ultimately in service of).
- `data/orchestrator_status_log.jsonl` -- grepped for N8/ingest-verify dispatch status (confirmed:
  neither dispatched as of 2026-07-07, still a live open item).
