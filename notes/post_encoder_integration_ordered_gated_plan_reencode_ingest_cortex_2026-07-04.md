# Post-encoder integration: ordered gated plan (verify -> re-encode -> dogfood ingest -> cortex)

**Date:** 2026-07-04. **Type:** research/planning drill (NO experiment dispatch). **Author:** Director.

Answers the USER's question: *"worth planning exactly the next steps after confirmation -- is the
first step to make sure the entire substrate is properly encoded, and start ingesting additional
data?"*

## 0. TL;DR recommendation

**The first step is NOT re-encode or ingest. It is INTEGRATION-VERIFY: prove the trained encoder
actually works INSIDE the live substrate (store -> retrieve -> compose end-to-end), not just in the
offline eval harness.** The USER's instinct is correct in *substance and order* -- yes, re-encode the
existing substrate BEFORE ingesting new data -- but there is a mandatory gate in front of both: you
cannot trust a re-encode you have not verified in-situ, and you cannot trust an ingest onto vectors
whose in-situ retrieval you have not confirmed. Integration-verify is cheap, local-CPU, and
**fork-independent** (it tests whichever checkpoint ships), so it is the maximum-unblock, zero-fork-risk
action to take the moment the encoder ship is decided.

**Ordered plan:** `0 integration-verify -> 1 BCT-safe re-encode -> 2 controlled dogfood ingest ->
3 M3 cortex-2 resume` (`4 general-knowledge ingest` stays USER-LOCKED "not yet", out of scope).

## 1. First-principles ordering argument (why 0 before 1 before 2)

The dependency chain is strict:

1. **You cannot trust a re-encode or an ingest until the encoder is verified working in-situ.** Offline
   `ret_agree10 = 0.20-0.41` is measured in a numpy eval harness. It does NOT exercise the live path:
   the real PartitionedStore write/read API, complex64/FHRR serialization, the sparse block-code storage
   format, cleanup-memory readout, and the ANN/cosine metric the store actually uses. A single
   normalization or dtype mismatch between the offline harness and the live store silently degrades
   retrieval -- the classic integration bug, invisible to offline eval. **=> Step 0 must come first.**

2. **You cannot ingest-new until existing content is compatibly re-encoded.** If new atoms enter on the
   new encoder while old atoms sit on the old space (`char_trigram_v1` KB index, or BGE teacher vectors,
   or nothing), the two populations live in DIFFERENT vector spaces and cross-retrieval collapses to ~1%.
   This is not a hypothesis -- it is the MEASURED result of `exp_encoder_cross_checkpoint_retrieval_compat_v1`
   (SAME-version top1 = 1.0, CROSS-version top1 = 0.010-0.015, random floor 0.0002). A mixed-encoder store
   is a silently-broken store. **=> Re-encode (1) before ingest-new (2).**

3. **Re-encode itself is destructive-adjacent and must use BCT or it silently invalidates every stored
   vector.** `exp_encoder_bct_compatibility_loss_v1` (HARD_PASS, full) proves the BCT compatibility loss
   (w=0.15) restores cross-version min_ratio 0.0 -> 0.887 at 83.6% quality retention -- i.e. re-encode
   becomes NON-breaking. Without it, step 1 is the compat-probe failure by construction. **=> Step 1
   depends on BCT wiring, not just on "run the encoder over the atoms".**

So: **verify the plumbing (0) -> convert existing content safely (1) -> add new content (2)**. The
USER's "make sure the entire substrate is properly encoded" IS step 1; "start ingesting additional data"
IS step 2; the missing piece is the verify-gate (0) in front, and the BCT-safety wrapper around (1).

**One disambiguation the plan forces up front (a step-0 sub-task):** "re-encode the ENTIRE substrate"
needs scoping. Today the substrate holds THREE candidate representations -- the `char_trigram_v1` lexical
KB index (a retrieval convenience), any BGE teacher vectors, and the new sparse concept code. Do NOT
blindly re-encode everything. Step 0's first act is to INVENTORY which stores/lanes hold which
representation and which operational query paths (Layer-0 dense retrieval, Layer-0.5 KG-walk, cortex
consult, M3 agent) read which -- then scope the re-encode to the concept-vector representation those
paths actually use. This is also where the known addressability breaches (5000-line KB cap;
wikipedia-in-math-lane = 17 atoms) get audited, per the ingest-completeness integrity contract.

