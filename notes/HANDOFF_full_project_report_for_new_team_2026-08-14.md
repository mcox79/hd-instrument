# hd-instrument — Complete Project Handoff Report

**For:** the incoming team (nibalyst + Opus 5.0) taking over the substrate.
**Date:** 2026-08-14. **Author:** outgoing Director session.
**Status of numbers:** every commit hash and metric below was read off disk (git + `data/exp_*/metrics.json`) by two independent disk-verification passes; anything not re-derivable is marked **UNVERIFIED**.

> **How to read this doc.** §0 is the 60-second version. §1–§4 are *why the project is built the way it is* (mission, invariants, philosophy, the baseline arguments — read these before touching code). §5 is *what exists and how it's wired*. §6 is *everything we've tried and what it returned* (the results ledger, including the negatives). §7 is *where the frontier actually is right now* — read it honestly, it is not a victory lap. §8 is the do-not-re-tread list. §9 is how to operate the project day-to-day. §10–§12 are open questions, where everything lives, and your first moves.

---

## §0 — Executive summary (read this first)

**What this is.** `hd-instrument` is a **glass-box hyperdimensional-computing (VSA/HDC) substrate** — a knowledge system whose every representation and inference step is inspectable (unbind + cleanup, no opaque weights at inference). The north star is a substrate you can **converse with that genuinely reasons**, built to a hard invariant: **no LLM at inference time**. It is meant to *learn a body of knowledge by reading, reason over it, and self-direct its reading toward its own gaps.*

**Where it stands (honest, two lenses that must be held together):**
- **The growth MECHANISM works and is clean.** Reading real modern curriculum grows the grounded foundation from a ~360-word seed to **3,544 grounded concepts / 7,966 facts** (~9.9×), with the controls that matter passing: no-leak (0 violations), scramble-discrimination (0.077 ≪ 0.5), and persistence that round-trips **bit-identical** and **survived a mid-run process death**. The substrate can also now **self-direct what to read next** (identify the missing prerequisite — "read math before quantum" — precision 1.0 vs 0.0 ablated).
- **The QUALITY of what it grounds does NOT yet clear its own gate.** The live grounding-readout is at a measured floor: open-vocabulary hit@1 **4.80% vs 0.80% scramble** — 6× its scramble floor, but the ≥10% revival gate is RETIRED (2026-08-14) and C3 now FAILS the four-condition hardened gate (`tools/c3_gate.py`; `notes/c3_gate_hardening_2026-08-14.md`). The defect is localized and specific: **within-neighbourhood separation** — the substrate lands in the right *neighbourhood* but picks the wrong *member* (axon→dendrite, artery→vessel). Retrieval is healthy (self-retrieval 0.786); supply is closed; the problem is discriminating near-paradigmatic members.

**The one problem to pick up first:** close the grounding-*quality* gap (within-neighbourhood separation), i.e. make what the substrate grounds not just *clean* but *correct and well-separated*. Everything else (speed, scale, more reading) is gated behind that.

**The single most valuable cultural asset to preserve:** the **layered-controls + fair-test discipline**. This program's credibility comes from *killing its own false positives* — every apparent comprehension win is run through scramble + ablation + no-leak + held-out, and several confident hypotheses (and one "cross-the-Rubicon" conclusion) were correctly *retracted* by their own controls. Keep that reflex. It is the reason the numbers in this doc can be trusted.

---

## §1 — Mission & North Star

Build a **glass-box substrate that can hold a conversation and genuinely reason** — not retrieve, not pattern-match, but compose stored knowledge into answers whose derivation is fully inspectable. Concretely, the milestone chain is:

1. **Learn a body of knowledge by reading** real curriculum (in progress; mechanism proven, quality gated).
2. **Reason over it** to answer questions it was never directly told (multi-fact composition).
3. **Self-direct its reading** toward its own gaps (prerequisite-first; landed as a controlled capability).
4. → **Converse** — the receptive/comprehension side is largely built; the expressive/production side (question→query, surface realization, dialogue state) is the next major construction.

The "why glass-box, why no LLM at inference" is not aesthetic — it is the product thesis: an auditable reasoning system whose every step can be shown. An LLM may be used **offline** to build a vetted knowledge foundation (this was pre-authorized — the "07-14 pivot"), but the **runtime must stay glass-box with no LLM in the loop**. That invariant is load-bearing; do not relax it without an explicit charter decision from the project owner.

---

## §2 — The invariants (non-negotiable)

1. **Glass-box at inference, always.** Every inference is unbind + cleanup over inspectable hypervectors. No opaque model in the runtime path. This *overrides* other preferences when they conflict.
2. **No LLM at inference.** Offline LLM use to build/vet a foundation is permitted (authorized 2026-07-14); runtime LLM use is not.
3. **Brain = the reference standard.** The brain is treated as an existence proof that the target capability is achievable (100% achievable), and as the design template. Default to the brain-faithful mechanism; you may do *better* than the brain only if the improvement is brain-*compatible*. A brain-faithful design that is losing is presumed an implementation bug until proven structural.
4. **Only held-out / public-benchmark numbers count.** In-sample or construction-determined wins are not capability wins.
5. **Modern sources only** for any corpus/reference (no McGuffey / antique graded readers — a locked rule).

---

## §3 — Design philosophy (how the work is done)

