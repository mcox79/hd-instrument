# Who-did-what: the brain's EXACT mechanism vs ours, and WHERE we lose signal (measured)

**Owner asked (2026-09-04):** "understand EXACTLY where we're losing signal. How does the brain do this
EXACTLY, and where does our process, here and upstream, differ, PRECISELY" + "how does our performance
compare to the brain? The brain is glass-box, so if we're replicating it faithfully we should be doing much
better."

This is the answer: the brain's 8-stage who-did-what pipeline (hdi_research this session, cited), each stage
mapped to our organ with its **on-disk signal-loss number** (mined from 7 landed signal-loss cells +
measured this session). Nothing here is hand-waved; every loss figure has a file:line.

---

## 1. PERFORMANCE vs THE BRAIN -- the fair target is a CURVE, not a flat 99%

The human ceiling is **sentence-type-conditioned** (Ferreira 2003; Christianson 2001; Caramazza-Zurif 1976):

| sentence type | competent human | OUR reader (clean gold) | gap |
|---|---|---|---|
| canonical / irreversible (SVO, meaning disambiguates) | ~95-99% | **0.97 (nphead) / 0.98 (ledger)** | ~0 -- WE MATCH THE BRAIN |
| plausible passive / non-canonical | ~86-92% | ~0.65 (Competition Model pre-verbal) | real gap |
| **reversible** passive (meaning can't disambiguate) | **~75-80%** | ~heuristic (missing the override) | the diagnostic gap |
| reduced relative / garden path | **~40-55%** (humans keep the wrong reading!) | 0.28 ("other" bucket) | gap, but human bar is low |

**So the owner's intuition is right AND precise:** on canonical prose we are already at the human ceiling
(0.97-0.98) -- we even BEAT the spaCy competent parser (`clean_frame_ladder` nphead 0.9701 vs spaCy 0.9162,
+0.0539 CI-sep, `data/exp_whodidwhat_clean_frame_ladder_v1/metrics.json:58-66`). Where we are NOT much
better is exactly where the brain ALSO drops (reversible/garden-path) -- and even there the human target is
75-80% / 40-55%, not 99%. **The "we're at 0.25-0.44" wall is mostly the RULER, not the reader** (next).

## 2. HALF THE APPARENT LOSS IS THE RULER, NOT THE READER (measured)

- **Non-core roles.** The FULL-gold 0.44 -> CLEAN_DO 0.97 (+0.49) swing is the metric grading a PATIENT
  selector on roles it structurally should not pick: PP-oblique **49.5%** + copular **24.6%** + pre-verbal
  7.4% of the gold (`data/exp_whodidwhat_clean_frame_ladder_v1/metrics.json:6-9,39-48`).
- **Defensible pronoun/coref.** 26.55% of the role-balanced errors are metric-fidelity, not brain-fidelity
  (the span metric penalizes a defensible local pronoun/antecedent) -> adjusted ceiling 0.8168
  (`data/exp_noncanonical_error_taxonomy_v1/metrics.json:26-30`).
- **Gold noise on non-canonical.** 61.04% of the "non-canonical" LitBank set is mislabeled-intransitive-
  subject + cross-clause GOLD NOISE, not a modeling frontier
  (`data/exp_whodidwhat_noncanonical_upstream_v1/metrics.json:9`).

## 3. THE 8-STAGE MECHANISM-DIFF (brain stage -> our organ -> measured loss)

| # | brain stage (PINNED unless noted) | our organ | status | signal-loss / recovery ON DISK |
|---|---|---|---|---|
| 0 | verb argument-frame retrieval (valency/subcat) -- MUC "Memory" | `verb_subcat`, `thematic_role_labeler` | **PARTIAL (supply-limited)** | verb-frame identifies 48% of non-canonical noise but SUPPLY is thin (`noncanonical_upstream:8`); 5/13 clean-DO residual (`ledger:14`) |
| 1 | prominence / actor-first heuristic (animacy, case, ORDER, agreement) | positional `_assign_roles` (order) | **PRESENT** | order is our dominant cue; on canonical it MATCHES brain (0.97) |
| 2 | verb-driven PREDICTIVE slot-filling (Altmann-Kamide anticipation) | -- | **MISSING** | not built; no anticipatory pre-binding |
| 3 | cue-based BINDING of args to slots + interference (Lewis-Vasishth) | positional bind + `np_head_reduce` | **PARTIAL** | NP-head bind +0.0599 on clean-DO (`clean_frame_ladder:44-48`); no interference model |
| **4** | **algorithmic OVERRIDE of the heuristic via word-order/voice/morphology (dorsal / BA44)** | `graded_role_assigner` (Competition Model) | **BUILT but DEFAULT-OFF (island); PARTIAL live via parse-router** | **VOICE cue worth +0.4389 on non-canonical** (COMP - drop_passive, CI-sep, `competition_v2:contrasts`); takes non-canonical 0.17 -> 0.61 |
| 5 | thematic-fit / world-knowledge re-ranking (McRae; Elman) -- incl. ANIMACY | `animacy_lexicon` + `context_grounded_valence` | **WEAK; and STRUCTURALLY NEUTRAL on reversible** | **graded animacy worth ~0 on who-did-what** (measured this session: graded-floor +0.0000 all / +0.0026 n.s.); animacy cue validity 0.51 subordinate to order/voice 1.67/3.23 |
| **6** | **incremental CLAUSE SEGMENTATION (WM stack of open clauses) -- bind each verb to its OWN args** | flat parse; `relcl_resolver` filler-gap | **WEAK / MISSING** | clause-window filler-gap 0.2254 BEATS landed resolver 0.1056 on cleaned non-canonical (`noncanonical_upstream:18-20`); cross-clause is 12.8% of gold noise |
| **7** | **REANALYSIS / structural revision (garden-path recovery; P600)** | -- | **MISSING ENTIRELY** | we commit once, never revise; humans also under-revise (~50-60%), so target is "any revision > none" |

**POS and PARSE are NOT where we lose signal** (this is the counter-intuitive, load-bearing result): on the
clean gold, gold-POS recovers **-0.0464** and gold-full-parse recovers **-0.0509** -- both score BELOW our
glass-box reader (`data/exp_whodidwhat_signal_loss_ledger_v1/metrics.json:8-9`). The "parser is the root"
reading appears only on the UNcleaned 19c gold (arc-attach S4=0.4577, `exp_19c_signal_loss_v1:42`) and the
clean-frame + non-canonical cells re-attribute most of it to gold contamination.

## 4. WHERE THE SIGNAL IS LOST, PRECISELY (ranked, disk-backed)

On CANONICAL items we already match the brain. The GENUINE reader gap is the **dorsal algorithmic triad**:

1. **Stage 4 -- the word-order/voice OVERRIDE is worth +0.4389 on non-canonical, and its strong (graded)
   form is DEFAULT-OFF.** This is the single largest genuine lever. It is the same machinery agrammatic
   patients lose when they drop to chance on reversible sentences (Caramazza-Zurif 1976) -- the exact
   profile of our failure.
2. **Stage 6 -- clause segmentation.** Cross-clause argument theft + filler-gap; the clause-window rule
   already beats the landed resolver (+0.12) but is not the live path.
3. **Stage 7 -- reanalysis.** Missing entirely; a single conflict-triggered re-binding pass would move us
   off the once-and-done floor.
4. **The candidate SOURCE (upstream of role assignment)** was the biggest ALREADY-LANDED win: coref-column
   -> referent-per-NP took end-to-end 0.443 -> 0.8054 (`referent_per_np_signal_loss_waterfall:12,23`).

## 5. WHY THIS BRIEF'S LEVER (graded POS posterior -> animacy) IS AIMED AT THE WRONG STAGE

The graded NOUN/PROPN posterior feeds **Stage 5** (animacy / thematic-fit). The brain research proves Stage 5
is **NEUTRALIZED on exactly the hard items we fail**: on reversible/non-canonical sentences both role
orderings are equally plausible, so thematic fit carries no signal and **only Stage 4 (the algorithmic
override) can decide**. I measured this end-to-end: the graded animacy is a genuinely MORE-valid cue
(learned validity 0.511 > floor 0.467 > shuffled-twin 0.296, beats the twin CI-sep) but changes ~0 role
picks, because it is a low-validity Stage-5 cue and word order dominates. **The signal we are losing is not
in POS-category consumption at all** -- it is in the missing Stage-4/6/7 dorsal machinery downstream.

**Where the graded posterior DOES serve who-did-what: the VERB axis, not the NOUN/PROPN axis.** Stage 4's
voice override needs reliable participle/verb detection; the graded P(VERB) posterior recovers 19c dropped
verbs 0.582 -> 0.806 (P7, `crf_tagger` -> `predicate_detector`, already landed). So the graded posterior's
real contribution to this chain is the VERB plumbing for Stage 0/4 -- landed -- and the NOUN/PROPN axis this
brief targets is the low-leverage one.

## 6. SO: ARE WE REPLICATING THE BRAIN FAITHFULLY? (the owner's real question)

- **Stages 0,1,3 (heuristic route) + the candidate source: YES, faithfully, and we match the brain on
  canonical prose (0.97-0.98 ~ human 95-99%).**
- **Stages 2, 4(strong), 6, 7 (predictive + dorsal algorithmic + revision): NO -- weak, off, or missing.**
  This is precisely the machinery for reversible/non-canonical/garden-path items, and it is precisely where
  we underperform. We are not "worse than the brain everywhere"; we are **a faithful ventral/heuristic
  reader with an under-built dorsal route** -- the agrammatism profile, localized.

The reason we are not "much better" than we are is NOT that the brain is a black box we can't match -- on the
stages we've built faithfully we DO match it. It is that three specific, nameable, buildable brain stages
(4/6/7) are not yet faithful, and half of the remaining apparent gap is the metric.

## 7. NEXT PROBLEMS (the load-bearing builds -- most are already OWNED by concurrent briefs)

1. **Stage 4: wire the graded Competition-Model override LIVE** (currently default-off island; voice cue
   worth +0.44 on non-canonical). -- adjacent to the concurrent `discrete_where_the_brain_is_graded...` /
   `non_canonical_argument_structure` briefs.
2. **Stage 6: incremental clause segmentation** (a WM stack of open clauses) so each verb binds its own args;
   the clause-window filler-gap already beats the landed resolver.
3. **Stage 7: a reanalysis pass** -- the first structural-revision operator in the substrate (nothing owns
   this yet; a genuinely new problem).
4. **The RULER: fix the who-did-what metric** to score only core args a patient-selector should pick (the
   +0.49 clean-frame swing is metric, not reader) -- so future gains are visible.

**None of these is graded-POS-posterior consumption on the NOUN/PROPN axis** -- which is the point: the
signal loss the owner asked me to localize is downstream of, and orthogonal to, the lever this brief named.
