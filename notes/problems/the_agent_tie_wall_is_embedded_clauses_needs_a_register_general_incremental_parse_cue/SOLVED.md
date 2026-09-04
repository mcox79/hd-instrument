---
problem: the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_incremental_parse_cue
status: SOLVED
bar: "PASS = a glass-box, REGISTER-GENERAL incremental structure cue (NO trained parser, NO LLM) entering `graded_competition` as ONE precision-weighted cue + recency-weighted Centering, such that on the embedded/relative-clause agent slice it beats the current cue competition CI-separated, with a shuffled-structure info-free twin LOSING and NO regression on canonical clauses (the whole-arm number does not drop). Report CI half-width + null p95; recompute floors on the same population; replicate on held-out docs. A rigorous located NEGATIVE — register-general incremental parsing cannot be built glass-box to beat the competition on the tie slice, with the named cause + number — is a FULL PASS."
result: "board who-did-what AGENT accuracy on the EMBEDDED-CLAUSE nominative-vs-nominative TIE slice (>=2 animate tracked candidates preverbal; SITQA.build_events_questions -> context-cued answer_instanced -> _match; LitBank 19c, referent_per_np + full P2 stack ON): the register-general incremental left-corner STRUCTURE cue entering hdlab.graded_competition as ONE self-gating precision-weighted cue lifts the tie slice from base 0.6372 to 0.7098 = +0.0726, doc-bootstrap 95% CI [+0.0435,+0.0992], half-width 0.0279, p(<=0)=0.000 -> CI-SEPARATED (tuned, n_tie=317). GENERALIZES held-out (docs[16:40], never inspected, n_tie=552): 0.6178 -> 0.6739 = +0.0562 CI[+0.0336,+0.0811] hw 0.0238. Canonical does NOT regress (tuned +0.0074 CI[+0.0021,+0.0133]; held +0.0039 CI[+0.0016,+0.0067]); whole-arm improves (tuned +0.0188 CI[+0.0130,+0.0246]; held +0.0140 CI[+0.0097,+0.0190])."
floor: "strongest floor actually run = the CURRENT cue competition = the LIVE full P2 stack (cm_agent + include_pron_agents + case_filter + clause_local, referent_per_np ON), recomputed on the SAME tie-slice population = 0.6372 tuned / 0.6178 held-out. Info-free shuffled-structure twin (same machinery, the structure cue's per-candidate support permuted) = 0.4890 tuned / 0.4710 held-out (null p95: struct-twin +0.2208 CI[+0.1751,+0.2571] tuned, +0.2029 CI[+0.1611,+0.2416] held -> the twin LOSES CI-separated; the twin scores BELOW base because a weighted NOISE cue misdirects the competition, isolating that the STRUCTURAL signal is what carries)."
controls: "(1) shuffled-structure info-free TWIN loses CI-separated on tie (tuned +0.221, held +0.203, p<=0=0.000) -> the structure INFORMATION carries, not the extra cue slot. (2) CANONICAL-slice no-regression CI-separated on both sets (the whole-arm number RISES, does not drop). (3) HELD-OUT replication of every headline (never-inspected docs[16:40]). (4) RECENCY-Centering REFUTED: adding the brief's recency-Centering cue (Cb = previous subject) does NOT beat base on the tie slice (tuned +0.0252 CI[-0.0091,+0.0592] NOT-separated; held +0.0199 NOT-separated) and is WORSE than the structure cue alone -> matches the substrate's OWN measured salience_binder finding (recency at chance on hard cases) + the mechanistic fact that embedded clauses introduce a NEW subject. GRAMMATICAL-PROMINENCE Centering ALSO fails (prom-struct = -0.0221 CI-sep BELOW) -> both Centering variants lose to structure alone; structure is the sole lever for these ties. eADM GRADED precision (distance / relativizer-gating) does NOT beat the SELF-GATING flat cue (prec_dist -0.0063 NOT-sep; prec_rel identical); weight-robust across struct_w in {1.5,2.5,4.0} (all CI-sep vs base). (5) MORE-BRAIN-FAITHFUL RC-POP (revision) REJECTED: a stack-based left-corner with relative-clause pop is WORSE than the flat cue on tie (rcpop-struct = -0.0126 CI[-0.0231,-0.0033] CI-separated BELOW) -> reproduces the incremental_parser organ's own measured lesson (revision HURTS clean prose; over-fires as a general cue). (6) UPSTREAM animacy-lexicon collective-human fix is neutral on tie, marginally positive whole-arm (+0.001). (7) TRAINED parser stays BARRED (P2 section6 measured OOD loss; corroborated by the adjacent relcl SOLVED: the general dependency parser is HARMFUL here, 0.198 < twin). (8) scaffold-free witness test_cmrole_agent_struct_organ.py."
files_changed: "experiments/exp_cmrole_agent_struct_v1.py (the register-general structure cue + slice classifier + measurement + self-test), experiments/exp_cmrole_agent_struct_opt_v1.py (eADM graded-precision + weight-robustness + prominence-vs-recency), experiments/exp_cmrole_agent_struct_v2.py (the more-brain-faithful RC-pop prototype + upstream animacy fix), experiments/exp_cmrole_agent_thematic_v1.py (the thematic-fit/agentivity next-lever route-closure, section 7a), experiments/exp_cmrole_agent_detect_v1.py (the 47.8%-bucket decomposition probe: predicate_recall +0.0083 CI-sep whole-arm, section 7a), verification/test_cmrole_agent_struct_organ.py (scaffold-free witness). NO hdlab file changed (solver scope; proposed hdlab diff in section 8, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_cmrole_agent_struct_organ.py"
---