## 2. The ordered gated plan

| # | Step | GATE (entry precondition) | SUCCESS criterion (exit) | Top risk | Rough effort |
|---|------|---------------------------|--------------------------|----------|--------------|
| **0** | **INTEGRATION-VERIFY in-situ** | Encoder fork resolved (lever-B verdict landed); checkpoint chosen | In-situ `ret_agree10` within +/-0.03 of the offline number for the SAME encoder+K, measured THROUGH the real store write/query API; algebra keyed@J5 within tol of 1.00 across a store roundtrip (write->serialize->read->bind/unbind/cleanup); dtype/norm/shape asserted at write AND read (zero silent mismatch); store/representation inventory + addressability audit done | A normalization/dtype/metric mismatch between offline harness and live store silently collapses retrieval (sparse block code + cleanup memory that assumes dense unit vectors). Also: store re-normalizes the code; ANN uses dot vs cosine mismatched to calibration | SMALL. 1 cell, local CPU, few-hundred concepts. No GPU. Build now (fork-independent), run on ship |
| **1** | **BCT-safe RE-ENCODE existing content** | Step 0 PASS + encoder shipped with BCT anchoring (or first-encode into a fresh space with atomic full rebuild) | 100% of in-scope atoms re-encoded (`atoms_reencoded == atoms_in_store` completeness assert -- no silent truncation); post-re-encode known-item probe retrieves at the step-0 in-situ level; if a version SWAP: cross-version min_ratio >= 0.5 (BCT floor); ZERO atoms stranded in the old space; cross-checkpoint compat probe re-run as acceptance gate | **Mixed-encoder store** (some atoms old, some new) -> cross-retrieval ~1% (the compat-probe finding). Also: re-encode without BCT when unreachable external caches exist (silent invalidation); vector rewritten but ANN/cleanup index left pointing at stale vectors | MEDIUM. Compute is small (thin substrate) but CARE is high: atomic single-writer bulk write (partition writes are NOT concurrency-safe), pre-write snapshot, completeness assert. Route via Orchestrator, not hand-rolled |
| **2** | **Controlled DOGFOOD INGEST (our own research/notes)** | Steps 0+1 PASS (existing content verified + compatibly encoded) | Curated known-item probe (20-50 concepts we KNOW are in the ingested notes) returns at rank-1 above floor (top-1 >= 0.8); completeness assert (`atoms_in == atoms_expected`); no placeholder labels (real strings in `name`); addressability verified (new atoms reachable via the SAME query path cortex/M3 will use -- mind the 5000-line cap); pipeline is repeatable/asserting/atomic; measurable KB thickening (atoms/entity rises from ~1.6) | (a) silent truncation (5000-line KB cap -> ingested but unreachable); (b) placeholder labels; (c) dedup collapses distinct relations to one type (the Wikidata mono-typic `DEPENDS_ON` regression) -- MUST use predicate-inclusive dedup + open relation vocab; (d) shipped retrieval too low -> dogfood near-neighbor retrieval marginal; (e) chunk granularity misaligned with query granularity | MEDIUM-LARGE. Pipeline design + validation. START SMALL (50-200 notes), verify known-item retrieval before scaling |
| **3** | **RESUME M3 CORTEX-2 stages** | Step 2 PASS (thicker, properly-encoded, properly-addressable atom set to consult) | Phase-2 first-probe gates (per `research_drill_cortex_2_phase_2_advisory_to_enforcement_architecture`): nonce-consumption >= 0.90 all cases; null-arm vs real-arm KS p<0.01 for >=3/5; dose-response monotone over a swept recommendation; per-atom SHADOW->WARN->LIVE graduation. NOT CG until (a)+(b)+(c) all fire | Decorative enforcement -- cortex "applies" a recommendation the downstream routine never reads (the write-nonce + null-arm A/B discriminator exists exactly to catch this). Advisory quality degrades if atom retrieval is weak | LARGE. The real M3 prize; multi-cell arc. Stage-1 physics-map / K-sweep can run IN PARALLEL (encoder-independent) to keep idle GPU fed |
| **4** | **GENERAL-KNOWLEDGE INGEST** | **USER-LOCKED "not yet" -- explicit USER decision to lift; do NOT assume** | (out of scope) The encoder removes the QUALITY blocker that was the stated reason for the lock, so it becomes REVISITABLE -- gated on USER consent + step-2 having PROVEN the pipeline + retrieval quality adequate on the real task | n/a | n/a (deferred) |

