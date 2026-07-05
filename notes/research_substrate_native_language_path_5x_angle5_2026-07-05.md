# 5x-drill Angle 5/5 — the honest path from proven capability set to substrate-native LANGUAGE

Date: 2026-07-05. Type: internal-scour + brain-mechanism synthesis (level-2 operational drill on EXISTING
findings, not a fresh lit-scan — most of the external Levelt/psycholinguistics/VSA-resonator literature this
question needs was ALREADY gathered today by `research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md`;
this note verifies, cross-checks against the filesystem, and answers the three questions the USER actually asked
rather than re-deriving citations). No dispatch performed (per task instruction).
Method: `python tools/orchestrator/research_field_advisor.py` (physics-field advisor — not directly relevant to
this architecture question, confirms no adjacent physics-field angle was skipped); read-end-to-end on ~12 M3/
cortex/decoder notes + 12 language-track-history notes (1 Sonnet sub-agent, internal scour); direct filesystem
verification of the decoder's filler-codebook provenance (traced concept indices to real ConceptNet/math-taxonomy
name strings — see section 3).

---

## HEADLINE

**The mechanism gap is smaller than the framing suggests, and it is NOT the gap the USER's question implies.**
Three independently-proven CG/HARD_PASS primitives — (1) multi-hop KG retrieval over real ingested atoms,
(2) the Integration reason-to-generate bridge (symbolic cleanup beats a learned bridge, HARD_PASS at FULL,
2026-07-05), and (3) the native-GSBC block-local decoder (exact-ordered 1.000 to D=26/V<=1024, LANDED TODAY,
2026-07-05) — already compose, end to end, on REAL NAMED CONCEPTS (verified off-disk: the decoder's filler
codebook traces through `concept_rows` to `id_order_json` string names like `CN_scabicide`, not anonymous
integers). What is MISSING is not a new mechanism — it is a ~100-line glue script that (a) sources real
ConceptNet-derived S/V/O facts instead of hand-picked round-trip triples, (b) prints the recovered token
STRINGS via the existing name lookup instead of reporting only index-match accuracy, and (c) hand-curates a
common-word subset so the output is human-legible (the raw 10,000-concept sample includes entries like
`CN_catoptrophorus_semipalmatus`, i.e. correct-but-obscure). Separately, the thing the USER's mental model calls
"the cortex layer" is actually TWO different pieces of code that do NOT gate this capability: Cortex-1 (the noise/
context/attention/clarify facade) is CG-plumbing with unproven downstream payoff (HONEST_NEGATIVE on the one
utility probe run), and Cortex-2 (atom-consultation) is a self-referential constraint layer that reasons over the
substrate's OWN build-discipline metadata via a tiny char-trigram sidecar — it has ZERO wiring to the concept
encoder and does not touch language at all. Neither is a prerequisite for a grounded telegraphic utterance.
**Rating: the narrow "speak a real fact as an ordered short phrase" capability is READY, one glue script away
(good, not smoke — every load-bearing piece is independently CG or HARD_PASS already). Full conversational
glass-box-LM (M3/M4) is genuinely further out and IS the capstone — gated on unproven Cortex-2 utility, the
still-open one-to-many generalization ceiling, and morphology/function-word encoding that doesn't exist yet.**

---

## 1. WHAT'S THE GAP

### (a) Vocabulary grounded in ingested meaning — SMALLER GAP THAN ASSUMED, verified off-disk

The task brief's framing ("generation round-trips codes exact-ordered... NOT language") describes the STATE
from a few weeks ago (the RNS/CRT V=65536 capacity envelope, and the original decoder MVP on
BGE-randproj-bipolar STAND-IN fillers). That framing is now stale for the specific decoder cell that landed
TODAY. I traced the filler provenance by hand:

- `exp_generation_decoder_gsbc_native_blocklocal_v1.py` draws fillers from
  `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` — a 10,000-of-177,899 SAMPLE of the REAL deployed
  concept encoder's output (`GSBC_EXPAND2X_seed7_FULL`), not synthetic random codes.
- That npz stores `concept_rows` — integer indices into the master 177,899-concept table
  `data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`.
