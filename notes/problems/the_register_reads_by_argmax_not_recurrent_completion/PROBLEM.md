---
priority: 4
review:
review_text:
---

# PROBLEM: the live situation register (and the cleanup path generally) reads out by a single-best `argmax` POINT-ESTIMATE where the brain's CA3 reads by RECURRENT PATTERN COMPLETION — the phase-diagram audit MEASURED this as an artificial capacity cliff (argmax 0.644 → joint-completion 0.971 at overload, ~4× load recovery), i.e. a READOUT artifact, not a dimensionality limit. Build the brain-faithful recurrent-completion / resonator readout, prove it recovers the overloaded regime CI-separated over argmax — AND resolve the standing tension that recurrent completion HELPS overloaded set-decode but HURTS ranked retrieval (it re-promotes hubs)

**slug:** `the_register_reads_by_argmax_not_recurrent_completion` — **opened:** 2026-08-28 by the strategy session
(surfaced + measured by the integrated `dimensional_phase_diagram_audit_of_the_current_organs`, owner-DONE/EXCELLENT: its
#1 proposed hdlab follow-on). **status:** OPEN — a BUILD + MECHANISM problem. You build + measure in `experiments/`;
strategy lands any hdlab change (Q111). There is a concrete, already-measured lever to reproduce+extend and a real
discovery tension to resolve.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4`. This is a **book-scale CAPACITY / scaling lever**,
> not a current-sentence-task win — be clear-eyed about that (see §2). The audit itself found the live register is
> STRUCTURAL at the *current* low load (the current wall is the FRONT-END linking, 0.17 vs 0.60 oracle, a different
> problem). The value here is that the register's argmax cleanup imposes an ARTIFICIAL cliff that caps how much a single
> entity/moment can hold as reading scales to book length — and the audit showed that cap is ~4× recoverable by the
> brain's own readout. **Re-rank per the owner.**

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

When the reader stores several things bound into one memory vector (an entity that did several things, a moment holding
several events) and then reads them back, it currently "cleans up" the readout by taking the SINGLE best match at each
step — an `argmax` over the cleanup dictionary (`cleanup_argmax`). This is a greedy point estimate: it commits to one
winner and throws away the rest of the evidence. The brain's hippocampal CA3 does NOT do this — it reads by **recurrent
pattern completion**: a partial/noisy cue is fed through recurrent collateral connections that settle into the nearest
stored attractor, and (for a superposed set) can be iterated to peel off multiple stored patterns jointly rather than
one-at-a-time. The phase-diagram audit measured exactly this: on an overloaded register, the argmax readout scores 0.644
while a CA3/SIC joint-completion readout scores 0.971 — **the "capacity cliff" is largely a READOUT artifact, not a
dimensionality limit.** The task: build the brain-faithful recurrent-completion readout, prove it recovers the overloaded
regime CI-separated over argmax on the REAL register/composed reader load — and RESOLVE the standing tension that the same
recurrent completion HELPS overloaded set-decode but was found to HURT ranked retrieval on the cortical store (it
re-promotes high-degree "hub" items). The deliverable is a readout that knows WHEN to complete.

## 2. WHY THIS ONE — AND ITS HONEST SCOPE

**Honest scope first (do not overclaim):** the audit found the live register is STRUCTURAL at the CURRENT sentence-scale
load — the current dominant wall is the FRONT-END linking (real 0.17 vs oracle 0.60), which is a DIFFERENT problem
(coref / meaning-supply / incremental parser). So a readout fix will be **inert on the current low-load task** — you must
NOT report a current-task win. **The value is a SCALING / capacity lever:** as reading extends to book length, a single
entity accumulates many events and a single moment holds many co-events (the fan effect), pushing the bundle toward its
cliff — and the argmax readout makes that cliff ~4× WORSE than the brain's own readout would. It also generalizes: the
`argmax` cleanup is the substrate's DEFAULT readout everywhere (register, cortical store, meaning cleanup), so getting the
readout rule brain-right is a broad fidelity fix. And it is exactly the kind of "copy the COMPUTATION (recurrent
completion), SWEEP the PARAMETER (iterations/sparsity/threshold)" the project is built on — the audit already proved the
harness can SEE the cliff, so a clean result is interpretable.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED (the computation to copy):** hippocampal **CA3 recurrent pattern completion** — dense recurrent collaterals
  form an autoassociative attractor network that completes a partial cue to a stored pattern (Marr 1971; McNaughton &
  Morris 1987; Rolls 2013; Treves & Rolls 1994). Modern-Hopfield / attractor dynamics is the computational-level model
  (Hopfield 1982; Ramsauer et al. 2020). For reading out a SUPERPOSITION of several bound patterns, the **resonator
  network** (Frady, Kent, Olshausen & Sommer 2020; Kent 2020) is the FHRR-native factored decode — iterated
  bind/unbind + cleanup that jointly resolves multiple factors where a single argmax cannot.
- **PINNED (why argmax is wrong):** a greedy single-best readout is the noise→0 argmax COLLAPSE of the graded attractor
  settle — it discards the joint evidence that lets completion separate overlapping patterns (this is the same
  discrete=argmax-collapse-of-a-graded-competition the substrate already accepted for parsing/role assignment).
- **OUR-INVENTION-UNDER-TEST (sweep, do not adopt):** the completion SCHEDULE (iteration count, stopping rule), the
  attractor sparsity/threshold, the resonator factor set, and any inhibition-of-return between peels. The brain's exact
  gamma-cycle iteration budget is a constraint we do NOT share → sweep it.
- **THE REAL DISCOVERY (the tension to resolve — this is the meat):** recurrent completion is NOT universally good.
  The integrated `the_consolidated_cortical_store_is_written_but_never_read` work found that recurrent attractor
  completion **HURTS ranked retrieval** because it re-promotes high-degree HUB items (an attractor basin is bigger for
  frequent patterns → completion pulls toward hubs, wrong for a RANKING task). Yet the audit found it HELPS overloaded
  SET-decode. Reconcile: characterize WHEN CA3 completion is the correct readout (hypothesis: completion wins for
  RECALL/set-decode from a degraded superposition, and hurts for RANK/similarity retrieval where the raw graded scores
  already carry the answer and completion adds hub bias) — and deliver a readout that applies completion PRECISELY where
  it wins, degrading to the graded scores where it does not.

## 4. MEASURED vs INFERRED
- **MEASURED (the audit, REUSE — do not re-derive):** on an overloaded register, argmax 0.644 vs CA3/SIC joint completion
  0.971 (`exp_dim_phase_diagram_cleanup_rule_v1`, `test_dim_phase_diagram.py` READOUT check); the positive-control cliff
  (flat_D256_M64 0.526 → D1024 0.988) and the info-free twin at chance are in the same harness. The sparse-code lever
  (multibank +0.497 at fixed D) is measured and DISTINCT from the readout lever.
- **MEASURED (the counter-case, REUSE):** `the_consolidated_cortical_store_is_written_but_never_read` — recurrent
  attractor completion HURTS ranked retrieval by re-promoting hubs (its logged NEW deviation).
- **MEASURED (adjacent, do not duplicate):** p2 `the_entity_store_is_a_dense_bundle_that_fans` built the FACTORIZED store
  (sparse DG + graded temporal context + SET-RETURN via CA3 reactivation) — that is a STORE-STRUCTURE fix on a SEPARATE
  island store. THIS problem is the READOUT RULE on the LIVE dense register (`situation_model_accumulate.cleanup_argmax`),
  which is un-changed. Show the two compose (readout-fix ON the current register vs SWITCHING to p2's sparse store are
  different moves; ideally quantify readout-fix alone, store-fix alone, and both).
- **INFERRED (to prove):** that a faithful recurrent-completion readout recovers the overloaded register CI-separated over
  argmax on the REAL composed-reader load, with the hub-bias failure mode characterized and gated. UNPROVEN at the
  organ/composition level (the audit's number is on the register-decode probe, not the end-to-end reader).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The audit's cleanup-rule probe (argmax vs joint completion) and positive control EXIST — **cite + reuse the machinery
  and the 0.644→0.971 number as the STARTING POINT, do not reproduce it as your result.** The NEW value is: (a) the
  brain-faithful completion built as a real readout on the LIVE register, (b) measured on the REAL reader load with floors
  + info-free twin recomputed, (c) the help-vs-hurt reconciliation delivered as a gated readout.
- Do NOT re-open p2's sparse STORE (different lever — store structure, not readout). Do NOT raise D as the fix (the audit
  ruled dimensionality out — a readout fix at FIXED D is the whole point).
- Do NOT naively apply recurrent completion everywhere — the cortical-store hub-bias result is the reason; a blanket swap
  that regresses ranked retrieval FAILS the bar.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- `tools/experiment_index.py query "cleanup"` / `"completion"` / `"resonator"` / `"attractor"` / `"capacity"` — read the
  audit's cleanup-rule harness and any existing resonator/Hopfield cells; lift their machinery.
- Read `hdlab/situation_model_accumulate.py` (the register + `cleanup_argmax` — where the readout lives),
  `hdlab/vsa_cleanup_memory.py` (the cleanup dictionary + capacity_curve), and the audit's
  `experiments/exp_dim_phase_diagram_cleanup_rule_v1.py` + `verification/test_dim_phase_diagram.py`.
- Read the cortical-store SOLVED/PROBLEM (`the_consolidated_cortical_store_is_written_but_never_read`) for the
  attractor-hurts-ranking deviation you must reconcile, and p2's SOLVED for the factorized store you must NOT duplicate.
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the newest phase-diagram entry: readout is a lever, orthogonality
  dominates N).

## 7. THE BAR
The problem PASSES only with ALL of:
1. **A brain-faithful recurrent-completion / resonator readout built on the LIVE register** (copy the computation:
   iterated attractor settle / resonator factored decode; sweep the schedule/sparsity/threshold — do not adopt a number).
2. **Recovery of the OVERLOADED regime, CI-separated over the argmax baseline, on the REAL register/composed-reader load**
   (the regime where the cliff bites — high fan / book-scale load, NOT the current low-load sentence task where it is
   correctly inert). **Recompute the strongest real floor AND an info-free twin (e.g. random-cleanup, or a
   shuffled-completion that iterates but toward random attractors) AT EACH LOAD — the twin MUST LOSE CI-separated.**
   Report CI half-width + null p95. No number crosses load-populations or scorers.
3. **DISTINGUISH the readout lever from the others:** hold D FIXED (readout-only, not more-D) and quantify readout-fix
   alone vs p2's sparse-store-fix alone vs both — so strategy knows what buys what.
4. **RESOLVE the help-vs-hurt tension:** show the SAME completion that recovers overloaded set-decode does NOT regress
   ranked retrieval (characterize the hub-bias failure mode; deliver a readout that completes where it wins and degrades
   to the graded scores where it does not). A blanket swap that helps decode but regresses ranking FAILS.
5. **A one-screen summary:** readout rule → regime → floor → twin → verdict → recommended default (and where it stays
   argmax). **Route the heavy book-scale/high-fan sweeps to REMOTE compute (standing rule).**
A rigorous NEGATIVE is a FULL PASS — e.g. "faithfully-built recurrent completion does NOT beat argmax on the real reader
load once floors are recomputed" (with the positive control confirming the harness sees the cliff) closes the audit's
open lever honestly.

## 8. FILES AND ENTRY POINTS
- Readout site: `hdlab/situation_model_accumulate.py` (`cleanup_argmax`), `hdlab/vsa_cleanup_memory.py`.
- Audit machinery: `experiments/exp_dim_phase_diagram_cleanup_rule_v1.py`, `verification/test_dim_phase_diagram.py`
  (READOUT + ADAPTATION checks), `hdlab/k_cliff_scaling.py` (the closed-form capacity control).
- Counter-case: `notes/problems/the_consolidated_cortical_store_is_written_but_never_read/`. Adjacent store: p2
  `notes/problems/the_entity_store_is_a_dense_bundle_that_fans/` + `hdlab/factorized_entity_store.py`,
  `hdlab/dg_pattern_separation.py`.
- Composed-reader load: `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py`.
- **Route heavy sweeps to REMOTE** (`tools/queue_add.py` → marsh@home). Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.

## DO NOT QUOTE / DO NOT REDO
The audit's 0.644→0.971 register-decode number is the STARTING POINT (a controlled probe), NOT your end-to-end result —
re-earn it on the real reader load with floors recomputed. The cortical-store hub-bias result is prior work to build ON
and reconcile, not to reproduce. Do NOT claim a current-sentence-task win (the readout is correctly inert there — the
front-end is that wall). Strategy owns any hdlab landing — you propose the readout rule + the gate, you do not write
`hdlab/`.
