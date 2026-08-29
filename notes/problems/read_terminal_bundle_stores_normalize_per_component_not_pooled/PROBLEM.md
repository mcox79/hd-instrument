---
priority:
review: EXCELLENT
review_text: "RIGOROUS NEGATIVE / PARTIAL (owner-DONE) integrated 2026-08-29 = a full pass per the bar. Reverified FIRST-HAND: test_read_terminal_divnorm.py ALL CHECKS PASS (W1–W11, scaffold-free on real organs/tasks). The brief's blanket 'switch EVERY read-terminal caller to divnorm' is REFUTED by per-caller live measurement: divnorm ≥ per-component ONLY for a DIRECTION-SENSITIVE read under OVERLOAD, largest for the gain-matched serial decode — and the only two callers with both (register + multibank) were ALREADY switched by the parent divnorm landing. No other enumerated caller should switch, each MEASURED: typer sup_map HURTS at low load (−0.0375 CI-sep, divnorm double-counts the explicit shard weights); typer sub-bundle inert (round-trip key); goal_achievement can't overload (≤6 attrs); cosine consumers NULL (ordered_frac identical, d' headroom unused). The discriminator is READOUT-CLASS + LOAD, not read-terminal-vs-rebound. EXEMPLARY self-correction (owner-pushed): an apparent gain-matched typer win (+0.0139 CI-sep @n=40) was REJECTED after a 4-arm brain-fidelity test + literature — it is non-brain-faithful per-role L2 equalization, load-fragile (−0.0556 @n=8); the brain-faithful shared-pool norm is ARGMAX-INVARIANT (inert). The PPC magnitude-as-reliability alternative to the LOO weight is refuted (−0.2167 CI-sep). BIGGEST FINDING (new, measured): capacity is set at the register WRITE path, not READ — the flat running-sum has a hard capacity wall (recent-event recovery 0.125 @256) that read-time divnorm CANNOT move (raw==divnorm every load); the brain-faithful fix is an ASYMMETRIC CONTINUOUS leaky/recency write (recovers recent @256 → 1.0, reproduces the primate-PFC 66/45/39 recency gradient — Warden-Miller 2007/Konecky 2017), a fundamental single-store trade needing a content/salience-gated hand-off into the existing HDFactStore (NOT a new CLS mechanism). AUDIT CORRECTION folded (§2b): the earlier 'a read-terminal bundle must be pooled-divisive-normed' rule was too broad + mis-attributed → replaced with the readout+load rule + three gating conditions; the register divnorm is DEMOTED from implied PINNED to OUR-EXTENSION-UNDER-TEST (an exhaustively-searched absence, ~28 sources — no paper fits pooled Carandini-Heeger to real hippocampal/PFC multi-item WM data; we are in the right computational CLASS, not circuit-measured). hdlab landing: NONE earned (register+multibank already divnorm; switching anything else is measured neutral-to-harmful) — the result IS 'no change'. The write-path fix is a NEW build problem (packaged separately)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-29 (grade: EXCELLENT; rigorous negative / PARTIAL owner-DONE)
> **Verdict:** a rigorous negative = a full pass, and an exemplary one. Reverified first-hand
> (`test_read_terminal_divnorm.py` **ALL CHECKS PASS**, W1–W11, scaffold-free on the real organs/tasks). The brief's
> blanket "switch every read-terminal caller to divnorm" is **refuted** by per-caller live measurement: divnorm beats
> per-component **only** for a direction-sensitive read under overload (largest for the gain-matched serial decode), and
> the only two callers with both (register + multibank) were **already switched** by the parent. Every other caller
> measured neutral-to-harmful (typer HURTS −0.0375 CI-sep at low load; cosine/goal_achievement NULL). The real
> discriminator is **readout-class + load**, not read-terminal-vs-rebound.
> **Exemplary self-correction (owner-pushed):** an apparent gain-matched typer win (+0.0139 CI-sep) was **rejected** after
> a 4-arm brain-fidelity test — it's non-brain-faithful per-role L2 equalization, load-fragile; the brain-faithful
> shared-pool norm is argmax-invariant (inert). The PPC magnitude-as-reliability alternative is also refuted (−0.217).
> **Biggest finding (new, measured):** capacity is set at the register **WRITE** path, not read — the flat running-sum has
> a hard capacity wall (recent-recovery 0.125 @256) that read-time divnorm **cannot** move; the brain-faithful fix is an
> **asymmetric continuous leaky/recency write** (recovers recent @256→1.0; reproduces the primate-PFC 66/45/39 recency
> gradient — Warden-Miller 2007/Konecky 2017), a fundamental single-store trade needing a content/salience-gated hand-off
> into the existing `HDFactStore` (not a new CLS mechanism).
> **Audit correction (folded §2b):** the earlier "a read-terminal bundle must be pooled-divisive-normed" rule was too
> broad + mis-attributed → replaced with the readout+load rule + three gating conditions; **the register divnorm is
> demoted from implied PINNED to OUR-EXTENSION-UNDER-TEST** (an exhaustively-searched absence, ~28 sources — no paper fits
> pooled Carandini-Heeger to real hippocampal/PFC multi-item WM data; right computational CLASS, not circuit-measured). A
> genuine rigor upgrade.
> **hdlab landing: NONE earned** — register+multibank already divnorm; switching anything else is measured
> neutral-to-harmful. The result IS "no change." **The write-path fix is a NEW build problem** (packaged separately as the
> next brief).

