# Coreference / entity-tracking — brain-led 5-angle drill (2026-07-19)

Research drill, no atoms banked, no routing files (USER-locked discipline). Deflated per
[[feedback-lit-scan-calibration-penalty]]: novel-synthesis P capped at 0.50; established-lit
findings are NOT deflated (they're textbook/replicated results, not our synthesis) but are
flagged for confidence per-source. Composes with, does not re-derive: the coref HARD_FAIL
(atom 29341), head-finder CHAIN_GRADE (atom 29342), quotative CHAIN_GRADE (atom 29345), and
Step-1's pronoun-invisible finding (atom 29353, `research_fork_c_compounding_end_to_end_substrate_loop_2026-07-19.md`).

## HEADLINE

Coreference is now **conditionally viable, not unconditionally viable** — the upstream candidate-
generation bug that caused the HARD_FAIL is real and partly fixed, but the lit scan surfaces a
SECOND, independent reason the prior lever hurt: coref was almost certainly applied **ungated**
(every pronoun forced to a resolution) in a regime (intersentential/across-sentence) where even
the best rule-based, treebank-free systems in the literature are honestly only ~74% accurate —
so "broke 16 for 1 fix" is closer to the EXPECTED behavior of an ungated resolver at that accuracy,
not a mysterious defect. The fix implied by every one of the 5 angles is the SAME fix: **coref
must be a margin-gated cue-based retrieval that abstains under low confidence**, built first on
the easy (intrasentential, high-margin) sub-case where humans and rule-systems both hit 86-89%,
not the hard (intersentential) sub-case where they hit 65-74%. The brain shares this bound (children
take until ~10-11 to reliably do the hard cases; adults still err under cue conflict) — this is
a genuine SAME-LIMIT on raw accuracy, but the RETRIEVAL MECHANISM itself (cue-based, content-
addressable, parallel constraint satisfaction under similarity-interference) is a strong,
independently-published architectural match to our HD cleanup-memory unbind — that part is a
NATIVE FIT, not a same-limit. Verdict: build it, gated, starting from the intrasentential slice.

## Ranked verdict (viability ladder)

1. **Mechanism-level fit: STRONG (established analogy, not our invention).** Cue-based/content-
   addressable retrieval (Lewis & Vasishth 2005; McElree SAT work) is the dominant model of how
   humans access antecedents — parallel cue-match against active memory, not serial search — and
   the literature already draws (Lebiere & Anderson 1993; more recent computational-neuro
   syntheses) an explicit architectural line from this to Hopfield-style associative/pattern-
   completion memory. Our cleanup-memory unbind is exactly this operation. Confidence: high that
   the *mechanism class* matches; medium that this has been *directly validated on pronouns
   specifically* (see angle 2 caveat below) — most of the strongest evidence is from filler-gap/
   agreement dependencies and generalized to anaphora by analogy, with only a thinner direct-
   pronoun literature (Foraker & McElree 2007).
2. **Candidate-generation fix: REAL, but proven NARROW so far.** Head-finder (29342) gives clean
   NP-head candidates in general; quotative (29345) is a genuine existence-proof that coref-shaped
   resolution helps at the RIGHT structural layer (speaker attribution). But VET already caught
   the over-read that head-finder mechanically UNLOCKED quotative — the two were INDEPENDENT, not
   enabling. That caution applies again here: do NOT assume "candidate-gen fixed" transfers
   automatically to general pronoun coref. It removes ONE known failure mode (non-entity
   candidates) but the lit scan's honest ceiling numbers (below) say a SECOND failure mode —
   applying resolution ungated in the hard sub-case — is independently sufficient to reproduce
   the HARD_FAIL even with perfect candidates. Confidence this alone fixes it: LOW on its own;
   MEDIUM combined with gating (see design below).
3. **Accuracy ceiling: a genuine SAME-LIMIT, brain-shared, not an engineering shortfall.** Rule-
   based/treebank-free coref (Hobbs 1978; Lappin & Leass 1994 RAP) tops out around 86-89% on
   intrasentential pronouns but only 74% on intersentential ones — and children take until
   ~10-11 years old to be adult-reliable on exactly the harder, comparative (reference-set)
   judgment, not the grammar itself (Chien & Wexler 1990; Reinhart's processing-load account).
   No brain-faithful or rule-based approach gets this for free. Accept the ceiling; design around
   it (gate, don't force).
4. **Overall: VIABLE AS A GATED, STAGED BUILD.** Not viable as "coref resolves every pronoun."
   Viable as "coref resolves the high-margin, intrasentential/local-window subset and abstains
   elsewhere," which is both (a) the sub-case with the best published accuracy and (b) exactly
   the sub-case Centering Theory says is cheapest/most reliable for humans too (CONTINUE
   transitions). Deflated novel-synthesis P = **0.40** (capped by policy at 0.50; deflated further
   because the "components are independent, don't assume transfer" lesson from head-finder/
   quotative applies directly and hasn't been re-tested here).

## 5-angle findings (credited, confidence-flagged)

**1. Psycholinguistics (cue ordering + failure conditions).** Ariel's Accessibility Theory and
Gundel/Hedberg/Zacharski's Givenness Hierarchy: pronouns mark HIGH-accessibility antecedents —
scalar/implicational, well-established. Centering Theory (Grosz, Joshi & Weinstein 1995): each
utterance has a ranked Cf list (subject > object > oblique — grammatical-role hierarchy) and a
single Cb; transition preference CONTINUE > RETAIN > SMOOTH-SHIFT > ROUGH-SHIFT (cost increases
down this list) — well-established, though the RT-cost claim is more theory-internal than always
directly reading-time-validated. Implicit causality (Garvey & Caramazza 1974 onward): verb
semantics (praise=NP1-biasing vs admire=NP2-biasing) pre-emptively shift pronoun expectations,
strong and heavily replicated, and can OVERRIDE structural cues. Gender/number agreement:
strong early-acting cue but LEAKY under semantic interference (contested — not a strict filter).
Ranked dominance (synthesis, disagreement noted): agreement (near-filter, leaky) > implicit
causality (pre-emptive, can override structure) > grammatical role/subjecthood (Cf rank) >
recency > discourse-coherence-relation (modulates all others). **Humans err exactly where cues
conflict** (subjecthood vs recency vs implicit-causality pointing different directions), not
where any one cue is simply weak — and reanalysis after garden-path pronoun misassignment often
leaves residue (doesn't fully erase the earlier wrong binding).

**2. Neuro/memory (cue-based retrieval = cleanup-memory).** Lewis & Vasishth (2005, ACT-R) and
McElree's speed-accuracy-tradeoff work (flat retrieval-speed across dependency distance) are the
field's canonical evidence for PARALLEL CONTENT-ADDRESSABLE retrieval, not serial search — high
confidence for dependency resolution generally. Similarity-based interference (Van Dyke &
McElree; Jäger, Engelmann & Vasishth 2017 meta-analysis): retrieval slows/misfires as MORE
candidates share retrieval-relevant features (gender/number/animacy/role) — a crosstalk-style
degradation profile, not combinatorial search cost, directly analogous to HD superposition
crosstalk. Cues combine via WEIGHTED PARALLEL CONSTRAINT SATISFACTION (individual-differences
work shows people vary in relative cue weight), not strict filter-then-rank — medium-high
confidence. Direct architectural bridge to Hopfield/associative memory has been explicitly drawn
in the cog-sci literature (Lebiere & Anderson 1993; more recent ACT-R/neurobiology syntheses) —
medium confidence, a real but cross-disciplinary analogy. **Honest caveat (own it): the strongest
retrieval evidence is from filler-gap/agreement dependencies, not pronouns specifically; direct
pronoun evidence (Foraker & McElree 2007) exists and IS consistent with the same architecture,
but is thinner** — treat "pronoun resolution = cleanup query" as a well-supported extrapolation,
not a directly-proven identity.

**3. Acquisition (why some baseline fragility is structurally expected).** DPBE (Chien & Wexler
1990): children over-accept local coreference on pronouns until ~10-11 years old, while
reflexives (Principle A) are adult-like by ~3-4 — a large grammar-early/pragmatics-late gap,
well-replicated. Consensus (Reinhart's reference-set computation / Conroy et al.'s Rule-I
pragmatic-competition account): the deficit is NOT missing grammar, it's a COMPARATIVE
computation — checking the chosen structure against an alternative (e.g., would a reflexive have
worked here?) — that is processing/capacity-costly and matures late. A competing account (PMC
2021) ties the residual errors to Theory-of-Mind/inhibitory control rather than raw working
memory. Either way: **pronoun-antecedent judgment is the single costliest step of reference
resolution even in a fully grammatical system** — some baseline error rate is a real
computational cost, not purely an engineering gap to be closed to zero.

**4. Computational (honest treebank-free ceiling).** Hobbs' naive algorithm (1978): tree-search +
agreement filtering, 88% on his own restricted set (inflated by many single-candidate cases);
broader replications (Charniak, Hale & Ge 1998) found 65.3% alone, 75.7% with gender/animacy
features — genre-dependent (a Portuguese replication found 40-51% outside clean news text).
Lappin & Leass (1994) RAP: hand-set salience weights (recency, subjecthood, existential/
accusative emphasis, head-noun repetition) — no learned component — reach 86% overall, but
**89% intrasentential vs only 74% intersentential**: the SAME split our within-document carry
problem sits on. Neural mention-ranking trained on OntoNotes coreference chains reaches ~68-70
CoNLL F1 vs ~49.5 F1 for Stanford's deterministic rule baseline on the harder full-clustering
metric — a real ~20pt gap that a supervised treebank buys, which we do not have and are not
using (glass-box discipline). A 2022 weak-supervision distillation of rule outputs (no gold
coref labels) bought only +3.7 F1 over the rule baseline — confirming a real but SMALL headroom
from learning-without-labels alone. **Honest no-treebank ceiling: ~70-85% pronoun accuracy on
well-behaved text, 60-75% on harder/intersentential cases; biggest failure mode = tied candidates
needing world knowledge (Winograd-schema class) and long-distance/intersentential antecedents.**

**5. Structural verdict — synthesis (this drill's own contribution, capped P=0.40).** See Ranked
verdict above. The core move: separate the MECHANISM question (does a cue-based cleanup-memory
query correctly model coref? — yes, strong lit support) from the CEILING question (will it be
accurate enough to help rather than hurt if applied everywhere? — no, both brain and rule-based
systems say the hard cases are genuinely ~65-75%, not near-ceiling) from the DEPLOYMENT question
(so gate it to the reliable subset and let it abstain elsewhere — this is the actual fix). The
prior HARD_FAIL's "broke 16 for 1 fix" pattern is fully consistent with an UNGATED resolver
running partly in the ~65-75%-accurate intersentential regime: at that error rate, forcing a
resolution on every pronoun candidate will produce enough wrong links to swamp a small number of
genuine fixes, independent of whether the candidate list itself was clean.

## Design: human cue -> HD operation mapping

| Human cue (angle 1/2 evidence) | HD-substrate operation |
|---|---|
| Gender/number/animacy agreement (strong early filter, leaky) | Hard pre-filter on candidate feature vectors before cleanup query (not a bind-time constraint — a pre-query mask) |
| Grammatical role / Cf-rank (subject preference, Centering) | A recency-decayed, role-weighted salience score bundled into the candidate's key vector (already the shape of the fork-C note's Tier-2 role/event carry) |
| Implicit causality (verb-semantic pre-bias) | A verb-conditioned bias term added to the query vector BEFORE cleanup match (a learned/lexical addend, not structural) |
| Recency / distance | Decay weighting on candidate activation, consistent with Centering's LOCAL window (current + immediately preceding utterance's Cb/Cf list) — NOT the whole document |
| Parallel weighted constraint satisfaction (not filter-then-rank) | Single cosine cleanup-memory query against a SMALL local candidate bundle (all cues folded into one key vector), matching McElree's parallel-not-serial signature |
| Similarity-based interference (crosstalk under cue-overlap) | Expected, not a bug: matches HD cosine-crosstalk when two candidates share gender/number/role — the margin between top-1 and top-2 IS the interference signal |
| Reference-set comparison being the late-maturing, costly step (acquisition angle) | A MARGIN GATE: only commit a resolution when top-1 cosine clears top-2 by a decisive threshold; below threshold, ABSTAIN (leave pronoun unresolved) rather than force |

## First buildable component

**Margin-gated, LOCAL-WINDOW (intrasentential + immediately-preceding-sentence) pronoun-to-
antecedent cleanup query**, restricted to the Lappin-Leass/Centering high-reliability sub-case
(the 86-89% regime in the literature), explicitly NOT the full-document/intersentential case
(the 65-74% regime the prior lever likely ran into). Concretely:
1. Candidate pool = NP heads proposed by the now-fixed head-finder (29342), filtered to the
   current clause + immediately preceding clause/sentence (Centering's Cb/Cf local window), hard-
   filtered by gender/number/animacy.
2. Each candidate's key vector = bind(head-noun-code, role-weight-by-Cf-rank, recency-decay).
3. Query vector = pronoun's agreement features + (if available) the governing verb's implicit-
   causality bias term.
4. Cleanup-memory cosine match against the local candidate bundle; commit resolution ONLY if
   top-1 minus top-2 margin clears a pre-registered threshold; otherwise ABSTAIN (identical to
   current no-coref behavior on that token — this is the change from the prior lever, which
   evidently forced resolutions).
5. On commit, emit BOTH (a) the resolved entity for who-did-what precision scoring, and (b) the
   coref-resolved entity code fed into the fork-C Tier-2 FHRR carry (Step-1's untested lever,
   atom 29353) — this is the SAME resolution serving both consumers named in the task, not two
   separate builds.

## Cheap decisive test / design-gated can-fail

Real baseline = current reader (0.557, no coref). One variable changes: gated intrasentential-
only coref on/off. Measure BOTH consumers named in the task (precision AND the entity-carry),
per [[feedback-experiment-design-gate-can-fail-real-baseline-difficulty-on]].

**Prediction A (precision, must not repeat the HARD_FAIL).** P=0.40 (deflated, capped).
HARD-PASS: agent-lens/who-did-what precision on the pronoun subset improves, AND the count of
newly-broken previously-correct extractions is <= the count of newly-fixed extractions (a hard
break-budget — the prior failure was 16-broken-for-1-fixed; this time it must not be net-negative
at all, ideally near-zero breakage given the abstain gate). HARD-FAIL: net breakage still exceeds
net fixes even restricted to the intrasentential/local-window high-reliability subset with
abstention — this would mean the bound is NOT (only) upstream candidate-gen or (only) ungated
application; something deeper in the scoring/margin mechanism itself is broken, and the honest
conclusion becomes "brain-faithful coref shares the accuracy ceiling but our margin-gate
implementation can't isolate the reliable subset" — a genuine, informative negative.

**Prediction B (entity-carry, tests Step-1's specific open lever).** P=0.35 (deflated).
HARD-PASS: feeding gated coref-resolved entity codes into the Tier-2 FHRR carry produces
measurable non-zero same-entity continuity capture across a pronoun-antecedent pair (directly
reversing Step-1's "pronoun-invisible" finding on the subset where coref commits). HARD-FAIL:
even committed (high-margin, presumably-correct) coref resolutions fail to change carry behavior
— which would mean the carry's blindness to pronoun-mediated continuity is NOT solely a missing-
coref-signal problem but something about how the carry integrates entity codes (a DIFFERENT,
also genuinely informative negative — echoes the "components can be independent, not enabling"
lesson from head-finder/quotative, this time for coref-vs-carry).

**Cross-check (both-ways can-fail, explicit).** If Prediction A passes but B fails: coref is a
real, standalone precision win but does NOT unlock compounding — a valuable, bounded result, and
compounding investment should stay on the cross-document consolidation thread per the fork-C
note rather than the within-document coref-carry path. If A fails but B passes: coref helps the
carry but the precision-scoring integration itself has a bug independent of the resolution
quality — worth a narrower re-test before concluding coref itself is unviable. If both fail:
the accuracy-ceiling same-limit (angle 3+4) dominates even in the easiest sub-case, and the
honest verdict flips to "brain-faithful coref needs a treebank-scale weak-supervision signal
(the 2022 rule-distillation precedent, +3.7 F1) before it clears break-even" — a real, bounded
scope-expansion candidate for a future drill, not a dead end.

## Cross-thread synthesis

Composes directly with three same-day/adjacent notes without re-deriving them: the coref
HARD_FAIL (atom 29341) diagnosed an upstream candidate-gen cause; this drill adds a SECOND,
independent, lit-supported cause (ungated application in the honest-ceiling-limited
intersentential regime) that would reproduce the same symptom even with clean candidates — so
"candidate-gen is fixed" is necessary but was never sufficient on its own, consistent with the
VET's caution (head-finder and quotative turned out INDEPENDENT, not enabling) that this drill
explicitly does not repeat by assuming the same for coref. The design directly serves Step-1's
named open lever (atom 29353, pronoun-invisible carry, `research_fork_c_compounding_end_to_end_substrate_loop_2026-07-19.md`)
by construction — the SAME gated resolution feeds both consumers, rather than building coref
twice. The cleanup-memory framing is directly grounded in the measured envelope in
`vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md` (cleanup is a hard step not
graceful degradation; modern/iterative cleanup dominates classical Hopfield; operate well inside
the low-crosstalk regime) — the margin-gate is exactly the "operate well inside the reliable
regime, don't push to the cliff" discipline that note already recommends for other cleanup uses.

## Substrate-product implications

A gated, local-window coref component is a genuine product capability, not a publication result:
it directly improves who-did-what precision (a user-facing correctness metric for reading
comprehension) on pronoun-bearing sentences, and it is the FIRST concrete candidate for making
the reader's understanding of a document compound as it reads further (entity continuity across
sentences) rather than treating each sentence in isolation — the core "gets smarter as it reads"
story the product needs. The explicit abstain-when-uncertain design also gives an honest,
inspectable confidence signal (the top1/top2 margin) that a glass-box product can surface to a
user or an auditor ("resolved with high confidence" vs "left ambiguous"), which a black-box
neural coreference system cannot offer as cleanly.

## Citations (verified count: 19 distinct sources across 4 sub-agent lit scans)

Psycholinguistics (angle 1): Grosz, Joshi & Weinstein 1995 (Centering); Walker, Joshi & Prince
1998; a Reformulation of Rule 2 of Centering Theory; Ariel 1990 Accessibility (+ Arnold 1998
revision); Gundel, Hedberg & Zacharski 1993 Givenness Hierarchy; Garvey & Caramazza 1974 +
Hartshorne implicit-causality synthesis; Van Berkum et al. implicit-causality ERP; role-noun
gender-mismatch (Frontiers 2015); lingering garden-path misinterpretation (Christianson et al.);
prominence-cues-in-children (Journal of Child Language).

Neuro/memory (angle 2): Lewis & Vasishth 2005; McElree SAT direct-access retrieval (PMC); Jäger,
Engelmann & Vasishth 2017 meta-analysis; Villata et al. encoding/retrieval interference; Foraker
& McElree 2007 (pronoun-specific SAT); Lebiere & Anderson 1993 (ACT-R + Hopfield); 2023 ACT-R
declarative-memory neurobiology synthesis.

Acquisition (angle 3): Chien & Wexler 1990; Reinhart's reference-set computation account; Conroy
et al. Rule-I pragmatic-competition; PMC 2021 (Theory-of-Mind/inhibition, not working memory);
Tomasello usage-based acquisition synthesis.

Computational (angle 4): Hobbs 1978; Charniak, Hale & Ge 1998 replication; Santos & Carvalho 2007
(Portuguese, genre-dependence); Lappin & Leass 1994 (RAP); Lee et al. 2017 end-to-end neural
coreference; Stanford CoreNLP deterministic rule-based baseline (OntoNotes F1); 2022 ACL*SEM
weak-supervision rule-distillation paper.

Full URLs preserved in the four sub-agent transcripts (not re-listed here to keep this note
scannable); available on request via re-dispatch of the same lit-scan agents if a citation needs
direct verification.
