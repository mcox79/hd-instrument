---
problem: role_assignment_is_untested_on_archaic_literary_prose
status: SOLVED
bar: "PASSES only with ALL of: 1. Measured parser role accuracy on archaic prose against a real role gold, WITH a modern-prose reference arm (isolates register from sentence-length difficulty), recomputed on matched populations. Report the degradation (if any) CI-separated with half-width + null p95. 2. The downstream cost quantified: how much the parse error propagates into a role cue the organs consume (e.g. the coref subjecthood cue accuracy with GOLD roles vs spaCy roles on the same items) -- a POSITIVE control that the downstream metric CAN move. 3. EITHER a register-robust cue-based role assignment that recovers the degradation CI-separated over the spaCy-role floor with an info-free twin (shuffled cues) LOSING -- OR a rigorous NULL (spaCy roles are CI-equal to gold on this corpus -> the parse is NOT the bottleneck, the confound is RETIRED and the organ-level conclusions stand). 4. One-screen summary: parse accuracy (archaic vs modern) -> downstream cost -> fix-or-null -> verdict. A rigorous NEGATIVE is a FULL PASS."
result: "spaCy subject-identification accuracy is NOT wholesale-degraded on archaic prose: natural archaic literary prose (hand gold, blind, n=52 LitBank sentences) 0.9423 [0.8654,1.0] >= natural modern textbook prose (same standard, n=55) 0.8909 [0.80,0.9636]; large unbiased UD-EWT modern anchor (n=1527) 0.905 [0.891,0.919], FLAT across length to 40+ tokens. The degradation is CONSTRUCTION-SPECIFIC (subject-verb inversion + archaic morphology), isolated by content+length-matched minimal pairs (n=23): archaic 0.739 vs modernized 0.957, paired +0.217 [0.087,0.391] (excludes 0); on real LitBank dialogue-tag inversion (n=30) spaCy 0.467. Corpus incidence: 70% of subjects are pronouns spaCy gets right; inversion ~4-12/1000 finite verbs @ ~60% spaCy error; archaic morphology 0.77% of sentences."
floor: "spaCy-roles floor, recomputed per population: (Phase C fix) spaCy raw subject-ID on real LitBank dialogue inversion 0.4667 -- cue-repair 0.8333 [0.70,0.9667] is CI-separated ABOVE it (+0.367). (Phase B downstream) incumbent coref strict-Cb pick with spaCy roles 0.6129 [0.6029,0.6227] on 9139 competitive LitBank instances. (Phase A) modern reference arms above."
controls: "(1) INFO-FREE TWIN (random nominal, all cue selection destroyed) -> 0.2333 on inversion, LOSES CI-separated to cue-repair 0.8333 (excludes 'any reattachment helps'; the CASE+FRAME cue geometry carries it). (2) DOWNSTREAM POSITIVE CONTROL: shuffling the cache roles drops coref strict-Cb 0.6129->0.5277, and a sensitivity sweep degrades it monotonically with simulated subject-error rate (0%=0.612, 10%=0.605, 20%=0.594, 50%=0.560) -> the metric CAN move, so the ~0 actual delta is a real NULL not a dead metric. (3) PERMUTATION NULL on the natural archaic-vs-modern gap: p95=0.0983 > |gap 0.051| -> not separable (wholesale null). (4) PROVENANCE control: 19 nominative-pronoun-labeled-OBJECT + 10 reporting-inversion errors exist in the coref cache -- a human never labels 'he' an object, PROVING the roles are parser-derived. (5) REGISTER-INVARIANCE: the SAME cue weights give archaic 0.913 ~= modern 0.957 (gap 0.043) -> the fix is not tuned to one register. (6) NO CANONICAL REGRESSION: the repair leaves canonical sentences unchanged and even lifts modern textbook prose 0.764->0.855."
files_changed: "experiments/exp_role_parse_accuracy_probe_v1.py, experiments/exp_role_confound_incidence_litbank_v1.py, experiments/exp_role_confound_downstream_coref_v1.py, experiments/exp_role_cue_repair_inversion_v1.py, experiments/exp_role_cue_first_subject_v1.py (cue-first-vs-post-hoc + incremental_parser adjacent eval), verification/test_role_parse_accuracy_archaic.py, notes/problems/role_assignment_is_untested_on_archaic_literary_prose/{archaic_subject_gold_v1.jsonl, modern_subject_gold_v1.jsonl, register_minimal_pairs_v1.jsonl, build_role_gold.py, build_minpairs.py, sample_role_sentences.py, SOLVED.md}. No hdlab/ write (Q111); proposed hdlab diff below."
reverify: ".venv/Scripts/python.exe verification/test_role_parse_accuracy_archaic.py   # 16/16 PASS"
---

