# Integration audit: BUILT vs WIRED vs USED (the working_memory failure class)

Author: hdi_testbed. Date: 2026-08-02/03 (registry snapshot audited at
`last_audit_utc: 2026-08-03T03:41:58Z`, 55 rows).

## Why this audit exists

USER worry: "we worked hard on things (e.g. the chain-grade multi-bank
`working_memory`) that aren't actually bundled/used in the substrate -- what
else did we build that isn't integrated?" `data/capability_registry.jsonl`'s
`integration_status` field is computed from `tools/integration_health.py`'s
**import graph over `experiments/` + `hdlab/`**. That graph answers "is this
module imported by *something*" -- it does NOT answer "is this module
imported by the **active reading/comprehension pipeline**." A module can be
`WIRED` (imported by some experiment cell, or even by another hdlab module)
and still be completely invisible to the thing that actually reads text
today. `hdlab/working_memory.py` is exactly this case, and it isn't alone.

## Method

Traced the real import closure from the five named active entry points:

- `tools/read_anne_glassbox_v2_honest_ledger.py` (imports `tools/read_anne_glassbox_v1.py` too)
- `hdlab/coreference_resolver.py`
- `hdlab/situation_model_accumulate.py`
- `hdlab/self_improving_loop.py`
- `hdlab/state_of_mind.py`

**Reachable hdlab set (verified by grep of every `import`/`from` line, one
level at a time, to fixed point): exactly 8 files** --
`coreference_resolver.py`, `state_of_mind.py`, `situation_model_accumulate.py`,
`self_improving_loop.py`, `binding.py`, `bundling.py`, `modulators.py`,
`tracing.py`. No `importlib`/dynamic imports found in any of the 5 entry
points (grepped `importlib|__import__`, zero hits), so this closure is exact,
not an approximation. `hdlab/` has ~100 files total -- so by raw count,
~92 hdlab modules are outside the active-pipeline closure. Most of those
serve *other* legitimately-active programs (ARC/cortex reasoning frontier,
KB ingest/query, cert/atom-store infra) that are not part of "the reading
pipeline" by design -- flagging all 92 as the working_memory failure class
would be noise, not signal. The classification below distinguishes
genuinely-worrying unused-comprehension-capability (B) from
used-by-a-different-active-track (not flagged) and legitimately-shelved (D).

Also notable and load-bearing for the read: **the current Anne-reader
pipeline uses NO neural encoder at all** -- `tools/read_anne_glassbox_v2_honest_ledger.py`
is pure regex/`difflib` mention extraction + symbolic coref + FHRR
accumulate register. Zero references to any Encoder/EncoderExtractor class.
That means the entire encoder-track capability cluster (TinyTransformer,
gated_fusion, learned_relational_readout, encoder_retrain_persist, char_trigram_encoder)
is -- for the *current* reading pipeline specifically -- categorically out of
scope right now, not because of an oversight but because the reader doesn't
read through an encoder at all yet.

## Counts

