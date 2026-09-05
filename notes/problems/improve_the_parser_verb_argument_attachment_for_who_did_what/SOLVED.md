---
problem: improve_the_parser_verb_argument_attachment_for_who_did_what
status: SOLVED
bar: "PASS = a glass-box, register-general, verb-frame-guided LABELED incremental parse (NO batch LLM, NO trained-modern-only parser) that raises the live who-did-what PATIENT toward the 0.912 clean-UD ceiling CI-separated on BOTH modern AND 19c registers, with an info-free twin LOSING and NO regression on the non-role dims or the P2 AGENT. Report CI half-width + null p95; recompute floors on the same population; measure on the CLEAN UD structural gold (the LitBank OBJECT gold is confounded -- do not use it). A rigorous located NEGATIVE -- register-general labeled valency-slot attachment cannot be built glass-box to beat the current structural patient, with the named cause + number -- is a FULL PASS. Strategy lands the Q111 wire."
result: "LIVE who-did-what PATIENT, clean UD-EWT gold (patient := obj|nsubj:pass off gold relations, LIVE arc_parser heads, n=1255): deployed structural_patient_pick 0.7450 -> improved readout 0.8311, +0.0861 (cluster-bootstrap CI[0.0678, 0.1043], CI-separated); closes ~52% of the gap to the 0.913 gold-parse position-ceiling. Train (n=1604): 0.8030 -> 0.9009, +0.0979 CI[0.0810, 0.1157]. Register-general on 19c clean direct objects (LitBank, n=669): position 0.7728 -> readout 0.870, +0.0972. The win is a brain-faithful READOUT (voice remapping + labeled obj-relation + valency binding), head-INDEPENDENT (arceager UAS 0.842 gives the same +0.077), zero tuned parameters."
floor: "The DEPLOYED landed structural_patient_pick (default-on, hdlab.predicate_argument_frontend), recomputed on the LIVE arc_parser heads per population: clean UD-EWT test 0.7450 (n=1255) / train 0.8030 (n=1604); 19c LitBank clean-DO nearest-post-verbal position 0.7728 (n=669). Gold-parse ceilings on the same instrument: 0.9131 (position) / 0.9610 (labeled)."
controls: "INFO-FREE TWINS (all LOSE CI-separated, clean UD test): shuffled-VOICE twin -- voice lever +0.1968 CI[0.1740,0.2197] (the signal is the voice VALUES); shuffled-LABEL twin -- label lever +0.0781 CI[0.0618,0.0954]; shuffled-HEADS twin (each nominal to a random verb) -- full readout +0.1554 CI[0.1335,0.1794] (the structural signal is real). NO-REGRESS: wired through the LIVE SituationReader on 16 LitBank docs (n_q=2634) -- 2718/8049 patient picks change yet all 6 QA dimensions (coref/events/temporal/causal/location/belief) and the aggregate (0.6625) are byte-0.0-delta (the events QA is AGENT-only, so the patient change is correctly invisible + the P2 AGENT is untouched; zero collateral). HEAD-INDEPENDENCE control: swapping the live arc_parser (UAS 0.79) for arceager (UAS 0.842) leaves the readout gain essentially unchanged (+0.0773) -> the win is the readout, not head accuracy. REGISTER-SAFETY control: under the labeled readout the stronger arceager parser does NOT regress on 19c clean-DO (+0.0045), reversing the -0.0017 it causes under the position readout."
files_changed: "experiments/exp_valency_labeled_patient_v1.py (the ladder + twins + CI + gold ceiling, clean UD), experiments/exp_valency_labeled_patient_19c_v1.py (19c register-safety/generality), experiments/exp_valency_labeled_live_reader_v1.py (end-to-end no-regress through SituationReader), experiments/exp_valency_labeled_patient_reattach_v1.py (the head-residual selectional re-attachment located-negative, sec 5), experiments/exp_categorical_backbone_parser_v1.py (the brain's register-general categorical-backbone parser + Jabberwocky mechanism validation, sec 5c; research note notes/research_register_general_argument_attachment_mechanism_2026-09-04.md), experiments/exp_ideal_argument_reader_v1.py (the full two-tier legality-gates-preference reader + cross-register/role generalization test, sec 5d), verification/test_valency_labeled_patient.py (scaffold-free witness, 5 assertions), notes/problems/improve_the_parser_verb_argument_attachment_for_who_did_what/{SOLVED.md, FULL_PARSER_REPLACEMENT_consumer_analysis.md}. NO hdlab/ written (Q111 -- proposed one-line diffs named in section 6)."
reverify: ".venv/Scripts/python.exe verification/test_valency_labeled_patient.py"
---