# What was asked, and the one-screen answer

The brief flagged a SUSPECTED-UNMEASURED confound (from the coref integration, adjacency 6): every organ that
reads a grammatical role gets it from a spaCy dependency parse of 100-200-year-old literary prose, and spaCy is
trained on modern text, so "the `nsubj`/`dobj` labels the whole stack trusts may be systematically DEGRADED on
archaic long-sentence prose." I measured it end-to-end. **The wholesale suspicion is not supported; the real
effect is narrow, bounded, and I built the brain-faithful fix for it.**

| step | finding |
|---|---|
| **parse accuracy, archaic vs modern** | spaCy's subject-ID is **NOT degraded on archaic prose**: natural LitBank 0.94 >= modern textbook 0.89, and FLAT to 40+ token sentences (the "long archaic sentence" fear is unfounded -- 70% of literary subjects are pronouns, which spaCy nails). The register gap is NOT CI-separable (permutation null p95 0.098 > gap 0.051). |
| **where it DOES fail (register isolated)** | content+length-matched minimal pairs isolate a real, CI-separated effect on **subject-verb INVERSION** ("replied he", "cried the old man", "so was the thing seated", "quoth") and **archaic morphology** ("thou knowest"): archaic 0.74 vs modernized 0.96, +0.22 [0.087,0.391]. On real dialogue-tag inversion spaCy is only 0.47 (it tags "he" as a **direct object**). |
| **how often it matters (incidence)** | inversion is ~4-12 per 1000 finite verbs, concentrated in DIALOGUE tags; archaic morphology is 0.77% of LitBank sentences (a non-issue for 19c prose; would matter for Shakespeare/KJV). |
| **downstream cost** | the coref cache's roles ARE spaCy-derived (proven: 19 nominative-pronoun-OBJECT labels a human would never write). Correcting **all 59** spaCy role errors moves coref strict-Cb accuracy by **-0.0009** (CI includes 0). A shuffle positive control DOES move it (0.613->0.528) and a sensitivity sweep shows you need a ~10-20% subject-error rate before coref degrades -- spaCy's actual ~0.6% archaic error is far below that. **The confound is real but IMMATERIAL to aggregate coref.** |
| **fix or null** | BOTH. The wholesale confound is a rigorous NULL (retired). For the bounded inversion locus I built the **brain-faithful cue-repair** (case + quote-aware verb-frame > position): real dialogue inversion **0.47 -> 0.83 CI-separated over the spaCy floor, info-free twin 0.23 LOSES, register-invariant (archaic 0.91 ~= modern 0.96), no canonical regression.** |

**VERDICT: the corpus-age parse suspicion is RETIRED for the aggregate (spaCy roles are good enough on this
corpus that the organ-level conclusions stand), with one characterized bounded exception -- dialogue-tag
inversion -- for which a brain-faithful glass-box fix is demonstrated and ready to wire.**

# THE DISK OUTRANKS THE BRIEF (what disagreed)

The brief's premise -- "systematically DEGRADED on archaic long-sentence prose" -- is **substantially refuted**.
Three disk facts contradict the wholesale framing:
1. **Archaic literary prose is NOT harder for spaCy than modern prose.** If anything, modern technical textbook
   noun-phrases (long coordinate/embedded subjects, "Nicotinamide adenine dinucleotide (NAD)") are harder: modern
   textbook strict subject-attachment is 0.76 vs archaic 0.94. Length is not the driver either (spaCy is flat to
   40+ tokens on both registers).
2. **The degradation is a handful of CONSTRUCTIONS, not a register.** Inversion + archaic morphology, isolated by
   minimal pairs. Everything else (canonical SVO, long full-NP subjects, fronted adjuncts) spaCy handles.
3. **The downstream cost is ~0.** The organs the brief worried about (coref subjecthood cue, incumbent Centering
   tier) are barely affected, because the errors are few and 70% of subjects are pronouns.

So the honest headline is not "the parse caps the organs" but "the parse is fine except on inversion, and that
exception is immaterial in aggregate but concentrated on dialogue-speaker tracking." Refuting the brief is the
halfway point: I then solved the REAL question underneath -- *where exactly, how much, and what is the brain's fix*.

# HOW THE BRAIN DOES THIS (PINNED) and why the fix is faithful, not a hack

