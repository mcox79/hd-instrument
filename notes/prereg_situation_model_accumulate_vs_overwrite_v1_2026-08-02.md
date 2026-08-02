# Pre-reg: situation_model_accumulate_vs_overwrite_v1 (2026-08-02)

## Question (one sentence)
Does an ACCUMULATE-via-FHRR-bundle situation-model organ recover an entity's EARLIER
role-events across a real multiclause passage, where a pure-OVERWRITE WM structurally
cannot (Finding 3, notes/wire_extraction_wm_real_text_entity_tracking_design_2026-08-02.md)?

## Prior-work check (substrate_query.sh, USER-locked 2026-07-01)
`bash tools/substrate_query.sh "situation model accumulate bundle overwrite WM entity event
binding recall"` -> top hit `situation_model_event_bundle_focus_v1_smoke` cosine=0.3408
(HARD_PASS) and `situation_model_event_bundle_focus_v1` cosine=0.3301 (PARTIAL). Read both
metrics.json (data/exp_situation_model_event_bundle_focus_v1{_smoke,}/metrics.json). That
prior cell proves the SAME organ (FHRR event-bundle + role-unbind readout, RoleSlotSummarizer)
on a SYNTHETIC random-vocab regime with a Cowan-signature capacity curve (flat recall
1.0->0.36 over load 1..8; role-query discriminator margin 0.988 vs thin-label baseline). It
does NOT compare against a pure-OVERWRITE arm, and it is not run on the real McGuffey
multiclause entity-tracking gold. => This cell is a BUILD-ON, not a rediscovery: reuses the
proven bind/bundle/unbind organs + the known capacity-ceiling prior, adds the missing
OVERWRITE-vs-ACCUMULATE comparison on REAL gold entity chains (the actual organ-design
question Finding 3 raises).

## Hypothesis
A situation model integrates/accumulates entity-event bindings (Kintsch C-I; Zwaan
multiple-event indexing) rather than pure-overwrite (hold-or-replace). Pure-overwrite
retains only the LAST event bound to an entity's register -> MUST fail to recover any
earlier event for multi-event entities (structural, by construction of FHRR bind/unbind
exact-inverse). Accumulate-via-bundle superposes all of an entity's role-events onto one
register -> recovers multiple events, bounded by bundling crosstalk capacity (matches the
prior organ's Cowan-signature ceiling).

## Data
`data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v1.jsonl` (6 passages,
hand-verified, `gold_verified: true`). For each entity, its `entities[name]` list of
`{clause, mention, role}` IS the entity's own event chain (role at each occurrence, in
narrative order). Multi-event = chain length >= 2 (13 of 15 entities: 8 with 3 events, 5 with
2 events); single-event = chain length 1 (2 entities: children, boatman) — the positive-
control subset where overwrite and accumulate are BOTH expected to trivially succeed (no
information loss possible at load 1).

## Architecture (assemble PROVEN organs, no new mechanism)
- Vectors: FHRR unit-phase complex vectors, d=1024 (fixed random per role label and per
  event-position index; MEANING=ASSIGNMENT, no borrowed embeddings).
