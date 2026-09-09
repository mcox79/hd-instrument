# Per-story causal-network structure learner -- the recurrent loop's structural core, built + tested. LOCATED NEGATIVE (11th triangulation)

**problem:** chain_multi_step_plans_and_scripts_for_the_generative_world_model | **date:** 2026-09-08
**cell:** experiments/exp_multistep_causal_network_v1.py | **gold:** TellMeWhy non-adjacent, n=256
**research:** notes/research_narrative_causal_network_structure_2026-09-08.md (4 lit lanes, delivered inline to solver)

## WHY (owner: "build it -- the recurrent generative loop / whatever is left -- brain-foundationally, right not cheap")
Both PAIRWISE formal halves (forward SUFFICIENCY gate 0.68; counterfactual NECESSITY) tie + reduce to lexical
set-membership. The one unrefuted route: build a per-story CAUSAL GRAPH and select by GLOBAL STRUCTURE (Trabasso &
van den Broek 1985 causal network + main-chain membership; the true cause sits on the connected causal chain to the
outcome). RESEARCH-CALIBRATED going in (honest): connectivity-SELECTS-cause is an UNTESTED extrapolation (Trabasso
validated connectivity/main-chain for recall/importance/summarization, NEVER for cause-selection -- 2 papers read in
full); global-beats-local under the confound is untested with a cautionary "centrality is a poor substitute for
causal inference" (Sci Reports 2019); noisy edges corrupt global centrality MORE than local pairwise. P=0.15-0.20
full-pop / 0.35-0.40 confound.

## WHAT I BUILT (glass-box; reuses the LANDED hdlab.causal_reasoner.CausalGraph -- Trabasso/Pearl-pinned)
- NODES = story sentences. EDGES under TEMPORAL PRIORITY (i->j only if i<j; Trabasso criterion 1), weighted by
  forward-predictability w(i->j)=cos(T.vec(i),vec(j)) from the construction-validated forward operator.
- STRUCTURE = order-constrained DAG (K2/Chow-Liu pinned tractable, Cooper-Herskovits 1992): each event attaches to
  its best-supported prior parent (single-parent backbone) + top-tau extra edges.
