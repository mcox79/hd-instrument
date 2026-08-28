---
priority:
review: EXCELLENT
review_text: "Owner-DONE. The flagged fidelity wall is RESOLVED: the register's per-component bundle renorm (S_i/|S_i|, hdlab/bundling.py default — a non-invertible per-channel magnitude-erasure) is the OUR-INVENTION outlier that breaks the theta-gamma serial readout; the brain-faithful fix is POOLED divisive normalization (Carandini & Heeger 2012 — ONE shared scalar over the pool), which preserves the linear structure exactly and serves BOTH readouts. Re-verified FIRST-HAND (`verification/test_register_divisive_norm.py`, ALL 8 checks PASS — ran it myself). Copy-the-computation / sweep-the-parameter done cleanly: RESULT (D=256 FIXED, V=100, per-slot filler-recovery, bootstrap CI over entities) serial:per-component 0.367 → serial:divisive 0.988 @M=64, +0.62 CI-sep [+0.58,+0.62] hw 0.037; TIES the raw-sum ceiling at every load (Δ<0.001); argmax NO-REGRESSION and in fact improves 0.529→0.644 (scale-invariant → bit-identical to raw-sum argmax); info-free shuffled-key twin 0.027 LOSES CI-sep; PARAMETER-FLAT (serial=1.000 across every C-H sigma AND homeostatic target → the OPERATION, not a tuned number). POSITIVE CONTROL (the strength): even the best gain-matched serial readout CANNOT recover the per-component store (0.367 vs 0.988) — isolates the STORE norm, not the readout, as the constraint, and the harness sees the break at M≥48 while M=8 is fine. The brief's fidelity question is answered POSITIVELY: one divisive normalization serves BOTH the argmax cleanup AND the serial readout — NO raw-sum shadow copy needed (store & readout norm must MATCH: naive serial on a scaled store 0.117 → pooled-gain 0.988). COMPOSE (measured, not inferred): on the DEFAULT multibank backend in the compose regime (M=384/8 banks, k_per_bank≈60) the norm fix recovers serial 0.733→1.000 (+0.29 CI-sep) and argmax 0.654→0.765 — so the p2 store-distribution lever and this norm fix are the 12-16× compose, now measured with the norm in place. SCRUPULOUS brain-fidelity discipline (2 adversarial literature drills tasked to REFUTE): pooled divisive normalization is DIRECTLY CONFIRMED in sensory/decision cortex but its application to a WM/memory register is labeled OUR-EXTENSION-UNDER-TEST (not PINNED; closest pooled precedent Eliasmith NEF/SPA near-unit-radius + Frady/Kleyko/Sommer 2018), while the NEGATIVE half is stronger — per-component instantaneous magnitude-erasure has NO fast biological analogue (Turrigiano scaling is slow/weight-level/structure-PRESERVING). HONEST scope (withdraw-first): M≥96 is a TRUE capacity bound (divisive serial == raw-sum serial there, both fall) NOT a norm win — the M-transition IS the brain's WM→episodic (CLS) boundary (normalize a bounded bundle vs sparse-pattern-separate a large one = the p2 lever); real-narrative D=1024 load inherited from the parent (divisive serial == raw-sum serial, proven, so the parent's 0.959→1.000 high-fan recovery transfers), not re-run; write-stability moot (AccumulateRegister is stateless — register() re-bundles fresh each read). Directly COMPLEMENTS the `decode_serial` I landed this session (which reads the RAW sum to bypass the renorm): decode_serial_pooled is the gain-matched generalization (g≈1 on raw sum → reduces to the landed decode_serial). Applied the owner's evaluate-adjacent-components directive (`ADJACENT_COMPONENTS_brain_fidelity_map.md`): a GENERAL substrate rule surfaced — every `bundling.bundle` caller is READ-terminal (none re-bind), so the per-component default is sub-optimal substrate-wide, and the `sign()`-on-a-bundle sites are the SAME wrong-op — folded to the audit as a candidate follow-on. hdlab landing QUEUED (Q111, careful COUPLED port, default-off/opt-in): `norm=\"divnorm\"` on `bundling.bundle` + a `bundle_norm=\"percomp\"` (default) constructor arg on AccumulateRegister/multibank + the gain-matched `decode_serial_pooled` — land TOGETHER (the store option without the gain-matched readout breaks serial callers)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT; owner_verdict: DONE)
> **Re-verified FIRST-HAND** (`verification/test_register_divisive_norm.py`, ALL 8 checks PASS — ran it myself).
> **Result:** the register's per-component bundle renorm (`S_i/|S_i|`, `hdlab/bundling.py` default — a non-invertible
> per-channel magnitude-erasure) is the OUR-INVENTION outlier that breaks the theta-gamma serial readout; the
> brain-faithful fix is **POOLED divisive normalization** (Carandini & Heeger 2012 — one shared scalar over the pool),
> which preserves the linear structure exactly and serves BOTH readouts.
> **Argument audit (not just arithmetic) — the controls + the honesty are the strength:** (a) serial:per-component 0.367
> → serial:divisive **0.988 @M=64, +0.62 CI-sep** (hw 0.037), TIES the raw-sum ceiling at every load; (b) argmax
> NO-REGRESSION and IMPROVES 0.529→0.644 — scale-invariant, so a scalar-normed store gives **bit-identical** argmax to
> raw-sum (no-regression proven by identity, not just CI); (c) **POSITIVE CONTROL (the strongest move):** even the
> gain-matched serial readout CANNOT recover the per-component store (0.367 vs 0.988) → the constraint is the STORE norm,
> not the readout, and the harness sees the break at M≥48 while M=8 is fine; (d) info-free shuffled-key twin 0.027 LOSES
> CI-sep; (e) store & readout norm must MATCH (naive serial on a scaled store 0.117 → pooled-gain 0.988); (f)
> PARAMETER-FLAT (serial=1.000 across every sigma + homeostatic target) → the OPERATION, not a tuned number.
> **The brief's fidelity question, answered POSITIVELY:** one divisive normalization serves BOTH the argmax cleanup AND
> the serial readout — no raw-sum shadow copy needed.
> **COMPOSE (measured):** on the DEFAULT multibank backend (M=384/8 banks, k_per_bank≈60) the norm fix recovers serial
> 0.733→1.000 (+0.29 CI-sep) and argmax 0.654→0.765 — the p2 store-distribution lever and this norm fix are the 12-16×
> compose, now measured with the norm in place, not inferred.
> **Brain-fidelity discipline (2 adversarial literature drills tasked to REFUTE):** pooled divisive normalization is
> DIRECTLY CONFIRMED in sensory/decision cortex, but its application to a WM/memory register is honestly labeled
> **OUR-EXTENSION-UNDER-TEST** (not PINNED; pooled precedent Eliasmith NEF/SPA, Frady/Kleyko/Sommer 2018); the NEGATIVE
> half is stronger — per-component instantaneous magnitude-erasure has NO fast biological analogue (Turrigiano scaling is
> slow/weight-level/structure-PRESERVING). **Honest scope (withdraw-first):** M≥96 is a TRUE capacity bound (divisive
> serial == raw-sum serial, both fall) NOT a norm win — the M-transition IS the WM→episodic (CLS) boundary, i.e. the p2
> sparse-store lever; real-narrative D=1024 load inherited from the parent (divisive serial == raw-sum serial → the
> parent's 0.959→1.000 high-fan recovery transfers), not re-run; write-stability moot (stateless register).
> **Reconciled with this session's landing:** directly complements the `decode_serial` I landed this session (reads the
> RAW sum to bypass the renorm); `decode_serial_pooled` is the gain-matched generalization (g≈1 on raw sum → reduces to
> the landed `decode_serial`). **Applied the owner's evaluate-adjacent-components directive** (`ADJACENT_COMPONENTS_brain_fidelity_map.md`):
> a GENERAL substrate rule — every `bundling.bundle` caller is READ-terminal (none re-bind), so the per-component default
> is sub-optimal substrate-wide, and the `sign()`-on-a-bundle sites are the SAME wrong-op — folded to the audit (§2b + the
> per-component-normaliser scope) and flagged as the next candidate brief. **AUDIT UPDATE folded (§2b).**
> **hdlab landing QUEUED (Q111 — careful COUPLED port, default-off/opt-in; NOT this commit):** `norm="divnorm"` on
> `bundling.bundle` (pooled Carandini-Heeger) + a `bundle_norm="percomp"` (default) constructor arg on
> `AccumulateRegister`/`situation_model_multibank` threading into the `register()`/`_bank_register()` bundle calls + the
> gain-matched `decode_serial_pooled` method. Land TOGETHER (the store option without the gain-matched readout would break
> any serial caller assuming raw scale); default `"percomp"` keeps every current caller bit-identical until opted in.


