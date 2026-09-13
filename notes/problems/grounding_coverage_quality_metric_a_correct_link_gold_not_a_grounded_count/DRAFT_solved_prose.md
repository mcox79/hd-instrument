# DRAFT prose for SOLVED.md (assembled into SOLVED.md once the full FLAT-on-count numbers land)

## Scope recap (from the brief's STATUS UPDATE 2026-09-11)
The CORE sense-assignment quality instrument already exists (strategy-landed):
`experiments/exp_board_grounding_coverage_quality_v1.py` -> board arm `grounding_coverage_quality`, which shows
(a) MOVES-on-quality and (c) twin-at-chance. Solver scope narrowed to three items:
- (a) REFERENT-LINK half (grounded word -> right discourse ENTITY, GUM coref gold).
- (b) explicit FLAT-on-count demonstration (inflate n_grounded without changing correctness; quality dim flat).
- (c) POWER (raise the scorable population; full-population CI).

## Item (a): the referent-link-to-entity half is a RIGOROUS LOCATED NEGATIVE for THIS loop (checklist-4 pass)
ENUMERATION (not a keyword search; full-file grep + import-trace on the three loop files):
- `hdlab/reading_grounding_loop.py` (3022 lines) contains ZERO occurrences of entity / coref / mention / pronoun /
  antecedent. It makes exactly two kinds of grounding decision:
  1. lexical SENSE-ASSIGNMENT: `canonicalize` / `canonicalize_fast` / `FusedSenseRanker.rank` -- binds a WORD/LEMMA
     to a word-sense ANCHOR by nearest-neighbour over ConceptSpace, SDT-gated. word -> word-sense, never
     mention -> discourse entity.
  2. perceptual VISUAL grounding: `FusedSenseRanker.use_referent` -> `hdlab.sensorimotor_spoke.referent_vector` =
     a per-WORD DINOv2 multi-exemplar centroid over THINGS object photos. This "referent" is a LEXICAL/PERCEPTUAL
     referent (word -> photo centroid), NOT a discourse-entity referent. It votes inside the SAME anchor-field
     argmax as the grounded + SEQ channels (fused sense-assignment), not entity linking.
- `hdlab/gap_driven_reader.py` and `hdlab/substrate.py` import only the loop's own functions; neither imports any
  coref/entity organ.
- A coreference organ EXISTS but is a STRUCTURALLY SEPARATE, unwired organ: `hdlab/coreference_resolver.py`
  (`build_mention_stream`, `run_match_or_allocate`, `run_strict_cb`, `run_principle_b(_deixis)`, `bcubed`,
  `mention_link_wrong`). `hdlab/substrate.py` slot E3 records its status verbatim: it "reads passage['entities'] --
  a GOLD mention inventory ... decides linking GIVEN the mentions, so it does not transfer to raw prose" =>
  NEEDS_ADAPTER, and its own prior score (0.7193 = 41/57 on McGuffey gold-mention role) is flagged NOT
  CI-separated at n=57. Other entity organs on disk (entity_resolver, world_state_entity_binding,
  online_entity_cluster, referent_per_np, ...) are likewise not called by the loop.

