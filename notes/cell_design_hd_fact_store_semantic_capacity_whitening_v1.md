# Cell design: hd_fact_store_semantic_capacity_whitening_v1

INLINE-LOCAL foreground measurement (no queue/push/remote). Author: exp_dev. VET-PENDING.

## Question (USER 2026-07-24)
The 29532 capacity result (obj recovery ~1.0 to V=1M) was measured on EXACT bipolar
near-random codes. The real semantic encoder (29533, SemanticHDEncoder) produces STRONGLY
CORRELATED codes (anisotropy 0.588 vs 0.122 random). `correlation-hurts-capacity` is banked
(reference_correlation_hurts_associative_store_capacity...2026-07-08, cosine 0.40 KB-hit).
So the "1M-fact foundation-ready" claim MUST be re-checked on the REAL semantic representation
before we scale, and WHITENING tested as the fix.

Prior-work check: TOP KB hit = reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval
(cosine 0.3955, >0.30). This cell is a RE-VERIFICATION/EXTENSION of that banked principle onto the
FACT-STORE cleanup codebook specifically (not novel) -- it measures WHERE the wall lands on the
real GloVe rep and whether the canonical ZCA whitening restores it. Reported as build-on, credited.

## Nuance (designed in)
A fact is a role-slot bundle: quantize(bind(ARG0,subj)+bind(REL,rel)+bind(ARG1,obj)+bind(SOURCE,src)+bind(TRUST,trust)).
Role vectors (ARG0/REL/ARG1/SOURCE/TRUST) stay RANDOM; only the FILLERS (subj/rel/obj values) become
semantic/correlated. Crosstalk lives in TWO places:
 (a) full-fact round-trip: bundle noise from the other 4 bindings + argmax cleanup over the object codebook;
 (b) semantic-codebook cleanup: argmax over a codebook where SIMILAR concepts are CLOSE -> harder than
     argmax over near-orthogonal random symbols. This is the real question -- meanings overlap.

## Method (reuse, not reinvent)
- Byte-identical store primitives: hdlab.role_slot_summarizer._bipolar_bind/_quantize/_random +
  hdlab.event_bundle.EventBundleCodec.role_key (same as HDFactStore / 29532 Part B).
- Whitening: hdlab.whitening.WhiteningTransform (canonical ZCA, the 4-atom chain-grade impl).
- Semantic codes: GloVe (glove-wiki-gigaword-300, cached) top-V words -> L2 rows -> Gaussian JL(300->n_dim)
  -> sign() = correlated bipolar codebook (same JL as 29533/word2vec_bind).
- Whitened codes: ZCA-fit on the L2 GloVe matrix (300d), transform, -> JL -> sign().
- Random codes: _bipolar_random (reproduces 29532 baseline == Gate-D positive control).

## Arms (codebook types) x n_dim {2048, 8192} x V sweep
1. random  2. semantic_raw  3. semantic_whitened.
V(real GloVe): 2048 -> {1k,10k,100k}; 8192 -> {1k,10k,50k} (memory bound: 50k*8192*4=1.6GB).
Analytical extension to V=1M: SYNTHETIC codes with anisotropy MATCHED to measured semantic_raw
(shared-direction generator), chunked, n_dim=2048 (labeled SYNTHETIC-MATCHED).

## Measurements
M1 anisotropy(bipolar codebook) per arm (mean off-diag pairwise cos, 2000-sample). Discriminator.
M2 ISOLATED cleanup recovery vs V (part b): filler_hat = true code exactly, argmax over V codes.
   Isolates semantic-codebook-cleanup difficulty from bundle noise.
M3 FULL-FACT round-trip recovery vs V (part a): 5-role bundle, semantic subj+obj, unbind obj, cleanup.
M4 conflict/sr_key false-conflict rate: distinct (subj,rel) semantic sr_keys with cosine>=0.75 (precision wall).
M5 semantic-structure-survives-whitening: synonym-pair vs random-pair bipolar cosine SEPARATION per arm.
   If whitening kills separation -> capacity restored AT THE COST of fuzzy-retrieval structure -> HYBRID.
M6 SYNTHETIC-MATCHED 1M analytical probe (isolated cleanup to V=1M).

## Pre-reg bands (envelope-fail)
- Discriminator fires: aniso(semantic_raw) >= aniso(random) + 0.05 (correlation present in real rep).
- CORRELATION-HURTS confirmed if: semantic_raw M2 recovery drops < 0.95 at some (n_dim,V) while
  random stays >= 0.99 at the SAME point (CAN-FAIL; if random also drops, wall is dim not correlation).
- WHITENING RESTORES if: semantic_whitened M2 recovery >= random - 0.05 at the point where raw failed.
  PARTIAL if it lifts raw by >=0.10 but stays < random-0.05. NO-FIX if within 0.05 of raw.
- HYBRID IMPLICATION fires if: M5 shows semantic_raw separation > 0.05 AND semantic_whitened separation
  < raw*0.5 (whitening destroys the fuzzy-match structure while restoring capacity).
- Determinism: threads=1; re-run one point bit-identical (bipolar dots exact int).

## Honest verdict targets
Report the recovery-vs-V curves (semantic-raw / semantic-whitened / random baseline), where the
crosstalk wall lands on correlated codes, whether whitening restores it, the semantic-cleanup-is-harder
finding (M2 raw vs random at matched V), and the honest foundation-scale verdict on the REAL rep. If
raw semantic caps well below random AND whitening trades capacity for semantic structure (M5), report
the hybrid: EXACT-ID keys for high-capacity fact storage + semantic codes only for FUZZY-match retrieval.

## Contract
INLINE-LOCAL foreground-to-completion (timeout 600000); NO queue/push/remote-persist; store LOCAL-ONLY
uncommitted; glass-box; deterministic (threads=1, fixed seeds); ASCII-only; serialize; only stop what we spawn.
