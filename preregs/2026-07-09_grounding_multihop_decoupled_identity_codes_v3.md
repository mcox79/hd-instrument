# Pre-reg: reader WIN-CELL v3 -- DECOUPLED / NEAR-ORTHOGONAL IDENTITY CODES

**Anchor:** `grounding_multihop_decoupled_identity_codes_v3`
**Cell:** `experiments/exp_grounding_multihop_decoupled_identity_codes_v3.py`
**Filed:** 2026-07-09 (exp_dev). **Builds on:** `exp_grounding_multihop_local_chain_index_v2` (commit 8efbb57b7, HARD_FAIL_SEMANTIC_FLOOR, VET-confirmed).

## Thesis (falsifiable)

v2 landed HARD_FAIL_SEMANTIC_FLOOR: the LOCAL-neighborhood-scoping count-tax fix WORKS (LOCAL reach1=0.453 vs
GLOBAL 0.088; 6x lift) but reveals a floor beneath -- SAME-RELATION ALIASING. Among LOCAL hop-2 errors,
`local_aliasing_frac=0.815` vs same-relation `base_rate=0.491` (excess=0.324): same-relation sibling nodes have
codes too similar to disambiguate, AND that confusability EXCEEDS the graph's structural same-relation base rate
by 0.324 -- i.e. the codes ACTIVELY mislead toward the wrong same-relation sibling beyond chance.

KEY (MEASURED@data/exp_grounding_multihop_local_chain_index_v2/metrics.json:mechanism_selftest.reach_local): the
v2 self-test with CLEAN PLANTED separable codes gives LOCAL=1.0 at all depths. Clean/separable codes solve it;
the char-trigram+InfoNCE learned codes are the problem. The trigram features inject WORD-SURFACE correlation
(similar words -> similar trigrams -> correlated codes), and same-relation siblings tend to be semantically
similar, so the binding encoder is driven to place their codes too close.

**Fix under test (VET-corrected -- relation-conditioned scoring was RULED OUT because same-relation siblings
SHARE the relation so conditioning adds no discriminative info):** attack the REPRESENTATION. Replace the
semantically-correlated char-trigram input features with NEAR-ORTHOGONAL IDENTITY features (random Gaussian
per-node, pairwise cosine ~ 1/sqrt(feat_dim)), decoupled from word semantics. The binding encoder then places
each node's code freed from the trigram-correlation constraint, so same-relation siblings separate by IDENTITY
rather than being pulled together by shared surface content. This is the DG pattern-separation analog: decouple
the chain/identity layer (decorrelated) from the retrieval-semantic layer (correlated, kept in reserve).
Everything else (LOCAL neighborhood candidate scoping, chains, roles, seeds, dim) is held IDENTICAL to v2 -- so
any gap is purely the CODE design (feature decoupling), a clean within-dim attribution.

## Compute architecture

- **Class:** (a) batched-GPU. Substrate primitives (HRR bind = FFT elementwise mul; cleanup = matmul/einsum +
  argmax; DG sketch = matmul + top-m) are matmul-heavy and run device-aware torch (cuda if available). Per-hop
  chain retrieval has a genuine sequential dependency (hop N commit feeds hop N+1 candidate set), but WITHIN a
  hop all C chains are batched; the encoder training is fully batched. Sequential-across-hops is inherent to
  chain traversal (only MAX_REACH=4 hops).
- **Storage strategy:** SHARDED (each node its own code vector Z[node]; no bundled superposition). Chain
  retrieval is compositional (bind+cleanup sequence), so sharded is mandatory per META_STORAGE law. Confirmed.
- **Cost:** 3 encoders trained per seed (semantic / partial / identity) instead of v2's 1. v2 FULL ran 13.6s for
  3 seeds; v3 ~ 3x train cost => est 40-60s FULL on GPU. Cheap; route overnight_queue (GPU, idle).

## Arms (6; PAIRED -- identical planted chains + identical roles + identical seeds + identical graph + identical
dim across ALL arms; the ONLY difference is the INPUT FEATURES the encoder sees (=> the learned codes) and the
cleanup candidate set / scoring)

1. `NO_CLEANUP`         : must-fail control. Semantic codes (Z_sem). Raw HRR accumulation carried forward each
                          hop, top-1 GLOBAL readout. Anti-saturation gate: MUST collapse at reach>=2.
