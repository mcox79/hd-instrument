---
priority: 6
review:
review_text:
---

# PROBLEM: the reader builds a situation model but cannot REASON over it to answer inference questions on real text. The reader now assembles a genuine situation model — who/what (roles), WHEN (timeline), WHERE (space), WHY (causation), and belief organs — and it can improve the MEANING of words by reading. But the North-Star capstone (`turn_on_the_learner…`, EXCELLENT) drew a sharp boundary: growth helps comprehension that reduces to SIMILARITY (+0.06 paraphrase) but is essentially NEUTRAL on inference multiple-choice QA (+0.005 on MCScript2), because those questions need REASONING over the situation model — combining facts, bridging the unsaid, chaining — not surface similarity. And the reasoning organs we DO have (`situation_model_has_no_discourse_fact_reasoning` EXCELLENT; `the_reader_cannot_answer_a_question_over_its_situation_model` STRONG; `transitive_comparison_reasoning…` EXCELLENT) are validated largely in ISOLATION / on curated inputs, NOT driven end-to-end from the reader's OWN assembled situation model on real inference benchmarks. So the reader cannot yet answer a question that requires reasoning over what it just read. Drive question-answering / multi-hop INFERENCE over the reader's OWN situation model (the assembled who/what/when/where/why) through `SituationReader.read()` on a real inference benchmark, and PROVE it beats a similarity-only floor and a no-situation-model floor CI-separated with the info-free twin LOSING — or, if the live situation model is too sparse/noisy to support inference, enumerate WHY (which, per SPACE, likely points at the parser-recall / forward-prediction ceiling). This is the FIRST STEP toward REASONING — the North Star's remaining half now that meaning-learning is proven.

**slug:** `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference` — **opened:** 2026-08-31 by the
strategy session (owner: "work towards reasoning"; the capstone's honest boundary — growth helps similarity, not
inference MC-QA — localizes the gap to reasoning over the situation model). **status:** OPEN — a WIRE + MEASUREMENT
problem (the situation-model dimensions are assembled + the reasoning organs are built; this drives inference over the
reader's OWN model on real benchmarks and measures where it breaks). You build + validate in `experiments/`; strategy
lands any hdlab wire (Q111, default-off, witness required). NO external LLM at inference (the invariant — the reasoning
must be glass-box over the substrate's own situation model, not an LLM QA).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` — the FIRST STEP of the REASONING direction, the
> North Star's remaining half (meaning-learning is now proven; reasoning is what's left). Ranked below the immediate
> learner endgame (live-canary p3), the assembly-validation (p4), and belief (p5) because it OPENS a large new direction
> and its first job is exploratory (find the ceiling), but it is strategically the highest-leverage frontier. This is a
> FIRST can-fail step (inference over the live situation model on real benchmarks), NOT the whole reasoning program.
> **Re-rank per the owner** — if reasoning is the priority, this rises. ⚠️ Compose with the reader's capable flags ON
> (`python tools/reader_capabilities.py`, incl. `timeline_register`). MIND the corpus-age confound (MCScript2 is modern).

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
The reader now builds a real mental model of a story — who did what, when, where, why, who-knows-what. But if you ask it
a question that needs it to REASON over that model — combine two facts, fill in something unsaid, follow a chain — it
can't. We saw this sharply: learning-by-reading made it much better at "does this mean the same thing" but barely moved
"answer this question about the story," because the second one needs reasoning, not similarity. Make the reader answer
real inference questions BY reasoning over the model it just built — querying it, combining facts, bridging gaps — and
prove on a real question-answering benchmark that it beats both a "just use word-similarity" baseline and a "no model at
all" baseline, with a scrambled-model control that must fail. If the model it builds is too thin or noisy to reason
over, say exactly why — that tells us whether the wall is the reasoning step or the reading step underneath it.

## 2. WHY THIS ONE
Meaning-learning is proven; REASONING is the North Star's remaining half, and this is its first concrete, measurable
step. The capstone localized the gap precisely (growth helps similarity, not inference MC-QA), so we know exactly where
to push. We already have reasoning building blocks (discourse-fact reasoning, question-over-situation-model, transitive
comparison) — but they've never been driven from the reader's OWN assembled model on real inference questions. Proving
(or honestly bounding) that end-to-end is the first step that turns "the reader understands a story" into "the reader can
reason about a story."

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the operation):** comprehension = building a SITUATION MODEL and drawing INFERENCES over it, not
  matching surface form (Kintsch construction-integration 1988; van Dijk & Kintsch — the situation model is the level
  inference operates on). BRIDGING / knowledge-based inferences fill the unsaid (Graesser, Singer & Trabasso 1994).
  Multi-hop reasoning = CHAINING facts through the model (relational/transitive composition — the substrate's proven
  weak→strong three-tier combination + `transitive_comparison`). Answering a question = a CUE-BASED RETRIEVAL + match
  against the model (the substrate's convergent retrieval operation), then an inference step, NOT a similarity lookup.
- **OUR-INVENTION (sweep, do NOT adopt as truth):** the question→situation-model MATCHING (how a question cues the
  relevant model slots), the inference CHAINING depth/policy, and the answer read-out. Glass-box over the substrate's OWN
  situation model — NO external LLM QA (the invariant); the answer must be an inspectable derivation over the model.

## 4. MEASURED vs INFERRED
- **MEASURED (INHERIT, do NOT re-derive):** the capstone's boundary — growth is +0.06 on paraphrase but +0.005 on
  MCScript2 inference MC-QA (twin-loses read-out valid). The reasoning organs are validated in isolation:
  discourse-fact reasoning (EXCELLENT), question-over-situation-model (STRONG), transitive comparison (EXCELLENT). The
  situation-model dimensions (roles/time/space/causation) are assembled + wired (see `tools/reader_capabilities.py`).
- **INFERRED (you must measure):** whether driving inference over the reader's OWN assembled situation model on a real
  inference benchmark (MCScript2 MC-QA + a multi-hop set) beats a similarity-only floor AND a no-situation-model floor
  CI-separated, info-free twin (shuffled situation model) LOSING, with a multi-hop discriminator (accuracy vs # inference
  hops) — or is ceiling'd (the live model too sparse/noisy), enumerated (which likely points at the parser-recall /
  forward-prediction wall SPACE + the capstone already named).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The 4 reasoning organs above (integrated) — INHERIT their isolation results; do NOT re-derive them. This is the
  END-TO-END inference over the reader's OWN live situation model on real benchmarks.