## 3. Integration-verify (step 0) -- the concrete end-to-end test

The offline `ret_agree10` is NOT sufficient. The in-situ test:

1. **Inventory** the stores/lanes and which representation + query path each uses (the disambiguation
   above). Output: the exact scope of "the substrate" that the encoder governs.
2. Take a held-out set (a few hundred concepts), **encode with the shipped checkpoint**, and **WRITE them
   to a fresh test PartitionedStore partition** via the real store API (not the numpy harness).
3. **Retrieve** with held-out probes THROUGH the real store/cleanup path; measure top-k retrieval.
4. **Compose across the store roundtrip:** bind two STORED concepts, unbind, cleanup -- verify the
   keyed@J5 algebra roundtrip survives serialization/dtype/normalization (this is what an offline eval
   never touches).
5. **Assert** dtype/norm/shape at write and at read; assert the store's similarity metric matches the
   encoder's calibration (cosine vs dot).

**Pass gates:** in-situ ret_agree10 within +/-0.03 of offline for the same encoder+K; in-situ keyed@J5
within tol of 1.00; zero silent format/normalization mismatches. A GAP between in-situ and offline is
itself the finding -- it localizes an integration bug the offline number hides.

## 4. Re-encode (step 1) -- mechanics, what breaks, verification, rollback

**Procedure:** (a) scope to the concept-vector representation the operational paths use (from step 0);
(b) confirm the shipped encoder was trained WITH the BCT compatibility loss anchoring it to the prior
representation -- OR, if migrating from a non-comparable prior (char-trigram) where "compatibility" is
moot, plan an ATOMIC full rebuild of every consumer so no old cached vector survives; (c) snapshot the
store; (d) single-writer atomic bulk re-encode (`.tmp` + rename, respecting the not-concurrency-safe
partition-write gotcha); (e) rebuild the ANN/cleanup index over the NEW vectors.

**What breaks if done wrong:** a mixed-encoder store (partial re-encode, or external caches missed)
collapses cross-retrieval to ~1% -- silently. A vector rewrite that skips the index leaves the index
pointing at stale vectors.

**Verify no stored vector is silently invalidated:** re-run `cross_checkpoint_retrieval_compat` as the
acceptance gate; assert `atoms_reencoded == atoms_in_store`; known-item spot-check.

**Rollback:** restore the pre-write snapshot. BCT is the deeper insurance -- because every version is
anchored, re-encoding again when the encoder improves (v1->v2) is non-breaking, so a premature re-encode
is recoverable, not fatal.

## 5. Dogfood ingest (step 2) -- pipeline, "controlled", failure modes

**Pipeline:** chunk research/notes -> extract concept atoms + relations -> encode with the shipped
encoder -> dedup on a **predicate-inclusive key** `(subject, predicate, object)` -> A5-gated write.
Relations are **ATOMS in an open vocabulary (no closed enum)**, FHRR-encoded so they compose with
bind/unbind and support relation-similarity + slow drift. Never refuse a triple because "we don't know
that relation."

**"Controlled" means:** start with a handful of KNOWN notes; verify retrieval on known items (query a
concept you KNOW is in note X, confirm rank-1) BEFORE scaling; completeness assert; addressability check
against the operational query path (the 5000-line cap will silently hide new atoms if unaddressed).

**Failure modes:** silent truncation (the cap); placeholder labels; relation-vocab collapse (mono-typic
`DEPENDS_ON` regression); chunk-granularity vs query-granularity mismatch; and -- load-bearing --
**shipped retrieval too low to serve the Director-KB dogfood use case.** This last point is a FEATURE:
step 2 is the floor-check of the encoder's retrieval target on the REAL downstream task. If K128@0.20
retrieval makes dogfood retrieval marginal, that is direct evidence for shipping the denser fallback or
pushing lever B harder -- exactly the "floor-check the target task class" discipline.

