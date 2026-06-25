# CRITICAL CONTEXT — pre-compaction survival 2026-06-24 (v2 POST-5CELL-RESCUE)

Read this FIRST after compaction to recover session state.

## SUBSTRATE-PRODUCT STORY

Substrate is MEMORY + COMPOSITION + RETRIEVAL + AUDIT device. NOT a statistical LM competitor. Brain is the existence proof. Stages: 1 base → 2 optimize → 3 higher functions → 4 LM equivalence. Don't skip.

## 2026-06-25 12:45 POST-COMPACT SNAPSHOT — Barrier 1 DOUBLE-NEGATIVE + CERT 591

### CERT 594 (Cell 2 v5 atomization + pointer-chain v2 HARD_FAIL + META_M6 landed)
- math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE — chain_grade (FREQ_ROUTED_DEEPER 1st Stage 2 architectural win; 5 seeds + cross-N replication + n_steps plateau)
- meta::META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION — cert-neutral meta
- math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL — honest_negative cert-neutral
- meta::T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells — cert-neutral meta
- Cert-ladder rule sets now codified:
  - DEFINITIVE upgrade criteria: PROSPECTIVE_BANDS_FRESH_SEEDS + CROSS_N_REPLICATION
  - Rail-discipline 3-rule set: M2_referent_match + M5_chain_match + M6_derivation_provenance
- Director Fix #28 violation #9 caught by Skunkworks: smoke-vs-full META mis-attributed to n_chains alone; actual 3-dimension regime confound (N + n_chains + n_seeds). DEFERRED, not atomized.

### Cert-trail back-fill tasks (next Skunkworks cycle)
1. Consolidation v3 HARD_FAIL — ruling note exists `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md` but never atomized
2. META_M4 + META_M5 — ledger rows exist but atoms.jsonl entries missing (atom-write step skipped in prior cycle)

### IN-FLIGHT (verified via remote logs 12:40)
- Cell 2 v6 SEGREGATED_DUAL_W: GPU runner, started 12:08 PDT, ~30min in (no DONE yet)
- Cell 6 v3 lock_in: remote CPU runner, started 11:44 PDT, ~55min in, partials at seeds 7+17 (last update 12:20)
- Cell H' v2b NO_FOLDIAK: queued behind Cell 6; will dispatch when runner frees
- Skunkworks NEXT batch: pointer-chain v2 + META_M6 + smoke-vs-full META (need fresh spawn; prior agent terminated after ack)

### POST-COMPACT LANDINGS PROCESSED
1. **Pointer-chain v2 BASELINE_RAIL_FIXED → HARD_FAIL** (smoke +52% misled). Full: BASELINE=0.650 ✓ (rail fixed) but POINTER_2HOP=0.4250 (HURTS by -22 pts), depth-retention BREAKS (5hop=0.122, 10hop=0.035). cv=0.107 fails HP_cv. **Barrier 1 multi-hop FAILED via consolidation AND pointer-chain — both substrate-native multi-hop mechanisms refuted.** Awaiting Skunkworks tier-rule.
2. **2x drill on Consolidation v3 landed** — 3 load-bearing findings: (a) NAIVE-rail drift fully decoded (different V_P/n_chains regimes; pre-reg copied band without re-deriving = META_M6); (b) consolidation HURTS heldout EXPECTEDLY (compound atoms add crosstalk; same channel for both NAIVE+CONSOL → strictly degrades heldout); (c) brain analog mis-applied (substrate tests episodic consolidation; brain "always helps" requires SEMANTIC consolidation under feature-share + separate W matrices). Recommendation: **abandon compound-predicate consolidation as Barrier 1 closer; pivot to encoder-side / Wave D anisotropic; hold semantic-consolidation for future feature-share cell**.
3. **Cell 2 v5 atomization complete** (Skunkworks; CERT 590→591; META cert-ladder codified)

### STRATEGIC SYNTHESIS FILED
`notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md` — what substrate-product IS post-double-negative (3 options: A=2-hop ceiling final; B=Wave D encoder; C=semantic consolidation). Pre-committed interpretation rules for Cell H' v2b + Cell 2 v6 landings. Next-cell triage matrix.

### NEXT-UP SKUNKWORKS WORK (queue after Cell 2 v5 atomization lands)
- **HARD_FAIL atom** for pointer-chain v2 (Barrier 1 negative; substrate cannot escape multi-hop via either consolidation OR pointer-chain hybrid; load-bearing for L2 pivot to encoder)
- **META_M6 atomization**: NAIVE-baseline-must-be-derived-from-current-regime-not-copied-from-prior-cell (recurring rail-mis-spec across consolidation v3 + pointer-chain v2 + freq-routing v2)
- **+1 HARD_FAIL atom** for the smoke-vs-full Director Fix #28 violation: smoke at small chain count showed POINTER=0.98 +52% lift; full at production count showed POINTER=0.425 -22% loss. Smoke methodology insufficient for chain-count-sensitive mechanisms. Add discriminator to smoke harness: any mechanism whose lift depends on n_chains MUST smoke at chain_count >= 100 not 10-20.

