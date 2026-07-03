# Director post-compaction BACKUP — 2026-07-03 LATE

**Filed 2026-07-03 ~19:20Z. Read this file end-to-end before any other action. Replaces prior BACKUP as pickup canonical.**

---

## STEP 0: FIRST ACTIONS (run these in order)

```bash
# 1. Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# 2. Recent landings pane (auto-refreshed by tools/landing_notifier.py every 3 min)
cat d:/AI/hd-instrument/data/latest_landings.md

# 3. Session tally disk-audit
grep -c "$(date -u +%Y-%m-%d)" d:/AI/hd-instrument/data/substrate_index/{math,meta}/atoms.jsonl

# 4. In-flight spawn state (task-notifications will arrive automatically)
ls C:/Users/marsh/AppData/Local/Temp/claude/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a/tasks/*.output

# 5. Tailscale test (blocker for remote dispatch)
timeout 10 ssh -o ConnectTimeout=5 -o BatchMode=yes marsh@home "echo up" 2>&1
```

Then read the 6 files below in this order:
1. THIS FILE (fully)
2. `notes/design_layer_075_candidate_refinement_primitive_drill_synthesis_2026-07-03.md` — Layer 0.75 v3 mechanism design (arc-closed)
3. `notes/design_m3_cortex_layer_substrate_operates_off_stage1_findings_2026-07-03.md` — M3 cortex Layer 0.5+0.75+1 pipeline (updated 5x today)
4. `notes/research_optimal_retrieval_architecture_for_substrate_director_kb_2026-07-03.md` — original drill that set the arc direction
5. Latest memory index `C:/Users/marsh/.claude/projects/d--AI/memory/MEMORY.md`
6. Any pending routing files matching `notes/watchdog_ping_to_research_*.md`

---

## STEP 1: TWO INFRASTRUCTURE BLOCKERS (as of 19:20Z)

### 1a. Tailscale peer key expired on marsh@home (USER ACTION REQUIRED)

**Symptom:** `ssh marsh@home` → "connect to host home port 22: Connection timed out"
**Root cause:** Testbed identified: tailscale peer key expired between 18:20Z and 18:45Z
**Fix:** USER must run `tailscale up` on the home box
**Impact:** ALL remote dispatch (overnight_queue GPU, remote_cpu_queue) is DOWN until re-auth
**Recovery when restored:** dispatch queue below (STEP 4)

### 1b. Safety classifier occasional outages (transient, self-resolves)

Earlier in session got 4 API `ConnectionRefused` crashes across orchestrator/exp_dev spawns (crashed WITHOUT completing remote work). Classifier came back after ~5 min. If it fails: wait, do read-only work, retry.

**Rule I filed this session:** don't propagate spawn-agent landing reports without off-disk verify — the `data/exp_<anchor>/` AND `data/exp_exp_<anchor>/` (SH-4 double-prefix) paths must both be checked. Testbed candidate fix flagged for verify_landing.py + scp_recover_landing.py + Skunkworks role verify tooling.

---

## STEP 2: SPAWNS COMPLETE AT COMPACTION TIME (updated 19:57Z)

**All in-flight spawns have RETURNED. Files committed locally; push blocked pending Tailscale.**

| agentId | role | result |
|---|---|---|
| `a4f83923fa23b6b28` | Probe 6 v2 TOPOLOGY × MECH revival | **SMOKE HP** commit `9d1995f81`; mech_var=0.20 at F=1 AND F=16; ranking CROSSOVER (modern wins F=1, soft_energy wins F=16) |
| `a9ac5b62777c16c18` | Probe 7 v2 N × MECH revival | **SMOKE HP** commit `20d72dba6`; mech_var=0.100 at N=2048 (H1 threshold); cliff N-dependent |

**Both required grid revision (Plate 0.14×N was 5-10× too pessimistic).** Empirically corrected: L≥4, corr≈0.90 for SHARDED FHRR.

**⚠️ KEY FRAMING CORRECTION:** the "STORAGE UNIQUELY MODERATES" thesis I was pushing toward is FALSE. Convergent evidence from Probes 6 v2 + 7 v2 shows ALL AXES moderate CLEANUP_MECHANISM at cliff-adjacent regime; NONE at deep-saturation. See AMENDMENTS at bottom of this file for full analysis.

**Post-Tailscale action:** push commits `9d1995f81` + `20d72dba6` + dispatch Probes 6+7 v2 FULL to overnight_queue GPU (3 seeds each, ~15s per seed).

---

## STEP 3: USER ACTIVE STRATEGIC DIRECTION (verbatim)

> "prepare for compaction it's not that far away. make sure the next sesssion has everything theey need"
> "keep going full auto"
> "if there is design space to map, we should 100% do that" (regime map arc)
> "Are we using the GPU to full effect on mapping?" (GPU utilization audit; caught me under-firing)
> "keep pushing" (continuous full-auto directive)
> "no closed enum" (brain-analog design principle — filed as project memory)

**Full-auto = make the call, don't stack questions** (USER-locked rule filed today).

---

## STEP 4: PRIORITY QUEUE POST-COMPACTION (once infra restored)

### Immediate on wake (assuming both blockers resolved)

1. **Read `data/latest_landings.md`** — captures any landings that arrived during compaction
2. **Check Probe 6 + 7 SMOKE landings** — if HP → dispatch each to remote GPU FULL via orchestrator
3. **Recovery orchestrator** — verify remote queue + re-dispatch anything that got queued pre-Tailscale-expiry:
   - **Probe 4 STORAGE × N FULL** (SMOKE HP; SMOKE showed BUNDLED-delta-N cross-term emerging)
   - **Probe 5 STORAGE × TOPOLOGY FULL** (SMOKE HP; ceiling/floor at SMOKE; needs mid-band)
   - **BGE 178K cache build** (~5hr GPU; unblocks 170K scale re-test)
4. **Layer 0.5 FULL landing check** at `data/exp_layer_05_production_wiring_skeleton_smoke_2026_07_03/metrics.json` — may have landed pre-Tailscale-expiry on remote_cpu_queue
5. **170K unified scale re-test cell** — waits for BGE cache; author reactivation via SendMessage to task-id `a7e8f6084e84c6ec3` if still resumable, else re-dispatch fresh

### Later (as spawn slots open)

6. Skunkworks landed-VETs on any FULL landings
7. If Probes 6+7 SMOKE reveals cross-terms: file amendment atoms to Probes 2+3 revising MM_STANDARD → potential CG_META
8. If Probes 4+5 FULL confirm STORAGE moderates N and TOPOLOGY: file composite CG_META `PHYSICS_LAW_STORAGE_UNIQUELY_MODERATES_v1`
9. Non-STORAGE pair probes for regime map completeness: N × TOPOLOGY, N × ALGEBRA, TOPOLOGY × ALGEBRA
10. Non-mechanism pair probes: STORAGE × ALGEBRA (last of the 4 STORAGE-pair probes)

---

## STEP 5: DISCIPLINE REMINDERS (5+ Fix#28 hits today; internalize)

**Fix#28 pattern hits recorded today (7 total):**
1. Wikipedia FULL 10K hallucination (morning)
2. PHYSICS_LAW over-framing (M-sweep CG_META — scope-narrow correction)
3. PPMI-alone-first over-framing
4. Orchestrator Probe 3 "fabricated report" (actually SH-4 verify tooling bug — memory rule refined)
5. Probes 2+3 saturation-vacuous framing (over-claimed nulls; Skunkworks caught both)
6. Exp 3E FULL over-framing (declared arc-closed; Skunkworks downgraded to MM_MARGINAL)
7. Layer 0.75 v3 SMOKE→arc-closure over-framing (declared closed at SMOKE; corrected)