# PROBLEM: the register bundle-renorm result generalizes to a SUBSTRATE-WIDE fidelity rule the p5 solver measured and mapped — a bundle that is READ (unbind+cleanup, or cosine-compared), NOT re-bound as an operand, must be normalized by a POOLED/scalar divisive gain (Carandini-Heeger), never by the per-component `S_i/|S_i|` default; EVERY enumerated `bundling.bundle` caller is READ-terminal (none re-bind), so the default is sub-optimal for the whole consumer set, and the `sign()`-on-a-bundle sites are the SAME wrong-op in a bipolar code. Now that `bundling.bundle` has the LANDED `norm="divnorm"` option, switch the enumerated read-terminal callers to pooled divisive norm and MEASURE each on its OWN task — CI-separated over the per-component floor with the info-free twin losing, or a rigorous per-caller NULL closing it

**slug:** `read_terminal_bundle_stores_normalize_per_component_not_pooled` — **opened:** 2026-08-28 by the strategy session
(the general substrate rule mapped by the integrated `the_register_bundle_renorm_breaks_the_serial_readout`,
owner-DONE/EXCELLENT: its `ADJACENT_COMPONENTS_brain_fidelity_map.md`). **status:** OPEN — a FIDELITY + MEASUREMENT
problem. You build + measure in `experiments/`; strategy lands any hdlab change (Q111). **UNBLOCKED 2026-08-28:**
`hdlab/bundling.py` now has `norm="divnorm"` (pooled Carandini-Heeger) + `AccumulateRegister(bundle_norm=...)` landed, so
the building block exists — this problem MEASURES which read-terminal callers it should be turned on for.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` — BROAD, high-confidence substrate hygiene: the
> register result already PROVED the mechanism (per-component 0.367 → pooled 0.988 serial; argmax 0.529 → 0.644) and the
> building block is LANDED; this problem carries the proven fix across the mapped consumer set and turns a one-organ win
> into a substrate-wide one. Lower ceiling per-caller than a new capability, but wide and de-risked. **Re-rank per the owner.**

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
Many organs stack several facts into one vector (a "bundle") and then rescale it. The default rescale in
`hdlab/bundling.py` divides EACH channel by its own magnitude (`S_i/|S_i|`) — a per-component distortion that quietly
destroys the linear structure a downstream read needs. The register problem PROVED this: swapping it for a POOLED
rescale (one shared scalar over the whole vector — the brain's divisive normalization) took an overloaded register's
serial readout from 0.367 to 0.988 and improved the simple readout too. The p5 solver then enumerated EVERY caller of
`bundling.bundle` and found they are ALL "read-terminal" — the bundle is unbound+cleaned-up or cosine-compared, never
re-bound as an operand (the one case where per-component rescale is correct). So the per-component default is the wrong
choice for the whole set. The building block is now LANDED (`norm="divnorm"`). The task: turn it on for each enumerated
read-terminal caller and MEASURE the effect on that caller's own task — a CI-separated win with the info-free twin
losing, OR a rigorous null (that caller's readout is insensitive) that closes it. This is measure-each, not assume-all.

## 2. WHY THIS ONE
Broad, de-risked substrate hygiene: the mechanism is proven and landed; this carries it across the mapped consumer set,
converting a one-organ fidelity win into a substrate-wide one, and cleanly separates the callers that genuinely benefit
from those whose readout is scale-insensitive. It also unifies with the `sign()`-on-a-bundle family (the same wrong-op
in a bipolar code), so one principle — "pooled divisive normalization at read-terminal bundles" — is validated once and
applied everywhere it holds.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** a population that is READ controls its summed magnitude by **pooled DIVISIVE
  NORMALIZATION** — divide by ONE scalar over the pool (Carandini & Heeger 2012), a global rescale that preserves the
  linear/relative structure — never a per-channel nonlinearity. Established for THIS substrate by the register result
  (per-component `S_i/|S_i|` breaks the read; pooled divisive recovers it; parameter-flat = the operation, not a number).
  The `sign()` quantiser on a bundle is the bipolar-code analogue of the same per-component error (audit: "graded beats
  sign CI-sep, growing margin").
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** which read-terminal callers actually benefit (MEASURE each — some
  cosine reads may be scale-insensitive), and the pooled-scalar variant (l2 / rms / divnorm / homeostatic — all pooled
  members; the register result was parameter-flat across them). Copy the COMPUTATION (pooled divisive norm at a
  read-terminal bundle); SWEEP the caller set + the variant.
- **NOT brain-faithful:** the per-component `S_i/|S_i|` default at a read-terminal bundle; `sign()` on a bundle read. The
  per-component renorm's ONLY correct scope is torus-closure for an atom that will be RE-BOUND (measure, don't assume a
  caller re-binds — the map found none that do).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the register result (per-component 0.367 → pooled 0.988 serial;
  argmax 0.529 → 0.644; parameter-flat); the LANDED `bundling.bundle(norm="divnorm")` + `AccumulateRegister(bundle_norm=)`
  + `decode_serial_pooled` (witness `test_register_divisive_norm_organ.py` 7/7); the enumerated read-terminal caller set
  + classification in `the_register_bundle_renorm_breaks_the_serial_readout/ADJACENT_COMPONENTS_brain_fidelity_map.md`
  (`situation_model_multibank`, `selection_weighted_sharded_typer`, `script_grain_acquisition_loop`, `goal_achievement`
  via unbind+cleanup; `lexical_similarity` / `verb_lexical_similarity` / `quality_relation` via cosine); the `sign()`>graded
  audit measurements (~lines 1001/1176).
- **INFERRED (to prove):** per caller, whether pooled divisive norm beats per-component on that caller's OWN task (or is
  neutral). The cosine consumers are a DISTINCT question — cosine of a PER-COMPONENT-renormed bundle differs in DIRECTION
  from a pooled-normed one (per-component changes the vector's direction, not just scale), so measure them, do not assume
  cosine is invariant.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-derive the REGISTER result (it is the proven starting point). Do NOT change the `bundling.bundle` DEFAULT
  (per-component must stay the default for re-bound atoms + byte-identical existing behavior — the landed option is
  OPT-IN). Do NOT rebuild `decode_serial`/`decode_serial_pooled` (landed). Measure each caller; a null on a caller is a
  result, not a failure.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/bundling.py` (the landed `norm` branches incl. `divnorm`) and the ADJACENT_COMPONENTS map (the enumerated
  callers + their consumption class). Read each caller's read path (`selection_weighted_sharded_typer`,
  `script_grain_acquisition_loop`, `goal_achievement`, `lexical_similarity`, `quality_relation`) and its existing
  validation harness / witness. `tools/experiment_index.py query "bundle"` / `"cosine"` / `"cleanup"`. Audit:
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` — the newest §2b register-norm entry (the general rule) + the `sign()` sites.

## 7. THE BAR
PASSES only with ALL of (per read-terminal caller you evaluate — cover at least the argmax/cleanup family AND one cosine
consumer):
1. **Switch the caller's read-terminal bundle to a pooled divisive norm** (`norm="divnorm"` or the best pooled variant),
   measured on that caller's OWN validated task/gold.
2. **Pooled ≥ per-component CI-separated on that task** (recompute the per-component floor on the same population), with
   the **info-free twin** (shuffled / random pooled scale, or a scrambled read) LOSING CI-separated; report CI
   half-width + null p95 — OR a **rigorous NULL** (the caller's readout is provably scale/direction-insensitive, e.g. a
   cosine that is unchanged) that CLOSES that caller. No number crosses callers/populations.
3. **A POSITIVE control** the metric can move (a load/regime where per-component demonstrably breaks the read, as the
   register showed at overload), so a null is interpretable.
4. **One-screen summary:** per-caller table (caller → norm → win/neutral/null → evidence) + the recommended default per
   caller. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the cosine consumers are scale-insensitive → no change; only the
cleanup/argmax family benefits" — a principled per-caller verdict IS the deliverable; the point is to MEASURE, not to
flip everything).

## 8. FILES AND ENTRY POINTS
- `hdlab/bundling.py` (landed `norm="divnorm"`); the enumerated callers above; the ADJACENT_COMPONENTS map; the `sign()`
  sites (`grounding_acquisition_loop`, `situation_focus`, `role_slot_summarizer`, `event_bundle`). Audit + heavy→REMOTE.

## DO NOT QUOTE / DO NOT REDO
The register 0.367→0.988 numbers are the MOTIVATING evidence, not your result — measure each caller on its own task. Do
NOT change the `bundling.bundle` default or re-derive the register/decode_serial work. Strategy owns any hdlab landing —
you propose which callers to switch (with per-caller measurement), you do not write `hdlab/`.
