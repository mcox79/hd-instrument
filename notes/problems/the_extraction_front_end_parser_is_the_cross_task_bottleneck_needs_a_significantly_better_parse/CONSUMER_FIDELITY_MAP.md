# PARSER CONSUMER × BRAIN-FIDELITY MAP (owner directive 2026-09-01)

> Owner: *"deeply understand all the organs that rely on your outputs to make sure you optimize the
> outputs of all of them. Evaluate the brain-foundational fidelity of each — some may not be brain
> foundational, and thus their needs may differ from those that are. Knowing which are not brain
> foundational helps us improve those as well."*

**The parser's public output** (`hdlab/arc_parser.py:186`): `ParseResult(arcs, margins, heads)` — an
**UNLABELED** head-attachment map (`heads`), a per-token attachment **margin** (best−second = a soft
distribution), and `arcs`. POS+lemma come from `hdlab/pos_tagger.py`. Voice/filler-gap from
`hdlab/relcl_resolver.py`. **No dependency-relation labels natively** (arc_labeler adds them, off-path).

## THE HEADLINE STRUCTURAL FACT (from the consumer trace)
**The DEFAULT reader (`SituationReader()`, all 13 flags off) invokes NONE of the six parser modules.**
`read()`→`_read_events` with `role_route=='positional'` (the default) assigns roles **purely
positionally** over CoNLL mention structure + an inline surface passive heuristic. The parser modules
wake only behind a default-OFF flag (`role_route='wired'`, `predict_revise`, `predict_surprisal`,
`verb_subcat_gate`). So the parser's downstream value is **entirely latent** today — improving it moves
a live number only once the wired/graded path is turned on. *This is itself a fidelity gap: the brain
does position-DOMINANT + cue-OVERRIDE (Competition Model, Bates & MacWhinney); pure-positional with no
override is a degenerate placeholder.*

## ⚠️ MEASURED CORRECTION (2026-09-02, `exp_parser_through_real_organs_v1` + `exp_predarg_frontend_organ_v1`)
Running the improved parser THROUGH the real organs refined this map: the who-did-what **PATIENT-IDENTITY**
organs (`graded_role_assigner.hybrid_role_patient`, `relcl_resolver.resolve_patient`) are **HEAD-INDEPENDENT** --
they take `(toks,pos,v,cands)` and decide the patient from POSITION + VOICE + competition, NOT the parse heads
(they score 0.541/0.411 on QA/19c, already label-free, unmoved by the parser). The parser's HEADS are consumed by
`predicate_argument_frontend` (matrix-verb selection + PP/oblique roles), where the better parser DOES help
CI-sep (matrix-verb F1 +0.015, PP-role F1 +0.027). So the "head-attachment" need in the rows below belongs to
`predicate_argument_frontend`, NOT to the patient organs -- read the table with that correction.

## THE MAP — consumer × parse-property-needed × brain-fidelity × implication for the parser

