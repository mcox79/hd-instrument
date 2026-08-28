---
priority:
review: EXCELLENT
review_text: "A rigorous, decisive NEGATIVE on the owner's question — dimensionality (N) is NOT a performance lever anywhere in the substrate — re-verified 18/18 FIRST-HAND (positive-control cliff SEEN 0.526→0.988, info-free twins at chance). Real-task register decode FLAT across D=256..8192 (STRUCTURAL, wall is front-end linking not capacity), meaning sparse-EXACT (no fixed D), memory stores were ALREADY at N_DIM=8192 → the brief's 'all at D=1024, never swept' premise is FALSE on disk. Goes BEYOND the bar: a 4-law store-family census (bundle ~N/log2N vs matrix-Hebbian ~16N differ ~190x), and it identifies the REAL fidelity axis — CODE ORTHOGONALITY dominates N (ρ0.0→0.65 vs ρ0.8→0.03; real WordNet codes ARE correlated, DG decorrelation recovers 0.74→0.98). TWO integrity self-corrections raise trust: its synthetic cliff REPRODUCES the existing closed-form k_cliff_scaling (a positive control, not a new law) and its 'multihop directedness defect' was on a NAIVE commutative store — the real kg_traversal organ is directed by construction (8-hop clean) → downgraded to a caution, not a substrate gap. Routed the +0.88 cortical-read headroom to the FILED problems rather than claiming it (Q113). NO hdlab landed by the solver (correct — it's a negative); proposed follow-on landings queued."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT)
> **Re-verified FIRST-HAND** (`verification/test_dim_phase_diagram.py`, **18/18 PASS**, 0 fail — suspected my own checker, ran
> the live recompute myself). Positive control fires (`flat_D256_M64` 0.526 collapses vs `flat_D1024_M64` 0.988 recovers → the
> harness demonstrably SEES a cliff); info-free random-key twin at chance (0.013 ≈ 1/100).
> **Result (answers the owner's exact question, a full-pass NEGATIVE on N):** dimensionality is NOT a lever anywhere.
> (1) The load-sensitive REGISTER: real-task oracle decode is FLAT across D=256..8192 (0.60→0.61, CIs overlap) → **STRUCTURAL**
> at D=1024; the wall is front-end LINKING (ACT-R 0.17 vs oracle 0.60), not capacity. (2) MEANING is sparse-EXACT (K*≈256, not
> rising at 1024). (3) The memory stores were ALREADY pinned to N_DIM=8192 on disk → the brief's "all at D=1024, never swept"
> premise is **false on disk** (verified). So the composed reader's modest absolute numbers are NOT a D-artifact.
> **Argument audit (not just arithmetic):** the NEGATIVE is interpretable precisely because the positive control + the
> per-D-recomputed floors + info-free twins (all losing) rule out a blind harness. The BEYOND-N axes behave coherently:
> orthogonality is a strong lever (ρ0.0 0.651 vs ρ0.8 0.026), binding DEPTH is not (depth1≈depth5), precision bites only at
> q=2 (sign-binary 0.311 vs full 0.653), and a CA3/SIC joint-completion readout recovers the register cliff (argmax 0.644 →
> 0.971) — i.e. the register "cliff" is largely a **readout** artifact, not dimensions.
> **Two integrity self-corrections (the mark of quality — carried into the audit):** (a) the solver's synthetic cliff
> REPRODUCES the existing closed form `hdlab.k_cliff_scaling.k_cliff(N)=0.87·N/log2(N)` → it is a positive control on the
> harness, explicitly NOT claimed as a new law. (b) Its first-pass "multihop directedness DEFECT" was on a NAIVE
> commutative-bind edge store; the substrate's REAL multihop organ (`kg_traversal.KGStore` + `multi_hop`) is directed by
> construction (relation-typed key + asymmetric Hebbian W) and reasons perfectly to 8 hops at every D → **downgraded to a
> naive-storage caution, NOT a substrate gap**. Both are exactly the honest self-correction the operating protocol asks for.
> **Store-family census (beyond the bar):** the substrate runs FOUR distinct capacity laws — vector-bundle ~N/log2(N)
> (register + `vsa_cleanup_memory.capacity_curve` cross-validate), sparse Willshaw > bundle (DG raises it), matrix-Hebbian
> relational ~16·N (~190× the bundle — the actual multihop memory), multi-timescale temporal (floor set by the PERIOD
> spectrum, not 1/√D). **No single capacity number crosses families** — recorded so nobody quotes one across them.
> **Brain-fidelity / AUDIT:** the dominant fidelity axis is CODE ORTHOGONALITY / FEATURE_OVERLAP, not N — real WordNet codes
> are correlated (0.039 vs 0.025 ideal) and cost capacity; DG sparse pattern separation recovers it (dense M32 0.742 → DG
> sparse 0.979). This reinforces the audit's standing flag that our iid-random / maximal-orthogonality code is an unflagged
> OUR-INVENTION. Folded to §2b (+ the register-STRUCTURAL@1024 verdict + the not-uniformly-D=1024 correction).
> **To the solver's credit:** it routed the biggest LIVE lever — the cortical/consolidated READ regime (+0.88 generalisation
> headroom: a distributed semantic cue retrieves at 1.00 where the exact-key hash reads ~chance 0.11) — to the ALREADY-FILED
> problems (`the_consolidated_cortical_store_is_written_but_never_read`, `cortical_read_never_tested_where_it_matters`) rather
> than claiming it under this slug (Q113 role-separation). Datapoint attached there.
> **hdlab:** NONE landed by the solver (correct — Q111, and a negative needs none). **PROPOSED follow-on landings QUEUED (NOT
> this commit — substantial builds, some overlapping p2): (1) swap the register argmax cleanup for CA3/resonator JOINT
> completion (the ~4× readout lever); (2) add code-orthogonality + numeric-precision as first-class audit axes + a
> DG-decorrelation check before autoassociative storage; (3) optionally the confidence-gated ADAPTIVE readout controller.**
> DO NOT (carried from the submission): raise D anywhere as a capacity fix (ruled out); build a multihop directedness fix
> (already handled); quote any single capacity number across store families. Honest scope: this is a DIAGNOSTIC — it changes
> INTERPRETATION (the fidelity lever is orthogonality/readout/sparsity, not dimensions), it does not itself add capability.
> *Note: the solver's own 20-min deepening cron lives in the SOLVER's session (crons are session-scoped) — not deletable from
> here and harmless (a deepening probe on a now-closed problem); it lapses with that session.*