CONCLUSION (numbered located negative): the reading-grounding loop makes NO mention->entity / pronoun->antecedent
decision, so there is NO decision variable in THIS loop for a GUM/LitBank coref gold to score. GUM coref gold IS on
disk and parseable (301 GUM .conllu files carry Universal-Anaphora coref in MISC col 10, `# global.Entity = GRP`,
`(N` / `N)` bracket clusters; 25 LitBank `*_brat.conll` in CoNLL-2012 bracket format) -- the gold is affordable; the
DECISION is absent. Building a coref-quality instrument would require scoring `hdlab/coreference_resolver.py`
instead, which (i) is a different organ (out of this brief's "reuse the grounding loop" scope), and (ii) is
gold-mention-dependent (NEEDS_ADAPTER: it cannot consume the loop's raw sentence stream without a new mention
detector), so it is not measurable end-to-end on the reader's own read yet. ROUTE: the referent-link-to-entity
instrument belongs to the coref line (`coreference_resolver` + a raw-prose mention adapter), filed as the named
follow-on; it is NOT a defect in the grounding-quality instrument. This is exactly the brief's blessed
"which grounding decision has no affordable independent gold, with the reason" -- here it is inverted and sharper:
the gold is affordable, the DECISION does not exist in the measured organ.

## Item (b): the FLAT-on-count demonstration -- mechanism
The loop's grounding gate accepts a link iff the SDT familiarity standout `z_top >= criterion(n_cand)`, where
`criterion = (1-FA)` quantile of `z_top` on an info-free iid null (Yonelinas 2002 recognition SDT;
`FusedSenseRanker.criterion`). `FA = SDT_FALSE_ALARM` is a SWEPT precision knob. Raising FA LOWERS the criterion ->
more links clear the gate -> `n_grounded` rises. But FA never enters the RANKING (the argsort over the fused
convergent-cue combination) or `z_top` -- so link CORRECTNESS is untouched. Proven on the LIVE ranker (witness V1):
the ranked `order` and `z_top` are byte-identical across FA=0.01 vs FA=0.40; only the accept verdict differs, and
the FA_hi accepted set is a superset of FA_lo. This IS the mechanism that makes the count quality-blind.

THE 2x2 (the complete separation the bar asks for):
- QUALITY dim (correct-link MRR@0.5 coverage) MOVES CI-separated on a real quality change (incumbent bag-cosine ->
  FUSED convergent-cue read): [FILL FUSED vs INCUMBENT diff + CI from full run].
- QUALITY dim is FLAT on the count-only change (FA 0.01->0.40): the ranking-based MRR is EXACTLY FA-invariant
  (diff = 0; not an underpowered null -- an identity by construction, proven by V1).
- COUNT dim (n accepted over the grounding-target population) MOVES CI-separated UP on the same FA change:
  [FILL frac-accepted diff + CI + n_lo->n_hi from full run].
- The count grows FASTER than the correct count: correct-rate-among-accepted does not rise as FA rises
  (V3) -- more links, not more correct.
- Twin (scrambled-link, evidence from another query) at chance: [FILL twin MRR].

## The gold is a HUMAN-COMPETENCE truth signal, not a machine/taxonomy (owner question 2026-09-12)
The 100%-BF requirement is on the MECHANISM AT INFERENCE (the grounding loop -- already 100% BF / parser-free per
the prior FULL_CHAIN_BF_AUDIT), not on the measuring stick. The gold never enters inference; it is the exam answer
key. The requirement on a gold is that it be an INDEPENDENT, non-circular truth signal reflecting what a competent
human reader comprehends ("change the gold to the ability").
- SimLex-999 / SimVerb-3500 are AGGREGATED HUMAN BEHAVIORAL similarity judgments (SimLex designed to capture
  genuine synonymy, penalizing mere association). That is a direct measurement of the human semantic system's own
  verdict on meaning-sameness -- the brain's answer key -- and it is WordNet-INDEPENDENT (a control the prior SOLVED
  relied on). This is brain-foundational as a GOLD.
- WordNet is human lexicographic KNOWLEDGE (hand-built ontology); admissible as a static offline asset, but NOT used
  as gold here -- to avoid taxonomic circularity and to keep the gold WordNet-independent (the representation chain
  is deliberately WordNet-free). If more power is needed, MEN (Bruni-Tran-Baroni human behavioral ratings) is the
  next gold, not WordNet.
- The metric COMPUTATION is itself the comprehension-test logic (match the resolved meaning to the human key);
  it sweeps nothing that changes truth.

## Phase-diagram framing (owner reminder 2026-09-12)
The instrument's operating point is FREE to SWEEP, not adopted: the accept threshold (FA), the coverage stratum
(the 50% MRR-frontier point), and the gold subset (SimLex/SimVerb high-sim) are all swept. The FA sweep IS a
phase-diagram sweep of the accept-criterion operating point -- and it is precisely what exposes the count's
quality-blindness: the count number is a function of the operating point, the quality metric is (for the ranking)
invariant to it.

## Full-stack upstream (owner directive 2026-09-12)
The upstream component the instrument scores -- the reading-grounding loop's fused sense-assignment read -- was made
100% brain-foundational (parser-free directional-SEQ + grounded-ATL + SDT gate) and PROVEN to lift coverage QUALITY
CI-separated by a REAL brain-foundational change (grow-by-reading to 1M+ modern lines: +0.16 -> +0.26 CI-sep,
monotone, twin losing) in the prior owner-DONE pri-5. This instrument is what makes that upstream gain SCORABLE:
the count could not see it; the quality dim does, and (item b) the count cannot be gamed past it. No downstream
consumer regresses because the instrument is measurement-only (a board dimension OUT of the headline aggregate) --
it changes no organ.