## INTEGRATED_BY_STRATEGY (2026-09-04) — EXCELLENT
Landed all 3 Q111 diffs into `hdlab/predicate_argument_frontend.py` (precise voice + labeled-obj/valency `structural_patient_pick`, `labeled_pick`/`position_pick`/`_transitive` promoted verbatim) + `hdlab/situation_reader.py` (`parser_arceager` DEFAULT-ON). Reverified `test_valency_labeled_patient.py` 5/5 + `test_labeled_patient_landing.py` (byte-identity 0/1255, +0.0861); arceager board-neutral (0.0 all dims); no-regress (patient invisible to the agent-only events QA). Follow-on filed: `add_a_patient_slot_who_did_what_qa_on_clean_gold`. §2b folded.

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
- **The brain's competitive-unification HEAD mechanism (precision-weighted selectional RE-ATTACHMENT) does NOT
  capture the +0.06 head residual -- fairly tested and null-to-negative.** Re-binding a LOW-confidence object arc
  (arc_parser margin < tau) to the post-verbal candidate with the best verb->PATIENT selectional fit scores
  -0.0056 to -0.0199 vs R_final across a tau/delta sweep, and TIES its shuffled-verb info-free twin (0.8255 vs
  0.8247) -- the selectional signal carries ~no information over a WRONG verb on this (modern, in-domain)
  instrument. Consistent with the CHAIN_SIGNAL_LOSS thematic-fit finding (subordinate to position; OOD-bound) and
  the FRAME_FIRST collapse (0.58). So the residual is genuine parse-HEAD error, not capturable glass-box by
  selection/valency competition -- a FAIR located-negative for the one remaining head lever. (per-arc confidence
  precision-weighting between parsers likewise gives only +0.002 on modern obj-attach.)