# PROBLEM: every current reader organ + the composition was validated at ONE fixed dimensionality (D=1024 default) and NEVER swept — run the dimensional phase-diagram audit and classify each observed ceiling as STRUCTURAL vs UNDER-DIMENSIONED, recomputing the floor + info-free twin AT EACH D

**slug:** `dimensional_phase_diagram_audit_of_the_current_organs` — **opened:** 2026-08-27 by the strategy session
(owner-surfaced: "is it worth running a substrate-wide phase-diagram evaluation? I'm not sure we probed each piece at
full dimensionality"). **status:** OPEN — a DIAGNOSTIC + MECHANISM problem. You build + measure in `experiments/`;
strategy lands any hdlab change (Q111). There are concrete ceilings to adjudicate and a can-fail bar.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` (back of the open queue) because it is a
> PARALLEL, NON-BLOCKING diagnostic — it does not gate p1/p2/p3, it runs on remote compute alongside them. **But it is
> arguably HIGHER leverage than its rank suggests: it de-risks the INTERPRETATION of every consolidation number at once
> (if a ceiling is a dimensionality artifact, the fidelity lever is elsewhere). PROMOTE it if you want it to lead.** Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE

Every piece of the reader is stored at one fixed "resolution" — a dimensionality of 1024 numbers per concept/memory
(`D = 1024`, the project default). The brain does NOT have a fixed resolution; we CHOSE 1024 for convenience and never
checked whether it is enough — or too much — for each piece. This matters because superposition memories have a sharp
**capacity cliff**: pack too many things into too few dimensions and retrieval collapses. So some organ that looks like
it has hit a ceiling might just be **starved of dimensions** (a fixable artifact), and some past "wall" we blamed on the
mechanism might have been **under-dimensioned** all along. **This has already bitten us once — a 256-dimension capacity
bottleneck was misread as an ABILITY limit.** The task: for each current organ AND the composed reader, systematically
vary D (and memory load, where relevant), and for every observed ceiling deliver a VERDICT — **STRUCTURAL** (stays flat
as you add dimensions → the mechanism truly is the limit, dimensionality is NOT the lever) or **UNDER-DIMENSIONED**
(still climbing at D=1024 → we are leaving capability on the table; raise D and re-adjudicate).

## 2. WHY THIS ONE

It de-risks the INTERPRETATION of the entire consolidation in one pass. Right now we cannot tell whether the composed
reader's modest absolute numbers (entity-solo 0.167, entity×meaning 0.119) are a real mechanism ceiling or a
capacity-cliff artifact of a fixed D=1024 carrying the entity fan-load. Dimensionality is a documented confound here,
and "flat result = broken experiment, not a ceiling" / "don't call a narrow failure impossible" are standing disciplines
this directly serves. It is also brain-faithful hygiene we owe ourselves: **copy the computation, SWEEP the parameter** —
D is a parameter (the brain's is enormous), and we adopted a number instead of sweeping it.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED (a math fact of superposition codes, not an invention):** VSA/HDC capacity theory (Frady, Kleyko & Sommer
  2018 "resonator/capacity"; Plate 1995; Gallant & Okaywe 2013) — for M items bundled in dimension D, retrieval SNR
  scales ~ √(D/M), producing a SHARP accuracy cliff at a critical load M*(D). The cliff is a phase transition (order
  parameter), which is why "phase diagram" is the right instrument.
- **PINNED (brain framing):** cortical/hippocampal dimensionality is set by EFFICIENT CODING (Laughlin) at a scale far
  above ours (millions of units/area) — the brain sits FAR from its cliff. Dimensionality is a parameter we do NOT share
  → **sweep it, never adopt a number** (the project's own discipline; our WORST result copied a number).
- **OUR-INVENTION-UNDER-TEST:** `D = 1024` as the one-size default for every organ. This audit is the test of it.
- **The brain-faithful REASON a piece might need more D:** the fan effect (an entity accumulating many events) raises the
  bundle load M → pushes that organ toward its cliff. Sparsity (p2's DG+CA3) is the brain's fix for load, NOT more D — so
  the audit must DISTINGUISH "needs more D" from "needs sparse coding" (they are different levers; see §7).

## 4. MEASURED vs INFERRED
- **MEASURED (historical, on the OLD primitives — REUSE, do not re-derive):** bundle SNR scaling
  (`exp_bundle_snr_scaling_cpu_v1`, HARD_FAIL), sequence-binding capacity cliffs
  (`exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1`), order-parameter/phase probes
  (`exp_bid_order_parameter_v1`), `exp_capacity_binds_c3_v1` — 560+ "capacity" / 856 "phase" indexed cells exist. The
  d=256 capacity-bottleneck misdiagnosis is on record.
- **MEASURED (current organs, all at FIXED D=1024, never swept):** entity register decode 0.167 (STEP-13/18),
  entity×meaning composition 0.119 (STEP-18), the fan slope 0.695→0.608 (entity integration). Meaning uses GloVe-300 /
  WordNet — its "D" is the embedding width, also fixed.
- **INFERRED (to test):** whether ANY of these ceilings move with D. UNPROVEN. A clean NEGATIVE (all saturated at
  D=1024) is a valuable PASS — it says dimensionality is not a lever and refocuses effort on mechanism.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The low-level primitive phase diagrams (bundle/binding/sequence capacity, SNR) EXIST (§4). **Cite + REUSE their
  machinery and theory; do NOT re-derive them.** The NEW value is at the CURRENT-ORGAN + COMPOSITION level, at full D,
  with recomputed floors.
- Do NOT re-open p2's store-sparsity fix — this audit MEASURES where the register sits vs its cliff (which informs p2),
  it does not build the sparse store.
- Do NOT treat this as a request to raise D globally. The deliverable is a per-organ VERDICT + the specific D where each
  saturates, not a blanket dimension bump.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- `tools/experiment_index.py query "capacity"` / `"phase"` / `"snr"` — read the existing capacity-cliff harnesses; lift
  their SNR/order-parameter machinery.
- Read `hdlab/situation_model_accumulate.py` (the register — where D enters; the most load-sensitive organ) and
  `experiments/exp_litbank_entity_tracking_end_to_end_v1.py` (`D = 1024`).
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b + the CONSOLIDATION_PHASE_LOG STEP-13/18 numbers you will re-probe.

## 7. THE BAR
The audit PASSES only with ALL of:
1. **A phase curve per current organ + the composed reader:** accuracy vs D (a real sweep, e.g. D ∈ {256, 512, 1024,
   2048, 4096, 8192}), AND vs load/fan for the load-sensitive ones (the register). **RECOMPUTE the strongest real floor
   AND the info-free twin AT EACH D** — no number crosses D-populations; a curve of accuracy without its floor at each D
   is a vanity plot and fails this bar.
2. **A per-ceiling VERDICT:** STRUCTURAL (accuracy flat within CI across the top of the D-range, twin still losing at our
   operating point) vs UNDER-DIMENSIONED (accuracy CI-separated-RISING at D=1024 → below the knee). Name the saturation D.
3. **A POSITIVE CONTROL that the harness can SEE a cliff:** reproduce ONE known capacity cliff (e.g. bundle SNR vs load)
   so a "flat/structural" verdict is not just a blind harness. Without this, a null is uninterpretable.
4. **DISTINGUISH the two levers where a ceiling IS dimensionality-sensitive:** show whether adding D vs adding SPARSITY
   (fixed D, sparse code) buys the recovery — this tells strategy whether the fix is "more dimensions" or "p2's sparse
   store," which are different brain-faithful moves.
5. **A one-screen SUMMARY TABLE:** organ → operating D → verdict → saturation D (or "structural") → recommended action.
A rigorous NEGATIVE ("every current organ is already saturated at D=1024; dimensionality is not a lever anywhere",
positive-control confirming the harness sees cliffs) is a FULL PASS — it closes the question the owner raised.

## 8. FILES AND ENTRY POINTS
- Historical machinery: `exp_bundle_snr_scaling_cpu_v1`, `exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1`,
  `exp_bid_order_parameter_v1`, `exp_capacity_binds_c3_v1` (via `tools/experiment_index.py query`).
- Current organs: `hdlab/situation_model_accumulate.py`, `hdlab/salience_binder.py`, `hdlab/conceptual_meaning.py`,
  `hdlab/graded_role_assigner.py`. Composition harness: `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py`.
- **Route the heavy sweeps to REMOTE compute** (`tools/queue_add.py` → marsh@home; standing rule: heavy/long runs go remote).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md`. Log: `notes/CONSOLIDATION_PHASE_LOG.md`.

## DO NOT QUOTE / DO NOT REDO
The historical primitive phase diagrams are PRIOR WORK to build ON and credit, not to reproduce as your result. The
D=1024 numbers (0.167, 0.119) are the FIXED-D baselines you are re-probing across D, not results to restate. Strategy
owns any hdlab landing — you propose the change (a per-organ operating D), you do not write `hdlab/`.
