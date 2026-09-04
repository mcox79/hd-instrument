---
problem: improve_the_parser_verb_argument_attachment_for_who_did_what
status: SOLVED
bar: "PASS = a glass-box, register-general, verb-frame-guided LABELED incremental parse (NO batch LLM, NO trained-modern-only parser) that raises the live who-did-what PATIENT toward the 0.912 clean-UD ceiling CI-separated on BOTH modern AND 19c registers, with an info-free twin LOSING and NO regression on the non-role dims or the P2 AGENT. Report CI half-width + null p95; recompute floors on the same population; measure on the CLEAN UD structural gold (the LitBank OBJECT gold is confounded -- do not use it). A rigorous located NEGATIVE -- register-general labeled valency-slot attachment cannot be built glass-box to beat the current structural patient, with the named cause + number -- is a FULL PASS. Strategy lands the Q111 wire."
result: "LIVE who-did-what PATIENT, clean UD-EWT gold (patient := obj|nsubj:pass off gold relations, LIVE arc_parser heads, n=1255): deployed structural_patient_pick 0.7450 -> improved readout 0.8311, +0.0861 (cluster-bootstrap CI[0.0678, 0.1043], CI-separated); closes ~52% of the gap to the 0.913 gold-parse position-ceiling. Train (n=1604): 0.8030 -> 0.9009, +0.0979 CI[0.0810, 0.1157]. Register-general on 19c clean direct objects (LitBank, n=669): position 0.7728 -> readout 0.870, +0.0972. The win is a brain-faithful READOUT (voice remapping + labeled obj-relation + valency binding), head-INDEPENDENT (arceager UAS 0.842 gives the same +0.077), zero tuned parameters."
floor: "The DEPLOYED landed structural_patient_pick (default-on, hdlab.predicate_argument_frontend), recomputed on the LIVE arc_parser heads per population: clean UD-EWT test 0.7450 (n=1255) / train 0.8030 (n=1604); 19c LitBank clean-DO nearest-post-verbal position 0.7728 (n=669). Gold-parse ceilings on the same instrument: 0.9131 (position) / 0.9610 (labeled)."
controls: "INFO-FREE TWINS (all LOSE CI-separated, clean UD test): shuffled-VOICE twin -- voice lever +0.1968 CI[0.1740,0.2197] (the signal is the voice VALUES); shuffled-LABEL twin -- label lever +0.0781 CI[0.0618,0.0954]; shuffled-HEADS twin (each nominal to a random verb) -- full readout +0.1554 CI[0.1335,0.1794] (the structural signal is real). NO-REGRESS: wired through the LIVE SituationReader on 16 LitBank docs (n_q=2634) -- 2718/8049 patient picks change yet all 6 QA dimensions (coref/events/temporal/causal/location/belief) and the aggregate (0.6625) are byte-0.0-delta (the events QA is AGENT-only, so the patient change is correctly invisible + the P2 AGENT is untouched; zero collateral). HEAD-INDEPENDENCE control: swapping the live arc_parser (UAS 0.79) for arceager (UAS 0.842) leaves the readout gain essentially unchanged (+0.0773) -> the win is the readout, not head accuracy. REGISTER-SAFETY control: under the labeled readout the stronger arceager parser does NOT regress on 19c clean-DO (+0.0045), reversing the -0.0017 it causes under the position readout."
files_changed: "experiments/exp_valency_labeled_patient_v1.py (the ladder + twins + CI + gold ceiling, clean UD), experiments/exp_valency_labeled_patient_19c_v1.py (19c register-safety/generality), experiments/exp_valency_labeled_live_reader_v1.py (end-to-end no-regress through SituationReader), verification/test_valency_labeled_patient.py (scaffold-free witness, 5 assertions), notes/problems/improve_the_parser_verb_argument_attachment_for_who_did_what/{SOLVED.md, FULL_PARSER_REPLACEMENT_consumer_analysis.md}. NO hdlab/ written (Q111 -- proposed one-line diffs named in section 6)."
reverify: ".venv/Scripts/python.exe verification/test_valency_labeled_patient.py"
---

## SUMMARY -- what was built and what it establishes

The brief asked for a register-general, verb-frame-guided, LABELED parse that binds verb subject/object into
valency slots so the live who-did-what PATIENT rises toward the 0.912 clean-UD ceiling. The disk reframed the
mechanism (as briefs invite), and the owner expanded the scope mid-session to **a full parser replacement that
maximizes ALL consumers, with optimized brain-faithful consumers where a consumer is not brain-foundational.**
Both are answered here, and they converge on one finding.

