# Pre-reg: arc_fact_retrieval_semantic_kb_climb_v1

Staged 2026-07-24 (exp_dev). "THE CLIMB" -- wire MEANING into the vetted HD fact store, ingest
vetted ConceptNet triples through the trust-gate, answer ARC by FACT-retrieval, and test whether it
beats the sentence-IR (+0.043) and semantic-IR (+0.042) ARC-Easy floors.

Builds on banked VETs: 29530 (ARC human-scale measure, baseline=CHANCE 0.252, sentence-IR broad
+0.043, no answer-key leak), 29531/29532 (HD fact store trust-vetting + O(1) index),
29533 (SemanticHDEncoder meaning-match AUC 0.96, semantic-IR ARC +0.042), 29534 (capacity re-check:
single semantic-rep store IS foundation-scale to 100k -- NO forced hybrid).

Prior-work KB check (substrate_query.sh): top cosine 0.3066 (generic 'Fact' concept + metacognition
memory notes); NO prior ARC-fact-retrieval cell at cosine>0.30. Genuinely novel; builds on the
above ingredient VETs.

## The question (real, can-fail)
Does answering ARC-Easy by RETRIEVAL over a store of VETTED ConceptNet triples (semantic HD fillers,
trust-gate-resolved) BEAT semantic-IR over raw ARC_Corpus sentences (the +0.042 floor)? Both arms use
the IDENTICAL SemanticHDEncoder; they differ ONLY in store content (vetted triples vs raw sentences).
This isolates: does structuring knowledge as a vetted KB beat raw sentence retrieval?

HONEST EXPECTATION (deflated): likely FLAT or modest -- ConceptNet is commonsense-heavy
(AtLocation/CapableOf/Antonym/Causes), thin on grade 3-9 SCIENCE specifics -> coverage may cap the
climb. FLAT is an INFORMATIVE verdict here (diagnose COVERAGE vs MECHANISM), not a failure. Challenge
expected flat (multi-hop; separate reasoning layer).

## Arms
- `empty`            : empty fact store -> all choices tie -> seeded random -> ~chance 0.25 (leak floor).
- `fact_retrieval`   : ConceptNet triples through trust-gate -> live vetted facts -> semantic-encode
                       fact text "subj rel obj" -> ARC max-cosine argmax. Curve over ingest fractions.
- `semantic_ir_broad`: broad answer-agnostic ARC_Corpus sentence sample, SAME SemanticHDEncoder -> the
                       floor to beat (recomputed IN-REGIME per Gate D; not merely cited from 29533).
- `scramble`         : same-size random-bipolar store -> collapses to chance (genuineness control).

## Compute architecture
- class: **(b) sequential-CPU with justification**. Ingest is a sequential `store()` stream with a
  conflict-index dependency (each insert queries prior state); GloVe/WordNet lookups are CPU; ARC
  scoring is chunked numpy matmul (CPU). No GPU speedup path for the sequential ingest; scoring matmul
  is modest (~13.5k queries x <=60k facts). Wall estimate FULL ~15-25 min.
