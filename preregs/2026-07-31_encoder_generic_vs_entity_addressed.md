# PRE-REG: encoder_generic_vs_entity_addressed_v1

Filed: 2026-07-31. Cell: `experiments/exp_encoder_generic_vs_entity_addressed_v1.py`.
Director spawn: does the certified minimal-unfreeze encoder retrain (atom 29593) lift GENERIC
representation-quality (helps even NON-entity-addressed decode = domain-general) or is it
ENTITY-ADDRESSING-SPECIFIC (only helps queries/decodes that route through entity/mark identity)?

## Question
`exp_encoder_alltype_transfer_v1.py` (landed HARD_PASS, this session) showed the retrain lifts ALL
THREE situation-model query types (a_name_maintenance, b_competitive_coref, c_overwrite), including the
two "non-coref" types. But all three are still ENTITY-ADDRESSED in the broader sense: every query
answer is retrieved by the FHRR reader addressing a specific entity's binding (`main_enc` arm, via
`ef`/`ih` addressing) -- so "universal across query types" is NOT yet "universal outside entity-routed
comprehension". This cell tests a genuinely non-entity-addressed decode: does the retrain also sharpen
the encoder's own token-level CONTENT representation (which color fills a semantic slot), read with ZERO
entity/mark identity involved (no cross-sentence binding, no addressing step)?

## One variable
Same as sibling cells: which encoder checkpoint `eb.EncoderExtractor` loads (frozen v2 default vs
persisted retrained `data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt`), via the SAME
`__init__.__defaults__` monkeypatch pattern already VET'd (frozen-vs-frozen 0.0-drift control).

## Measurement 1 (decisive): non-entity-addressed content decode
`eb.build_decoded_dataset(dataset, extractor, "role_attn")` (called internally by
`lt.score_extractor` -> surfaced in `base_loop._eval_heldahead(...)["sc"]["stage_role_attn"]`, already
computed as a side-effect of the SAME held-ahead eval every sibling cell runs -- no new decode machinery)
returns a per-stage accuracy tally with keys `{ENT, MARK, S, P, ENT_q, MARK_q, entity_consistency}`.
- **S** and **P** are the state/placement filler-color decodes for each event
  (`"the ENT was set S and placed P ."`) -- read from the LOCAL token span's representation via a fixed
  role cue ("what was set to?" / "what was placed to?"), with NO cross-sentence binding, NO entity/mark
  matching, NO addressing step. This is the genuinely non-entity-addressed probe: "which color word is
  written here", independent of which entity the event belongs to.
- **ENT, MARK** (tag-position identity-label decode), **ENT_q, MARK_q** (query-frame decode, requires
  identifying the target entity/mark) and **entity_consistency** (cross-mention consistency of decoded
  entity id) are the entity-addressed comparison set.
- Reused verbatim; this cell adds ZERO new decode code for measurement 1, only surfaces existing fields.

## Measurement 2: representation-geometry diagnostics (entity vs non-entity dims)
- ENT-slot separability: `lt.within_minus_cross(ext, held_colors, seed)` (existing, cert-atom-adjacent
  function; measures mean within-color-pair cosine minus mean cross-color-pair cosine on ENT-slot
  role_attn reps) -- reused verbatim.
- S-slot separability (NEW, ~15 lines, mirrors `within_minus_cross` exactly but targets the S filler
  slot instead of ENT, via `eb.render_name_event(o1, c, o2)` and `ef._ent_slot_reps` which is already
  slot-type-generic): same within-minus-cross computation on STATE-filler-color identity instead of
  entity identity. This answers "does the retrain sharpen ONLY entity-routed geometry or the
  representation broadly."

