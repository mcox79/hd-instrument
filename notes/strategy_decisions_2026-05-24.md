# Strategy decisions -- 2026-05-24

Owner: Strategy session (verdict_handler sub-agent invocations + main thread).
Convention: append-only; newest-first within a cycle; PROT-009 paired-commit stage with cap_map.md + history.md + active_priorities.md + visibility_decisions_<date>.md.

---

## Cycle 193 / v173 -- BATCHED PAIR envelope-narrowing verdicts (verdict_handler BATCHED-mode)

### Context

BATCHED-mode verdict_handler dispatched on TWO verdicts both NARROWING existing ✅ / 🟢 rows' envelopes. Both arrived in overnight_queue. Per the v164 / v166 / v172 BATCHED-mode precedent (multi-verdict atomic paired commit), processed together to avoid version-bump churn.

### V1 verdict context

```json
{"name":"wave14_sagawa_ueda_pareto_multiprotocol_v1","verdict":"CAP1_PARETO_KILL","verdict_msg":"Sagawa-Ueda Pareto KILL: 12/48 = 25.00% pass. Cap 1 envelope is narrow.","queue":"overnight_queue"}
```

**Significance**: Cap 1 (Crooks forensic erase ✅ via Sagawa-Ueda Tier-2 envelope at v158) passes its pre-registered Pareto criterion at ONLY 25% (12/48 cells) across 4 erasure protocols × 12 (M_base, p) cells.

### V2 verdict context

```json
{"name":"wave14_streaming_NESS_eta_sweep_v1","verdict":"NESS_BIMODAL_FRAGILE","verdict_msg":"Bimodality collapses under streaming noise. Overall fraction = 0.19 ≤ 0.30 across 16 cells. Per-eta: {'0.001': [1, 4], '0.010': [1, 4], '0.100': [0, 4], '1.000': [1, 4]}.","queue":"overnight_queue"}
```

**Significance**: v164b Cap 3 Glauber-Hopfield discrete-spin NESS extension row (🟢 at v164; explicit ✅ promotion criterion was "want N=4096+ multi-N validation") DOES NOT survive streaming-noise injection η ≥ 0.001. Bimodal P(q) FRAGILE -- 3/16 = 19% cells; at η=0.1 ZERO cells survive bimodality.

### Strategy decision -- Cap 1 row scope-clarification annotation (no revert)

**Read of Cap 1 promotion gate (per v158 cap_map narrative)**: "**Tier 2 (noisy substrate)**: Sagawa-Ueda noise-corrected bound `delta_S_emp(p) <= theta(p) + 0.02` at `p in {0.05, 0.10, 0.20}` where `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`. v158 CPU re-analysis PASS at all 3 noise levels." The v158 Tier-2 promotion is **single-protocol over 3 pre-registered p values** (canonical Crooks protocol). The multi-protocol Pareto stress test is a STRICTLY BROADER claim than what v158 promoted.

**Strategy verdict**: Cap 1 ✅ STAYS at the v158 single-protocol scope; v173 annotates the row with explicit multi-protocol scope language. NOT a revert. Per [[feedback-no-smoke]] brutal honesty: v158 never claimed multi-protocol invariance; the multi-protocol Pareto test extends to a broader claim that fails. The right move is scope-clarification annotation, not row-state demotion.

**Cap 1 row text v173 update** (annotation appended in cap_map.md "Substrate-product positioning v173" section and active_priorities.md row 4): "Tier 2 Sagawa-Ueda envelope holds at v158 single-protocol scope; under multi-protocol Pareto stress (4 erasure protocols × 12 (M_base, p) cells; 48 cells total) the envelope NARROWS to 12/48 = 25% pass -- the substrate's Tier-2 forensic-erase bound is protocol-dependent, not protocol-invariant. Single-protocol envelope at v158 pre-registered scope UNAFFECTED. 6th-candidate elective rescue sketch: protocol-conditioned Sagawa-Ueda calibration (per-protocol theta_protocol(p) re-axiomatization analogous to v158 Sagawa-Ueda-from-Crooks)."