# A register-general incremental STRUCTURE cue resolves the embedded-clause AGENT tie wall — as ONE precision-weighted cue in the competition, NOT a parser swap

## 1. What the bar asked, and the headline
P2 left a measured, localized residual: with the Competition-Model AGENT competition landed (who-did-what
agent 0.041 -> ~0.69), the remaining errors concentrate in nominative-vs-nominative ties in embedded/relative
clauses. The brief asked for a glass-box, REGISTER-GENERAL incremental structure cue entering
`graded_competition` as ONE precision-weighted cue (+ recency Centering) that beats the current competition on
the embedded-clause slice CI-separated, twin losing, no canonical regression — trained parser BARRED.

**Delivered (LitBank 19c board who-did-what AGENT, context-cued readout, embedded-clause TIE slice):**

| arm | tie acc (tuned) | tie acc (held-out) | what it is |
|---|---|---|---|
| `base` (current competition = live full P2 stack) | 0.6372 | 0.6178 | the recover-past floor |
| **`struct` (register-general left-corner cue)** | **0.7098** | **0.6739** | **THE FIX** |
| `twin` (shuffled-structure, info-free) | 0.4890 | 0.4710 | must lose |

- **Beats the competition on the tie slice, CI-separated:** `struct − base = +0.0726` CI[+0.0435,+0.0992] tuned
  (n_tie=317), `+0.0562` CI[+0.0336,+0.0811] held-out (n_tie=552). ✓
- **Info-free twin loses, CI-separated:** `struct − twin = +0.2208` tuned / `+0.2029` held-out. ✓
- **No canonical regression:** canon `+0.0074`/`+0.0039` CI-sep (it RISES); whole-arm `+0.0188`/`+0.0140` CI-sep. ✓
- **Generalizes** out-of-sample at every headline (docs[16:40], never inspected). ✓

