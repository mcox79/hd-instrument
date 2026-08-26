---
priority:
review: EXCELLENT
review_text: "RE-INTEGRATED 2026-08-26 on the owner's per-problem owner_verdict:DONE (after an earlier PREMATURE integration off a directional 'yes' was reverted -- see the process note in this file's history). Outcome PARTIAL, work EXCELLENT. All THREE regimes re-verified scaffold-free FIRST-HAND: (1) READ-OUT REFUTED -- test_sign_quantiser_not_the_bottleneck_on_hit1.py PASS (graded vs sign +0.0015 NULL; the whole faithful code-format family + a self-supervised CBOW learner tie counting ~0.05, all CI-below the 0.171 generic-word floor; only WordNet-SUPERVISED beats it -> the read-out wall is meaning SUPPLY, not the sign). (2) BINDING CONFIRMED -- exp_superposition_capacity_binding_v1 reproduces: graded beats sign for CORRELATED bound codes, capacity cliff B*=8->12 at d=256 (B8 0.88/0.58, B12 0.67/0.36), correlation-specific. (3) LIVE LATENT -- exp_live_binding_load_signgap_v1 reproduces verdict SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL: real load mean B=2.85 (14% B>4), atomic fillers |cos|0.06 -> gap +0.013 (~0 today); graded-semantic fillers |cos|0.25 -> +0.044, +0.087 on the B>4 tail. So the brief's instinct about the OPERATION was right but named the wrong PLACE: sign() is NOT the averaging machine at the read-out, but IS one at BINDING for correlated codes -- a LATENT guardrail COUPLED to the graded-code (B4) fix, not a current bug and not a standalone win. FOLDED: audit deviation #2 = PARTIAL (read-out refuted + binding latent-coupled-to-B4); the read-out's two-similarity-systems finding drives the new p1 build; the binding guardrail recorded against the B4/binding line (p3, p5) -- when B4 makes fillers graded-semantic, the sign()-on-a-bundle sites (situation_focus, role_slot_summarizer, event_bundle, CA3 cleanup_family) go graded in the SAME change. NO hdlab landing (latent; do NOT land standalone). A model of the strengthened protocol: refuted the surface question, swept the whole faithful family, doubted the TARGET (found the two-systems map), then found the real regime where the operation DOES bite and live-verified it as latent."
---

> ## SOLVER REVIEW (strategy, 2026-08-26 — re-integrated on the owner's per-problem owner-DONE)
> **Grade: EXCELLENT. Outcome: PARTIAL.** All three regimes re-verified scaffold-free first-hand.
> - **READ-OUT — REFUTED.** `sign()` is null on the real open-vocab task (+0.0015); the whole brain-faithful
>   code-format family + a faithful self-supervised CBOW learner all tie plain counting (~0.05), below the 0.171
>   generic-word floor; only WordNet-SUPERVISED learning beats it. The read-out "averaging machine" is a meaning-SUPPLY
>   + measurement-axis + structure problem, not the quantiser. (Drove the new **p1** two-similarity-systems build.)
> - **BINDING — CONFIRMED.** For CORRELATED bound codes, graded beats sign; capacity cliff **B\*=8→12** at d=256,
>   correlation-specific. The brief's instinct about the OPERATION was right — it just named the wrong PLACE.
> - **LIVE — LATENT.** Real binding load is mean B=2.85 with atomic near-orthogonal fillers, so it does **not** bite
>   today (gap ~0); it bites (+0.087 on the B>4 tail) only once binding is made brain-faithful (graded-semantic
>   fillers). So it is a **GUARDRAIL coupled to the graded-code (B4) fix**, not a current bug and not a standalone win.
> **Folded:** audit deviation #2 = PARTIAL; the binding guardrail recorded against the B4/binding line (p3, p5) — when
> B4 makes fillers graded-semantic, the `sign()`-on-a-bundle sites (`situation_focus`, `role_slot_summarizer`,
> `event_bundle`, CA3 `cleanup_family`) go graded in the SAME change, gated on the two binding cells. No hdlab landing.

# PROBLEM: a `sign()` at the end of almost every step throws away signal STRENGTH and keeps only DIRECTION -- turning the substrate into an averaging machine, where the brain codes GRADED