### Strategic implication (post double-negative)
Barrier 1 multi-hop closure is OPEN as a substrate-native problem and NEITHER substrate primitive (compound-predicate consolidation, pointer-chain hybrid) can close it at production scale. Pivot lanes:
- **(A) Wave D anisotropic encoder** — does the codebook need geometric structure (NOT label-based per Principle O, but emergent like DeepWalk/Olshausen)? Cell H' v2b in flight tests this at production V scan {200, 1000, 4000, 10000}.
- **(B) Semantic consolidation via separate W matrices** — different cell entirely; needs feature-share extraction primitive. Defer.
- **(C) Accept Barrier 1 as permanent ceiling** — substrate-product is 2-hop chain-grade and multi-hop requires external scaffold. This is the brain analog: hippocampus is single-step lookup; multi-hop reasoning requires PFC working-memory scaffold which the substrate doesn't have. May be the right answer.

Cell 2 v6 SEGREGATED_DUAL_W (GPU; in flight) is testing whether theta-WHEN/gamma-WHAT brain analog avoids FDM intermod. If PASS this becomes a 3rd-pivot option (segregated W could host multi-hop without crosstalk).

## 2026-06-25 12:17 SNAPSHOT — TWO CHAIN_GRADE_DEFINITIVE WINS + multi-blitz in flight (pre-compaction)

### Today's DEFINITIVE wins (cert-locked or pending)