2. `GLOBAL_SEMANTIC`    : reference (reported, NOT gated). Z_sem, per-hop top-1 snap over the FULL codebook
                          (v2 continuity). The global-count-tax baseline.
3. `LOCAL_SEMANTIC`     : BASELINE floor (= v2 LOCAL_CLEANUP). Z_sem, per-hop top-1 snap restricted to graph
                          neighbors. identity_fraction alpha_id=0.0. Expect reach2~0.12, aliasing~0.815.
4. `LOCAL_PARTIAL`      : dose midpoint. Z_partial (features = normalize(0.5*sem + 0.5*identity)), LOCAL snap.
                          alpha_id=0.5. Dose-response probe.
5. `LOCAL_DECOUPLED`    : THE WIN LEVER. Z_id (features = near-orthogonal random identity), LOCAL snap.
                          alpha_id=1.0.
6. `LOCAL_DECOUPLED_DG` : strongest identity form. Z_id + DG sparse-expansion (k-WTA) re-separation at scoring
                          (pattern-separate the query+candidates in a fixed-random high-dim sparse sketch space).

WIN_ARMS (HP_SCOPE -- WIN gate applies ONLY to these): `{LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG}`.
DOSE arms (aliasing monotonicity / necessity-under-ablation): `[LOCAL_SEMANTIC(0.0), LOCAL_PARTIAL(0.5),
LOCAL_DECOUPLED(1.0)]`.
CLEAN-CODE POSITIVE CONTROL (the CEILING): the mechanism self-test's planted separable codes give LOCAL=1.0 --
the decoupled arm should approach this to the extent the real graph lacks genuine same-relation ambiguity.

## Metric

`reach@d` = TOP-1 COMMIT accuracy at hop d (committed node == true target). Honest chaining metric (chain carries
exactly ONE node forward). `local_aliasing_frac` per LOCAL arm = among hop-2 LOCAL errors (hop-1 conditioned
correct), fraction whose wrongly-picked neighbor is a SAME-RELATION sibling of the true edge. `same_rel_base_rate`
= graph-structural fraction of the midpoint's neighbors sharing the true relation (arm-invariant). `excess` =
aliasing_frac - base_rate (the code-induced confusability BEYOND chance). hit@10 = SECONDARY diagnostic (NOT
gated). MECHANISM CHECK: does decoupling reduce `excess` toward 0 (collision cracked)?

## Capability-test framing (3-part criterion -- REAL capability test, not construction-proof)

1. **DIFFERENT CHANNEL:** the decoupled codes must help the DOWNSTREAM multi-hop task (reach2/reach3 top-1
   commit propagated through the chain), not just a static probe.
2. **LIVE ALTERNATIVE:** the baseline (LOCAL_SEMANTIC) genuinely fails (reach2~0.12
   MEASURED@data/exp_grounding_multihop_local_chain_index_v2/metrics.json:gates.reach_mean.LOCAL_CLEANUP), so a
   pass is not rigged.
3. **NECESSITY UNDER ABLATION (dose-response):** identity_fraction alpha_id in {0.0, 0.5, 1.0} across
   {LOCAL_SEMANTIC, LOCAL_PARTIAL, LOCAL_DECOUPLED}. If identity decoupling is the lever, aliasing `excess`
   drops monotonically as alpha_id rises (identity codes are USED, not merely present).

## Pre-registered WIN bands (picked BEFORE the run)

- `HOP1_PRESENT = 0.08` -- GLOBAL_SEMANTIC@1 must clear (single-hop machinery works; >> chance ~0.0002).
  HYPOTHESIZED@this prereg (v2 MEASURED GLOBAL@1=0.088).
- `BASE_IN_BAND_HI = 0.95` -- LOCAL_SEMANTIC@1 must be < this (baseline in measurable band; v2 MEASURED 0.453).
- `BASE_COLLAPSE_ABS = 0.10`, `BASE_COLLAPSE_FRAC = 0.50` -- anti-saturation: NO_CLEANUP@2 <= 0.10 abs AND
  <= 0.5x NO_CLEANUP@1 (must-fail control loses >= half its reach). v2 MEASURED NO_CLEANUP@2=0.011.