**Scope lock:** step 2 is DOGFOOD-ONLY (our own research/notes = the "substrate as Director-KB dogfood"
vision). It does NOT lift the general-knowledge ingest lock. General knowledge (Wikipedia, books, common
crawl) remains USER-LOCKED "not yet" -- an explicit USER decision, not implied by the encoder shipping.

## 6. Where this rejoins M3 cortex-2 (step 3) and the parked Stage-1 gaps

The cortex-2 arc (LIVE-mode ring rollout) was PARKED behind the encoder. It resumes at step 3 BECAUSE
cortex consults ATOMS: a thicker, properly-encoded, properly-addressable substrate makes advisory
consultation meaningful, and the open-relation-vocab **consolidation loop** (neocortical-analog: observe
N witnesses -> propose a new relation) is itself a cortex function that needs BOTH the encoder (to encode
new relations as FHRR vectors) and the ingest pipeline (to have witnessed patterns). Cortex genuinely
sits downstream of encoder + ingest.

Stages resume as designed: **advisory (Phase 1, DONE, match-and-honored 0.80) -> per-atom SHADOW/WARN/LIVE
graduation (Phase-2 apply-mode, two-part write-nonce + null-arm discriminator) -> dose-response (monotone
over a swept recommendation) -> multi-atom.** Not CG until nonce-consumption + null-arm-effect +
dose-response all fire (per the cortex-2 phase-2 memo). The parked **Stage-1 physics-map / candidate
K-sweep** work is encoder-INDEPENDENT and should run IN PARALLEL to keep idle GPU fed while the
encoder-integration path (steps 0-2) is CPU-light.

## 7. Fork-independent vs density-dependent (holds for K128-2% OR K372/K512-denser)

- **Step 0 (integration-verify): FORK-INDEPENDENT.** Identical test; plug in whichever checkpoint ships.
  This is precisely why it is the right FIRST step -- maximum unblock, zero fork risk. Build it now, run
  it the moment the ship is decided.
- **Step 1 (re-encode): procedure fork-INDEPENDENT; TIMING mildly fork-dependent.** Do NOT bulk-re-encode
  onto a checkpoint about to be superseded by lever B -- re-encode onto the SETTLED ship. BCT makes even a
  premature re-encode recoverable.
- **Step 2 (dogfood ingest): pipeline fork-independent; ingest QUALITY density-dependent** -- and that
  dependence is the useful floor-check on the real task (see section 5).
- **Step 3 (cortex): mostly fork-independent** (mild advisory-quality dependence on retrieval).
- **Step 4 (general knowledge): out of scope, USER-locked.**

**Net:** the plan is robust to the encoder fork. The only fork-sensitive knob is the TIMING of the bulk
re-encode (wait for the ship) and the QUALITY the dogfood ingest reveals (which itself becomes evidence
in the fork decision). Everything structural holds whether we ship 2%-sparse K128 or the denser fallback.

## 8. Intuitive summary

**What this is:** the plan for what happens the moment the encoder is called -- turning a trained
component into a working part of the live system. **Why it matters:** the encoder is the foundation
everything above it (cortex, conversation, self-improvement) sits on; wiring it in wrong -- silently --
would poison every stored memory. **The key insight:** the USER's instinct (encode the whole substrate,
then ingest more) is right, but there is a cheap, must-do step in front of it: PROVE the encoder works
inside the real system before trusting it to rewrite everything. We already have the two hardest facts
in hand -- an encoder swap silently breaks stored memories (measured), and a compatibility trick makes
swaps safe (measured, near-free) -- so the risky part is de-risked; what remains is disciplined plumbing.
**Progress/position:** we are at the encoder's decisive verdict; this memo is the runway on the far side
of it, and it holds regardless of exactly how sparse the shipped encoder is. **What's next after this
runway:** the real prize -- the cortex layer that lets the substrate act on its own knowledge -- which
has been waiting behind the encoder all along.
