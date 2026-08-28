---
priority: 7
review:
review_text:
---

# PROBLEM: multiple reader organs re-implement ARGUMENT-STRUCTURE extraction (who is the agent, what is the moved theme, which PP is the goal) INLINE and ad-hoc, and the shared residual — caused-motion "eased/struck THEM to the ground" (the theme moves, the agent stays), participial "went ON" (continue not motion) — bit the SPACE organ's goal extraction and the who-did-what front-end alike. There is no SHARED shallow predicate-argument (semantic-role) front-end that robustly maps parsed spans to agent/theme/goal/instrument roles. FIRST verify whether the landed role organs already provide this on raw prose (if so, this is a WIRING problem); if they do not (the SPACE solver's inline argument-structure gate suggests they do not), build the shared shallow SRL over the dependency parse, validate it beats the current inline/ad-hoc extraction CI-separated on a real-prose role gold with the info-free twin losing, and show it lifts a downstream front-end (SPACE goal precision or who-did-what)

**slug:** `no_shared_shallow_predicate_argument_front_end` — **opened:** 2026-08-28 by the strategy session (the SHARED
argument-structure wall flagged by BOTH the integrated `situation_model_has_no_spatial_location_dimension` (its adjacency:
"a shallow SRL that marks the agent as the moving theme would close most of the residual") AND the who-did-what /
coref lines). **status:** OPEN — a MECHANISM + INSTRUMENT problem, possibly a WIRING problem (verify first). You build +
validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `7` — a SHARED front-end (like the SPACE organ was):
> argument-structure extraction is re-derived inline by the motion/location organ, the who-did-what reader, and the coref
> caused-motion residual. A robust shared extractor lifts several organs at once. **BUT it MUST first establish it is not
> a duplicate of the landed role organs** (`graded_role_assigner`, `thematic_role_labeler`, `arc_parser`) — if those
> already provide robust agent/theme/goal extraction on raw prose, this collapses to a WIRING task. **Re-rank per the owner.**

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
To read "who did what to whom / where", you must map the words to ROLES: in "the blow eased **them** to the ground", the
agent is "the blow", "them" is the thing that MOVES, and "to the ground" is where THEY end up — not where the agent goes.
Several organs need exactly this argument structure — the SPACE location register (which PP is the mover's goal?), the
who-did-what reader (agent vs patient), the coref caused-motion residual (is the "to X" head a destination or a
recipient?) — and each currently re-derives it INLINE with its own ad-hoc rules. The SPACE solver had to build a bespoke
argument-structure gate; the who-did-what front-end has its own. There is no SHARED, robust shallow predicate-argument
(semantic-role) extractor. The task: FIRST establish whether the landed role organs already provide robust agent / theme
/ goal extraction on raw prose (if yes → this is a WIRING problem: wire them in, delete the inline copies); if NO (the
inline gates strongly suggest a gap), build the shared shallow SRL over the parse and prove it beats the current inline
extraction on a real-prose role gold, lifting a downstream front-end. A rigorous NEGATIVE (the landed organs already
suffice → wire, don't build) is a full pass.

## 2. WHY THIS ONE
It is a SHARED front-end wall named by three integrations — the highest-leverage KIND (build once, lift many). A robust
agent/theme/goal extractor removes duplicated inline logic from the SPACE organ, the who-did-what reader, and feeds the
coref caused-motion residual, and it is the natural companion to the verb-sense (p4) and coherence-prior (p5) work.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** thematic-role assignment is CUE-BASED, GRADED integration over the realized syntax +
  the arguments' semantic types (Competition Model, MacWhinney & Bates; the reader's own graded cue-combination;
  posterior-temporal / pMTG for reversible role binding — Beber 2025; Matchin & Hickok 2020). VerbNet/PropBank frames
  give the mapping from a verb's syntactic arguments to thematic roles (agent/theme/goal/instrument); the moved THEME of
  a caused-motion verb is its direct object, and a goal PP is the THEME's destination, not the agent's (Levin 1993;
  Rappaport Hovav & Levin 2008).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the feature set + frame inventory + the granularity (start with the
  roles the downstream organs actually consume — agent, moved-theme, goal, recipient — not full PropBank). Copy the
  COMPUTATION (graded cue-based role assignment over the parsed argument structure); SWEEP the features/frames.
- **NOT brain-faithful:** a fixed verb→role lookup ignoring realized syntax; a raw dependency-label read (the audit:
  `arc_parser` head/deprel are PLACEHOLDERS at inference; `thematic_role_labeler` is RIGHT-OP-WRONG-METRIC) — which is
  exactly why the inline gates exist. An external SRL model / LLM at inference is barred (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the SPACE organ's inline argument-structure gate (goal precision
  0.219→0.909 on 186 real LitBank tokens; residual = ambiguous caused-motion); the who-did-what front-end's inline role
  logic; the landed `graded_role_assigner` / `thematic_role_labeler` / `arc_parser` and the audit's verdicts on them
  (placeholders / wrong-metric). **The DUPLICATION is the measured evidence** — three organs, three inline extractors.
- **INFERRED (to prove):** whether a SHARED shallow predicate-argument extractor beats the inline/ad-hoc extraction on a
  real-prose role gold and lifts a downstream front-end — OR whether the landed role organs already suffice (a wiring
  result).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-solve the SPECIFIC role problems already integrated (non-canonical argument structure; who-did-what
  mislabeling; relcl filler-gap; graded role assignment) — this is the SHARED extractor those assume. Do NOT rebuild the
  SPACE motion gate (reuse it as one downstream consumer). Do NOT use an external SRL/LLM at inference. FIRST check the
  landed role organs (a wiring result closes this without a new build).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/graded_role_assigner.py`, `hdlab/thematic_role_labeler.py`, `hdlab/arc_parser.py`/`arc_labeler.py` (what
  they actually output on raw prose); the SPACE organ's inline gate (`situation_model_has_no_spatial_location_dimension`
  SOLVED + `experiments/location_register.py`); the who-did-what front-end's role logic. `tools/experiment_index.py query
  "role"` / `"argument"` / `"SRL"` / `"thematic"`. Audit: the thematic-role + arc-parser entries (the placeholder /
  wrong-metric verdicts). **Mind the CORPUS-AGE confound** (archaic prose parse noise — see the sibling brief
  `role_assignment_is_untested_on_archaic_literary_prose`).
- Gold: a real-prose agent/theme/goal role gold (a mined LitBank set or a PropBank-style annotation — state how built +
  verified).

## 7. THE BAR
PASSES only with ONE of (both are full passes):
- **BUILD path:** a shared shallow predicate-argument extractor (agent/theme/goal/recipient over the parse), beating the
  current inline/ad-hoc extraction **CI-separated** on a real-prose role gold (recompute the inline floor on the same
  population); **info-free twin** (shuffled role features / random role assignment) LOSES CI-sep; report CI half-width +
  null p95; a **POSITIVE control** a role-decisive minimal pair the extractor gets and the inline rule cannot; AND it
  **lifts a downstream front-end** (SPACE goal precision OR who-did-what) CI-sep vs the inline path — wire-don't-island.
- **WIRING path (a rigorous negative = a full pass):** demonstrate the landed role organs ALREADY provide robust
  agent/theme/goal extraction on raw prose (CI-equal to the inline gates on the same gold) → the deliverable is to WIRE
  them into the SPACE / who-did-what organs and DELETE the inline copies (measured no-regression), not a new build.
- **One-screen summary:** extraction path → floor → twin → downstream lift (or the wiring no-regression) → verdict.
  Heavy → REMOTE.

## 8. FILES AND ENTRY POINTS
- `hdlab/graded_role_assigner.py`, `hdlab/thematic_role_labeler.py`, `hdlab/arc_parser.py`; the SPACE inline gate
  (`experiments/location_register.py`); the who-did-what front-end. Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (thematic
  role + arc parser). Heavy → REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The SPACE gate's 0.219→0.909 + the duplication are the MOTIVATING evidence, not your result. Do NOT re-solve the specific
integrated role problems. Strategy owns any hdlab landing — you propose the shared extractor (or the wiring), you do not
write `hdlab/`.