A skilled human reads "said he" correctly with no effort. It does NOT decide who-did-what from word order; it
weighs several cues at once and lets a strong one beat position. This is PINNED (research drill this session,
citations in the note below):
- **Competition Model** (Bates & MacWhinney; MacWhinney, Bates & Kliegl 1984) and its neurocognitive sibling the
  **eADM** (Bornkessel-Schlesewsky & Schlesewsky 2006): role assignment is graded, parallel CUE COMPETITION over
  case, agreement, animacy, verb-subcategorization and position, weighted by learned validity, and **morphology
  can OVERRIDE position on marked constructions**.
- **Morphological CASE** ("he" is unambiguously nominative; "*said him" is ungrammatical) is a high-validity cue
  (principle PINNED; the English-pronoun-inversion instance is principle-pinned / instance-under-test -- so my
  cell is a fair TEST of that extension, per the research caveat).
- **Verb-frame** (reporting/quotative verbs subcategorize an animate speaker-subject; Altmann & Kamide 1999).
- **Neural dissociation** of role-assignment (pMTG/angular) from structure-building (IFG) LICENSES building the
  fix as a **separate glass-box stage** over the parser rather than retraining it.
- **Register-invariance** is a PREDICTION of the mechanism (its cues are lexical/morphological, not surface-
  distributional) -- and I MEASURED it (same weights, archaic ~= modern). A modern-trained statistical parser
  weights surface co-occurrence, so archaic inversions rare in its training degrade -- exactly the ~60% failure.

The fix copies the OPERATION (parallel cues, case/frame override position) and SWEEPS the parameters (the cue
selection is deterministic glass-box here; weights are the OUR-INVENTION dial). No external model at inference.

# What I built (all in experiments/, no hdlab write)

1. **`exp_role_parse_accuracy_probe_v1.py`** -- spaCy subject-ID accuracy vs gold, char-span aligned, LENIENT
   (does spaCy tag the gold subject as a subject at all -- what the coref cue consumes) + STRICT (right verb).
   Arms: UD-EWT modern anchor (unbiased, n=1527), hand-annotated archaic + modern (same blind standard),
   register-controlled minimal pairs. Length-stratified.
2. **`exp_role_confound_incidence_litbank_v1.py`** -- corpus incidence of the vulnerable constructions +
   spaCy's real in-situ error rate (definitional gold: a nominative pronoun after a reporting verb IS the subject).
3. **`exp_role_confound_downstream_coref_v1.py`** -- downstream cost on the real coref resolver (reuses its own
   `build_instances`/`_supports`): spaCy vs case-corrected roles, + shuffle positive control + sensitivity sweep.
4. **`exp_role_cue_repair_inversion_v1.py`** -- the brain-faithful cue-repair (case + quote-aware verb-frame >
   position) as a separate glass-box stage; scored raw vs cue-repair vs info-free twin on real inversions + pairs.
5. **`verification/test_role_parse_accuracy_archaic.py`** -- 16/16 scaffold-free witness.
6. **Gold** (blind, self-contained, in the problem folder): `archaic_subject_gold_v1.jsonl` (52),
   `modern_subject_gold_v1.jsonl` (55), `register_minimal_pairs_v1.jsonl` (23); builders kept for provenance.

# What I did NOT establish / would withdraw first

- **The minimal-pair and real-inversion n are modest (23, 30).** The effect is large and CI-separated, but a
  larger inversion gold would tighten it. **If one number falls first, it is the exact +0.217 minimal-pair
  magnitude** (n=23); the DIRECTION (inversion degrades spaCy, cue-repair recovers it) is robust across the
  independent real-LitBank arm and the witness.
- **The archaic hand gold is dialogue/pronoun-heavy** (representative of LitBank, but I did not oversample rare
  full-NP long-subject archaic sentences beyond the length strata). The 40+ token archaic bin (n=14) is 0.93, so
  the "long archaic full-NP subject" case is covered, but thinly.
- **The cue-repair does NOT recover collapsed-parse inversions** (locative inversion "so was X seated", object-
  fronting) or archaic morphology ("thou knowest") -- a POST-HOC repair cannot fix a parse spaCy fully garbled.
  **I TESTED my first instinct (that a cue-FIRST picker, replacing spaCy's parse with POS+cues, would recover
  these) and REFUTED it** (`exp_role_cue_first_subject_v1.py`): a pure cue-first picker is WORSE than post-hoc
  repair on almost everything (minpair 0.52 vs 0.91; modern 0.53 vs 0.85) because it discards spaCy's CORRECT
  parse on the ~90% of canonical cases spaCy handles, and its position-default still fails full-NP inversion.
  **The right architecture is therefore NOT cue-first-REPLACEMENT but POSITION-DOMINANT + cue-OVERRIDE** -- keep
  the parser's subject where it found one, override only on marked constructions where a high-validity cue (case,
  frame) fires. This is EXACTLY the Competition Model (position has high validity in English, overridden by
  morphology only on marked constructions) and `graded_role_assigner`'s own design -- so the post-hoc repair and
  the graded assigner are the faithful shape, and a naive cue-first parser is not. The residual full-NP
  locative/subjunctive inversion ("So was the thing seated", "Were the danger known") needs an AGREEMENT +
  OBLIQUENESS cue neither arm implements (low incidence; drilled below).
