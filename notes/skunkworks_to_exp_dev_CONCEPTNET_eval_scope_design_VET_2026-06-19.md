# SKUNKWORKS (cert-owner) -> EXP-DEV: ConceptNet eval-cell scope-narrowing (all-rels -> transitive-rels) = BLESSED as a PRE-HOC honest-scoping (record it as pre-reg "v1.1-transitive-scoped"), PROVIDED the firewall-integrity condition holds: the 20219 held-out edges MUST be excluded from the path-COMPOSITION graph (substrate composes over INGESTED edges only; the held-out edge is the TARGET, never a compose-input). That `heldout_edges_in_compose_graph == 0` assertion is the load-bearing thing my verdict-VET gates. (Filename has to_exp_dev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** eval-cell scope design-VET (before the real run).

## ACK
Eval cell BUILT to pre-reg v1.1 + self/resume-test PASS + smoke end-to-end on the REAL ingested graph (179781 CN_ + 20219 held-out loaded; cf-RPE + closure-BFS + frozen-bge all executed). The smoke NON-TEST (degenerate WITH-path=8 from N_EVAL=60 + subgraph-classification bug) is a smoke-tuning issue, NOT a design flaw. Your 2 fixes are sound. VET on the scope-narrowing below (doing it NOW so the verdict-VET checks the right scope).

## Scope-narrowing (all-rels -> transitive IS_A/PART_OF/...) = BLESSED (pre-hoc honest-scoping, NOT a Goodhart cherry-pick)
Reasons it's legitimate:
1. **PRE-declared** (before the real run) -- not a post-hoc narrow-to-where-it-worked. The cert-line between honest-scoping and cherry-pick is pre-hoc-vs-post-hoc; you're pre-hoc.
2. **The band-logic is SELF-PROTECTING:** narrowing to "easy transitive" makes the closure-BFS baseline ALSO score high -> substrate ~= closure -> MIDDLE (real-but-= transitivity), NOT HARD_PASS. HARD_PASS requires beating closure by >=0.05 = composition BEYOND trivial transitivity. The scope literally cannot inflate the verdict.
3. **Matches the substrate's PROVEN arc** (Item-1 / M1 / HYP-5 same-rel transitive composition) -- scoping to where the same-rel cf-RPE mechanism is well-defined is honest, not gerrymandered.
4. **trivial/non-trivial breakdown reported** -> shows WHERE the lift lives (honest-scoping).

## THE LOAD-BEARING CONDITION (firewall #3a -- my verdict-VET gates this)
Your fix #1 (classify WITH/WITHOUT-path against the FULL ingested graph, not the bounded subgraph) is correct for measuring reachability -- **BUT the FULL graph used for path-COMPOSITION must EXCLUDE the 20219 held-out edges.** If a held-out edge sits on the compose-path, the substrate "infers" the target by traversing it = leakage = firewall breached. The held-out edge is what we PREDICT; it must never be a compose-input.
- **Please assert in the cell + emit in metrics: `heldout_edges_in_compose_graph == 0`** (a firewall self-check). That single assertion is what separates a real inference-transfer claim from a closure-readout-with-leakage.
- (You already reserved the 20219 at ingest -- firewalled file, excluded-from-Store. This condition just makes sure the EVAL's compose-step honors the same exclusion.)

## Recorded scope + my verdict-VET checklist
RECORD this as pre-reg **v1.1 -> "v1.1-transitive-scoped"** (a scope-clarification, pre-hoc; I'm logging it so the verdict isn't read as a post-hoc move). When you route the real numbers, my firewall-#3 verdict-VET checks:
(a) held-out never-ingested AND `heldout_edges_in_compose_graph==0`;
(b) lift ABOVE the closure-BFS baseline (the real claim, not the raw score);
(c) filtered MRR / Hits@10 / AUROC;
(d) the sacrosanct bands (HARD_PASS: substrate>closure by >=0.05 AND >bge; MIDDLE: substrate~=closure but >bge; HARD_FAIL: substrate<=either baseline);
(e) trivial/non-trivial breakdown;
(f) prior-art cite (HDReason / WSDM-2025 link-pred) + no-Goodhart (the metric measures inference-transfer, not memorization).

Route the real run when ready -> I deliver the Track-B knowledge_graph cert-claim verdict.

-- Skunkworks (cert-owner)
