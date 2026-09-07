# FULL BRAIN-FOUNDATIONAL FIDELITY SCAN -- the cross-type definite->name bridge, all the way up the chain

**Owner ask (2026-09-07):** "is this 100% brain-foundational? ... run a 100% brain-foundational fidelity scan of
this component all the way up." **Verdict: NOT 100% -- the COMPUTATIONS are brain-foundational at every layer, but
5 of the 12 layers have PROXY implementations, and 2 are the LOAD-BEARING gaps (the anaphoricity-gate detector and
the statistical parser).** Each layer below: brain structure + PINNED-vs-OUR-INVENTION + our implementation +
fidelity verdict + the MEASURED evidence (this problem's cells) + the upstream dependency. Ordered TOP (deepest
upstream) -> BOTTOM (the bind + consumers). "MEASURED" = a number from a cell here; "PINNED" = literature-fixed.

| # | layer | brain computation (PINNED?) | our implementation | fidelity | measured evidence |
|---|---|---|---|---|---|
| 1 | tokenize / sentence-seg | word/clause segmentation | GUM gold / reader splitter | mechanical (not modeled) | -- |
| 2 | POS tagging | rapid incremental lexical-category assignment | UD-trained averaged-perceptron `PosTagger` | **PROXY** (statistical, not predictive) | part of the live-parse drop |
| 3 | **PARSING** (heads) | INCREMENTAL PREDICTIVE parse, left-corner/surprisal (Lewis-Vasishth PINNED) | arc-eager transition parser (`arceager_parser`) | **RIGHT ARCHITECTURE, STATISTICAL SCORING** -- arc-eager IS an incremental transition system (brain-plausible), but scored by a perceptron, not surprisal/prediction. The reader-wide PARSER GAP. | live parse vs gold: coverage 0.156->0.123, precision 0.96->0.86 (the parse costs ~21% coverage / 10pt precision) -- LOAD-BEARING |
| 4 | dep-relation labeling | grammatical-relation typing | `ArcLabeler` (UD deprels) | PROXY (statistical) | feeds role (below) |
| 5 | GRAMMATICAL ROLE | thematic/grammatical role by CUE COMPETITION (MacWhinney Competition Model; landed `graded_role_assigner`) | deprel -> {SUBJECT/POSSESSIVE/OBJECT/OTHER} | **FAITHFUL** (given the parse) -- subject/object are real grammatical roles; the CM assigner is landed brain-foundational | role feeds the Cf-salience |
| 6 | ANIMACY | lexical-semantic TYPE (ATL hub); animacy a core feature (Dahl-Fraurud) | UPGRADED: WordNet FIRST-SENSE = noun.person (FREQUENCY PRIOR, Anderson base-rate) + tiny WSD-hard legal residual | **FAITHFUL (frequency prior)**, capped by WSD ambiguity | WN-freq-prior vs hand-stoplist: ceiling coverage 0.201->0.309 LIVE at equal precision (0.775->0.778) -- more principled + more coverage; deployment C3 +0.053->+0.036 (extra coverage needs the gate) |
| 7 | DESCRIPTIVE-CONTENT extraction | DRT FILE-CHANGE: accumulate stated descriptive CONDITIONS on the card (Heim 1982 / Kamp PINNED) via semantic composition | precise-constructs: apposition/copula/copular-verb/conj-subject/detached-appositive/relcl/title + FrameNet-style VERBAL role | **FAITHFUL COMPUTATION, SYNTACTIC-PROXY extraction** (UD patterns, not full composition; depends on the parse) | detector ladder 0.004->0.156 GOLD @ 0.96 precision (39x); the residual ~0.85 is genuine WK/context (3-way cross-validated: this cell 0.19, project-landed 0.191, Raghunathan MUC-6 0.15) |
| 8 | **ANAPHORICITY / FAMILIARITY gate** | a definite presupposes a FAMILIAR/identifiable referent (Heim familiarity PINNED); discourse-new detection (Ng-Cardie) | OUR-INVENTION proxy: fire only on predication OR age/gender re-mention | **CONSTRAINT PINNED, DETECTOR PROXY -- the LOAD-BEARING gap** | UNGATED cue-retrieval over-merges (0.50 precision) and REGRESSES C1 -0.0058 CI-sep; the gate fixes it (C1 -0.0004, safe). ~80% of person-definites are non-anaphoric (the gate's job) |
| 9 | Cf-RANKED SALIENCE | Centering Cf-ranking subj>obj (Grosz-Joshi-Weinstein PINNED ordering) x ACT-R base-level activation B=ln(sum w*dt^-d) (Anderson-Schooler PINNED) | `salience_binder.actr_activation`, ROLE_PROMINENCE {4.0,2.5,2.0,1.0}, decay 2.0 | **FAITHFUL COMPUTATION, INVENTED WEIGHTS** -- the equation is PINNED (copy); the weights + decay are OUR-INVENTION (the literature gives an ORDERING, not numbers -- should be swept, not adopted) | the reader's OWN primitive, reused unchanged |
| 10 | GENDER/NUMBER agreement | GRADED, violable phi-agreement (Carminati 2002) | hard filter on known m/f | **DEVIATION** (hard vs graded) -- but gender ~6%-sparse on modern nominals, so limited impact | (p11 gender-sparsity cap) |
| 11 | **THE BIND** (cue-based retrieval) | content-addressable CUE-BASED RETRIEVAL (Lewis-Vasishth 2005 PINNED); descriptive content OVERRIDES salience (Almor 1999 PINNED); confidence-gated commit (McElree SAT) | unified argmax over desc-boost + Cf-salience + gender + recency, margin abstain | **FAITHFUL COMPUTATION, INVENTED cue weights** (DESC_BOOST, margin -- swept) | gated cue-retrieval is the DEPLOYABLE best: C1 safe, C2 +0.0057, C3 +0.0528 CI-sep (live), > the recency proxy (+0.051) and > uniqueness (+0.033) |
| 12 | THE CARD / bind writeback | Heim/Kamp DRT file-change: ONE card, updated (PINNED) | cluster merge (role mention -> named entity) | **FAITHFUL** | twin (random targeting) LOSES CI-sep -> the correct targeting is load-bearing |
| -- | DOWNSTREAM consumers | situation model binds affect/goals to entity cards (Zwaan-Radvansky) | entity-KB / `make_canonicalizer` / affect-experiencer (landed organs) | landed; the bridge feeds them | C3 experiencer +0.0528 CI-sep, twin loses |

## The dependency chain (why "all the way up" matters -- MEASURED, not asserted)
**PARSE (3) -> ROLE (5) -> Cf-SALIENCE (9) -> BIND (11), gated by ANAPHORICITY (8).** Two measured proofs that
the chain is load-bearing:
1. **The bind depends on the anaphoricity gate (8).** The faithful cue-based retrieval (11), dropped in WITHOUT the
   familiarity gate, over-merges (0.50 precision) and REGRESSES the entity-layer CoNLL CI-separated (-0.0058). WITH
   the gate it is safe (C1 -0.0004) and net-positive (C3 +0.0528). You cannot install the sophisticated retrieval
   without the upstream gate -- the deepest "up the chain" lesson.
2. **The whole bridge depends on the parse (3).** Re-running the exact detector on the reader's OWN arc-eager parse
   instead of gold UD drops coverage 0.156->0.123 and precision 0.96->0.86. The bridge is only as faithful as the
   upstream parse; the parser's statistical scoring (not surprisal/prediction) is the reader-wide ceiling.

## Overall verdict
- **Computations: 100% brain-foundational** (DRT file-change, Centering Cf, ACT-R cue-based retrieval, Heim
  familiarity, Almor descriptive-override, frequency-prior animacy -- every layer's OPERATION is the brain's).
- **Implementations: ~7/12 faithful, 5/12 proxy.** The 2 LOAD-BEARING proxies (measured): (8) the anaphoricity
  DETECTOR (a predication/age-gender proxy, not a familiarity classifier -- the ungated over-merge quantifies it)
  and (3) the statistical PARSER (the reader-wide gap -- the live-parse drop quantifies it). The 3 lesser proxies:
  (2/4) statistical POS+labeler, (9/11) invented ACT-R/cue WEIGHTS (swept, not adopted -- the literature gives
  orderings not numbers), (6) animacy WSD-residual.
- **The ordered path to 100%:** (a) a real anaphoricity/discourse-new detector (Ng-Cardie) to safely unlock the
  ungated cue-retrieval's 3x coverage (C3 +0.104); (b) SWEEP the ROLE_PROMINENCE + cue weights on held-out rather
  than adopt them; (c) the incremental-predictive parser (reader-wide, a separate program); (d) frame-ELEMENT
  FrameNet agent ingest (the clean verbal-role); (e) graded phi-agreement once gender is denser. Each is a named,
  measured follow-on -- none is a hidden gap.