- **Comprehension is a growing *library of construction-competencies*, not one objective.** One global objective saturates. Each construction type (passive, relative clause, coreference, negation, narrative, causal…) gets its own *learned, modular, glass-box* capacity. Entity-identity was competency #1; the loop engine's job is to *grow* competencies.
- **Route every error by flavor** before concluding "ceiling": (1) *used-an-ability-wrong* → fix + generalize; (2) *missing-primitive* → build it; (3) *missing-fact* → supply it; (4) *missing-learning* → reuse/expand the learner, don't build a parallel one. Every negative also asks: *is a needed component missing (especially learning) before I call this an intrinsic ceiling?*
- **Never generalize a narrow implementation failure to "impossible."** A fair test of a weak/narrow implementation proves *that setup* failed, not that the capability is impossible. Before declaring a route exhausted, write down exactly what was tested (data size/quality, mechanism depth) and the *stronger* version the brain actually uses — then test that. (This exact discipline caught a wrong "no-LLM reading can't scale → cross the Rubicon" conclusion — see §6 Arc F.)
- **For every mechanism ask two questions:** which *brain structure* does this (a neural system, not a cognitive-theory label), and does it *share* an already-built process → **reuse that organ** rather than build a parallel one (the brain reuses circuits; a parallel build is both non-faithful and creates islands).
- **Wire, don't island.** Every proven gain is promoted into `hdlab/` + a verification witness + registered as WIRED *before* the next build. Atomizing a result ≠ wiring it. There is a formal capability-integration gate (§9) precisely because hand-kept capability docs rotted silently in the past.
- **Layered self-correcting controls + reasoning ≠ comprehension.** Run the *full* control stack (scramble + prior-lesion + ablation + no-leak + attribution) on every apparent win; a positive isn't real until it survives the control that isolates its *claimed* mechanism — prefer the control that would reproduce the win from the *wrong* source. And distinguish glass-box *reasoning over structure* from glass-box *comprehension of prose*: if a tool/oracle did the reading, the claim is reasoning-over-structure, not comprehension.
- **Honesty deflation.** Rate results deflated (GOOD/MEDIOCRE/BAD); never present a baseline as a ceiling; verify on disk, never quote a remembered number; and caveat *interpretations*, not just verdicts (strategic reads run ahead of evidence — flag them as hypotheses pending VET).

---

## §4 — The baseline arguments / theses (the intellectual spine)

These are the load-bearing arguments a new team should understand and preserve.

