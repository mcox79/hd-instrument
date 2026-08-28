---
priority: 4
review:
review_text:
---

# PROBLEM: there is no glass-box verb-sense / POLYSEMY disambiguator, and it is a cross-cutting wall every text front-end pays — "left the room" (depart) vs "left a letter" (deposit), "returned home" vs "returned a reply" (said), "observed the move" (watched) vs "observed" (remarked), "passed away" (died) vs time-passed — build a minimal brain-faithful sense/frame disambiguator over the dependency parse (motion-vs-transitive, perception-vs-speech) that beats the most-frequent-sense floor CI-separated, twin losing, and lifts a downstream front-end

**slug:** `no_glass_box_verb_sense_disambiguation` — **opened:** 2026-08-28 by the strategy session (the precisely-named
wall from the integrated `theory_of_mind_residual_is_the_observation_cue_front_end` — polysemy bit BOTH its motion
extractor AND its gold labels). **status:** OPEN — a MECHANISM + INSTRUMENT problem. You build + validate in
`experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — BROAD leverage: verb polysemy is the diagnosed
> wall that caps the ToM observation cue, corpus mining of clean events, and any front-end reading motion / perception /
> state-change from prose. A minimal disambiguator lifts several organs. **Re-rank per the owner.**

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
The same word means different things: "she LEFT the room" (moved away) vs "she LEFT a note" (put down); "he RETURNED
home" (came back) vs "he RETURNED a sharp reply" (said); "she OBSERVED the swap" (saw) vs "she OBSERVED that..."
(remarked); "he PASSED AWAY" (died) vs "an hour PASSED". Our reader has NO glass-box way to tell these senses apart, so
every front-end that keys on a verb's meaning (motion → location update, perception → knowledge, state-change → event)
either over-fires or misses. This bit the theory-of-mind observation cue in two places at once: its motion extractor
(a manner verb used non-locomotively) AND the automatic gold labels (a mined "left"/"returned" with the wrong sense).
The brain crosses this with full lexical semantics; we need a minimal, glass-box substitute. The task: build a small
sense/frame disambiguator over the dependency parse — at least motion-vs-transitive-deposit and perception-vs-speech —
validate it beats a most-frequent-sense floor CI-separated on a real WSD gold with the info-free twin losing, and show
it lifts a downstream front-end (the ToM motion cue or a mined-event precision).

## 2. WHY THIS ONE
It is a shared front-end wall named precisely (not "the corpus is noisy") by a rigorous integration. Resolving even the
two dominant confusions (motion-vs-deposit, perception-vs-speech) raises the ToM cue, event mining, and any reader that
localises "what happened". A minimal glass-box disambiguator is a broadly-reused primitive.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** word sense is selected by CONTEXT via the argument structure / thematic frame the verb
  realises — the presence and type of arguments and satellites disambiguates the sense (a Goal/Path PP → motion; a
  Theme direct object of a physical object → deposit; a that-clause / quote → speech; a perceivable-event object →
  perception). This is FrameNet / VerbNet frame selection driven by SELECTIONAL PREFERENCE over the parsed arguments
  (Fillmore frames; Levin 1993 verb classes; the reader's own `graded_competition` cue-combination can score competing
  frames). The disambiguating signal is IN the realized syntax + the argument's semantic type, not the verb string.
- **OUR-INVENTION-UNDER-TEST (sweep):** the exact frame/feature set and the score threshold; the granularity (start with
  the two dominant binary confusions, not full WordNet WSD). Copy the COMPUTATION (frame selection by
  selectional-preference over parsed arguments); SWEEP the feature/threshold.
- **NOT brain-faithful:** a fixed verb→sense lookup (ignores context) or a manner-verb whitelist (the ToM solver proved
  the whitelist is the implementation trap).

## 4. MEASURED vs INFERRED
- **MEASURED (REUSE):** the ToM line names the exact confusions + shows a whitelist fails; `hdlab/thematic_role_labeler`,
  `hdlab/arc_parser`/`arc_labeler` (the dependency parse the features come from), the landed selectional-preference
  assets (`data/selectional_preferences_v1/`) and `hdlab/graded_competition` (the scoring currency) all exist.
- **INFERRED (to prove):** whether frame-selection-by-selectional-preference over the parse beats most-frequent-sense on
  a real WSD gold, and whether it lifts the ToM motion cue / mined-event precision.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT build a verb→sense whitelist or a full WordNet all-words WSD (out of scope + not the wall). Do NOT use an
  external LLM at inference (the invariant). Reuse the parse + selectional-preference assets + `graded_competition`.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the ToM SOLVED's polysemy section (`notes/problems/theory_of_mind_residual_is_the_observation_cue_front_end/SOLVED.md`),
  `hdlab/thematic_role_labeler.py`, `hdlab/arc_parser.py`/`arc_labeler.py`, `hdlab/graded_competition.py`,
  `data/selectional_preferences_v1/`. WSD gold: SemCor / a mined motion-vs-deposit + perception-vs-speech set (state how
  built + verified). `tools/experiment_index.py query "sense"` / `"polysemy"` / `"frame"`. Audit: the verb-polysemy wall entry (ToM §2b).

## 7. THE BAR
PASSES only with ALL of:
1. A glass-box sense/frame disambiguator over the dependency parse for AT LEAST the two dominant confusions
   (motion-vs-transitive-deposit; perception-vs-speech). Copy the computation; sweep the features/threshold.
2. Beats a **most-frequent-sense** floor CI-separated on a real WSD gold (recompute the floor on the same population);
   an **info-free twin** (shuffled frame features / random sense) LOSES CI-separated; report CI half-width + null p95.
   A positive control the metric can move (a context-flipped minimal pair the disambiguator gets and MFS cannot).
3. **Lifts a downstream front-end:** feeding it into the ToM motion cue (or a mined-event precision) measurably improves
   that number CI-separated vs the un-disambiguated path — i.e. it is a shared primitive, not an island.
4. One-screen summary; heavy runs → REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).
A rigorous NEGATIVE is a full pass (e.g. "frame-selection ties MFS on the gold, but the two-confusion disambiguator
still lifts the ToM cue" — the downstream lift alone passes).

## 8. FILES AND ENTRY POINTS
- `hdlab/thematic_role_labeler.py`, `hdlab/arc_parser.py`, `hdlab/arc_labeler.py`, `hdlab/graded_competition.py`;
  `data/selectional_preferences_v1/`; the ToM cue in `experiments/perceptual_access_ledger.py`. Audit + heavy→REMOTE.

## DO NOT QUOTE / DO NOT REDO
Do NOT restate the ToM polysemy examples as your result — they are the motivating evidence. Strategy owns any hdlab
landing — you propose the disambiguator, you do not write `hdlab/`.