- storage strategy: **SHARDED** (HDFactStore stores each fact as its OWN role-slot bundle; per-fact
  recovery independent of #facts -- 29532). Retrieval store matrix is one row per live fact.
- **REMOTE-PORTABILITY: NOT remote-queue-eligible.** ConceptNet jsonl AND the gensim GloVe cache are
  git-ignored (verified `git check-ignore`) -> absent on origin/main -> a remote runner FileNotFounds.
  Same INLINE-LOCAL constraint as sibling cells 29530/29533. FULL runs LOCAL (director inline-local OR
  local_cpu_queue exception); NOT remote_cpu_queue/overnight_queue.

## Bands (author-designed; strictly-above-floor per META_RULE_L)
PRIMARY discriminator = ARC-Easy fact_retrieval accuracy at full ingest.
- **KB_BEATS_FLOOR (HARD_PASS)**: `fact_easy_full - semantic_ir_easy >= +0.02` AND
  `fact_easy_full - empty_easy >= +0.05` AND `fact_easy_full - scramble_easy >= +0.03`.
- **KB_FLAT (informative can-fail)**: `|fact_easy_full - semantic_ir_easy| < 0.02` -> KB does not beat
  raw sentence retrieval; report COVERAGE (ConceptNet ARC-vocab coverage) vs MECHANISM diagnosis.
- **KB_BELOW_FLOOR**: `fact_easy_full - semantic_ir_easy <= -0.02` -> triples lose to raw sentences.
- **LEAK_FLAG**: `scramble_easy >= fact_easy_full - 0.03` OR `scramble_easy >= empty_easy + 0.05`
  -> gain is artifact; overrides all.

## Mandatory honesty controls (a can't-fail cell is worse than idle)
1. empty-store baseline ~chance 0.25 (asserted in smoke; else answer-leak).
2. SCRAMBLE control collapses fact_retrieval gain to chance (margin >= 0.03).
3. BROAD ingest = a deterministic random 60k slice of ConceptNet (FULL), answer-agnostic -- ConceptNet
   is a fixed external KB, CANNOT be test-targeted (structurally resolves the 29530 tailoring caveat).
4. NO answer-key leak: ARC query index built from stem+ALL choices only, NEVER answerKey (reuses
   arc._build_queries which is code-verified leak-free in 29530); ConceptNet ingest never sees ARC.

## Monitors to REPORT (director cares)
- **ingest COVERAGE**: fraction of ConceptNet entities that landed with a REAL semantic vector (GloVe/
  WordNet hit) vs OOV-random; AND fraction of ARC-Easy question content-words present as ConceptNet
  entities (the real coverage cap -- thin science coverage silently caps the climb).
- **trust-gate fire rate**: histogram of resolutions (CLEAN_STORE/REPLACE/DROP/FLAG/COMBINE/DUP) over
  the ingest -- non-vacuous (conflicts detected + resolved by the 4 rules).
- **glass-box fact round-trip**: sample live facts, unbind + per-domain cleanup, recover subj/rel/obj;
  report recovery rate. Semantic-filler cleanup is HARDER than random-code (correlated codes) -- an
  honest crowding-cost number vs the 29531 random-code 1.000.
- **FUZZY conflict demo** (Part B, bounded curated set): semantic sr_key cosine detects a same-(s,r)
  surface-variant conflict (usa == united_states) that the exact O(1)-hash path MISSES; trust resolves
  it (closes 29531 gap #a). Bounded -- ANN/LSH sub-linear fuzzy retrieval at scale = noted-not-built.

## SCHEMA-VET fields
- cardinality_ok: n/a (no seed x sweep grid; ingest-fraction curve is one deterministic run).
- crlb_n/a: "accuracy discriminator, not a noise-floor estimator. Feasibility: chance floor 0.25 <
  HP target; store capacity proven to 100k live facts (29534) >> 60k ingest -> discriminator reachable."
- discriminator_reachability: true (HP band above chance floor; fact_retrieval can exceed OR tie OR
  lose the floor -- genuinely can-fail).
- baseline_in_band: true (empty ~0.25 in [0.05,0.95]); verified in smoke.
- final_metrics_atomicity: tmp_replace.
- arms_differ_verified: true (empty/fact/semantic_ir/scramble store hashes differ; asserted in smoke).
- calibration_check: default_ok_for_this_regime (sr_threshold 0.75 from 29531; fuzzy_threshold
  author-set 0.55 with a can-fail separation check in smoke).
- cell_chunked: false (single deterministic run; no seed axis).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- defensive_error_checking: passed_all_4_patterns.
- real_code_path_exercised: [SemanticHDEncoder, SemanticHDFactStore, arc._score_curve, arc._build_queries].
- substrate_signature_checked: [HDFactStore.__init__, EventBundleCodec._register].
- deterministic_seeding: true (fixed int seeds + numpy default_rng + sorted iteration; no hash()-seed).
- progress_logging: line_buffered_stdout + print_flush_true (FULL may exceed 15 min; heartbeats/stage).
- discriminating_fraction: n/a (not a sweep); discriminator-fires gate = fact_retrieval best-cosine
  non-trivial (>0.10 for a meaningful fraction) AND differs from scramble AND empty (smoke-asserted).

## Verdict logic
LEAK_FLAG (if triggered) > KB_BEATS_FLOOR > KB_FLAT > KB_BELOW_FLOOR. Report the fact-retrieval climb
number, the floor delta, WHERE limited (coverage vs mechanism), Challenge honestly (expect flat).
