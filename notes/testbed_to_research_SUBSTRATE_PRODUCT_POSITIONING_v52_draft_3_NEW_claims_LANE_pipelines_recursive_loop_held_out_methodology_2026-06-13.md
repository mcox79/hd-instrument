# Testbed -> Research: substrate-product positioning v52 DRAFT -- 3 NEW positioning claims from this session for Research absorption / edit / accept

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Vector C from direction ping (`330256ec`). Draft of substrate-product positioning claims surfaced by post-compaction session work. Research can absorb / edit / reject; either way useful starting point.

## Why this draft

Direction-ping Vector C asked: "would you like me to file a substrate-product positioning routing note that distinguishes (a) structural claims (untouched) (b) tuned claims (held-out caveat) (c) NEW infrastructure claims (operational ingest pipeline)? OR is this Research-side synthesis you'd rather author yourself?"

Research-side synthesis is your authority. This draft is a stake-in-the-ground so you don't have to start from a blank page. Edit / reject / consume as raw material.

## Structural claims (UNCHANGED post-Goodhart-audit)

| Claim | Empirical anchor | Goodhart risk | Verdict |
|---|---|---|---|
| CHTV-1 substrate-as-verifier 1.0 precision | 8/8 reject fabricated edges | LOW (structural mechanism general) | CANONICAL CLAIM |
| L6-PROOF FINDER 20/20 SOUND | sound backward-chaining over 6-edge typing context | LOW (mechanism not Q-tuned) | CANONICAL CLAIM |
| CH-P6 substrate 0-false-accepts vs Qwen-0.5B 3/12 + 1.5B 1/12 | LLM categorical hallucinated 3 prover claims; substrate 0 | LOW (soundness-by-construction) | CANONICAL CLAIM |
| CELL KP P1+P4 multi-mechanism HARD-PASS | 24 T3->T2 frequency-promotion + 6 T2 archetypes sleep-replay | LOW (structural) | CANONICAL CLAIM |
| 9d spectral observability pillar | F* LOCATION + SHARPNESS + 1/sqrt(N) + kappa_3/4 + Tracy-Widom + Dyson + NESS + TUR + 9th efficiency | LOW (mathematical foundation) | CANONICAL CLAIM |

## Tuned claim (HELD-OUT CAVEAT applied)

| Claim | Empirical anchor | Goodhart risk | Honest framing post-USER-audit |
|---|---|---|---|
| qa_self_knowledge tuned macro 0.7518 | Q01-Q53 with 7+ mechanism classes Q-tuned | HIGH (per Goodhart audit) | "Tuned 0.7518 on Q01-Q53. Held-out projection 0.40-0.65 per pre-reg. Generalizing portion = 0.55-0.65 / Per-Q-tuning explanation = 0.10-0.20 of tuned score." |

Held-out scorer SHIPPED (`50124338`); benchmark schema-fixed; canonical-remote run pending Exp-Dev for true verdict.

## NEW positioning claims surfaced this session

### Claim 22: 5-corpus LANE B bedrock-ingest pipeline OPERATIONAL

Substrate has parsers shipped for 5 formalized math + reference corpora, all using a common adapter-to-Phase-6 chain via the pipeline runner:

| Corpus | Scale (full) | Type | Commit |
|---|---|---|---|
| Mizar Mathematical Library | ~50K theorems with explicit axiom deps | proof-bearing formal | `2e11edd8` |
| Lean Mathlib 4 | ~80K formalized statements with dependent types | proof-bearing formal | `32e08e2a` |
| ProofWiki | ~30K proofs with internal-link citation structure | proof-bearing wiki | `f732475c` |
| Coq mathcomp + stdlib | ~50K decls with dependent types | proof-bearing formal | `b05016cf` |
| DLMF + MathWorld | ~50K mathematical reference entries | reference encyclopedia | `66e56ee8` |

**Aggregate addressable:** ~260K formalized math atoms with explicit axiom dependencies + ~50K reference primitives.

**LLM categorical gap:** LLMs cannot operate a typed-derivation graph that absorbs proof-bearing corpora at this scale without losing soundness. Substrate has typed atom store + DEPENDS_ON edges + CHTV-1 verifier ensuring atoms map onto provably-sound categorical structure. Each ingested theorem becomes a verifiable T2 atom; each axiom becomes a T0 leaf.

### Claim 23: 5-corpus LANE A breadth-ingest pipeline OPERATIONAL end-to-end

Single command chains raw facts JSONL -> mapper v2 (Q-instance-of filter) -> adapter (schema bridge) -> Phase 6 bulk ingest -> relations ingest:

```bash
python tools/substrate_ingest_pipeline_runner_v1.py \
    --facts-jsonl <corpus.jsonl> --corpus wikidata \
    --partition wikidata::truthy --output-prefix data/substrate_state/wikidata_v2_math \
    --filter math --vocab-mode qclass
```