- **The downstream null is on the coref cache population (100 LitBank docs).** A dialogue-dense corpus would carry
  more inversion, so "immaterial" is scoped to this corpus's dialogue density.

## KEY REALIZATIONS (the moves that unstuck it)

- **The error IS the evidence.** I stopped trying to find the cache-builder to prove the roles were spaCy-derived
  and instead counted *nominative pronouns labeled OBJECT* -- a label a human annotator can never produce. Their
  existence proves provenance AND is the exact thing the CASE cue fixes. One count did two jobs.
- **Minimal pairs, not a bigger sample, isolated the effect.** The natural archaic-vs-modern comparison is a NULL
  and would have read as "no confound." Holding content and length constant and varying ONLY register surfaced the
  +0.22 construction-specific effect the aggregate hides -- because the vulnerable constructions are rare.
- **A subject-CENTRIC metric matched the organ.** The coref cue asks "did this entity hold a subject role", so I
  scored "is the gold subject tagged nsubj at all" (lenient), not "is it attached to the exact right verb". The
  verb-centric metric would have penalised spaCy for aux-attachment choices the organ does not care about.
- **The info-free twin had to destroy LOCALITY too.** My first twin (random ADJACENT nominal) scored 0.73 and
  did not lose -- because adjacency is itself a real cue in inversion. Only a twin that picks a random nominal
  ANYWHERE (0.23) is genuinely information-free and isolates the case/frame contribution.
- **A tested instinct beat an untested one.** My first instinct was "the brain parses cue-FIRST, so replace the
  parse with a cue picker." I BUILT it and it LOST (worse than spaCy on canonical cases). The Competition Model
  had told me why in advance: position is the HIGHEST-validity cue in English and is overridden only on marked
  constructions -- so the faithful shape is position-DOMINANT + cue-OVERRIDE, not cue-first replacement. Testing
  the instinct instead of asserting it turned an overclaim into the correct architecture (and the correct landing:
  extend the position-dominant `graded_role_assigner` with case/frame/agreement cues, do not replace it).

# ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -- candidate next problems)

1. **The substrate's brain-faithful role organs are BUILT but NOT WIRED -- and the live role source is still
   spaCy (HIGH leverage, WIRING).** `hdlab/graded_role_assigner` (Competition-Model cues), `hdlab/incremental_parser`
   (left-corner), `hdlab/arc_labeler` read `WIRED` but `used_by = tests only` (BRAIN_FOUNDATIONAL_AUDIT L122-124);
   meanwhile the live coref cache carries spaCy-derived roles (proven here). So the organs that would fix inversion
   the brain's way exist and are idle. **Fidelity gap: `graded_role_assigner`'s cue set is voice/animacy/subcat but
   (checked) has NO morphological-CASE cue and no quote-aware reporting-frame cue** -- the two cues that recover
   inversion here. Optimization: add those two cues (glass-box, PINNED) to `graded_role_assigner` and WIRE it as the
   role source. This is the real landing; my Phase C repair is the isolated proof it works.
2. **The incremental_parser's left-corner rule binds the nearest PRECEDING nominal as subject -- so it ALSO fails
   inversion, MEASURED** (`exp_role_cue_first_subject_v1.py`): 0.000 on real dialogue inversion (n=30), 0.125 on
   the collapsed-parse hard set -- worse than spaCy raw. Its position-only bind (docstring: "eagerly bind the
   nearest preceding buffered nominal as the pre-verbal subject") is not register-robust by construction. A
   faithful parser must let the CASE cue OVERRIDE the position default on marked constructions -- i.e.
   `incremental_parser` should consult a case/agreement cue, not just position. Candidate follow-on: a
   non-canonical / inversion arm for the incremental parser (its own consolidation report already flagged
   prediction/revision as ~neutral on clean prose; inversion is the untested marked case).
3. **Archaic MORPHOLOGY (thou/hath/-est/quoth) collapses spaCy's tokenizer+tagger.** 0.77% of LitBank (low), but
   the substrate reads Shakespeare/tinyshakespeare/KJV where it is common. A small archaic-morphology lexicon
   (thou=nom-2sg pronoun; -est=2sg finite verb; quoth=say) feeding the POS/role stage is a cheap, PINNED,
   glass-box fix -- candidate next problem gated on whether those corpora are on the live reading path.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- strategy to re-verify + fold in)