| Class | Count | Meaning |
|---|---|---|
| (A) WIRED + USED | 4 registry rows (+ shared primitives binding/bundling) | reachable from the 5 active entry points |
| (B) WIRED-but-UNUSED-by-reader (worrying class) | 3 registry rows + **1 unregistered module** (`working_memory.py`) | in hdlab, importable, but the active pipeline never calls it |
| (C) ISLAND-but-VALUABLE | 9 registry rows | VET-confirmed real, not reachable, should be promoted/wired |
| (D) LEGITIMATELY-SHELVED | ~24 registry rows | HARD_FAIL / deprecated / synthetic-superseded, correctly unwired |
| Other-active-track (WIRED+USED, but by ARC/cortex/KB, not the reader) | ~15 registry rows | not flagged -- genuinely serving a different live program |
| Registry-coverage gap | at least 2 modules found on disk, VET-referenced, absent from the registry entirely | `hdlab/working_memory.py` (chain-grade cert'd K=4096), `hdlab/animacy_lexicon.py` |

(55 registry rows total; counts above sum to 55 for the registry-native rows;
the coverage-gap row is *in addition to* the 55, found by disk-scan, not registry-listed.)

## (A) WIRED + USED -- good, confirmed by real import closure

- `situation_model_accumulate_register_organ` (`hdlab/situation_model_accumulate.py`) --
  `AccumulateRegister`, imported directly by both `read_anne_glassbox_v1.py`
  and `v2_honest_ledger.py`, and by `self_improving_loop.py`. VET math seq
  29609/29610.
- `coreference_resolver_match_or_allocate_strict_cb_principle_b`
  (`hdlab/coreference_resolver.py`) -- imported directly by
  `read_anne_glassbox_v2_honest_ledger.py`. Atoms 29613/29614/29616/29618.
- `self_improving_loop_coherence_gated_keep_revert_controller`
  (`hdlab/self_improving_loop.py`) -- imports `AccumulateRegister`; its own
  reachability from the Anne reader wasn't re-verified this pass (not
  directly imported by `read_anne_glassbox_v2_honest_ledger.py` per the grep
  -- it's a downstream consumer of the coref+accumulate organs, invoked from
  its own driver cell `exp_coref_autonomous_fix_router_v1.py`, not from the
  reader script itself). Flag: **this is a partial USED claim** -- the
  decision-layer module is wired-and-real but not yet called *from inside*
  the reader entry point; worth a follow-up check whether it's meant to be.
- `hdlab/state_of_mind.py`, `hdlab/binding.py`, `hdlab/bundling.py`,
  `hdlab/modulators.py`, `hdlab/tracing.py` -- reused verbatim by the above,
  confirmed reachable, not separately registry rows (they're substrate
  primitives, correctly treated as infra not standalone capabilities).

## (B) WIRED-but-UNUSED-by-the-reader -- the worrying class, working_memory's siblings

### 1. `hdlab/working_memory.py` -- **not even in the registry** (the sharpest finding)
- **What it does**: multi-bank working-memory primitive, K-item capacity via
  per-bank cleanup (content-anchored bank routing + bind/unbind/argmax
  cleanup per bank).
- **VET status**: chain-grade CERT'd in its own docstring -- "HARD_PASS
  chain-grade at K=4096 MULTI_64x per Skunkworks landed-VET; ledger row
  62ce9e7dca071828" (recall 0.9927 random, 0.9801 adversarial, both regimes).
  Real, measured, not a stub.
- **Why not used**: zero imports from any of the 8 reachable modules. Its
  only in-hdlab consumer is `hdlab/context_retention.py`, which is *itself*
  unreachable from the active pipeline (nothing in the reachable set imports
  `context_retention`). `hdlab/state_of_mind.py` line 56 *mentions* it in a
  docstring ("(3) hdlab.working_memory multi-bank (K-capacity chain-grade at
  K=4096, k_per_bank>=64)") as if it were part of the design, but no code in
  `state_of_mind.py` actually imports or calls it -- this is the textbook
  documented-but-not-wired pattern the task asked to hunt for.
- **Recommend**: WIRE, priority **HIGH**. This directly serves the current
  comprehension frontier (multi-entity working-memory capacity is exactly
  what a longer/denser passage needs once the coref+accumulate organs run
  out of naive-dict capacity) and MEMORY.md's own next-step list wants
  "RICHER/LONGER content" as the self-improving-loop's next lever --
  `working_memory.py`'s multi-bank capacity is a direct answer to the
  capacity wall that richer content will hit. Concretely: register it in
  `capability_registry.jsonl` (closing the coverage gap) and give it a real
  consumer -- either swap `AccumulateRegister`'s naive per-entity dict for
  bank-routed capacity when entity count is large, or wire it into
  `context_retention.py` and then wire `context_retention.py` itself into
  the reader (see item 2).

### 2. `hdlab/context_retention.py` -- unused, and it's the one file that *does* import working_memory
- **What it does**: appears to be a context-retention layer built on top of
  `hdlab.working_memory` + `hdlab.cleanup_family.k_NN_lookup`.