# PROBLEM: the situation register bundles superposed traces with a PER-COMPONENT RENORMALIZATION, and that renorm is not brain-faithful — it BREAKS the theta-gamma serial decode-and-suppress readout (serial_renorm 0.119 << serial_rawsum 0.983 at overload). Determine the brain-faithful bundling/normalization for a superposition register (does the brain renormalize a population sum per-component, or preserve the linear sum with divisive/homeostatic gain?), build it, and prove it PRESERVES the serial-readable linear structure without regressing capacity — CI-separated over the current renorm, twin losing

**slug:** `the_register_bundle_renorm_breaks_the_serial_readout` — **opened:** 2026-08-28 by the strategy session (the
STRONGEST adjacency flagged by the integrated `the_register_reads_by_argmax_not_recurrent_completion`, owner-DONE). **status:**
OPEN — a FIDELITY + MECHANISM problem. You build + measure in `experiments/`; strategy lands any hdlab change (Q111).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — a clean, focused, brain-fidelity gap with an
> already-measured effect: the register's per-component bundle renorm collapses the theta-gamma serial readout that
> recovers overloaded capacity (0.119 vs 0.983). Getting the normalization brain-right unlocks the readout lever the
> register-readout problem proved. **Re-rank per the owner.**

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
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
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
The situation register stores many bound traces SUPERPOSED (added) into one vector, then renormalizes. The
register-readout integration found that the brain reads such a superposition by theta-gamma SERIAL decode-and-suppress
(decode the strongest, suppress it, decode the next from the residual) — but this only works on the RAW LINEAR SUM. The
register's current PER-COMPONENT bundle renormalization destroys that linear structure: the serial readout collapses
(serial_renorm 0.119 vs serial_rawsum 0.983 at overload M=64). So a non-brain-faithful normalization choice is silently
capping the register's readable capacity. The task: figure out how the brain actually normalizes a population-coded
superposition (does it renormalize each component, or preserve the summed vector and apply DIVISIVE/HOMEOSTATIC gain
control at readout?), build the brain-faithful version, and prove it PRESERVES the serial-readable linear structure
(and the argmax path) without losing capacity — CI-separated over the current renorm, with an info-free twin losing.

