# THREE-TIER KNOWLEDGE ARCHITECTURE -- DESIGN + OWNED-ORGAN AUDIT (2026-08-11)

Self-contained (written for post-compaction pickup). This is DESIGN/AUDIT ONLY -- no code
was built or changed in this pass. All file paths are relative to `d:/AI/hd-instrument/`
unless stated otherwise. Every organ below was READ (not label-trusted) and cross-checked
against `data/capability_registry.jsonl` (104 rows) where a registry entry exists.

## THE USER'S ARCHITECTURE (recorded verbatim, 2026-08-11)

On a knowledge GAP:
1. **GATHER** as much context as possible from a LARGE NUMBER of complementary comprehensive
   databases (holistic multi-source, combination of ALL sources).
2. **REASON** to ANSWER the question with the gathered info.
3. **PARSE** the new info into FOUNDATIONAL KNOWLEDGE VECTOR(S), as much as possible.
4. If it passes the **GATE** -> promote to the foundation.
5. If NOT -> it stays in a **~MIDDLE database** of gathered info that is ALWAYS REFERRED TO
   FIRST, accumulates (may grow very large), and is PERIODICALLY SWEPT for NEAR-CONCEPTS to
   optimize/consolidate -> combined evidence eventually passes the gate.

Brain-faithful framing: Complementary Learning Systems (McClelland/O'Reilly/Norman).
GATHER = external refs; MIDDLE = hippocampus (fast/accumulate/always-first); FOUNDATION =
neocortex (consolidated); GATE + SWEEP = systems consolidation.

## HEADLINE FINDING (read before anything else)

**The user's exact 5-step architecture is not hypothetical -- an ~80%-complete implementation
of it was already built and run end-to-end this session, and it HARD_FAILED at full scale.**
This is the single most important fact for planning next steps: this is not a green-field
design exercise, it is a POST-MORTEM-INFORMED design exercise. Every organ recommendation
below is filtered through "did the one place this was actually assembled and tested on a
real benchmark work," and the honest answer is: the FADE half worked, the
CONSOLIDATE/SWEEP/PROMOTE half did not clear its own gates.

Evidence (disk-verified this pass):
- `data/exp_crutch_fade_social_iqa_v1/metrics.json` (binary baseline, FULL, real Social IQa
  dev n=1954 + CSKG 1.15M edges): **verdict=HARD_FAIL**. Fade mechanism itself worked
  (fire_rate 0.3378->0.2958, rel_drop=0.1242, no_regression=True, scramble-controlled) but
  comprehension lift was flat (+0.0123, below the +0.05 band).
- `data/exp_crutch_fade_social_iqa_v1_3tier_seed7/metrics.json` (the actual 3-tier
  MIDDLE-tier-plus-sweep build, FULL scale): **verdict=HARD_FAIL**.
  `tier_fidelity_ok=False` (HP2) -- combined-evidence cluster promotions (n=403 at
  checkpoint 100%) scored **worse** than raw uncorroborated crutch lookups
  (combined_acc=0.356 vs cru_acc=0.369). `comp_lift_covered` for the 3-tier arm
  (0.366) **underperformed** the binary baseline (0.377) on the same covered-item slice
  (HP3=False). The fade-vs-binary comparison DID show more fade (rel_drop 0.36 vs 0.12,
  HP1=True) -- the extra machinery fades the crutch faster, it just doesn't make the
  combined evidence trustworthy enough to use.
- `data/exp_crutch_fade_bank_native_promotion_test_a_v1/metrics.json` (the
  exposure+consistency promotion-gate unit test cited in memory as "Test-A cleared"):
  **verdict=MIDDLE_BAND**, not HARD_PASS. The specific numbers memory cited are correct
  (gate1_promote_rate=1.0 5/5, guard_holds=True 0/12 leaks) but the cell's own overall
  verdict is MIDDLE_BAND -- correct the record: this is a promising but not a clean-passing
  result.
- `data/capability_registry.jsonl` row `crutch_fade_social_iqa` (id, line 89):
  `gate_decision: SHELVE`, `status: honest_negative_fade_works_lift_below_band_2026-08-10`.

Root cause chain the cell's own code comments disclose (3 iterations of live diagnosis,
all MEASURED not guessed): (1) a small number of SIQa-template hub concepts ("person",
"want", "happy" -- degree up to 8057 vs median 1.0) dominate crutch scoring regardless of
per-item relevance -> hub-degree penalty added; (2) even after hub penalty, the CA3/DG
near-concept clustering key (`relation_family` = CSKG relation TYPE, e.g. `xAttr`/
`xEffect`) is **intrinsically too coarse** -- a broad relation type spans huge, semantically
heterogeneous swaths of common sense, so "same relation family" != "same schema"; only 2
clusters formed by checkpoint 100 regardless of hub filtering. The per-item promote gate
was never loosened; the cluster-grain gate was made 4x stricter (never weaker) and STILL
failed fidelity. The code's own comment names the correct fix as future work: **the
clustering KEY itself needs to be semantic/embedding-based, not the raw CSKG relation-type
label** -- this is the single most actionable lead for a rebuild.