- SELECT by GLOBAL structure (CausalGraph): cn_root=ultimate_cause (connectivity-ranked root ancestor);
  cn_conn=max-connectivity ancestor (Trabasso salience); cn_nec=structural necessity via graph surgery (is_necessary:
  remove C, does q lose reachability from remaining roots -- LABELED an ancestry PROXY, valid for single chains, NOT
  full Halpern-Pearl AC2 per the research's two-arsonists refutation); cn_parent=best direct parent (local control).
- CONTROLS: info-free twin + the decisive STRUCTURE-SHUFFLE (permute edge weights -> random backbone of equal
  density; does the REAL structure beat it?); confound subset; GOAL/OTHER; single-gold + credit@2. tau swept {0.6, none}.

## THE MEASURED RESULT (n=256; base_mult 0.2773) -- verdict CAUSAL_NETWORK_LOCATED_NEGATIVE (robust across tau)
- ALL structural selectors UNDERPERFORM base: cn_conn 0.207, cn_nec 0.191, cn_parent 0.211, cn_root 0.000 (the
  main-chain ROOT is systematically the story opening -- never the non-adjacent cause; confirms Trabasso connectivity
  is a recall/importance metric, NOT a cause-selector). best-struct(cn_conn)-base FULL -0.070 CI[-0.141, 0.0].
- CONFOUND subset (n=192): cn_conn beats base +0.12 (base 0.052 -> 0.172, CI-sep) -- BUT that is the low-base artifact.
- THE DECISIVE TEST -- STRUCTURE vs its SHUFFLE-TWIN: full +0.043 (NOT CI-sep); CONFOUND +0.010 (NOT CI-sep). The
  REAL causal backbone does NO BETTER than a RANDOM backbone of equal density -> global structure carries NO
  cause-selection signal over these (noisy) edges. best-struct vs local-parent -0.004 (structure adds nothing over
  the local edge). Robust at tau=0.6 AND backbone-only. credit@2 base 0.289 -> cn_conn 0.344 (lenient, not decisive).

## CONCLUSION -- the causal-selection problem is now BRACKETED on ALL THREE fronts (11th triangulation)
I have now built + measured the COMPLETE space of formal/structural causal-selection computations:
  1. LOCAL SUFFICIENCY (forward event-transition, gate 0.68): ties, twin-artifact.
  2. LOCAL NECESSITY (counterfactual leave-one-out over bound events): ties, set-membership, twin-artifact.
  3. GLOBAL STRUCTURE (causal network: connectivity + main-chain + structural necessity): UNDERPERFORMS base, and
     STRUCTURE = SHUFFLE (no global signal over noisy edges).
ALL THREE tie/underperform and NONE beats its info-free/structure twin. The ceiling is DEFINITIVELY the
causal-EDGE-correctness (determining the true causal link from text -- the parent's ~8-way wall) + the EVAL
(TellMeWhy single-gold; 26.12% inter-answer lexical overlap; credit@2 does not rescue). Global structure does not
escape it -- exactly the research's mechanical prediction: with edge-extraction capped ~70-75% even for strong LLMs,
noisy edges corrupt a global centrality computation (which integrates many wrong edges) MORE than a local pairwise
judgment (which needs one pair right). This is the honest, formally-grounded, thrice-confirmed answer to "build the
recurrent generative loop": its structural core, built to spec, does not cross THIS wall, because the wall is the
edges (+ the eval), not the selection computation over them.

## WHAT REMAINS GENUINELY OPEN (honest)
- The edge-CORRECTNESS itself (better causal-link extraction) is the true bottleneck -- but every proxy tried
  (connective, force, temporal, means-end, forward-transition, STRIPS object-match, resonance) is promiscuous; a
  materially better LLM-free edge extractor is the parent's open wall, not solved here.
- INCREMENTAL online construction (Fletcher-Bloom current-state; Landscape; Event-Indexing) vs the post-hoc
  whole-story graph I built: the research says online is the general brain claim; post-hoc is a defensible
  idealization for short chronological stories (TMW), so online construction is unlikely to change THIS result.
- A genuinely graded causal-network EVAL (Trabasso-Sperry connectivity gold) would need annotation.

## REVERIFY
.venv/Scripts/python.exe experiments/exp_multistep_causal_network_v1.py --run --n 1500 [--tau 0.6]
Witness: verification/test_multistep_meansend_chain.py W27-W28 (structure underperforms base + structure=shuffle-twin).

## TLDR (plain English)
The last brain-faithful idea was: instead of comparing sentence-pairs, build a little cause-and-effect MAP of the
whole story and pick the cause by its place in the map (the true cause is on the connected chain that leads to the
outcome). I built exactly that, reusing our existing causal-graph tools. It did WORSE than the plain baseline -- and
the decisive check settled it: the REAL map does no better than a RANDOMLY-WIRED map of the same size. That means
the map's shape carries no real cause information here, because the links we can draw between sentences are
themselves too unreliable -- and a whole map built from unreliable links is even noisier than judging one pair at a
time. So we have now tried all three textbook ways to pick a cause -- "did it make the outcome likely," "would the
outcome have happened without it," and "where does it sit in the story's cause map" -- and all three come out even
with the baseline. The wall is not which method we use; it is that reliably telling a real cause-link from a
coincidence in plain text is the hard unsolved thing (and the answer key is itself inconsistent). This is a real,
now three-times-confirmed result about where the wall is.

## QUESTIONS
None. (The genuinely-open item -- a materially better LLM-free causal-edge extractor -- is the parent's standing wall.)

## NEXT STEPS
- The forward-transition organ's HOME benefit (closing the N400 forward loop) is validated by the existing
  exp_forward_event_* family + this session's operator -- propose landing it (Q111) independent of cause-selection.
- Do NOT build further causal-SELECTION scoring computations over the current edges (thrice-confirmed capped).
- If the core is revisited: the only lever left is EDGE-correctness (a better LLM-free causal-link extractor) or a
  graded multi-reference EVAL -- both are large, separate programs.
