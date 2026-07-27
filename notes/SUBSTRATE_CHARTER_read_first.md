# SUBSTRATE CHARTER — READ FIRST, EVERY SESSION (the anti-drift anchor)

If you read one thing, read this. It exists because sessions have strayed (tangents, re-deciding settled things, reaching for shortcuts). Before starting ANYTHING, confirm it serves THE GOAL and the CURRENT FOCUS below.

## THE GOAL (one sentence)
Build a glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS (inspectable derivations, not parroting), by having it EARN its meaning and knowledge the brain's way — then keep developing it.

## INVARIANTS (never violate — this is what "brain-true" means here)
1. **Glass-box:** reasoning is inspectable; NO external LLM at inference.
2. **No borrowed embedding** (GloVe / BGE / any transformer vector) as the meaning organ, AND **no bolt-on existing reader/parser** (situation_reader, spaCy, external NLP) as the comprehension organ (USER 07-27: "EVERY time you used an existing reader it was a disaster"). The substrate EARNS meaning AND comprehension itself — error-driven, its own learned mechanism. Supplying KNOWLEDGE/DATA (CSKG, grounding norms) is fine; supplying the MEANING or COMPREHENSION mechanism is the forbidden shortcut.
3. **Brain = existence proof + reference standard.** It does this, so it IS achievable. A shortfall is NEVER a ceiling: on every negative, evaluate the difference between what we do and how the BRAIN does it, and iterate toward the brain's mechanism. Do NOT be defeatist; do NOT lead with fail-odds.
4. **VET every load-bearing verdict** before treating it as fact (the Director over-reads positives — the VET is the guardrail; separate MEASURED from READ).
5. **Check prior work FIRST, on the FILESYSTEM** (experiments/ + data/*/metrics.json + atoms), not just KB cosine-query — we have done a LOT; build on it, don't reinvent.

## THE THREE LAYERS (the whole build, in dependency order)
1. **REPRESENTATION (meaning)** — substrate LEARNS grounded, generalizing concept reps. **← CURRENT FOCUS / the blocker.**
2. **KNOWLEDGE (relations/facts)** — dense, vetted per-concept; MAY be sourced from external tools, but represented + reasoned-over glass-box (held-out slice reserved to prove reasoning, not parroting).
3. **REASONING** — additive multi-constraint constraint-satisfaction (brain CA3 attractor) over layers 1+2. Reasoning scales with the NUMBER OF CONSTRAINTS brought to bear.

## CURRENT FOCUS (the one thing — do not stray from this)
Make the LEARNED representation scale on REAL data the brain's way: fix the learning objective (global/landmark, teacher-free-capable), wean off any external teacher onto an INTERNAL self-teacher, ground it (Binder/experiential), and judge it ONLY on **held-out-to-NEW-concept generalization (memorizing = FAIL).** Full detail: `THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md`.

## ANTI-DRIFT RULE (say it before you dispatch)
"Does this serve the current-focus layer (learned grounded representation), the brain's way?" If you find yourself testing inference/tricks over SUPPLIED symbolic KBs, reaching for a borrowed vector, re-deciding a settled direction, or building before checking prior work — YOU HAVE STRAYED. Stop and re-anchor here.