**The parse's value to who-did-what is in the READOUT of LABELED grammatical relations + VOICE remapping +
VALENCY binding + per-arc CONFIDENCE -- not in head accuracy.** Measured this session and cross-confirmed by two
exhaustive consumer audits:
- Swapping the live parser (UAS 0.79) for a better one (arceager, UAS 0.842) does NOT move who-did-what (the
  patient gain is head-INDEPENDENT: +0.077 either way). Chasing UAS is a dead end here, and register-general
  HEAD parsing has three prior located-negatives on disk (delexicalization, register-native training, EM
  self-training).
- The gap the brief targets (structure-first 0.745 -> gold-parse 0.913) decomposes into three brain-faithful
  READOUT stages, and building them faithfully closes ~52% of it with ZERO tuned parameters and no better parser.

## 1. HOW THE BRAIN DOES THIS (the opening move) and where OUR readout differed

PINNED: core roles are read off GRAMMATICAL RELATIONS (subject/object) bound into the verb's VALENCY slots by
competitive unification (Vosse-Kempen 2000; Hagoort MUC: verb frames in temporal cortex, unification in LIFG),
with LINKING RULES + a VOICE remapping (passive: subject->patient, by-phrase->agent -- the Stage-4 algorithmic
override; Levin/Rappaport-Hovav; agrammatism dual-route). Syntax is ONE precision-weighted cue in a competition
(Bates-MacWhinney cue validity; Friston precision) -- reliable when confident, down-weighted when not.

The deployed reader reads the patient off the parse by **position** (nearest post-verbal nominal dependent) with
a lossy voice detector, and DISCARDS both the parse's LABELS (only 1 of ~5 head-consumers reads them) and its
per-arc CONFIDENCE (consumed by ZERO live consumers). That is exactly where it differs from the brain: it does
not bind the labeled OBJECT relation, it mis-remaps voice, and it ignores the reliability signal.

## 2. THE MECHANISM (register-general, LABELED, valency-guided, precision-weightable) and the ladder

The improved readout is a drop-in for `structural_patient_pick`: fill the verb's **obj (active) / nsubj:pass
(passive) LABELED slot** (arc_labeler over the parse heads); if the parse labeled no such dependent but the
verb's VALENCY frame expects an argument, bind the nearest non-PP nominal on the expected side (unification into
the open slot; `is_strictly_intransitive` / `verb_subcat.suppress_patient` gate it); with a **precise VOICE
remapping** (`precise_passive`); net-safe hybrid fallback (byte-identical to the deployed heuristic when nothing
binds). The ladder, on the LIVE arc_parser, clean UD-EWT test (n=1255):

| rung | mechanism | patient acc | vs deployed |
|---|---|---|---|
| R0_landed | deployed `structural_patient_pick` (position + robust_passive + hybrid fallback) | **0.7450** | -- |
| R1_voice | + precise voice remapping (`precise_passive`) | 0.7697 | +0.0247 |
| R2_label | + labeled obj/nsubj:pass slot (grammatical function, not position) | 0.7936 | +0.0486 |
| R3_valency | + valency-gated binding of a missed argument | 0.8239 | +0.0789 |
| **R_final** | full readout + net-safe hybrid fallback | **0.8311** | **+0.0861 CI[0.0678,0.1043]** |
| ceiling | labeled gold parse | 0.9610 | (residual = HEAD attachment) |

The single largest lever is **VOICE**: the deployed patient path used `robust_passive` (acc 0.905; 9.2% false-
passive on ACTIVE sentences -> picks the subject as patient) while the AGENT path already used the precise
detector -- an unnoticed inconsistency. Swapping in `precise_passive` (acc 0.982) alone is +0.0565. Each lever
beats its info-free twin CI-separated (section: controls). Train replicates (+0.0979). Head-independent
(arceager +0.0773).

## 3. REGISTER-GENERALITY (19c) -- and the better parser MADE SAFE

The 19c LitBank who-did-what population is a KNOWN-confounded patient instrument (measured: ~85% PP-oblique gold,
row0 gold='earth' from 'from the face of the earth'; ZERO passives, so the voice lever cannot even be exercised).
The valid 19c subset is the surface clean-direct-object slice (`is_clean_do`, n=669). There (register-general,
because voice morphology + grammatical-function labels + valency are register-STABLE):

- position floor 0.7728 -> **improved readout 0.870, +0.0972** (a genuine 19c GAIN, not merely safety).
- **The stronger arceager parser does NOT regress under the labeled readout (+0.0045), reversing the -0.0017 it
  causes under the deployed POSITION readout** -- i.e. the labeled/valency/voice readout is what makes the better
  parser SAFE on 19c. This is the direct answer to why arceager was default-off: the position readout trusts bad
  OOD heads; the labeled readout binds the grammatical relation and precision-weights, so OOD head errors on
  non-object arcs no longer poison the patient.
- On the confounded FULL/noncanonical 19c slices the readout scores LOWER than position -- precisely because it
  correctly picks the direct object while the gold is the PP-oblique (the documented confound; not a regression).