**v169 closed-form annotation PRESERVED**: V1's multi-protocol stress test does NOT touch the Clifford-design / Pauli-channel lens. The closed-form annotation is about the *form* of the noise-corrected bound (Pauli-twirl gives theta(p) = ln(2) + p·ln(p) + (1-p)·ln(1-p)), which is unchanged across protocols at the single-protocol scope where v158 was promoted. The multi-protocol narrowing is about WHICH ERASURE PROTOCOL the bound applies to, not about the FORM of the bound. v169 annotation stands.

### Strategy decision -- Cap 3 v164b extension row zero-noise scope-tightening annotation (main Cap 3 ✅ row UNTOUCHED)

**Read of Cap 3 v164b extension row scope (per v164 cap_map narrative)**: "Cap 3 Glauber-Hopfield discrete-spin NESS extension. **State**: 🟢 Validated, want stronger (single-N N=1024 12/18 low-T cells; want N=4096+ + multi-seed >= 5)." The v164b extension was ALWAYS 🟢 (not ✅); the ✅ promotion criterion was unmet. V2's streaming-noise test is a third stress axis (noise-tolerance) layered on the unmet multi-N requirement.

**Strategy verdict**: Cap 3 v164b extension row STAYS at 🟢 with v173 zero-noise scope-tightening annotation. Main Cap 3 ✅ row UNCHANGED -- V2 targets the discrete-spin extension under streaming noise, which is a different observable family than the main row's continuous-state drift-diffusion NESS under bit-flip noise. Per [[feedback-dont-overextend-theorems]] no row-state demotion needed (the row was never promoted to ✅); the v164b row's claim scope is narrowed to zero-noise Glauber dynamics only.

**v164b extension row v173 annotation text** (appended in cap_map.md "Substrate-product positioning v173" section and active_priorities.md row 7 note): "extends to Glauber-Hopfield bimodal P(q) at low T in ZERO-NOISE Glauber dynamics; FRAGILE under streaming-noise injection η ≥ 0.001 -- 13/16 = 81% of cells lose bimodality under noise; at η=0.1 ZERO cells survive bimodality; v164b extension does NOT compose cleanly with the streaming-NESS framing of the main Cap 3 ✅ row. v164b 🟢 row's scope is explicitly NARROWED to ZERO-NOISE Glauber dynamics; pending N=4096+ multi-N validation (unmet) the row stays 🟢 at the narrower scope."

**v169 Cap 3 Holevo-capacity closed-form annotation PRESERVED**: V2 targets the v164b Glauber-Hopfield discrete-spin extension row, not the main Cap 3 ✅ row's continuous-state drift-diffusion NESS. The Holevo-capacity annotation lives on the main row and is unchanged.

### Strategy decision -- inefficiency LOCK candidate (RECOMMENDED LOCK not DEFER)

Both v173 verdicts surfaced envelope-expansion drills that lacked PRE-REGISTERED fail bands matching the broader claim being tested. Per [[feedback-strategy-shore-up-capabilities]] envelope-expansion drills SHOULD include explicit "fail bands" -- without them the verdict_handler is forced into post-hoc scope-clarification work. This is the SECOND observation (first was v157 Cap 1 narrowing → v158 Sagawa-Ueda re-axiomatization; v173 is the second instance). Two observations meets the two-observation lock threshold.

**RECOMMENDED LOCK** (not DEFER): file as memory_curator addendum to [[feedback-strategy-shore-up-capabilities]]:

