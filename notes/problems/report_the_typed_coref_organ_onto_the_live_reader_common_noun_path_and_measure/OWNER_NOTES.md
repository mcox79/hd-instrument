---
owner_verdict: DONE
---

PROBLEM (slug: report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure):
Re-recognising an entity from a plain common noun ("the company" -> Google, "the boy" -> the kid named earlier) is
common-noun coreference. A typed common-noun coref win (a clean nominal-identity view + a non-writing type bridge) was
promoted to hdlab/typed_coref.py and proven on the URG board-instrument PROXY -- but the DEPLOYED reader common-noun
path (hdlab/commonnoun_binder.py) is a DIFFERENT mention schema + binding and never uses it. THE TASK: re-port the two
brain-faithful levers onto the live reader path and prove the LIVE common-noun RESOLUTION accuracy lifts CI-separated on
modern GUM, with the info-free twin losing and pronoun/kb no-regress; a rigorous negative is a full pass.

STATUS: PARTIAL (finalized per strategy 2026-09-08; pending owner verdict).  opus 4.8 solver.

Write-up: notes/problems/report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure/SOLVED.md
  + BRAIN_FOUNDATIONAL_ANALYSIS_2026-09-08.md (same folder; full-chain fidelity ledger + efficiencies + upgrades).
Reverify (scaffold-free; recomputes every headline from source on the full GUM modern TEST; NO hdlab write, Q111):
  .venv/Scripts/python.exe verification/test_commonnoun_binder_live_report.py     # 19/19

CORE RESULT (all on the HONEST de-leaked floor -- GUM modern TEST, n=2855 anaphoric common-noun mentions, metric =
resolved-referent nominal-dominant gold eid == mention eid; string-identity floor 0.5412 = the URG board floor):
- BRIEF MECHANISM REFUTED on the live path. The deployed binder scores 0.4904 (BELOW string-identity, -0.0508 CI-sep),
  replicating the URG defect on the actual deployed binding. Re-porting the levers only reaches PARITY (generalized
  non-writing bridge 0.5201, -0.0210 CI[-0.0458,+0.0008] includes 0) -- NOT a CI-separated win. De-pollution is a no-op
  (the binder is pronoun-free by construction -- subsumption).
- DEFICIT LOCATED = the binder's BINDING (a LitBank cluster-F1 organ: person-gate + modifier-split + event-centrality,
  used for a resolution task). The URG/typed_coref resolution binding on the SAME live schema is +0.0581 over the binder
  CI-sep; the committed hdlab.typed_coref organ BEATS string-identity +0.0259 CI-sep (0.5671).
- THE FIX, PROVEN ON THE EXACT LIVE DICT SCHEMA: the full typed_coref logic ported to the reader's mention stream
  (typed_coref_liveschema_resolve) = 0.5664, +0.0252 over string-identity CI[+0.0126,+0.0375] CI-sep, recovers the organ,
  +0.0760 over the binder CI-sep, twin loses +0.0256, OOD-replicated on GENTLE (+0.0255, matches GUM). No-regress by
  construction (non-writing -> cluster labels byte-identical to the deployed binder; sm.entities + pronoun stream unchanged).

DE-LEAK (strategy ruling 2026-09-08): my pipeline does NOT use the reader's gold-coref inheritance (the ~0.80-0.86 leak).
gold_eid is used ONLY for scoring + the anaphoric-population definition, never in a resolution decision (verified on disk;
the one gold-using arm, bridge_oracle, is an explicit ceiling). All my numbers ARE the honest floor.

BRAIN-FOUNDATIONAL ROUTES PROTOTYPED (owner-directed "prototype all"):
- BINDING FIX (typed_coref) = brain-foundational, proven (above). The deployed binder it replaces is the non-brain-
  foundational component.