- `WIN_REACH2 = 0.60` -- WIN: best WIN_ARM reach-2 top-1 commit >= this.
- `WIN_REACH3 = 0.35` -- WIN: best WIN_ARM reach-3 top-1 commit >= this.
- `ALIAS_DROP_MIN = 0.10` -- MECHANISM: LOCAL_DECOUPLED aliasing `excess` must be >= this much BELOW
  LOCAL_SEMANTIC `excess` (collision materially cracked toward base rate).
- `FAIL_REACH2 = 0.15` -- HARD_FAIL floor.

**Verdict logic:**
- `HARD_PASS_DECOUPLED_WIN` = a WIN_ARM has reach2 >= WIN_REACH2 AND reach3 >= WIN_REACH3 AND aliasing reduced
  (excess_semantic - excess_decoupled >= ALIAS_DROP_MIN). Collision cracked at modest dim.
- `HARD_FAIL_IDENTITY_NOT_LEVER` = aliasing NOT reduced (excess_semantic - excess_decoupled < ALIAS_DROP_MIN)
  AND best WIN_ARM reach2 < FAIL_REACH2. Identity separation is not the lever; residual is a genuine floor.
- `MIDDLE_BAND_PARTIAL` = partial crossing (aliasing drops but reach short of WIN, OR reach lifts but misses a
  band). Reported with dose-response curve.
- Guards: `INCONCLUSIVE_HOP1_ABSENT` if GLOBAL@1 < HOP1_PRESENT; `INCONCLUSIVE_BASELINE_DID_NOT_FAIL` if
  NO_CLEANUP does not collapse.

## DISCRIMINATOR-SURVIVES-SCALE

The aliasing discriminator is GRAPH-STRUCTURAL (local neighborhood, mean_out_degree ~ 6.65 regardless of total
n_nodes) so it is scale-independent. It FIRES AT SMOKE on the real subgraph: (i) NO_CLEANUP collapses at reach>=2;
(ii) LOCAL_SEMANTIC aliasing excess is high (~0.32); (iii) the KEY mechanism gap -- LOCAL_DECOUPLED excess <
LOCAL_SEMANTIC excess -- must show DIRECTIONALLY at smoke (n_nodes=1800). If the DECOUPLED-reduces-aliasing gap
does not fire at smoke, STOP and re-spec (the mechanism is not working). Smoke uses the SAME 6 arms / same code
path as FULL; only n_nodes/dim/epochs/seeds/n_chains scale.

## SCHEMA-VET fields

- `arms_differ_verified: true` (smoke gate; WIN arms use Z_id != Z_sem => distinct per-chain commit signatures;
  asserted LOCAL_DECOUPLED sig != LOCAL_SEMANTIC sig != NO_CLEANUP sig).
- `arms_differ_exempted: []`
- `final_metrics_atomicity: "tmp_replace"` (via _seed_checkpoint.write_metrics + os.replace).
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 6 arms x all 4 depths
  (arm/depth cardinality check).
- `crlb_floor_computed`: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000). `crlb_formula_reference`:
  "top-1 chance = 1/n_nodes; LOCAL load = mean_out_deg/dim = 6.65/2048 = 0.0032 << resonator thresh 0.056 so
  the LOCAL count-tax is NOT the binding constraint at this dim -- the residual is code correlation, measured as
  aliasing excess (not a closed-form floor)". `discriminator_reachability: true` (WIN reach2>=0.60 >> chance;
  reachable IFF same-relation ambiguity is code-induced-excess, which is the falsifiable question). `crlb_n/a`
  for the semantic-floor branch (measured aliasing, not a closed-form estimator floor).
- `baseline_in_band: true` -- LOCAL_SEMANTIC@1 in (0.05, 0.95) (v2 MEASURED 0.453); NO_CLEANUP@2 collapses.
- `calibration_check: "adaptive_with_discriminator_gate"` -- baseline-collapse + baseline-in-band + aliasing
  base_rate recomputed empirically per run; paired per-chain top-1 commits so all deltas are paired.