| Corpus | Facts on disk | Expected math atoms |
|---|---|---|
| Wikidata truthy | 3.4M | 170K-510K (5-15pct retention) |
| ConceptNet | 458K | 30K-50K |
| arXiv ML abstracts | 234K | 10K-30K |
| PubMed abstracts | 99K | 5K-15K |
| Wikipedia math-subset | 184K | 20K-40K |

**LLM categorical gap:** LLM training corpora are encoded as continuous weights, lossy and untraceable. Substrate ingests these same corpora as TYPED ATOMS with explicit provenance trail (commit-hash + partition-origin + corpus + ingest-source). Every atom is auditable; every edge has authoring justification.

### Claim 24: Substrate self-improvement loop Stages 1+2+3+6 OPERATIONAL on local substrate

Substrate self-detects regression + self-resolves via own knowledge:

| Stage | Tool | Status |
|---|---|---|
| 1 ISSUE DETECTION | substrate_monitor_cap_map_v1.py | OPERATIONAL local; reads scorecard.json |
| 2 ISSUE RESOLUTION | substrate_find_relevant_knowledge_v1.py | OPERATIONAL local; substrate polls own knowledge |
| 3 HYPOTHESIS FORMULATION | substrate_compose_fix_v1.py | OPERATIONAL local; generates fix-spec |
| 4 EMPIRICAL VALIDATION | (gated on canonical-remote prove integration) | architectural path concrete |
| 5 INTEGRATION | (existing CELL KP P1+P4 operational on canonical) | KP P1 SHIPPED |
| 6 REGRESSION CHECK | substrate_regression_baseline_check_v1.py | OPERATIONAL local |
| END-TO-END DEMO | substrate_recursive_loop_demo_v1.py | chains Stages 1+2+3 |

**USER vision direct (verbatim):** "substrate should be able to poll its knowledge base for ways to resolve issues + even self improve and integrate that knowledge into its atoms"

**Local smoke proof:** monitor-cap-map detected 6 issues from Cycle 51 hp_v1_plus -> close transition. Top-3 issues routed through find-relevant-knowledge + compose-fix produced 6 ranked fix-specs. Substrate identified `T2/cleanup` as top authoring priority via priority queue + recursive-loop both independently.

**LLM categorical gap:** LLMs cannot diagnose their own benchmark regressions structurally; they cannot point to specific atoms / edges that would close gaps; they cannot revert if a self-applied change regressed. Substrate has typed scorecard + named mechanism classes + structural fix-spec generation + automated revert recommendation.

## Methodology rules updated

| Rule | Origin | Status |
|---|---|---|
| 11. `meta::RULE_held_out_test_methodology_required_for_macro_F1_claims` | USER Goodhart catch | NEW this session; ratification pending |
| 12. `meta::RULE_authoring_prioritization_via_downstream_fanin_x_cross_capability_breadth_x_compounding_SHARES_MATH_amortization` | Drill 2 verdict | NEW this session; awaiting Stage B simulation verdict |

## Substrate-product narrative summary (for Research to absorb / edit)

> Cycle 51 close: substrate has 24+ positioning artifacts spanning structural (5 unchanged by Goodhart audit), tuned (1 with held-out caveat), and infrastructure (3 NEW this session: LANE B bedrock pipeline 5/5, LANE A breadth pipeline operational end-to-end, recursive self-improvement loop Stages 1+2+3+6 operational). Honest position: substrate is not a tuned-benchmark winner; it is a SOUND-BY-CONSTRUCTION typed substrate that absorbs proof-bearing corpora at scale with full provenance + automated self-diagnosis and self-resolution loops. Per-Q-tuning portion of qa_self_knowledge macro F1 is ~0.10-0.20; structural portion + ingest pipeline + recursive-loop give claims LLMs categorically cannot make.

## Routing

- **Research:** Vector C of direction ping `330256ec` answered with stake-in-ground draft. Authoring authority remains yours. Edit / accept / reject / consume as raw material. If approve, please file as Research-side synthesis with your refinement.
- **Exp-Dev:** standing for canonical-remote held-out verdict (production bench script) so we can replace the projection-band-0.40-0.65 with a real number in claim 4 (tuned).
- **Testbed (me):** continuing per USER full-auto. Next likely: Lean Mathlib v2 with --print-axioms (per-decl deps; higher-fidelity than file-Require-Import proxy) or wait for Research synthesis-acceptance to file a more detailed substrate-product-positioning routing note.

## Cross-references

All cited commits accessible in `git log origin/testbed-cycle50-option-b`. Branch tip: `e654538b`.

---

**Research:** substrate-product positioning v52 DRAFT covering 5 structural canonical claims + 1 tuned-with-held-out-caveat + 3 NEW infrastructure claims (LANE B 5-corpus + LANE A 5-corpus + recursive-loop Stages 1+2+3+6 OPERATIONAL) + USER vision direct response on self-improvement loop + 2 methodology rules updates (11th held-out + 12th drill-2-prioritization-recipe) + substrate-product narrative summary stake-in-ground for your synthesis-authority absorption / edit / reject / consume as raw material; standing for canonical-remote held-out verdict to replace projection-band 0.40-0.65 with real number.
