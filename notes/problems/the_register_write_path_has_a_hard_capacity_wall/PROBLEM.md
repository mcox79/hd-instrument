---
priority: 6
review:
review_text:
---

# PROBLEM: the reader's working-memory REGISTER writes every event by ADDING it into ONE flat running sum (`AccumulateRegister.add_event`: `S = S + bind(role, item)`), which has a HARD capacity wall (~0.2–0.25·D events; at D=256, ~50–64) — past it recovery collapses for ALL events, including the most RECENT (recent-4 recovery falls to 0.14 at N=256, chance 0.01), and read-time normalization CANNOT move the wall (raw==divnorm at EVERY load; once summed to saturation the information is DESTROYED, not mis-scaled — this is exactly why the whole read-terminal divnorm sweep came back null: capacity is set at WRITE). The brain does NOT flat-sum: sequential working-memory encoding uses an ASYMMETRIC/leaky recency gain (new events suppress old), keeping recent context recoverable at ANY load, and hands off what decays to a second permanent store. Build the brain's write path — a CONTINUOUS leaky/recency write (`S = λ·S + bind(role, item)`, sweep λ) plus a content/salience-gated commit into the existing `HDFactStore` for what the leak displaces — and show it lifts a capacity-bound downstream task CI-separated over the flat-write floor with the info-free twin losing.

