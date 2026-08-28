---
priority: 5
review:
review_text:
---

# PROBLEM: theory-of-mind's belief mechanism is LANDED and perfect with oracle observation (1.000), but the end-to-end drops to 0.821 because reading "did this character WITNESS the change?" from prose is unsolved — build the brain-faithful observation-cue front-end (perceptual access / "seeing = knowing"), validate it beats the lexical baseline CI-separated on a CORPUS-mined false-belief gold, twin losing

**slug:** `theory_of_mind_residual_is_the_observation_cue_front_end` — **opened:** 2026-08-28 by the strategy session (owner
MUSED a dedicated ToM re-eval after p1 landed). **status:** OPEN — a MECHANISM + DATA problem. You build + validate in
`experiments/`; strategy lands any hdlab change (Q111). Builds on the LANDED `hdlab/belief_partition.py`.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5`, below the learner (p2) + foraging (p3) + the
> phase-diagram (p4). This STRENGTHENS an already-integrated result (theory-of-mind), so it is a refinement, not a new
> capability — but it targets the one measured residual (the observation front-end) + the honest corpus-generality gap. Re-rank per the owner.

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
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (Theory of Mind / mentalizing; the
> front-end); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission.

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just landed a real Theory-of-Mind ability: the reader tracks what each character BELIEVES separately from what's actually
true, and gets false-belief questions perfect (100%) — WHEN it's told who saw what. But reading "**did this character
actually WITNESS the change?**" from ordinary prose is unsolved: a crude keyword matcher gets it right only ~81% of the
time, which drags the whole ability down from 100% to 82%. And the test stories were hand-written by the solver, so we
haven't shown it works on REAL story passages. Build the brain's way of deciding "did the character see it?" — perceptual
access, the "seeing-leads-to-knowing" principle young children use — and prove it on real, corpus-mined false-belief passages.

## 2. WHY THIS ONE

It is the ONE measured residual of an otherwise-perfect, already-landed organ (`hdlab/belief_partition.py`), and it closes
the honest corpus-generality gap the solver flagged. It is also the SAME front-end class we keep hitting ("the front-end is
the binding constraint") — reading a specific relation (here: did agent A perceive event E?) from arbitrary text — so a win
here generalises the front-end story. It does NOT re-open the belief mechanism (that is solved + landed).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED — perceptual access → knowledge ("seeing is knowing").** Children track knowledge via PERCEPTUAL ACCESS: an
  agent knows a fact iff it perceived (or was informed of) it (the developmental ToM literature; the false-belief task
  turns on exactly this). The observation cue = "was agent A perceptually present / informed at the moment of the change?".
  This is the input the landed `belief_partition` gate consumes (`believed_location(observed, initial, final)`).
- **PINNED — it is a discourse/situation-model inference, not a keyword.** "While she was out", "he had gone to the field",
  "asleep", "watched from the doorway", "was told" — the cue is carried by PRESENCE / ABSENCE / INFORMED state in the
  event structure, which is exactly what the situation model + coreference + the entity register already track (agent
  location vs event location over time). Build the observation cue AS a read of the situation model, not a regex.
- **OUR-INVENTION-UNDER-TEST:** the exact extractor. The landed lexical version (0.808) is the STAND-IN to beat. COPY the
  computation (perceptual-access inference over the event/entity structure), SWEEP the parameters.

## 4. MEASURED vs INFERRED
- **MEASURED (the integrated ToM work, `hdlab/belief_partition.py`):** with ORACLE observation, belief-acc 1.000; with the
  lexical text extractor (0.808 cue accuracy), end-to-end 0.821 — the FULL_TOM(oracle) − LIVE gap localises the residual to
  the observation cue. The belief mechanism, controls, and dissociations are DONE (do not redo).
- **INFERRED (to test):** a brain-faithful observation-cue extractor (perceptual-access inference over the situation/entity
  structure) beats the 0.808 lexical baseline CI-sep AND lifts end-to-end toward the oracle 1.000, on a CORPUS-mined (not
  authored) false-belief gold. UNPROVEN — could be null (a valid PASS: the residual is elsewhere / the cue is genuinely hard).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The per-agent belief partition IS solved + LANDED (`belief_partition.py`) — build the observation FRONT-END that feeds it,
  do NOT rebuild the belief mechanism, the controls, or the dissociations.
- The lexical extractor (0.808) is the BASELINE to beat, not a result to reproduce.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reverify the belief organ: `.venv/Scripts/python.exe verification/test_belief_partition_organ.py` (+ the integration
  witness `verification/test_theory_of_mind_realtext.py`).
- Read `hdlab/belief_partition.py` (the gate consuming `observed`) + `experiments/exp_theory_of_mind_realtext_v1.py`
  (`extract_observed_from_text`, the 0.808 lexical baseline) + the situation/entity organs (`situation_model_accumulate`,
  `salience_binder`, coref) you should read the cue FROM.
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the ToM entry) — the residual is named there.

## 7. THE BAR
PASSES only with ALL of:
1. **The observation-cue extractor beats the 0.808 lexical baseline CI-separated** on cue accuracy (did agent A witness
   event E?), on a **CORPUS-mined false-belief gold** (real story passages, not authored) — recompute the strongest real
   floor; info-free twin (shuffled presence/absence signal) LOSES CI-sep; report CI half-width + null p95.
2. **Lifts the END-TO-END belief accuracy** (feeding the LANDED `belief_partition`) toward the oracle 1.000, CI-separated
   over the lexical-cue end-to-end 0.821 — the whole point is the composed lift, not the cue in isolation.
3. **Brain-faithful mechanism:** the cue is a PERCEPTUAL-ACCESS inference read from the event/entity/situation structure
   (presence/absence/informed at the moment of change), NOT a keyword list. State the operation. COPY the computation, SWEEP params.
4. **A corpus-mined false-belief gold exists + is verified** (the honest corpus-generality gap): real passages where an agent
   holds a belief the world has since falsified, with the observation state derivable from the text; report how it was mined + verified.
A rigorous NEGATIVE (a faithfully-built perceptual-access extractor does NOT beat the lexical baseline on real corpus text) is
a FULL PASS — localising why (the cue needs coref the reader lacks / the corpus is too sparse / it needs the incremental parser).

## 8. FILES AND ENTRY POINTS
- Organ + baseline: `hdlab/belief_partition.py`, `experiments/exp_theory_of_mind_realtext_v1.py` (`extract_observed_from_text`).
- Read the cue FROM: `hdlab/situation_model_accumulate.py`, `hdlab/salience_binder.py`, the coref organs.
- Gold source: mine real false-belief passages (LitBank / Gutenberg narrative; the situation-model corpora on disk).
- **Route heavy corpus-scale runs to the REMOTE GPU box** (`tools/queue_add.py`).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (ToM).

## DO NOT QUOTE / DO NOT REDO
The belief mechanism (1.000 with oracle observation), its controls, and its dissociations are DONE + LANDED — do not redo
them. The lexical extractor (0.808) is the BASELINE. Strategy owns the hdlab landing — you propose the diff (the observation
front-end + a corpus gold), you do not write `hdlab/`.