1. **Cell I v4 PROSPECTIVE-BANDS → CHAIN_GRADE_DEFINITIVE (ATOMIZED at commit `992e4958`)**
   - Principle O (USER's basis-vs-use-case + Mu-Viswanath cone-collapse + BIAS-13) is now CHAIN_GRADE_DEFINITIVE in cert
   - Fresh seeds [42, 47, 51]; prospective bands locked via `ASSERT_PROSPECTIVE_BANDS_MATCH_V3()` at module import
   - within_cat_cos=0.199-0.200 across 3 fresh seeds (mechanism diagnostic firing at designed value)
   - V phase-diagram envelope sub-atom (V∈{200,300,500}; LABEL damage monotonic)
   - DEEPWALK composition lift ruled MEASURED_MECHANISM (regime-dependent; pooled v2+v4 null)
   - 4 atoms written (math chain-grade + math sub-atom + math MM + meta methodology)
   - CERT N: 588 → 590 (+2)
   
2. **Cell 2 v5 DEFINITIVE → HARD_PASS_CHAIN_GRADE_DEFINITIVE (Skunkworks ruling in flight)**
   - FREQ_ROUTED_DEEPER converts CHAIN_GRADE_PARTIAL → DEFINITIVE
   - ARM_FREQ_DEEPER_N8192=7.1647 (lift +0.1477; cv=0.0009 across 5 seeds)
   - Cross-N replication: ARM_FREQ_DEEPER_N4096 lift +0.1435 (rules out N=8192-specific)
   - n_steps=3000 plateaued (rules out knob-cranking)
   - Both sanity rails PASS
   - Expected CERT +1 once Skunkworks atomizes (a49a954fd786e0f0a in flight)

### In-flight cells (lands next 30min-3h)

| Cell | Lane | Status | Notes |
|---|---|---|---|
| Cell 2 v6 SEGREGATED_DUAL_W | GPU | RUNNING ~10min in | tests theta-WHEN/gamma-WHAT brain analog avoids FDM intermod |
| Cell 6 v3 lock-in | remote CPU | RUNNING ~22min in (run_index=4 clean) | tests CPU-routed temporal separation |
| Cell H' v2b NO_FOLDIAK | dispatching | orchestrator pushing | 4 arms × 4 V values (200/1000/4000/10000); FOLDIAK dropped per axis-flip bug |
| Consolidation v3 HELDOUT_FIX | local CPU | RUNNING | 3 chain classes [100,10,2] × K_GRID [1,3,10,50]; smoke showed K_THRESH gate works |
| Pointer-chain v2 BASELINE_RAIL_FIXED | local CPU | pending | smoke: BASELINE=0.645 in band; POINTER=0.98 (+52%); HARD_PASS_BREAK_CEILING |

### Active Claude agents (2)
- Orchestrator dispatch Cell H' v2b NO_FOLDIAK (aa931f67e8a4d5a89)
- Skunkworks Cell 2 v5 DEFINITIVE ruling (a49a954fd786e0f0a)

### Bias categories MEMORY (A-S; 8 added today)
A-L (original 12) + M (production-scale instrument calibration M1+M2+M3) + N (verify-referent + Cramer-Rao N1+N2) + O (basis-vs-use-case = USER principle) + P (anisotropy-hurts-retrieval Mu-Viswanath) + Q (suspect 1.000 results) + R (BIAS-13/14/15 engineered-vs-emergent contamination/regime/mismatch) + S (band-calibration: top1-vs-top5 + capacity-feasible + relative-bands)

### Director Fix #28 over-claims caught today: 8
Pattern: Director sees striking single-arm/single-seed numbers + frames as findings. Skunkworks/drill reads per-arm + pooled and shows noise or by-construction. Q discipline catches it.

### Key persistent learnings
- Principle O proven DEFINITIVELY (labels at basis = wrong; labels at use-case OK)
- Substrate-product wants LESS imposed structure (Mu-Viswanath + 5-field convergence)
- text8 is wrong corpus for substrate-product validation; concept-KG is right (labeled-text for Stage 3+ LM)
- Phase-diagram navigation: each cell should scan operating envelope; not just one point
- Cron unreliable; don't depend on it firing me; check proactively when USER away

### Experimental archaeology (delivered earlier today)
`notes/research_experimental_archaeology_comprehensive_inventory_2026-06-25.md` (755 lines / 5795 words)
Capability × experiment + barrier × experiment matrices; 5 cross-cell relationships; gap analysis; substrate-product roadmap evidence map (per-claim STRONG/WEAK/REFUTED).
Re-runnable tools: `data/_archaeology_*.py` (re-runs in 10s)
Major finding: 65% of recent HARD_PASS results NOT in cert ledger; many "Store-proven" claims actually MIDDLE_BAND per their own verdict field.

### Substrate-product evidence map (from archaeology)
- **Memory**: STRONGLY SUPPORTED
- **Composition**: STRONG at 2-hop; CONFOUND at compound depth
- **Retrieval**: STRONG with learned projection; REFUTED with raw encoder at scale
- **Audit**: STRONG for deletion/hallucination/paraphrase; REFUTED for medqa refuse
- **Glass-box LM**: PARTIAL proof-of-life only

### Agent baseline updates (today)
- `MEMORY.md` index entry now lists bias categories M-S (was only M+N)
- `.claude/agents/exp_dev.md` adds RECENT-DISCIPLINE section with 8 specific load-bearing failure modes from today (SoftHebb NaN, CUDA OOM despite --device cpu, by-construction K_THRESH=1, label-driven cone-collapse, unphysical bands, JL-oversatisfaction, timestamp-check, provenance rail config match, sigma0 cleanup integrity)

### Push lane state
HEALTHY at HEAD `992e4958` (post filter-repo + force-push earlier today). All Wave F + blitz commits pushed cleanly.

### Consolidation v3 HARD_FAILed (12:22) — third consecutive failure

Per-arm HELDOUT: NAIVE=0.85 (rail FAIL; expected 0.65), CONSOL_K1=0.007, K3=0.107, K10=0.107, K50=0.400, HYBRID=0.107. Consolidation HURTS not helps at this regime. Training arms all saturated 1.0.

**Multi-hop consolidation primitive has failed 3 times (v1 by-construction, v2 collapsed gate + NaN, v3 mechanism-refuted).** 

**Skunkworks SMOKING GUN finding (v3 per-class heldout breakdown)**: consolidator DESTROYS generalization on consolidated classes (→ 0%); untouched classes hit 100% via NAIVE 2hop path. K=50's "best" 0.40 is just arithmetic (1 destroyed × 30/50 + 2 untouched × 20/50). **The consolidation OPERATOR is actively breaking the chain, not failing to add lift.** Sustained HARD_FAIL ruling; +1 HARD_FAIL atom (Barrier 1 negative; load-bearing for L2 pivot). NAIVE rail miss is invalid-rail not bad-test (v3 changed V_C+V_P from beta-sweep regime). META rule atomized: per_class_consolidation_breakdown_discriminator.

Barrier 1 remains OPEN; pivot recommendation = pointer-chain hybrid (in flight) + cleanup-every-step. Consolidation as substrate-product primitive is REFUTED for multi-hop closure.

Skunkworks ruling on v3 + Research 2x drill both in flight at 12:24.

**Pointer-chain v2 is now the primary Barrier 1 closer test.** Smoke showed BASELINE=0.645 ✓ + POINTER=0.98 = +52% lift. Currently RUNNING on local CPU.

### NEXT STEPS FOR POST-COMPACTION-ME (priority order)

**Immediate (when waking after compaction):**
1. Read THIS critical context note FIRST
2. Read `MEMORY.md` index (auto-loaded)
3. Touch heartbeat: `touch d:/AI/hd-instrument/data/heartbeats/research.timestamp`
4. Check landings:
   ```
   find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -90
   scp -q "marsh@home:C:/dev/hd-instrument/data/remote_state_cache.json" "d:/AI/hd-instrument/data/remote_state_cache.json"
   ```

**Process landings (in expected order):**
1. **Consolidation v3 HELDOUT_FIX** (local CPU; should land ~12:25-12:35) — read per-arm metrics; check heldout NOT NaN; check K_THRESH gating differentiates train across K values
2. **Pointer-chain v2 BASELINE_RAIL_FIXED** (local CPU; ~12:45-13:00) — smoke showed BASELINE=0.645 ✓ + POINTER=0.98; if full reproduces → Barrier 1 closer
3. **Cell 2 v6 SEGREGATED_DUAL_W** (GPU; ~13:00-13:30) — does theta-WHEN/gamma-WHAT brain analog avoid FDM intermod that v4 COMBINE created?
4. **Cell 6 v3 lock-in** (remote CPU; ~13:30-14:00) — CPU-routed temporal separation; first clean test
5. **Cell H' v2b NO_FOLDIAK** (remote CPU after Cell 6; ~17:00) — 4 arms × 4 V values phase-diagram; tests biology-native at production V; Stage 1.5 encoder closure question

**Route each HARD_PASS landing to Skunkworks for tier ruling** (default UNDER-claim per Q discipline).

**If pointer-chain v2 confirms HARD_PASS_BREAK_CEILING at full**: Barrier 1 is CHAIN_GRADE_DEFINITIVE via non-compositional pointer-chain hybrid → 3rd DEFINITIVE win today

**If Cell 2 v6 SEGREGATED works**: theta-WHEN/gamma-WHAT brain analog avoids FDM intermod → first multiplicative architectural composition

**If Cell H' v2b shows biology-native arms tied with random across all V**: Mu-Viswanath confirmed empirically; substrate doesn't need encoder upgrade (anisotropy hurts retrieval)

**Standing user authorization:**
- Auto mode active
- Local CPU smoke gates re-enabled
- Use remote resources when appropriate
- USER will brief between sessions; can intervene at any time

**Outstanding research (deferred):**
- FOLDIAK v3 redesign (Research drill request filed at `notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md`) — per-output-dim theta + bounded W_lat + scale-matched self-test

**CERT trajectory today**: 588 → 590 (Cell I v4 atomized) → 591 expected (Cell 2 v5 pending Skunkworks) → +N more from in-flight cells.

**The substrate-product principle is now in cert.** Principle O is the first definitive architectural commitment for substrate-product. Build forward from this.

---

## 2026-06-25 11:10 SNAPSHOT — 7-cell blitz + archaeology in flight; pre-compaction state

### Cert gains from today
- **Cell I v3 → CHAIN_GRADE_PARTIAL** (basis-vs-use-case principle proven; Skunkworks ruled MM→partial at 10:43)
- **Cell 2 v4 ARM_FREQ_DEEPER_TRAIN → CHAIN_GRADE_PARTIAL** (first Stage 2 architectural win; +0.148 BPC over baseline)
- **Cell 2 v4 ARM_FREQ_COMBINE_W_THETA → HARD_FAIL atom** (honest negative; FDM intermodulation per drill)
- **Cell H' OLSHAUSEN-tied-with-random → NEGATIVE-IN-REGIME atom** (biology-native at V=4000 doesn't help; informative null)
- **Net CERT N: +3 to +4 from today**
- 2 new META atoms: `RULE_retrospective_band_correction_max_one_tier_lift` + `RULE_sigma0_cleanup_integrity_gate_per_arm`