**slug:** `the_sign_quantiser_makes_the_substrate_an_averaging_machine` - **opened:** 2026-08-26 by the strategy session
(packaged from `notes/BRAIN_FOUNDATIONAL_AUDIT.md` deviation #2 -- the highest-blast-radius fidelity gap in the substrate)
**status:** OPEN - **the defect is first-hand in the audit + ORGAN_MAP, re-verify before quoting**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. This is the single most CROSS-CUTTING
> brain-fidelity deviation we have -- it is present at ~34 sites across 12 modules and shapes nearly every
> composition/read-out in the pipeline. Fixing it (or bounding where it must stay) has the largest blast radius
> of anything unqueued. Re-rank if you judge a narrower, more-proven build higher.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> **📐 COUPLED FIX -- DENSE -> SPARSE (folded in here per owner 2026-08-26, to keep the queue focused).** The
> `sign()` quantiser and our DENSE code are the SAME representation deviation seen from two angles: the brain
> codes GRADED *and* SPARSE + higher-dimensional; we code 1-bit *and* dense (~2,377 concepts in 256 dims). The
> largest measured single lever we own is dimensionality -- 16x dims buys +0.0843. So this brief's real target is
> the representation FORMAT: test GRADED (drop the terminal `sign()`) AND sweep dimensionality / sparsity together,
> because meaning that survives superposition needs both (a graded code that is also sparse enough not to
> collide). Report which of the two -- losing strength, or lacking capacity -- dominates on the real task.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the system combines evidence -- several readings of a word, several features of a concept -- it adds them
up (which is right; the brain's concept combination is additive too). But then, at the very end, it runs
`sign()`: it throws away HOW STRONG each dimension is and keeps only whether it was positive or negative. Do that
after a sum and something specific happens: whenever the shared part of the evidence is bigger than the
distinctive part (which is almost always), the answer collapses onto the shared part. The system stops
representing "this particular thing" and starts representing "the average thing in this neighbourhood." It
becomes a prototype/averaging machine. The brain does NOT do this -- cortical codes are GRADED (they keep
strength), and the pooling step the brain uses (divisive normalisation) is graded, not a 1-bit threshold. The
graded path already exists in our code behind default-OFF flags. The question is whether turning it on -- keeping
strength instead of just sign -- makes the system represent the DISTINCTIVE thing well enough to win a real task.

## 2. WHY THIS ONE

- **Blast radius.** The `sign()` quantiser is at ~34 sites / 12 modules; it sits at the end of word encoding, the
  concept hub, per-occurrence pooling, comparison, CA3 completion, the store, prediction. A single fidelity fix
  here touches more of the substrate than any other queued item.
- **It is a NAMED, PINNED deviation.** The brain codes graded (ORGAN_MAP B4, PINNED: dense/graded/low-dim, NOT
  binary), and per-occurrence pooling is divisive normalisation (B2, PINNED), NOT a sign threshold. Our terminal
  `sign()` is the inverse of both.
- **The pieces exist.** Graded flags (`freeze_graded`, `graded_query`) are already in the code, default-OFF -- the
  work is proving graded wins on a REAL task (and where it does not), not building from scratch.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** cortical semantic codes are GRADED and low-dimensional (IT sparseness ~0.2-0.3; explicitly NOT
1-bit) -- strength is information the brain keeps. The per-occurrence combination the brain uses is **divisive
normalisation** (`r_i = x_i^n / (sigma^n + sum_j x_j^n)`, Carandini & Heeger) -- a graded, pool-normalised rate
code, not a threshold. Conceptual COMBINATION in LATL is approximately ADDITIVE (Baron & Osherson) -- so the SUM
our code takes is already faithful; **only the terminal `sign()` normaliser is not.**
**OUR-INVENTION-UNDER-TEST:** WHERE graded must be kept vs where a quantiser is acceptable (capacity is a real
constraint we partly share -- superposition of many graded codes can collide). Copy the brain's COMPUTATION
(graded pooling / divisive normalisation at the composition and read-out steps); SWEEP the parameter (which
sites, dimensionality, the normalisation exponent) -- never adopt a number.

**Corpus-age note:** the reading corpus (McGuffey) is ~200 years old; if a graded read-out looks flat on modern
gold, ask whether corpus modernity is doing the work before concluding graded does not help.

## 4. MEASURED vs INFERRED

**MEASURED** (`ORGAN_MAP.md` + `BRAIN_FOUNDATIONAL_AUDIT.md`, re-verify): `sign()` is at ~34 sites/12 modules;
`sign(shared + distinctive) = sign(shared)` wherever shared dominates, so it acts as a prototype extractor. The
SUM it sits on is faithful (additive). **The half-fix caveat, and it is load-bearing:** removing the `sign()`
buys `+0.0602` on a 2AFC instrument but **~null on open-vocabulary hit@1**, and there is a SEPARATE
superposition-capacity cliff below B=4 for correlated codes -- so which loss dominates depends on which codes are
being summed and on which task you score.
**INFERRED (the open question, decisive either way):** whether turning on the graded (non-`sign`) path at the
composition/read-out steps beats the `sign`'d path **on a REAL downstream task** (open-vocab read-out or the
meaning/recall instrument), not just 2AFC -- and if so, at which sites and at what capacity cost.

## 5. ALREADY TRIED (do not re-run)

- The bare 2AFC `sign`-removal (+0.0602) -- known; do NOT re-quote it as a capability, it does not transfer to
  hit@1. The open question is the REAL task.
- Free Hebbian "clumping"/isotropic tricks that raise cosine without raising the channel -- refuted (LONG_TERM_
  PLAN §2). Do NOT reach for a cosine-raiser; the target is task performance over a floor.
- Query `experiment_index.py query "graded"`, `query "sign"`, `query "quantise"`; read the `freeze_graded` /
  `graded_query` flag sites in `reading_grounding_loop.py` and `bundling.py` before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Enumerate the actual `sign()` / `np.sign` / `torch.sign` sites (do not trust the count) and identify which sit
  on the LIVE composition/read-out path vs off-path.
- Confirm the `freeze_graded` / `graded_query` flags exist and what they switch; confirm the DEFAULT is sign'd.
- Pick the real downstream task and recompute EVERY floor on its population (the constant/prototype floor is the
  one that has repeatedly beaten graded arms -- include it).

## 7. THE BAR

On a REAL downstream task (open-vocabulary read-out hit@1, or the meaning/recall instrument -- NOT a bare 2AFC),
on a held-out population with all floors recomputed on it: **the graded (non-`sign`) path must beat the `sign`'d
path CI-separated over the strongest floor's UPPER bound** (include the constant/prototype floor), **info-free
twin LOSING**, with the CI half-width and null p95 reported beside the margin. Sweep WHICH sites are made graded
(the whole point is to find where strength matters) and report the capacity cost (does superposition collapse
below B=4?).
**DECISIVE EITHER WAY:** if graded beats the sign'd path on the real task -> flip those sites to graded (propose
the hdlab diff; strategy lands it, default-off flag). If graded only helps 2AFC and stays null/negative on the
real task at every site -> the `sign()` is NOT the bottleneck for that task and the loss is elsewhere (capacity,
or the codes being summed carry no distinctive signal) -- report that precisely; a rigorous negative is a PASS
and it retires "the sign is the problem" as the headline.

## 8. FILES AND ENTRY POINTS

- `hdlab/reading_grounding_loop.py` (`freeze_graded`, `canonicalize_fast` sign sites, `graded_query`),
  `hdlab/bundling.py`, `hdlab/grounding_acquisition_loop.py`, `hdlab/hd_fact_store.py` -- the composition/read-out
  sign sites.
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (deviation #2; tiers B2/B4/C1) and `notes/ORGAN_MAP.md` §"cross-cutting
  arithmetic defect" -- the audit rows; report any correction as an AUDIT UPDATE.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, board Q111).
  Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the 2AFC `+0.0602` as evidence graded fixes the system -- it does not transfer to hit@1.
- Do NOT carry any number between the 2AFC and the open-vocab/recall instruments -- different scorers, no number
  crosses. Recompute every floor on the real task's population.
- Do NOT "fix" it by raising cosine with free clumping -- refuted; the target is task accuracy over a floor.