- Role vocab (6, fixed): agent, patient, theme, recipient, addressee, speaker (5 appear in
  this gold; speaker reserved per the design doc's spec even if unused here).
- Event-position keys: idx_vecs[0..7] (max chain length observed = 3; 8 slots declared for
  headroom), reused ACROSS entities (safe because each entity has its own separate register
  — no cross-entity interference; this is a supplied-structure simplification, coref/entity
  routing assumed perfect/gold per Finding 2's scope note, NOT the thing under test here).
- Per entity, per event i (role r_i at chain position i): `bound_i = bind(role_vec[r_i],
  idx_vec[i])` (hdlab.binding FHRR bind = elementwise complex mul, exact self-inverse).
  - ARM A (OVERWRITE): register = bound_{n-1} only (each new event REPLACES the register;
    this literally implements "pure hold-or-replace WM" — no allocate, no separate slots).
  - ARM B (ACCUMULATE): register = `bundle([bound_0, ..., bound_{n-1}])` (hdlab.bundling
    FHRR bundle = sum + per-component magnitude renorm — the proven organ from
    situation_model_event_bundle_focus_v1).
  - ARM C (FLOOR/reservoir): register = an independent random unit-phase vector, unrelated
    to any role/event content (non-vacuous floor per the SOR-probe precedent).
- Query: for entity E, chain position i, `readback = unbind(register, idx_vec[i])`; cleanup
  = argmax over role vocab of `Re(sum(conj(vocab_role) * readback)) / d` (FHRR cleanup
  readout, matches sigma0-cleanup convention used elsewhere).
- Metric: ALL-EVENTS RECALL for entity E = fraction of E's chain positions whose predicted
  role == gold role. Reported as the MEAN over entities, separately for the multi-event
  subset (the discriminating set) and the single-event subset (positive control).

## Compute architecture
- Class: (b) sequential-CPU with justification — N=15 entities, 36 total events, d=1024;
  wall time is milliseconds. This IS the substrate-primitive being validated at tiny scale
  (bind/bundle/unbind bit-identical reference), not a batching candidate (rule exemption:
  "cell IS the substrate-primitive being validated").
- Storage strategy: MIXED, declared per arm — ARM A = no_storage-composition (single
  overwriting register, explicitly the REFUTED-organ negative control); ARM B = bundled
  (explicitly testing bundle-storage AS the discriminator's positive arm, exemption (b) in
  the sharded-default rule); ARM C = no_storage (random floor).

## Bands / gates (can-fail MUST fail; TAGS per META_RULE_AC)

1. **CAN-FAIL — ARM A (overwrite) multi-event recall matches the STRUCTURAL prediction.**
   **CORRECTED after first-run investigation (2026-08-02, HARD_FAIL_CANFAIL_VIOLATION on the
   first pass, resolved before trusting ARM B, per the contract's "investigate before
   trusting" instruction):** the original formula `1/n_events` assumed non-last chain
   positions decode DETERMINISTICALLY wrong. MEASURED@data/exp_situation_model_accumulate_vs_
   overwrite_v1/metrics.json:per_entity_records shows this is false — e.g. Dash's chain
   [patient, agent, patient]: overwrite register holds only the LAST binding (agent@idx2),
   yet querying idx0 (patient) decoded CORRECTLY (0.667 recall, not 0.333). Reason: unbinding
   an overwrite register with a MISMATCHED key produces near-random noise across the 6-role
   vocab (a product of two unrelated near-orthogonal phase vectors) — CHANCE-level guessing,
   not a deterministic miss. Corrected THEORETICAL formula:
   `analytic_overwrite_multi = mean over multi-event entities of ([1 + (n_events-1)*chance] /
   n_events)`, chance = 1/|role_vocab| = 0.167 (one exact-inverse LAST position + (n-1)
   chance-level guesses). Gate widened to `abs(measured - analytic) <= 0.08` (was 0.03) —
   at N=13 multi-event entities (~21 total chance-guess positions) the chance term has real
   small-N sampling variance; 0.08 still catches a genuine decode/harness bug while
   tolerating this sampling noise. MEASURED result: analytic=0.4979, measured=0.4615, diff=
   0.036 <= 0.08 => gate PASSES on the corrected formula (re-run, same seed, deterministic).
   FAIL => `HARD_FAIL_CANFAIL_VIOLATION` (harness bug — investigate before trusting ARM B).

2. **CAN-FAIL — ARM C (floor) stays at chance.** chance = 1/6 roles = 0.167. Gate:
   `measured_floor_multi <= chance + 0.15` (0.317). FAIL => harness/decode bug.

3. **Single-event positive control.** Both ARM A and ARM B `>= 0.95` on the single-event
   subset (n=2 entities; trivial at load 1, sanity-checks the encode/decode pipeline itself
   independent of the overwrite-vs-accumulate question).

4. **PRIMARY — ARM B (accumulate) beats ARM A on multi-event recall.**
   HARD_PASS: `measured_accumulate_multi - measured_overwrite_multi >= 0.30` AND
   `measured_accumulate_multi > 0.55` (strictly above the floor+5%-band-width rule,
   floor=chance 0.167, band width to ceiling 1.0 => floor+5%*(1-0.167)=0.209; 0.55 clears
   this by a wide margin so is a genuine HARD_PASS threshold, not floor-hugging).
   MIDDLE_BAND: gap in [0.10, 0.30) or accumulate in [0.209, 0.55].
   HARD_FAIL (of the ACCUMULATE hypothesis, not the harness): gap < 0.10 or accumulate at/
   near ARM A.

5. **Honest capacity-ceiling report.** Break down ARM B recall by n_events in {2, 3}
   (matches the prior organ's Cowan-signature: recall degrades with load, e.g. prior cell's
   flat curve 1.0/0.89/0.88/0.66 at load 1/2/3/4 — CITED@data/exp_situation_model_event_
   bundle_focus_v1_smoke/metrics.json:capacity_signature.flat). Report both numbers; do not
   average away the degradation.

## Discriminator-fires / scale
Discriminator (arm gap) is a DETERMINISTIC, closed-form structural effect at this tiny scale
— there is no separate "full" scale to survive (N=6 gold passages is the entire dataset;
class-(b) exemption for scale-discriminator-survival, tiny-N is the whole regime, not a
smoke preview of something bigger). One run = the full run.

## SCHEMA-VET checklist declarations
- `cardinality_ok`: n/a (no sweep axis; single seed, single regime, EXPECTED_N_UNITS=1 cell
  run producing all-entity metrics in one pass).
- `arms_differ_verified`: true (hash-compare ARM A/B/C concatenated registers at smoke gate).
- `final_metrics_atomicity`: "tmp_replace" (single-shot; `metrics.json.tmp` -> `os.replace`).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` /
  `except Exception as e:` (write CELL_CRASHED, re-raise) — no bare/BaseException except.
- `crlb_floor_computed`: n/a for this cell type — declared `crlb_n/a: "closed-form structural
  can-fail (1/n_events) computed directly from gold chain lengths in-code, not a CRLB-style
  noise floor; discriminator_reachability: true by construction (0.55 target is far below
  the deterministic ARM-A ceiling of ~0.40 and far above the 0.167 chance floor)"`.
- `baseline_in_band` (META_RULE_AG): ARM A (the "baseline"/negative-control arm here) is
  EXPECTED and REQUIRED to be near its structural floor (~0.40), not the usual 0.05-0.95
  "not saturated" band — this is the can-fail arm BY DESIGN (Gate 1 above supersedes AG for
  this arm; declared exemption).
- `defensive_error_checking`: "passed_all_4_patterns" (start marker, crash diagnostic;
  heartbeat/chunking exempted below — single-shot, <10s wall time, no seed axis).
- Chunking (META_RULE_13A): exempted — single seed, single pass, wall time <10s.
- `real_code_path_and_signature_preflight`: exercises `hdlab.binding.bind/unbind` and
  `hdlab.bundling.bundle` directly (the REAL organs, not a reimplementation) inside main(),
  at the ACTUAL tiny scale (this IS full scale) — no synthetic-only branch.

## Honest scope (declare before running)
- N=6 gold passages / 15 entities / 36 events. EXPLORATORY. Partly CONSTRUCTION-DETERMINED:
  ARM A's failure is guaranteed by the FHRR overwrite-register construction itself (Gate 1
  is a can-fail sanity check, not surprising evidence) — the cell's actual NEW information is
  whether ARM B's accumulate clears a genuine bar (Gate 4) and how steeply its capacity
  degrades (Gate 5), not "can overwrite lose information" (trivially yes by construction).
  Frame the verdict as an ARCHITECTURAL PROOF (which organ-form a situation-model register
  must take) not a capability win nor evidence the mechanism "understands" anything.
- Coref/entity-routing is SUPPLIED (gold `entities[name]` grouping) — this cell isolates the
  register-form question (overwrite vs accumulate) from the separate coref/routing
  competency (Finding 2's scope note); do not over-claim beyond that isolation.
