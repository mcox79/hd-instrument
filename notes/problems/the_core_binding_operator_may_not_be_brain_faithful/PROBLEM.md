---
priority:
review: EXCELLENT
review_text: "Re-verified scaffold-free (witness PASS, reproduced first-hand). A MODEL of the strengthened protocol: it REFUTED the surface question (is our bind operator wrong?) -- at EQUAL storage our compressed FHRR bind BEATS the two writable brain theories (tensor-product, conjunctive), so the operator is VALIDATED as efficient, not a liability -- then went one level DEEPER and located the REAL deviation: the flat-superposition RETRIEVAL architecture. We cram many bindings into one vector and un-mix on demand; the brain SEPARATES into slots and retrieves CONTENT-ADDRESSABLY, so a partial cue still works. Built the brain version (theta-gamma content-addressable separation) and stressed both with a degraded cue: it recovers ~5x more often (0.128 vs 0.025 at D64/N16/p0.9), CI-separated, at EQUAL storage, every info-free twin losing. Load-bearing negative: routing FHRR through the real CA3 attractor TIES argmax -- you cannot clean your way out of superposition, the fix is the STORAGE architecture. The substrate ALREADY OWNS the parts (ca3_completer, dg_pattern_separation, both default-off) but wires them so the advantage is lost. Honestly scoped as a synthetic construction proof, NOT a downstream win. Re-locates audit deviation E1 (operator validated; deviation is the retrieval, shared with E2/E3)."
---

> # MY REVIEW -- EXCELLENT. IT REFUTED THE SURFACE QUESTION, VALIDATED THE OPERATOR AGAINST THE BRAIN THEORIES, AND RE-LOCATED THE DEVIATION ONE LEVEL UP.
> *Reviewed 2026-08-26 (owner-DONE). Re-verified scaffold-free: `verification/verify_binding_operator_stress.py` PASS -- GUARD confirms FHRR_percomp == `hdlab.bundling.bundle` (the baseline IS the live op); info-free twins all lose (<0.008); HEADLINE theta 0.1281 [0.1164,0.1408] vs FHRR 0.0247 [0.0196,0.0310] CI-separated; CA3 attractor cleanup TIES argmax (0.0236 vs 0.0247); normaliser percomp 0.4003 < L2 0.5330; content-addressable theta 0.3865 > hash-routed multibank 0.1965 CI-separated.*
>
> ## WHY EXCELLENT
> The brief asked "is our central operation, the bind, non-brain-faithful?" The solver answered it AND then did the harder, more valuable thing: it showed the question was aimed one level too low. **The bind OPERATOR is fine** -- at equal storage the compressed FHRR multiply beats the two brain theories you can actually write as an equation (tensor-product / Whittington TEM product; Rigotti-Fusi conjunctive), so it is an efficient choice, not a lazy one. TPR loses to FHRR in every exact-cue cell. That is a rigorous VALIDATION of the invention -- exactly the "a negative validates the foundation" outcome the brief framed as a full PASS.
>
> ## THE REAL DEVIATION, LOCATED AND MEASURED
> The deviation is the flat-superposition RETRIEVAL built on the operator: we superpose many bindings into one vector and un-mix on demand; the brain SEPARATES (a few slots) and retrieves CONTENT-ADDRESSABLY (match the -- possibly partial -- cue, then complete). Under a degraded cue the brain mechanism (theta-gamma temporal separation) recovers **~5x more often, CI-separated, at EQUAL storage footprint**, every info-free twin losing -- and the win was PREDICTED by the CA3 partial-cue dissociation (Nakazawa 2002), not found by sweeping. The `theta_blind_slot` twin (random slot pick) loses CI-separated, so the role->slot MATCHING carries the information, not just clean storage.
>
> ## THE LOAD-BEARING NEGATIVE
> Routing the FHRR readback through the brain's own CA3 attractor (`hdlab.iterative_attractor`, alpha=0.5) TIES argmax -- for a single noisy readback vs a near-orthogonal codebook, argmax is already the MAP estimate. **You cannot clean your way out of superposition crosstalk; you have to not superpose.** This kills the tempting "add attractor cleanup to the flat read" fix and points all the way back to the storage architecture -- a genuinely valuable negative.
>
> ## HONEST LIMITS (flagged, withdraw-first) -- and my scope
> It is a SYNTHETIC-ALGEBRA construction proof, NOT a downstream comprehension win (the standing "isolation win is not a capability" lesson -- so the proposed changes MUST be measured on the live reading task before any capability claim). The theta win is REGIME-SPECIFIC (partial-cue / low-D interference; theta has a ~7-item capacity cliff and FHRR wins at exact cue). Roles are random/near-orthogonal, so the fan effect (where DG pattern separation would matter) is untested. All flagged withdraw-first. Exemplary.
>
> ## WHAT THIS CHANGES
> **The binding foundation is RESOLVED (validated) and RE-LOCATED to the retrieval architecture (shared with E2/E3).** Two hdlab changes are earned (Q111, I land them):
> - **A (small, safe, strongly evidenced):** the per-component superposition normaliser in `hdlab/bundling.py` only ever hurts (L2/raw-sum beat it 32/32, it wins zero); add a `norm="l2"` option -- WITH the coupled cosine readout in `hdlab/atoms.py:similarity` (which assumes per-component unit magnitude), landed together, DEFAULT-OFF, measured live before flipping. *Owner-flagged: touches the shared similarity path in two files, wants care.*
> - **B (the real lever):** give the SEPARATED store (`situation_model_multibank`) a CONTENT-ADDRESSABLE retrieval path for partial cues (route `decode()` through the owned, default-off `ca3_completer` instead of the exact-key hash), paired with `dg_pattern_separation`. This is where the 5x lives -- a capability build measured on the live situation-model task, recorded as the proven-ready direction.
> **AUDIT UPDATE folded into `BRAIN_FOUNDATIONAL_AUDIT.md`: E1 re-tagged (operator validated at equal storage; deviation is the flat-superposition retrieval; unifies E1/E2/E3 under cue-based content-addressable retrieval).**

