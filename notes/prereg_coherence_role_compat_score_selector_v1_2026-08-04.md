# Pre-reg: coherence_role_compat_score_selector_v1

Filed by: exp_dev. Director spec: `notes/research_coherence_constraint_satisfaction_settling_selector_design_spec.md`
(commit 70eb5d817) WITH the Director's single-pass refinement (build the minimal role-compat
SCORE, not the iterative settling loop -- the spec's own Henry test is single-pass-solvable).

## Scope / claim

MECHANISM-CAPACITY proof over SUPPLIED role-structure: "the substrate can USE a supplied
symbolic role-compatibility structure to discriminate GOAL_OWNER role-content where
`decode_coherence_margins` gave EXACTLY 0.0 (`data/exp_coherence_role_conflict_crosstalk_v1/
metrics.json`)." Does NOT prove (a) iterative settling is needed (single-pass suffices here),
NOR (b) that role-structure can be EARNED from text (supplied here). N=1 existence proof
(one candidate-pair item family, 3 controlled variants + positive control, 5 seeds for
determinism-robustness, not for statistical variance -- the mechanism is deterministic given
supplied structure).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)

`bash tools/substrate_query.sh "role compatibility score selector goal owner binding coherence
single-pass"` -> top hits `coherence_selector_insim_v1` (HARD_FAIL, cosine=0.2871) and
`coherence_selector_insim_v2` (HARD_PASS, cosine=0.293) -- BOTH BELOW the cosine>0.30
rediscovery threshold, and on inspection both are a DIFFERENT mechanism (`COHERENCE_REVERSE_
REPLAY`, a TD-replay-learned entity-type-recurrence selector over episodic sequences,
`experiments/exp_coherence_selector_insim_v2.py`) answering a different question (predicting
which entity a pronoun/reference resolves to via learned reverse-replay, generalizing to
NOVEL entities) -- NOT this cell's supplied-symbolic-role-compat-table + single-pass score.
Verdict: novel, not a rediscovery.

## The mechanism (minimal, per Director refinement -- NOT iterative settling)

For a GOAL_OWNER query at outcome-event `E_out` contested between two candidate entities
(true owner, foil): `score(E) = sum over E's OTHER established (role-type, event-type)
propositions of w(GOAL_OWNER, role-type-at-event-type)`, where `w` is a SUPPLIED symbolic
lookup table over 4 Trabasso-taxonomy-derived combined role/event-type labels:
- `AGENT_OF_ATTEMPT` (the entity is AGENT of an ATTEMPT event elsewhere) -> w = +1.0
  (causal-chain adjacency GOAL -> ATTEMPT, spec Section 3 item 2)
- `EXPERIENCER_OF_OUTCOME` (the entity is EXPERIENCER of an OUTCOME event elsewhere) -> w = +1.0
  (causal-chain adjacency GOAL -> OUTCOME/REACTION, spec Section 3 item 2)
- `AGENT_OF_UNRELATED` / `EXPERIENCER_OF_UNRELATED` (role at an episode with NO causal link to
  `E_out`) -> w = 0.0 (spec Section 3 item 2, "orthogonal roles = 0")

No FHRR cosine, no event-COUNT term, no vector geometry anywhere in `w` or in the score --
`w` is a plain Python dict lookup over 4 symbolic string labels. Established-proposition NODES
are pulled from a real `hdlab.situation_model_accumulate.AccumulateRegister` (constructed +
populated via `add_event` for real, self-test-verified -- genuine reuse of the situation-model
organ for node PROVENANCE) but the SCORE reads the role-type labels symbolically from the
same construction data used to populate the register, NOT via FHRR `decode()` -- this is the
whole point (decode-margin is what's already proven role-content-blind).

SELECT: `hdlab.self_improving_loop.decide_keep_or_revert` (reused verbatim, unmodified) applied
to `{"role_compat": margin}` where `margin = score(true_owner) - score(foil)`. Returns
`"role_compat"` (adopts true owner over the recency/baseline foil pick) iff margin clears
`ABSTAIN_BAND=0.02`; else `None` (keeps the wrong/recency baseline pick).

Iterative settling explicitly NOT built -- deferred per Director: this item is single-pass
solvable (one application of the score separates true owner from foil); a future
globally-coherent-but-locally-ambiguous case that single-pass cannot solve would justify
building the relaxation loop next, not testable at N=1 here.

## Item construction (4 variants, all built from the same 2-candidate Henry/old_gentleman
frame; entity ID strings kept, event-slot integers reseeded per seed for robustness)