## (A) PER-STAGE TABLE: user's 5 steps -> owned organs

| # | User's step | Owned organ(s) | WHERE | Validated scope | Verdict |
|---|---|---|---|---|---|
| 1 | GATHER (multi-source, holistic) | `hdlab/director_kb.py` (+`director_kb_query.py`, `director_kb_chunk_ingest.py`, `director_kb_bio_sources.py`, `director_kb_math_sources.py`, `kb_encoder_registry.py`) | hdlab, WIRED (registry rows `director_kb_query`=15, `kb_encoder_registry`=13, `char_trigram_encoder`=12) | Ingests notes/, USER memory, preregs, `data/exp_*/metrics.json`, WordNet/VerbNet/FrameNet (NLTK API), GO/KEGG/NIF bio ontologies, unified chunk-level content queryable by cosine. Schema-as-config (`config/director_kb_schema.json`), deterministic, per-file reject-log, coverage_ratio manifest. | **REUSABLE** as the batch multi-source ingest engine, but it is a **build-time indexer**, not a live per-question fan-out-and-fuse. |
| 1 | GATHER (trust-vetted single store) | `hdlab/hd_fact_store.py` (`HDFactStore`) | hdlab, WIRED (registry row `hd_fact_store`=7, "WIRED_BUT_NOT_PIPELINE_REACHABLE") | Role-slot-bound (s,r,o,SOURCE,TRUST) bipolar bundle; glass-box unbind+cleanup recovery; native (s,r) HD signature for O(1) conflict lookup; INGEST-VET conflict resolution REPLACE/COMBINE/FLAG/DROP by trust rank. 5/5 self-tests pass (roundtrip, signature separation, four resolutions, zero false-flag, O(1)/O(n) index equivalence). | **REUSABLE**, well-tested at the unit level. This is the correct home for BOTH the foundation store (step 4) and, instance-per-tier, the middle-tier store (step 5, at `TRUST_LOW`) -- already used both ways (see row 5 below). |
| 1 | GATHER (worked multi-source merge, one-shot) | `experiments/exp_cskg_foundation_v1.py` | exp-cell, ISLAND by design (registry row `cskg_foundation_v1`=16, `ALREADY_WIRED_VIA_DATA_ARTIFACT` -- correctly NOT a live-import consumer, its ARTIFACT is what's load-bearing) | Streams full CSKG (ConceptNet+ATOMIC+WordNet+Wikidata-CS merge, 6.0M rows), SPINE relation filter, k-core decomposition, 4 grounding-norm attachments (Lancaster/Concreteness/VAD/AoA), held-out 2% reservation, relation-reconstruction can-fail gate vs shuffled control. **HARD_PASS** on its own gate (`data/cskg_foundation_v1/metrics.json`). Landed 1,238,686 typed edges / 482,588 nodes in `hd_fact_store` field schema. | **REUSABLE as a worked example / the concrete "foundation" this session's own crux experiment reads from** -- but it is a ONE-TIME batch script, not a reusable "gather-N-sources-live" primitive. Proves the SHAPE (many sources -> one hd_fact_store-schema foundation) is buildable and gate-able; does not provide the runtime fan-out. |
| 2 | REASON to ANSWER | `hdlab/glass_box_loop.py` | hdlab, WIRED (imported by several exp cells; not independently registered) | retrieve -> gate (BG Go/NoGo value-gate on arbitration margin) -> audit (Merkle-chained step log, tamper-detect) -> WM-mediated requery -> commit. CHAIN_GRADE-certified on real ConceptNet, non-ceiling at 80x scale (`exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1`, commit ba552930a). | **REUSABLE**, best-validated "answer with gathered info" loop. CAVEAT: its bind/bundle primitives are a semantics-matched **numpy reimplementation**, not a direct import of `hdlab.binding`/`hd_fact_store` -- a real build should re-verify equivalence or refactor to import directly before treating it as one pipeline with GATHER. |
| 2 | REASON to ANSWER (multi-cue / multi-hop) | `hdlab/multi_hop.py` (`naive_chain`, `iter_cleanup_chain`) over `hdlab/kg_traversal.KGStore` | hdlab, WIRED (registry row `kg_ingest`=23, 33 consumers) | CHAIN_GRADE at K=2 hops (`substrate_2hop=0.426` vs frozen-encoder baseline `0.012` = 36.49x, CERT 585). Accuracy decays beyond K=2 (disclosed HARD_FAIL in-file for the iterative-cleanup extension past K=2). | **PARTIAL** -- solid bounded (K<=2) hop primitive; do not assume it generalizes to deep multi-cue convergence. |
| 2 | REASON to ANSWER (typed derivation / meet-in-middle) | `hdlab/reasoner.py` (`DerivationReasoner`) | hdlab, registry row `reasoner_composed_entry_arc_program`=8: `gate_decision: SHELVE`, `status: built_2026-07-25_then_abandoned_2026-07-27`, "below-bands walls on every arm" | Composes typed-rule graph (P1) + negation-aware node identity + meet-in-middle forward/backward search (P3) + CI polarity-consistency check (P4) + do-calculus routing. Ambitious, most complete "multi-cue convergence" organ on disk. **Built, then abandoned** -- not a live win. | **MISSING (in practice)** -- exists on disk but is a known dead end for the ARC-comprehension task it was built for; would need its own re-diagnosis before reuse, not a drop-in. |
| 3 | PARSE into FOUNDATION VECTOR(S) | `hd_fact_store.HDFactStore.store()` (single-value-per-slot, lossy on conflict) | hdlab, WIRED | See row 1. Each `store()` call resolves a (s,r) conflict to ONE live object per trust rules (REPLACE/DROP) or an explicit COMBINE/FLAG for multivalued/contradictory cases -- i.e. this is symbolic-record fusion, not literal vector superposition of the *same* slot. | **REUSABLE** for typed-fact storage; NOT the "keep all context-dependent variants coexisting" mechanism the user's step 3 implies ("as much as possible" -- preserve multiplicity). |
| 3 | PARSE into FOUNDATION VECTOR(S) (context-preserving superposition) | `experiments/exp_bootstrap_fhrr_superposition_fade_v3.py` (`FHRRProcessStore`) | exp-cell (not yet promoted to hdlab) | Per-process FHRR (complex64) bind+bundle registers keyed by process, so multiple context-dependent (entity,fate) facts for the SAME entity coexist SEPARABLY rather than collapsing to one value (reuses `hdlab.binding` bind/unbind verbatim). Design doc claims v2's process-tag accuracy (0.7167) as the base gate. Self-test asserts 2 context-bound facts for one entity recover separably (real-code-path check). **FULL run on real ProPara: `verdict=HARD_FAIL_no_rise+no_fade_lesion_gap+scramble_no_collapse`.** | **PARTIAL** -- the representational MECHANISM (superposition-not-collapse) is exactly what step 3 asks for and is unit-level sound; the one real-corpus application of it this session HARD_FAILED on the downstream fade/lesion/scramble battery. Needs its own root-cause pass before reuse, and needs promotion out of a one-off exp-cell into an hdlab primitive. |
| 3 | PARSE (general accumulate-register primitive) | `hdlab/situation_model_accumulate.py` (`AccumulateRegister`, + `CausalLinkRegister`, `RelationRegister` subclasses) | hdlab, not independently registered but is validated per in-code citation "atom 29609" | FHRR bind(role_vec, filler)+bundle-accumulate per entity/event register; `unit_phase_vec`/`cleanup_argmax` readout. Two more-specific subclasses already extend it (event-causal-links, arbitrary-content relation registers) -- evidence this primitive genuinely reuses well. | **REUSABLE** general-purpose accumulate-and-cleanup primitive; a natural building block for a promoted version of the FHRR superposition store above. |
| 4 | GATE -> promote to foundation | `hdlab/grounding_acquisition_loop.consolidation_pass(..., native_store=HDFactStore)` | hdlab, WIRED (imports `hd_fact_store`; `hd_fact_store`'s own registry row lists `grounding_acquisition_loop.py` as a `used_by`) | THIRD, independent, strictly-stronger gate on top of BANK's own (schema_thresh, vote-margin) gates: exposure (>=8 traces) AND consistency (`abs(vote_margin)>=0.75`), operationalizing Logan 1988 instance-count + Schneider&Shiffrin 1977 consistent-mapping. `HDFactStore.store()` is the actual promotion write. Self-test 7a/7b (real `HDFactStore`, not synthetic) proves promote-fires-when-earned AND does-not-leak-when-merely-adequate. | **REUSABLE**, this IS the GATE the user's step 4 describes, already wired to write into a real `hd_fact_store`. |
| 5 | MIDDLE tier: always-first, accumulates, never discards | `TierState.prelim_lib` / `TierState.prelim_store` inline in `experiments/exp_crutch_fade_social_iqa_v1.py` (class `TierState`, function `update_prelim_and_generalize`) | **exp-cell only -- NOT promoted to hdlab.** Not independently registered (folded into the `crutch_fade_social_iqa` SHELVE row). | `prelim_lib` is a `grounding_acquisition_loop.Library()` instance **deliberately never passed through `consolidation_pass`** so items structurally never leave `PENDING` -- i.e. genuine retain-forever accumulation (the base `Library` in `grounding_acquisition_loop.py` itself does NOT have this property: it terminalizes to GROUNDED/ESCALATED and then rejects new evidence, which is the BANK/GATE engine for step 4, not the accumulate-forever store for step 5). `prelim_store` is a second `HDFactStore` instance at `TRUST_LOW`, queried at answer time (tag `PRELIM_RESOLVED`) as a fallback AFTER the native/foundation tier and BEFORE the raw multi-source crutch. This is a real, running implementation of "keep sub-threshold evidence, pull it at re-encounter" -- it ran at full scale and its retain+pull half was not itself the failure point (see combined_evidence numbers above; the SWEEP step is what failed fidelity, not the retain/pull step). | **PARTIAL** -- the mechanism EXISTS, ran end-to-end on a real benchmark, and its core retain/accumulate/pull property is exactly step 5's spec. It needs (i) promotion out of one exp-cell into a reusable hdlab module (currently an unexported inner class), and (ii) the sweep-step fix below. |
| 5 | PERIODIC SWEEP for near-concepts | `hdlab/script_grain_acquisition_loop.py` (`ScriptLibrary.match_or_spawn`, `script_consolidation_pass`) called via `update_prelim_and_generalize`'s `relation_family()` clustering key | hdlab, WIRED (imported by the exp-cell above; not independently registered) | CA3/DG soft-match-or-spawn keying via the OWNED `hdlab.cleanup_family.iterative_attractor` (brain-canonical, Treves-Rolls), FHRR script-instance registers (`build_instance_register`), `calibrate_novelty_threshold`, prioritized replay (`surprise_order` as an actual consolidation-attempt-budget gate, not just diagnostic). **Self-test passes**: matched-vs-wrong-type separation (margin>0.15), scramble-must-collapse control (2 iterations to get combinatorially robust), match/spawn correctness, singleton-noise-never-merges. The MECHANISM is sound in isolation. **Its one real-corpus application (the `relation_family`-keyed clustering inside crutch_fade_social_iqa_v1) HARD_FAILED fidelity** -- see Headline Finding above; root cause is the clustering KEY (CSKG relation-type label), not the CA3/DG matcher itself. | **REUSABLE mechanism / MISSING correct application** -- the attractor-clustering organ is validated; what's missing is a semantically-adequate clustering KEY (embedding-based near-concept similarity) to feed it, in place of the too-coarse relation-type label that caused the HARD_FAIL. |
| 5 (underlying) | Attractor / cleanup primitive powering the sweep | `hdlab/cleanup_family.py` (registry: `iterative_attractor`=one of 5 `PRIMITIVES`) + `hdlab/iterative_attractor.py` (`iterative_cleanup`) | hdlab, WIRED (registry rows `readout`=20, `pattern_completion`=22, `cleanup_attractor`=24, all `ALREADY_WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`) | Soft cosine-similarity attractor with softmax weights over an L2-normalized codebook; brain-canonical CA3/DG. Self-tests: zero-noise identity recovery, low-noise recovery, argmax-limit equivalence, contracting trace, batched shapes, basin-robustness sweep -- all pass. Also provides `classical_hopfield`, `modern_hopfield_continuous`, `k_NN_lookup`, `no_cleanup` as swappable siblings, plus `peel_sic_readout` (beats flat top-J at high bundle load, CG-certified). | **REUSABLE**, solid low-level primitive; this is not where the sweep failure lives. |
| 5 (secondary gate) | "genuinely compressible" MDL check on accumulated middle-tier evidence | `hdlab/learner/` (`core.mdl_select`, `registry.learn`/`apply`, `plugins/{estimation,ruleind,gam,proginduction}_plugin.py`) | hdlab, **not found in `capability_registry.jsonl`** (an apparent registration gap, not a code gap) | Two-part-code MDL model-selection engine (Perfors & Tenenbaum 2009); wraps two already-banked cells (condenser atom 29476, rule-inducer atom 29485) as plugins behind one `learn()`/`apply()` interface; `per_cluster_gate` enforces "must compress past the null code." `consolidation_pass`'s `mdl_gate_fn` hook (both `grounding_acquisition_loop.py` and `script_grain_acquisition_loop.py`) is designed to plug this in CONJUNCTIVELY (AND, never OR) with the existing schema-consistency guard -- but neither `crutch_fade_social_iqa_v1.py` call site actually passes an `mdl_gate_fn` (both call sites use the default `None`). | **PARTIAL** -- the organ exists, is wired at the interface level (the hook is there and documented), but was **never actually invoked** in the one real end-to-end run. This is a concrete, low-risk next lever: turning on the MDL gate the design already anticipates, rather than only the cosine-based schema-consistency check, before concluding the sweep step needs a whole new clustering key. |
| (fade dynamics, cross-cutting) | replay-based drift mitigation | `hdlab/continual.py` (`replay_cycle`, `nrem_replay_decorator`) | hdlab, WIRED (registry row `catastrophic_forgetting`=25, 16 consumers) | NREM sharp-wave-ripple replay analog; **proven-bound, not chain-grade**: +0.57 absolute drift_reduction at best schedule (replay_every=100), but forget<=0.05 bar NOT met (partial mitigator only). Companion proven-negative on file: global downscale (REM analog) destroys older traces uniformly, deliberately not exposed as public API. | **PARTIAL** -- real, disk-proven, bounded improvement; do not expect it alone to solve consolidation drift for a live three-tier loop. |

## (B) CONCRETE BUILD SPEC

### Data flow (one gap -> resolution)

```
gap detected (e.g. bow_margin below gate_thresh, per resolve_item() pattern already in
exp_crutch_fade_social_iqa_v1.py)
  |
  v
[1] MULTI-SOURCE GATHER  ---------------------------------------------------------------
  query, in this order, EVERY source that is cheap enough to hit live:
    (a) FOUNDATION hd_fact_store instance(s)      <- hdlab.hd_fact_store.HDFactStore.query()
    (b) MIDDLE-tier hd_fact_store (TRUST_LOW)     <- same class, second instance
    (c) director_kb (chunk-content + typed-triple index)  <- hdlab.director_kb_query
    (d) any standalone batch-built foundation (e.g. cskg_foundation_v1 edges_shard_*.jsonl,
        loaded once at process start into an in-memory pair-index, per
        exp_crutch_fade_social_iqa_v1.load_cskg_index)
  FUSE: this session's ONLY real precedent (crutch_fade_social_iqa_v1.resolve_item) does
  NOT fuse scores across sources into one holistic vector -- it tries stores in strict
  PRIORITY ORDER and takes the first that fires (native -> prelim -> raw crutch). This is
  the honestly-validated pattern; a true score-fusion ("combination of ALL sources" in one
  shot) is a NEW component (see Gap G1 below), not something proven to work yet.
  |
  v
[2] REASON to ANSWER  ------------------------------------------------------------------
  hdlab.glass_box_loop's retrieve -> gate -> audit -> requery -> commit shape (re-verify /
  re-wire to import hd_fact_store + kg_traversal directly rather than its own numpy
  reimplementation). For >1-hop questions, bound the hop depth at K<=2
  (hdlab.multi_hop.naive_chain / iter_cleanup_chain) per its own disclosed chain-grade
  scope. Do NOT reach for hdlab.reasoner.DerivationReasoner without first reading
  notes on WHY it was abandoned 2026-07-27 (below-bands on every arm) -- treat it as a
  research lead, not a component to wire in as-is.
  |
  v
[3] PARSE into FOUNDATION VECTOR(S)  ----------------------------------------------------
  Prefer hdlab.situation_model_accumulate.AccumulateRegister-style bind+bundle
  (context-preserving superposition) over a single hd_fact_store.store() call whenever the
  same (entity, relation) can legitimately take context-dependent values -- this is what
  exp_bootstrap_fhrr_superposition_fade_v3.FHRRProcessStore attempted; promote its
  FHRRProcessStore class into hdlab/ as a reusable sibling of AccumulateRegister BEFORE
  reusing it, and re-diagnose its HARD_FAIL on real ProPara first (see Gap G3).
  For facts that are genuinely single-valued (most typed KB triples), hd_fact_store.store()
  is fine as-is and is the one already wired into the GATE step below.
  |
  v
[4] GATE  ------------------------------------------------------------------------------
  hdlab.grounding_acquisition_loop.consolidation_pass(..., native_store=<foundation
  HDFactStore>, promote_min_exposure=8, promote_min_consistency=0.75) -- REUSE VERBATIM.
  This is the validated exposure+consistency+schema-consistency conjunctive gate. PASS this
  turn's SWEEP-passing mdl_gate_fn (see [5b] below) into the currently-unused
  mdl_gate_fn= hook -- this is free (the interface already exists) and untested in the one
  real run, so it is the first thing to try before any deeper rebuild.
  |
  |-- PASS --> promote into FOUNDATION hd_fact_store (TRUST_HIGH/TRUST_MID per consistency)
  |
  '-- FAIL --> [5] MIDDLE TIER  -----------------------------------------------------------
        (a) RETAIN: a second, PERMANENT-PENDING grounding_acquisition_loop.Library() +
            a TRUST_LOW hdlab.hd_fact_store.HDFactStore instance -- copy the
            TierState.prelim_lib / prelim_store pattern out of
            experiments/exp_crutch_fade_social_iqa_v1.py verbatim into a new hdlab module
            (this is the single highest-value promotion in this whole spec: it is the only
            piece of the user's exact step-5 spec that is both already-built AND was not the
            locus of the HARD_FAIL).
        (b) SWEEP: hdlab.script_grain_acquisition_loop.ScriptLibrary.match_or_spawn, called
            periodically (every N gaps or every checkpoint) over the middle tier's pending
            items. DO NOT reuse relation_family() (the CSKG relation-type label) as the
            clustering key without a fix -- this was the disk-diagnosed root cause of the
            fidelity HARD_FAIL. Candidate fixes, cheapest first:
              (i) swap the clustering key to a semantic-embedding cosine over the pair's own
                  extracted concepts (e.g. the encoder already validated+WIRED as
                  scale_win_tinytransformer_encoder, registry row 3) instead of the CSKG
                  relation-type label;
              (ii) turn on the already-wired-but-unused mdl_gate_fn hook in
                  script_grain_acquisition_loop.script_consolidation_pass as a SECOND,
                  conjunctive filter on which clusters are even eligible to combined-evidence
                  promote (cheap: the hook exists, just was never passed a real function);
              (iii) only if (i)+(ii) still fail fidelity, consider a genuinely new clustering
                  key design (out of scope for a first rebuild).
        (c) COMBINED-EVIDENCE PROMOTE: re-evaluate the IDENTICAL [4] GATE at cluster grain
            over agreeing members only (update_prelim_and_generalize's own pattern, keep the
            CLUSTER_EXPOSURE_MULTIPLIER=4 stricter-never-weaker discipline) -> loops back to
            [4].
        Middle tier is ALWAYS QUERIED FIRST relative to the raw external multi-source GATHER
        (this matches the already-implemented priority: native foundation -> prelim/middle ->
        raw crutch) so repeat gaps get progressively cheaper/faster answers as the middle
        tier accumulates, even before anything promotes.
```

### Minimal module inventory for a rebuild (in priority order)

1. `hdlab/hd_fact_store.py` -- use as-is (foundation + middle-tier instances).
2. `hdlab/grounding_acquisition_loop.py` -- use `Library`, `consolidation_pass` as-is for
   the GATE; but this session's PENDING-forever middle tier ("prelim") is NOT in this file
   -- it must be extracted from the experiment cell (step below).
3. **NEW hdlab module** (promotion, not new design): extract `TierState` /
   `update_prelim_and_generalize` from `experiments/exp_crutch_fade_social_iqa_v1.py`
   (lines ~571-697 of that file) into a new `hdlab/prelim_tier.py` (or fold into
   `grounding_acquisition_loop.py` as an alternate `Library` mode) -- generalize away the
   Social-IQa/CSKG-specific bits (`pair_key`, `relation_family`) into caller-supplied
   functions, mirroring how `hdlab.learner`'s plugin registry generalized two prior
   one-off cells.
4. `hdlab/script_grain_acquisition_loop.py` -- use `ScriptLibrary.match_or_spawn` as-is,
   but do NOT reuse `relation_family()`; supply a new, semantic clustering key function
   (Gap fix (i) above).
5. `hdlab/cleanup_family.py` / `hdlab/iterative_attractor.py` -- use as-is (already the CA3/DG
   engine underneath #4).
6. `hdlab/learner/` -- wire its `mdl_select`/plugin machinery into the `mdl_gate_fn` hooks
   in both #2 and #4's consolidation passes (currently unused in the one real run --
   cheapest untried lever).
7. `hdlab/glass_box_loop.py` + `hdlab/multi_hop.py` + `hdlab/kg_traversal.py` -- for the
   ANSWER stage; re-verify glass_box_loop's numpy primitives against real `hd_fact_store`/
   `kg_traversal` semantics before trusting it as one pipeline with the rest.
8. `hdlab/director_kb.py` + `hdlab/director_kb_query.py` -- for broadening GATHER beyond a
   single hand-loaded CSKG-shard index, if/when the rebuild needs more than one external
   source live (current validated precedent uses exactly one external source, CSKG).
9. `hdlab/situation_model_accumulate.py` (`AccumulateRegister`) + promoted
   `FHRRProcessStore` (from `exp_bootstrap_fhrr_superposition_fade_v3.py`) -- for PARSE,
   only where context-dependent multi-valued facts are actually expected; re-diagnose the
   FHRR store's real-corpus HARD_FAIL first (Gap G3).

## (C) HONEST GAPS

- **G1 -- no live multi-source SCORE FUSION.** Every validated precedent (this session's
  crutch-fade cell) tries sources in strict PRIORITY ORDER and takes the first hit; nothing
  on disk fuses N sources' evidence into one holistic context vector per the user's literal
  "combination of ALL sources" framing. Building true fusion (vs. priority-fallback) is new
  work, not a wire-up.
- **G2 -- the SWEEP step's clustering key is the disk-diagnosed root cause of the one real
  HARD_FAIL**, not the CA3/DG matcher itself. Any rebuild that reuses `relation_family()`
  unmodified will very likely reproduce the same fidelity failure. This is the single
  highest-leverage fix identified in this audit.
- **G3 -- the FHRR superposition foundation-vector store (`exp_bootstrap_fhrr_
  superposition_fade_v3`) is unit-sound but real-corpus HARD_FAILED** (no rise, no
  fade/lesion gap, scramble didn't collapse). Its self-test proves the representational
  claim (two context-bound facts coexist separably) but the full pipeline around it did not
  show the expected behavior on ProPara. Root cause not yet diagnosed on disk -- do this
  before promoting it into the PARSE stage of a rebuild.
- **G4 -- the middle tier ("prelim") mechanism is islanded inside one experiment cell.**
  It is the most literal, most validated-in-motion match to the user's step 5 spec, but it
  has never been promoted to `hdlab/`, contrary to this project's own WIRE-don't-island
  discipline. Promoting it is cheap (it is already generic-enough code) and should happen
  before any new build reinvents it.
- **G5 -- the MDL conjunctive gate (`hdlab/learner`) was wired at the interface level but
  never actually exercised** in the one real end-to-end run (`mdl_gate_fn=None` at both call
  sites). Untested, not proven to help or hurt; cheap to try (Gap fix (ii) above) before
  deeper redesign.
- **G6 -- `hdlab.reasoner.DerivationReasoner` (the most architecturally ambitious ANSWER-
  stage organ) is a disclosed dead end** ("below-bands walls on every arm", abandoned
  2026-07-27). Do not silently reuse it as if it were validated; it needs its own
  diagnosis or a from-scratch replacement for the ANSWER stage of any rebuild.
- **G7 -- registry hygiene.** `hdlab/learner/`, `hdlab/script_grain_acquisition_loop.py`,
  `hdlab/grounding_acquisition_loop.py`, and the middle-tier `TierState` pattern have NO
  independent row in `data/capability_registry.jsonl` (only `hd_fact_store`'s row
  mentions `grounding_acquisition_loop.py` in passing, as a `used_by` entry). Recommend
  adding explicit registry rows for these once a rebuild lands, per this project's own
  formal WIRE-or-SHELVE gate discipline.
- **Corrections to avoid propagating mislabels found this pass:** (i) `hdlab/store.py` is
  a DuckDB-backed **execution-TRACE logger** (op/inputs/output/modulator-state per step),
  NOT a foundation-knowledge-vector store -- do not confuse it with `hd_fact_store.py`.
  (ii) The base `grounding_acquisition_loop.Library` (word-grain) TERMINALIZES
  (GROUNDED_*/ESCALATED reject further evidence) -- it is the GATE engine for step 4, not
  the accumulate-forever store for step 5; only the ad hoc `TierState.prelim_lib` (never
  routed through `consolidation_pass`) has the retain-forever property step 5 needs.
  (iii) "Test-A cleared" in prior memory is directionally right on the cited sub-numbers
  (5/5 promote, 0/12 leak) but the cell's own verdict is MIDDLE_BAND, not HARD_PASS --
  cite it as promising-but-unclean, not validated.

## SMALLEST FIRST EXPERIMENT to validate the loop end-to-end on a real gap

Goal: isolate whether Gap fix (i) (semantic clustering key) alone resolves the one known
real-world failure, before any larger rebuild. This reuses 100% existing, already-shipped
machinery and changes exactly ONE variable, matching this project's own experiment-design
discipline (one-var, real baseline, can-fail discriminator, pre-registered bands).

1. **Anchor**: a new cell, e.g. `exp_crutch_fade_social_iqa_v2_semantic_cluster_key.py`,
   forked from `experiments/exp_crutch_fade_social_iqa_v1.py`.
2. **ONE change**: replace `relation_family(idx, pk)` (the CSKG relation-type clustering
   key fed into `ScriptLibrary.match_or_spawn`) with a semantic-embedding cosine key built
   from the pair's own two concept strings, using the already-WIRED
   `scale_win_tinytransformer_encoder` (registry row 3, "the project's best-validated
   from-scratch concept encoder") or, if that is not readily composable, the char-trigram
   encoder already used by `director_kb` -- either choice must itself be logged as the
   experiment's stated one-variable change.
3. **Everything else held fixed**: same hub-degree exclusion (`HUB_DEGREE_THRESH=500`),
   same `CLUSTER_EXPOSURE_MULTIPLIER=4`, same `PROMOTE_MIN_EXPOSURE`/
   `PROMOTE_MIN_CONSISTENCY`, same 9-arm/5-checkpoint design, same frozen dev set.
4. **Gate** (reuse v1's own pre-registered shape, per
   `preregs/2026-08-10_crutch_fade_prelim_tier_staged_consolidation_v1.md`): HARD_PASS
   requires `tier_fidelity_ok=True` (combined-evidence cluster accuracy >= raw crutch
   accuracy, HP2) AND `comp_lift_covered` for the 3-tier arm >= the binary baseline's
   (HP3) -- i.e. literally flip the two HARD_FAIL flags this audit found, on the same
   real benchmark, same real 1.15M-edge CSKG crutch, no synthetic shortcut.
5. **Smoke first** at the already-known-working smoke scale (`SMOKE_TRAIN_CAP=15000`,
   `SMOKE_DEV_CAP=400` -- this scale MEASURED real promotions in prior history) before any
   FULL dispatch, per this project's standing smoke-gate discipline.
6. If smoke shows `n_clusters` still collapsing toward the 2-cluster degenerate case,
   that is itself the answer (semantic key alone insufficient) and motivates trying Gap fix
   (ii) (turn on `mdl_gate_fn`) as arm 2 of the SAME cell before escalating to a genuinely
   new clustering design.

This is deliberately the smallest change that directly tests this audit's own diagnosed
root cause (G2) against a real, already-hard, already-once-failed benchmark, reusing every
other validated organ unchanged.
