# Pre-reg: state_of_mind_relevance_gather_reasoning_union_v1

USER-directed task (2026-08-11 spawn to exp_dev): decisive prototype of the "weak->strong"
combination bet -- reasoning over a STATE-OF-MIND-conditioned relevance-gathered union
recovers grounded facts absent from every single source, and that naive combination
(voting/blind-union) cannot produce. Corrects two prior wrong-mechanism tests (voting;
edge-density).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh` run with the mechanism keywords. Top hit cosine=0.3701
(notes/research_consolidation_confidence_permanence_relational_inference_2026-07-14.md --
provisional-relation CONFIDENCE dynamics, a different mechanism: Bayesian confidence update on
a single relation, not multi-source relevance-gather + chain composition). No hit above
cosine=0.30 tests this exact mechanism (state-of-mind-cued CA3 gather -> K<=2 chain over a
multi-source union). Verdict: NOVEL, not a rediscovery.

## Sources (real, disk-backed; declared scope)
- S_READ: (process, entity_head, fate) facts, regenerated deterministically by calling
  `experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision.extract_facts_strict`
  over `data/corpora/process_articles_v1/process_articles.json` (same corpus + extractor as
  commit 2e3ed1edf / exp_bootstrap_dense_process_article_reading_fade_v6). MEASURED: 103 unique
  (process, entity, fate) triples across 15 processes (40 articles, 1229 sentences).
- S_CSKG: `data/cskg_foundation_v1/edges_shard_*.jsonl` (1,213,912 edges; CSKG multi-source
  merge of ConceptNet/VisualGenome/ATOMIC/WordNet/Wikidata). Used at TWO scopes:
  - NARROW (`/r/MadeOf` only, obj=material in S_READ vocab): the CUED arm's hop-2 bridge.
    MEASURED: 92 raw MadeOf edges touching the 70-word S_READ vocabulary.
  - WIDE (ANY of the ~30 CSKG relation types touching the material, either direction): the
    BLIND arm's hop-2 candidate pool. MEASURED: 10,310 edges, 4,863 distinct candidate wholes.
- CauseNet-precision + go.obo (`data/bio_kb_cache/`, ingested commit 875598d08): INSPECTED,
  DECLARED OUT OF SCOPE as a bridge-relation source. CauseNet-precision (197,806 causal pairs,
  full file scanned) is dominated by social/medical causal pairs (disease->death,
  accident->injury) with ZERO literal overlap with this gap-set's (process, whole) pairs
  (MEASURED: 0/657 vocab-touching hits match a gap-set (process,whole) pair) -- it DOES
  independently corroborate several S_READ facts (photosynthesis->oxygen, combustion->
  carbon_dioxide, combustion->smoke), a nice sanity signal that the domain is coherent, but it
  supplies no MATERIAL-COMPOSITION bridge for this domain. go.obo's relations are
  process-to-process (is_a/part_of within the biological_process hierarchy), not
  process-to-substance -- not a composition bridge either. Declaring this honestly rather than
  force-fitting an unhelpful source, per the task's own "if too few survive, report it
  honestly" spirit extended to source selection.

## Mechanism (reuse owned organs, cited)
- STATE OF MIND: `hdlab.situation_model_accumulate.RelationRegister` (bind_filler /
  decode_filler) -- per process P, `bind_filler(P, "GAP_MATERIAL", content_vec)` once per
  material P's own reading facts mention; the register is the FHRR bundle of ALL of P's
  established materials (the "maintained context"). `decode_filler` unbinds exactly (single
  role, proven exact by the module's own docstring) -> a noisy composite query vector = sum of
  P's material content vectors.
- RELEVANCE-CONDITIONED GATHER: `hdlab.cleanup_family.iterative_attractor`, called in a
  peel-loop (deflate + repeat, matching-pursuit style) against a codebook of ALL 70 materials,
  to recover the SET of materials in P's own bundle (CA3-style pattern completion recovering
  the gap's neighborhood from a superposed cue) -- NOT a blind full scan (the BLIND arm skips
  this and uses every material + every relation type indiscriminately). FHRR complex64 -> real
  adapter: `concat(Re(v), Im(v))` preserves the exact cleanup inner product
  (Re(conj(a).b) = dot(concat(Re(a),Im(a)), concat(Re(b),Im(b)))), so `iterative_attractor`'s
  real-valued cosine cleanup is mathematically identical in scoring to
  `situation_model_accumulate.cleanup_argmax` on the native complex vectors, just with
  iterative_attractor's multi-step attractor refinement on top.
- REASON -> GROUNDED SEGMENT: `hdlab.kg_traversal.KGStore` (the n8 CERT-585 chain-grade
  multi-value Hebbian (s,p,o) store) + `predict_one_hop_topk` fan-out composition (K=2: hop1
  process->material via FATE relation, hop2 material->whole via BRIDGE relation), aggregated
  by max(hop1_score * hop2_score) per candidate whole. Single-path `naive_chain`/
  `predict_two_hop` is NOT used directly because hop1 is genuinely multi-valued (a process can
  have several materials tied to the same fate, e.g. combustion DESTROY -> {magnesium, heat,
  gas}); a single top-1 argmax would arbitrarily pick one and silently drop the others,
  confounding the gather-vs-blind measurement with an unrelated hop1 tie-break artifact. The
  fan-out composition reuses the SAME certified single-hop primitive
  (`KGStore.predict_one_hop_topk`, the primitive `naive_chain`/`predict_two_hop` themselves
  call) -- not a new retrieval mechanism, a different (K=2, multi-candidate) composition of it.

## Gap-set construction (programmatic, deterministic, audited)
1. For each S_READ fact (P, C, F), for each S_CSKG-narrow whole X with `(X, /r/MadeOf, C)`,
   X != C: candidate target = (P, X, F).
2. NO-LEAK ABSENCE FILTER: candidate survives iff (P, X, F) is NOT itself a literal S_READ
   fact (i.e. X was never directly extracted as fate F for process P). CSKG/CauseNet/go.obo
   structurally cannot express this predicate at all (no process-fate-entity schema), so they
   are trivially absent for every candidate; this is verified programmatically (arm0 check
   below), not merely assumed.
3. AUDIT (MEASURED): 124 raw candidates -> 121 survive the absence filter -> 121 unique
   (process, whole, fate) targets across 9 of the 15 processes (combustion, photosynthesis,
   electricity_generation, erosion_weathering, hydrocarbon_formation, igneous_rock_cycle,
   carbon_cycle, sedimentation, respiration). Honest note: candidate diversity is skewed by 2
   hub materials (`water` via CN commonsense "mostly-water" facts: lettuce/ocean/rain/human_body/
   ice/etc, and `steel` via WD manufactured-object facts: bicycle_frame/submarine/knife/etc) --
   reported per-hub in metrics so this skew is transparent, not hidden. A handful of targets
   inherit reading-extraction noise (the v2 extractor is ~0.85 precision, not 1.0) -- e.g.
   `photosynthesis CREATE leaf` (via chlorophyll) is a plausible extractor mis-attribution, kept
   honestly (not hand-filtered) because the pre-reg's "verify absence + report the audit,
   don't fabricate derivability" mandate applies to the CONSTRUCTION pipeline, not to post-hoc
   cherry-picking of only the facts that look nicest.
4. If a target set this size did not survive, that would itself be reported as the honest
   finding (per task instructions); it did survive at N=121, so the decisive test proceeds.

## Arms (query = (P, F); success = recovering a specific gold X)
- **Arm 0 (best single source alone):** structural check, executed as real code (not assumed):
  for each target, verify (P,X,F) is absent from S_READ's own fact set (by construction, always
  true) AND that CSKG has no direct process-fate-entity edge at all (true by schema: CSKG has no
  "process" node type with a fate relation) AND CauseNet has no literal (P,X) pair among the
  full-file scan hits. `arm0_recall = 0.0` by construction; reported as `arm0_structural_zero`,
  not silently assumed.
- **Arm 1 (BLIND UNION + K=2 fan-out, no state-of-mind cue):** hop-2 KGStore ingests, for EVERY
  material in ALL 9 processes' vocab (cross-process mixed, no per-query restriction), ALL CSKG
  edges of ANY relation type touching that material (the WIDE pool, 10,310 edges / 4,863
  wholes) as generic BRIDGE triples. hop-1 KGStore is the shared S_READ store (same for all
  reasoning arms; hop-1 is not where blind/cued differ). This is the literal "not narrowed by
  relevance" arm.
- **Arm 2 (VOTING / co-occurrence, no chaining):** for query (P,F), candidate pool = every
  whole connected (ANY relation, WIDE pool) to ANY of P's own materials REGARDLESS of fate
  match; rank by raw edge-count frequency (no bind/unbind, no argmax chain, no fate-relation
  awareness). Top-1 = highest count, deterministic tie-break by first-seen order.
- **Arm 3 (STATE-OF-MIND CUED gather + K=2 fan-out):** RelationRegister + iterative_attractor
  peel-loop recovers P's own material set from the bundled register (validated against ground
  truth as `gather_precision`/`gather_recall`, both self-test-gated >= 0.90). hop-2 KGStore
  restricted to (a) ONLY the CA3-recovered materials and (b) ONLY `/r/MadeOf` edges (the NARROW
  pool). Same fan-out+aggregate composition as arm 1, different (smaller, relevance-scoped)
  ingested content -- isolating "gather scope" as the one experimental variable between arm1
  and arm3.

Metric: recovery@1 (top-1 aggregate-score whole == gold X) and recovery@5 (gold X in top-5),
per arm, averaged over all 121 targets (and reported per-process).

## Controls
- **SCRAMBLE-THE-CHAIN:** fixed-seed permutation of the NARROW pool's (material -> whole)
  endpoint assignment (shuffle which wholes attach to which materials, same edge count/degree),
  rebuild arm 3's hop-2 store, rerun. Expect recovery@5 to collapse toward the empirical chance
  floor (~1/|candidate pool per material|).
- **ABLATE-THE-STATE-OF-MIND-CUE:** arm1 vs arm3 IS this ablation by construction (arm1 =
  arm3's identical fan-out+aggregate algorithm, MINUS both the CA3-material-scope restriction
  and the MadeOf-only relation restriction). Report recovery delta arm3 - arm1.

## Pre-registered bands
- HARD_PASS: recovery@5(arm3) >= recovery@5(arm1) + 0.20 absolute AND recovery@5(arm3) >= 0.20
  absolute (clears arm0's structural 0) AND scramble collapses arm3 recovery@5 to <= 0.10 AND
  ablation delta (arm3 - arm1) on recovery@5 >= 0.15.
- HARD_FAIL: recovery@5(arm3) <= recovery@5(arm1) (blind suffices; state-of-mind not
  load-bearing) OR recovery@5(arm3) <= 0.05 (mechanism inert) OR scramble does NOT collapse
  arm3 (post-scramble >= 0.5x pre-scramble) OR ablation delta < 0.05.
- MIDDLE_BAND: any measured outcome between the two (e.g. arm3 beats arm1 but under the strict
  margin, or one control is borderline/ambiguous). MIDDLE_BAND is an acceptable, informative
  outcome per task instructions; no rubber-stamping to HARD_PASS.

## SCHEMA-VET gates
- `sweep_alignment_verdict`: N/A -- no swept axis (fixed 121-target gap set, 4 arms, one seed
  regime); declared `no_sweep_axis`.
- `discriminating_fraction`: N/A for the same reason; declared `no_sweep_axis`.
- `composition_edges`: KGStore(hop1, S_READ) -> KGStore(hop2, BRIDGE) SHAPE_MATCH (both
  bipolar-codebook KGStore instances sharing ONE seeded E/R codebook so entity/relation vectors
  are bit-identical across arms; only ingested-triple content differs).
- `positive_control_arms`: `predict_one_hop_topk` / `KGStore.ingest_triples` are the n8 CERT 585
  chain-grade primitive, reproduced at THIS regime by the self-test (tiny synthetic fixture,
  below) before the real-data run -- tolerance: self-test top-1 recovery must be exact (1.0) on
  the planted chain, since the fixture is noise-free by construction.
- `functional_requirements`: (1) represent a maintained gap/context -> RelationRegister
  (existing organ). (2) narrow a large union to the relevant neighborhood -> iterative_attractor
  peel-loop (existing organ). (3) compose 2 hops of retrieval into a grounded prediction ->
  KGStore.predict_one_hop_topk fan-out (existing organ, K<=2 per its own chain-grade scope).
  No new mechanism class introduced.
- `real_code_path_exercised`: [RelationRegister, iterative_attractor, KGStore] -- self-test
  constructs all three as REAL objects at N~10-16 entities, not a synthetic-only branch.
- `substrate_signature_checked`: KGStore(n_ent=int, n_rel=int, n_dim=int, generator=Generator)
  -- base/portable kwargs only (no `init_entities` override; matches F.3's stable-signature
  discipline).
- `guard_baseline_validated`: N/A -- no control-beats-baseline break-guard in this cell (bands
  above are direct recovery-rate thresholds, not a POP-vs-RANDOM guard); declared `n/a`.
- `deterministic_seeding`: true -- ALL RNG uses `torch.Generator().manual_seed(<fixed int>)`;
  gap-set construction and CSKG/S_READ scans are pure-Python deterministic (`sorted()` on all
  dict/set iteration before use, no `hash()`-derived ordering).
- `crlb_n/a`: "discrete top-k retrieval accuracy over an exactly-enumerated candidate pool, not
  a continuous-noise-floor reconstruction metric; no Gaussian argmax-noise CRLB applies."
  `discriminator_reachability`: true (0.20 absolute margin is achievable given arm1's WIDE pool
  averages ~85 candidates/material vs arm3's NARROW pool averaging ~3 candidates/material --
  chance-level top-5 for arm1 is far below chance-level top-5 for arm3 by construction).
- `baseline_in_band` (META_RULE_AG): arm1 (baseline-ish, the ablated/no-cue arm) is NOT
  expected in [0.05,0.95] by design -- it is the intentionally-weakened control being compared
  against, not a saturating baseline; declared `exempt: arm1_is_the_can-fail_control_not_a_
  saturating_baseline`.
- `cell_chunked`: false (single deterministic pass, no per-seed axis; wall time well under the
  chunking threshold).
- `arms_differ_verified`: MANDATORY at smoke -- arm0/1/2/3 per-target prediction arrays hashed;
  asserted not-all-identical.
- `final_metrics_atomicity`: `tmp_replace` (single-shot; tmp file + os.replace).
- `progress_logging`: N/A -- `timeout_s` for this cell is well under 1800s (measured smoke
  ~45s, measured FULL ~130s including the 80s CauseNet full-file leak-audit scan); the
  print-progress-flushing MANDATE only applies at `timeout_s >= 1800`. Declared
  `progress_cadence_expected_s: n/a (short cell)`.

## Compute architecture
Sequential-CPU, justified: N=121 targets x 4 arms, each a tiny (<5,100-entity) KGStore matmul
at n_dim=2048 -- reasoning-only wall time < 5s total; the dominant cost is I/O (frontend
load ~22s, CSKG shard scan ~8s, optional CauseNet bz2 scan ~80s FULL-only), not compute --
GPU batching would not help an I/O-bound, sub-5000-entity symbolic pipeline. Storage strategy:
`sharded_kgstore_hebbian_associative` -- each entity/material/whole is its own random codebook
row (sharded); KGStore's W is the standard multi-value Hebbian accumulation, the SAME primitive
already chain-grade-certified at K=2 (n8 CERT 585) -- not a from-scratch bundle-everything
design.

## Self-test (formula, real-code-path, per F.1)
Synthetic fixture at N~16 entities (6 processes-analog, 4 materials, 6 wholes), n_dim=64: ONE
planted cross-source chain (whole0 MadeOf material0; process0 DESTROY material0) that is ABSENT
as a direct (process0, whole0, DESTROY) edge by construction. Asserts:
(a) arm0 structural check reports absent (0.0) for this planted target;
(b) arm3 (cued, real RelationRegister + real iterative_attractor peel + real KGStore fan-out)
    recovers whole0 at top-1 for query (process0, DESTROY);
(c) arm2 (voting, no fate-awareness) does NOT reliably recover it once a same-material
    different-fate distractor whole is added (voting can't distinguish fate-match).
This is the "known cross-source chain recovered by arm-3 and NOT by arm-0/2" gate the task
requires. Exercises REAL objects (RelationRegister, iterative_attractor, KGStore) at tiny scale,
not a synthetic-only mocked branch.

## Smoke design
Real pipeline (real frontend load + real corpus read + real CSKG scan), restricted to 2
processes (combustion, photosynthesis) to keep wall time low; CauseNet full-file leak-audit
scan SKIPPED in smoke (80s, declared `causenet_leak_check: full_mode_only`). Smoke gate: the
discriminator must fire -- recovery@5(arm3) - recovery@5(arm1) >= 0.10 on this 2-process subset
before FULL is dispatched (DISCRIMINATOR-MUST-SURVIVE-SCALE, preview-arm form: smoke runs the
REAL retrieval mechanism on real (if reduced) data, not a toy substitute).

## Dispatch
Estimated wall time: smoke ~45s, FULL ~130s (both CPU-only, no GPU benefit). Per the
USER-LOCKED 2026-07-01 rule, SMOKE runs on `local_cpu_queue`; FULL is handed off to
`remote_cpu_queue` (fast, but the lock has no fast-cell carve-out) via the exact
`queue_add.sh` command in the completion report, for the orchestrator to ship.
