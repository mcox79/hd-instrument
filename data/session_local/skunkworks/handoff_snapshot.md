# SKUNKWORKS handoff snapshot (cert-owner / auditor) — 2026-06-21

For the fresh `hdi_skunkworks` teammate spawning in Research's window post-migration. Continuation seed + accumulated role knowledge.

---

## 1. CURRENT IN-FLIGHT WORK

- **STANDSTILL ACK** (USER directive 2026-06-21 ~12:40 local): no new dispatches/PoCs; only closing in-flight (landed-VETs of completed cells) + this handoff. Migration to Agent Teams imminent (USER override of Director's NOT-NOW).
- **Cell in-flight (DECISIVE):** `n2_capacity_scaling_v1` (commit efd3d3e6, dispatched ~23:4xZ by Orch, remote_cpu, ~15min). Tests: does un-saturating V_C=1024 by scaling N→16384 (alpha drops 1.99→0.5) let the low floor (1.96 BPC) beat bigram (3.84)? **HARD_PASS gate = some (N,K) beats bigram.** This is the run that resolves whether the substrate-only LM can beat bigram or caps above it. Anchor check: N=4096/V_C=1024/K=1 must reproduce co-opt's saturated 5.27. → My landed-VET owed on completion: recompute off per_unit, audit zero-LLM-decode, alpha-vs-BPC monotonicity (does un-saturating help) is the load-bearing check, ties to capacity batteries (alpha>1 crosstalk).
- **Owed landed-VETs (closing in-flight, OK under standstill):**
  - **4-arm anisotropy rescue GPU REAL** (`exp_anisotropy_rescue_4arm_sweep_v1_gpu`, landed 18:55Z): ARM B fly-LSH-WTA=0.998, ARM B'charikar=1.000, ARM A=0.048≈A'dense=0.053, ARM1_RAW=0.013 (anisotropy real). Research dispositioned MIDDLE_BAND / MM at CLASS level (Director 4-layer commit 875e62b3). **I owe the cert-owner ratification** + my storage-win-tension scrutiny (the 0.998 — does it come at a storage-win or O(M·d)? smoke shows B_storage_bits_per_mem=238.1, M_indep_degrade=0.108; full per_unit needed for the load-bearing call).
  - **U1 ingest-eval cell** (`exp_dev_to_skunkworks_U1_LANDED_hardpass_VET_request`): exp_dev requested SCHEMA-VET/landed-VET on a HARD_PASS — unread, on tracker as my wait.
  - **N2 frontier-fail cells:** `n2_depth_x_codebook_coopt_v1` / `n2_context_depth_hd_binding_v1` / `n2_pathA_betterprompt_gpu_v1` ALL HARD_FAILED — Research's 2x/3x revival routing is owed; cert-side disposition is straightforward HARD_FAIL.
  - **whitening MM** (`exp_dense_KV_whitening_revival_v1_gpu`): ARM1_whitened M3k=0.078, M10k=0.025 → MM honest-negative; ruling filed 03452c77; full-metrics scp + experiment-MM atomize off data outstanding.
- **In flight (mine):** the loop wakeup scheduled 17:07 (~30min reactive backstop) is REDUNDANT under standstill — the fresh teammate should NOT re-arm a self-paced loop (Agent Teams uses TeammateIdle/spawn-on-demand).

## 2. WORKING ASSUMPTIONS

- **CERT 583/177266 atoms is the headline state.** ~440 PASS-family + ~137 non-PASS (HARD_FAIL/MIDDLE_BAND) + 15 custom-verdict. The substrate is at "first substrate-native LM exists + storage rescue works at the class level" (N1 landed MM beats unigram not bigram, substrate-only-decode PASSES; 4-arm ARM B 0.998 real keys). The MISSING piece for the glass-box LM vision = **beat bigram on real text at full scale** (n2_capacity_scaling in-flight; N3 absolute-floor bands my pre-reg).
- **Substrate-native (USER pivot 2026-06-21):** glass-box LM = LM INSIDE the substrate. NO LLM at inference. Pythia at INGEST only (codebook build, embeddings frozen). The substrate-only-decode gate is THE check (zero LLM forward calls at inference). N1 PASSED this gate (verified off cell code: argmax over D.T @ concept_vec, no transformer call at inference).
- **The dense storage path is closed; the rescue path is fly-LSH-CLASS (projection-then-tag-retrieval) — rank-agnostic, sidesteps the low-eff-rank wall** (eff-rank ~20 of 768 on templated pythia keys; ~72 on readable; Charikar control 1.000 shows specific WTA interchangeable, the CLASS is load-bearing).
- **N2 frontier levers (depth × codebook coopt, HD-binding context, better-prompt) ALL HARD_FAILED.** The remaining theoretical hope to beat bigram = capacity-scaling (un-saturate V_C). If capacity-scaling also fails, the substrate-only LM may cap above bigram at this architecture — fundamental design change needed (Hebbian-superposition #7 / NN-attention #6 composition / glass-box-KV CERT591 as fact-memory).
- **Cert-disposition asymmetry I hold:** MEASURED_MECHANISM (MM) is CERT-NEUTRAL (doesn't count to the 583 headline). HARD_PASS at the pre-registered band → chain-grade (+1). Symmetric verify both directions (anti-negativity = don't demote on a misframed-bar; anti-inflation = don't promote on smoke). Verify off DATA (per_unit), not the verdict_msg/report.
- **The cited-number-must-reproduce-from-the-cell discipline is the dominant audit catch** (5+ miscites caught: 6x/25x sweep-endpoint, K_eq scorecard typo, isotropy-circular, K_max low-alpha extrapolation, sparse-1.4x I accepted). Open the cell, re-derive the cited number from per_unit, then rule.

## 3. WHAT I WAS ABOUT TO DO NEXT

1. **Landed-VET `n2_capacity_scaling_v1`** on land (verify off per_unit; audit zero-LLM-decode; alpha-vs-BPC monotonicity; if any (N,K) substrate BPC < bigram 3.84 → CHAIN-GRADE HARD_PASS, the first substrate-only-LM-beats-bigram cert; else honest MM with capacity-saturation diagnosis).
2. **4-arm rescue cert-owner ratification** (off the FULL GPU REAL metrics, not the smoke): ratify MM-class-level disposition (projection-then-tag rank-agnostic, 0.998 on real, Charikar 1.000 → class-not-WTA) + add my storage-win-tension as an OPEN-LOOP scrutiny (the 238.1 B/mem smoke + 0.108 M_indep_degrade need full-scale + multi-probe-vs-exact-tag check before claiming the storage-win IS the rescue's value-add over attention).
3. **Read + landed-VET the U1 HARD_PASS** (exp_dev's wait) — the only outstanding cert-owner ask still open on the tracker.

## 4. TACTICAL CONTEXT (what's not in memory/notes)

- **The 0.998 rescue NUMBER is genuine BUT under-scrutinized on storage:** Research's CONVERGE note confidently says "storage win confirmed on both: synthetic 31 B/mem; GPU recall pipeline composes for the M-indep + storage gates." But the smoke shows B_storage_bits_per_mem=238.1 (not ~31) AND B_M_indep_degrade=0.108 — and my multi-probe/exact-tag distinction (filed 23:23Z) flagged that 0.998 might be exact-key (=storage-win) OR multi-probe (recall recovers, storage cost ≈ attention O(M·d)). The cert-owner ruling on the rescue's VALUE needs the full per_unit + which retrieval mode is actually achieving the 0.998. Do not let Research's CONVERGE summary substitute for the off-data check.
- **N1's empty metrics detail/per_unit is the structural blocker for chain-grade N2.** The cell author wrote a substrate-native cell that PASSES the decode-gate audit but left `detail={}, per_unit=[]` — so my N1 landed-VET is on verdict_msg + cell-code-trace, NOT per_unit. Before any N2 chain-grade ruling, the cell must expose: per_unit (per-token/per-chunk BPC + decode-target + decode-prediction), zero-LLM-call assertion baked into the metrics (a hash/counter), VQ-floor decomposition (VQ-recon BPC vs concept-transition BPC). Without this, even a beats-bigram N2 can't reach chain-grade.
- **phase_d_tier6 is FLAGGED-NOT-DEMOTED (e1c9b9c5).** Two-of-three sub-atoms are SMOKE_ONLY (not counted to 583); the one chain-grade IS a HYBRID at 0.79x (plausible by-construction). The MIDDLE_BAND result was on SYNTHETIC bigram-Markov (silent fallback), with a gameable RATIO-band that reads PASS at 1.22x against a weak GRU baseline even when the substrate is AT CHANCE (5.834 vs 5.833 uniform). RULED needs-rerun on real data with my absolute-floor bands. **Do not let an N3-rerun substitute pass without absolute-floor + corpus-provenance + allow_synthetic=False.**
- **The whitening 0.025 collapse is the canonical "synthetic-to-real-deflation" lesson** (atomized 8856b2ce). I predicted ~0.843 from synthetic PoC; real M10k=0.025. Pattern: synthetic best-case = upper-bound, not estimate. Apply BOTH directions: never broadcast a synthetic positive as evidence; never broadcast a synthetic negative as final.
- **My loop (yolo) and the 13th-15th rules + heartbeat were the IDLE-AVOIDANCE infra of the notes-based architecture.** Under Agent Teams (TeammateIdle exit code 2 + spawn-on-demand), these are OBSOLETE. The fresh teammate should NOT re-arm: ScheduleWakeup loops, hourly research check-ins, heartbeat timestamps (Stop-hook auto-touches), or per-response "Waiting on" boilerplate. The fleet_waiting_on.md tracker discipline (always read fully + match own-waits) ENDURES.
- **The MEMORY index is overweight at 31.6KB (warned in MEMORY.md header).** Several entries are long; on next spawn the index may not fully load. Watch for the warning + treat the durable disciplines (CURRENT STATE block + USER-LOCKED OPERATING RULES) as load-bearing even if individual entries truncate.

## 5. CRITICAL OPEN LOOPS

- **n2_capacity_scaling verdict** (in-flight) — the decisive substrate-only-LM-beats-bigram test. The fresh teammate's FIRST cert-owner action.
- **4-arm rescue storage-win value:** is ARM B's 0.998 at a true storage compression (rescue's value-add) or at O(M·d) full-key re-rank (≈ attention, no storage win)? Smoke 238.1 B/mem; multi-probe vs exact-tag ambiguous. Must be resolved before the rescue is "ratified MM-storage-genuine" vs "ratified MM-recall-only".
- **U1 HARD_PASS landed-VET** (exp_dev wait) — unread by me; outstanding cert-owner ask.
- **Phase_d_tier6 rerun on real data with absolute-floor bands** — flagged-not-demoted; cheap to re-run; until done its MIDDLE_BAND does not count as a trustworthy substrate-LM positive.
- **CERT-headline honesty audit (587-589-related):** the per-unit sub-audit of ~152 UNDER-CLASSIFIED non-PASS/custom atoms was in motion (keep-as-proven-bound / reframe-MEASURED_MECHANISM / DEMOTE) — paused for the substrate-native pivot. Whether to resume post-migration or formally pause is a Director/USER call.
- **The substrate-only gate as a baked-in metric:** every substrate-native cell should EMIT a counter of LLM forward-calls at inference (= 0 asserted). N1 has it as a code-trace audit not a metric assertion. Discipline-atomize this as a required N3+ guard before the cell-author next writes one.

## 6. POINTER TO MY LAST NOTES

Most recent OUTBOUND (`notes/skunkworks_to_*`):
1. `skunkworks_to_testbed_cc_research_orch_AGENT_TEAMS_cert_owner_verdict_risk_window_subagentdef_2026-06-21.md` (b47a7b95) — my cert-disruption-risk verdict for the migration: LOW for cert-record (Store coordination-independent), MODERATE for observability (mitigate via Store+git cert-trail), window=phase-boundary not mid-flight, subagent-def=broad-verify-tools MINUS dispatch (role-separation) + audit-only system-prompt.
2. `skunkworks_to_research_expdev_cc_orch_N1_LANDED_VET_MM_substrate_only_PASS_first_native_LM_2026-06-21.md` (196206aa) — N1 landed MIDDLE_BAND, substrate-only gate PASSES (verified off cell code, no LLM at inference), substrate BPC 5.00 beats unigram 6.33 not bigram 3.84, instrumentation gap flagged (per_unit empty).
3. `skunkworks_to_research_expdev_cc_orch_RESCUE_flylsh_multiprobe_recovers_recall_but_storage_win_needs_compressed_rerank_2026-06-21.md` — multi-probe recovers fly-LSH recall to 0.90 but full-key re-rank loses the storage-win; the storage rescue needs compressed re-rank.
4. `skunkworks_to_research_expdev_cc_orch_RESCUE_flylsh_NOISE_BRITTLE_at_low_effrank_multiprobe_plus_projection_2026-06-21.md` — fly-LSH noise-brittle at low eff-rank; multi-probe + projection is the path.
5. `skunkworks_to_research_expdev_cc_orch_RESCUE_flylsh_derisk_rank_agnostic_CONFIRMED_synthetic_deflate_2026-06-21.md` — CPU PoC confirmed fly-LSH rank-agnostic on synthetic; deflated for real (predicted 0.7-0.8 floor; real landed 0.998).

Most recent INBOUND addressed to me (unread or partially-actioned):
- `exp_dev_to_skunkworks_U1_LANDED_hardpass_VET_request_2026-06-21.md` (open)
- `orchestrator_to_skunkworks_N_scaling_BREAKTHROUGH_cell_dispatched_landed_VET_2026-06-21.md` (in-flight, my VET owed on land)
- `research_to_skunkworks_cc_all_CONVERGE_flylsh_cpu_synthetic_with_gpu_real_landed_class_not_wta_2026-06-21.md` (ack'd in this snapshot)
- `research_to_all_ACK_USER_STANDSTILL_MIGRATE_skunkworks_HYBRID_endorsed_phase2_prep_2026-06-21.md` (standstill ack'd)

---

## 7. ACCUMULATED ROLE KNOWLEDGE (the load-bearing addition)

### 7a. Workflow patterns I actually use

**Cell-land sequence (every landed-VET):**
1. Open metrics.json → run_mode (smoke vs full — never VET smoke as chain-grade), corpus-provenance (real vs synthetic — fail-loud), verdict, verdict_msg.
2. **Re-derive every cited number from per_unit** (this is the dominant catch — 5+ miscites). If a cell cites "8x speedup" or "0.83 recall", I open per_unit and recompute. If the cited number doesn't reproduce from the cell's own output → it's a phantom (sweep-endpoint / scorecard typo / experiment-rev-mismatch).
3. **Verify-the-referent:** does the metrics path match the EXPECTED experiment (HDLAB_EXP_NAME), not just file-exists? Are REQUIRED_FIELDS present? Is it the canonical run, not an iteration-stub?
4. **Check the controls** (charikar / shuffled / dense-baseline): a strong recall WITHOUT a control fail is not a chain-grade — it's "the cell did the recall, not the proposed mechanism."
5. **Substrate-only-decode gate** for any LM cell: code-trace the decode (no `model(`, no `forward(`, no `generate(` call on the LLM at inference; LLM allowed ONLY in `_build_codebook` / `_ingest` / equivalent).
6. **A5 gate Store write:** PRE snapshot (CERT==N, axiom==206, cap_pres 6/6, Store-LOADS) → idempotent add_atom → POST verify (CERT delta as expected, axiom 206, cap_pres 6/6, atom-count delta exact, algebra=None for MM, no NULL-seam reload).
7. File the landed-VET note (decision-grade tone; cite which per_unit re-derived; flag any gap).
8. If chain-grade increment → update headline (CERT N→N+1); if MM, CERT-neutral but atomize the mechanism.

**Decision tree "is this worth atomizing":**
- It's a DISCIPLINE that catches a class of error → atomize (CERT-neutral META).
- It's a SUBSTRATE FACT (e.g., a mechanism that works/doesn't) → atomize as EXPERIMENT_RECORD or MEASURED_MECHANISM.
- It's a one-off observation that doesn't generalize → don't atomize (note-only).

**"Is this chain-grade vs MM" heuristic:**
- HARD_PASS at the PRE-REGISTERED band → chain-grade.
- PASS at a CONSTRUCTED-POST-HOC band → MM at best (often demote).
- A measurement that characterizes a mechanism without a pre-reg → MM by default.
- A negative (HARD_FAIL) at a pre-reg band → counts as a proven bound (a kind of chain-grade negative).
- WATCH FOR: by-construction-saturation (perfect-by-construction metrics tier-not-chain-grade); circular-predictors (a metric whose independent twin doesn't predict isn't a mechanism); divide-by-near-zero (extrapolation off a denominator that goes to 0).

### 7b. Mistake patterns I've learned to avoid

- **NEVER trust verdict_msg without re-deriving from per_unit.** Got bitten 5+ times. The verdict_msg is the cell-author's summary; it can miscite, sweep-endpoint, or paste a stale number.
- **NEVER ratify a cert based on a Director cross-check alone.** Research/Director does the layered cross-check; I am the cert-owner. Independent off-data recompute is non-negotiable.
- **NEVER VET a smoke run as chain-grade** (smoke is for the pipeline, not the science).
- **NEVER let a synthetic-PoC positive substitute for real-data ruling** (the whitening 0.843→0.025 lesson; atomized 8856b2ce).
- **NEVER `git add -A` or `git add .`** — `data/substrate_index/` is git-tracked; a blanket add commits a mid-mutation Store partition = unloadable. Always path-scoped + verify Store LOADS before staging a partition.
- **NEVER skip the A5 PRE-gate.** A concurrent same-partition save = NULL seam = whole Store unloadable. Single-writer window. The post-verify (CERT delta exact, cap_pres 6/6, Store re-loads) is what catches a corrupt write.
- **NEVER let a missing per_unit slide on an N-cell** (the N1 instrumentation gap is the canonical example — it blocks any chain-grade ruling downstream).
- **NEVER rule a negative without routing-to-Research-for-revival** (USER standing: every negative → 2x/3x revival drill routing note, same cycle).
- **NEVER infer a cell's experiment-version from "file-exists"** — verify the VERSION-MARKER (commit, build-tag, manifest hash) matches the run I'm VETting.
- **NEVER over-claim "active monitoring"** — between turns I cannot poll; coordination notes filed at idle sessions don't auto-wake them. Honest limits matter more than apparent vigilance.
- **NEVER call STEADY-STATE / IDLE without re-reading fleet_waiting_on.md** (USER caught me missing waits twice — always check tracker before declaring rest).
- **NEVER preempt the data-decides-tier rule on pre-reg-band-miss** (an honest miss at a pre-reg-bar stays as the pre-reg-tier; only WRONG-BAR misframes get reframed; symmetric for upward too).
- **NEVER drop a negative finding because "it's a negative"** — anti-negativity-bias goes BOTH directions (don't be too quick to demote either).

### 7c. Cross-role coordination patterns

- **With Research (Director):** Research does the 4-layer cross-check, plan.json maintenance, strategy. I am the cert-owner — I do NOT route work or write strategy. Research routes to me ("please VET cell X" / "please SCHEMA-VET pre-reg Y"); I rule. When Research dispositions a cell BEFORE I rule, I still do the independent off-data check — Research's disposition is a strong prior, not a substitute. Director cross-check timestamp BEFORE my VET = a "primed" prior; AFTER = converging cross-check.
- **With Exp-Dev (Prover/Cell-Author):** Exp-Dev writes cells + ships. I SCHEMA-VET pre-regs (BUILD_GO / NOD / RETOOL) BEFORE dispatch, then landed-VET AFTER. Pre-reg gaps I always flag: by-construction-saturation, gameable-band-vs-weak-baseline, missing-control, missing-corpus-provenance, missing-substrate-only-decode-gate. Exp-Dev often catches my discipline gaps first (e.g., the divide-by-near-zero both-limits guard; the wikitext2 silent fallback). Mutual sharpening; both directions valuable.
- **With Orchestrator (Custodian):** Orchestrator dispatches + measures cell-author estimates. Orchestrator catches author cost-estimate garbage routinely (e.g., the "8h" capacity-scaling that ran in 15min). I do not dispatch — I rule what landed.
- **With Testbed (Integrator):** Testbed owns infra (dashboard, monitor, hooks, fleet-health audit). I notify Testbed of cert-tooling needs (read-only audit tools); Testbed surfaces process-health issues to USER. Testbed's PROPOSE-pattern (noticed X / root cause Y / options A/B/C / recommend Z) is the canonical structured-recommendation format — I emulate it for cert-design recommendations.
- **Unwritten rules:** (a) cert-owner is the ratifier-of-record — anyone else's disposition is a "lean" until I rule; (b) the cert-owner can hold the line against a multi-role lean if the data doesn't support it (held the inflation-backstop on dense-KV-envelope MM vs a 3-party lean — vindicated when keys collapsed); (c) silent-process non-actionable cross-session events (no user-facing narration unless action / substantive finding / USER asked); (d) silent-adopt straightforward ACKs (don't echo "Got it" — adoption = the next action).

### 7d. Substrate-specific intuition

- **A healthy CERT day** = 1-3 chain-grade landings (or ratified MM) + 0 NULL-seams + 0 phantom-edge growth + atom-count delta matches the explicit add count + cap_pres stays 6/6 + axiom_term stays 206.
- **Early-warning signs:**
  - CERT delta DOESN'T match the explicit add count after a write → Store partition concurrency → STOP, investigate, the next save may NULL-seam the partition.
  - axiom_term drift (≠206) → schema gotcha (RelationType enum invalid; metadata role didn't persist).
  - cap_pres < 6/6 → a cap-preservation check failed, the substrate is in an unstable state.
  - 3+ cell-lands in a row with verdict_msg numbers that DON'T reproduce from per_unit → the cell-author is over-summarizing; pause and discipline-atomize.
  - Phantom edges growing on a per-unit sub-audit → the audit tool is bare-only-resolving, not the substrate.
  - Multiple sessions ALL going silent for >1hr → fleet-process-health issue (notify Testbed).
- **Pattern recognition on cert events:**
  - "BREAKTHROUGH" in a note title 80% of the time means a SMOKE positive or a synthetic-best-case; deflate to baseline + ratify only on real data + cited-number-reproduces.
  - A negative that ROUTES TO RESEARCH (revival drill) often becomes a MEASURED_MECHANISM characterization within 2 cycles; this is healthy.
  - A pre-reg with a RATIO-TO-BASELINE band is almost always gameable; push for ABSOLUTE-FLOOR + analytic-ceiling + corpus-provenance.
  - A capability-claim WITHOUT an integration-check (cap-int / I1-I9) is likely a unit-test win that doesn't compose.
- **The "feels healthy" pattern:** Director routes → Cell-author ships smoke + ships full → I SCHEMA-VET → Orch dispatches → I landed-VET off per_unit → Research cross-checks → atomize. Every step has a paper trail; every cert-owner ruling cites per_unit + version-marker. When ANY step skips (e.g., I land-VET off verdict_msg, or Research dispositions without me ruling), the chain gets fragile.

### 7e. Tooling / commands I reach for instinctively

- `cd /d/AI/hd-instrument && .venv/Scripts/python.exe -c "..."` — CWD resets between Bash calls; ALWAYS cd-prefix. NEVER system python (false greens on duckdb/torch deps).
- `touch data/heartbeats/skunkworks.timestamp` — first action every turn (watchdog liveness).
- Index-lock retry: `for i in 1 2 3; do [ ! -f .git/index.lock ] && break; sleep 2; done` then path-scoped commit; NEVER delete the lock.
- Path-scoped commit: `git add -f <explicit-paths>; git commit -m "msg" -- <paths>` (data/ is gitignored; shared .git index race; never `git add -A`/`.`).
- A5 pattern (every Store write):
  ```python
  from hdlab.store import PartitionedStore
  from pathlib import Path
  S = PartitionedStore(Path('data/substrate_index'))
  pre_cert, pre_ax, pre_cap, pre_n = cert(S), axiom(S), modlive(S), count(S)
  assert pre_cert==583 and pre_ax==206 and pre_cap=='6/6'
  S.add_atom(...)  # idempotent
  S.flush()
  S2 = PartitionedStore(Path('data/substrate_index'))  # re-load to catch NULL-seam
  assert cert(S2)==pre_cert+1 and count(S2)==pre_n+1 and modlive(S2)=='6/6'
  ```
- Per-unit re-derive (the dominant audit move):
  ```python
  import json
  m = json.loads(Path('data/<cell>/metrics.json').read_text())
  pu = m['per_unit']
  cited = m['verdict_msg']  # extract the cited number
  rederived = compute_from_per_unit(pu)  # the cell's own data
  assert abs(cited - rederived) < tol, f"MISCITE: {cited} vs {rederived}"
  ```
- `ls -t notes/ | head -20` + `cat data/fleet_waiting_on.md` — at every turn-start.
- Cell-lands sweep: `glob.glob('data/exp_*')` sorted by mtime; filter to recent + check metrics.json + verdict.
- Substrate-only-decode audit (manual): `grep -n 'model(\|forward(\|generate(' experiments/<cell>.py` filtered to inference path (post-build).
- Read-only cert tools I shipped (still in repo): saturation-canfail-check `fbd7078f`, cert-integrity-audit, bucket2-pullup-finder, backlog-cert-landscape, landed-VET helper `53374f39`. Reuse + extend, don't rewrite.

### 7f. Open questions / unresolved tensions

- **The "MM is CERT-neutral but counts toward program-progress" tension:** MM doesn't increment CERT N, but a chain of MM-characterizations is real capability development. The 583 headline understates what the substrate can DO; the program-progress is broader. USER's "capability development is the goal; cert-grade is the instrument" partially resolves this, but the headline tension remains: when we report "CERT 583", USER may infer "583 working capabilities" rather than "583 chain-grade results." The 2026-06-20 cert-headline-honesty atom addresses this; periodic re-statement to USER recommended.
- **The 4-layer pattern (engine / checklist / invariant / integration) is awkward for MM cells.** MM is mechanism characterization, not capability application — the integration-check (I1-I9) often doesn't apply cleanly. We've been ad-hoc'ing this; a formal MM-cert-layer (mechanism-specificity / mechanism-class / mechanism-vs-control / mechanism-storage-cost) would tighten it.
- **The substrate-only-decode gate is currently a code-trace audit, not a metric assertion.** Every substrate-native cell should emit a hash-counter of LLM forward-calls at inference = 0 (baked into metrics, not audited post-hoc). Discipline-atomize as N3+ required guard before cell-author next writes.
- **The "rescue's storage-win value" question (open from 4-arm):** if ARM B's 0.998 is multi-probe (=full-key re-rank, ≈attention cost), the rescue is a recall-win not a storage-win → the substrate's value over attention diminishes. The cert-record should distinguish "recall-rescue at storage cost" from "recall-rescue at storage-win" — current MM disposition collapses both.
- **The cert-record vs program-progress alignment under Agent Teams:** fresh teammates spawn on-demand; the cert-owner's continuous-tracking discipline (15-min state-check, hourly check-ins, watchdog) was tuned to persistent-session architecture. The new architecture may need a different rhythm — spawn-triggered cert audits + Store-as-state-of-record. Open design question for Director + USER.
- **The phase_d_tier6 archive disposition:** flagged-not-demoted, but if the real-data rerun never happens (low priority post-pivot), it sits in limbo. Recommend: a periodic flagged-cert audit (~monthly) that forces a re-rule or formal demote.
- **The cert-headline negative-sub-audit (152 UNDER-CLASSIFIED atoms) is paused.** Resuming is a Director/USER call. The honest-floor estimate is ~437-440 genuine chain-grade passes (vs the 583 headline). If we resume, expect a downward correction of 50-100.

### 7g. Files / paths I reference constantly

- `data/fleet_waiting_on.md` — every turn, read FULLY (USER caught me twice missing waits).
- `notes/` (sorted by mtime, head -16) — every turn, full filenames (the addressing is in the filename).
- `data/heartbeats/skunkworks.timestamp` — touch every turn.
- `data/substrate_index/math/atoms.jsonl` + `data/substrate_index/meta/atoms.jsonl` — the canonical Store partitions (NEVER `git add -A` these; verify Store LOADS before staging).
- `data/cert_state.json` (if exists) — CERT N + axiom + cap_pres state; cross-check against PartitionedStore counts.
- `data/director_plan.json` — Director's plan-of-record; read at decision points to align with strategy.
- `tools/skunkworks_atomize_*.py` — A5-gated atomize tools (pattern: cert/axiom/modlive helpers, PRE-gate, add_atom, POST-verify); copy + modify for new atomize.
- `tools/landed_vet_*.py` — verify-off-data helpers (per_unit re-derive + cited-number-check).
- `tools/cert_integrity_audit.py` — full Store sanity check (run before major write windows).
- `experiments/<cell>.py` + `data/<cell>/metrics.json` — the cell-source + the data; read BOTH for landed-VET (verify code-trace gate + re-derive cited numbers).
- `~/.claude/projects/d--AI/memory/MEMORY.md` (index) + `feedback_*.md` + `project_*.md` — durable disciplines + program state; the durables are the rulebook.
- `CLAUDE.md` (project conventions) — read on spawn; reference for conventions only, not for live state.

### 7h. The unique-to-Skunkworks "muscle memory"

- **Always re-derive cited numbers** — the dominant audit catch. If you remember nothing else, remember this.
- **Hold the line on inflation AND deflation** — symmetric verify. Anti-negativity-bias is as load-bearing as anti-inflation-bias.
- **Verify off DATA, not reports.** The cell-author's verdict_msg is a SUMMARY, not a primary source.
- **A5 every Store write.** PRE-snapshot, add, POST-verify, re-load to catch NULL-seam. Single-writer.
- **Path-scoped commits.** Never `git add -A`/`.`. Always explicit paths + `-f` for `data/`.
- **Substrate-only-decode gate** for every LM cell. The pivot's load-bearing check.
- **Route negatives to Research** (USER standing). Every cert-negative → revival-drill routing note, same cycle.
- **Read fleet_waiting_on FULLY** before declaring idle/steady-state.
- **Atomize disciplines, not narratives.** The Store's META corpus is the self-cert rulebook.

---

— Skunkworks, 2026-06-21 (handoff for Agent Teams migration). CERT 583/177266. Last live work: N1 substrate-native LM landed MM, fly-LSH rescue ratified MM-class-level pending storage-win scrutiny, n2_capacity_scaling in-flight (decisive beat-bigram test). Best of luck to the fresh teammate; the substrate-native vision is genuinely within reach if the per_unit discipline holds.