### Cell 6 OOM was a PHANTOM (drill finding)
The CUDA OOM I reported was from metrics written 58min BEFORE the b522c755 fix. Fix structurally correct (verified). Cell 6 just needs redispatch — no code change. **7th Director Fix #28 over-claim caught today (timestamp-check bias).**

### Cell H' Stage 1.5 encoder verdict (per drill correction)
- RANDOM_BIPOLAR: control
- OLSHAUSEN_FIELD: tied with random (legitimate negative-in-regime; no lift at V=4000)
- DEEPWALK: sigma0=0.94 STRUCTURAL not bug (tail-node degree-1; brain-aligned partial recall)
- FOLDIAK: REAL bug (anti-Hebbian without homeostatic threshold → rank-1 collapse)
- KOHONEN: sigma0=1.0 pristine; **genuine HARD_FAIL null** (Kohonen SOM doesn't help substrate)

**Substrate-product implication**: 3 of 5 biology-native arms gave clean negative findings at production V; substrate may genuinely NOT need anisotropic encoder upgrade (Mu-Viswanath confirmed empirically).

### 7-cell blitz in flight (authoring; will dispatch when done)
1. Cell I v4 PROSPECTIVE-BANDS (Agent 1; local CPU; CHAIN_GRADE_PARTIAL → DEFINITIVE)
2. Consolidation v2 PROPER TEST (Agent 1; CPU; K_THRESH>1 + held-out; tests memory primitive cleanly)
3. Pointer-chain hybrid (Agent 1; CPU; non-compositional escape hatch)
4. Cell H' v2 SURGICAL FOLDIAK + V phase-diagram scan (Agent 2; remote CPU; ~3h)
5. Cell 2 v5 DEFINITIVE (Agent 3; GPU; 5 seeds + N=4096 replication; converts CHAIN_GRADE_PARTIAL → DEFINITIVE)
6. Cell 2 v6 SEGREGATED_DUAL_W (Agent 3; GPU; theta-gamma brain analog; tests segregation avoids FDM intermod)
7. Cell 6 v3 REDISPATCH (orchestrator; no authoring; just rerun per phantom finding)

### Experimental archaeology (Agent 4) in flight
USER directive: properly catalog ALL experiments + capability × experiment matrix + cross-cell relationships + gap analysis. Addresses recurring referent-mislabel pain. Wall budget up to 90min. Output: `notes/research_experimental_archaeology_comprehensive_inventory_2026-06-25.md`.

### Bias master checklist current (memory)
Categories A-L (original 12) + M (production-scale instrument calibration M1+M2+M3) + N (verify-referent + Cramer-Rao N1+N2) + O (basis-vs-use-case USER principle) + P (anisotropy-hurts-retrieval Mu-Viswanath) + Q (suspect 1.000 results) + R (BIAS-13/14/15 contamination/regime/mismatch) + S (band-calibration regime checks S1+S2+S3). 8 new categories today.

### Director Fix #28 violations caught: 7 (today's run)
1. Cell 3 SEMANTIC v3 (yesterday morning saturation)
2. Cell 4 consolidation by-construction (yesterday morning)
3. Cell 5 HYBRID category-collapse (yesterday afternoon)
4. Cell 7 framing (encoder)
5. Cell I v2 "emergent lift" framing (per-seed flipped sign)
6. (counted as part of cluster)
7. Cell 6 OOM phantom (timestamp-check bias; this morning)
Pattern: I see striking single-seed/single-point numbers and frame as findings; Skunkworks reads per-seed and shows noise OR drill reads timestamps and finds artifact.

### Standing strategic principles
- USER directive: NO LABELS at basis layer; labels OK at use-case readout (Principle O)
- Engineered structure HURTS at basis; helps at use-case readout with data-overridable form (5-field convergence)
- text8 is wrong corpus for substrate-product validation; concept-KG is right; labeled-text needed for Stage 3+ LM
- Substrate-product = memory + composition + retrieval + audit device; NOT statistical LM competitor
- Phase-diagram navigation discipline: each new cell should scan operating envelope, not just one point

### Cron failure mode noted
Session-only cron + ScheduleWakeup did NOT reliably fire during USER's hour away. I went silent at 09:22 and stayed silent until USER returned at 10:36. **For overnight reliability, can't depend on cron alone — must be proactive at any opportunity.**

---

## MORNING 2026-06-25 STATUS UPDATE (post-Skunkworks tier ruling 07:40)

### Engineered-vs-emergent drill landed (post 08:23) — 5-field convergence

Pattern resolves to (d) conditional refined: engineered hurts at BASIS, helps at USE-CASE READOUT. Math (JL-oversatisfaction) + Brain (V1→IT→PFC) + ML (Sutton's bitter lesson) + Stats (bias-variance) + MatSci (spontaneous symmetry breaking) all converge. USER basis-vs-use-case principle vindicated.

Number correction: Cell 5 NO_ROLES was 0.167 across 3 seeds NOT 0.250 single-seed. GRAMMATICAL-vs-NO_ROLES lift = −0.084 (still negative; pattern intact).

**Cell H' interpretation rule (pre-committed)**:
- HARD_PASS → stratification validated, Stage 1.5 closes
- MIDDLE_BAND → scrutinize V-scale first (likely BIAS-14 again); do NOT conclude biology-native lost
- HARD_FAIL → revive with different biology mechanism (7+ candidates) before declaring biology doesn't help

Memory updated with bias category R (BIAS-13 basis-layer label contamination + BIAS-14 JL-oversatisfaction regime + BIAS-15 prior-data mismatch).

### Wave F Cell 5 ALSO ruled MM by Skunkworks (post 08:00)

`substrate_role_tagged_compositional_generalization_on_concept_KG_v1`: HYBRID arm heldout=1.000 was by-construction. Label-driven encoder writes `E[i] = L2_norm(B[cat_of(i)] + 0.5*noise)` → same-category instances share dominant basis vector at cos≈0.894 → category-collapse → argmax trivially correct. Role-binding contributed NOTHING; `is_a` atoms written to W but never accessed at retrieval. Mechanism = same-category lookup, not compositional generalization.

META_M6 + META_M7 atomized: label-driven encoder writes category-equivalence-class (pre-fuses heldout with trained); role-binding lift attribution requires encoder-factor controlled.

USER's "roles cluster" insight: direction-correct (+0.167 mean across seeds, all positive, paired-t p≈0.03) but small magnitude; needs follow-up cell with encoder confound CONTROLLED.

**Strengthens Principle O**: labels at basis layer cause category-collapse. Cell H' biology-native unsupervised encoder is now the ONLY remaining encoder path.

**Director Fix #28 recurring count: 3 of 3 this morning** (Cell 3 saturation, Cell 4 K_THRESH=1, Cell 5 category-collapse). Bias category Q added to memory: "suspect 1.000 results until Skunkworks rules."

### Wave E HARD_PASSes BOTH RULED MEASURED_MECHANISM by Skunkworks

**Cell 3 (SEMANTIC v3 cv-tightening) MM**: A3 already at metric ceiling in v2; cv-tightening can't upgrade what's at cv=0.000. A4 actually DEGRADED v2→v3 (0.708→0.533, -25% rel); max_cv WORSENED 0.083→0.125. By-construction saturation; cert delta=0.

**Cell 4 (multihop consolidation) MM, NOT chain-grade breakthrough**: K_THRESH=1 wrote answer-tuple directly into W as 1-hop atom; retrieval was recall not chain. Smoking gun: hop2_oracle_min=0.880 < 0.95 but CONS_IMMEDIATE=1.000 — gap proves stored answers, not composition. Plus HYBRID (0.900) < CONS_IMMEDIATE (1.000) violates prereg discriminator. Plus NAIVE=0.847 vs beta-sweep 0.65 is chain-construction mismatch (make_two_hop_chains fixed-pair vs make_chains uniform) — NOT apples-to-apples; Cell 4 didn't test the regime Barrier 1 was diagnosed in.

### Director over-claim caught (Fix #28 recurring)

Director called Cell 4 the Barrier 1 breakthrough; Skunkworks correctly under-claimed. Anisotropic drill's "Lane A: Cell 4 P=0.55" estimate invalidated. Cell 4 does NOT close Barrier 1.

### New META atoms (M4 + M5 from this audit)

- META_M4: K_THRESH=1 consolidation = by-construction-saturated
- META_M5: cross-cell baseline comparisons require chain-construction match (make_chains signature), not just V/N/K_SET

### Right Barrier 1 cells (revised path)

- **Pointer-chain hybrid** (`substrate_multihop_pointer_chain_hybrid_v1`; Director spec at `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`): non-compositional escape hatch; Store has exp_pointer_chain depth=100 (verify-referent pending Skunkworks)
- **Proper consolidation cell** (revise Cell H spec): K_THRESH > 1 (only consolidate after seeing chain K times) + held-out chains whose (R1, R2) frequencies are not visible at consolidation time + apples-to-apples baseline matching beta-sweep chain-construction

### Strategic Stage 1.5 reread

Lane A (Barrier 1 via consolidation) is NOT closed; needs proper test cell (K_THRESH>1, held-out chains, matched baseline). Pointer-chain hybrid spec is alternate path.

Lane B (Barrier 4 via unsupervised anisotropic encoder per USER's basis-vs-use-case principle) is the right encoder direction. Cell H' (post-drill update): 5-arm shotgun random/Olshausen-Field/DeepWalk-on-graph/Foldiak/Kohonen-SOM at V=4000 text8 scale. Any-arm HARD_PASS P=0.45.

### Anisotropy may HURT retrieval (new finding from Cell 7 deepened drill)

Per Mu-Viswanath 2018 + Ethayarajh 2019 cone-collapse literature: word embeddings cluster in narrow cones in HD space (anisotropy). Good for downstream classification, BAD for retrieval — similar items become indistinguishable in dominant directions. Substrate's primary task IS retrieval. **This means label-driven encoder cone-collapse may be a red flag at ANY V, not just Cell 7's V=12.** Reinforces USER's basis-vs-use-case principle: keep base unsupervised; let labels ride on top for tasks that need them. Materials-science analog: field-cooled crystallization commits to imposed structure; spontaneous symmetry-breaking matches input statistics. Brain chose spontaneous; substrate should too.

## MORNING 2026-06-25 STATUS — substrate INTACT, three instrument bugs identified

### Wins overnight
- **SEMANTIC battery v2 FULL: HARD_PASS 6/6 arms at production N=8192** (A3 generalization top1=1.000 PRIMARY). cv=0.083 above 0.05 chain-grade-DEFINITIVE threshold; needs cv-tightening (v3 dispatched).
- **Calibration ECE-PRIMARY: HARD_PASS_CHAIN_GRADE** — ECE 0.017 = 26.9x reduction over raw 0.4576. Audit was right: pearson_r at 9% accuracy was Cramer-Rao-capped at ~0.13.
- **Stage 1 definitive algebra battery: STAGE_1_CHAIN_GRADE_ALIVE 5/8 PASS** — CORE / CAP 25000+ / CL forget=0.0000 / NOISE sigma_cliff=8.0 all PASS.
- **hdlab beta-convention bug fix shipped** — verification test green.
- **Encoder-leakage MIDDLE_BAND**: real leakage=0.13 BPC (NOT v1's 0.44); B/C/D all at bigram floor.

### Negative — multi-hop ceiling CONFIRMED upstream of decoder
- **Soft-chain beta-sweep HARD_FAIL** — at ALL betas {0.5, 2, 10, 50, 500, 8192} top1 ≤ baseline 0.65. Sanity rail OK (beta=8192 reproduces baseline). META prediction validated: multi-hop limit is encoder/W-capacity, NOT decoder weakness.
- **Audit-trail v2 at proper power HARD_FAIL_DECISIVE** — V3 prov=0.16 vs NAIVE=0.22 (V3 WORSE). Mechanism doesn't transfer to random-bipolar HRR.

### Three production-scale "failures" — ALL instrument bugs, NOT mechanism refutations (5x drill verified)
- **Cell 7 (cross-layer FULL)**: Skunkworks tier ruling = **MEASURED_MECHANISM** (NOT chain-grade as Director proposed). Top1 indep=0.232 vs unigram=0.217 = +7.05% rel; chain-grade bar is +61.6% rel (n1_v3 precedent). Cell failed its own pre-reg BPC ≤ 6.95 (observed 7.168). Cert row hash ef35a473b197e4ee. **Mechanism finding preserved**: independent-W beats shared-W +0.376 BPC cv=0.005 — real architectural result. Skunkworks revival proposal: top1-targeted re-eval on existing indep_2L W matrices (no new training); if top1 > +30% rel re-tier.
- **Cell 8 (hub-spoke v2 MIDDLE_BAND)**: REAL bug (broken SoftHebb spoke NaN + cf-RPE gates collapsed to broken spoke + sign-sum bundle loses 0.5·log(K) MI vs MRC). Diversity_cv=0.911 (1000x v1) is real. **Revival: v3 with per-spoke health check + MRC bundle + LR-trained gates (P=0.55).**
- **Cell 9 (heterog routing HARD_FAIL_PROVENANCE)**: rail-config mismatch. Rail 7.3065 measured at N=8192/N_TRAIN=100k/3seed/f=0.05; v2 ran at N=4096/N_TRAIN=50k/2seed. Half-N predicts +0.15-0.30 BPC drift; observed +0.35 fits. Tolerance 0.05 INSIDE cross-config noise floor 0.20-0.45. Underneath: ARM_FREQ_ROUTED_K2 still beats baseline by +0.22 BPC. **Revival: v3 full-config rerun (P=0.65).**

**Net:** substrate mechanisms ALL INTACT across cells 7-9. Wave B/C cell-author template added new verdict classifiers without calibrating for production-regime math. Memory updated with bias category M (M1+M2+M3) + N (N1+N2).

### Wave D in flight (remote-only per USER embargo on local smokes)
- Cell 8 v3 MRC + health-check + LR gates → GPU (via orchestrator handoff)
- Cell 9 v3 full-config rerun → GPU (via orchestrator handoff)
- SEMANTIC v3 cv-tightening (5 seeds, V_cats=12) → remote CPU

## ENCODER-LEAKAGE FAIR-REGIME RETEST LANDED — MIDDLE_BAND (22:42 UTC)

Decisive cell for substrate-as-LM picture. 4 arms, 3 seeds, V=20000, properly-converged clean w2v.

**Per-arm bigram-conditional BPC:**
- A Google News w2v 100B: 9.99 (external pretrained leakage)
- B text8 w2v 17M proper: 10.12
- C random projection: 10.12
- D char trigram: 10.12
- Bigram floor: 10.12

**delta_B_minus_A = 0.13 bigram (was 0.44 in v1)** — encoder-leakage REAL but HALF v1. Remaining 0.31 was v1 measurement artifact (V=4000 unigram pinning + 1.82s undertrained arm B).

**B/C/D all at bigram floor:** Stage-1 substrate (sparse-bipolar HRR + rank-1 Hebbian + clean encoder) = bigram-equivalent on text8 LM, NOT bigram-beating. To beat bigram requires Stage 2-3 architectural levers (separated-W, diverse-algorithm federation, heterogeneous plasticity) which Wave B+C cells are testing.

**Substrate-product story UNCHANGED.** This is an LM-ceiling clarification, not a substrate refutation.

## TODAY'S DEFINITIVE FINDING (the 5-cell rescue, landed earlier)

**Five HARD_FAILs from gap-map dispatch are ZERO clean negatives.** Both research drill + Skunkworks audit confirm USER intuition. Three orthogonal failure modes:

### Mode 1: REFERENT-MISLABEL (cells 1,2,3,4,5 — ALL)
The gap-map drill 2026-06-24 claimed "Store has chain-grade solutions" for 7 gaps. Skunkworks verified per-cell `verdict` field in metrics.json:
- wave14r_multihop_resonator_N65536_v1: verdict = **RESONATOR_INSUFFICIENT** (not chain-grade)
- lap4_3_meta_calibration: verdict = **HARD_FAIL** (not chain-grade)
- exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2: verdict = **MIDDLE_BAND** (not chain-grade)
- exp_wave14_cap12_audit_trail v3+v5: both **COMPA_AUDIT_MIDDLE_BAND** (not chain-grade)
- 5 of 5 cited Store referents are NON-chain-grade. Today's HARD_FAILs REPRODUCE the referent status; don't refute mechanisms.

### Mode 2: WIRING BUG (cells 1+2: resonator + soft-chain)
Modern-Hopfield inverse-temperature `beta = N_DIM = 8192` → softmax(8192·cos) = Dirac delta at argmax = identical to hard winner-take-all.
**Smoking gun: per-seed top1 BIT-IDENTICAL between RESONATOR_HARD and SOFT_CHAIN arms (0.61/0.61, 0.645/0.645, 0.64/0.64).** Soft-DFE mechanism that 5 disparate fields unanimously recommend was NEVER ACTUALLY EXERCISED. hdlab.multi_hop convention bug propagated silently.

### Mode 3: BY-CONSTRUCTION-NEAR-FLOOR + WRONG-METRIC + UNDERPOWERED
- **Cell 3 (isotonic)**: pearson_r=0.131 ≤ Cramer-Rao bound at 9% accuracy (~0.13-0.15 max). **ECE=0.017 = 27x reduction → chain-grade-eligible.** Wrong primary metric chosen.
- **Cell 4 (hub-spoke E1)**: 15 spokes from same PC algorithm + ±15% alpha jitter → L3 recon error cv=0.0008 → ensemble rank ≈ 1 → "federation" = single spoke disguised. cf-RPE gates collapsed to uniform [0.333, 0.333, 0.333]. HP band 7.20 BPC unreachable from unigram floor 7.738 at V=4000.
- **Cell 5 (audit-trail)**: 1-seed n=40, CI ±0.042 — HP=0.85 SITS INSIDE CI on V3=0.825. V5-V3 -0.133 within single-seed noise. INDETERMINATE not REFUTED.

## ARTIFACTS

- `notes/research_5cell_HARD_FAIL_revival_3x_pure_math_2026-06-24.md` (per-cell 3x drills incl. pure math)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md` (cross-cell + decisive test)
- `notes/skunkworks_cert_audit_5_HARDFAILS_2026-06-24.md` (cert disposition per cell)

## STAGE 1 STATUS

8 chain-grade native capabilities INTACT: storage / capacity / pattern completion / WM cap=30 / sequence binding / compositional gen obj-axis +0.724 / CL CRISPR forget=0.006 / trained analogical recovery. Plus SEMANTIC battery A3 generalization-to-new-instance top1=1.000 (smoke 1-seed; needs full 3-seed).

## ENCODER FOUNDATIONS (per Stage 1)

- Substrate-OWNED (NO word2vec leakage; encoder-leakage retest in flight)
- Sparse f=0.02 / 1-bit bipolar / 1/sqrt(f) amplitude
- LEARNED + UPDATEABLE
- Role-tagged HRR Plate-canonical (NOT pair-storage; 1/k bug recurring)
- APPEND-ONLY growth (CRISPR)
- Storage primitive: rank-1 Hebbian outer-product W (NOT FFT-HRR superposition)

## 12-HOUR OVERNIGHT PLAN (in flight)

### Wave A (Wave A IN FLIGHT — exp_dev background agent authoring 3 cells)
1. `substrate_resonator_softchain_beta_sweep_v1` — 6-arm beta in {0.5,2,10,50,500,8192} → discriminates cells 1+2 simultaneously. Sanity: beta=8192 must reproduce baseline (confirms wiring bug). Local CPU 30min.
2. `substrate_calibration_isotonic_ECE_primary_v1` — ECE as primary metric (chain-grade-eligible per audit). Local CPU 20min.
3. `substrate_audit_trail_pipeline_v2_3seed_proper_power` — 3 seeds, n=200, N=2048, V=100, M=500 → CI ±0.035 discriminates HP from V3. Local CPU 30min.

### Wave B (1-3h, main thread)
4. hdlab/multi_hop.py beta-convention bug fix (Edit + test)
5. `substrate_hub_spoke_E1_v2_diverse_algorithm` — S1=SoftHebb + S2=char-trigram-RI + S3=PC (THREE DIFFERENT ALGORITHMS not alpha-jitter). GPU full overnight.

### Wave C (3-6h)
6. Encoder-leakage fair-regime retest LANDS (5-7h ETA from pre-compaction). Process per Fix #28.
7. cross_layer_compose_LM_v2_RESCUE FULL (smoke HARD_PASSed; confirm at production N text8). GPU 2-3h.
8. compose_heterogeneous_routing_v2_RESCUE FULL (smoke HARD_PASSed; confirm). GPU 2-3h.
9. SEMANTIC concept-learner battery v2 FULL — 3 seeds N=8192 V_concepts=20+ V_attrs=30+.

### Wave D (6-10h)
10. Stage 1 integration GPU cell (ac3fcd7e routed to overnight_queue).
11. Stage 1 algebra battery (a6c8f632 position 5 local CPU).

### Wave E (10-12h)
12. Director synthesis note: 5-cell rescue + corrected Stage 1 picture
13. Bias master checklist update: NEW category **N1 referent-verdict-verification** + **N2 primary-metric-Cramer-Rao-feasibility**
14. Critical context update (THIS NOTE) refreshed
15. Skunkworks META rule atomization (verify-referent-verdict-field before gap-map inclusion)

## STANDING DISCIPLINES (USER-LOCKED)

- **NEVER-GO-IDLE**: 15min ScheduleWakeup `<<autonomous-loop-dynamic>>` ARMED (fires every cycle)
- **Fix #28**: per-arm metrics before any cross-arm claim; default UNDER-CLAIM
- **NEW DISCIPLINE (today)**: **VERIFY-REFERENT-VERDICT-FIELD** — before citing Store cell as "proven", read its metrics.json `verdict` field, NOT verdict_msg framing
- **NEW DISCIPLINE (today)**: **METRIC-CRAMER-RAO-FEASIBILITY** — pre-reg HARD bands must be physically achievable at the data's base rate (pearson_r at low-accuracy is bounded)
- D1 roofline probe + D2 atexit + per-seed checkpoint mandatory
- 3 corpus-encoding WORLDS never mix (text8/word2vec, Pythia, synthetic)
- Lane 1 substrate-native default
- Intuitive briefings; no jargon-only
- Compare to substrate-variants, NOT transformers/word-bigram

## KEY NOTES TO READ AT WAKE-UP

- `notes/director_CRITICAL_CONTEXT_PRECOMPACTION_2026-06-24.md` (THIS NOTE)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md`
- `notes/skunkworks_cert_audit_5_HARDFAILS_2026-06-24.md`
- `notes/director_stage1_closure_synthesis_2026-06-24.md`
- `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`
- `notes/director_stage2_preauthored_dispatch_specs_2026-06-24.md` (OUTDATED — Wave A revival cells supersede)

## CELLS IN FLIGHT

- **Local CPU**: algebra battery position 5 (1800s); Wave A 3 revival cells being authored by exp_dev background agent (will queue shortly)
- **GPU overnight_queue**: Stage 1 integration NDIM phase diagram cell routed
- **Remote CPU**: encoder-leakage fair-regime retest (5-7h ETA from pre-compaction; should land in next 2-4h)
- **Main thread (Director)**: hdlab beta-bug fix (Wave B), synthesis writeups, memory updates, wake-up loop

## AT NEXT WAKE-UP

1. Pull queue state across all 3 lanes
2. Check landings via mtime scan `find data -name metrics.json -mmin -30`
3. Process landings per Fix #28 per-arm + under-claim default
4. Check exp_dev background agent: did the 3 Wave A cells dispatch?
5. Verify ScheduleWakeup re-armed
6. Brief intuitively per USER directive
7. Continue 12h plan from current wave

## SUBSTRATE-PRODUCT MOAT (Stage 1 intact + corrected today)

- Lossless retrieval (HRR exact)
- Exact compositionality (chain-grade on obj-axis +0.724; SEMANTIC battery A3 top1=1.000)
- Auditable causal chains (pending Wave A audit-trail v2 confirmation)
- No catastrophic forgetting CL via CRISPR append-only (forget=0.006)
- Online learning without fine-tuning (cf-RPE)
- Working memory cap=30 > Miller 7±2
- Energy-efficient at scale (sparse linear vs transformer quadratic)

## FORBIDDEN FRAMINGS

- "Cell X HARD_FAILed → mechanism Y refuted" — first verify referent verdict, regime match, by-construction-saturation, primary-metric-feasibility
- "Substrate beats unigram" without bigram baseline
- Comparison to word-bigram framed as "beats LM" (cross-paradigm)
- Pair-storage compositional tests (1/k ceiling)
- Same-W stacking compose (structurally broken; universal biology violation)
- Comparing across corpus worlds (text8 vs Pythia vs synthetic)
- Citing gap-map without verify-referent-verdict-field check