| consumer | live? | parse property it needs | brain-fidelity (audit verdict) | implication for THIS problem |
|---|---|---|---|---|
| **graded_role_assigner** (who-did-what IDENTITY) | LIVE\* (wired) | head-attachment + VOICE | **PINNED-faithful**, assembly-wired (audit L232) | REAL need. Optimize head-attach + voice. |
| **predicate_argument_frontend** (event-semantic router: matrix-verb via root/coord heads + PP-attach for oblique roles) | LIVE\* (wired) | head-attachment (root/coord + PP), VOICE, oblique/PP roles | shallow predarg front-end ≈ brain's structure-building + role-binding pools (Matchin-Hickok 2020); **faithful but has a QUOTATIVE-INVERSION gap** (audit L968) | REAL need. Head-attachment is the single most load-bearing property. |
| **relcl_resolver / predict_revise** (filler-gap drop-fill) | LIVE\* (predict_revise) | VOICE + filler-gap patient + **argument RECALL** (fill dropped '?') | **PINNED-faithful** (Frazier & Flores d'Arcais; Stowe 1986; active-filler). Already recovers who-did-what +0.060 CI-sep (audit L79) | REAL need. RECALL (don't-drop-args) is load-bearing here — the N2 axis. |
| **verb_subcat** (does the verb take an object) | LIVE\* (verb_subcat_gate) | verb subcategorization (lemma-only) | **brain-foundational** (lexicalized argument structure); graded upgrade queued (audit L252) | REAL need (N9). Lemma-only; parser need is minimal. |
| **predictive_reader / predict_surprisal** (N400 forward prediction) | LIVE\* (predict_surprisal) | a CONFIDENCE signal; POS for nominal set | **PINNED-faithful** (predictive coding, Hale/Levy). Its OWN residual analysis: errors are STRUCTURAL, "the sole lever is a better parser" (audit L89) | REAL need. Motivates the whole problem. |
| **graded_competition** (maintained DISTRIBUTION over attachments) | off-path (built, PINNED) | the parser should EMIT a soft distribution / margin (N7) | **PINNED-faithful** (Bayesian posterior over parses, McClelland 2013) | REAL need, currently UNCONSUMED live = a WIRING gap. The parser SHOULD emit its margin so this organ can consume it. |
| **incremental_parser** (left-corner incremental builder) | off-path ISLAND | bounded incremental head-attachment; argument RECALL | **PINNED-faithful SHAPE** (Now-or-Never, Christiansen & Chater 2016) but precision-only when tried (+0.145 P bought with −0.093 R; NO role gain, audit L268) | The brain's SHAPE is incremental; but a 1-best incremental selector did not lift roles. The lever is attachment PRECISION + a maintained distribution, not the incremental control flow alone. |
| **candidate_generator / completeness_checker** (margin consumers) | off-path | head-attachment + margin + arg RECALL | semi-foundational (completeness = engineering QA over margin) | minor; margin need is real but only these off-path tools consume it today. |
| **arc_labeler** (adds dobj/nsubj LABELS to unlabeled arcs) | off-path (only reading_grounding_loop) | turns head-attachment into dep-relation LABELS | **LOW / OUR-INVENTION.** The brain binds thematic roles (agent/patient), it does NOT emit linguists' grammatical-relation labels; the live path recovers roles from head+preposition+voice WITHOUT labels ("dead weight on the live path") | ⚠️ Do NOT make dep-LABEL accuracy a first-class parser objective **unless** measurement shows the arc→spaCy gap is a LABEL gap (spaCy's role recovery uses dobj/nsubjpass). MEASURE label-vs-UAS contribution first. |
| **semantic_parser** (HD-bundle intent + role-slot) | off-path ISLAND (NEEDS_ADAPTER) | intent + per-role slot + confidence, over composed HD vectors | ⚠️ **OUR-INVENTION placeholder** — the intent+slot frame is the classical dialogue-NLU paradigm (Alexa/Siri), NOT a brain mechanism; no live caller | candidate FOLLOW-ON: re-found or retire; its "needs" do NOT constrain the sentence parser. |
| **typed_rule_parser** (tablestore TSV → relation/arg0/arg1) | off-path | KB relation LABEL + args (a TSV parser, not a sentence parser) | N/A — a FOUNDATION-BUILDING tool (offline KB ingest), not a runtime brain organ | not a sentence-parse consumer; out of scope. |

## WHAT THIS REFRAMES FOR THE MULTI-OBJECTIVE (the owner's point, made precise)
1. **The REAL brain-foundational needs to optimize:** head-attachment accuracy (drives role assignment,
   matrix-verb selection, PP/oblique roles), POS/lemma, VOICE, argument RECALL (predict-revise), verb
   subcat, **and a maintained confidence distribution** (graded_competition — currently unconsumed, a
   wiring gap the parser should enable by emitting its margin).
2. **Two "needs" in the brief's N-list trace to LOW-fidelity consumers and must be treated with
   suspicion, not chased blindly:**
   - **Explicit dep-relation LABELS (N-implicit)** — needed only by the off-path `arc_labeler`/
     `reading_grounding_loop`; the brain does not emit them. **MEASURE whether the arc→spaCy who-did-what
     gap is a UAS gap or a LABEL gap before deciding to build labeling.** (This is the crux experiment.)
   - **HD-bundle intent/slot parse (`semantic_parser`)** — an OUR-INVENTION placeholder; its needs must
     NOT distort the sentence parser. Flag as a follow-on to re-found.
3. **The confidence DISTRIBUTION (N7) is a REAL brain-faithful need that is currently unserved** because
   the parser's `margins` field is not consumed on any live path. A faithful parser emits a distribution
   (constraint-based, graded); wiring `margins`→`graded_competition` is in-scope value.

## CANDIDATE FOLLOW-ON PROBLEMS (adjacent-component evaluation, per the owner)
- **`semantic_parser` is a classical intent/slot placeholder** (OUR-INVENTION, island) → re-found on a
  brain-faithful role-binding basis or retire.
- **The default reader is pure-positional (no cue-override)** → make the graded wired role path
  default-on (Competition Model faithful) — the parser's value is latent until then.
- **arc_labeler / explicit grammatical labels** → evaluate whether the substrate needs labels at all, or
  whether head+preposition+voice role recovery is the faithful (label-free) path.
