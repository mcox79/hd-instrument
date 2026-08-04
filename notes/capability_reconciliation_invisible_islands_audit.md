# Capability reconciliation audit — invisible islands (Skunkworks/auditor)

**Trigger:** `exp_theory_of_mind_sally_anne_nested_hrr_v1` was found HARD_PASS on disk
(oracle 1.0, 5 seeds) with **zero rows** in `data/capability_registry.jsonl` — invisible
to `tools/capability_registry_audit.py` because that tool only checks
REGISTERED->wired, never HARD_PASS->registered. USER asked: are there other invisible
islands? This audit answers that, scoped and disk-verified.

**Role note:** audit-only. No cells authored, nothing wired. Recommendations are
WIRE/SHELVE judgments for Director to act on.

## Method (see conversation for full detail)
1. Scanned `data/exp_*/metrics.json` for the literal string `HARD_PASS` (2,993 dir-level
   hits; confirms the ~3029 baseline the Director quoted — this is per-seed/shard NOISE,
   not distinct capabilities).
2. Collapsed to ~2,477 base anchors (stripped `_seed_N`, `_vN`, `_smoke/_localsmoke`
   suffixes) — still noisy (arms, sub-experiments, iterations count separately).
3. Filtered to 225 anchors matching comprehension-relevant keywords (coref, situation,
   causal, binding, memory, coherence, ToM, goal, appraisal, narrative, temporal, etc).
4. Cross-checked each against `data/capability_registry.jsonl` (path/id/name fields, not
   loose token match — token match produced false "registered" positives, e.g. "sally"/
   "anne"/"mind"/"nested" all appear incidentally elsewhere in the registry blob (Anne
   reader, state_of_mind.py, etc), which would have wrongly cleared the ToM organ as
   "registered" — corrected to literal substring-of-path/id/name matching).