- `the_reader_cannot_answer_a_question_over_its_situation_model` (STRONG) — the receptive/query end; build ON it, this is
  the inference end (questions that need COMBINING, not lookup).
- The MEANING learner (capstone) — growth is NEUTRAL on MC-QA; do NOT re-run the growth experiment. The gap is REASONING
  over the model, not more meaning.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/reader_capabilities.py` (turn the capable flags ON — reasoning needs the full model). Read the
  reasoning organs' witnesses + `the_reader_cannot_answer_a_question_over_its_situation_model`'s cell (the query end) +
  the capstone's MCScript2 cell (`experiments/exp_learner_growth_mcscript_v1.py`) for the inference-boundary finding +
  the read-out that made the twin lose. Read how SPACE/belief drove a dimension end-to-end from the reader's own model.
- Pick a real inference benchmark: MCScript2 MC-QA (modern, script/commonsense inference) + a multi-hop set if reachable
  (a bridging-inference gold on LitBank passages is fine; report n). MIND the corpus-age confound (MCScript2 is modern).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a real inference benchmark, answering BY reasoning over the reader's OWN assembled situation model through
`SituationReader.read()`:
- **PASS =** inference accuracy CI-separated over BOTH floors — (a) a SIMILARITY-ONLY floor (the meaning read-out /
  paraphrase similarity alone, which the capstone showed is ~+0.005 on inference) and (b) a NO-situation-model floor
  (surface/lexical baseline) — with the info-free twin (SHUFFLED situation model — same slots, scrambled bindings)
  LOSING CI-separated, AND a multi-hop DISCRIMINATOR (accuracy degrades gracefully with # inference hops, not a cliff)
  as the graded reasoning signature. Report CI half-width + null p95 beside every margin; the derivation must be
  inspectable (glass-box, no LLM).
- **A rigorous NEGATIVE is a full PASS:** if the reader's OWN situation model is too sparse/noisy to support inference on
  real prose (inference not beaten CI-separated), name WHY — enumerated (which inference types fail; is it the model's
  RECALL [the parser wall] or the reasoning STEP [a missing inference mechanism]?). That discriminates the two halves of
  the North Star's remaining frontier and tells the reasoning program exactly where to build.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`: compose the reasoning organs (question→model matching + inference chaining) over the reader's
  OWN situation model from `SituationReader.read()`; score inference accuracy + both floors + the shuffled-model twin +
  the multi-hop discriminator from source through the live reader. A scaffold-free witness recomputes every headline.
  Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the bar, strategy lands the hdlab wire
  (Q111, default-off `answer_query` / reasoning read-out). This is the first live node of the REASONING program — the
  North Star's remaining half.

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the reasoning organs' ISOLATION numbers as a LIVE result — they are the inherited baselines; this
  measures inference over the reader's OWN live situation model on real benchmarks (a different population). No number
  crosses scorers/populations.
- 🚫 Do NOT use an external LLM to answer — the reasoning must be a glass-box, inspectable derivation over the substrate's
  own situation model (the invariant).
- 🚫 Do NOT re-run the meaning-growth experiment — the gap is REASONING over the model, not more meaning (the capstone
  proved growth is neutral on inference MC-QA).