> "Envelope-expansion drills MUST include pre-registered fail bands matching the broader claim being tested. When a Cap N capability is being stress-tested at a broader scope than the original promotion (e.g., multi-protocol for Cap 1 single-protocol promotion; streaming-noise for Cap 3 v164b zero-noise extension), the pre-reg MUST state explicit PASS / PARTIAL / FAIL thresholds for the BROADER claim, so the verdict read at completion is unambiguous and verdict_handler does not have to do scope-clarification reasoning post-hoc."

Consistent with the v171 "compound-gate promotion discipline" addendum to [[feedback-dont-overextend-theorems]]; both are about EXPLICIT PRE-REGISTRATION OF SCOPE in stress tests.

### Strategy follow-up actions (cycle 193)

1. **PROT-009 v173 paired commit** -- 87th observation.
2. **NO new Research routing filed this cycle**. The v173 envelope-narrowings are annotation-level and do NOT trigger Research drills per [[feedback-negative-results-2x-research]] -- envelope-narrowing within a pre-registered scope test is an expected-boundary measurement at the broader claim level. Elective rescue sketches noted (protocol-conditioned Sagawa-Ueda calibration for Cap 1; multi-N Glauber-Hopfield without streaming noise for Cap 3 v164b 🟢 → ✅ promotion) are filed in active_priorities under row notes, NOT routed to Research bandwidth this cycle. The v172 close-out already exhausted Cap 2 / Bet T rehab cycles.
3. **active_priorities.md** updated atomically v172 -> v173: Cap 1 row 4 annotated with v173 multi-protocol envelope-narrowing scope-clarification; Cap 3 row 7 annotated with v173 v164b zero-noise scope-tightening; substrate-physics characterization line UNCHANGED.
4. **NO Exp Dev routing filed** per [[feedback-dispatch-wrappers-default]].
5. **NO queue-refill triggered** per [[feedback-pipeline-pacing]]: pipeline healthy (GPU=2 pending+1 running, remote CPU=2 pending+1 running with BBMD rehab anchors picking up, local CPU idle).
6. **Inefficiency LOCK candidate filed**: "envelope-expansion drills require pre-registered fail bands matching the broader claim being tested" -- RECOMMENDED LOCK not DEFER (two-observation threshold met).

### Files filed this cycle

- `notes/substrate_capability_map.md` -- Cycle 193 narrative + Capability moves table appended.
- `notes/substrate_capability_map_history.md` -- v173 one-line index entry appended.
- `notes/active_priorities.md` -- header updated v172 -> v173; Cap 1 + Cap 3 row annotations.
- `notes/strategy_decisions_2026-05-24.md` -- this entry (FIRST entry on new date file).
- `notes/visibility_decisions_2026-05-24.md` -- 2 status_log entries appended (V1 MEDIUM; V2 MEDIUM).
- No new Research request file. No new Exp Dev request file.

### Queue / push status

- Local commit only (sub-agent push blocked per [[feedback-subagent-permission-inheritance]]); main thread executes push.
- Queue-refill NOT triggered. Queue depth ≥ 1 invariant satisfied.

### Tally (one-line)

PAIR OF VERDICTS v172 -> v173: (V1) CAP1_PARETO_KILL 12/48 = 25.00% -- Cap 1 ✅ STAYS at v158 single-protocol scope + v173 multi-protocol envelope-narrowing annotation (protocol-dependent, not protocol-invariant); (V2) NESS_BIMODAL_FRAGILE 3/16 = 19% -- Cap 3 v164b 🟢 STAYS at 🟢 with v173 zero-noise scope-tightening annotation; main Cap 3 ✅ row UNCHANGED; portfolio count UNCHANGED at 11; ZERO open ❌ PROVISIONAL preserved from v172; v169 closed-form annotations PRESERVED; per [[feedback-no-smoke]] scope-clarification not demotion; PROT-004/006 NOT triggered; PROT-008 0 new ❌; PROT-009 87th paired commit; 2 MEDIUM status_log entries; inefficiency LOCK candidate (envelope-expansion drills require pre-reg fail bands); pause flag CLEARED -- ACTIVE.
