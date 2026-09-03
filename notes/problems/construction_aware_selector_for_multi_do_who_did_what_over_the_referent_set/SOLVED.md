---
problem: construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set
status: REFUTED
bar: "PASS = a glass-box construction-aware SELECTOR (Goldberg argument-structure constructions as high-validity cues over the referent-per-NP candidate set; NO external LLM) that raises the LIVE reader's effective who-did-what CI-separated over the current selector, with a shuffled-construction info-free twin LOSING CI-separated and NO regression on canonical single-DO clauses. Report CI half-width + null p95; lead with a CLEAN gold (the 19c who-did-what gold is ~76% oblique-contaminated). A rigorous located NEGATIVE — the construction cues do not net-help live beyond the structural-DO selector, with the named cause — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "LOCATED NEGATIVE (the brief's sanctioned FULL PASS). A Goldberg construction-aware selector adds 0.0000 over the LIVE proximity/Competition-Model theme selector (hdlab.graded_role_assigner.hybrid_role_patient), scorer pick==gold_head abstain=wrong, at THREE levels: (1) SELECTOR-level over the referent-per-NP candidate set, cleaned-DO 19c LitBank n=149: +0.0000 CI[-0.0201,+0.0201] half=0.0201 null_p95=0.0134; full cleaned-DO n=669: -0.0030 CI[-0.0105,+0.0045] (slightly NEGATIVE); multi-DO subset n=162: -0.0123 CI[-0.0432,+0.0185]. (2) END-TO-END through the actual live SituationReader().read() on 25 LitBank conll docs: FULL n=1354 +0.0000 CI[0,0], CLEAN_DO n=149 +0.0000 CI[0,0]. (3) MODERN QA-SRL n=1261: -0.0008 CI[-0.0040,+0.0016] (register-invariant null). Our live selector is statistically TIED with a competent reader (spaCy oracle, reference-only): 0.9283 vs 0.9223, +0.0060 CI[-0.0164,+0.0284] n.s."
floor: "Strongest floor actually run = the LIVE reader's deployed theme selector hdlab.graded_role_assigner.hybrid_role_patient (Competition-Model: word-order-dominant resolve_patient + voice/gap/animacy overrides, np_head_reduce ON) -- the EXACT function the wired route_predicate_arguments calls at line 427. Selector-level over referent-per-NP candidates: 0.9283 (cleaned-DO n=669); it already BEATS the experimental ideal_pick baseline the prototype used (0.8984, +0.030) -- the prototype's +0.146 was ideal_pick's animacy-override bug, not a real gain. Deployed end-to-end (coref source, all net-positive flags): CLEAN_DO 0.4698 / FULL 0.2105 (the parent's source-loss floor; construction leaves it byte-identical). Reference ceiling: competent reader (spaCy) 0.9223, statistically TIED."
controls: "(1) SHUFFLED-CONSTRUCTION info-free twin: construction ROUTE fires at the same rate on the same multi-DO clauses but the picked end is randomised -- it LOSES to the construction arm (selector +0.034 CI-sep n=149; end-to-end +0.013 n.s.), BUT this is a TRAP that does NOT prove capability: randomising an already-correct proximity pick hurts; the honest bar is construction-vs-LIVE (=0.000), not construction-vs-twin. (2) NO-REGRESSION on single-DO clauses: construction vs live = +0.0000 CI[0,0] (identical -- the routing only touches multi-DO give/naming). (3) GENERALIZATION twin: the null replicates on modern QA-SRL (-0.0008) and 19c (-0.0030) -- register-invariant. (4) BRAIN-COMPARISON oracle (spaCy, reference-only): ours TIED with the competent reader (+0.006 n.s.); of our 48 residual errors, 56% are recoverable by a better PARSE (a fidelity gap owned by the parser problems) and 44% are a genuine ambiguity/gold-noise ceiling the competent reader ALSO misses. (5) END-TO-END through the real read() (not just the isolated selector): confirms 0.000, ruling out that the selector-level isolation hid a live effect. (6) IDEAL_PICK re-baseline: reproduces the prototype's +0.146 over ideal_pick, then shows it collapses to 0 over the live selector -- isolating the artifact."
files_changed: "experiments/exp_construction_aware_selector_diagnosis_v1.py, experiments/exp_construction_aware_selector_residual_v1.py, experiments/exp_construction_aware_selector_brain_comparison_v1.py, experiments/exp_construction_aware_selector_generalization_v1.py, experiments/exp_construction_aware_selector_live_reader_v1.py, experiments/exp_construction_ideal_composition_v1.py, verification/test_construction_aware_selector.py, notes/problems/construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set/SOLVED.md, notes/problems/construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set/OWNER_NOTES.md. (REUSED read-only: experiments/exp_referent_per_np_selection_improvement_v1.py [the parent prototype -- re-ran once to reproduce; byte-identical science], exp_whodidwhat_ideal_brain_foundational_v1.py, exp_whodidwhat_coverage_transitivity_control_v1.py, exp_19c_composed_cleaned_gold_v1.py, hdlab/graded_role_assigner.py, hdlab/relcl_resolver.py, hdlab/predicate_argument_frontend.py, hdlab/situation_reader.py, hdlab/np_head_reduce.py.) NO hdlab/ written."
reverify: ".venv/Scripts/python.exe verification/test_construction_aware_selector.py   # 9/9 -- selector-level null (n=149) + full-power null (n=669) + premise-refuted + tied-with-brain + parse-is-the-real-lever + register-invariant + end-to-end null + IDEAL-composition indef-pronoun win (CI-sep) + composition ceiling 0.969, all from landed metrics.json (re-runs no cell)"
---

# REFUTED — a construction-aware selector adds nothing over the live proximity/Competition-Model selector

## Status in one line
A Goldberg construction-aware selector adds **exactly 0.000** to effective who-did-what over the LIVE theme selector
(`hybrid_role_patient`) — at the selector level (n=149 and n=669), end-to-end through the real `read()` (n=1354), and
in modern register (n=1261) — because the live selector's word-order/proximity rule **already** implements the
double-object construction's role assignment, and the brain assigns thematic roles by **feature-competition, not
construction-template retrieval**. Our live selector is statistically **tied with a competent reader** (0.928 vs
0.922). This is the brief's explicitly-sanctioned located NEGATIVE (a FULL PASS), and it corrects the brief: the
prototype's +0.146 / "84% multi-DO" premise was an artifact of the experimental `ideal_pick` baseline's animacy bug.

## 0. THE OPENING MOVE — how does the brain assign a thematic role, and are we replicating it? (owner's standing question)
I opened with the brain, not the tool. I ran a 5-lane brain-mechanism research drill (`research_construction_vs_competition_brain_foundational_2026-09-03.md`). The convergent finding, PINNED across the primary neuroscience:

**The brain assigns thematic roles by graded FEATURE-COMPETITION, not by retrieving a construction template.**
- **Frankland & Greene 2015 (PNAS), 2020 (Cereb. Cortex):** left mid-STC holds an abstract agent/patient slot code that is **verb-independent and surface-syntax-independent** (active/passive decoded identically; no region encodes surface subject/object). Construction/event-specific conjunctions live *separately* in amPFC — a complementary prior, not the binding mechanism.
- **Bornkessel-Schlesewsky & Schlesewsky eADM (2006, Psych. Review):** one weighted **prominence-competition** (animacy, case, voice, order) runs everywhere; only the cue *weights* vary by language/construction — no per-construction template is retrieved.
- **Hagoort MUC / Vosse & Kempen 2000:** lexicalist unification by **competitive inhibition** among candidate attachments — again feature-competition.
- **Bates & MacWhinney Competition Model:** English is **word-order-dominant**; other cues override order only on marked structures.

Our live selector `hydlab.graded_role_assigner.hybrid_role_patient` (word-order-dominant `resolve_patient` + voice/gap/
animacy overrides via `graded_competition`) **is** this mechanism. A Goldberg construction-template router bolted on
top is therefore *less* brain-faithful, not more — the brain does not do construction-template retrieval for role
binding; constructions enter only as event-schema priors (amPFC / Kuperberg), which are verb/event-specific and are
already what the Competition-Model cues encode.

**Why construction is REDUNDANT with word-order here (the crux):** Construction Grammar's own flagship evidence
(Bencini & Goldberg 2000; Johnson & Goldberg 2013 jabberwocky; Kako 2006 nonce verbs) dissociates the construction
from the **VERB'S** meaning — and every stimulus is in **canonical word order**, so the construction's template *is*
a word-order pattern. No CxG study pits word-order against the construction and shows the construction win. The
Competition Model predicts exactly this: high-validity cues **converge** on canonical structures. So on canonical
English multi-DO, word-order (proximity) and the ditransitive construction assign the **same** role. That is why the
gain is zero.

## 1. THE DECISIVE MEASUREMENT — the disk outranks the brief
The brief's prototype (`exp_referent_per_np_selection_improvement_v1`) measured the construction fix at **+0.040 all /
+0.146 multi-DO CI-sep** — but its BASELINE was the experimental `ideal_pick`, whose animacy override mis-fires on the
double-object construction ("pay passengers a penny" → passengers animate, penny inanimate → `ideal_pick` returns the
inanimate theme "penny"; the who-did-what gold is the recipient "passengers"). The construction rule "fixes" that back
to nearest-post-verbal — **which is what the LIVE reader already does.** I re-baselined against the actual live
selector `hybrid_role_patient` (the exact hdlab function `route_predicate_arguments` calls), holding the candidate set
= referent-per-NP:

| arm (cleaned-DO 19c) | ALL n=669 | MULTI-DO n=162 | give-class | naming-class |
|---|---|---|---|---|
| `ideal_pick` (prototype baseline) | 0.8984 | 0.6790 | — | — |
| **LIVE `hybrid_role_patient` (the floor)** | **0.9283** | **0.9136** | 0.871 | 0.500 |
| + construction (Goldberg, over LIVE) | 0.9253 | 0.9012 | 0.871 | **0.250** |
| shuffled-construction twin | 0.9013 | 0.8025 | — | — |

- **construction vs LIVE (ALL): -0.0030 CI[-0.0105,+0.0045] n.s.** (slightly negative). **MULTI-DO: -0.0123 n.s.**
- On **give-class the live selector is already at 0.871 = the construction ceiling** (nearest-post-verbal already
  picks obj1 = recipient = the gold patient). On **naming the construction rule HURTS** (0.50→0.25): the "patient" of
  a naming clause is genuinely inconsistent in the gold (see §3), so `naming→last-DO` is wrong as often as right.
- **No single-DO regression:** construction vs live = +0.0000 CI[0,0] (identical — routing touches only multi-DO
  give/naming).

**End-to-end through the actual `SituationReader().read()`** (25 conll docs, monkeypatching only `hybrid_role_patient`):
FULL n=1354 **+0.0000 CI[0,0]**, CLEAN_DO n=149 **+0.0000 CI[0,0]**. The selector-level isolation is the *higher-power*
test (it strips the upstream source/event losses common to both arms — the deployed reader is 0.47/0.21, ~0.30 below
the selector's 0.93, all of it upstream); end-to-end can only dilute an already-null selector difference, and it does:
still exactly zero.

## 2. THE BRIEF'S PREMISE WAS AN ARTIFACT (correction, per "the disk outranks the brief")
- **"84% of residual errors are multi-DO competition":** that was `ideal_pick`'s residual. Under the LIVE selector the
  residual (48 errors on n=669) is **only 25% multi-DO competition**; it is dominated by single-DO head/parse errors
  (37.5%), oblique/cross-clause gold (23%), and indefinite-pronoun coverage (15%). Multi-DO (0.914) actually *beats*
  single-DO (0.933... i.e. is comparable) — it is not the bottleneck.
- **"+0.146 on the multi-DO subset":** reproduced first-hand over `ideal_pick` (+0.1463 CI[+0.049,+0.268]), then shown
  to be **0.000 over the live selector**. The number was real but measured against a buggy baseline.
- **"distributional re-rank adds +0.007 n.s. over constructions":** stands, and is now moot — constructions are 0 over
  live, so the distributional re-rank (which was subsumed by constructions) is also 0 over live.

## 3. WHERE WE DIFFER FROM A BRAIN — the residual decomposed (owner: "how do we perform vs a brain, and where exactly")
Competent-reader oracle = spaCy dependency parse (REFERENCE-ONLY, the documented diagnostic exception; nothing on the
inference path). Our live selector **0.9283** vs competent reader **0.9223** — **+0.006 CI[-0.016,+0.028] n.s., a
statistical TIE.** We are AT a competent reader on the selection task. Of our 48 residual errors:
- **56% (27) are recoverable by a better PARSE** (a fidelity gap the brain closes): clefts ("what frightened people"),
  locative inversion ("were seen the landscapes"), apposition ("her sister Celia"), relative-clause attachment ("the
  house Mrs Carey died in"), long-distance/garden-path. The research says exactly where each belongs: **clefts =
  filler-gap PARSER** (unambiguous, not selector-fixable — Ferreira 2003; the 2026 filler-gap-family work); **locative
  inversion = parser + a discourse old/new module** (Birner & Ward 1998; Bresnan 1994); **passive** is already handled
  by our voice cues.
- **44% (21) are a genuine ceiling the competent reader ALSO misses** — ambiguity + gold noise, chiefly the
  **object-complement / naming** construction. This is **ill-posed, not a fixable gap**: small-clause syntax (Stowell
  1981; den Dikken 2006) makes "the matrix verb's patient" of "call X Y" a category error (the object is the whole
  small clause [X Y]); and whether the internal subject is a "patient" (resultative account, Sánchez 2023) or a
  "theme of a classification relation" (stative account, Matushansky 2008) is an **actively unsettled dispute in
  linguistics as of 2023.** Our gold proves it: for naming verbs, spaCy's `dobj` (the named thing) matches gold 10×
  and its complement `oprd` matches gold 15× — there is **no single ground-truth patient** to select.

## 4. GENERALIZATION (owner: "consider whether this needs to generalize, and how the brain does it")
The null is **register-invariant**: construction-vs-live is -0.0008 on modern QA-SRL (n=1261) and -0.0030 on 19c
LitBank (n=669). This is the brain-faithful prediction — English word-order dominance is a robust, register-invariant
default (Competition Model; Ferreira good-enough processing). The research adds an honest nuance (a real, non-blocking
lever elsewhere): literary/older prose carries MORE non-canonical order (heavy-NP-shift ~5-10% even in modern prose,
Wasow 1997; quotative inversion concentrated in fiction, Cichosz; locative inversion in narrative), so a
proximity-only rule misfires *more* in those pockets — but the fix there is the **PARSE + a discourse module**, not
construction re-weighting. (One genuine open gap the research flagged: whether experienced readers re-weight
Competition-Model cues by register is UNTESTED — an assumption, not a finding.)

## 5. WAS THE REAL PROBLEM SOLVABLE A DIFFERENT WAY? (protocol: refuting the brief is the halfway point)
The real problem underneath is "improve who-did-what role SELECTION over the referent-per-NP candidate set." I
establish it is **NOT solvable by any selector route I could test** beyond the deployed live selector, because:
- the live selector is **already at the competent-reader ceiling** (0.928 vs 0.922, tied) at the selector level;
- every remaining selector-level lever is **out of the selector's scope**: the parse (clefts/inversion/apposition —
  filed as `parser_arceager` / relcl work), the source (indefinite-pronoun coverage — the parent's referent-per-NP
  territory), the meaning channel (the genuine-ambiguity tail — the filed learner-on successor), or **ill-posed**
  (naming/object-complement — no ground truth exists).
- Routes tested and shown null/negative over the live selector: Goldberg construction routing (give + naming);
  distributional selectional-preference (subsumed, per the parent); `ideal_pick`'s animacy override (net-NEGATIVE vs
  the live selector). The brain's own mechanism (feature-competition) is what is already deployed.

So the honest answer is not "we failed to build it" — it is "the deployed selector is already the brain-faithful
mechanism at the competent-reader ceiling; the remaining who-did-what signal is upstream (source/parse) and in the
meaning channel, all separately owned." The BIG end-to-end lever is not the selector at all: the deployed reader is
0.47/0.21 because of the SOURCE loss (the parent's referent-per-NP wire, gated on the coref linker), while the selector
given clean candidates is 0.93.

## 7. THE IDEAL, EXACT BRAIN-FOUNDATIONAL SOLUTION — prototyped + measured (`exp_construction_ideal_composition_v1`)
"Do we have enough to prototype the ideal, including upstream optimizations to maximize performance?" **YES — and the
key structural fact is that the ideal's SELECTOR is already deployed and at ceiling, so the ideal is defined by the
UPSTREAM stages.** The composition, each stage PINNED-vs-OUR-INVENTION, measured on cleaned-DO n=669 (selector task,
gold verb):

| stage | brain mechanism | status | measured |
|---|---|---|---|
| **S1 SOURCE** | referent-per-NP introduction (Kamp 1981 / Heim 1982 DRT) | PINNED (parent's, landed default-off) | base 0.9283 |
| **S1 opt: indefinite-pronoun coverage** | DRT opens a referent for QUANTIFIED/indefinite NPs too (everybody/thee) | PINNED — **NEW, buildable, prototyped here** | **0.9283 → 0.9387, +0.0105 CI[+0.003,+0.019] CI-sep, twin loses** |
| **S3 SELECTOR** | feature-competition (Bates & MacWhinney; eADM; Frankland-Greene abstract role code) | PINNED — **already at ceiling, held fixed** | 0.9283 = spaCy 0.9223 (tied) |
| **S-PARSE** (clefts/inversion/register-POS mistags) | hierarchical structure-building + register-native tagging | the FILED parser/POS problems (bounded here) | **ceiling 0.9686, +0.040 CI-sep** (best-of ours-or-competent) |
| **meaning-fit + ill-posed naming** | thematic-fit on meaning (McRae/Ferretti) / small-clause | GATED / ill-posed | genuine residual **3.1%** |

**The composition ceiling on the selector task is 0.969**, leaving a **3.1% genuine, irreducible residual** (12
ill-posed naming/object-complement clauses with no ground-truth patient + 9 gold-noise/hard). Two readings:
- **The one genuinely NEW buildable win is upstream and small: indefinite-pronoun SOURCE coverage** (+0.0105 CI-sep,
  twin loses). It is source-side (the parent's referent-per-NP territory) — recommend it as a tiny referent-per-NP
  extension. The SELECTOR itself has no buildable win (it is at the competent-reader ceiling).
- **The +0.040 "competent-parse" ceiling decomposes into ALREADY-FILED upstream problems, NOT a new selector or even a
  new dependency parser** (`exp_construction_ideal_composition_v1` + the residual dump): ~7 indefinite pronouns
  (captured by the S1 opt above), **~5-6 register-native POS mis-tags** (the 19c tagger tags "cheery-looking",
  "dreamiest", "nicens" as NOUN, so the selector picks a mis-tagged adjective as the nearest post-verbal noun — the
  parent's filed register-native-POS problem), and ~2-3 filler-gap **pseudo-clefts** ("what frightened people" — the
  filed parser). Confirmed on disk: those adjectives ARE tagged NOUN by the deployed tagger.

**To MAXIMIZE END-TO-END performance (the honest ranking):** the selector-task ceiling (0.969) is not the deployed
number — the deployed reader is 0.47 (clean) / 0.21 (full) because of the **SOURCE loss**, not the selector. So the
single biggest lever by far is **turning on the referent-per-NP SOURCE** (0.47→0.81 end-to-end, the parent's measured
+0.336), which is GATED on the coref linker (filed). Then register-native POS (~+0.01 of the parse ceiling), then
indefinite-pronoun coverage (+0.0105), then filler-gap clefts. Every one is upstream; none is the selector.

## KEY REALIZATIONS (the enabling moves)
- **Re-baseline against the function the live reader actually calls, not the experimental one in the prototype.** The
  entire +0.146 was `ideal_pick`'s animacy override picking the inanimate theme where the gold is the animate
  recipient. Swapping the baseline to `hybrid_role_patient` (line 427 of `predicate_argument_frontend`) collapsed the
  gain to exactly zero. *The prototype answered a different question than the bar asked.*
- **Word-order and construction give the SAME answer on canonical English — the cue is redundant, not absent.** The
  construction is real (Goldberg); it just carries no information the proximity cue doesn't already carry on canonical
  ditransitives. This is the Competition Model's cue-convergence, and it is why the brain's own role code (Frankland &
  Greene) is surface-syntax-*independent*: it doesn't need the construction label to bind the role.
- **The shuffled-construction twin "winning" is a TRAP, not evidence.** Randomising an already-correct pick hurts, so
  the twin loses — but the honest comparison is construction-vs-LIVE (=0), not construction-vs-twin. A control that
  can make a null look like a win is worse than no control; the fix was to report the direct baseline delta.
- **The naming-clause gold is genuinely under-determined, and the literature says so.** spaCy's dobj vs oprd both match
  ~half the naming gold; small-clause syntax + a live 2023 linguistics dispute say there is no single "patient." Do
  not build a rule for an ill-posed target.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy re-verifies + folds in)
`situation_reader` who-did-what SELECTOR (`hybrid_role_patient` via `route_predicate_arguments`): the deployed
theme selector is the brain's feature-competition mechanism (Bates & MacWhinney Competition Model; eADM prominence
competition; Frankland & Greene surface-syntax-independent role code) and is **already at the competent-reader
ceiling** (0.928 vs spaCy 0.922, tied) on the who-did-what selection task over a clean candidate set. A Goldberg
construction-aware selector adds **0.000** (selector-level, end-to-end, modern + 19c) — construction is REDUNDANT with
word-order on canonical English; the brain does not do construction-template retrieval for role binding (PINNED). The
who-did-what selector is therefore NOT a lever; remaining signal is upstream. **Two corrections to the parent
`open_a_discourse_referent_...` write-up (its NEXT-STEP #1 + IDEAL composition):** (a) the "construction-aware selector
0.873→0.913 (+0.146 multi-DO)" gain is an artifact of the experimental `ideal_pick` baseline's animacy override and is
0.000 over the deployed live selector — DO NOT land it; (b) `ideal_pick` (used in the parent's ideal composition) is
NET-NEGATIVE vs the deployed `hybrid_role_patient` at the selector level (0.898 vs 0.928) — its animacy override
should not be adopted.

## 6. ADJACENT-COMPONENT MAP → candidate next problems (owner's standing instruction; each EVALUATED for fidelity)
| component | brain status | measured limitation | is it a lever? | next problem |
|---|---|---|---|---|
| **who-did-what selector** (`hybrid_role_patient`) | PINNED (Competition-Model feature-competition = the brain's mechanism) | at competent-reader ceiling (0.928); construction adds 0 | **NO** — do not add cues | none (this refutation) |
| **the PARSE** (clefts / locative inversion / apposition / relative-clause attachment) | filler-gap = PINNED parser job (not selector) | 56% of the residual is recoverable by a better parse | YES (upstream) | `parser_arceager` route (filed) + a discourse old/new module for inversion |
| **candidate SOURCE** (indefinite-pronoun objects: everybody/somebody/thee) | referent introduction = PINNED (Kamp/Heim) | 15% of the residual: gold pronoun not opened as a referent (referent_per_np excludes STOP/pron) | YES (upstream, small) | extend referent-per-NP to indefinite-pronoun heads (parent's source territory) |
| **object-complement / naming** ("call/make X Y") | ILL-POSED (small-clause; patient vs theme unsettled in linguistics 2023) | ~ the genuine-ceiling residual; gold inconsistent | NO (no ground truth) | if anything, a small-clause EXTRACTOR (emit both args), not a patient selector |
| **meaning-fit selector** (genuine ambiguity) | thematic-fit on MEANING = PINNED (McRae/Ferretti) | the deepest residual; competent reader also loses ~0.15 | GATED | the filed learner-on / meaning-channel successor |

## What I did NOT establish (would withdraw first if wrong)
- I did NOT run the full end-to-end with the referent-per-NP SOURCE turned on (it is default-off / coref-regressing,
  parent territory); the end-to-end confirmation used the DEPLOYED coref-source reader. This is conservative: the
  selector-level test already isolates the selector over the referent-per-NP candidate set and is null, and the SOURCE
  affects both arms identically, so it cannot resurrect a null selector delta. First to re-examine if a wire ever
  turns the rnp source on.
- The competent-reader oracle is spaCy (reference-only); "tied with a brain" is "tied with a strong parser proxy," not
  a human study. The 44%/56% residual split depends on spaCy's parse quality; a stronger parser would shift some of
  the 44% into recoverable — which would only *strengthen* "the lever is the parse, not the selector."
- I re-ran the parent's `exp_referent_per_np_selection_improvement_v1` once to reproduce it; that re-dated its landed
  `metrics.json` (byte-identical science: 0.9128/0.7805 matched the doc). No science changed; the timestamp did.
- The multi-DO give-class n is modest (31 on n=669); the give-class "already at ceiling" claim is on that n. The
  end-to-end and register-invariance results do not depend on it.

---

### TLDR (plain language)
The idea we were asked to test: when a sentence has two possible objects ("she gave the man a book", "they called the
place a haven"), teach the reader to use the *sentence pattern* to pick which noun is the answer, instead of just
taking the nearest noun after the verb. We built it and measured it carefully — and it makes **no difference at all**
(zero, measured three different ways, on both old and modern text). The reason is simple and it's how the brain
actually works: for ordinary English, "the nearest noun after the verb" and "what the sentence pattern says" point at
the **same** word, so the fancier rule adds nothing. In fact our reader, when it's handed a clean list of candidate
nouns, is **already as accurate as a strong off-the-shelf parser** at this picking job (about 93%). The errors that
remain are not this kind of problem: about half are cases where the sentence needs to be properly *parsed* (things
like "what frightened people" or "were seen the landscapes"), and about half are genuinely unanswerable — including
"call X Y" sentences where even linguists disagree about which noun is "the thing acted on," so there's no right
answer to pick. Bottom line: the picking step is already as good as it's going to get; the remaining gains are in
better sentence-structure analysis and in the meaning system, both of which are already separate tasks on the board.
One correction to a prior write-up: the earlier "+15 points on two-object sentences" was measured against a buggy
stand-in, not the real reader, and vanishes against the real one.

### QUESTIONS
None blocking. One judgement call for strategy: this REFUTED result means the parent problem's NEXT-STEP #1 ("land the
construction-aware selector") should be **struck**, and its ideal-composition write-up carries a small correction
(`ideal_pick`'s animacy override is net-negative vs the deployed selector). I have written both as an AUDIT UPDATE
above rather than editing the parent's owner-DONE files (scope).

### NEXT STEPS (ranked by measured END-TO-END leverage; none is "add a cue to the selector")
The ideal composition (§7) is prototyped; the SELECTOR is done. The levers, largest-first:
1. **[BIGGEST, gated] Turn on the referent-per-NP SOURCE.** The deployed reader is 0.47/0.21 vs the selector's 0.93
   because of source loss; the parent's measured lift is **+0.336** end-to-end. GATED on the coref linker (the parent's
   filed `wire_the_referent_to_coref_linking_pass...`). This is where the who-did-what performance actually is.
2. **[NEW, buildable, small] Extend the referent-per-NP source to indefinite-pronoun / quantifier heads**
   (everybody/somebody/thee). Prototyped here: **+0.0105 CI-sep, twin loses** (§7). A tiny referent-per-NP extension
   (parent's source territory) — recommend landing with the source wire.
3. **[filed] Register-native POS tagging** — the parent's filed 1c; it is ~5-6 of the parse-recoverable residual (the
   tagger mis-tags 19c adjectives as NOUN, so the selector picks them). Confirmed on disk (§7).
4. **[filed] Filler-gap for pseudo-clefts** ("what frightened people") — the filed parser problem; ~2-3 clauses.
5. **A small-clause EXTRACTOR for object-complement/naming** ("call X Y" → emit BOTH args) rather than forcing a
   single ill-posed "patient" pick. This is the 12-clause ill-posed core of the 3.1% genuine residual — a fidelity
   refinement, not a signal-loss lever.
6. **The meaning-fit selector for genuine ambiguity** — GATED on the meaning channel (the filed learner-on successor);
   the competent reader also loses here, so part is shared hard gold.