- **Why not used**: not imported by any of the 5 active entry points or
  their reachable closure. Not present in `capability_registry.jsonl` at
  all (second coverage gap).
- **Recommend**: WIRE-or-diagnose, priority **MEDIUM**. Worth a short look
  at whether this is the missing link between `working_memory.py` and the
  reader (i.e. wiring #1 might really mean wiring this file into the reader
  and letting it own the working_memory call).

### 3. `working_overlay_situation_reader` (registry row `working_overlay_situation_reader`) -- registry entry gone stale
- **Registry says**: `gate_decision: SHELVE`, bundling `hdlab/situation_focus.py`,
  `hdlab/state_of_mind.py`, `hdlab/bundle_focus_coref.py`, `hdlab/coref.py`,
  `hdlab/event_bundle.py` together as one "reader cluster," decided SHELVE
  2026-07-28 because it didn't fit ARC single-sentence comprehension.
- **The gap**: `hdlab/state_of_mind.py` was subsequently (2026-08-02)
  reused verbatim and promoted as a dependency of `coreference_resolver.py`,
  which **is** wired and used by the active reader. The registry row still
  lumps it in with the shelved cluster. This is not the working_memory
  failure mode (state_of_mind IS used) -- it's the opposite risk: a stale
  SHELVE decision on a *bundle* row can hide that one member of the bundle
  got individually promoted later. `situation_focus.py`, `bundle_focus_coref.py`,
  `coref.py`, `event_bundle.py` remain genuinely unused (correctly D), but
  `state_of_mind.py` should be split out of this row.
- **Recommend**: registry hygiene, priority **LOW** -- split the row so
  `state_of_mind.py`'s status isn't misreported as SHELVE when it's
  load-bearing infra for a WIRED capability.

## (C) ISLAND-but-VALUABLE -- VET-confirmed real, not wired, should be promoted

Ranked by relevance to the current comprehension frontier:

1. **`native_vsa_cross_slot_relational_binding`** (`experiments/exp_cross_slot_relational_binding_v1.py`,
   VET-confirmed, main-eval ~0.80-0.855, causally-attributed, generalizes to
   held-out role-swaps 0.73-0.77) -- native FHRR bind/unbind does cross-slot
   "who-did-what-to-whom" relational binding; a learned per-slot WM/linear
   readout architecturally CANNOT do this (bilinear vs linear). `gate_decision: WIRE`,
   never promoted to `hdlab/`. **Priority HIGH** -- this is a real
   candidate mechanism for the role-extraction half of "THE WALL" MEMORY.md
   names as the current blocker (extraction generalization on real text).

2. **`native_vsa_multirelation_composition_slotfilling`** (VET-scoped,
   `gate_decision: WIRE`) -- composes multiple superposed relation-instances
   + answers multi-query retrieval over structured slot-filling. Honest
   scope: not naturalistic yet, but names the exact 5 remaining gaps to get
   there (syntactic role parsing, competitive coref, overwrite, entity
   generalization, non-templated text) -- a real roadmap, currently an
   island. **Priority MEDIUM-HIGH.**

3. **`encoder_retrain_persist_generalizing_lever_reusable_v1`**
   (`hdlab/encoder_retrain_persist.py`) -- registry says `WIRED` (has a
   verify-consumer), but that consumer is a synthetic smoke test, not a
   production caller, and the active reader uses no encoder at all right
   now (see Method section). Effectively an island relative to the reader.
   **Priority MEDIUM** -- only matters once/if the reader grows an encoder
   stage; don't force it in before that's decided.