1. **ORIGINAL (load-matched)**: true owner (Henry) established props =
   `[AGENT_OF_ATTEMPT, EXPERIENCER_OF_OUTCOME]` (score=2.0); foil (old_gentleman) established
   props = `[AGENT_OF_UNRELATED, EXPERIENCER_OF_UNRELATED]` (score=0.0). **Control 1 LOAD-MATCH**:
   assert `len(established[true_owner]) == len(established[foil])` (2==2) BEFORE scoring --
   same node COUNT, only role-TYPE differs; rules out load as the explanation (mirrors the
   assertion pattern at `exp_coherence_role_conflict_crosstalk_v1.py` ~line 164).
2. **ANTI-RECENCY (Control 3)**: same role-content as ORIGINAL, but event-slot positions
   reordered so the foil's (score=0.0) established props are the MOST RECENT (closest to
   `E_out`'s event-slot) and the true owner's (score=2.0) established props are furthest --
   a recency-keyed baseline would pick the foil; role-compat score must still pick Henry
   (score is order/position-invariant by construction -- the test is that the mechanism
   ignores position and drives on role-content alone).
3. **CONTROL 2 -- ROLE-TABLE SCRAMBLE (the decisive control)**: same items as ORIGINAL, but
   `w` is replaced by `W_SCRAMBLED = {AGENT_OF_ATTEMPT: 0.0, EXPERIENCER_OF_OUTCOME: 0.0,
   AGENT_OF_UNRELATED: 1.0, EXPERIENCER_OF_UNRELATED: 1.0}` -- a fixed involution swap of the
   table's VALUES, item construction (node set / counts / positions) UNCHANGED. If the score
   genuinely uses role-CONTENT (reads the table), this must COLLAPSE the discrimination (margin
   flips negative -> `decide_keep_or_revert` returns `None`, wrong/recency pick kept). If the
   margin and pick are UNCHANGED despite the scramble, the "win" is a structural/count/position
   artifact (the `shuffled_reproduces=True` signature from
   `data/exp_coherence_role_conflict_crosstalk_v1/metrics.json`) = HARD-FAIL.
4. **POSITIVE CONTROL**: foil has ZERO established props (empty list, score=0.0 by construction,
   not by table lookup); true owner keeps `[AGENT_OF_ATTEMPT, EXPERIENCER_OF_OUTCOME]`
   (score=2.0). Margin=2.0, must fire near-ceiling (>> abstain_band) before trusting any
   negative -- pipeline sanity gate.

## Compute architecture

Sequential-CPU, justified: this cell IS the primitive under test (a plain symbolic dict-lookup
+ sum, no vector geometry); wall time << 10s total for all 5 seeds x 4 item variants. No GPU
batching candidate exists (nothing to batch -- scalar arithmetic over 2-4 established props per
item). `storage strategy: no_storage` (no PartitionedStore/composition; the `AccumulateRegister`
instances constructed here are single-item, single-passage scratch objects, not persisted).

## Bands (pre-registered)

**HARD-PASS**: role-compat score correctly picks the true owner (Henry) in ORIGINAL
(load-matched) AND ANTI-RECENCY across all 5 seeds, AND Control-2 (role-table scramble)
COLLAPSES the discrimination (wrong pick / margin <= abstain_band) across all 5 seeds, AND the
positive control fires near-ceiling (margin >= 1.0, i.e. >> abstain_band=0.02, in every seed).