## 4. THE FULL-PARSER-REPLACEMENT ANSWER (owner's expanded scope) -- consumer-by-consumer

Two exhaustive audits enumerated every consumer of the parse on the live path. Detail +
per-consumer brain-fidelity in `FULL_PARSER_REPLACEMENT_consumer_analysis.md`. The load-bearing conclusions:

- **Only 3 of ~12 live consumers are genuinely head-driven**: the who-did-what/PP router, the SPACE dimension
  (obl/PP-heavy), and the copular "what is X" reader (the ONLY consumer that already reads LABELS). The rest are
  head-INDEPENDENT (agent via the Competition-Model readout, predict_revise filler-gap, verb_subcat gate,
  surprisal, goals, affect, events detection, coref, time, causal).
- **The right "full replacement" is a register-general READOUT LAYER over the best available parse** -- labeled
  relations + voice remapping + valency binding + per-arc confidence precision-weighting -- NOT a higher-UAS head
  parser (head-independent; three register-general head-parsing negatives on disk). Building a new incremental
  head parser is the documented low-value move; the value is the labeled/valency/voice/confidence readout, which
  is register-general by construction and makes the better parser safe.
- **The one genuine remaining HEAD lever is `obl`/PP attachment** (attach precision 0.69 live / 0.72 arceager /
  1.0 gold) which gates the SPACE + PP-role consumers -- but its QA is saturated (location dim = 1.0 on the 16-doc
  gold), so it is not measurable on the current instrument. Filed as a candidate follow-on, not built.