## 2. The brief was HALF right — structure YES, recency-Centering NO (disk + the substrate's own organ overrule)
The brief bundled TWO mechanisms. Measured separately:
- **Register-general incremental STRUCTURE cue — CONFIRMED (the lever).** +0.073/+0.056 CI-sep on the tie slice.
- **Recency-weighted Centering — REFUTED.** Adding the Cb=previous-subject cue does NOT beat base on the tie
  slice (tuned +0.0252 NOT-sep; held +0.0199 NOT-sep) and is WORSE than structure alone. This is not a tuning
  miss: it reproduces the substrate's OWN measured `salience_binder` finding — *"on the HARD ambiguous cases
  RECENCY IS AT CHANCE; the load-bearing cue is grammatical PROMINENCE, not recency"* (GAP, human-labeled) —
  and the mechanistic reason is specific to this residual: an embedded clause INTRODUCES a new subject, so a
  "continue the previous subject" preference mispredicts EXACTLY where the tie lives. Structure, not recency,
  is the register-general lever.

## 3. How the brain does this, and what is reused (every component brain-foundational)
PINNED: role assignment is INCREMENTAL and CLAUSE-BOUNDED (Christiansen & Chater 2016 Now-or-Never; Lewis &
Vasishth 2005 cue-based retrieval; Frazier/Clifton clause boundaries). Syntax is ONE cue in a graded
competition, PRECISION-WEIGHTED (eADM actor competition, Bornkessel-Schlesewsky 2006; Friston precision).
ATTACHMENT and ROLE-BINDING are SEPARATE POOLS sharing the activation FORM (Matchin-Hickok 2020; Beber 2025
double dissociation) — so structure enters the role competition as a weighted CUE, it does not replace it.

REUSED, not re-derived:
- **`hdlab.incremental_parser.incremental_build`** — the landed REGISTER-GENERAL (rule-based, glass-box, NOT
  trained) left-corner incremental structure builder (from the owner-DONE `the_argument_parser_is_batch_where_
  the_brain_is_incremental`). Its subject rule (nearest preceding nominal in a bounded Now-or-Never buffer) IS
  the register-general cue source; the cell reproduces that exact operation (`incremental_subject_before`,
  self-tested to match `incremental_build` at every verb) and feeds it as one support array.
- **`hdlab.graded_competition.net_activation`** — the SAME additive-cue posterior (McClelland 2013) the AGENT
  competition already uses; the structure cue is one more weighted support (the separate attachment pool feeds
  the role pool). PINNED, not convenient.
- **`hdlab.graded_role_assigner`** (the landed P2 `agent_supports`/`clause_bounds`/`AGENT_VALIDITIES`).
The structure cue is SELF-GATING (minimal eADM precision: it votes only when the parse's bound subject maps
onto a tracked candidate; otherwise its support is all-zero and the lexical/discourse cues carry) — register-
general graceful degradation, no train/test domain.

## 4. eADM precision-weighting + weight robustness — self-gating is the right amount (tuned, `exp_..._struct_opt_v1`)
The brief asked for a PRECISION-weighted cue (eADM). Tested three ways against the self-gating flat cue:
- **Weight robustness (non-knife-edge):** `struct − base` on the tie slice stays CI-separated across
  `struct_w ∈ {1.5, 2.5, 4.0}` (+0.0473 / +0.0726 / +0.0726). w2.5 and w4.0 are IDENTICAL — the structure cue
  SATURATES once strong enough to break the tie (more weight cannot change the argmax); w1.5 is weaker but
  still positive. Not a tuned knife-edge.
