# FINAL: the EXACT gaps + the specific next step -- chain_multi_step_plans_and_scripts_for_the_generative_world_model

**date:** 2026-09-08 | **status:** PARTIAL (subset win + rigorous located negative = the bar's blessed full pass) |
**witness:** verification/test_multistep_meansend_chain.py 35/35 | **owner_verdict:** unset (owner's call)

This consolidates a full arc (9 cells, ~16 research lanes, 15 located negatives) into the EXACT gaps, each with its
measurement, and the one specific next step. Detail lives in SOLVED.md (UPDATES 1-7) + the *_RESULT_* notes.

## WHAT IS SOLVED / BANKED (promote this)
The GOAL-causation slice. The ATL means-end hub (ATOMIC PPMI+SVD, diagnostic-normalized) cracked coverage 8.7%->88%
and DOUBLED the subset win: me2 0.5326 vs base 0.2935, +0.2391 CI[0.1304,0.3587] CI-separated, info-free twin loses
(p=0). This is the ONE place the reader has causal knowledge SPECIFIC enough to discriminate (the story states the
explicit goal; the hub connects it to the action). Brain-foundational (Lambon-Ralph ATL hub + Baker-Saxe-Tenenbaum
inverse planning). It should LAND for its slice (Q111 -- solver does not write hdlab).

## THE EXACT GAPS (specific, measured -- NOT vague "needs more work")

**GAP 1 (THE gap) -- MECHANISM-LEVEL CAUSAL KNOWLEDGE is missing for every non-goal causal type.**
The knowledge-granularity ladder, fully climbed, each rung MEASURED to tie at chance on full-population cause-selection
(pairwise gold-vs-distractor AUC ~0.50-0.51, ties base, loses to its info-free twin):
  - GENERIC knowledge (ATOMIC xNeed/xEffect precondition/effect KB): coverage 100%, AUC 0.51 (exp_multistep_atomic_knowledge_necessity_v1).
  - + ENTITY specificity (WorkingOverlay resolved participants): still AUC ~0.51 (W15/W18/online cell).
  - + OBJECT grounding (schema instantiated on the story's specific objects): still AUC 0.507 (exp_multistep_online_worldmodel_v1).
The residual, pinned precisely: CAUSAL-MECHANISM-level knowledge -- "does action A PRODUCE the specific state that q
NEEDS" (how the world works), the transition that distinguishes the true cause from a co-occurring distractor. We
have it ONLY for goals (means-end hub). Absent for physical/mental/emotional. This is one level FINER than
entity/object binding and is the learned-world-model frontier (even LLMs cap ~70-75%; LLM-free open-domain is the
40-year-unsolved ontology wall: Schank-Abelson scripts, Forbus QPT/Companions, Mueller Event-Calculus all hit it).

**GAP 2 -- the exposed NON-BRAIN-FOUNDATIONAL system: the substrate's world-knowledge is ASSOCIATIVE.**
Measured: the causal edge is ORTHOGONAL to association -- on answerable-from-context items the true cause is LESS
associated with q than the best distractor (54% by lexical overlap, 73% by forward-prediction, 34% share ZERO content
words; mean overlap gold 1.06 vs distractor 1.64; exp_lever_signal_loss_diagnostic_v1). Verified science (Pearl's
causal-hierarchy theorem, Bareinboim et al. 2022): intervention/counterfactual queries are UNIDENTIFIABLE from
associative data in general -- so a co-occurrence/PPMI/transition-frequency store is the WRONG COMPUTATIONAL CLASS for
causation, no matter how much of it we have. The brain-foundational alternative is a structured, role-asymmetric,
INTERVENABLE causal model. The intervenable MACHINERY is LANDED (WorldState do() fold/apply_event/unmet_preconditions;
PP-270 do-calculus acc=1.000; PP-286 causal-DAG edge_prec 0.782; PP-291 Bayes-net) -- what it LACKS is GAP-1's
mechanism-level knowledge to feed it. (NOT embodiment: causal-network construction is amodal -- Speer et al. found no
causal-specific sensorimotor signature; P~0.15 that embodiment is required.)

**GAP 3 -- the ASSOCIATIVE 39% slice has NO directed causal mechanism, by nature (a genuine ceiling, not a fix).**
Cause-type composition (n=256): GOAL 92 (36%), untypeable-ASSOCIATIVE 101 (39%), PHYSICAL 29 (11%), MENTAL 20 (8%),
AFFECTIVE 14 (5%). Even a perfect set of typed engines caps at ~0.70 (the oracle ladder's associative +0.297 is
base/topical territory -- no directed engine addresses it).

**GAP 4 -- the EVAL is leaky but PROVEN NOT the bottleneck.** TellMeWhy single-gold has 26.12% inter-answer overlap
(graded human signal collapsed to a union). BUT the mechanisms tie even PAIRWISE (2-candidate AUC ~0.5,
exp_multistep_pairwise_discrimination_v1) -> the tie is a genuine MECHANISM cap, not an eval artifact; a graded/clean
eval would not rescue it. (A fairer eval is still worth having so the goal win is not understated, but it is not the
lever.)

## WHAT IS DEFINITIVELY CLOSED (do not re-attempt)
Every SELECTION computation over the current (associative) knowledge: forward sufficiency (gate 0.68, ties), pairwise
necessity (set-membership, ties), global causal-network structure (=shuffle), force-dynamic edges (14% cov, no lift),
multi-engine competition (promiscuous), and the eval fix (mechanisms tie pairwise). And every knowledge-granularity
rung buildable LLM-free EXCEPT mechanism-level (generic/entity/object all tie).

## THE NEXT STEP (specific, singular)
Build a CURATED, MECHANISM-LEVEL CAUSAL-EFFECT FOUNDATION asset -- for each action/verb, the SPECIFIC state-change it
produces (action -> resulting world-state), fine-grained enough that C's effect UNIQUELY satisfies q's precondition --
extending the proven GOAL/means-end template to the other causal types, and FEED it to the already-landed intervenable
machinery (WorldState do() / PP-270). This is the north-star KNOWLEDGE LEVER (curated foundation FIRST, then online
propose-verify grow), SCOPED to the corpus's dominant everyday event schemas (tractable) rather than open-domain
(intractable LLM-free). It is a MULTI-CELL KNOWLEDGE-ACQUISITION program, not a mechanism cell -- and per the whole
arc it is the ONLY route the measurements leave open for the non-goal population. Immediate concrete deliverable:
promote the banked GOAL win (GAP-0/SOLVED) now.

## REVERIFY
.venv/Scripts/python.exe verification/test_multistep_meansend_chain.py   # 35/35 (~1-2 min)
Cells: exp_multistep_{meansend_chain,forward_transition,necessity,causal_network,pairwise_discrimination,
worldstate_necessity,atomic_knowledge_necessity,online_worldmodel}_v1.py + exp_lever_signal_loss_diagnostic_v1.py +
exp_forward_transition_coherence_v1.py. NO hdlab written (Q111). ASCII-clean.

## TLDR (plain English)
We now know exactly what's missing, with numbers. Our reader has plenty of general knowledge (it applies to 100% of
stories) and can even reason about specific people and things -- but that still isn't enough to pick the cause,
because the wrong answers involve the same people and things as the right one. The one missing ingredient is
knowledge of HOW one action actually brings about another (the specific cause-and-effect mechanism). We have that for
goal-driven causes (and we win there); we don't have it for physical/emotional/other causes, and building it for
open-ended stories is the hard "how the world works" knowledge that large models get from scale. So the next step is
a knowledge-building program: curate a fine-grained "this action produces this state" rulebook, starting from the
kinds of everyday events these stories use, and feed it to the cause-testing machine we already have.