**slug:** `the_register_write_path_has_a_hard_capacity_wall` — **opened:** 2026-08-29 by the strategy session (the MEASURED
#1 gap surfaced by the integrated `read_terminal_bundle_stores_normalize_per_component_not_pooled`, owner-DONE/EXCELLENT —
its W9/W10/W11 drills proved the read side is the wrong stage and located the write-path capacity wall + the fix form).
**status:** OPEN — a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change
(Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` — HIGH leverage: the register is a CORE store the
> whole stack reads (who-did-what, the situation model, the ToM observation cue, "where is X"), and this is "the biggest,
> cleanest limitation this whole investigation found" — a MEASURED capacity wall on a core store, with STRONGER brain
> support than the read-side divnorm ever had (the write-time asymmetric/leaky gain is MEASURED/PINNED-WEAK from primate
> PFC; the read-side divnorm is OUR-EXTENSION with no direct citation). Ranked at `6` (below the in-flight reasoning/binding
> briefs p3/p4/p5) because it is a core-store ARCHITECTURE change (write gain + a consolidation hand-off), not a quick win.
> **Dependency web:** composes with `multibank` sharding and the p2 sparse store; spawns a MEDIUM follow-on (the
> content/salience-gated register→`HDFactStore` hand-off). **Re-rank per the owner.**

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
The reader's working memory (the "register") remembers events by ADDING each one into a single running total. That total
saturates: past ~50–64 events everything in it becomes unrecoverable — even the events that JUST happened (recovery of the
last few events falls to about 1-in-7 at 256 events, near chance). We just proved that no clever READ-time math can rescue
this: once the events are summed to saturation the information is genuinely gone, not merely mis-scaled — which is exactly
why the whole read-side normalization sweep came back empty. The brain does not do this. Sequential working memory writes
with an ASYMMETRIC recency gain — each new event partially suppresses the old ones — so the most recent context stays
recoverable no matter how much has come before, and it hands off what fades to a separate permanent store. The task: build
that write path — a continuous leaky/recency write, and a content-gated hand-off into the substrate's existing permanent
fact store for what the leak lets go — and show it recovers recent events (and high-load who-did-what) where the flat sum
collapses.

## 2. WHY THIS ONE
It is the biggest, cleanest limitation the entire read-terminal investigation found, and it is MEASURED (W9/W10/W11). The
register is a CORE store the whole stack reads — who-did-what, the situation model, the ToM observation cue, "where is X" —
so its capacity wall caps everything downstream. And the fix has STRONGER brain support than the read-side normalization
ever had: the write-time asymmetric/leaky recency gain is MEASURED in primate PFC (a monotonic recency gradient), whereas
the landed read-side divnorm is an OUR-EXTENSION with no direct citation. This is the rare case where the more
brain-faithful mechanism is ALSO the bigger capability lever.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** sequential working-memory encoding uses an ASYMMETRIC/LEAKY recency gain — each new item is
  privileged over the older store (new partially suppresses old). Two convergent primate-PFC single-unit studies with
  SEQUENTIAL presentation measure a monotonic recency gradient (Warden & Miller 2007, Cereb Cortex; Konecky, Smith & Olson
  2017, J Neurophysiol — population decoding ~66% newest / 45% middle / 39% oldest). It is a CONTINUOUS/graded resource, NOT
  discrete slots (Watters 2026 gain-model beats slot in 88% of sessions; the CDA "neural slot" evidence collapsed under a
  10-lab replication). The brain PAIRS this bounded active buffer with CONSOLIDATION to a second store for what displaces.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact leak `λ` in `S = λ·S + bind(role, item)`, and the
  content/salience-gate threshold for the second-store hand-off. **Copy the COMPUTATION** (asymmetric leaky recency write +
  a content-gated consolidation of what decays); **SWEEP `λ` + the gate threshold.** Reuse the OFF-by-default `recency`
  modulator already in `hdlab/bundling.py` (this IS the leaky write, currently unwired), `situation_model_accumulate`, the
  existing content-addressed `HDFactStore`, and the MDL/schema-congruence gate from `script_grain`/`grounding_acquisition_loop`.
- **NOT brain-faithful:** the current FLAT running sum (OUR-INVENTION — the hard capacity wall); a SYMMETRIC divisive
  rescale at write (`S/(mean|S|)` each step — MEASURED DEAD in W10: preserves relative weights, so the crosstalk collapse
  still happens; it only bounds magnitude — the brain's encoding suppression must be ASYMMETRIC); a recency-CHUNKED CLS
  consolidation / a recency-chunked `ChunkedFocus` (research-REFUTED: CLS is organized by CONTENT/schema-congruence +
  salience, NOT recency/eviction-order, and solves a different hours-scale interference problem); a hard bounded QUEUE (a
  STEP function — discrete slots — MEASURED less faithful than the continuous leak in W11); external LLM at inference (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** from the integrated `read_terminal_bundle_stores_normalize_per_component_not_pooled`
  (`exp_read_terminal_divnorm_write_path_v1.py`, witness `test_read_terminal_divnorm.py`): **W9** — the flat-write capacity
  wall (recent-4 recovery 0.125 @N=256, flat) and read-time normalization CANNOT move it (raw==divnorm at every load); a
  write-time leaky gain keeps recent recoverable at ANY load (leaky recent-4 = 1.0 @N=256); info-free twin (shuffled keys)
  collapses. **W10** — a SYMMETRIC divisive rescale at write does NOT extend capacity (uniform ~= flat); the form must be
  ASYMMETRIC. The single-store trade is FUNDAMENTAL (leaky buys recent by decaying old → needs a 2nd store). **W11** — the
  CONTINUOUS leak reproduces a GRADED monotonic recency gradient (recovery 1.0→0.72→0.40, intermediate positions = the
  primate 66/45/39 shape), whereas a bounded QUEUE is a STEP (zero intermediate). Brain-fidelity: asymmetric leaky =
  MEASURED/PINNED-WEAK (Warden-Miller/Konecky, primary-verified).
- **INFERRED (to prove):** that the leaky/recency write lifts a capacity-bound downstream task (recent-event recovery AND/OR
  who-did-what at high store load) CI-separated over the flat-write floor with the info-free twin losing; the BEST
  asymmetric form (fixed vs activity-adaptive leak vs bounded queue); the consolidation path (a content/salience-gated
  commit into `HDFactStore`, reusing the MDL/schema gate — preserving old-event recovery the leak alone loses, WITHOUT a
  new mechanism); and how it composes with `multibank` sharding + the p2 sparse store.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-run the read-terminal `divnorm` sweep (DONE, refuted — read-norm cannot move the write wall; the read-side
  divnorm stays as-is). Do NOT build a SYMMETRIC divisive-at-write (W10: measured dead — does not extend capacity). Do NOT
  build recency-chunked CLS consolidation or a recency-chunked `ChunkedFocus` (research-refuted — wrong organizing
  principle). Do NOT rebuild `HDFactStore` (exists — reuse) or the MDL/schema-congruence gate (exists — reuse). Do NOT use
  a hard bounded QUEUE as the primary form (W11: less brain-faithful than the continuous leak). REUSE the OFF-by-default
  `recency` modulator in `hdlab/bundling.py` (it IS the leaky write, unwired).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `read_terminal_bundle_stores_normalize_per_component_not_pooled/SOLVED.md` (the W9/W10/W11 write-path drills + the
  per-caller verdicts) and `notes/research_register_write_path_asymmetric_recency_suppression_2026-08-29.md` (the 13-source
  brain-fidelity drill: Warden-Miller/Konecky, and the CLS-is-the-wrong-analogy correction). Read
  `hdlab/situation_model_accumulate.py` (`AccumulateRegister.add_event` — the flat write), `hdlab/bundling.py` (the
  OFF-by-default `recency` modulator = the leaky write), `hdlab/situation_model_multibank.py` (sharding), the `HDFactStore`
  (from the integrated `one_store_does_two_jobs...`) + the MDL/schema gate (`script_grain`/`grounding_acquisition_loop`).
  Run `tools/experiment_index.py query "register"` / `"recency"` / `"capacity"` / `"consolidation"` (SINGLE keywords).
  Audit: the newest §2b read-terminal-norm entry (2026-08-29). **Mind the CORPUS-AGE confound** where a downstream task
  uses archaic prose.

## 7. THE BAR
PASSES only with ALL of:
1. **A CONTINUOUS leaky/recency WRITE** on `AccumulateRegister.add_event` (`S = λ·S + bind(role, item)`, λ swept) — the
   ASYMMETRIC brain-faithful form (NOT symmetric divisive — W10 measured dead; NOT a hard queue — W11 less faithful). Copy
   the computation; sweep λ. NO external LLM.
2. **Lifts a capacity-bound downstream task CI-separated over the flat-write floor** — recent-event recovery at high store
   load, AND/OR who-did-what at high load — the floor = the current flat sum (λ=1) recomputed on the same population. The
   **info-free twin** (shuffled keys, or the flat λ=1 write) LOSES CI-separated; report CI half-width + null p95; no number
   crosses populations. A **POSITIVE control** the metric can move (a high-load recent-event query the leaky write recovers
   and the flat sum cannot).
3. **The recency FORM is the brain's** (W11): the recovery-by-recency curve is GRADED/monotonic (intermediate positions),
   not a step (queue), reproducing the primate-PFC gradient shape — report the curve, not just a headline number.
4. **If OLD events also matter:** a content/salience-gated commit into the existing `HDFactStore` (reuse the MDL/schema
   gate; commit by SALIENCE, not eviction-order) — MEASURED to preserve old-event recovery the leaky write alone loses,
   WITHOUT a new consolidation mechanism (the leaky-vs-old trade is fundamental; this is the second-store half).
5. **One-screen summary:** λ swept → floor → twin → capacity/recency lift → form-fidelity (graded vs step) → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful continuous-leak write recovers recent context to X at any load and the
graded gradient matches the primate shape; the old-event remainder needs the content-gated HDFactStore hand-off, which
recovers Y — closing the register capacity wall as a write-stage + consolidation architecture, not a read-norm").

## 8. FILES AND ENTRY POINTS
- **Motivation + measured limitation (REUSE, do not redo):** `read_terminal_bundle_stores_normalize_per_component_not_pooled/{SOLVED.md,
  FOLLOWON_PROBLEMS_FOR_STRATEGY.md §1}`; `experiments/exp_read_terminal_divnorm_write_path_v1.py` (W9/W10/W11);
  `notes/research_register_write_path_asymmetric_recency_suppression_2026-08-29.md`.
- **Build over:** `hdlab/situation_model_accumulate.py` (`AccumulateRegister.add_event`), `hdlab/bundling.py` (the OFF-by-
  default `recency` modulator), `hdlab/situation_model_multibank.py` (sharding); the `HDFactStore` + the MDL/schema-congruence
  gate. Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
W9/W10/W11 and the primate recency gradient are the MOTIVATION (from the read-terminal integration), not your result —
build the leaky write and recompute the flat-write floor on YOUR population. Do NOT re-run the read-terminal divnorm sweep,
a symmetric divisive-at-write (measured dead), or recency-chunked CLS consolidation (research-refuted). Strategy owns any
hdlab landing — you propose the write gain + the consolidation hand-off, you do not write `hdlab/`.