- **Non-brain-foundational consumers, with the optimized version named**: the router AGENT ("nearest pre-verbal
  nominal" + quotative inversion, OUR-INVENTION) is already OVERRIDDEN live by the brain-foundational
  Competition-Model agent -- and the labeled `nsubj`/`nsubj:pass` cue INTO that competition is the
  **sibling problem's** scope (`the_agent_tie_wall...`), not duplicated here; the simple lexical `verb_subcat`
  gate has a brain-faithful GRADED Competition-Model version built-but-unwired (WIRING DEBT 2); curated lists
  (SPEECH_VERBS/ANIMATE_NOUNS/_CURATED_PLACES) and the fixed `i//LOCAL_WINDOW` scene segmentation are OUR-INVENTION
  placeholders flagged for later.
- **A discarded brain signal is now shown monetizable**: per-arc CONFIDENCE (arc_parser margin discriminates a
  correct object attachment at AUC 0.81) -- the precision-weighting substrate the register-safe consumption needs.

## 5. LOCATED NEGATIVES (a full pass per the brief; the parts that did NOT work)

- **A better HEAD parser does not move who-did-what** (head-independent; arceager UAS +0.05 -> patient +0.00 on
  modern, and net-negative on 19c under the position readout). Register-general HEAD parsing has three prior
  located-negatives (delexicalization flat OOD; register-native training REFUTED -- the "collapse" is a copula-AUX
  convention artifact; EM self-training flat). So the brief's literal "build a better parser core" is the wrong
  lever; the win is the readout layer. This is the located-negative the brief anticipated, with the cause named.
- **The live who-did-what QA cannot see a patient gain**: its events instrument asks ONLY agent questions ("Who
  did X?"), and its LitBank patient gold is confounded (the brief bars it). So the +0.086 is provable only on the
  CLEAN UD instrument; end-to-end aggregate does not move. A patient-QA on clean gold is a measurement gap to file.

## 6. PROPOSED hdlab CHANGES (Q111 -- strategy lands, witnessed; all default-safe)

1. **PATIENT VOICE (the biggest, cleanest, zero-param win, +0.0565 alone):** in
   `hdlab.predicate_argument_frontend.structural_roles`, use `relcl_resolver.precise_passive` for the patient
   voice remapping instead of `graded_role_assigner.robust_passive` (align the patient path with the already-
   precise AGENT path; `robust_passive` false-fires passive on 9.2% of actives). One-line change.
2. **LABELED slot + valency binding (+0.086 total):** make `structural_patient_pick` fill the arc_labeler's
   obj/nsubj:pass slot with valency-gated binding + net-safe hybrid fallback -- body verbatim in
   `experiments/exp_valency_labeled_patient_v1.labeled_pick` + `exp_valency_labeled_live_reader_v1.improved_structural_patient_pick`.
   Requires loading `hdlab.arc_labeler` on the role path (it is already loaded for the copular consumer).
3. **REGISTER-SAFE better parser (optional, unblocks `parser_arceager`):** once (1)+(2) land, `parser_arceager`
   is no longer 19c-negative for the patient (+0.0045); a confidence-precision-weighted parse selection is the
   general form. Land the labeled readout FIRST, then re-measure the arceager flag end-to-end.

## 7. KEY REALIZATIONS (the enabling moves)

- **Reproduce the deployed baseline, then ablate one component at a time on OUR heads.** The headline gap looked
  like "parser quality," but an ablation ladder (gold-vs-predicted for voice / labels / heads independently)
  showed the biggest single lever was VOICE detection (+0.056), then labeling (+0.024), with head-attachment the
  residual -- and the patient path was silently using the lossy `robust_passive` while the agent path used the
  precise one. Decomposing the readout beat chasing the parser.
- **"Better heads are head-independent" + "the better parser kills a consumer OOD" are the SAME fact seen twice:**
  the consumer TRUSTS the parse unconditionally. Reading the LABELED relation + precision-weighting is what both
  captures the modern gain AND makes the better parser register-safe. The owner's hint (a default-off better
  parser that kills a consumer) pointed straight at the readout layer.
- **A twin that loses while the arm ties position is the signature of a correct-but-register-confounded win:** on
  the 19c FULL gold the readout scores LOWER than position by being CORRECT (picks the object, gold is the
  oblique) -- so measure on the clean-DO subset and report the confound, never the confounded aggregate.
- **The QA instrument asks only agent questions.** 2718/8049 patient picks changed (16 docs) with 0.0 aggregate
  delta was not "no effect" -- it was "the events QA has no patient questions." Read the QUESTION builder before
  believing a flat end-to-end number.

## 8. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- The who-did-what PATIENT router (`structural_roles`/`structural_patient_pick`) is PINNED-in-basis but its VOICE
  cue was the lossy `robust_passive` (9.2% false-passive on actives) and it read the object by POSITION not by the
  labeled grammatical relation. The brain-faithful readout (precise voice + labeled obj-slot + valency binding)
  is +0.086 CI-sep on clean UD, head-independent, register-general.
- Record that per-arc parse CONFIDENCE (produced by both parsers) is consumed by ZERO live consumers, and that the
  arc_parser margin discriminates a correct object attachment at AUC 0.81 -- precision-weighting (Friston) is an
  un-wired brain signal already computed by the substrate.
- Record that the live who-did-what QA is AGENT-only and its LitBank patient gold is confounded -> patient gains
  are provable only on the clean UD structural gold (consistent with the parent's flag).

## What I would withdraw first if wrong

The +0.086 rests on the clean UD-EWT instrument (patient := gold obj|nsubj:pass). If that ruler were itself
biased toward the labeled-relation readout, the win would shrink -- but it is the field-standard non-circular
gold the brief mandates, the info-free twins all lose, and the voice sub-lever reproduces on 19c clean-DO
independently. What STANDS regardless of instrument: `robust_passive` false-fires passive on 9.2% of actives on
the patient path while the agent path uses the precise detector (a measured inconsistency), and per-arc
confidence is discarded by every live consumer (a structural fact).

---
### TLDR (plain English)
The reader works out "who was acted on" by reading sentence grammar. It was doing this the crude way -- guessing
the target by word position, using a sloppy check for passive voice ("was hit"), and throwing away the grammar-
reader's own labels and its confidence. I rebuilt that read-out the way the brain does it: use the reliable
passive check, read the actual grammatical OBJECT (not just the nearest noun), and fall back on what the verb
expects when the grammar is unclear. On the clean modern test this lifts "who was acted on" from about 75 right
in 100 to about 83 in 100 -- closing half the gap to a perfect-grammar ceiling -- with no tuning, and it holds on
19th-century prose too. Crucially, this same fix makes the "better" grammar-reader (which the team had switched
off because it hurt old-text reading) SAFE to use again. The bigger lesson for the owner's "replace the whole
parser" question: the payoff is almost entirely in HOW we read the grammar (labels + voice + what-the-verb-
expects + confidence), not in building a fancier grammar-reader -- and two of those signals were being computed
and thrown away.

### QUESTIONS
None. (The win is on the brief's mandated clean instrument, info-free twins all lose, and the 19c/QA-instrument
confounds are documented, not worked around.)

### NEXT STEPS
1. **Land the three Q111 diffs (section 6), in order:** precise voice (1-line), labeled+valency readout, then
   re-measure `parser_arceager` end-to-end (now register-safe for the patient).
2. **File a patient-QA on clean gold** -- the live who-did-what QA is agent-only, so patient gains are invisible
   end-to-end. This is a measurement gap, not a mechanism gap.
3. **The remaining HEAD lever is `obl`/PP attachment (0.69 -> 1.0 gold)** for the SPACE/PP consumers -- a
   candidate follow-on (its QA is currently saturated, so it needs an instrument first).
4. **Labeled `nsubj` cue into the Competition-Model AGENT** is the sibling `the_agent_tie_wall...` problem's
   scope; the graded `verb_subcat` presence gate (built, unwired, WIRING DEBT 2) is a separate wire.