- `HP_SCOPE: {LOCAL_DECOUPLED: [WIN_REACH2, WIN_REACH3, ALIAS_DROP], LOCAL_DECOUPLED_DG: [WIN_REACH2, WIN_REACH3,
  ALIAS_DROP]}` -- WIN gate applies to WIN_ARMS only. NO_CLEANUP = must-fail control; GLOBAL_SEMANTIC/
  LOCAL_SEMANTIC/LOCAL_PARTIAL = reference/dose arms (reported, not WIN-gated).
- PAIRED trials: all arms share identical chains + roles + seeds + graph + dim.
- `cell_chunked: false` (multi-seed loop within one cell with per-seed write_partial + failure-class
  instrumentation; seeds=2 smoke / 3 full, cheap, GPU).
- `start_marker_written: true`; `crash_diagnostic_present: true`; `heartbeat_present: true` (per-epoch emit);
  `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"` (line-buffered stdout + per-epoch/per-seed flush prints + heartbeat).

### Section 15 gates
- `sweep_alignment_verdict: ALIGNED` -- swept axis = identity_fraction alpha_id in {0.0, 0.5, 1.0}. Effective
  parameter each encoder experiences = the actual input-feature correlation structure (semantic vs orthogonal);
  aligned with nominal alpha_id (no partition routing / no effective-vs-nominal divergence).
- `discriminating_fraction`: the WIN_ARMS reach2 is the discriminator; baseline in [0.10,0.20] (LIVE fail),
  clean-code ceiling 1.0, so the discriminating band is wide open. Dose arms span 0.0->1.0 identity fraction.
  Predicted >= 0.33 of arms in a discriminating band. ALIGNED.
- `composition_edges`: char_trigram/identity features -> ProjHead encoder (SHAPE_MATCH, feat_dim in / code_dim
  out, identical to v2) -> HRR bind (SHAPE_MATCH, code_dim) -> LOCAL cleanup (SHAPE_MATCH). No SHAPE_MISMATCH.
- `positive_control_arms`: LOCAL_SEMANTIC reproduces v2 LOCAL_CLEANUP AT THE SAME REGIME (n=5000, code_dim=2048,
  epochs=140, char-trigram features) -- cited prior reach2=0.121
  MEASURED@data/exp_grounding_multihop_local_chain_index_v2/metrics.json:gates.reach_mean.LOCAL_CLEANUP.2;
  tolerance 0.05. If LOCAL_SEMANTIC reach2 deviates > 0.05 from 0.121, the harness diverged from v2 -> suspect.
- `functional_requirements`: (1) chain must carry one node/hop -> top-1 commit metric; (2) disambiguate same-
  relation siblings -> near-orthogonal identity codes (new mechanism, decouples identity from surface semantics);
  (3) restrict per-hop candidates -> LOCAL neighborhood scoping (reused from v2, VET-confirmed working).

## Honesty

REAL CG'd teacher-free relational learned codes over the REAL ConceptNet typed subgraph; top-1 commit fidelity;
NO language understanding claimed. Identity features are random near-orthogonal per-node vectors (no word
content) -- a legitimate representational choice (pattern-separation analog), NOT oracle-cheating: the encoder
must still LEARN to bind (role_r, code[u]) -> code[v] over the real edges; wrong commits propagate to wrong
candidate sets. The LOCAL candidate restriction is legitimate for KG traversal (adjacency known at each step).
ASCII-only, device-aware torch. Reuses Stage-4/5 VET-landed encoder/chain/LOCAL-scoping primitives VERBATIM
(calibration continuity + no drift).

## Prior-work check

`bash tools/substrate_query.sh "decoupled near-orthogonal identity codes pattern separation same-relation
aliasing multi-hop chain"` -> top hit cosine=0.3213 (framenet Duration_relation, irrelevant); rank-3 chunk
(cosine=0.3115) = `research_drill_2x_orthogonal_role_basis_failure_revival_or_close_2026-06-27.md` (brain
DEVELOPS orthogonality through experience, does not init-orthogonal -- relevant framing, informs that identity
decoupling is a learned outcome, not free). NONE at cosine>0.35. This v3 cell is genuinely novel (no prior arc
cell tested identity-feature decoupling for same-relation aliasing); it is the VET-corrected continuation of v2's
HARD_FAIL_SEMANTIC_FLOOR, attacking the representation rather than the scoring.