- **The live who-did-what QA cannot see a patient gain**: its events instrument asks ONLY agent questions ("Who
  did X?"), and its LitBank patient gold is confounded (the brief bars it). So the +0.086 is provable only on the
  CLEAN UD instrument; end-to-end aggregate does not move. A patient-QA on clean gold is a measurement gap to file.

## 5b. WHERE WE STAND vs STATE-OF-THE-ART and vs THE BRAIN (the walls + opportunities)

**vs SOTA (measured, clean UD-EWT test, n=1255, SAME R_final readout on each parser's heads):** our glass-box
arc_parser 0.8311; a competent NEURAL parser (spaCy en_core_web_sm, the parent's SOTA reference) 0.8558
(+0.025); GOLD heads 0.9171 (the upper bound any parser -- SOTA included -- can reach with this readout). So a
better parser buys only ~+0.025-0.09 on modern who-did-what -- the READOUT dominates, not head accuracy. (spaCy's
raw UAS reads 0.566 here purely because its CLEAR attachment scheme != UD -- a scoring artifact; the patient
readout is robust to it. Field SOTA biaffine/transformer parsers reach ~0.92-0.95 UAS on modern UD and SOTA SRL
~0.86-0.88 F1, but they are trained-modern (documented to COLLAPSE OOD on 19c -- the invariant's whole reason)
and/or LLMs (barred). On CANONICAL who-did-what we BEAT the spaCy parser: nphead 0.9701 vs 0.9162, +0.0539 CI-sep
-- parent `clean_frame_ladder`.) Net: a few points below a modern-ONLY SOTA parser on modern, but glass-box +
register-general + no-LLM, which SOTA is not.

**vs the BRAIN (human who-did-what is sentence-type-conditioned; parent MECHANISM_DIFF):** canonical/irreversible
~95-99% -- WE MATCH (0.97 on canonical clean-frame); reversible passive ~75-80%; reduced-relative/garden-path
~40-55% (humans keep the wrong reading). Our clean-UD 0.831 (91% active) sits at the human ceiling on canonical;
the residual is (a) parse-HEAD quality -- the brain's parser far exceeds ours on ordinary sentences, and THIS is
where we are below the brain -- and (b) the confounded ruler + missing dorsal Stage-6/7 (clause segmentation,
reanalysis) mapped in the parent's diff. The READOUT itself is now brain-faithful end-to-end (Hagoort MUC
valency + Levin/Rappaport-Hovav linking rules + voice remapping + Friston precision-weighting).

**THE WALLS (understood + fairly tested):**
1. **Register-general glass-box parsing (the +0.06-0.09 head residual).** A modern-only SOTA parser closes part
   of it on modern but collapses OOD; a register-general glass-box parser at SOTA accuracy is unsolved here AND
   is a known-hard open problem in the field (cross-domain/low-resource parsing). The brain's own head mechanism
   (selectional competitive unification) tested NULL-to-negative here (sec 5). This is the fundamental wall, and
   it is a FAIR located-negative -- not a defect in this solution.
2. **The measurement wall.** The live who-did-what QA is AGENT-only; the LitBank patient gold is confounded
   (~85% oblique, zero passives); no 19c gold UD treebank exists. The win is provable only on the clean UD ruler.
3. **The 19c non-canonical SELECTION/FOUNDATION wall.** The residual there is world-knowledge/thematic-fit bounded
   by a register-native event-knowledge store (the project's north-star clean-foundation problem), NOT parsing
   (parent CHAIN_SIGNAL_LOSS: pure thematic fit 0.40 vs position 0.01 where syntax is silent; OOD-bound).

**THE OPPORTUNITIES (understood):** the READOUT-layer pattern (labels+voice+valency+confidence) is the reusable
lever for every head-consumer (patient done; agent=sibling; space/obl needs an instrument); per-arc CONFIDENCE is
a computed-but-discarded brain signal (precision-weighting); the graded verb_subcat presence gate is a ready
downstream wire; and the deep opportunity is a register-general glass-box parser that does not collapse OOD (wall 1).

## 5c. CRACKING WALL #1 -- RESEARCHED + BUILT + VALIDATED the brain's register-general mechanism (owner push)

Owner (2026-09-04): "can't crack glass-box is being lazy; the brain does it, so we can too." So I did not stop
at the located-negative. Dispatched a deep literature scan
(`notes/research_register_general_argument_attachment_mechanism_2026-09-04.md`, 45 sources) and BUILT the
brain's actual mechanism (`experiments/exp_categorical_backbone_parser_v1.py`).

**THE MECHANISM (research thesis):** a modern-corpus-trained parser conflates attachment LEGALITY (categorical,
register-invariant) with PREFERENCE (graded, corpus-frequency) into ONE frozen score -> collapses OOD. The brain
uses a CATEGORICAL BACKBONE with NO corpus prior (nothing to collapse): closed-class scaffold + clause
segmentation (Kimball Two-Sentences stack) + verb VALENCY projection (Vosse-Kempen/Hagoort) + word-order/UTAH
default-linking + voice flip; frequency enters only as an ONLINE, locally-re-estimated tie-break (Fine et al.
2013: humans recalibrate within tens of sentences of the text being read -- never a frozen corpus import). This
is why a human parses 19c/Jabberwocky with no retraining and a statistical parser cannot.

**BUILT it (Stages 0-4, NO trained parser) and ran the decisive tests:**
- **MECHANISM VALIDATED on the Jabberwocky battery** (nonce content words in known frames + real closed-class +
  morphology; zero lexical content -- a trained parser has no grip): backbone PATIENT ~0.81, AGENT ~0.97 from
  PURE STRUCTURE (research HARD-PASS >=0.80/0.90). This proves attachment does NOT require corpus statistics --
  the categorical backbone alone assigns subject/object correctly with no lexical content.
- **On REAL modern UD-EWT the backbone UNDERPERFORMS the trained readout** (patient CATEG 0.627 vs R_final 0.831;
  agent CATEG ~0.84 vs positional ~0.86). Named cause: Stage-0 clause segmentation on REAL messy prose (no
  punctuation, complex coordination/apposition) is imprecise -- the heuristic segmenter is the bottleneck, and
  the trained parser already handles modern clause structure (a clause-boundary GUARD on the trained pick adds
  exactly +0.000). The MECHANISM is right; realizing Stage-0 clause segmentation on real text to human precision
  is itself a hard parsing sub-problem.
- **And it does not even matter for the PATIENT:** the trained readout is ALREADY register-safe (0.87 on 19c
  clean-DO, sec 3), so a register-general parser is NOT the patient lever. The patient is solved by the readout
  (+0.086) + the register-safe better-parser flip.

**So wall #1 is now a RESEARCH-GROUNDED, MECHANISM-VALIDATED located-negative with a precise cause, not "lazy":**
the brain's mechanism is proven (Jabberwocky), the reason a glass-box register-general parser doesn't yet beat
the trained one on real text is NAMED (clause-segmentation precision on real prose), and the remaining lever is a
better register-invariant clause segmenter -- which pays on the AGENT/very-OOD (the sibling `the_agent_tie_wall`
problem, whose embedded-clause tie is exactly what clean clause segmentation resolves: backbone agent 0.97 vs
positional 0.64 on structural Jabberwocky cases), NOT on this patient problem. The validated categorical backbone
+ Jabberwocky battery are handed to that problem as a ready mechanism.

## 5d. THE FULL IDEAL BRAIN-FOUNDATIONAL READER + DOES IT GENERALIZE (owner synthesis request)

Synthesized everything into the brain's two-tier architecture and prototyped it end-to-end
(`experiments/exp_ideal_argument_reader_v1.py`): **LEGALITY (register-invariant categorical backbone: clause-seg
+ valency + word-order/UTAH + voice) GATES PREFERENCE (the trained parser's labeled pick, precision-weighted),
with the backbone as the register-invariant fallback.** Measured across three REGISTERS x two ROLES.

**PATIENT (IDEAL vs the trained readout vs backbone-alone vs positional; GOLD ceiling):**
| register | IDEAL | trained-readout | backbone-alone | positional |
|---|---|---|---|---|
| modern UD-EWT (n=1255) | 0.8295 | 0.8311 | 0.6271 | 0.612 |
| 19c LitBank clean-DO (n=669) | 0.8759 | 0.8774 | 0.6233 | 0.710 |
| Jabberwocky pure-structure (n=54) | 0.8148 | 0.8148 | 0.8148 | 0.5926 |
| **cross-register SPREAD (lower=generalizes)** | **0.0611** | **0.0626** | 0.1915 | 0.1174 |

**DOES IT GENERALIZE? YES.** The ideal reader has the LOWEST cross-register spread (0.061) of any arm -- it does
NOT collapse OOD (0.83 modern / 0.88 19c / 0.81 Jabberwocky), and it is register-general BY CONSTRUCTION (labels +
voice + valency are register-invariant; the backbone catches any illegal parser pick). Backbone-ALONE collapses
on 19c (0.62, spread 0.19); positional spread 0.12. So the readout layer -- not head accuracy -- is what carries
register-generality, confirmed across three registers.

**HONEST verdict on the integration:** for the PATIENT the legality gate is essentially DORMANT -- IDEAL == the
trained readout to within +/-0.0016 on every register, because the trained parser's patient picks are already
categorically legal (in-clause) across all tested registers (the clause-boundary guard fired ~never; the
imprecise segmenter's rare over-veto makes IDEAL a hair BELOW the ungated readout on modern). So the FULL IDEAL
PATIENT reader reduces to the already-landed R_final readout -- which is the ideal AND generalizes (spread 0.061).
The categorical backbone is a validated register-invariant SAFETY NET (dormant on these registers; it would fire
on harder-OOD illegal picks).

**Where the ideal architecture's second tier is ACTIVE: the AGENT.** Same reader, agent role: Jabberwocky
(structural/embedded cases) backbone-agent 0.9688 vs positional 0.6406 (+0.33) -- the register-invariant clause
structure resolves the embedded-clause subject that positional and the OOD-collapsed trained parser both miss.
On real modern UD the agent backbone is 0.841 (~ positional 0.860, segmentation-noise-limited). So the two-tier
reader GENERALIZES across roles: for the patient the trained-readout tier carries (already register-safe); for
the agent the categorical-backbone tier carries on exactly the embedded-clause cases that are the sibling
`the_agent_tie_wall...` problem's wall. The remaining lever is a more precise register-invariant clause segmenter
(would lift the agent backbone on real prose toward its 0.97 structural ceiling) -- the named next build, owned by
the agent/OOD problem.

**Bottom line:** the full ideal brain-foundational reader is the two-tier legality-gates-preference architecture;
it generalizes (lowest cross-register spread, no OOD collapse); the PATIENT piece is the landed R_final readout
(ideal + generalizing); the AGENT piece is the categorical backbone (register-invariant, active on embedded
clauses). Nothing here is a frozen corpus prior -- the readout is register-invariant and the backbone has no
corpus prior to collapse.

## 6. PROPOSED hdlab CHANGES (Q111 -- strategy lands, witnessed; all default-safe)

1. **PATIENT VOICE (the biggest, cleanest, zero-param win, +0.0565 alone):** in
   `hdlab.predicate_argument_frontend.structural_roles`, use `relcl_resolver.precise_passive` for the patient
   voice remapping instead of `graded_role_assigner.robust_passive` (align the patient path with the already-
   precise AGENT path; `robust_passive` false-fires passive on 9.2% of actives). One-line change.
2. **LABELED slot + valency binding (+0.086 total):** make `structural_patient_pick` fill the arc_labeler's
   obj/nsubj:pass slot with valency-gated binding + net-safe hybrid fallback -- body verbatim in
   `experiments/exp_valency_labeled_patient_v1.labeled_pick` + `exp_valency_labeled_live_reader_v1.improved_structural_patient_pick`.
   Requires loading `hdlab.arc_labeler` on the role path (it is already loaded for the copular consumer).
3. **REGISTER-SAFE better parser -- FLIP `parser_arceager` ON under the labeled readout (a SOLVED opportunity):**
   once (1)+(2) land, the labeled/valency/voice readout makes the stronger arceager parser (UAS 0.842) net-
   positive AND register-safe -- patient +0.006 on modern (R_final arc 0.8311 -> arceager 0.8375) and +0.0045 on
   19c clean-DO (reversing the -0.0017 arceager causes under the deployed position readout). This is the concrete
   resolution of "the better parser kills a consumer": it no longer does, under this readout. Land the readout
   FIRST, then flip `parser_arceager` default-ON and re-measure end-to-end. (A neural parser gives more on modern
   -- spaCy+readout 0.856 -- but is barred by the invariant; arceager is the glass-box register-safe choice.)

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
and thrown away. I then researched and built the FULL ideal version -- the brain's actual design, where fixed
grammar RULES decide what's even possible and the statistical parser only picks among the allowed options -- and
tested it on modern, 19th-century, and pure-nonsense-word sentences. It generalizes the best of everything tried
(it does not fall apart on unfamiliar styles). For "who was acted on" the ideal reader turns out to equal the
read-out fix above (already the best), so that is what we ship; the extra rule-based machinery earns its keep on
"who DID it" in tangled multi-clause sentences, which is a neighbouring problem we hand it to.

### QUESTIONS
None. (The win is on the brief's mandated clean instrument, info-free twins all lose, and the 19c/QA-instrument
confounds are documented, not worked around.)

### NEXT STEPS (further improvement -- ordered; the architecture to build ON is the two-tier ideal reader)

**SHIP NOW (this problem -- the patient reader is complete + generalizing):**
1. **Land the three Q111 diffs (section 6), in order:** (a) precise voice (1-line: `precise_passive` for the
   patient path), (b) the labeled-obj + valency readout `structural_patient_pick` (the R_final reader -- this IS
   the ideal patient reader; the legality gate is dormant so ship it UNGATED, per sec 5d), (c) then flip
   `parser_arceager` default-ON (now register-safe under this readout). Net: live patient 0.745 -> 0.831, register-
   general (cross-register spread 0.061), no-regress.
2. **Fix the measurement gap: add a PATIENT-slot QA on clean gold.** The live who-did-what QA is AGENT-only, so
   the +0.086 patient gain is invisible end-to-end -- future patient work cannot be seen until this exists.

**THE ONE HIGH-VALUE FURTHER-IMPROVEMENT LEVER (owned by the agent/OOD problem, mechanism handed off):**
3. **A more precise register-invariant CLAUSE SEGMENTER (Stage 0 of the ideal reader).** This is the single lever
   that would push further, and it is now precisely located: the categorical backbone attaches perfectly on clean
   structure (Jabberwocky agent 0.97) but drops to ~0.84 on real messy prose because clause segmentation on real
   text (no punctuation, complex coordination/apposition) is imprecise. A better segmenter would (a) lift the
   AGENT backbone toward its 0.97 structural ceiling on real prose -- the biggest remaining who-did-what gain
   (agent gold ceiling 0.97 vs live ~0.86), and (b) activate the ideal reader's legality tier as a genuine
   register-safety net on harder-OOD. **This belongs to `the_agent_tie_wall_is_embedded_clauses...` (the embedded-
   clause agent tie IS a clause-segmentation problem); the validated categorical backbone + Jabberwocky battery
   (`exp_categorical_backbone_parser_v1.py`) are handed to it as the ready mechanism.** NOT a patient-problem lever
   (patient is already register-safe).

**LOWER-VALUE / SEPARATE:**
4. **`obl`/PP attachment (0.69 -> 1.0 gold)** for the SPACE consumers -- head-attachment bound (same wall);
   labeling HURTS it (sec 4). Needs a non-saturated obl instrument first.
5. **The graded `verb_subcat` presence gate** (built, unwired, WIRING DEBT 2) -- a strategy-side wire for the
   PRESENCE half of who-did-what, not this identity problem.
6. **Online-local frequency tie-break (Fine et al. 2013)** -- the research note's Stage 6: a per-document,
   incrementally-re-estimated tie-break (NOT a frozen corpus prior) for residual ambiguity the categorical layer
   leaves open. Deferred: residual ambiguity after legality+preference is small on the patient; build only if a
   consumer needs it.