5. Ran `tools/capability_registry_audit.py --dry-run --json` directly — it already
   computes `unregistered_hdlab_modules` (hdlab/*.py files with zero registry row): **61
   of 105 hdlab modules are unregistered.** Cross-referenced this list against
   `notes/brain_component_functional_map_2026-08-04.md` to separate (a) correctly-unregistered
   infra primitives (Section C: atoms.py/memory.py/store.py/tracing.py/etc — genuinely
   not standalone capabilities), (b) wired reader-cluster modules that simply never went
   through the gate (candidate_generator.py, state_of_mind.py, scene_segment.py etc —
   process gap, not an island, since they're actively used and documented), from
   (c) genuine validated-but-unregistered organs.
6. **KEY BLIND SPOT FOUND:** `scan_unregistered_hdlab_modules()` only globs `hdlab/*.py`
   — it cannot see a HARD_PASS result that lives ONLY in `experiments/` and was never
   promoted to an hdlab module (exactly ToM's shape, and — new finding — VAMP-EP's and
   the grounded-appraisal organ's shape too). This is the actual hole; see systemic fix
   spec below.
7. Every verdict cited below was read directly from `metrics.json` on disk this session
   (not inherited from prior summaries or the functional map's prose).

## INVISIBLE ISLANDS (not registered AND not wired to the active reader) — ranked

### 1. `exp_theory_of_mind_sally_anne_nested_hrr_v1` (ToM) — CONFIRMED (the trigger case)
- Disk: HARD_PASS, Q2 false-belief 0.806 vs 0.138 no-partition (gap 0.668), oracle 1.0, 5 seeds.
- Registry: 0 rows. hdlab: not promoted (only `refuse_gate` dep reused).
- Doc: `notes/brain_component_functional_map_2026-08-04.md` line 133 — ALREADY CORRECTED
  same day (was mislabeled "GAP thin", now correctly "ISLANDED, HARD_PASS organ exists").
- Comprehension-relevance: **HIGH** — goal-owner inference under divergent belief; direct
  current-frontier extension (map names the exact wire-target: route off the
  coherence-selector arc, partition by narrative protagonist).
- Recommendation: **WIRE.** Registry row needed immediately (this audit does not write it
  — audit-only role; flagging for Director/skunkworks to file via A5-gated write).

### 2. `exp_grounded_appraisal_sim_earned_v1` (grounded appraisal / valence organ) — NEW
- Disk (`data/exp_grounded_appraisal_sim_earned_v1/metrics.json`), verified this session:
  `verdict: MECHANISM_EARNS`, `verdict_msg`: FULL_heldout=1.000, FULL_train=1.000,
  RANDOM=0.168, MEMORIZED=0.206, NO_APPRAISAL=0.239, revenge=1.000, specificity=1.000,
  earned_restore=1.000 vs recency_restore=0.303.
- Registry: **0 rows** reference this path (checked by exact path match, not just
  substring-in-blob — earlier substring check gave a false "FOUND" from unrelated cells
  `exp_grounded_appraisal_richer_eval_v1` / `exp_grounded_appraisal_transfer_to_text_v1`
  incidentally sharing path-list entries with other rows; the core earned-mechanism cell
  itself has no row).
- Comprehension-relevance: **HIGHEST** — this IS the current architectural pivot (blocked-
  goal->anger->retaliate, "you can't learn revenge from a book," per
  `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`). Map (line 76) already documents
  it as "ISLANDED (gate=WIRE, target unbuilt)" but the registry itself has never
  materialized a row.
- Recommendation: **WIRE** (registry row + continue the extraction-bottleneck program
  already in flight — this audit does not change program direction, only flags the gap).

### 3. VAMP-EP deep-chain solver (`exp_wave14_*vamp_chain*` family) — NEW
- Disk, verified this session across 3 cells:
  - `exp_wave14_vamp_chain_depth_ceiling_v1`: verdict `DEPTH_CEILING_HIGH`,
    acc_per_depth={50:1.0, 100:1.0, 200:1.0, 500:0.0} — sustains to depth 200.
  - `exp_wave14_vamp_chain_K_stress_v1`: verdict `K_STRESS_AGENT_READY`,
    acc_per_K={100:1.0, 500:1.0, 1000:1.0, 5000:1.0} at depth 50.
  - `exp_wave14_vamp_chain_noise_robust_v1`: verdict `VAMPNOISE_ROBUST`,
    acc_per_noise={0.0:1.0, 0.05:1.0, 0.10:1.0, 0.20:1.0, 0.30:1.0} at depth 50.
- **GOTCHA CONFIRMED:** none of these verdict strings contain the literal substring
  `HARD_PASS` (custom pass-verdicts: `*_HIGH`, `*_READY`, `*_ROBUST`). A naive
  grep-for-"HARD_PASS" island-detector (as first drafted this audit) MISSES this whole
  family. See systemic-fix note below.
- No hdlab module exists for VAMP-EP at all (confirmed: no `hdlab/vamp*.py`). Registry:
  0 rows (confirmed by id/path grep).
- Doc: functional map (line 74, synthesis item 2) already names this as the best deep-hop
  solver, "never left experiments/," and explicitly says "no hdlab organ, no registry row"
  — so this is a DOCUMENTED island, not a silently-missed one; the registry itself is
  simply behind the documentation.
- Comprehension-relevance: **HIGH** — the coherence-selector's confirmed 3-hop collapse
  (v4: all ~0.35 < random at 3-hop) is exactly the failure mode VAMP-EP's depth-200
  result solves. Caveat carried forward honestly: all wins are synthetic KG chains: NL
  causal-chain transfer is untested.
- Recommendation: **WIRE** (port to an hdlab organ + register), contingent on an NL-
  transfer smoke since the synthetic-chain result alone does not establish narrative
  applicability — flagging the caveat, not blocking the wire-decision (Director's call).

### 4. `hdlab/action_selection.py` (basal-ganglia Go/NoGo, extracted organ) — NEW
- Disk: 0 registry rows (checked by id containing "action_selection" and by path list
  membership — both empty).
- 2 exp consumers found (`exp_arc_retrieval_selection_gate_learned_credit_v1.py` —
  itself only `LEARNED_GATE_MIDDLE_BAND`, McNemar p=0.19 not significant;
  `exp_pfc_bg_composed_attention_value_gate_v1.py` — verified `verdict: HARD_PASS`,
  att_lift=0.193, value_actor_lift=0.733, n_seeds=5, oracle_repro=True). So the
  underlying HARD_PASS evidence for the *organ* is real; it just never got its own row.
- `pfc_gate_cfrpe_trained_v2` (the paired actor-critic cell, exp-only, no hdlab module of
  its own): verified `verdict: HARD_PASS`, but narrow — `n_fair=2/7` (only 2 of 7 regime
  cells clear the pre-registered fair band); gonogo_lift=0.600. Honest caveat: narrow,
  not the full regime sweep.
- Comprehension-relevance: **MEDIUM-HIGH** — map's synthesis item 4 already names this as
  the correct reuse target for the grounded-appraisal->action layer (do not rebuild).
- Recommendation: **WIRE** (register now; re-point, don't rebuild, once extraction lands).

### 5. `hdlab/slot_attention_wm.py` (parietal slot-attention stateful WM core) — NEW, lower severity
- Disk: 0 registry rows with this path.
- NOT a pure island by import count — 12 exp consumers (stateful-core / oracle-wm /
  selective-overwrite-recall cluster) — so `TRAPPED_SHARED` in practice, just never
  gated. `cross_boundary_comprehension_construction` (registered, `status:
  validated_asset_2026-07-28`) covers *some* of this cluster's evidence but is not the
  same row as the module itself.
- Comprehension-relevance: **MEDIUM** — alternative stateful situation core, disjoint
  from the live grounded-appraisal frontier per map.
- Recommendation: no urgent wire (map already treats this as a secondary track); file a
  registry row so it stops being invisible, gate_decision can default to VET_PENDING.

### 6. `hdlab/situation_model_multibank.py` / `hdlab/multi_hop.py` / `hdlab/modern_hopfield_readout.py` — minor, already partly documented
- All 3: 0 dedicated registry rows (checked by path membership).
- `situation_model_multibank.py` is mentioned only inside the `working_memory_multibank_K_capacity`
  row's free-text provenance, not as its own path entry — a minor under-registration, not
  a silent miss (map already treats it as the same wiring action as working_memory.py).
- `multi_hop.py`: map (line 49) already flags "wired-but-orphaned, no registry row" —
  documented gap, MIDDLE_BAND K=2 (weaker than the meet-in-middle reasoner variant that
  never got promoted either — compounding gap, not urgent, LOW comprehension-relevance
  right now since the frontier's chain-depth need is served by VAMP-EP instead).
- `modern_hopfield_readout.py`: map (line 60) flags "near-islanded (1 consumer)" —
  functionally redundant with the already-WIRED `cleanup_family.py` retrieval mechanism;
  LOW priority.

## Ruled OUT as false-positive islands (worth recording so they aren't re-flagged)
- `predictive_coding.py`, `working_memory.py` (`working_memory_multibank_K_capacity`
  row) — both DO have registry rows (`gate_decision` ALREADY_WIRED / WIRE respectively);
  `pipeline_status` correctly shows `WIRED_BUT_NOT_PIPELINE_REACHABLE` — consistent
  between registry and map, not a doc divergence, just a real not-yet-wired-to-the-reader
  state that's already tracked.
- Loose-token-match false "registered" hits during Step 4 above (see Method item 4) — the
  token-overlap heuristic is NOT reliable for a registry this size; direct
  path/id/name-substring matching is required (this is itself a note for anyone re-running
  a similar audit).

## Doc divergences found
- Only one material divergence found this session, and it was **already self-corrected**
  same-day by a prior pass: `notes/brain_component_functional_map_2026-08-04.md` line 133
  explicitly documents its own prior mislabel of ToM as "GAP thin" -> corrected to
  "ISLANDED (HARD_PASS organ exists, UNWIRED)". No other GAP/ISLANDED mislabels found on
  spot-check of predictive_coding, working_memory, grounded_appraisal, VAMP-EP,
  action_selection, slot_attention_wm rows against their disk verdicts — the *map* is
  currently accurate; the *registry* (`capability_registry.jsonl`) is what lags it. The
  practical divergence is process, not content: several Section-D "ISLANDED" organs the
  map already names (grounded appraisal, VAMP-EP, action_selection, slot_attention_wm)
  still have zero `capability_registry.jsonl` rows — the map got updated, the registry
  (the actual gate-tracking artifact) did not.

## Systemic fix (SPEC ONLY — not built, per audit-only role)

Extend `tools/capability_registry_audit.py` with a new pass,
`scan_unregistered_hard_pass_anchors()`, run alongside the existing
`scan_unregistered_hdlab_modules()`:

1. **Input:** glob `data/exp_*/metrics.json` (or, cheaper, only anchors whose dir name
   has no `_seed`/`_v[2-9]`/`_smoke` suffix, to approximate "latest of a lineage" without
   a full read of all ~7000 dirs every run — needs a real base-anchor collapse function,
   not the ad-hoc regex this audit used, since suffix conventions are inconsistent).
2. **Verdict test — DO NOT hardcode literal `"HARD_PASS"`.** This audit's own VAMP-EP
   finding shows custom pass-verdicts (`*_ROBUST`, `*_READY`, `*_HIGH`, `MECHANISM_EARNS`,
   etc) are common and a literal-string check silently misses them. Practical proxy:
   maintain a small denylist of known-negative/pending verdict-name substrings
   (`FAIL`, `HONEST_NEG`, `PENDING`, `INCONCLUSIVE`, `MIDDLE_BAND`, `CEILING` — careful,
   `DEPTH_CEILING_HIGH` is a PASS! — `KILLED`, `ABANDONED`) and flag anything NOT matching
   the denylist as "candidate positive, needs human triage" rather than trying to
   positively enumerate every pass-verdict spelling. Cheaper and safer than a fragile
   allowlist.
3. **Match against registry:** for each candidate anchor, check literal substring
   membership of the anchor's core name (stripped `exp_`/version/seed suffixes) against
   the UNION of every registry row's `path` list entries + `id` + `name` fields (NOT a
   token-overlap heuristic — Step 4 above showed token-overlap produces false-registered
   positives on a registry this size, because common words like "mind"/"nested"/"sally"
   recur incidentally across unrelated rows).
4. **Output:** a new report section `invisible_island_candidates` (anchor, verdict,
   verdict_msg snippet, whether an hdlab/*.py module exists with a related name) --
   printed as a FLAG (nonzero exit) alongside the existing flags, so it surfaces at
   session-start reads the same way `unregistered_hdlab_modules` already does.
5. **Cost control:** this needs to run over thousands of dirs; cache a
   `{anchor: (verdict, mtime)}` index (e.g. `data/capability_registry_reports/
   hard_pass_anchor_index.json`) and only re-scan anchors newer than the cached mtime, so
   routine session-start audits stay cheap after the first full scan.

This closes the hole the ToM case demonstrated: today's tool answers "is every
REGISTERED capability wired" but never asks "did every disk-verified positive result get
registered in the first place." The fix adds that second direction explicitly.