4. **`gated_fusion_relation_inference`** (+0.297, `hdlab/gated_fusion.py`) --
   registry `gate_decision: WIRED` but its own text admits "PENDING CODE-SWAP
   (the actual wire step, not done in the measurement cells)". So the
   registry's own WIRED label is aspirational, not actual, for the
   encoder-fusion code path. **Priority LOW right now** (same encoder-gate
   as #3), but flag: this is a case where the registry's `gate_decision`
   field says WIRED while its own provenance text says the code-swap never
   happened -- another instance of the registry-vs-reality gap, just
   self-documented this time instead of silent.

5. **`learned_relational_readout`** (HARD_PASS_MAJORITY, `gate_decision: WIRE`) --
   loop-readout wire explicitly HELD pending a 2nd independently-trained
   seed. Correctly parked, not urgent.

6. **`scale_win_tinytransformer_encoder`** (tail 29591, `gate_decision: WIRE`,
   "declare THE substrate encoder... promote to hdlab once readout/comprehension
   work settles") -- zero hdlab imports per its own provenance note. Real
   and validated, but appropriately deferred until the encoder question is
   settled (matches point above: reader has no encoder stage yet).

7. **`k_cliff_scaling`** (`hdlab/k_cliff_scaling.py`, analytic K_cliff(N)
   formula, R^2=0.99, zero imports) -- cheap process-wire (consult before
   sizing capacity cells), not code-critical. **Priority LOW**, easy win if anyone's touching capacity-sizing cells.

8. **`sr_routing_multihop`** (+0.253) -- registry itself admits "source path
   not re-confirmed on disk this pass" / `integration_status: UNKNOWN`.
   This is worse than an island -- it may be an orphaned result whose
   source cell can't currently be relocated. **Action: locate-or-retire**,
   not wire, until the source file is found.

9. **`encoder_retrain_minimal_unfreeze_top1_entity_reid_situation_model`**
   (`gate_decision: WIRE_CANDIDATE`, lifts held-out situation-model loop
   0.52->0.83) -- explicitly `PENDING_USER_steer_plus_naturalistic_validation`,
   correctly parked pending a real-text (not synthetic-template) re-run.
   Not actionable without that re-run.

## (D) LEGITIMATELY-SHELVED -- correctly unwired, listed for completeness, not flagged

`reasoner_composed_entry_arc_program` (SHELVE, de-facto abandoned 07-27),
`hdlab_encoder_cluster_vwfa_ppmi_composed_v3` (superseded by TinyTransformer),
`binder_direct_supply_grounding` (CLOSED, correctly data-bound),
`entity_slot_gate_cross_boundary_v1` (HARD_FAIL, random-init matched trained),
`attn_bilinear_readout_cross_boundary_v1` (HARD_FAIL, random-init-encoder
control matched real encoder -- exploited untrained-transformer structure,
not learned semantics), `wm_nl_binding_via_read_conditioning` (bounded, no
role generalization, HARD-FAILED held-out-role test), `native_vsa_zeroshot_novel_role`
(SHELVE pending key-orthogonality fix), `lock_in_amplifier`, `parietal_attention`,
`semantic_concept_learning` (superseded), `language_prediction_DEPRECATED`
(closed, USER directive), `redundancy_robustness`, `external_embedding_diag`
(charter invariant: borrowed embeddings never the meaning organ),
`provenance_watermark`, `cls_discrete_budget_consolidate_v6_replay` (VET_PENDING,
wiring smoke HARD_FAILed). These are honest negatives or closed decisions, not
debt -- no action needed.

## The "other active track" bucket -- not flagged, but worth naming explicitly

`char_trigram_encoder`, `kb_encoder_registry`, `partitioned_store`,
`director_kb_query`, `hd_fact_store`, `typed_rule_parser`, `cortex_eTensor`,
`composition` (binding/bundling/concept_encoder), `superposition`, `readout`,
`predictive_coding`, `pattern_completion`, `kg_ingest`, `cleanup_attractor`,
`catastrophic_forgetting`, `cert_audit`, `sequence_binding`,
`intent_classification`, `schema_abstraction`, `hierarchical_structure`,
`generation`, `cskg_foundation_v1`, `inflight_monitor` -- these are all
`WIRED` per the import graph and genuinely used, just by the ARC/cortex
reasoning frontier, the KB ingest/query surface, or cert/atom-store infra --
programs that remain independently active, not abandoned. Correctly not
flagged as the working_memory failure class. `cskg_foundation_v1` is a minor
exception worth a one-line note: its `gate_decision` says `WIRED` but its
own `integration_status` says `ISLAND` -- a self-contradictory row (used_by: []
despite the WIRED decision), likely a stale audit; cheap to fix at the next
registry pass but not urgent.

## Gate-gap finding: does the wire-at-land-time gate catch this?

**No, not fully -- and the registry rows 53-55 already prove it's fixable.**
The land-time gate (`data/capability_registry.jsonl` + `tools/capability_registry_audit.py`)
checks two things well: (1) is there a `hdlab/` module, (2) does
`tools/integration_health.py`'s import-graph scan find *a* consumer in
`experiments/` or `hdlab/`. It does NOT check whether that consumer is
reachable from the small set of files that actually run in production (the
Anne reader + its direct dependents). A module can satisfy both gate checks
by having a single throwaway `verify_*_v1.py` smoke-consumer file (several
rows above say exactly this -- e.g. row 53's own text: "the
experiments/verify_situation_model_accumulate_v1.py wire-point is a
synthetic smoke-consumer, not a comprehension-pipeline integration") and
still never be called by the reader. This is precisely how `working_memory.py`
slipped through, except `working_memory.py` didn't even get that far -- it
was never registered at all, so it didn't even hit the gate.

Two concrete fixes, both cheap:

1. **Add a USED-by-active-pipeline check.** `tools/capability_registry_audit.py`
   (or a new `tools/active_pipeline_reachability_check.py`) should compute
   the import closure from a small, explicit, CLAUDE.md-declared list of
   "production entry points" (today: the 5 files named in this task) and
   flag any `hdlab-module` row with `integration_status: WIRED` whose path
   is *not* in that closure as `WIRED_BUT_NOT_PIPELINE_REACHABLE` -- a third
   status distinct from `WIRED`/`ISLAND`, so it doesn't get silently folded
   into "the good bucket." This closes exactly the gap this audit had to do
   by hand.
2. **Registered-at-all is a separate gate from wired-correctly.** Add a
   disk-scan step (glob `hdlab/*.py`, diff against the registry's `path`
   fields) so a chain-grade module like `working_memory.py` can't exist in
   `hdlab/` for weeks without a registry row -- run this alongside the
   existing import-graph audit at session start, not as a new cron (per the
   CLAUDE.md discipline that crons silently die and the session-start read
   is the only durable enforcement).

Rows 53 (`situation_model_accumulate_register_organ`) and 54
(`coreference_resolver_...`) show the fix pattern already works when applied
deliberately: both were promoted with a *real* consumer chosen to also be a
genuine reachable dependency of the production reader script, not just an
import-graph-satisfying stub -- that's the discipline the new check should
enforce automatically instead of relying on whoever does the promotion to
remember it by hand.

## Top wire-or-shelve priorities (summary)

1. **WIRE `hdlab/working_memory.py`** -- register in the capability registry
   (close the coverage gap), then give it a real reachable consumer serving
   entity-capacity in the reader (either directly, or via `context_retention.py`).
2. **Diagnose/wire `hdlab/context_retention.py`** -- it's the one file that
   already bridges working_memory toward a retention layer; find out if it's
   meant to be the reader's capacity-extension point.
3. **WIRE `native_vsa_cross_slot_relational_binding`** (the FHRR bind/unbind
   relational mechanism) -- directly relevant to the extraction-generalization
   wall MEMORY.md currently names as the blocker.
4. **Add the USED-by-active-pipeline check** to the registry audit tool --
   process fix, prevents the next `working_memory.py`.
5. **Registry hygiene**: split the stale `working_overlay_situation_reader`
   bundle row (state_of_mind.py is actually wired-and-used now), fix the
   self-contradictory `cskg_foundation_v1` row, and locate-or-retire the
   orphaned `sr_routing_multihop` row.

This is analysis only -- nothing wired or dispatched in this pass.
