# THE BRAIN-FOUNDATIONAL EXTRACTION CHAIN — exact signal each needs + FIRST-STEP fidelity (+ the 19c root cause)

Owner Qs (2026-09-02): "why exactly did we lose on 19c — disambiguate at each step for the truly
brain-foundational components, understand the parser loss at the root, improve if we can" AND "how many truly
brain-foundational components are there? do we know exactly what signal they need, and can we disambiguate the
first step for all of them?"

## THE KEY STRUCTURAL FACT: they form ONE DEPENDENCY CHAIN, so every "first step" collapses onto 5 shared signals
```
  TOKENS  ->  POS/LEMMA  ->  HEADS  ->  ROLES  ->  EVENTS
 (segment)   (pos_tagger)  (parser) (role organs) (situation model)
```
Every truly brain-foundational component's FIRST required signal is one of these 5. So "disambiguate the first
step for all of them" = measure the fidelity of these 5 shared signals — which we now have.

## THE COMPONENTS (truly brain-foundational = PINNED "copy the brain's operation", NOT OUR-INVENTION placeholders)
| # | component | brain mechanism (PINNED) | EXACT signal it needs | its FIRST step (root input) |
|---|---|---|---|---|
| 1 | `pos_tagger` | lexical-category access (ventral stream) | token string + local char/word context | TOKENS |
| 2 | arc-eager parser | incremental structure-building (Now-or-Never; left-corner) | tokens + POS | POS |
| 3 | `graded_role_assigner` (hybrid_role_patient) | Competition-Model role binding (position-dominant + voice/gap OVERRIDE) | tokens + POS + verb-idx + candidate nominals | POS + POSITION |
| 4 | `relcl_resolver` / `predict_revise` | active-filler filler-gap (Frazier; Stowe) | tokens + POS + verb + relativizers/voice | POS |
| 5 | `predicate_argument_frontend` | structure + role pools (Matchin-Hickok); matrix-verb + PP/oblique roles | tokens + POS + **HEADS** | HEADS |
| 6 | `verb_subcat` | lexical argument structure | verb LEMMA | LEMMA |
| 7 | `predictive_reader` (predict_surprisal) | N400 forward prediction (predictive coding) | the extracted EVENT (verb+role+patient) | ROLES/EVENT |
| 8 | `graded_competition` | maintained distribution (Bayesian posterior; McClelland 2013) | per-candidate cue SUPPORTS + validities | the CUES (from #3) |
| 9 | `world_state_register` | event-indexing situation model (Zwaan-Radvansky; STRIPS) | events with agent/patient/RECIPIENT roles | ROLES/EVENT |
**Count: 9 truly brain-foundational components in the extraction chain** (further downstream: conceptual_meaning
/ belief / coref — different dimensions). NON-foundational, flagged, EXCLUDED: `arc_labeler` (grammatical labels
— measured harmful), `semantic_parser` (intent/slot placeholder). **Yes — we know exactly what each needs (the
"EXACT signal" column, read from the code), and the first step for all 9 is one of the 5 shared signals.**

## FIRST-STEP FIDELITY (measured; `exp_19c_signal_loss_v1` + the organ cells)
| shared signal | who needs it first | MODERN fidelity | 19c fidelity | drop |
|---|---|---|---|---|
| TOKENS | #1 tagger | pre-tokenized (PTB-style, clean) | pre-tokenized | ~0 |
| POS — verb tagged VERB | #2,#3,#4 | **0.892** | **0.791** | **−0.100** |
| POS — patient tagged NOMINAL | #3 | 0.997 | 1.000 | +0.003 |
| POSITION — patient post-verbal | #3 | 0.725 | 0.879 | +0.155 (19c EASIER on order) |
| HEADS — patient attaches to verb | #5, my head-rule | **0.578** | **0.458** | **−0.121** |
| ROLES — patient organ accuracy | #7,#9 downstream | 0.541 | 0.411 | −0.130 |

## THE 19c ROOT CAUSE, DISAMBIGUATED (answering "why exactly did we lose on 19c")
The 19c items are STRUCTURALLY EASIER (88% post-verbal vs 72%; only 12% passive/non-canonical vs 53%) — yet
accuracy is LOWER (0.41 vs 0.55). The loss is NOT the role mechanism; it is the two UPSTREAM brain-foundational
signals both degrading on an archaic register neither component has READ:
1. **POS (verb identification) drops −0.100** (0.892 -> 0.791): the tagger, trained on modern UD-EWT, mis-tags
   ~21% of 19c verbs (archaic morphology / literary syntax). This corrupts the voice cue AND the parse.
2. **HEADS (patient attachment) drops −0.121** (0.578 -> 0.458): the parser, trained on modern UD-EWT, attaches
   the patient to its verb only 46% of the time on 19c. THIS is exactly why my head-using rule LOSES to the
   position organ on 19c — the heads are wrong 54% of the time, so the position-dominant organ (which ignores the
   degraded heads — the brain-faithful move) is correctly more robust. Partition evidence: 19c "parser-did-not-
   attach" items are 54% of the set (vs 42% modern), and there the organ falls back to position (acc 0.27).
**ROOT = a REGISTER/experience gap in the two shared upstream signals (POS + HEADS), not a mechanism defect.**
The brain parses 19c by having READ 19c (experience-based statistics; Competition-Model validities are learned
per register). Our tagger + parser have not. This is the SAME root as the modern arc->spaCy residual (domain
shift), now localized to 19c with numbers.

## ⚠️ PROTOTYPE CORRECTION (`exp_tagger_prototype_19c_v1`) -- the tagger/parser register gap is NOT the who-did-what lever
Owner asked to prototype the fix to the worst component and show it improves. I fed a BETTER tagger (spaCy UPOS,
strong-reference proxy for a gold-target-register tagger) into the SAME parser + real organ. Result:
| signal | who-did-what recovery | verb-ID (S1) recovery | parser-attach (S4) recovery |
|---|---|---|---|
| modern | **+0.002 (none)** | +0.057 | +0.024 |
| 19c | **+0.000 (none)** | +0.025 | +0.010 |
The components DO improve at their OWN job (the tagger's verb-ID rises, the parser attaches a bit better), but
**none of it reaches who-did-what.** Reason: `hybrid_role_patient` is GIVEN the verb index and its candidates are
already 100% nominal-tagged, so it is ROBUST to tagger errors and position-dominant -- a better POS only nudges
the voice cue, not the position-dominant pick. **So my "the 19c who-did-what loss is rooted in the tagger+parser
register gaps" hypothesis is REFUTED by the prototype.** The register gaps are real AT the tagger/parser level
(and matter for the parser's OWN consumers -- matrix-verb F1, PP-role F1), but they do NOT flow to the patient
decision. THE REAL 19c who-did-what lever is the **SELECTION layer**: 43% of 19c items are "parser-did-not-attach
+ post-verbal" where the position fallback (nearest post-verbal) picks the WRONG one among several candidates --
a PLAUSIBILITY / world-knowledge decision (which noun is the plausible patient of THIS verb), i.e. the
register-native selectional store (the prior owner-DONE problem), NOT the tagger/parser. This is the value of
prototyping before attributing: the worst-MEASURED components were not the who-did-what lever.

## ⚠️ DEEP DISAMBIGUATION OF THE 19c WALL (owner: "disambiguate exactly the failure... understand all the walls") + PROPER prototype
Reading the `graded_role_assigner` submission COMPLETELY + characterizing the exact 19c failures
(`exp_19c_selection_failure_v1`) corrected the picture AGAIN. The 19c who-did-what failures are NOT the
tagger/parser register gap (proven: better POS -> WDW +0.00) and NOT the organ's documented reduced-relative/
verb-subcat residual (that was the McGuffey/QA-SRL slice). They are, decisively:
- **93.4% PP-EMBEDDING**: the gold argument is a PREPOSITION's object, mean **9 tokens** after the verb, the
  nearest post-verbal noun only 1.4% of the time; the verbs are often intransitive/copular (hover, droop, be,
  arise). E.g. "hovering in the rigging of great **ships**" (gold=ships), "a seat of yours at **kingsbere**".
  This is a property of long HYPOTACTIC 19c literary prose (Dickens/Austen/Poe) -- arguments buried in PP chains.
- The position-organ (nearest post-verbal) is STRUCTURALLY the wrong tool for these; the parser's head-chain /
  PP-attachment (`_attaches_to_verb` / `_pp_args_for_verb`) is the mechanism designed for it.
- **This is partly a TASK/GOLD characteristic**: many golds are LOCATIVE/OBLIQUE heads of intransitive verbs,
  i.e. the 19c "who-did-what patient" population is contaminated with obliques (a QA-SRL/head-extraction artifact
  on PP-heavy prose), not pure direct-object patients.
PROPER PROTOTYPE (the RIGHT component, its IDEAL mechanism; `exp_19c_pp_attachment_prototype_v1`): the gold is
transitively **REACHABLE via the parser head-chain 70%** on 19c (rich 0.698 > richfeat 0.676; vs 46% direct) --
so the parser CAN reach the PP-embedded gold, and the RICH parser reaches +0.02 more. A parse-based chain
selector (rich) = **0.428**, beating the position-organ (0.411) AND the richfeat chain (0.408) -- so the rich
parser HELPS 19c who-did-what modestly here (the earlier "parser doesn't help who-did-what" was only true for
the position-ORGAN, which ignores the chain). The residual = SELECTING which PP-chain noun is the argument
(semantic/plausibility), capped at the 70% reachability. On modern the chain selector is WORSE (0.463 vs 0.541)
-- modern is direct-object, 19c is PP-embedded: the two registers need DIFFERENT selectors.

## THE WALLS, ENUMERATED (owner: "understand all of the walls")
1. **Modern UAS residual to spaCy** (0.842 -> ~0.90): representation/architecture gap -- search + lexical
   refuted, structural crossed +0.024; residual = contextual encoding / annotation scheme / domain. FOLLOW-ON.
2. **19c PP-attachment REACHABILITY** (gold reachable 70% via parser chain): the parser degrades on long PP-heavy
   19c syntax; rich helps +0.02; register-native parse training would help more. PARSER lever.
3. **19c PP-noun SELECTION** (which of the reachable PP nouns is the argument): SEMANTIC/plausibility -- the
   register-native selectional store (matched fiction domain), NOT the parser. SELECTION lever.
4. **19c task-gold contamination** (obliques of intransitive verbs scored as patients): a MEASUREMENT/gold issue,
   not a mechanism wall -- the "who-did-what patient" metric is not clean on PP-heavy literary prose.
5. **Non-canonical reduced-relative residual** (organ's own submission): verb-subcat SUPPLY (WordNet, PROVEN
   +0.108) -> clause STRUCTURE (incremental parse) -> coref -> meaning-rep quality. ORGAN's documented walls.
6. **Tagger register gap** (verb-ID -0.10 on 19c): real at the tagger level but does NOT reach who-did-what
   (organ is head/tag-independent for the pick); matters for the parser's OWN attach + the meaning channel.

## CAN WE IMPROVE IT? (the brain-faithful fix, and what is already correct)
- **Already correct (do not "fix"):** the position-dominant + cue-override organ is the RIGHT mechanism for 19c —
  it correctly down-weights the degraded heads. Wiring heads INTO it hurts 19c (measured −0.044). Keep it.
- **The lever is register EXPERIENCE for the two upstream signals** (confirmed at the root): (a) tagger
  register-adaptation for archaic morphology (recovers the −0.10 verb-ID), (b) parser register-native training on
  GOLD 19c/literary parse data (recovers the −0.12 attach; self-training is refuted). Both are the SAME
  gold-target-register follow-on, now motivated by the exact per-step numbers rather than asserted.
- The residual after those (post-verbal multi-candidate selection on complex 19c clauses) is the selectional/
  world-knowledge layer, not the parser.
