# Research: additive map-builder integration ENDGAME (nativize-the-winner)

Date: 2026-07-13. Director design drill (code read + design only; NO build, NO experiments run).
Supersedes the "fork-open" framing of `notes/research_anchor_compose_live_store_integration_path_2026-07-13.md`:
that note staged a Stage-0 decisive test to pick between the cheap native-bind path (0a) and the costlier
adjunct-additive path (0b). **Today the fork has RESOLVED** (VET-confirmed FULL results below) toward the
adjunct-additive path. This note designs that endgame concretely.

## What the VET-confirmed FULL results settled (all `run_mode=full`, off-disk verified)

| cell | verdict | held-out MRR | ceiling H (ORACLE-RANDOM) | reading |
|---|---|---|---|---|
| `exp_anchor_compose_inductive_entity_cskg_v1` (ADDITIVE k=24) | HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE | **0.1282** | 0.1368 (ratio 284x) | the winner; CHAIN_GRADE inductive |
| `exp_native_bind_compose_inductive_entity_cskg_v1` (MULTIPLICATIVE n_dim=1024) | HARD_PASS_NATIVE_BIND_INDUCTIVE | **0.0140** | 0.0226 (ratio 51x) | passes its OWN relative bar but ~9.2x weaker absolute; its capacity ceiling is itself ~6x below additive's |
| `exp_kg_store_dim_scaling_ceiling_v1` | HARD_PASS_DIMENSION_RELIEVES_CEILING | ORACLE 0.023->0.78 @ n_dim 1024->8192; NATIVE compose 0.014->**0.0518** | - | dimension lifts the CAPACITY ceiling but native COMPOSE readout still STALLS at 0.052; residual wall = codes/compose, not capacity; and it costs O(n_dim^2) |
| `exp_kg_store_write_rule_decorrelated_ceiling_v1` | HARD_FAIL_WRITE_RULE_NOT_THE_LEVER | hebb 0.0140 ~= pinv 0.0156 | - | write rule is CLOSED / not the lever |

**Conclusion (the premise of this endgame):** the multiplicative store does held-out-entity induction only
IN-KIND and much weaker; dimension relieves capacity but not the codes/compose wall (and is O(n_dim^2)); the write
rule is not the lever. So the nativize path is NOT to force the multiplicative store to match -- it is to give the
substrate an **ADDITIVE-MODE** capability as a first-class live adjunct. The winning mechanism's advantage lives in
its **gradient-derived low-dim coordinates** (structure-derived positions, not random labels) + **direct-distance
readout** + **zero-training degree-invariant compose bundle**.

## 1. INTEGRATION PATH -- additive map-builder as a live substrate capability

### What ALREADY exists (proven, in `experiments/`, disposable-process only)
- `experiments/_kge_anchor1_fit.py::fit_kge_anchor1(train_edges, N, n_rel, k, device, seed, epochs, ...)`
  -> fits `X` [N,k], `D` [n_rel,k] via Adam SGD (k=24, 500 epochs, self-adversarial CE + N3 + reciprocal). THE
  map-builder. Already has `transductive_extra` (fold-in), `return_inverse`, checkpoint hooks, hard-neg lever.
- `experiments/_course_c_rotate_core_v1.py::additive_direct_scores(X, D, hold_edges, device, chunk)`
  -> `score(t) = -||X_h + D_r - X_t||`, query-chunked. THE direct-distance `score_all`. Format-agnostic (plain
  tensors), no Hebbian matrix in the path.
- `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py::build_anchor_compose_codes(X, D, support_int, ...)`
  -> `E_derived[t] = mean_i(X[h_i] + D[r_i])` (index_add + count-normalize). THE zero-training, degree-invariant
  `compose_entity`. The ONLY genuinely novel op with no analog in `KGStore`.

**Key structural advantage over the multiplicative store:** additive `X` is a plain `[N,k]` coordinate table, so
`insert_entity` is a trivial `torch.cat` of one row -- the "E is fixed-size, no append/grow" gap that blocks the
multiplicative KGStore does NOT exist in additive space. The winning geometry is also the *easier* one to grow.

### What must be BUILT to make it LIVE
1. **Promote to a maintained `hdlab` module** -- new `hdlab/additive_map.py` with an `AdditiveKGMap` class wrapping
   the three proven functions verbatim (no re-implementation; import/move from `experiments/`). Owns `X`, `D`,
   `entity_to_idx`, `relation_to_idx`.
