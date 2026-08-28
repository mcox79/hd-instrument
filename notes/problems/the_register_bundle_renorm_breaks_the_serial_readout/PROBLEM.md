---
priority: 5
review:
review_text:
---

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