**HARD-FAIL**: EITHER (a) ORIGINAL or ANTI-RECENCY fails to pick the true owner in any seed
(ties/picks foil -- adds nothing over the single-pass read it was meant to fix), OR (b) the
Control-2 table-scramble REPRODUCES the unscrambled margin/pick in any seed (artifact
resurfacing under new machinery -- the single most diagnostic failure per the design spec).

**MIDDLE_BAND**: fires at N=1 but a control is inconclusive/underpowered (should not occur
given this is a fully deterministic symbolic mechanism -- included as the honest fallback if a
seed genuinely disagrees with the others, which would itself be a bug signal worth flagging).

## Discriminator-fires / baseline-in-band gates

This is a DETERMINISTIC symbolic mechanism (no noise, no learned params) -- the standard
`baseline_in_band (0.05 < baseline < 0.95)` AUC-style gate does not apply (no continuous
baseline accuracy to saturate). Substitute gate: **the RECENCY-BASELINE arm (implicit: "adopt
whichever candidate is nearest to `E_out`") must independently be WRONG on the ANTI-RECENCY
item** (foil is nearer -> recency baseline picks foil, which is the wrong owner) -- this is
asserted in the item construction itself (Control 3), giving the mechanism something real to
overturn. `discriminator_fires: verified via anti-recency item construction, not a probability
sweep`.

## Cell-template mandates checklist

- `cardinality_ok`: `EXPECTED_N_UNITS = 5 seeds x 1 (no sweep axis beyond seed)`; verdict logic
  counts `len(per_seed)`; `< 5` -> `HARD_FAIL_CARDINALITY_BREACH`.
- `arms_differ_verified`: True -- ORIGINAL / ANTI_RECENCY / SCRAMBLE / POSITIVE_CONTROL item
  dicts hashed and asserted non-identical at self-test + smoke.
- `final_metrics_atomicity`: `tmp_replace` (single-shot smoke/full, `os.replace` pattern).
- Outer try/except: `except SystemExit: raise` / `except KeyboardInterrupt: raise` /
  `except Exception as e:` (crash-diagnostic + re-raise) -- no bare `except:`, no
  `except BaseException`.
- `crlb_n/a`: "no continuous noise floor -- deterministic symbolic score, not a decoded/noisy
  signal; CRLB formula does not apply."
- `baseline_in_band`: n/a per Discriminator-fires section above; substituted with the explicit
  anti-recency-baseline-is-wrong construction check.
- `cell_chunked`: False (single cell file, <10s total, per-seed checkpoint via
  `experiments/exp_checkpoint.py` unit_key/record_unit/load_units, same pattern as
  `exp_coherence_role_conflict_crosstalk_v1.py`).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: True / True /
  N/A (exempt, `elapsed_s` << 1800s threshold for Section 17 print-progress-flushing and the
  60s heartbeat rule of thumb).
- `progress_logging`: n/a (`timeout_s` << 1800; Section 17 exemption).
- All numbers in this pre-reg and the cell docstring are `THEORETICAL@this pre-reg's own w-table
  design` (the `w` values are the SUPPLIED structure being tested, not measured) except the
  `cosine=0.2871/0.293` KB-check values, which are `MEASURED@` the `substrate_query.sh` output
  above.

## Dispatch

LOCAL/CPU only (`local_cpu_queue`, or direct `.venv/Scripts/python.exe` invocation if the queue
is flag-paused). No push, no remote. Self-test -> smoke -> full, all foreground, all expected
to complete in well under 10s combined (deterministic symbolic mechanism, no heavy compute).

## Honest scope reminder (verdict_msg + `scope_label` field, mandatory)

A HARD-PASS here is a mechanism-capacity existence proof over SUPPLIED role-structure at N=1.
It does NOT prove settling is needed (single-pass sufficed), does NOT prove role-structure can
be EARNED from raw text (supplied by hand here), and is NOT a general role-content-coherence
capability claim.