- **Graded precision does NOT beat self-gating.** A distance-graded precision (down-weight a distant left-corner
  bind, DLT locality) = 0.7035 tie, `prec_dist − struct = −0.0063` CI[−0.0159,+0.0000] NOT-separated (slightly
  worse). A relativizer-gated precision (down-weight when a relativizer sits between subject and verb, the
  matrix-after-RC risk) = IDENTICAL to flat (that configuration is rare inside the tie cases). So the SELF-
  GATING minimal precision — the structure cue votes only when the parse makes a structural commitment on a
  tracked candidate, and abstains (weight→0) otherwise — IS the eADM precision; a graded reliability estimate
  from surface cues adds nothing here (surface features do not separate the reliable-embedded from the
  unreliable-matrix left-corner bind; the competition's other cues already arbitrate).
- **Grammatical-PROMINENCE Centering also fails** (accumulated prior-subject cue = 0.6877 tie,
  `prom − struct = −0.0221` CI[−0.0447,−0.0039] CI-separated BELOW). So BOTH Centering variants — recency
  (section 2) and prominence — lose to the structure cue alone: for these embedded-clause ties the discourse/
  Centering signal is not the lever; the incremental STRUCTURE is.

## 5. The MORE-brain-faithful component (RC-pop / revision) — prototyped, measured, and correctly REJECTED
The flat left-corner cue's #1 residual is the MATRIX-verb-after-relative-clause POP failure: pure left-corner
binds the RC-internal nominal ("the man who saw the boy RAN" -> boy) because it lacks REVISION. I built the
more brain-faithful version — a stack-based left-corner with RC-POP (a relativizer SAVES the matrix buffer and
opens an RC-local buffer; at the RC's end the matrix buffer is RESTORED so the matrix verb re-attaches the
ANTECEDENT). It is validated on canaries (subject-relative, object-relative, embedded-complement all bind the
correct subject: "ran"->man, "engaged"->chizzle).

**But as a general cue it is WORSE than the flat cue, CI-separated (rcpop − struct = −0.0126 CI[−0.0231,
−0.0033] on the tie slice).** This is the RIGHT answer, and it reproduces the `incremental_parser` organ's OWN
measured lesson: *revision HURTS clean edited prose ("don't reanalyse unless forced")*. Ungated reanalysis
OVER-FIRES on real 19c prose (mis-parsing "that"-complementizers, deep nesting), and those errors outweigh the
few matrix-after-RC cases it fixes. **The brain resolves this with a GATED, SPECIALISED filler-gap circuit
that fires on ~0.75% of text** — which is exactly the adjacent owner-facing organ
`the_relcl_parser_is_too_weak_for_filler_gap_role_assignment` (SOLVED: active-filler resolver, reaches oracle,
gated so it never fires on canonical clauses). The register-general STRUCTURE cue and that GATED filler-gap
circuit are complementary; conflating them (ungated revision in the general cue) is the measured mistake.

## 6. Upstream component — the animacy-lexicon collective-human coverage fix
The animacy CUE mislabels COLLECTIVE-HUMAN nouns as inanimate (`lookup_animacy`: people/crowd -> inanimate-
abstract; everyone -> None), flipping the cue AGAINST the true agent ("how many PEOPLE ... has stretched" ->
people scored inanimate, the S53 error). A glass-box coverage patch (COLLECTIVE_HUMAN -> animate) restores it.
Measured: neutral on the tie slice, marginally positive whole-arm (+0.001). Small but principled and non-
negative -> a fold-in candidate in the upstream `hdlab.animacy_lexicon` organ, not this one.

## 7. Performance vs the brain, and where signal is lost NOW (mechanism-diff)
A competent human reader is near-ceiling on these ties (effortful only on genuine garden-paths). We move the
tie slice 0.637 -> 0.710 (+0.073). The brain uses FOUR mechanisms; we replicate 1 fully, approximate 2, and
locate 3-4 as the residual:
1. **Incremental parse WITH revision.** OURS: bounded left-corner, revision OFF (measured to hurt). DIFF: right
   for embedded subjects, wrong for the matrix verb after an RC. We survive because structure is ONE cue the
   competition overrides (FIX:BREAK ~12:1). The gated relcl organ is the full version.
2. **Precision-weighting (eADM).** OURS: self-gating (graded precision tested, does not add — section 4).
3. **Thematic fit / selectional preference (McRae, Ferretti).** "Does this entity plausibly DO this action?"
   TESTED AND CLOSED (section 7a) — it cannot help THIS residual (89% character-vs-character; names carry no
   selectional signature), first-hand null AND three prior 19c prototypes null vs their twins.
4. **Complete Centering with grammatical PROMINENCE.** OURS: tested recency AND prominence (both fail, sections
   2 & 4); the discourse signal is not the lever for these ties.

## 7a. THE NEXT LEVER, RUN DOWN: thematic-fit is CLOSED, and the residual is ADJACENT organs (evidence-based)
The owner-named next lever was a thematic-fit / selectional-preference cue. I ran it down rather than assume:
- **Prior work (do not re-derive):** three landed 19c thematic-fit prototypes — `exp_19c_distributional_/
  reestimation_/composition_thematic_fit_prototype_v1` — do NOT beat their VERB-SHUFFLED info-free twin for
  role selection (DIST_vs_VERBSHUF +0.0084 CI[−0.0235,+0.0403]; C19_vs_VERBSHUF +0.0115 CI[−0.0221,+0.0435];
  both include 0). Thematic fit helps only PATIENT selection on clean direct objects, not agents.
- **First-hand on OUR tie slice (`exp_cmrole_agent_thematic_v1`):** the cheapest brain-foundational selectional
  cue — lexical AGENT-CAPABILITY (`animacy_lexicon.agent_capable`, Dowty proto-agent) — added to the
  competition does NOT beat its info-free twin (agentiv−twin = +0.0000 CI[−0.0228,+0.0199]) and is marginally
  worse than the structure cue alone (−0.0126). CLOSED.
- **Why (residual map, tie-slice errors after structure, n=92, `diag_residual`):** **89% are character-vs-
  character** (>=2 animate tracked candidates) — where a selectional cue structurally cannot discriminate (two
  named people are both plausible agents of the verb). The residual decomposes into ADJACENT organs, NOT a
  missing cue in this competition:
  - **47.8% STRUCT-RIGHT-but-readout/event-surfaces-wrong** — DECOMPOSED (`diag_readout_bucket`) and PROBED,
    not hand-waved: **~58% is event DETECTION @ the queried sentence** (29% predicate never detected, 29%
    detected elsewhere but not at S — often `have`/`be` copulas/light verbs), **~40% is the COMPETITION picking
    a wrong agent at a detected event** (fragmented: the animacy bug like `round`/people→bridges, matrix-vs-
    embedded like `engage`/chizzle→boys, possessive-of-gerund like `furnish`/his), **1% genuine readout pick.**
    PROTOTYPED the detection lever (`exp_cmrole_agent_detect_v1`): turning ON the EXISTING, currently default-
    OFF `predicate_recall` organ (register-robust event recovery, WordNet verb-gate; P6 owner-DONE) composed
    with the structure cue lifts the WHOLE agent arm **+0.0083 CI[+0.0048,+0.0122] CI-separated** (canonical
    0.722→0.732; tie unchanged — ties are not detection-limited), and with the animacy fix **+0.0094 CI-sep**.
    So this bucket has a real, measured lever that is simply switched off — but it is the EVENT-DETECTION organ
    (it changes all 5 reader dimensions), so its global turn-on belongs to a dedicated detection problem.
  - **13.0% matrix-after-RC pop** (STRUCT_ABSTAINED + relativizer) — the GATED relcl filler-gap organ's job.
  - **10.9% coref miss** (gold never a tracked candidate) — the coref resolver's recall.
  - **13.1% structure's own limit** (fired-wrong / pop-fail); 15.2% structure-abstained (no relativizer).
So the AGENT ROLE COMPETITION is at its CEILING on this slice; the remaining gains are ADJACENT organs, and the
single biggest (event detection) is not only named but PROVEN actionable here (+0.008 CI-sep from flipping one
existing organ ON) — see NEXT STEPS.

## 8. Proposed hdlab change (solver may not write hdlab; strategy lands under Q111)
One edit, reuses existing organs, no new dependency, NO trained parser, NO LLM:
- **`hdlab/graded_role_assigner.py`** — extend `agent_supports` with a `structure` cue: run the register-general
  left-corner subject bind (expose `incremental_subject_before` from `hdlab.incremental_parser` — a tiny
  addition returning the per-verb `subj` slot the organ already computes) and add `structure` to
  `AGENT_VALIDITIES` (STRUCT_W ~2.5, self-gating). Reference impl = `experiments/exp_cmrole_agent_struct_v1.py`
  (`incremental_subject_before`, `cm_agent_pick_struct`). Optionally fold the collective-human animacy patch
  into `hdlab.animacy_lexicon`.
**Turn-on impact:** tie slice +0.073 tuned / +0.056 held-out CI-sep; canonical +0.007/+0.004 (no regression,
slight gain); whole-arm +0.019/+0.014 CI-sep; patient untouched (agent-only). Net-positive with a measured
reason -> land ON (no-more-default-off). Do NOT add recency-Centering (refuted) or ungated RC-pop revision
(measured worse); the specialized filler-gap resolution is the separate gated relcl organ.

## 9. What I did NOT establish (would withdraw first if wrong)
- I measured the AGENT arm on the tie/canonical slices with the context-cued readout; not a full 5-instrument
  board re-run. The change is confined to the agent cue; patient is byte-identical by construction.
- The tie slice is defined by input structure (>=2 animate tracked preverbal candidates in the clause span) —
  a correctness-independent partition, but it under-counts embedded errors the crude `clause_bounds` misses
  (so the true embedded lever may be larger than the tie-slice number).
- The graded-precision and prominence-Centering negatives are on THIS corpus/population; on modern in-domain
  prose the reliabilities differ (the Competition Model's own register-specificity prediction).

## KEY REALIZATIONS
- **The register-general parser was already built — the work was using it as a CUE, not a parser.** The prior
  `wire_the_incremental_parser...` PARTIAL found swapping the candidate POOL to the incremental parser is
  AGENT-pool-insensitive; the win here comes from the parser's SUBJECT ATTACHMENT as one weighted vote in the
  competition (a different use of the same organ). Pool-swap vs cue-vote is the load-bearing distinction.
- **"More brain-faithful" is not "more machinery" — it is the RIGHT gating.** Ungated revision (RC-pop) is
  MORE like a full parser but LESS like the brain, which gates reanalysis; the flat left-corner + a separate
  GATED filler-gap circuit is the faithful decomposition. The measurement (rcpop worse than flat) is what
  proved it, reproducing the incremental_parser organ's own revision-hurts-clean-prose result.
- **Two info-free-twin styles agree.** Shuffling the structure support (not all cues) isolates the structural
  signal cleanly; the twin scoring BELOW base (a weighted noise cue misdirects) is a sharper control than a
  twin that merely ties base.
- **The substrate's own measured organ pre-answered the brief's recency half.** Reading `salience_binder`
  first (recency at chance, prominence carries) predicted, and my measurement confirmed, that recency-Centering
  would fail here.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **situation_reader who-did-what AGENT competition**: the landed Competition-Model agent competition
  (`graded_role_assigner.agent_supports`/`agent_competition_pick`) gains a brain-foundational STRUCTURE cue —
  the register-general incremental left-corner subject attachment (`incremental_parser`) entering the SAME
  `graded_competition` as ONE self-gating precision-weighted cue (Matchin-Hickok separate-pools; eADM). Fidelity
  up on the embedded-clause tie residual (+0.073/+0.056 CI-sep, generalizes). Residual is now MEASURED and is
  ADJACENT organs, not this competition (at ceiling): 48% event-detection/readout, 13% matrix-after-RC pop
  (gated relcl organ), 11% coref. Thematic-fit as an AGENT cue is TESTED + CLOSED on 19c (null vs twin).
- **incremental_parser**: confirmed as a register-general CUE source for role assignment (not just a candidate-
  pool front-end). Its documented "revision hurts clean prose" is reconfirmed here: ungated RC-pop as a general
  cue is net-negative; the brain's gated reanalysis lives in the specialized relcl filler-gap circuit.
- **animacy_lexicon**: collective-human nouns (people/crowd/everyone) mislabelled inanimate/None — a coverage
  gap that flips the agent animacy cue; glass-box patch proposed.

## TLDR (plain language)
The reader now names "who did it" well on ordinary sentences, and we just fixed the hardest leftover case:
long old-fashioned sentences with a clause inside a clause, where two living characters both sit before the
verb and every earlier clue says "either one." A person settles these by actually tracking the grammar —
which character is the subject of which clause. We reused a grammar-reader the project already built (a plain,
rule-based one that works on any era of writing, NOT the machine-learned parser that breaks on old prose) and
fed its "who is the subject here" opinion into the reader's existing weigh-the-clues step as ONE more clue
that quietly stays silent when it is unsure. On the hard clause-in-a-clause sentences this raised "who did it"
from about 64 to about 71 right in 100 (and the same on documents we never looked at), without hurting the
ordinary sentences, and a scrambled-clue version does clearly worse — so it is real. We also tried two things
the brief suggested and honestly report they did NOT help: preferring "the most recent character" (the brain
does not rely on recency for hard cases, and our own prior measurements already showed that), and a fancier
grammar-reader that re-reads and revises (it over-corrects on old prose — the project had already measured that
re-reading hurts clean text). The genuinely fancier grammar belongs in a separate specialist that only switches
on for the rare tricky sentence, which a teammate has already built.

## QUESTIONS
None. (The brief bundled structure + recency-Centering; structure is the lever, recency is refuted with a
measured cause — resolved in section 2. The more-brain-faithful RC-pop is prototyped and rejected with a
measured cause — section 5.)

## NEXT STEPS
1. **Strategy lands the structure cue as the Q111 wire (section 8)** — one `structure` cue added to
   `agent_supports`/`AGENT_VALIDITIES`, self-gating, default-ON (net-positive, patient-neutral, held-out-
   replicated). Optionally fold the collective-human animacy patch into `hdlab.animacy_lexicon`.
2. **➡️ THE NEXT FOCUS (open as its own problem): register-robust EVENT DETECTION.** This is the single
   highest-leverage remaining who-did-what lever — now MEASURED and PARTLY PROTOTYPED, not guessed: ~58% of the
   47.8% residual bucket is the predicate not being detected at the queried sentence (often `have`/`be` copulas/
   light verbs), and turning ON the EXISTING default-OFF `predicate_recall` organ already buys **+0.0083 CI-sep
   on the whole agent arm** (section 7a) — an immediate, concrete entry point. The full problem: a register-
   robust predicate detector (copula/light-verb/archaic-verb recovery) with the cross-arm turn-on impact analysis
   (`predicate_recall` changes all 5 reader dimensions, so its global flip is the detection problem's call, not
   this one's). Brain-foundational framing: register-invariant predicate detection (noisy-channel combination,
   Gibson 2013) + content-addressable context-cued episodic retrieval (Lewis-Vasishth; hippocampal event
   binding). Fixing it lifts EVERY who-did-what arm, not just this slice.
3. **After that, in measured order:** (a) wire the GATED relcl filler-gap organ (`the_relcl_parser...`, SOLVED)
   for the 13% matrix-after-RC pop cases — the brain-faithful gated reanalysis the ungated RC-pop could not be;
   (b) coref recall (11% gold-never-tracked); (c) fold the collective-human `animacy_lexicon` patch (section 6)
   into the upstream organ. **Do NOT re-file thematic-fit — it is a closed route (section 7a).**