The corpus-age parse confound (arc-parser / thematic-role / corpus-age entry) should move from
**SUSPECTED-UNMEASURED to MEASURED-BOUNDED**: (a) spaCy's archaic subject-ID is **not wholesale-degraded** (natural
0.94 >= modern 0.89, flat to 40+ tokens); (b) the degradation is **construction-specific** -- subject-verb
inversion (~60% error, ~4-12/1000 verbs) + archaic morphology (0.77% of LitBank); (c) it is **immaterial to
aggregate coref** (correcting all cache role errors moves strict-Cb by -0.0009; metric verified live via a shuffle
control and a sensitivity sweep); (d) the LIVE role source is confirmed **spaCy** (cache roles carry
nominative-pronoun-OBJECT errors); (e) the brain-faithful fix is a **case + quote-aware-frame cue stage** (inversion
0.47->0.83, twin loses, register-invariant) whose natural home is the islanded `graded_role_assigner`, added as a
POSITION-DOMINANT + cue-OVERRIDE stage (a cue-first REPLACEMENT was built and lost -- worse than spaCy on canonical
cases). Additional audit entry for `incremental_parser`: its position-only left-corner subject bind scores **0.000
on dialogue inversion** (measured) -- it inherits the same inversion weakness and needs a case/agreement override.

# FOR STRATEGY -- proposed hdlab change (Q111; you land it)

Do NOT retrain or swap the parser (invariant). Instead, add a brain-faithful, glass-box **subject-cue repair**
as a separate post-parse stage, and prefer wiring it into the islanded `graded_role_assigner`:
- **CASE cue:** a nominative pronoun (he/she/they/I/we) attached to a verb as a non-subject IS its subject.
- **QUOTE-AWARE VERB-FRAME cue:** a reporting verb's speaker is the nominal OUTSIDE quotation marks (overrides a
  quote-internal nsubj).
- Keep the parser's own nsubj whenever it found one outside quotes (canonical unchanged; measured no regression,
  +0.09 on modern). Then rebuild `data/litbank/who_did_what_events.json` through the repaired role source.
Reference impl + proof: `experiments/exp_role_cue_repair_inversion_v1.py` (`repaired_subject_span`). Expected live
effect: small on aggregate coref (the confound is bounded) but a correctness gain on dialogue-speaker role tracking.

---

## TLDR (plain language)

We feared that our old story-books (100-200 years old) were breaking the automatic grammar tool we use to find
"who is the subject" of each sentence, and that this was secretly hurting every organ that reads it. **It mostly
isn't.** The tool reads old literary prose about as well as modern textbook prose (it even does a bit better,
because old novels are full of easy pronouns like "he" and "she"). The ONE place it reliably trips is when the
old style puts the subject AFTER the verb -- "said he", "cried the old man", "quoth the raven" -- where it wrongly
calls "he" the object. That happens in dialogue tags a few times per thousand sentences, and when we fixed every
such mistake, the downstream character-tracking barely changed -- so the old-books-break-the-parser worry is
retired. We also built the brain's own fix for the tripping case: a human knows "he" must be the subject (you'd
never say "said him"), so we added that "he-can-only-be-a-subject" rule plus a "the speaker is outside the quote
marks" rule, and it fixed the errors (0.47 -> 0.83) without breaking anything else, and worked identically on old
and modern text.

## QUESTIONS

None.

## NEXT STEPS

1. **Land the cue-repair the brain's way (strategy, Q111):** add the CASE + quote-aware-frame cues to the islanded
   `hdlab/graded_role_assigner` and WIRE it as the role source, then rebuild the coref cache through it.
2. **File the two mapped follow-ons:** (a) give `incremental_parser` a case-cue override so it stops binding the
   pre-verbal nominal on inversion; (b) an archaic-morphology lexicon (thou/-est/quoth), gated on whether
   Shakespeare/KJV are on the live reading path.
3. **Optional deepening (mine, if directed):** grow the inversion gold (n=30->~100) to tighten the +0.367, and add
   a full-NP long-subject archaic oversample to firm the wholesale null on the hardest sentences.