- That master table's `id_order_json` field IS a JSON list of 177,899 real name strings, e.g.
  `T1/vector_space`, `T2/fhrr_bind` (math/methodology taxonomy atoms) and `CN_scabicide`,
  `CN_catoptrophorus_semipalmatus`, `CN_key_signature` (ConceptNet-derived entity names, `CN_` prefix).

**So the decoder's vocabulary is already grounded in real ingested concept names — this is a fact I verified
directly, not an inference from a note.** The gap is NOT "no grounding exists." The gap is: (i) the landed cell
reports index-match accuracy, not printed strings — nobody has looked at a decoded output and read it as words;
(ii) the raw sample is unfiltered ConceptNet, so a random S/V/O triple will often include obscure/Latin-binomial
entries (the willet-shorebird example) that are technically-correct but not legible as "language" to a human;
(iii) the source triples for the landed cell are ARBITRARY random concept juxtapositions, not real KG facts (no
subject-relation-object semantic coherence) — a decoded "sentence" today is 3 random correct words in a row, not
a true proposition. Fixing all three is curation + a print statement, not new mechanism (see section 3).

### (b) Sequential/syntactic structure — MECHANISM PROVEN, SCOPE NARROW (telegraphic only)

Stage B of the decoder design (`notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`)
binds position as one of exactly 2 factors per bound term (`bind(position_role, filler)`) — this is the SAME
abstraction as Garrett's frame-and-slot model and competitive-queuing/theta-gamma phase-slot coding (today's
generation drill cross-validated this against neuroscience + psycholinguistics + VSA theory independently; see
citations). This IS a real syntactic-position mechanism, verified: `exp_factorization_envelope_v1` shows F=2
(role+filler) holds to 1.000 while F=3 collapses to 0.217 and F=4 to 0.000 — so "position is a bound factor, not
a third slot" is a hard architectural constraint, not a design choice, and the block-local decoder respects it.
**What this buys: ORDERED recovery of up to D=26 slots (exact-ordered 1.000 to V<=1024, cliff only at
V=8192/D=26=0.86).** What it does NOT buy: morphology (tense, plurality, agreement), function words
(determiners, prepositions, auxiliaries), or any grammar beyond "N content words in a fixed slot order." This is
telegraphic speech (compare: agrammatic aphasia, or a 2-year-old's "doggie chase kitty") — a genuine, non-trivial
capability, but explicitly NOT sentence-level English grammar. No cell anywhere in the corpus attempts
morphological/function-word encoding; it is an unopened gap, not a failed one.

### (c) A cortex layer above the substrate + stochastic-noise-at-boundary — EXISTS, BUT WRONG PART, UNPROVEN PAYOFF

Two things both called "cortex" exist in code and neither is what closes the language gap:

- **Cortex-1** (`hdlab/cortex.py`, 763 lines; composes NoiseChannel/refuse_gate/TwoTierContext/chunked-attention/
  RoleSlotSummarizer/ClarifyGate): CG at the INTEGRATION level (runs correctly, preserves bind/unbind algebra,
  noise injected at the retrieval boundary per the USER-locked 2026-06-30 directive) — but the ONE downstream-
  utility probe that asked "does this composition help a task vs the sub-primitives alone" landed
  **HONEST_NEGATIVE**. So the noise-injection + facade machinery is real and correctly built, but nobody has
  shown it helps generation (or anything else) yet.
- **Cortex-2** (`hdlab/atom_consultation.py`, 978 lines; advisory -> SHADOW/WARN/LIVE dose-response over the
  substrate's own ~99 CG_META methodology atoms): this is what the USER's "M3 needs a cortex layer" project note
  was actually asking for (the substrate acting on its own knowledge) — but I confirmed by reading the code
  (`research_memo_cortex_needs_reencode_verdict_and_decisive_experiment_2026-07-04.md`, itself a direct code read)
  that it reasons over CURATED METADATA (op_class tags, discrete recommendation strings) via a tiny
  purpose-built `CharTrigramEncoder` sidecar that is explicitly, in the code's own docstring, "NOT the substrate
  n_dim." **It does zero FHRR bind/unbind on concept-encoder atoms and does not touch language at all.** It is a
  self-referential rules-engine over the substrate's own build discipline (op_class -> recommendation), not a
  reasoning-over-meaning layer. It is PARKED behind the encoder for unrelated reasons (needs a thicker,
  addressable substrate for a DIFFERENT future phase — semantic retrieval over the full 178k store — that was
  explicitly deferred, never built).

**Net: the M1.7/M1.9 primitives (RoleSlotSummarizer + SemanticParser) that DO operate on structured role-filler
HD bundles are the closer analog to "cortex operating on composed meaning" than either object literally called
"cortex" — see section 2 below.** Neither Cortex-1 nor Cortex-2, as they exist today, is a blocker for the
minimal language demo; conflating "cortex layer" with "prerequisite for speaking a grounded phrase" would be a
category error the filesystem does not support.

---

## 2. SEQUENCING — is language the capstone after ingest+integrate, or a parallel track?

**Parallel track for the narrow capability; capstone for the full one.** The dependency chain the USER's question
assumes (ingest -> integrate -> language) is the right shape for FULL conversational glass-box-LM, but the
MINIMAL grounded-utterance capability does not wait on the blocked steps:

| Dependency | Status | Blocks the minimal demo? |
|---|---|---|
| Perception/encoder (GSBC_EXPAND2X) | DONE, shipped, retrieval gap SOLVED via graded codes (2026-07-05) | NO — already the decoder's input |
| Narrow structured KG ingest (ConceptNet/FB15k-237/Wikidata, ~178k atoms) | DONE, existing, real named atoms (verified section 3) | NO — already the decoder's vocabulary source |
| General-knowledge ingest (Wikipedia/books/common-crawl) | **USER-LOCKED "not yet"**, explicitly out of scope | NO — the minimal demo does not need general knowledge, only the existing narrow KG |
| Bind/unbind compositional algebra | CHAIN_GRADE, mature | NO — already what the decoder IS |
| Multi-hop KG retrieval | CHAIN_GRADE (FB15k-237/ConceptNet/HotpotQA 2-hop) | NO — reusable as-is for sourcing real facts |
| INTEGRATION (reason -> generate compose) | **HARD_PASS at FULL, VET-confirmed, 2026-07-05** — symbolic cleanup beats a learned bridge; object-slot recovery 1.000 | NO — this is the exact bridge the demo reuses |
| Generation decoder (Stage A/B/C, native GSBC fillers) | **LANDED TODAY**, exact-ordered 1.000 to D<=26/V<=1024 | NO — this IS the demo's output stage |
| Dogfood ingest (our own notes, step 2 of the post-encoder plan) | NOT YET RUN (staged behind cortex-2 resume) | NO — irrelevant to a demo sourced from existing KG facts |
| M3 Cortex-2 (autonomous atom-consultation) | Parked, MM_TENTATIVE/SMOKE, self-referential | NO — as shown in 1(c), it doesn't touch language |
| Cortex-1 downstream utility | HONEST_NEGATIVE (unproven) | NO — the demo does not require the facade, only the primitives it composes |

Every gate that is genuinely BLOCKED (general-knowledge ingest, dogfood ingest, Cortex-2 LIVE-mode) is either
USER-locked-closed or simply irrelevant to a demo built from already-ingested narrow structured knowledge. The
things that DO gate the minimal demo — encoder, narrow ingest, algebra, retrieval, the reason-generate bridge,
the decoder — are ALL already done. This is why section 3's proposed cell is buildable now rather than a future
milestone.

**What IS a genuine capstone, sequenced after everything above:** the FULL M3/M4 conversational glass-box-LM
(grammar/morphology, autonomous cortex-mediated dialogue, general-knowledge grounding). That requires, in
addition to everything in this table: (i) Cortex-2 graduating past MM_TENTATIVE to a demonstrated reasoning
payoff (currently the one utility probe available is HONEST_NEGATIVE for Cortex-1 and untested for Cortex-2);
(ii) the one-to-many generalization ceiling (FRONTIER, closed as a genuine entropy ceiling this session — Hits@k
achievable, rank-1 is not) needs a resolution or a reframe before "answer any question, not just retrieve a
stored fact" is honest; (iii) morphology/function-word encoding, which is entirely unbuilt; (iv) the USER-locked
general-knowledge ingest gate would need to be explicitly lifted. None of those four are close. So: **narrow
grounded utterance = parallel-track, ready now; full glass-box-LM conversation = capstone, several
still-open bets away.**

---

## 3. THE SMALLEST REAL LANGUAGE DEMO — cell spec

**Name:** `exp_generation_grounded_fact_utterance_v1` (proposed; not dispatched per task instruction).

**What it does, end to end, reusing ONLY already-proven primitives:**
1. **Source real facts, not random triples.** Pull N>=20 subject-relation-object edges from the ALREADY-INGESTED
   ConceptNet/FB15k-237 atoms (the same corpus the CG multi-hop-retrieval cells already use). Hand-filter to
   common-word entries (reject Latin binomials / obscure technical CN_ nodes — a one-line regex/frequency filter
   against `id_order_json`, since the raw pool is unfiltered and the willet-shorebird problem is real).
2. **Retrieve, don't hand-supply.** Run the existing CG multi-hop retrieval primitive to fetch each fact (proves
   the pipeline starts from a query, not a pre-selected answer — closes the query -> answer loop, not just the
   encode -> decode loop).
3. **Compose via the proven bridge.** Feed the retrieved subject + relation into the Integration reason-generate
   bridge (symbolic cleanup->lookup, HARD_PASS mechanism, already shown to dominate a learned linear bridge) to
   produce the bound S/V/O proposition — reuses the EXACT mechanism VET-confirmed HARD_PASS this session, not a
   new composition step.
4. **Decode via the landed native block-local decoder** (`exp_generation_decoder_gsbc_native_blocklocal_v1`,
   Stage A factor / Stage B order / Stage C cleanup) to recover the ordered token-id sequence.
5. **THE ONE NEW STEP: print the human-readable output.** Map each recovered `concept_row` back through
   `id_order_json` to its real name string and print the ordered sequence — e.g. for a fact like
   (scabicide, causes, scabies-death) the pipeline should emit literal readable tokens such as
   `"scabicide -> kills -> scabies"` (exact surface form depends on the ConceptNet relation-to-verb mapping used),
   alongside the mechanical provenance trace (which unbind op produced which token, and its cleanup cosine) so
   the output is faithful-by-construction and auditable, not narrated after the fact.

**Why this is the RIGHT smallest cell (not a smaller or bigger one):** every stage reuses an ALREADY-CG-or-
HARD_PASS primitive except the string-lookup-and-print, which is not an experiment at all — it's instrumentation.
The only genuine open question this cell can answer that is NOT already answered is: **does the chained,
end-to-end (retrieve -> bridge -> decode -> name-lookup) pipeline still hold when composed, and does the output
actually read as recognizable words to a human** (the two things no existing cell has checked, because existing
cells check each stage in isolation with synthetic or hand-supplied inputs at the joints).

**Pre-registered bands:**
- **HARD-PASS:** end-to-end exact-ordered token match (against the true fact) >= 0.70 across >= 20 hand-vetted
  common-word triples; every emitted string round-trips through `id_order_json` to a real, human-legible name
  (zero garbled/placeholder decodes); a shuffled-fact control (same words, scrambled subject-relation-object
  pairing) collapses to near-chance exact-match (discriminator fires, proves the pipeline isn't just emitting
  fixed high-frequency words regardless of input).
- **HARD-FAIL:** exact-ordered match < 0.30 (the chained composition breaks something that worked in isolation —
  a genuine integration bug, not a mechanism failure, since every component independently clears its own bar), OR
  >= 20% of "correct" decodes are non-legible/obscure to a plain human reader (the mechanism is right but the
  vocabulary curation is not — an honest partial result: the substrate DOES retrieve/compose/decode correctly,
  it just doesn't yet look like "language" without curation).
- **MIDDLE:** 0.30-0.70, OR mechanism clears but legibility fails — diagnostic, not a wall; the fix in either case
  is curation/filtering of the ConceptNet vocabulary subset, not new architecture.
- **Effort:** near-zero. No new mechanism, no GPU, no new training. Estimated ~100-150 lines of glue + a manual
  curation pass over ConceptNet node names (CPU-local, minutes).

**How this maps to Levelt's stages (the brain analog, cross-checked against today's generation drill, not
re-derived):** Conceptualization (choosing WHAT fact to express) = the multi-hop retrieval step; grammatical
encoding (lemma selection + argument structure, order-independent at this stage) = the Integration bridge's
subject/relation/object binding; the frame-and-slot positional stage = Stage B (position-as-bound-factor,
independently cross-validated this session against competitive-queuing and theta-gamma phase-slot coding);
phonological encoding (mapping the selected lemma to its sound/word FORM) = the CLOSEST ANALOG in the substrate is
Stage C cleanup (concept-id -> `id_order_json` name string) — but this is the weakest part of the mirror: Levelt's
phonological stage handles morphology and word-form assembly, while Stage C only does a table lookup to a
frozen, pre-existing string. **The substrate mirrors Levelt's functional + positional stages well (Stage A/B); it
has no analog yet for morphological/phonological ASSEMBLY (Stage C is retrieval, not generation-of-word-form).**
That is the honest, precise version of "already partly mirrored in the frame-slot decoder" — partly is correct;
the missing third is morphology, not order or retrieval.

---

## 4. VERDICT — capstone or premature?

**Neither, cleanly — it is a MIS-SCOPED single question.** The narrow capability (retrieve a real fact, compose
it, speak it as an ordered short phrase of real named concepts) is READY NOW, not premature — every load-bearing
piece independently clears CG or HARD_PASS, verified off-disk in this drill, and the missing piece is
instrumentation (string lookup + print), not research. Calling this "language" in the sense the USER's north-star
means (a fully-functional glass-box-LLM-capable substrate, conversational, general-knowledge-grounded, grammatical)
IS premature and IS the capstone — it needs Cortex-2 to prove a reasoning payoff it has not yet shown (or possibly
does not need, if the narrow-utterance track proves sufficient for a real product story on its own), needs the
one-to-many generalization ceiling addressed or reframed, needs morphology/function-word encoding that is
entirely unbuilt, and needs the USER-locked general-knowledge gate explicitly lifted. The honest sequencing is:
**ship the narrow grounded-utterance demo now (cheap, decisive, closes a real "first spoken fact" milestone) as a
parallel track alongside the ongoing capstone bets, rather than treating either as blocking the other.**

---

## Cheap decisive test

Run `exp_generation_grounded_fact_utterance_v1` as specified in section 3 (~100-150 lines of glue over 3 already-
proven primitives + a manual ConceptNet-name curation pass). Single CPU-local smoke, no GPU, no new training. This
is the cheapest possible test because every failure mode it can surface (integration-joint breakage, vocabulary
legibility) is diagnostic and actionable in isolation — no ambiguity about which stage broke, since each stage has
an independent CG/HARD_PASS baseline to compare against.

## Falsifiable predictions

- **HARD-PASS:** end-to-end exact-ordered token match >= 0.70 on >= 20 curated common-word ConceptNet S/V/O
  facts; zero garbled/obscure-to-a-human decodes; shuffled-fact control collapses (discriminator fires).
- **HARD-FAIL:** exact-ordered match < 0.30 (a genuine, novel integration-joint bug between three otherwise-proven
  primitives), OR >= 20% non-legible decodes (mechanism sound, vocabulary curation the real gap).
- **HARD-FAIL (capstone claim):** if anyone represents this narrow demo, if it passes, as "the substrate speaks
  English" or "language is solved" — it is NOT; it is telegraphic (no morphology, no function words, no grammar
  beyond fixed-slot content-word order) and drawn from a narrow pre-ingested KG, not general knowledge. The
  HARD-FAIL condition for HONEST FRAMING is exactly this over-claim, independent of the cell's own numeric result.

