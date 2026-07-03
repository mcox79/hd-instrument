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

## STEP 2: IN-FLIGHT SPAWNS AT COMPACTION TIME

| agentId | role | what | expected |
|---|---|---|---|
| `a4f83923fa23b6b28` | hdi_exp_dev | Probe 6 non-saturated TOPOLOGY × MECH revival — SMOKE local | HP with confirmation grid is non-saturated (mean_acc in [0.30, 0.95]) |
| `a9ac5b62777c16c18` | hdi_exp_dev | Probe 7 non-saturated N × MECH revival — SMOKE local | HP with confirmation grid is non-saturated |

Both use higher M (up to 6400) + higher corruption (up to 0.70) + wider F/N ranges to force accuracy off the ceiling that made Probes 2+3 saturation-vacuous.

Task-notifications will arrive automatically. Landing pane at `data/latest_landings.md` will auto-refresh.

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

## STEP 9: 5 STAGE 1 CG_META PHYSICS-LAW AXES (regime-scoped)

1. **STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1** (2026-07-02) — sharded rule-storage FHRR chain regime
2. **STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1** (2026-07-02) — sharded vs bundled chain-depth
3. **SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1** (2026-07-02)
4. **PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian** (M-sweep FULL 2026-07-03) — bipolar-codebook cleanup regime; **CG_META CONFIRMED via Probe 1 evidence**
5. **META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_PROMOTION_MM_TENTATIVE_to_CG_META_CONFIRMED** (2026-07-03) — extends #4 with regime-scope annotation

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