## 2. WHY THIS ONE
It is the fidelity gap standing between the register and the proven ~2× readout lever (and its 12–16× compose with the
sparse store). A clean, bounded, high-fidelity fix: get the normalization brain-right and the serial readout works on
the real register, not just a synthetic raw-sum. It also touches a general substrate choice (how every bundle store
normalizes), so the answer generalises.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** cortical/hippocampal population codes SUM inputs (linear superposition on the dendritic
  tree) and control magnitude by DIVISIVE NORMALIZATION (Carandini & Heeger 2012 — a canonical cortical computation:
  the summed response is divided by a POOLED gain, not renormalized per component) and homeostatic gain/synaptic
  scaling (Turrigiano 2008). The linear sum is preserved; gain is applied at the pool/readout, which is exactly what
  keeps a superposition SERIALLY decodable (the strongest component stays largest; suppress-and-repeat works). VSA/HDC
  theory agrees: bundling is addition; normalization is a scalar/divisive step that preserves relative structure
  (Plate 1995; Kanerva 2009).
- **OUR-INVENTION-UNDER-TEST (the suspect):** the register's PER-COMPONENT renorm (each dimension rescaled) — a choice
  we made, not one the brain makes; it is what breaks the linear readout. SWEEP the normalization: raw-sum,
  scalar/divisive (pooled) normalization, homeostatic gain, unit-norm — copy the divisive-normalization COMPUTATION,
  sweep the pool/gain parameter.