**Discipline rules to READ before propagating any spawn-agent report:**

- `feedback_orchestrator_hallucination_pattern_verify_disk_before_propagating_2026-07-03.md` — verify BOTH single-prefix AND double-prefix paths
- `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03.md` MM_STANDARD — cite exact source signatures, don't abstract; extension: REGIME-mismatch is also a class
- `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md` — SMOKE HP ≠ arc closure; requires FULL + STACKED + cv<threshold + all-seeds-above-bar
- `feedback_full_auto_means_make_the_call_not_stack_questions_USER_2026-07-03.md` — stacking questions is standing
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03.md` — SMOKE gate for null-under-test cells must not gate on discriminator firing (Probe 2 cell-author caught this)
- Skunkworks-filed `META_saturation_floor_masks_null_variance_probe3_lesson` — null result is vacuous if grid saturated (Probes 2+3 hit this)
- `feedback_director_is_self_reference_stop_third_person_USER_2026-07-03.md` — I am the Director; use "I" not third-person

**Before framing to USER:** ask "would Skunkworks reproduce this claim off-disk with the tightest verification?" If no, downgrade tier and re-frame.

---

## STEP 6: SESSION TALLY (real disk truth at 19:20Z)

- **88 atoms filed today** (math=46, meta=42)
- **~15 landings today** (some crashed dispatches don't count)
- **~16 memory rules filed today** — huge discipline layer investment
- **6 orphan-kinds → 58 AtomKind enum-adds** (Testbed Blocker A fix)
- **Retrieval-architecture arc marginally closed** (Exp 3E FULL: cv=0.148 at CG boundary)
- **1 new physics-law axis established** + **1 CG_META promotion** in single session
- **7 infrastructure fixes committed + pushed**

---

## STEP 7: REGIME MAP ARC STATE (Stage 1 finalization extended per USER)

### CONFIRMED (VET-verified off-disk)
- **Probe 1 STORAGE × MECH FULL: CG_META CONFIRMED** — cv=0.148, 24/36 vs 0/36 categorical discrimination, mech_var@BUNDLED = 0.103 ± 0.03. Iterative_cosine wins BUNDLED. Real physics finding.

### SATURATION-VACUOUS (revival needed)
- **Probe 2 N × MECH FULL: MM_STANDARD** — grid saturated at 1.0 everywhere, null result meaningless. Probe 7 addresses via non-saturated regime.
- **Probe 3 TOPOLOGY × MECH FULL: MM_BOUNDED_NULL** — same saturation issue. Probe 6 addresses via non-saturated regime.

### SMOKE HP only (FULL crashed, dispatch queued)
- **Probe 4 STORAGE × N**: SMOKE showed BUNDLED gains with N (cross-term emerging: BUNDLED_delta_N=+0.10). FULL will discriminate H1 (STORAGE master moderator) vs H2 (mech-specific).
- **Probe 5 STORAGE × TOPOLOGY**: SMOKE at ceiling+floor points only. FULL 48-point grid resolves.

### Authoring in flight (local SMOKE)
- **Probe 6 non-saturated TOPOLOGY × MECH** revival (agent a4f83923fa23b6b28)
- **Probe 7 non-saturated N × MECH** revival (agent a9ac5b62777c16c18)

### The pending "STORAGE UNIQUELY moderates" composite CG_META

**NOT VALID YET.** Only Probe 1 has non-saturated evidence. Composite claim needs:
- Probe 6 SMOKE + FULL to show TOPOLOGY null at non-saturated regime (or reveal cross-term)
- Probe 7 SMOKE + FULL to show N null at non-saturated regime (or reveal cross-term)
- Probes 4+5 FULL to show STORAGE actively moderates the other 2 axes (positive evidence for master-axis)

Depending on outcomes, the composite atom is either:
- `PHYSICS_LAW_STORAGE_UNIQUELY_MODERATES_CLEANUP_MECHANISM_in_FHRR_v1` (Probes 6+7 null)
- `PHYSICS_LAW_STORAGE_MASTER_MODERATOR_v1` (Probes 4+5 confirm + 6+7 null)
- `PHYSICS_LAW_STORAGE_MECHANISM_SPECIFIC_COUPLING_v1` (Probes 4+5 null; Probe 6+7 could be null OR cross-term)

---

## STEP 8: OTHER OPEN ARCS

### Retrieval-architecture arc (MARGINALLY closed)

- **Exp 3E FULL: MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES** (aggregate)
- **Exp 3E CG_HARD_PASS** sub-claim on S1+S2-subtract diagnosis (drift 0.004 vs 0.511 at FULL)
- Revival to CG_aggregate: 5-seed OR 300q/seed s.t. sample-sd cv<0.09 AND MAIN margin ≥ 0.03

**hdlab/layer_075_structural_slot_filter.py** committed (03008c72e) — the mechanism promoted to first-class primitive. 6 verification tests PASS.

### Layer 0.5 production wiring

- SMOKE HP (INTEGRATION_END_TO_END = 0.833, 6-arm cell)
- FULL dispatched to remote_cpu_queue at 17:41Z (pre-Tailscale-expiry) — check `data/exp_layer_05_production_wiring_skeleton_smoke_2026_07_03/metrics.json` on wake for real landing

### 170K unified scale re-test

- Cell authoring halted mid-work by prior blockers (Blocker A + B); NOW blockers cleared per Testbed reconciliation
- Cell task `a7e8f6084e84c6ec3` may be resumable via SendMessage; else re-dispatch fresh with same design
- Waits for BGE 178K cache build (~5hr GPU when Tailscale restored)

### Open project principles (filed as memory)

- `project_substrate_ingest_completeness_and_addressability_USER_2026-07-03` — no silent truncation/placeholders
- `project_substrate_open_relation_vocabulary_no_closed_enum_USER_2026-07-03` — relations are ATOMS not enum values (brain-analog)
- `project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03` — regime boundaries + cross-terms + composition rules
- `project_stage1_phase_diagram_gaps_candidate_K_sweep_2026-07-03` — K-sweep gap noted
- `project_remote_repo_drift_4425_commits_testbed_cycle50_option_b_2026-07-03` — legacy branch triage

### Open infrastructure debt (Testbed-owned)

- Verify tooling path-convention: `verify_landing.py`, `scp_recover_landing.py`, Skunkworks role-verify default all use single-prefix; MUST check both
- `.gitattributes` with `* text=auto eol=lf` to prevent CRLF drift
- Orchestrator pre-dispatch remote-freshness check (would have prevented today's 5hr BGE burn attempt)
- SH-4 double-prefix cosmetic (runner canonicalization to single-prefix consistently)
- 4425-commit legacy branch on `testbed-cycle50-option-b` (audit before discard)
- 205 untracked preregs on remote (dedupe vs origin/main; PR the net-new)

---

## STEP 9: 5 STAGE 1 CG_META PHYSICS-LAW ATOMS ABOUT 4 SUBSTRATE SWEEP AXES

**FRAMING CORRECTION (Skunkworks structural VET 2026-07-03T21:35Z):** Prior heading "5 CG_META PHYSICS-LAW AXES" conflated two distinct concepts. Corrected: **5 abstract physical-law atoms** describe emergent substrate behavior; **4 concrete sweep axes** are the independently-controllable primitives in `build_rules` + `run_chain`: {STORAGE ∈ {SHARDED, BUNDLED}, N, F fan-out, mechanism}. Prior TOPOLOGY_FREE and ALGEBRA_SCALES_depth both alias to `F` (single param controlling perms/POS/sharded_codebook cardinality; verified off-disk at `_stage1_physics_law_joint_composition_factorial_v1_core.py:164`). Regime matrix therefore has C(4,2)=6 cross-terms, not C(5,2)=10. L (chain length) is a genuine 5th potential sweep axis but is FIXED at 2 across all Probes 1-11. See `math::META_regime_matrix_axis_aliasing_finding_v1_...2026_07_03` and `meta::META_axis_labels_map_to_substrate_primitives_..._discipline_v1_2026_07_03`.

**5 abstract physical-law atoms (each remains individually valid as claims about substrate behavior):**

1. **STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1** (2026-07-02) — sharded rule-storage FHRR chain regime
2. **STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1** (2026-07-02) — sharded vs bundled chain-depth
3. **SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1** (2026-07-02) — NOTE: "algebra" here = end-to-end M1.9/M1.10 roundtrip K=5, NOT the F fan-out that Probes 8/10 call "algebra"
4. **PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian** (M-sweep FULL 2026-07-03) — bipolar-codebook cleanup regime; **CG_META CONFIRMED via Probe 1 evidence**
5. **META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_PROMOTION_MM_TENTATIVE_to_CG_META_CONFIRMED** (2026-07-03) — extends #4 with regime-scope annotation

**Redundancy consequence (verified):** Probes 3, 6, 8 are regime-stratified replicates at F×mechanism cross-term (saturated vs non-sat vs cliff regime slices). Probes 5, 10 are regime-stratified replicates at STORAGE×F. Convergent-evidence framing "3 probes show mech-axis moderation" should be read as "F×mechanism replicated 3× across regime slices" — arguably STRONGER at that single cross-term, but NOT breadth across cross-terms.

Plus math CG atom:
- **MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP...** (2026-07-03) — first empirical measurement of regime-conditional cross-term

---

## STEP 10: THE INTUITIVE VERSION (per USER universal rule)

Today the substrate team spent one session doing what usually takes a week. We closed the retrieval-architecture arc (marginally) at real scale — the pipeline dense-search → PPR graph-walk → structural knowledge-graph filter → composition works end-to-end at the tested scope. We established a new physics-law axis about how storage strategy determines whether the choice of cleanup mechanism matters. We caught ourselves over-framing seven separate times, each caught by the independent auditor, and filed the pattern of each catch as a discipline rule so future sessions don't repeat them. We built the infrastructure fix that unblocks the real-scale test (which needs a 5-hour compute the user has to authorize once the tunnel to home is back). We started mapping the regime boundaries of the substrate's physics laws — proving that laws don't just compose universally, they have specific cross-term structure. The session hit its natural pause at a huge state of forward progress plus enough discipline-layer investment that future sessions should have less over-framing to correct.

The next session picks up here: the tunnel to remote needs re-authenticating (user action), then the queue re-fires the two dispatched full-scale tests plus starts the big compute build, and the two revival probes I authored locally SMOKE first, then FULL. If all goes well the "storage is uniquely the moderator" claim gets confirmed, we add a sixth physics-law axis, and the 170K real-scale retrieval test either validates the arc-closure at production scale or reveals a scale-dependent regime we didn't see.

---

## END OF FILE

## AMENDMENT 2026-07-03 19:40Z (CRITICAL FRAMING CORRECTION)

**Probe 6 v2 SMOKE landed HP with MAJOR finding that INVALIDATES the "STORAGE UNIQUELY MODERATES" thesis I was framing toward.**

At non-saturated regime (N=512 M=6400 corr=0.85), Probe 6 v2 shows:
- mech_var = 0.20 at F=1 AND F=16 (2× H1 threshold)
- Mechanism RANKING CROSSOVER across F: modern_hopfield leads at F=1 (0.85); soft_energy_attractor leads at F=16 (0.825)

**Revised understanding (cell-author informal MM_TENTATIVE atom at `notes/informal_diagnostic_H2_mechanism_degeneracy_non_saturated_sharded_fhrr_MM_TENTATIVE_2026-07-03.md`):**
- FAR from cliff (deep saturation): mechanism DEGENERACY holds
- NEAR cliff (mid-band mean_acc 0.30-0.95): mechanism DIVERGES AND ranking crossovers

**Implication for regime map:** Probe 1's STORAGE × CLEANUP_MECHANISM cross-term wasn't STORAGE being uniquely special — BUNDLED regime happens to be cliff-adjacent (low-accuracy) where mechanism variance can show. TOPOLOGY (Probe 6 v2) ALSO shows mechanism moderation at cliff-adjacent. Likely N moderates at cliff-adjacent too (Probe 7 pending).

**The composite CG_META claim I was framing "PHYSICS_LAW_STORAGE_UNIQUELY_MODERATES" is likely FALSE.** The real pattern is likely: "**ALL axes moderate CLEANUP_MECHANISM at cliff-adjacent regime; NONE moderate at deep-saturation regime**" — a much simpler and cleaner physics finding.

**Probe 1 CG_META still stands** (it's a real specific cross-term at BUNDLED regime), but its scope-annotation needs correction: not "STORAGE uniquely moderates" but "STORAGE × CLEANUP_MECHANISM cross-term in the BUNDLED cliff-adjacent regime."

**Files for next session:**
- Probe 6 v2 cell + prereg committed at 9d1995f81
- Informal MM_TENTATIVE atom at `notes/informal_diagnostic_H2_mechanism_degeneracy_non_saturated_sharded_fhrr_MM_TENTATIVE_2026-07-03.md`
- Probe 6 v2 needs FULL dispatch when Tailscale restored (73 pts × 3 seeds; expect ~15s each on GPU)
- Probe 7 v2 pattern (once landing): apply same cliff-adjacent regime discovery (N=512, corr=0.85, M=6400) not the original prereg's saturated regime

## AMENDMENT 2026-07-03 19:52Z (Probe 7 v2 CONVERGENT confirmation)

**Probe 7 v2 SMOKE HP with SAME empirical wall + finding as Probe 6 v2.** Committed `20d72dba6`.

**Two independent probes now converge on revised regime hypothesis:**
- Probe 6 v2 (TOPOLOGY × MECH at cliff-adjacent): mech_var = 0.20; ranking CROSSES OVER (modern wins F=1, soft wins F=16)
- Probe 7 v2 (N × MECH at cliff-adjacent): mech_var = 0.100 at N=2048; cliff N-dependent (smaller N cliffs first)

**Empirical convergence:** BOTH revival probes had to correct grids from the Plate-based prereg to (L≥4, corr≈0.90) — SHARDED FHRR chain composition is empirically 5-10× more robust than the Plate 0.14·N bound predicts. `META_saturation_floor_masks_null_variance_probe3_lesson`'s "corr≥0.6" revival criterion NEEDS AMENDMENT to "(corr near cliff ~0.90) AND (L≥4)" for SHARDED FHRR regime.

**Revised regime map hypothesis DOUBLY CONFIRMED (from 2 independent probes):**
- FAR from cliff (deep saturation): mechanism DEGENERACY holds
- NEAR cliff (mid-band mean_acc 0.30-0.95): mechanism DIVERGES

**The "STORAGE UNIQUELY moderates" thesis is FALSE.** Real pattern: **ALL axes moderate CLEANUP_MECHANISM at cliff-adjacent regime; NONE at deep-saturation.** Probe 1 (STORAGE × MECH at BUNDLED) still stands as CG_META but its scope-annotation must correct: it's a cross-term in the cliff-adjacent regime, not a universal STORAGE-specialness.

**Next session post-Tailscale-restore priority order (revised):**
1. Orchestrator push commits `20d72dba6` + `9d1995f81` (Probe 6+7 v2)
2. Dispatch Probe 6 v2 FULL + Probe 7 v2 FULL to overnight_queue GPU (3 seeds each, ~15s each on GPU per earlier probe wall)
3. Skunkworks landed-VET both — assess (a) does cliff-adjacent moderation reproduce at FULL 3-seed variance, (b) does mech ranking crossover reproduce, (c) file amended CG_META atom for regime-hypothesis "all-axes-moderate-at-cliff"
4. Amend `META_saturation_floor_masks_null_variance_probe3_lesson` per cell-author flag: cliff position is at corr≈0.90 AND L≥4 for SHARDED FHRR (not corr≥0.6 as originally filed)
5. Consider dispatching STORAGE × N (Probe 4) and STORAGE × TOPOLOGY (Probe 5) at cliff-adjacent regime too (previous SMOKEs were at ceiling+floor; need mid-band)
6. Continue original queue: Layer 0.5 FULL landing check, BGE 178K build, 170K scale re-test

**Composite CG_META atom candidate:** `PHYSICS_LAW_ALL_STAGE1_AXES_MODERATE_CLEANUP_MECHANISM_AT_CLIFF_ADJACENT_REGIME_v1` — pending Probes 6+7 FULL replication + STORAGE-pair-probes at cliff-adjacent regime.

## AMENDMENT 2026-07-03 20:29Z (Skunkworks VET corrections + 4 spawns in flight)

**Skunkworks landed-VET on Probes 6+7 v2 SMOKE (task ae76cfb6e241c7050) returned with 3 FIX#28 corrections:**

1. **"Plate 0.14×N 5-10× too pessimistic" was UNDERSTATED.** Actual gap is **20-90× at L∈{2,8}**. P6 (L=2 corr=0.85 N=512 M=6400) = 89× plate bound and still in-band mean_acc=0.73. Memory rule `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03.md` amended with corrected magnitude.

2. **"Cliff at corr≈0.90 AND L≥4" is NOT SUPPORTED.** Probe 6 v2 achieves non-saturated in-band at L=2, corr=0.85. My prior "L≥4 required" narrowing was over-specified. Memory rule amended. Cliff geometry undetermined without cross-L/cross-corr FULL sweep.

3. **P7 evidence THINNER than framed.** n_band_slices=1, single in-band cell (M=6400, corr=0.9, N=2048), single seed=7. The `H1_N_MODERATES_WHEN_NON_SATURATED` label reads as a general claim but rests on 1 cell only. Downstream cites MUST qualify.

**Tier verdicts (Skunkworks-authoritative):**
- Probe 6 v2 SMOKE → **HOLD (MM_TENTATIVE at best)** — SMOKE HP + crossover real signal, but n_seeds=1, no cv. FULL multi-seed required to promote.
- Probe 7 v2 SMOKE → **HOLD (MM_TENTATIVE_WEAK)** — n_band_slices=1. FULL multi-seed + ≥3 in-band N values required.
- Composite CG_META v1 → **NOT_READY** — requires FULL landings + cv on ≥2 axes.
- META saturation-floor v2 amendment → **NOT_WARRANTED** — current rule stands; no filing.

**Session cumulative unchanged: math=46, meta=42 (VET was audit-only, no substrate writes).**

**4 spawns FIRED in this pickup session (all within 5-agent budget):**

| agentId | role | task | status |
|---|---|---|---|
| `ae76cfb6e241c7050` | Skunkworks VET | Probes 6+7 v2 SMOKE landed-VET | **COMPLETE 20:29Z** (see above) |
| `a39a4c7aa07620699` | exp_dev | Probe 8 ALGEBRA × MECH at cliff-adjacent authoring | in flight |
| `a416f584633f92db0` | exp_dev | Probe 9 N × TOPOLOGY at cliff-adjacent authoring (first non-mechanism pair) | in flight |
| `a364bfa159e50a1f4` | Testbed | SH-4 double-prefix verify tooling fix | in flight |

**Framing correction to propagate:** ALL post-VET tier framings in my prior BACKUP amendments should defer to Skunkworks HOLD tier. The revised regime hypothesis "ALL axes moderate CLEANUP_MECHANISM at cliff-adjacent" remains DIRECTIONALLY plausible but is NOT SMOKE-promotable — awaits FULL multi-seed replication.

**Post-Tailscale action items (post-VET-updated):**
1. Push all local commits (9d1995f81, 20d72dba6, + Probe 8 + Probe 9 + Testbed SH-4 fix commits as they land)
2. Dispatch Probes 6+7 v2 FULL multi-seed (≥3 seeds) to overnight_queue GPU — needed for HOLD → promotion
3. Dispatch Probes 8+9 SMOKE outcomes (if HP local): each to FULL multi-seed
4. Do NOT propose composite CG_META atom until at least Probes 6+7 v2 FULL land with cv <0.15 and P7 has ≥3 in-band N values
5. Recovery orchestrator for Probes 4+5 FULL, BGE 178K cache build, 170K unified re-test

**Fix#28 cumulative today: 8 hits.** Discipline layer working — Skunkworks caught these before FULL dispatch. Both my initial magnitude framing AND cliff geometry claim were over-narrow. Directional intuition correct; magnitude precision needs FULL evidence.

## AMENDMENT 2026-07-03 20:36Z (Testbed SH-4 fix landed; Probes 8+9 SMOKE metrics on disk)

**Testbed SH-4 double-prefix verify tooling fix (task a364bfa159e50a1f4) COMPLETE:**
- Commit `70c9f6a5d` pushed to origin/main (Testbed pre-authorized per USER-locked rule)
- **Root-cause fix at `experiments/_seed_checkpoint.get_output_dir`** — normalizes `HDLAB_EXP_NAME` by stripping leading `exp_`, emits `[SH-4-normalize]` stderr warning, preserves legacy checkpoint continuity when `data/exp_exp_<anchor>/` already exists on disk
- **7 verify-tooling files patched** for double-prefix fallback: runner_status.py, healer.py, purge_pending_reruns.py, remote_state.py, dashboard/poller.py, scp_recover_landing.py (untracked; now added), + test_sh4_double_prefix_fallback.py (new smoke-test harness)
- verify_landing.py + landing_notifier.py + predispatch_check.py + audit_n_mismatch.py already handled double-prefix — no changes needed
- **46 legacy `data/exp_exp_*/` dirs on disk stay put; all verify tools now fall back**
- **Follow-on candidate:** `tools/queue_add.py` normalize at ship time → would eliminate runner-side normalization but requires queue-owner sign-off
- **3 pending queue entries begin with `exp_`** — will trigger `[SH-4-normalize]` warning on next dispatch (expected/informational)
- Fleet-process-health: 46 double-prefix dirs / 5469 total data/exp_* = **0.8% recurrence rate**
- Tests: SH-4 fallback 5/5, verify_landing 17/17, seed_checkpoint self-test PASS
- **The recurring Fix#28 SH-4 pattern is CLOSED AT ROOT CAUSE.** Future landings will be single-prefix; existing double-prefix landings verified via fallback.

**Probes 8+9 SMOKE data landed on disk (20:34-20:35Z; agents finishing reports):**
- Probe 8 ALGEBRA × MECH cliff-adjacent: `data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s7_smoke/metrics.json` (9300 bytes)
- Probe 9 N × TOPOLOGY cliff-adjacent: `data/exp_stage1_regime_probe_9_N_x_topology_non_saturated_v1_s7_smoke/metrics.json` (7298 bytes)
- Probe 9 cell committed at `0c5761c87` (before notification fired)
- Probe 10 STORAGE × ALGEBRA: still authoring
- Waiting for exp_dev notifications with structured verdicts + verdict/HP status

**Spawn state (updated):**

| agentId | role | status |
|---|---|---|
| `a364bfa159e50a1f4` | Testbed SH-4 fix | **COMPLETE** `70c9f6a5d` pushed |
| `a39a4c7aa07620699` | Probe 8 ALGEBRA × MECH | data on disk; awaiting exp_dev report |
| `a416f584633f92db0` | Probe 9 N × TOPOLOGY | data on disk; cell committed `0c5761c87`; awaiting exp_dev report |
| `a20d62a8213d64873` | Probe 10 STORAGE × ALGEBRA | authoring in flight |

**Session cumulative unchanged: math=46, meta=42** (Testbed infra work does not atomize; Probes 8+9 pending exp_dev reports before any atom filings).

## AMENDMENT 2026-07-03 20:48Z (Probes 8+9 exp_dev reports LANDED; all pushed to origin)

**Probe 8 ALGEBRA × MECH cliff-adjacent SMOKE HP** — commit `79fe2758d` pushed:
- `cliff_max_per_F_var_in_band = 0.20` (2× H1 threshold; well above)
- `mech_ranking_crossover = True` (F=1: mh>sea>ic; F=16: sea>ic>mh — MH↔SEA swap)
- `h3_null_fires = True` (deep_max_var=0.0 <0.05; mechanism DEGENERACY at DEEP_SAT confirmed)
- Empirical cliff-bracket BEFORE prereg: corr=0.85, L=2 validated (contradicts my earlier "L≥4 required" narrowing)
- Design refinement: added F=2 interstitial (Probe 6 v2 missed it), cardinality 25 FULL / 10 SMOKE
- Novel per substrate-KB query (top hit cosine ≤0.41)

**Probe 9 N × TOPOLOGY (F) cliff-adjacent SMOKE HP** — commits `0c5761c87` + `8f63ac421` pushed:
- 5/5 SMOKE HP; cardinality OK; SATURATION_PC pass; escapes_saturation_ceiling_smoke=True
- **hyp_preview = H2 (NULL — structurally separable at endpoints):** per-F mean 0.5125 at F=1 AND F=16; N × F cross-term = 0.0 at SMOKE endpoints (N=256 floor + N=2048 ceiling only)
- **Cell-author self-caught discriminator flaw mid-SMOKE:** original H1 gated on `max_N_var_in_band` (marginal), corrected to gate on `topology_var_range_across_N` / `N_var_range_across_F` / `max_N_x_F_deviation` (proper interaction metrics). Commit `8f63ac421`.
- **Skunkworks caveat flagged by cell-author:** `n_band_slices=2` is fluke — comes from per-F mean=0.5125 (average of floor+ceiling), NOT any individual (N,F) cell in-band. FULL grid provides real in-band cells at intermediate N ∈ {512, 1024}.
- Novel per substrate-KB (cosine=0.2715 < 0.30 threshold)

**Convergent-evidence framing (SMOKE-level; NOT arc-closure per Skunkworks discipline):**
- 3 probes (P6 TOPOLOGY×MECH, P7 N×MECH, P8 ALGEBRA×MECH) at cliff-adjacent all show mech_var ≥ 0.10 (0.20, 0.10, 0.20) + ranking dynamics
- 1 probe (P9 N×TOPOLOGY non-mechanism pair) at SMOKE endpoints shows H2-null preview (structurally separable) — CONSISTENT with "moderation is on mechanism axis, not on non-mechanism pair"
- Composite CG_META candidate remains NOT_READY per Skunkworks — FULL multi-seed cv <0.15 required
- **Directional signal is now 4-probe strong at SMOKE.** Awaits Probe 10 STORAGE × ALGEBRA + FULL replication before atom filing.

**Push state (all local commits now on origin/main):**
- `70c9f6a5d` Testbed SH-4 fix
- `79fe2758d` Probe 8 cell + prereg
- `0c5761c87` + `8f63ac421` Probe 9 cell + discriminator-fix
- `9d1995f81` + `20d72dba6` Probe 6 v2 + 7 v2 (already pushed pre-session)
- `111a24a5a` + `11682c3df` + earlier BACKUP amendments
- HEAD at `8f63ac421` (as of 20:48Z)

**Spawn state:**
- Only Probe 10 still authoring (`a20d62a8213d64873`)
- Will fire Skunkworks composite VET on 6+7+8+9 SMOKE ensemble once Probe 10 lands

## AMENDMENT 2026-07-03 20:55Z (Skunkworks composite VET — Fix#28 hits #9-#11)

**Skunkworks composite VET on Probes 8+9 SMOKE + 4-probe convergent framing (task aabcdafc7f1431a55) COMPLETE.**

**Off-disk verify OK:** All Probe 8 + Probe 9 cell-author claims reproduced via independent .venv Python. SH-4 root-cause normalization working (single-prefix only, no double-prefix dups).

**HOLD verdicts (both):**
- Probe 8 → HOLD. Cardinality/machinery pass. Ranking crossover directionally novel. But n_seeds=1 at TR=40, binom SD≈0.072 → 0.20 spread is only **~2.8σ from 1 seed**. Cross-seed cv unavailable. Arc-continuation ≠ arc-closure. **NO atom filed.**
- Probe 9 → HOLD_SATURATION_VACUOUS_PREVIEW. `main_grid_n_in_non_saturated_band = 0/4` (N=256 floor, N=2048 ceiling; neither individual cell in [0.30, 0.95] band). "cross-term=0.0" is TRIVIALLY TRUE because both endpoints pinned. `n_band_slices=2` is per-F-mean averaging artifact (fluke, as cell-author self-caught). SMOKE grid unusable for hyp assessment. **NO atom filed.**

**Fix#28 hits #9-#11 on my Director framing:**

**#9 — "cliff-adjacent regime" is LOSSY abstraction** (per `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03`):
- P6+P8 share CLIFF signature (N=512, M=6400, corr=0.85)
- P7 lives at DIFFERENT signature (N=2048, corr=0.9, L=8)
- P9 lives at ANOTHER signature (N∈{256,2048}, F∈{1,16}, L=4, corr=0.85; endpoint-only)
- Composite label `PHYSICS_LAW_ALL_STAGE1_AXES_MODERATE_CLEANUP_MECHANISM_AT_CLIFF_ADJACENT_REGIME_v1` **DENIED** — over-abstracts across regime-mismatched configs

**#10 — "4-probe convergent" INFLATES:**
- P9 is saturation-vacuous SMOKE, therefore SILENT (neither confirmatory nor denying) about the mech-axis moderation hypothesis
- My "H2-null preview CONSISTENT with moderation on mech axis only" was INFLATION — P9 provides ZERO signal at SMOKE
- Corrected count: at SMOKE, P6+P7+P8 give directional signal on mech-axis moderation at their OWN signatures; P9 is silent

**#11 — Composite promotion UNSUPPORTED at any tier at SMOKE:**
- All 4 probes single-seed SMOKE (no cv, no FULL)
- Best case honest framing: narrow MM_TENTATIVE for P6+P8 SHARED-signature (both at N=512 M=6400 corr=0.85) — even that requires cross-seed cv before promotion

**Skunkworks-provided BEST HONEST FRAMING (adopt as canonical):**

> "P6+P8 (shared CLIFF-N512-M6400-corr0.85 regime) both show mech-axis spread ≥0.10 at SMOKE with intriguing single-seed ranking-crossover in P8. P7 (different regime N=2048, corr=0.9, L=8) shows mech-axis moderation at ITS OWN signature. P9 (non-mech pair, saturation-vacuous SMOKE grid) HOLD pending in-band FULL. Each cited by source signature; no cross-regime collapse."

**FULL dispatch readiness (post-Tailscale — Skunkworks-authoritative):**
- **P8:** MULTI-SEED FULL essential — 5 seeds {7,11,13,17,19}, ~125s/seed, 15-min timeout. Must confirm ranking crossover holds across seeds (load-bearing novel claim).
- **P9:** MULTI-SEED FULL with in-band N ∈ {512, 1024} essential (SMOKE grid unusable). 5 seeds, ~100s/seed, 15-min timeout.
- **P6+P7:** also need multi-seed FULL (prior VET filed MM_TENTATIVE).
- Bundle all 4 in overnight_queue; sequential or batched (memory footprint small).

**Session cumulative unchanged: math=46, meta=42.** Cert delta this VET: ZERO. Two HOLDs recorded. No commit.

**Fix#28 cumulative today: 11 hits.** Directional intuition on mech-axis moderation at cliff-adjacent remains plausible; magnitude/scope/composability precision requires FULL evidence + source-signature discipline.

## AMENDMENT 2026-07-03 21:00Z (Probe 10 SMOKE HP landed; last spawn complete)

**Probe 10 STORAGE × ALGEBRA cliff-adjacent SMOKE HP** — commit `51b787ba7` pushed:

**3 empirical findings (all MM_TENTATIVE per cell-author's own discipline):**
1. **STORAGE main effect is HUGE at cliff:** SHARDED-vs-BUNDLED gap = **0.575 (F=1) to 0.655 (F=16)**, MECH-independent. Storage physics dominates.
2. **STORAGE × ALGEBRA cross-term is WEAK (~0.075)** — MIDDLE_BAND between H2=0.05 and H1=0.10; leans toward H2 (independence). F fan-out has similar (small) amplification at both storages.
3. **STORAGE regimes are NON-SUPERIMPOSABLE** — no single (N, M, corr) config saturates BOTH storages simultaneously. BUNDLED at DEEP_SAT (N=8192, M=800, corr=0.60) floors at 0.075 while SHARDED saturates at 1.0. DEEP_SAT gate was relaxed to SHARDED-only during SMOKE iteration; BUNDLED reported informationally.

**Design flags for FULL (cell-author-caught):**
- BUNDLED cliff at modern_hopfield may not have an in-band single-cell point at any tested (N, M, corr)
- Consider (a) BUNDLED FULL re-bracket to lower M or different N/corr axis, OR (b) accept CLIFF_BUNDLED as informational-only floor-arm, OR (c) switch BUNDLED arm to iterative_cosine mechanism (which does saturate at PC regime)
- s13/s19 sibling wrappers needed for 3-seed FULL

**Prior-work check (cell-author):** top substrate_query cosine=0.285 ("Bundle storage") — BELOW 0.30 novelty threshold. Genuinely novel arc-continuation (closes STORAGE column of pairwise regime matrix alongside Probes 4+5).

**Skunkworks VET queued** — will assess (a) STORAGE main effect claim (0.575-0.655 gap at cliff) via independent recompute, (b) cross-term=0.075 middle-band interpretation, (c) non-superimposable regime finding, (d) FULL dispatch design constraints.

**Spawn state: ALL COMPLETE at 21:00Z.** 5 spawns fired this pickup, all returned:
- Testbed SH-4 fix (COMPLETE 20:24Z; pushed `70c9f6a5d`)
- Skunkworks VET 1 (Probes 6+7 v2) (COMPLETE 20:29Z; 3 Fix#28 hits filed)
- Probe 8 ALGEBRA × MECH (COMPLETE 20:48Z; pushed `79fe2758d`)
- Probe 9 N × TOPOLOGY (COMPLETE 20:48Z; pushed `0c5761c87` + `8f63ac421`)
- Skunkworks VET 2 composite (COMPLETE 20:55Z; 3 more Fix#28 hits filed)
- Probe 10 STORAGE × ALGEBRA (COMPLETE 21:00Z; pushed `51b787ba7`)

**Session cumulative unchanged: math=46, meta=42** (all probes at HOLD tier; no atom filings from any of the SMOKE landings).

**Ready-to-fire post-Tailscale queue (updated with Probe 10):**
- **P8:** FULL 5 seeds ~125s/seed (confirm ranking crossover across seeds)
- **P9:** FULL 5 seeds ~100s/seed (in-band N ∈ {512, 1024})
- **P6+P7 v2:** FULL 3+ seeds (prior VET filed MM_TENTATIVE)
- **P10:** FULL 3 seeds w/ BUNDLED cliff re-bracket or scope-narrowed arm
- Bundle overnight_queue GPU; sequential or batched
- Recovery: Probes 4+5 FULL + BGE 178K cache build + 170K unified re-test

## AMENDMENT 2026-07-03 21:15Z (Skunkworks VET Probe 10 — FIRST ATOM FILINGS of pickup session)

**Skunkworks VET Probe 10 (task ad6b2b43cb9d4ef08) COMPLETE at commit `26d0f99ea`:**

**2 atoms filed via A5-gated PartitionedStore write:**
1. **Math atom #47:** `T3/EXP_stage1_regime_probe_10_storage_x_algebra_smoke_v1` → **MM_TENTATIVE_MIDDLE_BAND**
   - Composes: sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1, Probe 1 CG_META, META_saturation_floor_masks_null_variance_probe3
2. **Meta atom #43:** `META_cross_term_measurement_requires_both_arms_in_band_probe10_v1` → **MM_STANDARD**
   - Extends floor-vacuity rule to cross-term measurement generally: "BUNDLED_BRACKET M∈{100,400,800}={0.20,0.025,0.025} — NO in-band point exists at (N=2048, corr=0.20) tested grid"

**Session cumulative: math=47, meta=43 = 90 atoms today** (up from 88; first filings this pickup session).

**Fix#28 hits #12-#14 (14 total today):**
- **#12:** Cross-term=0.075 is NOISE-INDISTINGUISHABLE at 1 seed (z=0.63 vs binom SD 0.12); "leans H2 (independence)" tea-leaf reading NOT SUPPORTED at SMOKE — only 3-seed FULL can discriminate.
- **#13:** STORAGE main effect (0.575, 0.65) is REAL (z >5) but partly **FLOOR-vacuous** — measures SHARDED-in-band vs BUNDLED-at-floor. Not pure cross-term. Substantially RESTATES prior `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`. My "huge STORAGE main effect" framing over-inflated novelty.
- **#14:** "Non-superimposable STORAGE regimes" is real observation but a RESTATEMENT of storage capacity gap, not a new discovery warranting its own atom. Folded into existing atom's `framing` field.

**Scientifically correct FULL dispatch design (Skunkworks-authoritative):**
- **BUNDLED re-bracket at LOWER corruption** (corr=0.05-0.10) to bring BUNDLED cliff in-band, then re-run SMOKE before FULL
- **DO NOT dispatch FULL against floored BUNDLED arm** — "cross-term" would be uninterpretable (this is EXACTLY the floor-vacuity META rule just filed)
- If no (N, corr, M) combo brings BUNDLED cliff in-band without invalidating matched-cliff comparison: MECHANISM SWITCH or **SKIP Probe 10 FULL entirely** — STORAGE column already covered by prior atoms + Probes 4+5 FULL

**Novelty:** substrate_query cosine=0.254 (< 0.30 novelty threshold passes) but semantically composition-adjacent to prior work. Cross-arc overlap: Bundle_storage 0.254, set_algebra_bundle_cpu_v1 0.225, sharded_fhrr_cleanup_capacity family adjacent.

**Updated post-Tailscale queue (Skunkworks-corrected):**
- P6+P7 v2 FULL: dispatch as planned (multi-seed)
- P8 FULL: dispatch as planned (5 seeds; confirm ranking crossover; load-bearing novel claim)
- P9 FULL: dispatch with in-band N ∈ {512, 1024} (SMOKE grid unusable)
- **P10 FULL: DEFER + re-SMOKE with BUNDLED corr=0.05-0.10 first, OR skip entirely** (Skunkworks flagged both as scientifically valid)

**Discipline pattern this session:** 14 Fix#28 catches; 2 atom filings. High correction-to-filing ratio (7:1) reflects that today's landings are directionally interesting but not yet arc-closing. Skunkworks working exactly as designed.

## AMENDMENT 2026-07-03 21:30Z (STRUCTURAL DISCOVERY — axis-aliasing catches Fix#28 hit #15 BEFORE ship)

**Probe 11 TOPOLOGY × ALGEBRA exp_dev (task a0ffe8d16d04174b0) REFUSED TO SHIP with STRUCTURAL BLOCKER.**

**Finding:** TOPOLOGY and ALGEBRA are ALIASED in substrate primitives — both map to the same F parameter (sharded DAG fan-out). Substrate exposes 4 distinct CG_META SWEEP axes {STORAGE, N, F, CLEANUP_MECH}, not 5. Pairwise matrix is C(4,2)=**6, not C(5,2)=10**.

**Aliasing map (grep-verified across 6 cell cores by exp_dev):**
- Probe 3 (line 91): "TOPOLOGY axis: fan-out F in the sharded DAG"
- Probe 5 (lines 102-104): "F (fan-in / TOPOLOGY) axis"
- Probe 6 (line 93): "TOPOLOGY axis: fan-out F"
- Probe 8 (line 145): "Primary axis: F fan-out (ALGEBRA in this cell)"
- Probe 9 (line 137): "TOPOLOGY axis (F fan-out). Matches Probe 6 F grid."
- Probe 10 (line 143): "ALGEBRA (F fan-out) axis"

**Consequence:** Probes 3 ≡ 6 ≡ 8 test the SAME cross-term (F × CLEANUP) up to F-grid resolution; Probes 5 ≡ 10 test SAME cross-term (STORAGE × F). Would have been Fix#28 hit #15 if Probe 11 had shipped (bogus H2-pass via SAME-AXIS-COLLAPSE, not genuine independence).

**Regime matrix ACTUALLY COMPLETE at 6 pairs:**

| Pair | Probes | Status |
|---|---|---|
| STORAGE × N | 4 | SMOKE HP |
| STORAGE × F | 5, 10 | SMOKE HP (replicates) |
| STORAGE × CLEANUP | 1 | **CG_META CONFIRMED** |
| N × F | 9, 9v2 (in flight) | SMOKE HP (endpoints); P9v2 tests in-band L/N_cliff sweep per research |
| N × CLEANUP | 2, 7v2 | SMOKE HP (saturation-vacuous → v2) |
| F × CLEANUP | 3, 6v2, 8 | SMOKE HP (replicates) |

**Director decision (adjudicated):** PATH 1 — recognize matrix COMPLETE at 6, atomize the axis-aliasing finding. Path 2 (author distinct TOPOLOGY primitive like locality-preserving vs random-uniform IMPL permutation family) is different-arc R&D work; not scheduled.

**Skunkworks structural VET fired (task afadd5dbd43055cf1):** verify aliasing off-disk + reassess whether the "5 CG_META physical-LAW atoms" listed in Step 9 remain valid (they describe abstract laws, not sweep axes — distinct concept). File math atom `META_regime_matrix_complete_at_6_pairs_not_10_axis_aliasing_v1` + meta atom `META_axis_labels_must_map_to_substrate_primitives_not_theoretical_concepts` if warranted.

**Impact on today's convergent-evidence framing:**
- My earlier "3 probes convergent on mech-axis moderation at cliff-adjacent" (P6+P7+P8) partially collapses to "F×CLEANUP replicated 3× at similar signature (P3+P6+P8) + N×CLEANUP replicated 2× (P2+P7v2)."
- Skunkworks already flagged in earlier VET: "P6+P8 share CLIFF-N512-M6400-corr0.85 regime" — the reason they share the regime is BECAUSE they're testing the same axis pair (F × CLEANUP).
- **True 4-axis convergent evidence at cliff-adjacent:** F×CLEANUP replicates (P6v2+P8) both show mech_var ≥0.10; N×CLEANUP (P7v2) shows moderation at own signature. That's 2 pairs, not 3 axes.

**5 CG_META physical-LAW atoms remain valid as ABSTRACT LAWS about substrate behavior:**
- These describe emergent properties (scale-free, topology-free, algebra-scales, storage-strategy, cleanup-M-scaling)
- Distinct from concrete SWEEP AXES in build_rules (which are 4: STORAGE, N, F, CLEANUP_MECH)
- Framing correction: BACKUP Step 9's "5 CG_META axes" should read "5 CG_META physical-LAW atoms about the 4 substrate sweep axes"

**Session cumulative unchanged: math=47, meta=43 = 90 atoms** (Probe 11 refused to ship; no compute wasted; discipline WORKED).

**Fix#28 today: 14 hits recorded + 1 AVOIDED via structural discipline (P11 pre-ship refusal). Discipline layer has evolved from post-hoc correction to pre-hoc prevention.**

**Spawn state (3 in flight):**
- P10 v2 re-SMOKE with BUNDLED corr=0.05-0.10 (a7808cd4d2fe53f16)
- NEG1 follow-up P9 v2 with L/N_cliff sweep, research-recommended (a65fbcfda40db8b24)
- Skunkworks structural VET on axis-aliasing (afadd5dbd43055cf1)

## AMENDMENT 2026-07-03 21:45Z (Skunkworks BUNDLED VET filed 2 more atoms; tally 94)

**Skunkworks VET on P10 v2 BUNDLED bimodal physics finding (task a15d50b89be3f7b5f) COMPLETE.**

**2 atoms filed (A5-gated):**
- **Math (MM_STANDARD):** `EMPIRICAL_BUNDLED_FHRR_CHAIN_COMPOSITION_L2_F1_FIRST_ORDER_TRANSITION_NO_MIDBAND_v1` — theory-confirmed via AGS 1985 + Krotov-Hopfield 2016 + Ramsauer 2020
- **Meta (MM_TENTATIVE):** `META_when_cross_term_bracket_search_exhausts_design_space_file_HONEST_NO_MATCHED_CLIFF_and_SKIP_FULL_v1` — extends atom #43

**Session cumulative: math=49, meta=45 = 94 atoms today (+6 this pickup, +2 from this VET alone).**

**New meta rule (discipline extension):** when re-bracket search PROVES no in-band arm exists across reasonable design space (100+ phase points × multi-seed × multi-TR), the disciplined action is:
1. File HONEST_NO_MATCHED_CLIFF
2. SKIP FULL
3. Atomize bracket-exhaustion as boundary observation
4. Verify complement-arm sanity
**Do NOT dispatch confounded FULL to "recover spent compute."**

**Composition:** EXTENDS `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` — parent claims BUNDLED collapses at L≥2; new atom adds "no mid-band even at L=2 F=1" characterization. Parent + extension together characterize BUNDLED capacity boundary geometry.

**CERT delta this VET:** CG +0, MM_STANDARD +1, MM_TENTATIVE +1. No demotions.

**Director SKIP decision on P10 v2 FULL: CONFIRMED SCIENTIFICALLY CORRECT.** STORAGE column covered by P1 CG_META + Probes 4+5 FULL when Tailscale restores. Option R3 (SHARDED-only F sweep) would be partial single-arm measurement, not cross-term. Route attention to Probes 4/5 FULL VETs when they land + Probe 1 CG_META regime-cross-term promotion arc.

**Also fired (main-thread action while VET returning):** Probe 12 L-marginal effect sweep at SHARDED cliff-adjacent (aca2f567b885d62f7) — tests the newly-identified 5th untested axis. L∈{1,2,4,8,16} at N=512 M=6400 corr=0.85 F=1. If HP: L IS a real 5th sweep axis; today's "matrix complete at 6" gets revised. If HF: L is inert atomizable negative.

**Spawn state UPDATED (2 in flight):**
- NEG1 follow-up P9 v2 L/N_cliff sweep (a65fbcfda40db8b24)
- Probe 12 L-marginal-effect sweep (aca2f567b885d62f7)

**Fix#28 today:** 14 hits recorded, 2 hits AVOIDED via pre-hoc structural discipline (P11 refusal + P10 v2 refusal). Discipline evolution: post-hoc correction → pre-hoc prevention CONFIRMED WORKING.

## AMENDMENT 2026-07-03 21:55Z (Skunkworks VET P9 v2 caught Fix#28 hit #15 on my "novel signal" framing)

**Skunkworks VET on P9 v2 (task ac08eb86507b67812) COMPLETE. NO atom filed. Session tally UNCHANGED at 94.**

**Fix#28 hit #15 — "novel signal" narrative over-reach:**
- I framed P9 v2 as "highest-value SMOKE landing with novel non-monotonic L effect"
- Skunkworks disk-verify: SMOKE observation is max|dev|=0.0687 in NOISE BAND (not the 0.162)
- SMOKE only tested L∈{2, 16} — you cannot have "non-monotonic peak at L=8" from that
- The 0.162 residual + non-monotonic peak language came from `bracket_verify` SCRATCHPAD prior (which tested L∈{2,4,8,16} at 3-seed TR=100)
- Do NOT carry "non-monotonic-peak" narrative into FULL dispatch prompt as if SMOKE evidenced it
- Cite bracket_verify EXPLICITLY as the source of that pattern, not SMOKE

**Skunkworks-authoritative correct framing:**
> "SMOKE HP with clean gates + SATURATION_PC sanity + SHARDED positive control at N=2048 M=10 corr=0.10 F=1 modern_hopfield BUNDLED. Bracket_verify scratchpad (L∈{2,4,8,16} 3-seed TR=100) shows suggestive non-monotonic pattern at L=8 (0.65 vs 0.37, 0.47, 0.59) with max|additive residual|_in_band=0.162 exceeding H1 top-bucket threshold 0.15. FULL is the decisive test; H2 vs H1 vs MIDDLE_BAND fork resolves at 3-seed TR=100 with full 3×4 L-grid at this signature."

**Tier at SMOKE:** HOLD (implicit; no atom warranted). FULL required to promote.

**Fix#28 today CUMULATIVE: 15 recorded hits + 2 pre-hoc avoided = 17 total discipline interactions.** Discipline layer catching framing errors at every stage.

**Spawn state (1 in flight):**
- Probe 12 L-marginal-effect sweep (aca2f567b885d62f7) — Skunkworks-flagged untested 5th potential axis

## AMENDMENT 2026-07-03 22:05Z (P12 Skunkworks VET → Fix#28 hit #16; ALL SPAWNS COMPLETE)

**Skunkworks VET P12 (task a5ad6545eb12c11f0) COMPLETE. HOLD. No atom filed. Session tally unchanged at 94.**

**Fix#28 hit #16 — "L is 5th CG_META axis" framing:**
- Skunkworks disk-verify + concept-query: **chain-depth L is ALREADY atomized as CG_META at atom #3** `SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1` (M1.9/M1.10 K=5 roundtrip)
- P12 is REGIME-EXTENSION of atom #3 to (sharded FHRR, cliff-adjacent, F=1, TR=40); NOT discovery of new axis
- Cell-author's "L is genuinely distinct 5th CG_META axis" framing DOWNGRADED

**Additional catches:**
- L=1→L=16 spread of 0.875 is **theory-trivial** (SNR decays geometrically with chain hops per Amit-Gutfreund-Sompolinsky + Plate). Band-only spread 0.45 (L=1→L=4) is the SUBSTANTIVE signal
- SMOKE-vs-scratchpad bracket DIVERGENCE (mh L=1 shifts 0.950→0.875 SMOKE) — seed-sensitivity real, not point-wise reproducing
- Concept-overlap flagged at cosine 0.31-0.36 with `T3/EXP_q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048` (2026-06-04 α × L sweep MIDDLE_BAND; chain_depth_max(alpha)=22/(0.302-alpha)) — prior chain-depth work exists

**Corrected framing (Skunkworks-authoritative):**
> P12 SMOKE HP is a REGIME-EXTENSION test of atom #3 to sharded FHRR cliff-adjacent regime. L moderates capacity at MM_TENTATIVE strength. Theory-consistent (AGS + Plate). NOT a new axis discovery.

**Regime matrix atom #48 REMAINS VALID with addendum:** "matrix is L=2 slice; L cross-terms (L×N, L×F, L×M, L×corr) unmapped."

**Tier: HOLD.** Do NOT file atom at SMOKE per arc_continuation_vs_arc_closure discipline.

**Post-FULL atom candidate (only fileable after 3-seed FULL confirms):** `EMPIRICAL_L_MODERATES_CAPACITY_AT_SHARDED_CLIFF_ADJACENT_v1` → MM_STANDARD, COMPOSES atom #3, REGIME_EXTENSION classification.

**FULL dispatch spec (Skunkworks-authoritative):**
- 3 seeds essential (SMOKE-vs-bracket divergence proves seed-sensitivity)
- Full L-grid {1,2,4,8,16}: L=2, L=8 gap-fill needed
- BUNDLED arm NOT needed for this question; L cross-terms are FOLLOW-ON
- TR=100 (2SD drops to ~0.10 at p=0.5 → band-only spread 0.45 = 4.5× 2SD)
- Frame as REGIME_EXTENSION of atom #3, NOT axis discovery

**ALL SPAWNS COMPLETE. 0 in flight.**

**Fix#28 today CUMULATIVE: 16 recorded + 2 pre-hoc avoided = 18 total discipline interactions.**

**Final session tally: math=49, meta=45 = 94 atoms today (+6 this pickup).**

**Pickup session summary (18:55Z → 22:05Z, ~3.2 hours wall):**
- Spawns fired: 12+ (Testbed SH-4 + 3 Skunkworks VETs on Probes 6+7 v2 / P8+P9 / P10 / P11 structural / BUNDLED / P9v2 / P12 + Research 2x-drill + team lead + Probes 8-12 authoring + P10 v2 + P9 v2)
- Atoms filed: 6 (all via Skunkworks A5-gated writes on VET landings)
- Fix#28 discipline: 16 recorded + 2 avoided = 18 interactions
- Structural discoveries: axis-aliasing (TOPOLOGY/ALGEBRA = F fan-out); L is real substrate primitive orthogonal to F but already CG_META-covered
- Regime matrix status: 6-pair matrix all SMOKE-covered; 1 CG_META, 5 HOLD-pending-FULL, 1 (P10 v2) SKIP HONEST_NO_MATCHED_CLIFF
- Retrieval architecture arc: maintained marginal closure (Exp 3E FULL from prior session)
- K-parameter arc: RESOLVED (K is derived/coupled, not 6th axis)
- Blocker: Tailscale on marsh@home; entire FULL dispatch bundle spec'd and queued awaiting