- ENCYCLOPEDIC route (instance-of), OFFLINE prototype: WordNet instance-of + coarse PERSON-typing = 0.5765, +0.0102 over
  the fix CI-sep, twin loses +0.0326. RECONCILIATION vs strategy's occupation-KB located-negative: coarse person-typing's
  anaphor-TYPE match beats a person-REACH control +0.0053 CI-sep (W16) -> a REAL type constraint, DISTINCT from the
  specific occupation-KB (coverage-bounded). STRONG version = the built-but-unshipped C8 DBpedia spoke (sibling +0.0955).
- REASONING route (situation-model role-fit; agentive nominalization) = LOCATED NEGATIVE (+0.0014 not-sep, ~6/2855
  addressable): common-noun re-recognition is KNOWLEDGE-bound, not local-event-role-bound.
- ORACLE (perfect comparator) = 0.7492, +0.18 headroom -- but DECOMPOSED: ~73% is discourse multi-description + parse
  noise (situation-model inference = the generative-world-model program), NOT KB-addressable. The oracle over-counts what
  any KB can buy.

CONTROLS (witness 19/19): string-identity positive control == URG 0.5412; byte-identity faithfulness (my binder mirror ==
hdlab.commonnoun_binder on 9065 labels); no-regress by construction; info-free twins LOSE on every route; NAME no-regress;
OOD (GENTLE) replication; de-leak verified; occupation-KB reconciliation.

HANDOFFS (strategy ruling -- I do NOT solve these here):
- -> replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering : my honest-floor binder measurement
  (0.4904) + the two-part diff (binding is the deficit; typed_coref is the fix).
- -> world_knowledge_common_noun_to_name_bridge_the_81_percent_residual : the encyclopedic prototype + diagnosis + the
  occupation-KB reconciliation (do NOT reuse the specific occupation-KB axis).

FLAGGED HIGH-PRIORITY FOLLOW-ON (the knowledge gap): rebuild + wire the entity-type/world-knowledge KB (DBpedia C8 offline
dump + a ConceptNet slice -- the latter also restores the DEGRADED taxonomic part-whole route, WordNet-only in this copy)
into the resolution bridge. The single biggest brain-fidelity + accuracy lever left; static-offline + invariant-safe;
consume-mechanism already prototyped (encyc=True arm). A naive LIVE Wikidata/ConceptNet API acquisition was tried +
REFUTED (~65% API-fail + noisy surfaces -> the disambiguated offline dump is required).

NEXT STEPS: A. INTEGRATE (Q111): wire typed_coref as the resolution consumer (ref typed_coref_liveschema_resolve) + add a
board_commonnoun_resolution instrument-arm (additive, ON by default). B. HANDOFFS as above. C. DO NOT REDO: p11 writing
type-license; de-pollution on the binder; person-scoped bridge alone; levers-on-the-binder as the fix; role-fit reasoning
for this task; the specific occupation-KB axis.

KEY REALIZATIONS: read the DEPLOYED organ not the proxy (the binding, not the levers, was the untested variable); isolate
the binding by holding the schema fixed (+0.0581 the single redirecting measurement); a byte-identity faithfulness assert
makes no-regress free + explains p11's pronoun drag; de-pollution subsumed for a STRUCTURAL reason; an oracle DECOMPOSED
separates knowledge from inference (stops "just add a KB" mis-direction); verify the de-leak on your OWN code; a
located-negative-elsewhere is not automatically yours -- isolate the mechanism (coarse person-typing != specific occupation-KB).

FILES: experiments/exp_commonnoun_binder_live_report_v1.py + verification/test_commonnoun_binder_live_report.py (19/19)
+ the 2 notes + data/exp_commonnoun_binder_live_report_v1/metrics.json. NO hdlab written (Q111). Reuses data/corpora/gum/.

STATUS CALL: PARTIAL (solver scope), finalized per strategy. Brief's specific re-port refuted; the underlying goal
(brain-foundational live common-noun resolution beating the dumb rule) is achieved + measured on the honest floor via the
typed_coref binding; diagnosis feeds the two new problems. Nothing awaited from the solver.