**(a) Brain-as-existence-proof.** If the brain does capability X, X is achievable at 100% — so a shortfall is *never* accepted as a ceiling until two gates both pass: a *fair test* (can-fail, one-variable, real baseline) **and** an *exactly-like-the-brain* fidelity check (each element's SHAPE + POSITION + METRIC). Even then, the fix is the brain's way. This is why the program keeps digging on negatives instead of declaring limits.

**(b) The glass-box thesis.** The differentiating product value is an auditable reasoning substrate. This constrains architecture (inspectable representations, sharded/recoverable storage) and is defended even when an LLM would be "easier" — because *ease is the trap* the thesis exists to resist. The program tested the hard no-LLM paths to exhaustion *before* considering any Rubicon (see Arc E/F), precisely so the invariant is respected rather than abandoned for convenience.

**(c) Phase-diagram leverage — a DEFERRED lever (do not forget).** The substrate has full **phase-diagram freedom**: sparse-vs-dense codes, superposition load (facts bundled per vector), K, and n_dim are all tunable at will, each with known capacity peaks/cliffs (the Arc-A scaling laws bank this theory: FHRR capacity ~N^1.003, depth sub-linear ~0.717·log₂N). **The store today deliberately sits in the maximally conservative corner: dense bipolar + *sharded* (1 fact per vector), which OPTS OUT of the capacity phase diagram entirely** (no inter-item crosstalk → perfect recovery → perfectly inspectable — it serves the glass-box invariant). This is *deliberate*, not a limitation. Two banked **cash-in triggers** remain unspent:
  - **When RAM bites** (the real current ceiling) → *controlled superposition*: bundle B facts/vector at the capacity-safe load (B is pickable from the banked capacity-vs-load curve) as a substrate-native alternative to going on-disk.
  - **When building REASONING / going more brain-faithful** → *sparse codes* (biological ~1–5% active, cheaper memory, cleaner cleanup, own capacity peaks) + the composition-depth regime (how many bindings compose before a multi-hop chain degrades).
  The project owner explicitly said "we should not forget this." It is the highest-value queued architectural play once capacity/RAM or the reasoning layer becomes the binding constraint.

**(d) CLS three-tier memory.** The knowledge architecture is Complementary Learning Systems: *gather* (external refs) → *MIDDLE tier* (hippocampus: fast, retain-forever) → *FOUNDATION* (neocortex: consolidated, swept). Gate + sweep = systems consolidation. This is proven end-to-end and wired (Arc G1).

**(e) Same-representation / ATL amodal hub.** *Ideas should have the same representation no matter how they're worded.* Realized as **encode-time canonicalization** (native `(subject,relation)` store dedup with zero similarity calls at retrieval → same idea = bit-identical bundle = cosine 1.0), for both entity-canon and *learned* relation-canon. Maps to the anterior temporal lobe amodal semantic hub.

**(f) Weak→strong via reasoning, not voting.** Weak sources become strong knowledge through *relational/transitive inference* over their union (plus independence-weighted corroboration), **not** through density or majority voting. Proven N=121 (recovers facts no single source, blind-union, or vote has). Corollary the owner emphasized: the mechanism is *general* — domain performance is a question of supplying the right data/reading, not of rebuilding the mechanism.

**(g) Gap == grounding (the newest unifying insight, owner-originated 2026-08-12).** A knowledge *gap* and its *grounding solution* are the **same object**: the shortest missing *relational bridge* between a new concept and the grounded frontier. Naming the bridge = "what to read next"; traversing it = grounding. One act. Refinements that keep it honest: (i) gaps have **distance** — read the nearest-to-frontier link first, recursively (this *is* "can't learn QM before math" = zone-of-proximal-development / schema-congruence); (ii) distinguish a **bridgeable** gap (recurse and read) from an **unbridgeable** one (no path → need a new anchor/source); (iii) the identity holds **above the perceptual floor** (relational/curriculum knowledge) — the floor itself (perceptual anchors) is the seed's job, not reading's. **Architectural payoff:** unify `gap_detector` + `gap_driven_reader` + the grounding-quality evaluator onto **one metric — relational distance to the grounded frontier** (read-time = what-to-read-next; audit-time = grounding-quality; can-reason = traversing the bridge). The first single-hop cut is landed (`7dd02833b`); the recursive multi-hop version is the next increment.

**(h) The controls discipline IS the epistemics.** The reason this report's positives are trustworthy is that the program spends as much effort trying to *refute* each win as to produce it. Multiple headline results were retracted by their own controls. A new team that keeps only the wins and drops the controls will regress fast.

---

## §5 — Architecture & wiring map (disk-verified)

*The following section was produced by a disk-verification pass over `data/capability_registry.jsonl` (127 rows, parsed clean), `hdlab/`, and `notes/architecture_audit_2026-08-11.md`. Registry `pipeline_status` is known-unreliable; wiring below was confirmed by reading source, not labels.*

### 5.1 The read-to-grow pipeline (current head)

| Stage | File | Role | Depends on |
|---|---|---|---|
| **Reading extractor + canonicalize** | `hdlab/reading_grounding_loop.py` | `ReadingLoopState`/`process_sentence` reads curriculum in order; `canonicalize()` does nearest-neighbor sense assignment of a new word's context-vector (bipolar `np.sign` bundle) against every anchor in a `ConceptSpace` (the `content_repr_vector` primitive). Self-return = explicit NO-MATCH signal, not a meaning (fix for the retracted "65.7% tautology" bug). | `lexical_similarity.py` (~380-word seed lexicon), `closed_class_lexicon.py`, `animacy_lexicon.py`, `definitional_extraction.py` |
| **GATE** | `hdlab/grounding_acquisition_loop.py` | FLAG→LIBRARY→CONSOLIDATE→GUARD→BANK loop. Gates BANK on THREE independent conditions: vote-margin abstain-band, `schema_consistency_split_half` (false-memory guard — the *actual* gate), and exposure count ≥ threshold. PROMOTE writes natively into `hd_fact_store`. | `consequence_learning_loop.py`, `self_improving_loop.py`, `verb_lexical_similarity.py`, `hd_fact_store.py` |
| **three_tier_loop** | `hdlab/three_tier_loop.py` | Assembly glue (no new mechanism) wiring GATHER→REASON→PARSE→GATE→FOUNDATION/MIDDLE per CLS. `answer()` does priority-order fusion (FOUNDATION→MIDDLE→UNRESOLVED); a true holistic multi-source *score* fusion is explicitly **not** yet claimed (open gap). | `gather_reason.py` (CA3 gather + K≤2 fan-out), `grounding_acquisition_loop`, `prelim_tier.py`, `hd_fact_store.py` |
| **hd_fact_store** | `hdlab/hd_fact_store.py` | Native `(subject,relation,object)` role-slot-bound single hypervector; glass-box unbind+cleanup read path. `(s,r)` HD signature key → native dedup/conflict retrieval with **zero similarity call**. Source-TRUST ingest-vetting (REPLACE/COMBINE/FLAG/DROP) — *ingest* vetting, not correctness vetting. | `event_bundle.py`, `role_slot_summarizer.py` |
| **cleanup_family (CA3)** | `hdlab/cleanup_family.py` | Cleanup primitive library; `iterative_attractor` is the CA3/DG best-match picker imported verbatim by `gap_detector`. | leaf primitive |
| **gap_detector** | `hdlab/gap_detector.py` | The **only genuinely-online autonomous gap detector** (closes the audit's "gap-detection was offline KB-diff" finding). Per `(subject,relation,candidate)` probe: CA3 pick + CA1 match/mismatch margin (read pre-settle) vs a decision floor → GAP/KNOWN. Codebook rebuilt from `live_facts()` each `refresh()`. | `cleanup_family`, `hd_fact_store`, `role_slot_summarizer` |
| **gap_driven_reader** | `hdlab/gap_driven_reader.py` | Self-directed "what to read next": on an ungrounded concept B, identifies the missing prerequisite A that B leans on and ranks candidate material by how well it supplies A. | `reading_grounding_loop`, `gap_detector.familiarity`, `hd_fact_store`, `grounding_acquisition_loop` |
| **foundation_persistence** | `hdlab/foundation_persistence.py` | Deterministic save/reload of `HDFactStore` + `ConceptSpace` + `Library`, byte-identical round trip **including the `torch.Generator` raw state** (so post-reload symbol registration continues the identical stream). Without this the foundation reset to empty every run. Adds no methods / changes no defaults on the organs it persists. | `hd_fact_store`, `reading_grounding_loop`, `grounding_acquisition_loop` (read-only) |

**Known chain gap:** the GATE (`grounding_acquisition_loop.py`) has *no dedicated registry row* — it only appears inside a downstream capability's `path` list. A registry-first audit would conclude the GATE doesn't exist. (See wiring debt below.)

### 5.2 Registry summary

127 rows, all parse clean: **76 WIRED**, **25 ISLAND**, **24 TRAPPED_SHARED**, **2 N_A_SHELVED**.

Selected WIRED load-bearing organs beyond the pipeline: `coreference_resolver` (match-or-allocate + strict-Cb + Principle B), `situation_model_accumulate` (Kintsch/Zwaan multi-event entity-role register), `goal_owner_select`/`goal_typing`, `self_improving_loop` (gold-free coherence-gated keep/revert), `working_memory` (multi-bank K=4096), FHRR/HRR bind/bundle primitives (`binding.py`/`bundling.py`).

Notable **deliberately-not-wired** assets (this matters — see §7): a **39,707-word Lancaster/Brysbaert/Warriner grounding-norms island** and a **237.7M-token from-scratch transformer concept encoder** (`TRAPPED_SHARED`, zero `hdlab` imports) — both far bigger meaning-assets than the live ~380-word lexicon, both disconnected from the inference path. Also shelved-with-criteria: Theory-of-Mind nested-HRR (proven, needs re-run on real organs), VAMP-EP deep-chain solver (synthetic-KG only), capacity_scaling formula (calibrated on sequence binding only, does not transfer).

### 5.3 "Great vs meh" (from the 2026-08-11 architecture audit)

**GREAT / keep as-is:** `hd_fact_store` (best-built organ, real-data proven on 1.24M CSKG edges), `situation_model_accumulate` (accumulate 1.00 vs overwrite 0.46 vs floor 0.21 on real text), `gather_reason` (strongest real-benchmark arm 0.38 vs blind-union 0.04), `cleanup_family.iterative_attractor`, `three_tier_loop`, `grounding_acquisition_loop.consolidation_pass` (the GATE), `prelim_tier`, `content_repr_vector` canonicalization, `char_trigram_encoder`.

**MEH, by impact:** **(#1, VERY HIGH impact / low effort)** meaning is a ~380-word hand lexicon while the 39.7k-word norms island and the 237.7M-token encoder sit unused — *wire what already exists*. (#2) reading-extractor depth (SVO/passive pattern-matcher, 38 verbs → 3 classes; closed-schema IE, not comprehension). (#3) sweep's combined-evidence promotion never fired on real sparse data; clustering key is literal string match; multi-source coverage is thin. (#4) `glass_box_loop` (validated Go/NoGo value-gate + Merkle audit trail) sits unwired — exactly the arbitration `three_tier_loop.answer()` lacks.

### 5.4 Known wiring debt (state plainly, it's real)

- **The registry undercounts by audit-method, not rot.** `hdlab/` holds ~141–144 modules; a runtime trace found only ~35 reachable from the default path; ~62 have no registry row. **Rule going forward: enumerate from the filesystem, then reconcile to the registry — never the reverse.**
- **`pipeline_status` is wrong in both directions** — every live pipeline organ in §5.1 is mislabeled `WIRED_BUT_NOT_PIPELINE_REACHABLE` because the static import-graph scan misses lazy/function-body imports. Treat it as a hint; runtime observation decides.
- **4 load-bearing modules entirely unregistered:** `glass_box_loop`, `grounding_acquisition_loop` (the GATE), `multi_hop`, `script_grain_acquisition_loop`.
- **~13 orphan `hdlab/` files are live deps of committed organs but themselves uncommitted** (`arc_parser`, `pos_tagger`, `coref`, `candidate_generator`, plus modified `kg_traversal.py`/`lexical_similarity.py`) → **fresh-checkout-broken risk**: a clean clone would be missing imported files. Left untouched due to concurrent-session caution; must be reconciled before a clean release.
- **Duplicate registrations:** `cleanup_family`/`iterative_attractor` registered 3× under different names.

---

## §6 — The full results ledger (disk-verified)

*Every hash confirmed via `git show`; every metric read from `data/exp_*/metrics.json`. Unverifiable items marked UNVERIFIED. Arcs A→H are roughly chronological; the negatives are included deliberately.*

### Arc A — Substrate foundations (historical scaffolding)
HD/VSA primitives + scaling laws. FHRR capacity `k~N^1.003`; FHRR depth sub-linear (`0.717·log₂N−0.629`) vs HRR super-linear → production guidance (HRR depth-bound, FHRR capacity-bound, BSC memory-bound). BSC promoted to first-class in `hdlab/binding.py`. An early BGE-large encoder distillation FAILED at 178k scale (batch coverage too sparse). *Treat as settled infrastructure; the frontier moved on.* (`PROGRESS.md` secondary source, several items UNVERIFIED this session.)

### Arc B — Comprehension pipeline: the STORE arc
Candidate-retrieval **scales**; final single-argmax selection **does not**.
- Stage-1 salience-gated pull-in HARD_PASS 5/5 (`ceb8fe99b`); Stage-2A retrieve→validate→advance multi-hop HARD_PASS 5/5 (`013f1481e`); Stage-1.5 context-gate rescues EVT false-admission at scale HARD_PASS (`59e5c5f1f`).
- Monolithic dense Hebbian store hits a Hopfield crosstalk cliff (recall 0.967@1K → **0.000@30K**) — *contradicts its own cert docstring; do not trust cert docstrings without re-run.* Resonator rescue HARD_FAIL (`af9073fbc`).
- **Sharded + sparse (DG/CA3) + hierarchical subject-tier retrieval SOLVES candidate-retrieval at 1.2M-entity real CSKG** (shortlist-hit ≈0.853, scramble→0.12). But **single-argmax final selection HARD_FAILs** (`bec359477`, wrong-argmax ~0.71–0.77 regardless of leaf size) — a k_eff≈50 discriminability wall, not capacity. **Store arc closed 2026-08-10; do not re-grind store tuning.**
- Augment-not-replace + confidence-abstain-gate architecture: MIDDLE_BAND, no-regression confirmed (3 seeds). Reusable pattern.

### Arc C — The extraction wall (converged on 9+ times — the central negative)
Three flagship benchmarks, three independent negative arcs, same wall:
- **MCScript2.0** static SVO matching HARD_FAIL *below chance* (0.401 vs BoW 0.629); inference-augmented → MIDDLE_BAND (content-saturable; wrong flagship).
- **WIQA** signed causal-chain loop → NOT_CAUSAL_STRUCTURAL (`be812e883`): subset-scramble shows scrambling causal edges *costs nothing* — the lift was topology, not causal reasoning. Learned edge-polarity HARD_FAIL (`16f754442`, TRAIN 0.982 / TEST 0.412 overfit — edge polarity is world knowledge).
- **ProPara** oracle-propagation: v3 "genuine content" **retro-corrected** as an order-based disambiguation artifact — **do NOT cite ProPara v3 as a comprehension win; do NOT re-dispatch "propagation composition."**
- ~60 islanded "comprehension" cells audited: every real-text cell shows oracle-input near-ceiling (0.93–1.00) collapsing to self-extracted-input (0.25–0.68).
- **Convergent verdict:** the binding constraint is **real-prose extraction** (text → structured meaning), not storage/retrieval/inference (all of which work on clean input).

### Arc D — Frame-activation build → "pipeline 4/5 built" + MAVEN-ERE wins
- Convergence-gated frame selection real sub-win (`459098f52`, 26× scramble discrimination — scope: gate-discrimination only, parent cell HARD_FAIL).
- Schema pattern-completion self-test PASS (`e97a1437b`) — fills an unmentioned slot in isolation, but ProPara has zero never-mentioned participants so the capability is never exercised end-to-end.
- **MAVEN-ERE causal relation classification HARD-PASS full-dev** (`933773243` region): F1 **14.78** vs floor 5.93, scramble 3.48; 47% of SOTA. **MAVEN-ERE subevent HARD-PASS** (`3ea917044`): F1 13.63 vs floor 2.86. *Scoped* discourse-relation reading (events are benchmark-pretagged), not full E2E reading — but real, controlled glass-box wins.
- **Pipeline is honestly "4/5 built":** frame/schema selection ✓, fill-in-the-unsaid engine ✓ (isolation), local thematic-role reading ✓ (0.95 held-out), learned discrimination ✓ (MAVEN). The 5th — **per-participant grounded binding** — is the wall.

### Arc E — The deep-grounding wall (entity-level world knowledge)
Four independent no-LLM routes to entity-level process-role knowledge ("wood is *consumed* by combustion" vs "ash is *produced*") all FAIL on held-out unseen entities:
- Small learned model HARD_FAIL (`50b8d8751`, unseen lift 0.0, pure memorization).
- WordNet / ConceptNet / GloVe all HARD_FAIL (`0b5ca76a1`, 98–99% coverage but negative lift vs majority 0.394).
- Properly-powered pure selectional-preference acquisition (39.5M tokens, owned parser stack) HARD_FAIL (`1ffbba4e3`, real≈scramble).
- **All 4 converge negative** → the missing knowledge is LLM-scale (at this corpus/scale).

### Arc F — The bootstrap investigation + the Rubicon (raised, RETRACTED, re-earned) — *most important self-correction; read in order*
1. Director declared "all no-LLM routes exhausted → cross the Rubicon." **Owner caught the overreach:** the 3 negatives were each a fair test of a *narrow* implementation, not of "learning from reading" in general. → **locked discipline: never generalize a narrow failure to "impossible."**
2. Bootstrap fade v1 (`4fc4ca75c`): reading is a real growth channel (recall 0.048→0.226) but the crutch does *not* fade (grain mismatch: seed process-keyed, reading entity-global).
3. **Owner correction (load-bearing):** store context-dependent facts in **FHRR superposition**, not symbolic averaging. Storage v3 (`d716621dc`) proves it: self-consistency 0.9556, per-process registers coexist (water@water-cycle=MOVE and water@respiration=DESTROY both retrievable). **Storage solved + brain-faithful.** Wall moved upstream to *acquisition*.
4. Passage-context-binding hypothesis **falsified by a fair one-variable test** (`54adf9102`, owner: "make sure this test is fair"): passage-scope ≡ sentence-scope to 4 decimals. Real limiter = process-vocabulary overlap.
5. v5 schema-gated (`509639790`): no-LLM reading of general prose extends only a **thin ~18% slice**; seed knowledge load-bearing for ~75%.
6. **Owner's actual resolution (not the literal Rubicon):** grow the foundation by **reading real modern curriculum/textbooks** (OpenStax) — this is Arc G. **Do not re-run the scattered-SimpleWiki fade expecting a different result; do not re-litigate "reading can't scale" without first checking the corpus was dense/textbook-style.**

### Arc G — The pivot: read-to-grow (current architecture)
**G1 — three-tier substrate (all HARD_PASS, controls clean):** weak→strong reasoning-combination N=121 (`7a6afdab8`); three-tier accumulation+sweep dynamics (`73c54d094`, retain 1.00 + CA3/DG sweep 0.645 both load-bearing); independence-weighted corroboration (`62dafbc08`); same-idea→same-representation 145/145 (`e65de60f1`); learned relation-canonicalization (`1fdfcf300`); causal-domain generalization with zero mechanism change (`d982ab2aa`, MIDDLE_BAND = threshold artifact).

**G2 — read-to-grow foundation build:**
| Result | Verdict | Commit | Numbers |
|---|---|---|---|
| Cycle 1: grow from curriculum reading | HARD_PASS | `e38fd8454` | 0→185 concepts; scramble ratio 0.286; no-leak/monotone OK |
| Cycle 2: persistence + cumulative growth | HARD_PASS | `ac430868d`/`0472eeb0b` | round-trip bit-identical + survived process death; **185→3544 concepts / 7966 facts**; scramble **0.077** |
| Curriculum prerequisite-scaffolding | HARD_PASS | `5fe41846d` | correct-order 1.0000 / reversed 0.0000 / scramble 0.0000 — requires the prereq *consolidated*, not merely seen |
| Autonomous online gap-detector | landed | `700e9efe3` | familiarity/novelty gate |
| Self-directed gap-driven reader | HARD_PASS n=8 | `7dd02833b`/`8f03e21ed` | prereq-ID precision **1.0 vs 0.0 ablated**; grounds **1.0 / 0.0 ablated / 0.125 random**; doc-prioritize top-1 1.0 vs 0.25 |

**Honest scope limit (self-flagged):** these prove growth is *clean* (no-leak, scramble-discriminating, persists) — they do **not** yet prove what's grounded is *correct* or *well-organized*. That is Arc H.

### Arc H — Current frontier / open (2026-08-14) — *includes concurrent-session work on the same substrate*
- **H1 — grounding-readout QUALITY is the live gate, and it is NOT passing** (`exp_grounding_readout_known_answer_v1`, metrics `204eba1a0`). Banked-facts arm **AT_FLOOR** (GOLD_HIT 0.0251 vs scramble 0.0125, CI crosses zero low). 2AFC **MIDDLE_BAND** (0.5393 vs 0.50 chance, short of 0.60). **Open-vocab readout (closest to the live loop, n=4000/5491 anchors): hit@1 4.80% vs scramble 0.80% — 6× floor, but the ≥10% gate is RETIRED; C3 FAILS the four-condition hardened gate and is UNMEASURED on 3 of its 4 conditions (`tools/c3_gate.py`).** Self-retrieval 0.786 (retrieval healthy). **Defect = within-neighbourhood separation** (axon→dendrite, artery→vessel: right neighbourhood, wrong member). *Correction:* an earlier "65.7% tautology" figure was an **eligibility bug** (fix `1b2022522` → live path emits 0% tautology), not a meaning failure.
- **H2 — graded comparator landed default-ON** (`38f7a0d5c`, live path 0.6395→0.6980, +0.058). **Do NOT cite 0.7495** (unshipped d=1024 arm; mechanism claim separately refuted). Landed-VET (`f05b8a88a`): the *number* survives, the *mechanism claim is withdrawn*.
- **H3 — information foraging (MVT reading-order organ)** HARD_PASS 3/3 (`3d4761f69`). Counter-caveats that must travel with it: FROZEN beats FORAGE on raw held-out coverage (0.0743 vs 0.0617), and RANDOM beats FORAGE on grounding quality (0.3864 vs 0.3511) — the declared pairwise comparisons hold, but the FORAGE arm read naively overstates.
- **H4 — two clean same-day negatives:** rank-1 common-mode removal HARD_FAIL_NO_EFFECT (`34b94e8bc`; also corrects a "58%" premise → true shared energy 15.35%); forgetting-kernel/sign-readout REFUTED (`41da8e454`, substrate already has a power-law forgetting curve — the cascade organ is unnecessary).
- **H5 — encoder-retrain-persist** landed opt-in (`367a42729`, 2026-07-31) — commit confirmed, loader/checkpoint claims **UNVERIFIED this session**.
- **H6 — cert-ledger archaeology / audit-reliability meta-finding** (`notes/vscode_week_results_validity_audit_2026-08-14.md`): many recent *demotion* claims were themselves re-reading errors (wrong checkpoint/arm; absence-asserted-from-name-search) — 17 corrections-of-a-correction in 48h; the underlying measurements were mostly sound. **Implication: treat any demotion claim lacking a fresh on-disk re-check with the same suspicion as the original claim.**

---

## §7 — Where the frontier actually is (honest current state)

Hold two facts together:

1. **The growth mechanism is clean and real.** Read-to-grow reliably grows a persistent, scramble-discriminating foundation (185→3,544 concepts / 7,966 facts), and the substrate can self-direct its reading (prerequisite-first). The speed wall it hit (below) has a designed, brain-faithful fix ready.
2. **The quality of what it grounds does not yet clear its own gate.** Open-vocab grounding hit@1 is 4.80% vs 0.80% scramble — a real floor, but scramble is the WEAKEST baseline (frequency is 1.85%; the orthographic floor is UNMEASURED) and the ≥10% criterion is RETIRED in favour of the four-condition hardened gate (`tools/c3_gate.py`). The defect is *within-neighbourhood separation*: correct neighbourhood, wrong member. This is exactly the "meaning is a ~380-word hand-lexicon while a 39.7k-word norms island + a 237.7M-token encoder sit unused" gap (§5.3 MEH #1) showing up as a measured shortfall.

**These are consistent, not contradictory.** The pipeline plumbing works; the *meaning content flowing through it* is too coarse to separate near-paradigmatic members. That single fact defines the priority order:

**The roadmap (owner-set, gated):**
- **(2) Validate grounded + organized — and close the quality gap.** A validation harness (correctness + organization + can-reason, with scramble/ablation/no-leak) was built this session; its FULL run was in flight and is **not yet reported** (its build agent has no completion record — resume/re-run it). The concurrent grounding-readout cells already give a *negative* partial answer (H1). The real work is closing within-neighbourhood separation — almost certainly by **wiring the meaning assets that already exist** (the norms island + the encoder) into the live path (§5.3 MEH #1), i.e. this is a *missing-component/wire-don't-island* problem, not a new-mechanism problem.
- **(3) Scale + speed (design landed, build queued).** The `GapDetector` CA3 cleanup is **O(n_facts)** and gates throughput (~80s/chunk at ~8k facts). **The fix is a minimal extension, not a new build:** `hd_fact_store` already has an exact O(1) `(subject,relation)` content-hash index — it is simply switched *off* in the reading loop, and `GapDetector` ignores it and rescans the whole codebook. Route each probe through the existing bucket (relation/schema → content-hash), keep CA3 cleanup byte-identical but scoped to the tiny routed bucket → sub-linear. Also make the per-checkpoint full rebuild incremental. Design doc: `notes/research_sublinear_gap_detector_cleanup_shard_dg_ca3_design_2026-08-14.md`; build target `hdlab/sharded_gap_index.py`; verification = latency ratio ≤1.3× from 2k→16k facts + 100% correctness parity. (This is consistent with the phase-diagram thesis: the store deliberately sits off the capacity diagram in the sharded corner, so exact hashing is the right tool.)
- **(4) Unify gap==grounding onto one distance-to-frontier metric** (§4g). **(5) Recursive multi-hop** gap-reader (current is single-hop).
- **Gate:** do **not** grow the foundation big until quality (2) and scale (3) are both green. Growing a foundation that can't separate members just scales the error.

---

## §8 — Walls / do-not-re-tread (pull-out list)

1. **Grounding-SIMILARITY is taxonomic, not similarity** — owned norms (0.32) and distributional embeddings (0.46) both fail; the WordNet probe was killed by the owner. Closed.
2. **Store single-argmax final selection** — capacity/skew solved (shortlist 0.853@1.2M); single-argmax is a k_eff≈50 discriminability wall. Selection belongs to the downstream loop, not the store. Don't re-grind store tuning.
3. **Extraction wall** — 9+ independent real-prose cells: oracle-input near-ceiling, self-extracted-input at/below chance. Structural.
4. **ProPara "propagation composition" (ARM-1 v3)** — order-disambiguation artifact; explicit re-tread flag.
5. **WIQA causal-chain loop** — falsified as topological, not causal (subset-scramble).
6. **Entity-level world knowledge from no-LLM sources** — 4 independent HARD_FAILs on held-out-unseen generalization.
7. **"No-LLM reading can't scale" as a blanket claim** — a self-caught overreach. The claim that survives fair testing is "*shallow* extraction of *scattered* prose extends ~18%"; dense textbook curriculum is the untested/now-pursued case. Don't conflate.
8. **Rank-1 common-mode removal** and **forgetting-kernel/sign-readout** — cleanly negative (2026-08-14); don't revisit without a new mechanism.

---

## §9 — How to operate this project

**Operating model = agent-spawn.** The 4-session fleet model is dead. A single **Director** main thread does strategy / judgment / 1-off docs; all rote/heavy work is delegated to `hdi_<role>` sub-agents (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`):
- `hdi_exp_dev` — cell authoring, smoke gate, local dispatch.
- `hdi_skunkworks` — landed-VET + atomization, **audit-only** (never authors/dispatches — role separation).
- `hdi_orchestrator` — the only role with push-to-origin + remote queue.
- `hdi_testbed` — infra + 2nd-witness review.
- `hdi_research` — director/team-lead, literature scans.
Spawn ≤5 concurrent; background by default; **yield the turn after dispatching** (the measured bottleneck was the main thread staying busy, not the spawns). Hand agents *task shape + pointers*, never pre-baked numbers or conclusions (that turns them into rubber-stamps and defeats independent verification).

**Capability-integration gate** (owner mandate — hand-kept docs rotted silently before, so this is machine-audited): `data/capability_registry.jsonl` + `tools/capability_registry_audit.py`. At land-time for anything cert'd/HARD_PASS: **WIRE-or-SHELVE** (nothing in limbo; SHELVE needs explicit revival criteria); **query-before-build** (`capability_registry_query.py --serves`); **run the audit at session start** (durability lives in the session-start read, not a cron — 11 cron tasks were once silently disabled for ~12 days). **Caveat from §5.4: enumerate from the filesystem first, reconcile to the registry second.**

**Verification/cert discipline.** Every feature ships a scaffold-free witness in `verification/`; `python verification/run_certification.py` must pass on `main`; new feature order = closed-form theory/oracle → `verification/` test → `hdlab/` impl → `pytest verification/` green → `PROGRESS.md`. The role that authors a cell never certifies it.

**Store/dispatch hazards (always-on):** never `git add -A` on the canonical store; store writes are binary/`newline=''` only (text mode doubles CRLF) + git-commit after every bank; remote-persist + origin-push need explicit in-session owner auth; serialize registry edits; ASCII-only; `.venv` for cert; reconcile by `atom_id`, not seq-grep.

**Backup status (as of 2026-08-14):** all code + history is on branch `dataprep/mcguffey-graded-corpus`, pushed to origin/GitHub (`28e13d79b`). The 37 MB `data/foundation/reading_grounding_v1/` snapshot (3,544 concepts) is **gitignored → NOT in the remote**, but reproducible from the committed code + corpora. *Recommend snapshotting it separately if you want a restore point.*

**Permissions:** a safe auto-approve allowlist is at `d:/AI/.claude/settings.local.json` (read/inspect/python/local-git allowed; `rm -rf`/`reset --hard`/`push --force`/`sudo` denied; origin-push kept prompting as a deliberate gate).

**⚠️ Concurrent session caution:** at handoff, a second session was actively editing `hdlab/lexical_similarity.py`, `data/capability_registry.jsonl`, and several untracked orphan `hdlab/` files (Arc H work). Do not race those files; coordinate before committing over them. This is why the wiring-debt cleanup (§5.4) is still open.

---

## §10 — Open questions & risks

- **Q1 (the one that matters): can within-neighbourhood separation be closed by wiring the existing meaning assets** (39.7k norms + 237.7M-token encoder) into the live path, or does it need a new mechanism? The MEH-#1 framing says wiring; that hypothesis is untested end-to-end. Fair-test it before concluding either way.
- **Q2:** ANSWERED NO for the wiring half — meaning supply is REFUTED as the C3 constraint (`c0e6ec0da`; DO-NOT-REDO 31). Does the hardened gate clear once the meaning assets are wired *and* the sub-linear index lets the foundation grow larger/denser? Quality and scale may be entangled.
- **Q3 (integrity):** the fresh-checkout-broken risk (§5.4) and the 4 unregistered load-bearing modules — reconcile before any clean release or team transfer of the repo.
- **Q4 (audit reliability):** per H6, the audit layer has recently been *less* reliable than the measurements. Institute "no demotion without a fresh on-disk re-check."
- **Risk:** growing the foundation before closing quality scales the error — the gate exists for a reason.
- **Deferred lever not to forget:** the phase-diagram cash-ins (§4c) — controlled superposition at the RAM ceiling, sparse codes when building reasoning.

---

## §11 — Where everything lives (recovery map)

- **SUPERSEDED 2026-08-14:** the 08-04 backup below is NO LONGER the recovery entry point — **THIS FILE is**, then `notes/STATUS.md` -> `notes/RECOVERY_PROGRAM.md` -> `notes/SUBSTRATE_STRATEGY.md` + `notes/ORGAN_MAP.md` (chain recorded in `STATUS.md`'s header); starting at the 08-04 backup routes a cold session backwards.
- **Recovery entry point:** `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` — self-contained, reverse-chronological arc banners at the TOP are the authoritative current state. Then `notes/SUBSTRATE_CHARTER_read_first.md`, `notes/THE_PLAN.md`, `notes/WHERE_WE_ARE_NOW.md`.
- **Strategy + scoreboard:** `notes/SUBSTRATE_STRATEGY.md` (living); **organ inventory:** `notes/ORGAN_MAP.md`; **architecture audit:** `notes/architecture_audit_2026-08-11.md`; **validity audit:** `notes/vscode_week_results_validity_audit_2026-08-14.md`.
- **This session's design docs:** `notes/research_sublinear_gap_detector_cleanup_shard_dg_ca3_design_2026-08-14.md` (the (3) speed build spec).
- **Live substrate library:** `hdlab/`. **Experiment cells:** `experiments/`. **Cert witnesses:** `verification/`. **Registry:** `data/capability_registry.jsonl`. **Foundation snapshot:** `data/foundation/reading_grounding_v1/`.
- **Conventions/operating rules:** `CLAUDE.md` (session ritual, agent roles, cert discipline, checkpoint/resume).
- **Director's cross-session memory** (disciplines, owner directives, the gap==grounding note, phase-diagram deferral): the memory index + files under the Director's memory store (`MEMORY.md` + topic files). These encode *why* decisions were made and the owner's locked rules — read them to avoid re-litigating settled calls.

---

## §12 — Your first moves (so you don't miss a beat)

1. **Re-run the (2) grounding-quality validation** to a clean verdict (its FULL run never reported). Point it at `data/foundation/reading_grounding_v1/` (3,544 concepts). The question: is what we grounded *correct* and *separable*, and can it *reason* to multi-fact answers — with scramble/ablation/no-leak.
2. **Attack within-neighbourhood separation (§7 / Q1):** fair-test whether wiring the existing meaning assets (norms island + 237.7M-token encoder) into the live reading/canonicalization path closes the gap was TESTED and REFUTED (`c0e6ec0da`): the lift is matched by a zero-meaning spelling channel. The live TOP ITEM is now STRUCTURE, not supply — see `notes/STATUS.md`.
3. **Land the (3) sub-linear gap-index** (`hdlab/sharded_gap_index.py`) per the design doc — unblocks throughput so bigger reading is affordable. Minimal extension; verification benchmark is pre-specified.
4. **Then, and only then, grow the foundation big** — and cash in the phase-diagram levers (controlled superposition / sparse codes) as RAM and the reasoning layer demand.
5. **Housekeeping before a clean transfer:** reconcile the fresh-checkout-broken orphans + the 4 unregistered load-bearing modules (§5.4), coordinating with the concurrent session.

**Keep the controls discipline (§3, §4h).** It is the reason this report can be trusted, and the fastest way to regress is to keep the wins and drop the refutations.