- **The fidelity question to answer:** is per-component renorm ever justified (e.g. for the argmax cleanup or write
  stability), and can a divisive/homeostatic normalization serve BOTH the argmax path AND the serial readout?

## 4. MEASURED vs INFERRED
- **MEASURED (REUSE):** `the_register_reads_by_argmax_not_recurrent_completion` measured serial_renorm 0.119 <<
  serial_rawsum 0.983 @M64 (the renorm breaks serial), with an argmax_rawsum control isolating it; the serial readout +
  its witness are on disk (`experiments/exp_register_completion_readout_v1.py`, `verification/test_register_completion_readout.py`).
- **INFERRED (to prove):** which normalization is brain-faithful AND serves both readouts, and whether swapping it in
  recovers the serial readout on the REAL register without regressing the current argmax path or write stability.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-derive the readout result — REUSE it as the starting measurement. Do NOT change the STORE structure (that is
  p2 / the sparse-store line) — this is about the NORMALIZATION of the bundle, holding the store fixed.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_model_accumulate.py` (the AccumulateRegister + where the per-component renorm lives),
  `hdlab/bundling.py` / `hdlab/vsa_cleanup_memory.py`, and the register-readout cells + witness above.
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the register-readout entry names this bundle-renorm fidelity gap).
- `tools/experiment_index.py query "renorm"` / `"bundle"` / `"normalization"`.

## 7. THE BAR
PASSES only with ALL of:
1. A brain-faithful normalization for the superposition register (copy divisive/homeostatic normalization; sweep the
   pool/gain), built on the LIVE `AccumulateRegister` (holding the store fixed).
2. It PRESERVES the serial-readable linear structure: the theta-gamma serial readout on the normalized register recovers
   the overloaded regime CI-separated over the current per-component renorm (serial_renorm ~0.12 → target ~raw-sum),
   recompute per load; an info-free twin (shuffled-key serial / random normalization) LOSES CI-separated; report CI
   half-width + null p95. A positive control that the harness sees the renorm break the readout.
3. NO REGRESSION on the paths the register already serves: the argmax cleanup + write stability are preserved
   (byte-or-CI-equal on the current tasks) — the new normalization must not trade one readout for another.
4. One-screen summary (normalization → serial recovery → argmax no-regression → verdict). Heavy → REMOTE.
A rigorous NEGATIVE is a full pass (e.g. "per-component renorm is actually required for write stability and no divisive
normalization serves both readouts — so the serial readout must operate on a raw-sum shadow copy" — a principled
either/or, faithfully built, is the answer).

## 8. FILES AND ENTRY POINTS
- `hdlab/situation_model_accumulate.py`, `hdlab/bundling.py`, `hdlab/vsa_cleanup_memory.py`;
  `experiments/exp_register_completion_readout_v1.py`, `verification/test_register_completion_readout.py`. Audit + heavy→REMOTE.

## DO NOT QUOTE / DO NOT REDO
The 0.119-vs-0.983 renorm-break is the STARTING measurement, not your result. Do NOT change the store structure (p2).
Strategy owns any hdlab landing — you propose the normalization, you do not write `hdlab/`.