2. **Persistence** (today: none; the whole win is trapped in a disposable Python process). `X`/`D` are just two
   float tensors + two dict maps -> `save(path)` / `load(path)` via `torch.save` or `safetensors<2.6` (per infra
   rule) + JSON index maps. This is the single most load-bearing missing piece for "live".
3. **Query-time API** (the surface the task named):
   - `compose_entity(support_edges) -> code`  (wrap `build_anchor_compose_codes` for a single novel entity)
   - `insert_entity(code) -> new_idx`         (append a row to `X`; trivial in additive space)
   - `score_all(head_idx, rel_idx) -> [N]`    (wrap `additive_direct_scores` for one query)
4. **Ingest / fit hook** -- `fit(train_edges)` at build/consolidation time; `compose_entity` + `insert_entity` for
   novel entities at query time (fast path, no SGD). Two-timescale by construction: slow SGD fit, fast compose.
5. **Live-wired fairness re-run** -- re-run the composer's OWN pre-registered fairness apparatus (ORACLE-must-fire,
   RANDOM/SCRAMBLE must-fail, degree tertiles, POP) against the `hdlab`-wired version to confirm it reproduces the
   offline 0.1282 (guards the representational-mismatch hazard flagged in the prior note). This is the acceptance
   gate, not a formality.

### Stage minimal-viable -> full
- **MVP (minimal-viable):** items 1-3 + 5. `AdditiveKGMap` class + persistence + compose/insert/score API + a
  live-wired fairness re-run reproducing 0.1282. Most of the MECHANISM already exists and is VET-confirmed at FULL;
  the MVP is packaging + persistence + append-grow (trivial) + API + a confirmation re-run. Read-only w.r.t.
  `KGStore` (zero regression surface). Cost: moderate-small, engineering-only (no new mechanism research).
- **Full (later, staged):** item 4 ingest hook + consolidation cadence (periodic re-fit / schema-gated fold-in,
  the CLS "systems consolidation" analog) + Stage-1 fold into `predict_n_hop` multi-hop (this touches the
  CERT-584/585 hot path -- deferred, higher risk, re-validate 36.49x) + staleness/versioning.

## 2. THE GLASS-BOX JUDGMENT (surface for USER -- I do NOT decide this)

**The fork:** is a LEARNED k=24 additive-TransE construction an acceptable "native / glass-box" substrate
capability, or does it violate the glass-box guardrail?

