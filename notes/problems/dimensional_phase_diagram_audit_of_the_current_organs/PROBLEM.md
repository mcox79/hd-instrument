---
priority: 4
review:
review_text:
---

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
> **🔁 THE 30-MIN DEEPENING (`CronCreate "13,43 * * * *"`)** — each fire asks "how does the brain REALLY do this,
> one level deeper?" → implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate.
> CANCEL (`CronDelete`) and submit ONLY when the brain-mechanism bar is met.
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