## Cross-thread synthesis

Directly extends and cross-checks, without redoing: `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`
and `notes/research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md` (today's Levelt/Dell/competitive-
queuing/theta-gamma/resonator-network cross-field convergence — reused, not re-derived, per the 2x-drill
discipline); `notes/inventory_prior_cortex_reasoning_work_build_vs_fresh_2026-07-04.md` (Cortex-1/Cortex-2 status,
confirmed by direct code read this pass); `notes/research_memo_cortex_needs_reencode_verdict_and_decisive_experiment_2026-07-04.md`
(Cortex-2 does not touch the concept encoder — confirmed); `notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md`
(step sequencing, confirms general-knowledge ingest and Cortex-2 resume are NOT on the minimal demo's critical
path); `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md` +
today's internal-history scour (why the OLD bigram/trigram statistical-LM language track closed: a Hebbian/HRR
associative-memory W-matrix capacity wall on CONTEXT-TRANSITION storage, ~13,500x over capacity at production
scale — a DIFFERENT mechanism than today's decoder, which stores a linear V-size codebook and factors a KNOWN
bound proposition rather than predicting from statistics, and so does not inherit that wall); director backup
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` (INTEGRATION HARD_PASS + GENERATION LATEST
LANDING, both dated today, both verified against this note's own filesystem checks).

## Substrate-product implications

1. **A genuinely new, cheap, high-signal milestone is available right now:** "the substrate speaks its first
   grounded fact" — a real product-visible moment (a literal printed phrase, traceable end-to-end from query to
   spoken words) that costs a CPU-local glue script, not a research bet. Ship it before the next capstone push;
   it is a concrete existence-proof of the whole encode->retrieve->reason->generate loop that no single existing
   cell currently demonstrates together.
2. **Do not conflate "cortex layer" with "language prerequisite."** Two different pieces of code both carry the
   name; neither gates the narrow demo. Keep that distinction explicit in future planning to avoid an artificial
   dependency (waiting on Cortex-2 to "unlock" language, when the encoder+algebra+retrieval+decoder already do).
3. **The vocabulary-legibility problem (obscure ConceptNet nodes) is a real, cheap-to-fix product issue** — worth
   a one-time frequency/common-word filter over the 177,899-name table, reusable for every future demo that reads
   from this pool, not just this cell.
4. **Precisely scope any external or internal claim about this capability**: "retrieves and speaks a real
   grounded fact as an ordered short phrase" is honest and provable now; "the substrate generates language" is not
   — it lacks grammar, morphology, and general-knowledge grounding, and conflating the two would repeat exactly
   the over-claim pattern the USER's no-smoke discipline exists to catch.
5. **The morphology/phonological-assembly gap (Stage C is retrieval, not word-form generation) is the correct
   next research question if/when the narrow demo ships** — it is unopened, not failed, and is a smaller, more
   tractable-sounding gap than "language" as a whole once isolated this precisely.

## Citations (verified count)

This drill is primarily an internal-filesystem verification pass (concept-name provenance traced directly,
3 npz files read and inspected by hand) plus reuse of an ALREADY-CALIBRATED external lit-scan from today's sibling
drill. No new external citations were gathered in this pass (deliberate, per 2x-drill discipline — the relevant
literature was already gathered same-day and re-searching it would be redundant token spend, not rigor). Reused
citation set (already lit-scan-calibration-penalized in its origin note, ~40 core + ~10 flagged-approximate,
5 independent Sonnet sub-agents, cross-corroborated): Levelt 1989; Dell 1986; Garrett 1975/1980/1988; Roelofs
WEAVER++ 1992/1997; Bullock & Rhodes, Houghton 1990, Kornysheva et al. 2019 (competitive queuing); Lisman &
Idiart 1995, Jensen & Lisman, Lisman & Jensen 2013 (theta-gamma phase-slot coding); Frady/Kent/Olshausen/Sommer
2020 (resonator networks); Hersche/Terzic/Karunaratne/Rahimi 2025 (sparse-block-code factorizers); Plate 1995
(HRR capacity); Ramsauer et al. 2020 (modern Hopfield exponential capacity). Verified-by-this-pass (primary, not
literature): `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`, `data/substrate_index/cached_indices/
bge_large_v2_name_177899_54f7cf6a.npz` (id_order_json field, 177,899 real name strings, hand-inspected).