**Arguments FOR glass-box-acceptable:**
- k=24 is tiny + directly interpretable: 24 geometric coordinates per entity; relations are displacement VECTORS
  (directions in the same space); inference is vector addition + subtraction (the brain-aligned "relations =
  directions" code the relational-capability thread is built around).
- Readout is CLOSED-FORM Euclidean distance -- no learned aggregator, no attention, no deep net, no per-query
  parameters. Every score decomposes into inspectable per-coordinate contributions.
- The compose op is a plain arithmetic MEAN of per-edge estimates -- fully transparent, zero training on the novel
  entity. Arguably MORE glass-box than the multiplicative store's opaque 1024x1024 Hebbian `W`.

**Arguments AGAINST (the guardrail concern):**
- `X`, `D` are produced by gradient descent (Adam, 500 epochs, self-adversarial CE loss). The coordinates
  THEMSELVES are opaque learned parameters -- not derived by a transparent rule from entity content. The winner's
  entire advantage over the fixed-atom store came precisely from these gradient-derived positions.
- The guardrail was written against arbitrary learned aggregators / deep nets. This is neither -- but it IS
  gradient training producing the representation, which the fixed-atom multiplicative substrate deliberately avoids.

**The crux question I'm putting to USER (binary, load-bearing):** does "glass-box" mean
- **(strict) "no gradient training anywhere in the representation"** -> additive-mode FAILS the guardrail; the
  substrate must either accept the ~9.2x-weaker fixed-atom native capability, OR fund open research into a
  RULE-DERIVED (non-SGD) route to structure-derived coordinates (e.g. spectral/Laplacian graph embedding,
  closed-form factorization of the adjacency, Hebbian-derived low-rank -- none proven here, a real research bet); OR
- **(functional) "operative mechanisms are simple, low-dim, closed-form, and inspectable"** -> additive-mode PASSES
  (transparent structure + transparent readout + transparent compose; only the coordinate-fitting is gradient-based,
  and it is a one-time offline step, not a per-query black box).

I recommend framing it to USER as: *the winning mechanism is glass-box in STRUCTURE, READOUT, and COMPOSE, but
LEARNED (not rule-derived) in its COORDINATES.* The ruling is whether learned-coordinates-with-transparent-everything-
else clears the bar. This is genuinely USER's call and gates whether the MVP ships or a rule-derived-coordinate
research arc opens first.

## 3. Where this leaves the multiplicative store: COEXIST (not replace)

**Recommendation: COEXISTING SECOND MODE, not a replacement.** The multiplicative `KGStore` keeps its own role.
- **Distinct proven roles.** Additive-mode is proven ONLY for single-hop held-out-ENTITY induction. The
  multiplicative store owns CERT-584/585 **chain-grade multi-hop** (36.49x over frozen-encoder, refuse-OOD 0.999) --
  a capability the additive-mode has NOT been tested for. Replacing would trade a proven capability on one axis for
  an unproven one on another.
- **Brain analog (load-bearing, not decorative).** Complementary Learning Systems (McClelland/McNaughton/O'Reilly
  1995; Kumaran/Hassabis/McClelland 2016): fast/sparse hippocampal-like and slow/distributed cortical-like memory
  systems COEXIST as complementary duals, not merged into one representation. Multiplicative one-shot Hebbian bind =
  hippocampal-like fast write (immediate serving); additive structured low-dim geometry = cortical-schema-like slow
  structured induction. Different jobs, both real. Multiple memory systems is the biological norm.
- **Non-regression.** Adjunct = ZERO code touched in `KGStore.E/R/W`, `key`, `score_all`, `predict_*` -> zero
  regression risk to the proven 36.49x. A router dispatches by query class (novel-entity single-hop induction ->
  additive-mode; multi-hop chain over known entities -> multiplicative store).
- **Two-timescale design.** Fast native Hebbian write for immediate query-time serving + slow periodic additive
  re-fit for structured induction -- the hippocampus/neocortex consolidation pattern, mapped onto the two modes.

So: multiplicative store REPLACES nothing (keeps multi-hop); additive-mode is a NEW coexisting mode for
held-out-entity single-hop induction; a mode-router chooses.

## 4. Risks + cost + P_deflated

**Risks:**
- (R1) **Representational-mismatch / non-reproduction** -- the live-wired `hdlab` version fails to reproduce the
  offline 0.1282 (silent wrong-dimensionality numbers were the sharpest hazard flagged in the prior note). Mitigated
  by the mandatory live-wired fairness re-run (item 5) as the acceptance gate.
- (R2) **Glass-box rejection** -- USER rules the strict reading; the whole MVP path is gated off and a rule-derived-
  coordinate research arc must open first. This is the dominant strategic risk, and it is not mine to resolve.
- (R3) **Consolidation/re-fit staleness** (Full stage only) -- when novel composed entities accumulate, the fitted
  `X`/`D` drift; needs a re-fit cadence + versioning. Deferred to Full.
- (R4) **Stage-1 multi-hop regression** (Full stage only) -- folding composed codes into `predict_n_hop` touches the
  CERT-584/585 hot path. Deferred; keep MVP read-only w.r.t. `KGStore`.

**Cost:** MVP = moderate-small, engineering-only (promote 3 proven functions + persistence + trivial append-grow +
API surface + one confirmation re-run). No new mechanism research on the MVP path. Full = larger (consolidation
cadence, versioning, multi-hop re-validation), staged after MVP lands + VET.

**P_deflated:** for "MVP additive-mode ships as a working, non-regressive live single-hop induction capability that
reproduces the offline win," CONDITIONAL on USER ruling glass-box acceptable (R2): the mechanism is already
VET-confirmed at FULL and the remaining work is low-uncertainty engineering, but the live-wire reproduction hazard
(R1) is real -> raw ~0.70, deflated for novel-integration + reproduction hazard -> **P_deflated ~= 0.55**. The
glass-box ruling (R2) is a SEPARATE binary gate held by USER, not folded into this P; if USER takes the strict
reading, the MVP-as-designed P drops toward 0 and the effort redirects to a rule-derived-coordinate research arc
(a genuine, lower-P research bet, no precedent proven on this substrate).

## Cross-thread connections
Continues `notes/research_anchor_compose_live_store_integration_path_2026-07-13.md` (fork now resolved). Rests on
VET-confirmed FULL cells (additive HARD_PASS 0.1282; native 0.0140; dim-scaling; write-rule HARD_FAIL). Direct
engineering continuation of the "relational-capability-is-the-core-requirement" program spine (additive/geometric
codes = degree-invariant, relations-as-directions, brain-aligned). CLS coexistence argument grounds the
replace-vs-coexist call in the multiple-memory-systems brain analog.
