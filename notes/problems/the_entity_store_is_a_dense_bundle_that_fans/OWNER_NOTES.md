---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_entity_store_is_a_dense_bundle_that_fans   (STATUS: SOLVED)
hdlab/ UNTOUCHED by this session (proposed diff only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_entity_store_fan.py        -> core 21/21
          .venv/Scripts/python.exe verification/test_entity_store_frontier.py   -> frontier 26/26
          python tools/problem_ledger.py --check  -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════

BAR (PROBLEM.md §7): reduce the FAN-EFFECT SLOPE CI-separated vs the dense-bundle baseline, with an
info-free twin LOSING; report CI half-width + null p95; residual tracks item-SIMILARITY not COUNT.
Decisive either way.

CORE RESULT — the disk CORRECTS the brief, then the real problem is SOLVED brain-faithfully.
- The measured LitBank fan (0.945@few -> 0.657@many, slope 0.288) is NOT superposition blur. It is an
  ADDRESSING COLLISION + argmax readout: unique-(entity,sentence) decodes at 1.0000 at EVERY fan level;
  22.7% of addresses hold >1 verb; top-m set-return recovers the set at ~1.0 (the info is intact).
- Brain-faithful fix flattens it CI-separated: a FINER conjunctive temporal key (TCM) OR a SET-RETURN
  read (CA3 context-cued reactivation) -> slope 0.288 -> ~0.000, contrast -0.288 [-0.311,-0.265].
  FINER_CTX === FINER_CTX_SPARSE: sparse coding adds NOTHING to the measured fan (it's addressing).
- Info-free twin LOSES: shuffled-order twin 0.502 vs true 1.000, -0.498 [-0.480,-0.518], null p95 0.520.
- Sparse DG is the right design for the SEPARATE high-load SUPERPOSITION regime (dense_flat -> 0.048 at
  N=800; sparse holds 1.0), residual similarity-gated (3.5x) not count-gated.

FRONTIER (owner pushed "do it right, brain-foundational" — built + measured, each with an info-free twin):
Built the maximally brain-faithful episodic store and validated it, incl. ON REAL LitBank (28,569 queries):
- FACTORIZED two-system store (the optimal design): SHARP exact-recall + GRADED context, read SEPARATELY,
  bound only at storage. Gets BOTH on real data: fan slope 0.001 [0.000,0.004] AND contiguity 0.585 --
  where a single graded key is stuck trading them (fan 0.194 / contiguity 0.585, d-independent).
- SHARP half = SPARSE DG k-WTA (Treves-Rolls capacity): at fixed dim on correlated content, dense collapses
  to 0.454 @ N=8k, sparse (a=0.02) holds 1.000 -- ~2x+ capacity from sparsity alone; twin at chance.
- Also measured: reconstructive SEMANTIC errors (DRM intrusions 5.5x chance), EVENT-BOUNDARY effect
  (within>>across, gap 0.39), handmade PATH-INTEGRATION scaffold (relational transfer 0.80 vs abs-time 0.0),
  trained local-rule SUCCESSOR-REPRESENTATION predictor (next-event 1.0 vs chance 0.09), schema/gist
  interception (gain concentrated in coherent entities), race-to-stop set-return (F1 0.93 without oracle m).
- INDEPENDENTLY VALIDATED by the newest neuroscience: Bausch et al. 2026 (Nature, human single-unit:
  content & context are SEPARATE populations bound by timing) + TEM (bind only at storage). Verdict on the
  crux: sparsity COMPLEMENTS, does NOT dissolve, the separation-vs-contiguity tradeoff.

PROPOSED hdlab DIFF (strategy re-verifies + lands):
1. Fix the fan by the KEY not the store: finer conjunctive event key + a SET-RETURN decode mode on the
   situation-model register (sparse coding is NOT the measured-fan fix).
2. Adopt the two-system FACTORIZED store: sparse DG expand+k-WTA exact-recall half (a≈0.02-0.05) + graded
   multi-timescale context half, bound only at storage, read separately.
3. Schema/gist interception of routine events; race-to-stop set-return (no oracle count).
4. Test-before-commit (flagged, not assumed): CA3 iterative completion (Neher 2015 redundant vs Nakazawa
   2002 necessary); SR-layer/grid redundancy (Stachenfeld 2017).

KEY REALIZATIONS: (1) "ask whether the experiment could have SUCCEEDED first" — unique-address=1.0 killed
the superposition premise in one check; (2) the graded context's CONTIGUITY *is* the adjacent-slot leak, so
you can't get exact-recall + contiguity from one key — the brain uses TWO systems (measured, then confirmed
by Bausch 2026); (3) a learned scaffold is brain-founded in its TARGET (path-integration g/x) not its
TRAINING (backprop) — use handmade path-integration + local-rule SR, skip BPTT-TEM; (4) sparse DG's right
home is the exact-recall COMPONENT (capacity), not the fan fix (addressing).

FILES: experiments/{exp_entity_store_sparse_fan_v1, _schema_gist_v1, _graded_temporal_v1, _unified_v1,
_unified_litbank_v1, _sparse_capacity_v1}.py; verification/{test_entity_store_fan, test_entity_store_frontier}.py;
notes/problems/the_entity_store_is_a_dense_bundle_that_fans/{SOLVED.md + 4 research_*.md}. GPU-ready LitBank
validation is queue-compliant (--self-test/--smoke/metrics.json) for the remote box. hdlab/ UNTOUCHED.

TLDR: the "busy character memory" wasn't blurring — we filed several actions under one tag and read back
only one; file each action under a finer moment-tag and return the whole set and it vanishes. Pushed past
that to build the brain's actual episodic store — a two-system memory (a sparse, high-capacity "what"
store + a graded "when" store, kept separate and joined only when writing) — which on real novels recovers
what a character did AND preserves the sense of what happened nearby, and whose errors look like human
errors (misremember toward meaning; confuse adjacent moments). It matches human single-unit data published
this January. hdlab is untouched; it's a proposed design awaiting your DONE.

QUESTIONS: none. NEXT STEPS: strategy lands the finer-key + set-return fan fix first (cheap, real-data
proven), then the two-system sparse-DG + graded factorized store; test-before-commit the CA3-completion and
SR/grid-redundancy items; run the GPU-ready LitBank validation on the remote box during integration.
═══════════════════════════════════════════════════════════════════════════════════════════