# PROBLEM: our single most central operation -- binding a role to a filler -- is an OUR-INVENTION with no settled brain equation, and everything is built on top of it

**slug:** `the_core_binding_operator_may_not_be_brain_faithful` - **opened:** 2026-08-26 by the strategy session
(packaged from `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- the deepest foundational deviation, owner-directed
"attack the foundations first" 2026-08-26)
**status:** OPEN - **the deviation is first-hand in ORGAN_MAP E1 + the audit; re-verify before quoting**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3`, BELOW the two blocking foundational
> fixes (`sign->graded` p1, cortical-read p2) but ABOVE the downstream capability work (meaning-wiring, parser).
> It is foundational but NOT proven-blocking -- our binding is UNFALSIFIED, not shown wrong -- so a rigorous
> negative here (our invention is as good as the brain-motivated alternatives) is a full, valuable PASS that
> VALIDATES the foundation. Re-rank if you judge it more or less urgent than the meaning wiring.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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

Almost everything the substrate does -- holding "who did what to whom," storing a fact, building a situation
model -- rests on ONE operation: binding a role to a filler (tying "agent" to "dog" so we can later ask "who was
the agent?"). We implement that with a specific piece of vector math (FHRR/HRR "bind"). Here is the uncomfortable
truth the brain audit surfaced: **neuroscience does not know how the brain binds.** It is an open, three-way
contested question. So our central operation is NOT a replication of the brain -- it is OUR INVENTION, chosen
because it is convenient VSA math, and everything else is built on top of it. If that foundation is subtly
wrong, every layer above inherits the flaw. This problem asks the question directly: **is our binding operator
brain-faithful enough, or does one of the brain-motivated alternatives actually work better on a task that
genuinely stresses binding?** Either answer is worth having: a win replaces the foundation with a better one; a
rigorous loss VALIDATES the invention and lets us stop worrying about it.

## 2. WHY THIS ONE

- **It is the deepest foundation.** The audit ranks the binding operator as the single most central
  OUR-INVENTION. Unlike `sign()` (a known deviation) it is UNPINNED -- we cannot even score its fidelity, only
  test whether a more brain-motivated alternative beats it.
- **The owner's foundation-first directive names it.** If the substrate is predicated on anything non-foundational
  in a blocking way, attack it first. Binding is the last un-attacked foundation; this closes the set.
- **A negative is as valuable as a positive.** If FHRR ties or beats every brain-motivated alternative on a
  binding-stress task, we have EARNED the right to keep it -- turning an open worry into a settled decision.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**UNPINNED and actively CONTESTED three ways [OUR-INVENTION-UNDER-TEST is unavoidable here]:**
- **theta-gamma phase coding** -- items bound by firing in the same gamma slot within a theta cycle (Lisman &
  Jensen; ~7 slots/cycle).
- **conjunctive / mixed-selectivity coding** -- dedicated neurons fire for a specific role-filler conjunction
  (Rigotti & Fusi); perirhinal/hippocampal conjunctive codes.
- **tensor-product representation** -- role (X) filler outer product (Smolensky).
**PINNED-ADJACENT FACTS (the few anchors):** TEM's hippocampal conjunctive code is a PRODUCT `p = g (X) x`
(Whittington 2020); LATL conceptual COMBINATION is approximately ADDITIVE (Baron & Osherson). There is no settled
equation to be faithful to -- so the discipline is: **build each brain-motivated candidate as faithfully as the
literature allows, and test which (if any) beats our FHRR bind on the operation they all must perform.** Copy the
COMPUTATION (bind so that a role cue later recovers its filler under interference and partial cue); SWEEP the
parameters. Do NOT reach for a fourth convenient VSA trick -- the point is the brain-motivated set.

## 4. MEASURED vs INFERRED

**MEASURED (ORGAN_MAP E1, re-verify):** our `hdlab/binding.py` FHRR bind = elementwise complex multiply
(HRR = circular convolution; BSC = XOR). Known properties: separable superposition ~`0.956`; the per-component
complex normaliser costs **20-32% of d'** vs a whole-vector L2 normaliser; the oracle role-key derivation used
in some cells **has no mechanistic analog** (least-defensible). Fidelity is recorded as **UNSCORABLE** (brain math
UNPINNED) -- honestly, not claimed SAME.
**INFERRED (the open question, decisive either way):** whether a brain-motivated binding operator (theta-gamma
phase / conjunctive-mixed-selectivity / tensor-product) beats FHRR on a task that genuinely stresses binding --
multi-relation slot-filling recovered under interference, and relational retrieval under a PARTIAL role cue --
CI-separated, or whether FHRR ties/wins (validating the invention).

## 5. ALREADY TRIED (do not re-run)

- FHRR/HRR/BSC as binding operators -- built and in use (`hdlab/binding.py`); their basic separability is known.
  Do NOT re-benchmark bare separability; the open question is a BINDING-STRESS task vs brain-motivated alternatives.
- Learned-TPR role-key replacement -- CLOSED/deprioritized once (probe superposition-saturated, inconclusive);
  revisit ONLY with a non-saturated probe regime (ORGAN_MAP E1 note).
- Query `experiment_index.py query "binding"`, `query "tensor"`, `query "conjunctive"`, `query "theta"`; read
  `hdlab/binding.py`, `hdlab/perirhinal_conjunctive.py` (a default-off conjunctive encoder already exists),
  `hdlab/event_bundle.py`, and ORGAN_MAP E1 before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Confirm FHRR bind's actual op in `hdlab/binding.py` and the 20-32% normaliser cost; confirm
  `perirhinal_conjunctive.py` exists as a default-off conjunctive drop-in (a partial candidate already built).
- Build the binding-STRESS instrument yourself and recompute its floor: it must have real INTERFERENCE (many
  bound pairs superposed) and a PARTIAL role cue, because that is exactly where binding schemes diverge -- a
  clean single-pair bind separates trivially for all of them and would prove nothing.

## 7. THE BAR

On a binding-STRESS task -- multi-relation slot-filling recovered under interference AND relational retrieval
under a PARTIAL role cue, on a held-out population with floors recomputed on it -- **a brain-motivated binding
operator (theta-gamma phase / conjunctive-mixed-selectivity / tensor-product, built as faithfully as the
literature allows) must beat FHRR bind CI-separated over the strongest floor's UPPER bound, info-free twin
LOSING**, with CI half-width + null p95 reported. Sweep the operator's parameters; do not adopt a number.
**DECISIVE EITHER WAY:** if a brain-motivated operator wins -> propose replacing the bind (strategy lands it,
default-off flag; it changes the core op so extreme care). If FHRR ties/beats every brain-motivated alternative
on the stress task -> **the invention is VALIDATED** -- report that loudly; it retires the "our core operation
may be non-foundational" worry and lets the programme build on FHRR with confidence. A rigorous negative is a
PASS.

## 8. FILES AND ENTRY POINTS

- `hdlab/binding.py` (FHRR/HRR/BSC bind-unbind -- the operator under test), `hdlab/perirhinal_conjunctive.py`
  (default-off conjunctive candidate), `hdlab/event_bundle.py` / `hdlab/situation_model_accumulate.py` (the
  consumers that stress binding).
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (TIER 3 / deviation "the central binding operation") and ORGAN_MAP E1 --
  report any correction as an AUDIT UPDATE.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111).
  Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT claim FHRR is "brain-faithful" or "not brain-faithful" -- it is UNSCORABLE (the brain equation is
  unpinned). The only admissible claim is whether a brain-motivated alternative beats it on the stress task.
- Do NOT test on a single-pair clean bind (separates trivially for all schemes -- proves nothing); the
  interference + partial-cue regime is where they diverge.
- Do NOT reach for a convenient fourth VSA operator; the candidate set is the brain-motivated three.
