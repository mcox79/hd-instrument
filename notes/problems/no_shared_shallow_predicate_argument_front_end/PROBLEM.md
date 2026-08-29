---
priority:
review: STRONG
review_text: "PARTIAL (owner-DONE) integrated 2026-08-29. Reverified FIRST-HAND: exp_shared_predarg_frontend_v2.py --self-test 14/14 PASS. Scope finding confirmed (no shared front-end; role organs islanded/WIRE_CANDIDATE). The core WIN is decisive on an INDEPENDENT gold (FrameNet 1.7 FE, 58,808 items): the event-semantic PP-router (preposition-telicity + VerbNet event-class + animacy + constructional caused-motion — Jackendoff/Talmy/Zwarts, NOT a verb list) recovers location/path/source/recipient/direction — five roles the conflating inline rule scores exactly 0.000 on — every one CI-separated with the info-free twin below each; theme +0.059 and agent +0.017 CI-sep; goal-vs-recipient mislabel 9.1% vs 27.7%; caused-motion 8/8; positive control 0.886 vs 0.648. Brain-foundational upgrade (v1 verb-list → v2 event-semantics) is exemplary, and TWO measurement leaks were self-caught (checkpoint-reuse zeroing via baseline-invariance; a candidate-opening twin artifact via the info-free twin → strict re-test shows the parse-attachment gain is modest-but-real: eager slot-opening CI-sep on all 5 roles, selectional 4/5). HONEST bounds owned: goal RECALL 0.378 < the blunt inline grabber's 0.477 (a precision/recall trade — the grabber calls every spatial PP goal); recipient absolute low (0.152); the goal-vs-location boundary is graded (hard Destination cue trades goal +0.061 for location −0.073, correctly NOT adopted); richer-rep drill NEGATIVE (residual is ATTACHMENT, not representation). Grade STRONG not EXCELLENT: the bar's SECOND half (a downstream front-end lift via wiring — wire-don't-island) is DEFERRED to the strategy landing (the owner accepted PARTIAL and assigned it to strategy). QUEUED the full hdlab landing as ONE careful dedicated follow-on (I verified the core is portable but it is a ~300-line multi-dependency port — the event-semantic router + the v1 parse helpers + the live-nltk VerbNet event-class lookup + the WordNet place-typing subsystem, composing the landed binder/passive/animacy organs — and the live-reader no-regression de-dup is run-the-reader work; rushing it mid-heartbeat risks a subtly-wrong organ): create hdlab/predicate_argument_frontend.py, route situation_reader through it DEFAULT-OFF, and de-duplicate the three inline copies (location_register._goal_node, parse_goal_extraction, the inline who-did-what rule) with measured no-regression. Recorded in the STATUS wire-don't-island debt list. Audit §2b folded."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-29 (grade: STRONG; PARTIAL owner-DONE)
> **Verdict:** a STRONG PARTIAL. Reverified first-hand (`exp_shared_predarg_frontend_v2.py --self-test` **14/14 PASS**).
> The core is a genuine, brain-foundational win: on FrameNet's **independent** expert gold (58,808 real-prose items) the
> event-semantic PP-router recovers **five spatial/transfer roles the conflating inline rule scores exactly 0.000 on**
> (location/path/source/recipient/direction), every one CI-separated with the info-free twin below each; theme/agent also
> above; goal-vs-recipient mislabel cut 27.7%→9.1%; caused-motion 8/8; positive control 0.886 vs 0.648. The **v1→v2
> upgrade** (curated motion-verb list → preposition-telicity + VerbNet event-class + animacy + constructional caused-motion;
> Jackendoff/Talmy/Zwarts) is the right, brain-faithful move.
> **Rigor:** exemplary — **two measurement leaks self-caught** (a checkpoint-reuse rescore that zeroed every arm, caught by
> baseline-invariance; a candidate-opening twin artifact, caught by the info-free twin → the strict re-test shows the
> verb-led attachment gain is *modest-but-real*, not the majority-recovery the leak implied).
> **Honest bounds (owned):** goal *recall* 0.378 < the blunt inline grabber's 0.477 (a precision/recall trade, not a
> mechanism failure); recipient absolute low (0.152); the goal-vs-location boundary is graded (hard Destination cue trades
> goal +0.061 for location −0.073 — correctly **not adopted**); a richer-representation drill was NEGATIVE (the residual is
> ATTACHMENT quality, not representation — the incremental-parser swap is the real lever, a separate follow-on).
> **Why STRONG not EXCELLENT:** the bar had two halves — (a) the extractor beats inline [DONE, decisively] AND (b) a
> *downstream* front-end lift via wiring [DEFERRED]. The owner accepted the PARTIAL and assigned the wiring to strategy.
> **Queued (Q111 — ONE careful dedicated landing, recorded in the STATUS wire-don't-island debt):** create
> `hdlab/predicate_argument_frontend.py` (the event-semantic router + the v1 parse helpers + the live-nltk VerbNet
> event-class lookup + the WordNet place-typing subsystem, composing the landed binder / passive-detector / animacy
> organs) + a witness; then route `situation_reader` through it DEFAULT-OFF and de-duplicate the three inline copies
> (`location_register._goal_node`, `parse_goal_extraction`, the inline who-did-what rule) with MEASURED no-regression —
> the coupled, run-the-live-reader half of wire-don't-island. I verified the core is portable (~300-line multi-dependency
> port), but a faithful port + live-reader no-regression is a dedicated effort, not a heartbeat tail (rushing it risks a
> subtly-wrong organ — the place-typing/VerbNet subsystems have real correctness surface). **Audit:** folded into
> `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

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