## Pre-registered bands (fixed before running)
- **GENERIC/DOMAIN-GENERAL (HARD_PASS)**: mean(S,P) decode lift >= `LIFT_MIN = 0.05` (matches sibling
  cells' floor) on BOTH S and P, AND S-slot geometry delta (tuned - frozen) is >= `GEOM_FRAC_MIN = 0.4`
  of the ENT-slot geometry delta measured in the SAME run (ties the geometry floor to this cell's own
  measured entity-sharpening magnitude rather than an arbitrary absolute number) -- the retrain sharpens
  representation quality broadly, not just entity-routed dims.
- **ENTITY-ADDRESSING-SPECIFIC (HARD_FAIL, informative negative, not broken)**: mean(S,P) lift stays
  < LIFT_MIN on BOTH S and P, AND S-slot geometry delta < `GEOM_FRAC_FLAT = 0.15` of the ENT-slot delta
  (materially flat relative to the entity-geometry sharpening) while ENT-slot delta itself clears
  `ENT_GEOM_MIN = 0.02` (i.e. entity geometry DID sharpen, replicating the cert atom's 0.057->0.110
  direction) -- real, bounded: the retrain is entity-addressing-specific.
- **MIDDLE**: any pattern that clears neither pole cleanly (e.g. one of S/P lifts but not the other, or
  ENT geometry itself fails to clear `ENT_GEOM_MIN` making the ratio uninterpretable). Full per-type,
  per-slot trajectory reported for the escalation decision.
- **INVALID**: drift-control fails (max |frozen2-frozen1| decode drift > `DRIFT_MAX = 0.01`) OR
  `clean.audit_construction` flags fails OR a required persisted retrained ckpt is missing for a seed.

## CRLB / feasibility
`crlb_n/a`: no closed-form noise floor applies -- this is a paired frozen-vs-tuned decode/geometry
comparison on a fixed harness, not a capacity sweep.

## Grounding (not re-derived)
Cert atom 29593 (`exp_encoder_retrain_persist_v1`): name<->name (ENT-slot) cosine 0.057 -> 0.110 under
this exact retrain recipe. `exp_encoder_alltype_transfer_v1` (landed, this session, HARD_PASS
UNIVERSAL_LEVER across a/b/c query types) established the query-level lift is broad WITHIN
entity-addressed queries; this cell is the next open discriminator -- whether that broad lift extends
OUTSIDE entity-addressed decode entirely.

## Prior-work check
`substrate_query.sh "encoder representation quality generic vs entity-addressing specific non-entity
decode geometry"` -- top hit cosine=0.3271 (KG zero-shot relation-prediction entity-pair-geometry note,
different domain, not a prior measurement of this question). No hit above cosine 0.30 addresses whether
THIS certified encoder break's lift is generic-representation vs entity-addressing-specific. Not a
rediscovery.

## Compute architecture
sequential-CPU, eval-only (no training in this cell; 3 frozen-encoder forward-pass builds per seed,
matching sibling cells; geometry reuses the SAME already-built extractor instances, no extra encoder
construction). INLINE-LOCAL foreground-to-completion. Storage: no_storage (eval-only, reads persisted
ckpts read-only).

## Scope / parallel-safety
Writes only to `data/exp_encoder_generic_vs_entity_addressed_v1/` (new dir). Reads
`data/exp_encoder_retrain_persist_v1/ckpt_seed_*.pt` read-only. Does not touch
`exp_coref_encoder_transfer_v1`, `exp_encoder_alltype_transfer_v1`, or any `exp_encoder_*generaliz*` dir
another agent may be using in parallel. Does not modify `base_loop`, `lt`, `eb`, `ef`, or the growing-
library cell.

## Cell-template checklist
- `cell_chunked`: true (per-seed unit, `experiments/_seed_checkpoint`-style `tools/exp_checkpoint.py`
  resumable pattern, matching sibling cells).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true (canonical helpers,
  matching sibling cells verbatim).
- `arms_differ_verified`: frozen1 vs tuned per-seed results must differ; frozen1 vs frozen2 (drift
  control) must be within `DRIFT_MAX`.
- `final_metrics_atomicity`: tmp_replace.
- `except SystemExit: raise` before `except Exception` (no bare `except`, no `BaseException`).
- `cardinality_ok`: EXPECTED_N_UNITS = len(SEEDS_LITE) = 3.
- `progress_logging`: print_flush_true (elapsed_s per seed is well under 1800s so §17 flushing is
  best-effort, not the MANDATORY >=1800s gate, but applied anyway for consistency with sibling cells).
