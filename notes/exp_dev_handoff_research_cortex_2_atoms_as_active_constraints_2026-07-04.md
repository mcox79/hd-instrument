# exp_dev hand-off — research: cortex-2 atoms-as-active-constraints

**Filed by:** research sub-agent, 2026-07-04.

**Trigger:** `notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md` — strategic pre-drill for the NEXT M3 arc (cortex integration closed today at 5-of-6 primitives; this drill covers the gap that atoms are stored but never automatically consulted at operation boundaries).

**Pause state:** check `data/orchestrator_paused.flag` at pickup time; this hand-off does not assume either state.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names an ANCHOR + POINTERS only. exp_dev designs ALL of: N, K, seed count, threshold bands, queue tier, smoke profile, FULL profile. This file does not specify numerical parameters beyond what the research memo already proposed as illustrative starting points (exp_dev may substitute).

---

## Anchor candidate (rank 1, only candidate from this drill)

**`exp_cortex2_atom_consultation_smoke_v1`** — first probe for atom-store
consultation as an active-constraint layer in the Cortex facade.

- Anchor pointer: `notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md` section (d) "First-probe cell design" and section (c) "Concrete cortex.py v2 architecture."
- Substrate-product reading: cortex currently composes 5-of-6 CG-verified primitives but has NO automatic consultation of the ~99-atom Stage-1 CG_META / Fix#28 store at operation boundaries — cell-authors hardcode choices instead of the substrate applying its own learned laws. This closes that gap structurally (per M3 vision, USER 2026-06-28), starting from an ADVISORY-ONLY (non-enforcing) smoke probe.
- Tier: local or CPU (analyzer-scale; new module is NO_STORAGE, stateless query wrapper — no GPU need).
- Why now: cortex integration arc just closed today; this is the natural next M3 sub-arc, and the design is now grounded in a concrete module spec (below) rather than an abstract goal.

### What the probe cell must establish (from the research memo, not re-derived here)

1. New module `hdlab/atom_consultation.py`: `AtomConsultant` (NO_STORAGE, wraps existing `hdlab.director_kb_query.DirectorKBQuery` / `load_default_kb`), `AtomMatch` / `ConsultationResult` dataclasses. See memo section (c) for full sketch.
2. Integration point: new step (0) in `Cortex.forward()`, before existing step (1) M1.5 write. New `CortexConfig` field `atom_consultation_enabled: bool = False` (default False preserves backwards-compat, same pattern as `noise_channel_enabled`) + `atom_consultation_op_class: str`.
3. Operation-class tagging: fixed small enum (COMPOSITION / FRAMING / CAPACITY / RETRIEVAL / VERIFY), explicit per call-site — NOT a learned router (memo argues cost-benefit doesn't justify a learned gate at N~100 atoms).
4. Smoke assertions (memo section d): (a) consult() returns within measured sub-ms wall-clock budget, (b) tag-filter always returns a strict subset of full atom count (never full-scan bypass), (c) at least one hand-constructed case where a matched atom's `constraint_text` correctly predicts a known CG_META law (e.g. STORAGE_STRATEGY atom fires on a COMPOSITION-tagged call, text matches "SHARDED > BUNDLED at scale").
5. `applied` stays `False` throughout this probe — this is a retrieval-correctness smoke test, NOT an enforcement test. Enforcement is a separate, later, explicitly-audited promotion decision.

### Anti-drift discriminator (mandatory; from memo section e)

Log every consultation event (matched atom_ids + operation_class + downstream
parameter choice actually used) to a SHARDED per-call provenance store. Bucket
into (i) atom matched AND downstream choice equals atom's recommended value,
(ii) atom matched but choice differs, (iii) no atom matched. Compute
match-and-honored rate = (i)/(i+ii).

- **HARD-FAIL:** match-and-honored rate <20% after N>=50 calls — consultation
  is decorative (atoms retrieved but not actually informing outcomes). Do NOT
  promote to enforced; route back to research for a 2x-drill on tag-vector
  representation instead of plain-string tags.
- **HARD-PASS:** match-and-honored rate >=70% with zero cases of a matched
  physics-law atom being silently contradicted (bucket ii entries must be
  flagged in provenance, never silent). Clears the bar for a Skunkworks-
  reviewed promotion to `applied=True` on ONE narrow, named atom class only
  (never a blanket enable across all atom classes at once).

---

## Context pointers (paths, not summaries)

- `notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md` — full memo (lit-scan sources, cost estimate, architecture sketch, risk callouts, P_deflated=0.45).
- `hdlab/cortex.py` — current Cortex facade (5-of-6 CG-verified primitives); step-numbering + provenance-dict convention that the new step (0) must follow.
- `hdlab/director_kb_query.py` — existing `DirectorKBQuery` / `load_default_kb` interface; `AtomConsultant` wraps this, does not reinvent it.
- `notes/substrate_capability_map.md` — current cap_map; this anchor is not yet a row (novel synthesis, no prior arc).
- M3 vision: `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md` and `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md` (memory files) for the governing USER directive this anchor serves.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke (bands specified above; exp_dev may sharpen but not loosen).
- Self-test per [[feedback-formula-selftests]] — new module needs its own `_selftest_*` functions matching cortex.py's existing convention.
- SMOKE = FULL code path discipline: smoke must exercise the exact same branches as the eventual FULL run (same META_RULE candidate already in force for other cells).
- Skunkworks AUDIT-ONLY on every atom-application decision — no silent enforcement, ever (per drill's explicit design constraint).
- status_log entry with `plain_language` + `importance` on delivery.

## Autonomy declaration

exp_dev decides ALL of: cell name variant, N/K/seed counts, exact threshold
values within the HARD-PASS/HARD-FAIL bands given above, queue tier
(local/CPU), smoke profile, FULL profile, and whether to build
`atom_consultation.py` as specified in the memo or substitute an equivalent
design that satisfies the same anti-drift discriminator. If exp_dev judges
the Rete-alpha-tag-filter approach is not the right shape after starting
implementation, that's exp_dev's call to make and report back — this drill
is a starting hypothesis (P=0.45, deflated), not a locked design.

---

## Filed by

research sub-agent, 2026-07-04, in response to Director's strategic
pre-drill request ahead of the next M3 arc. Hand-off ready for `/exp_dev`
pickup (routing files deprecated per USER-locked discipline; this file is
discovered directly by exp_dev's hand-off scan, sorted by mtime).
