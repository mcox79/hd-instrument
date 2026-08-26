---
priority: 3
review:
review_text:
---

# PROBLEM: we blend many bindings into ONE vector and un-mix on demand; the brain SEPARATES into slots and retrieves by MATCHING a (partial) cue -- and that is ~5x better under a degraded cue

**slug:** `content_addressable_retrieval_over_a_separated_store` - **opened:** 2026-08-26 by the strategy session
(the RE-LOCATED binding deviation -- from `the_core_binding_operator_may_not_be_brain_faithful` SOLVED/EXCELLENT)
**status:** OPEN - **the deviation is first-hand + CI-separated in the binding SOLVED; the fix organs are OWNED**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` (foundational tier), the slot the resolved
> binding-operator problem vacated. This is the deviation that problem RE-LOCATED: the operator is fine; the flat-
> superposition RETRIEVAL is the real, foundational, CI-separated (~5x) lever, and it UNIFIES three deviations
> (binding E1, situation-model register E2, coreference E3) under one brain mechanism. The fix organs are already
> owned (default-off), so this is wire-and-prove-on-the-live-task, not build-from-scratch. **Coordinate with p2
> (`the_consolidated_cortical_store...`) -- p2 is the READ half of the SAME memory architecture; do not duplicate.**

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

Our substrate crams many role-filler pairs into ONE vector and "un-mixes" them on demand. The brain does not do
this. It keeps things SEPARATE (a small set of slots) and finds the one you asked for by MATCHING your cue against
what is stored -- so a partial or noisy cue still recovers the right thing. The binding investigation built the
brain mechanism and stressed both with a degraded cue: the brain-style content-addressable separation recovered
the right filler **~5x more often, CI-separated, at equal storage** -- and the win was PREDICTED by the CA3
partial-cue dissociation (CA3 knockouts retrieve from full cues, fail from partial ones; Nakazawa 2002). The
uncomfortable part, and why this is tractable: **the substrate ALREADY OWNS the parts** -- a pattern-completer
(`ca3_completer`) and a pattern-separator (`dg_pattern_separation`), both default-OFF -- but the live register
(`situation_model_multibank`) routes by an EXACT-KEY HASH, which has no graceful path for a partial cue, so the
advantage is thrown away. Wire the content-addressable retrieval over the separated store and prove it lifts a
LIVE situation-model task under partial/unknown cues.

## 2. WHY THIS ONE

- **It is the re-located foundational deviation, and it is EVIDENCED (~5x), not conjectured.** The binding result
  validated the operator and located the fault one level up, in the flat-superposition retrieval.
- **It UNIFIES three audit deviations under ONE brain mechanism** -- binding (E1), the situation-model register
  (E2), and coreference (E3) all need cue-based content-addressable retrieval with similarity interference. Fix it
  once, gain in three places.
- **The parts are OWNED and default-off** (`ca3_completer.complete_addressed`, `dg_pattern_separation`) -- this is a
  wire-and-prove, which is high-leverage and low build-cost.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** retrieval of a bound item is CUE-BASED CONTENT-ADDRESSABLE with similarity interference -- you match
the (possibly partial) cue against stored items in parallel and complete to the nearest (Lewis & Vasishth 2005;
McElree cue-based retrieval; audit E3 pins this for coreference). The hippocampal implementation is a matched pair:
**dentate-gyrus PATTERN SEPARATION** (orthogonalise overlapping items) + **CA3 COMPLETION** (a partial cue settles
to the stored pattern) -- and CA3's defining behaviour is exactly PARTIAL-cue robustness (Nakazawa 2002 NMDAR-KO
dissociation). The brain SEPARATES first, then retrieves by matching; it does not superpose-and-unmix, and it does
not look up by an exact key.
**OUR-INVENTION-UNDER-TEST:** the matching/completion parameters (how the cue is matched to slot tags, completion
steps). Copy the COMPUTATION (separate + content-addressable match-and-complete); SWEEP the parameters.

**Corpus-age note:** McGuffey is ~200 years old; hold corpus era fixed across the retrieval test.

## 4. MEASURED vs INFERRED

**MEASURED (`the_core_binding_operator...` SOLVED, re-verified):** at equal storage, content-addressable theta
separation beats the hash-routed multibank CI-separated under a partial cue (0.379 [0.357,0.401] vs 0.199
[0.182,0.217]) EVEN when the hash router is handed exact-identity routing. **The LOAD-BEARING negative:** routing a
FLAT-superposition readback through the real CA3 attractor (`iterative_attractor`) TIES argmax -- you CANNOT clean
your way out of superposition crosstalk; the gain is ARCHITECTURAL (separate the store), not a terminal cleanup.
`situation_model_multibank` routes by `stable_bank_id(hash(event_idx))` -- its own docstring: "routing accuracy is
1.0 by construction", i.e. it assumes the key is known EXACTLY and has no partial-cue path. `ca3_completer`
(content-addressable) exists, DEFAULT-OFF.
**INFERRED (the open question, decisive either way):** whether routing the register's `decode()` through
content-addressable `ca3_completer` (over the SEPARATED multibank store, + DG separation for overlapping cues)
beats the hash route on a LIVE situation-model task under partial/unknown cues.

## 5. ALREADY TRIED (do not re-run)

- The SYNTHETIC binding-stress win (content-addressable ~5x under partial cue) -- DONE; it is the MOTIVATION, not
  the deliverable. Do NOT re-run it; the deliverable is the LIVE-task transfer.
- CA3 attractor cleanup on a FLAT readback -- TIES argmax (do NOT bolt an attractor onto the flat read; it moves
  nothing). Any cleanup must operate over a SEPARATED store.
- Query `experiment_index.py query "content addressable"`, `query "multibank"`, `query "ca3"`, `query "partial cue"`;
  read `hdlab/situation_model_multibank.py`, `hdlab/ca3_completer.py`, `hdlab/dg_pattern_separation.py` and the E2
  LOCALIZED_WALL cell first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Confirm `situation_model_multibank` routes by an exact-key hash with no partial-cue path (read `decode()` /
  `stable_bank_id`), and that `ca3_completer.complete_addressed` + `dg_pattern_separation` are default-off and do
  what §3 says.
- Find the LIVE harness: the situation-model register task where a partial/unknown cue arises (the binding SOLVED
  names E2's LOCALIZED_WALL cell as the natural one). Recompute its floor on the scored population.
- Positive-control the negative: confirm CA3 cleanup on the current FLAT read does NOT move it (so the win must
  come from separation + content-addressing, not cleanup).

## 7. THE BAR

On a LIVE situation-model / register retrieval task under a PARTIAL or unknown cue, floor recomputed on its
population: **content-addressable retrieval (route `decode()` through `ca3_completer` over the SEPARATED multibank
store, paired with `dg_pattern_separation` for overlapping cues) must beat the exact-key HASH route CI-separated
over the strongest floor's UPPER bound, with the info-free twin (shuffled slot tags / random routing) LOSING
CI-separated**, CI half-width + null p95 reported. Sweep the matching/completion parameters.
**DECISIVE EITHER WAY:** a win on the LIVE task -> wire it (strategy lands it; default-off flag; this is the ~5x
lever realised). A rigorous loss -> the synthetic separation win does NOT transfer to the live register (report
why -- too few slots, cues never partial in practice, etc.); that is a real finding and a full PASS, and it tells
us the flat store is adequate for the live regime. **Watch the McGuffey caveat and the "isolation win is not a
capability" rule -- the synthetic ~5x means nothing until it moves a LIVE number.**

## 8. FILES AND ENTRY POINTS

- `hdlab/situation_model_multibank.py` (the hash-routed register -- `decode()` / `stable_bank_id`),
  `hdlab/ca3_completer.py` (`complete_addressed` -- the owned content-addressable completer, default-off),
  `hdlab/dg_pattern_separation.py` (the separator), `hdlab/iterative_attractor.py` (CA3 settling).
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the binding re-location) + E1/E2/E3, and the binding SOLVED Rec B --
  report any correction as an AUDIT UPDATE. Coordinate with p2 (`the_consolidated_cortical_store...`).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). Do
  NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the synthetic ~5x (0.379 vs 0.199) as a downstream capability -- it is an isolation construction
  proof; it counts only when it moves a LIVE task number.
- Do NOT bolt an attractor/Hopfield cleanup onto the FLAT read -- it ties argmax (measured); the fix is separating
  the store, then content-addressing.
- Do NOT carry a number between the synthetic binding-stress instrument and the live register task -- different
  scorers/populations; recompute the floor on the live task.
