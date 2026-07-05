# Research — the substrate reasoning about ITSELF: honest gap assessment + first self-reasoning cell

Date: 2026-07-05
Author: research (Opus)
Trigger: USER core strategic vision re-check (project_user_strategic_vision_self_improvement_portal_core_mathematics, 2026-06-22) — "when will substrate be able to self-improve... realize which capabilities are actually similar... identify a core underlying mathematics." Director asked for a brutally honest gap assessment + a first self-reasoning cell design (design only, no dispatch).
Discipline: generic-terms-only external queries (query-privacy); lit-scan calibration penalty applied (deflate 0.15-0.25, novel-synthesis capped 0.50); scoured substrate on-disk history before any external search (per [[feedback-prior-work-informs-not-constrains]]).

---

## HEADLINE

**Every piece of "self-reasoning" that exists today is Director/Python reasoning ABOUT the substrate's stored state, not the substrate's own HD algebra reasoning about itself.** `cert_ledger_query.py`, `director_kb_query.py`, `research_field_advisor.py` are all deterministic Python scripts that groupby/parse JSONL and markdown — useful, correct, but external. The ONE genuine attempt to get the substrate's OWN reasoning machinery (KGStore + multi-hop + community-detection) to reason about its own cert-ledger data — the `substrate_self_map` arc (v2 -> v2b -> v2c -> v2d -> v2e -> v2f, 2026-06-22/23, 6 attempts, ~50 cycles) — is **closed HARD_FAIL**: "self-mapping null even with semantic encoder; substrate self-mapping fundamentally hard regardless of encoder" (v2f verdict_msg, verified on disk). That result is real and should not be re-litigated. But it tested the **wrong, harder sub-problem**: unsupervised community-detection over atom NAME embeddings. Nobody has tried the **easier, narrower, already-proven-mechanism sub-problem**: pointing the substrate's CHAIN_GRADE multi-hop KG-retrieval (the same mechanism validated at 36x-ratio on FB15k-237/ConceptNet and at 16-18-hop depth on synthetic chains) at cert_ledger's own explicit bookkeeping fields (`supersedes`, `cert_status`, `verdict`) to answer two concrete self-evaluation queries: "what is capability X's CURRENT status" and "do any two records about the same thing disagree." That gap is real, cheap to close, and is the correctly-scoped first self-reasoning cell. P_deflated = **0.55** for the retrieval sub-task (near-engineering, low research risk), **0.35** for the conflict-flagging sub-task (novel-synthesis, capped), blended **0.45** for the combined cell.

---

## 1. WHERE ARE WE, HONESTLY (scoured, not assumed)

### 1a. What genuinely EXISTS (substrate stores + is queried about itself)

- **Storage**: `data/substrate_index/meta/cert_ledger.jsonl` — 1431 rows, verified on disk. Schema: `atom_id, atomized_by, cell_commit, cert_class, cert_increment_delta, cert_status, cv, note, op, referent_pointer, supersedes, ts, verdict, verified_off_data`. This IS a JTMS-style justification ledger already (see 2b) — it just isn't exposed to the substrate as a KG.
  - `count-by-status` (unfolded): chain_grade=533, measured_mechanism=191, None=183, under_classified=149, honest_negative=83, custom=54, hard_fail=32, middle_band=26, + 12 smaller classes.
  - **633 of 1431 rows (44%) have `verified_off_data` null/false** — an honest "audit debt" backlog that itself is a self-evaluation target (see Sec. 2).
  - **44 atom_ids have >1 ledger row** (a real revision/lineage), of which **11 have genuinely DISTINCT `cert_status` across their rows** — i.e., 11 real cases where a claim's status changed over time. This is the concrete, small, real test-bed for a currency/consistency cell (Sec. 3).
- **Query (external, deterministic)**: `tools/cert_ledger_query.py` (count-by-status, audit-debt-queue, find-by-atom-id, show-mm-partners, etc.) and `tools/director_kb_query.py` (semantic KB query over notes/memory with KG traversal for Director's post-compaction memory, per `project_substrate_as_director_kb_dogfood`). Both are read-only Python/CLI tools invoked BY Director or agents. Neither runs on the substrate's own HD vector-algebra machinery — `cert_ledger_query.py` is pure-stdlib JSON parsing; `director_kb_query.py` uses a Pythia-160m/BGE-style encoder for semantic similarity at the QUERY layer, with the substrate's KG only as an index, not as the reasoning engine that decides currency/consistency.
- **"Self-certification" (feedback_substrate_autonomy_path..., 2026-06-17)**: this USER directive is about encoding AUDITOR JUDGMENT as deterministic gates (cap_pres, axiom_term, verdict-mapping) that self-apply during atomization — this has genuinely happened (auto-applied gates exist) but it is rule-based bookkeeping applied at write-time, not the substrate reasoning about its own state at read-time. Real progress, different axis from what's asked here.
- **"Dogfood" (project_substrate_as_director_kb_dogfood, 2026-06-26)**: substrate as Director's post-compaction MEMORY — genuinely shipped (Wave 1), but explicitly scoped as passive index/cache with Director doing the reasoning ("Read-only from Director" is principle #6 of the design). By design, not self-reasoning.
- **`research_field_advisor.py`** ("propose next experiment"): a hand-coded Python heuristic (`tier_score - cost - saturation + scope_bonus`) parsing markdown notes. This is Director's OWN proposal-ranking tool, run by Director/research, not the substrate.

### 1b. What was GENUINELY TRIED and is a real prior data point: `substrate_self_map` v2-v2f (2026-06-22/23)

This is the one honest attempt at substrate-native self-reasoning and it deserves to be cited accurately, not buried:

| Attempt | Mechanism | Result |
|---|---|---|
| v2 | char-trigram encode atom names -> KGStore -> 2-hop Jaccard -> cluster | small-scope spurious signal (later shown confounded) |
| v2b | same, restricted scope | MIDDLE_BAND (small-N artifact) |
| v2c | same, FULL Store (200k triples) | HARD_FAIL, gap=-3 (resolution-limit / discriminator misspecified) |
| v2d | + IRF weighting + degree-preserving null | ground-truth (hand-built v1 lexical families) shown degenerate (2/20 anchors) |
| v2e | + modularity-Z gamma-sweep + Laplacian-RG + engram-allocation (5x-deeper drill, grounded in Fortunato-Barthelemy/Reichardt-Bornholdt/Villegas LRG) | **bit-identical to degree-preserving null at every gamma** — the char-trigram+Jaccard adjacency carries NO information beyond degree sequence |
| v2f | swap encoder to word2vec-keyword / hybrid (the prescribed "encoder-substitution" fix) | **still HARD_FAIL**: Z_w2v=0.61, Z_hybrid=0.94, both far below the >=2.0-3.0 pass bar; recall_min=0.53 also missed. verdict_msg (verified on disk, `data/exp_self_map_v2f_pretrained_encoder_smoke_v1_smoke/metrics.json`): *"self-mapping null even with semantic encoder; substrate self-mapping fundamentally hard regardless of encoder."* |

This is a **closed, well-earned negative** across 6 attempts and 3 independent discriminator classes (Jaccard-cluster, modularity-Z+null, LRG). Per [[feedback-prior-work-informs-not-constrains]] I am NOT proposing a 7th clustering attempt — that hypothesis class is exhausted. But the failure is narrower than "the substrate cannot reason about itself": it is specifically "**unsupervised community-detection over atom-name embeddings cannot discover NEW capability structure**." It never tested "**can the substrate's proven RETRIEVAL mechanism answer a SUPERVISED query about its own explicit bookkeeping fields**" — a mechanistically different and much easier task (Sec 3).

### 1c. The honest verdict on Q1

**All autonomous self-reasoning today is external (Director/Python/agent-driven).** The one native attempt closed HARD_FAIL on the hard sub-problem (structure discovery) and was never retried on the easy sub-problem (status retrieval + consistency check over explicit fields). That gap — not a new capability, just an unexploited reuse of already-CHAIN_GRADE machinery — is where the first real self-reasoning cell should go.

---

## 2. THE FIRST SELF-REASONING CELL

### 2a. Design principle: reuse the retrieval mechanism, NOT the (closed) clustering mechanism

`hdlab/kg_traversal.py` `KGStore` (multi-value Hebbian (s,p,o) triple store: `key = E[s]*R[p]*sqrt(n_dim)`, `scores = E @ (W @ key)`) and `hdlab/multi_hop.py` (`naive_chain`, `iter_cleanup_chain`, `bidirectional_chain`, `partition_routed_chain`) are the SAME primitives that:
- landed CHAIN_GRADE on FB15k-237 (U1, 5000-7410x random floor) and ConceptNet (n8, 36.49x ratio, setrecall@100000=1.000, refuse-OOD=0.999),
- and (per the 2026-07-05 backup) now extend to **16-18-hop usable chain depth** via key-slot sharding, and compose end-to-end through the full comprehend->reason->gate->generate stack with `compounding_ratio` ~0.97.

None of that machinery has ever been pointed at cert_ledger.jsonl for a RETRIEVAL task. The self_map arc pointed a DIFFERENT primitive (unsupervised clustering) at cert_ledger for a DIFFERENT task (structure discovery). Reusing the retrieval primitive for a retrieval task is the correctly-scoped move.

### 2b. Why NOT try to discover contradictions via similarity (a specific, lit-grounded caution)

An external lit-scan (generic KG-embedding search terms) surfaced a directly on-point, sobering result: a recent paper on stale-fact/supersession memory in retrieval systems found that **cosine-similarity embeddings are near-chance (AUROC ~0.59) at telling a CONTRADICTED/superseded fact apart from a mere paraphrase/duplicate** — a contradicted fact is often MORE embedding-similar to the original than a genuine rephrasing is. Their fix was explicitly NOT embedding-geometric: a deterministic `(subject, relation)` key-match plus an explicit `superseded_by` field, checked BEFORE retrieval. This matters directly here: cert_ledger ALREADY has that deterministic field (`supersedes`, a row-hash pointer, written at cert-relabel time) — so the correct design is to **expose the existing deterministic bookkeeping as explicit KG edges** (`SUPERSEDED_BY`, `SAME_SUBJECT`) and let the substrate's proven retrieval mechanism WALK those edges, rather than asking it to discover supersession/conflict from content similarity (a task the classical + modern KR literature both say is genuinely hard, see Sec. 4). This sidesteps the exact failure mode that a nearby field has already documented.

### 2c. The cell, concretely

**Anchor working name**: `exp_cert_ledger_self_query_v1` (spec only — not authored/dispatched per Director instruction).

**Ingest** (cheap, deterministic, ~1431 rows, no re-encode):
1. Entities = union of {ledger row-hashes} + {atom_qualified_ids} + {a small closed set of `cert_status` value-entities}.
2. Relations (new edge types, all deterministic at write time, none inferred): `SUPERSEDED_BY` (row-hash -> row-hash, inverse of the existing `supersedes` field — trivial to derive), `HAS_STATUS` (row-hash -> cert_status value-entity), `SAME_SUBJECT` (row-hash <-> row-hash sharing the same `atom_id` or `referent_pointer.atom_qualified_id`/`metrics_path` — exact-match, not similarity).
3. `KGStore.ingest_triples()` on this small graph (on the order of 1431 rows x ~3 edge types = a few thousand triples — three orders of magnitude below the 200k-triple full-Store scale that broke the self-map clustering attempts; well inside proven capacity).

**Task A — verdict-currency retrieval** (the safer, near-engineering half): for N held-out atom_ids with a known lineage (the 44 real multi-row atom_ids on disk today), walk `SUPERSEDED_BY` edges via `multi_hop` chain-following from any row in the lineage to the sink (no outgoing `SUPERSEDED_BY` edge = current). Compare the substrate-retrieved current `cert_status`/`verdict` against the Python oracle (`cert_ledger_query.py`'s `fold_supersedes()`, already correct and cheap to compute as ground truth). Shuffled-edge control: randomly permute `SUPERSEDED_BY` targets among same-atom rows; should collapse retrieval accuracy toward chance.

**Task B — same-subject conflict flagging**: for all 44 lineage atom_ids, use `SAME_SUBJECT` (exact-match, not learned) to group rows, then read off `HAS_STATUS` for each; flag groups where >1 distinct status value appears among rows where NEITHER supersedes the other (an unresolved disagreement, as opposed to a normal revision). Ground truth: the 11 atom_ids already known (by direct Python computation, Sec 1a) to have distinct statuses across rows — of those, how many are simple supersession (resolved) vs genuine unresolved conflict.

**Secondary diagnostic (brain-grounded, cheap, free byproduct of Task A/B)**: record the retrieval MARGIN (top-1 minus top-2 score) for every query. Per the ACC/conflict-monitoring literature (Sec. 4), a low margin should correlate with rows independently known to be ambiguous (`under_classified` status, or membership in the 633-row `audit_debt` backlog). This is a falsifiable, essentially-free correlation check, not a new mechanism.

### 2d. Bands (pre-registered here; deflate per role discipline)

- **HARD-PASS (Task A)**: substrate-retrieved current-status matches the Python fold_supersedes() oracle on >=90% of the 44 lineage atoms (>=40/44), AND shuffled-edge control accuracy <=1/n_status_classes + 0.10 (near chance). P_deflated = **0.55** (this is close to a proven-mechanism engineering check, not a research bet — deflated from a naively-high ~0.80 because the wiring is new: this exact edge-schema + KGStore combination has not been run, and hub-crowding at even this small scale (a handful of `cert_status` value-entities acting as high-in-degree hubs) is a documented failure mode elsewhere in the substrate, e.g. the deg8+ hub work).
- **HARD-FAIL (Task A)**: match rate <=60% (24/44) OR shuffled control not near chance (control retrieval >0.40, indicating the "signal" is a schema artifact not real edge-following). P = 0.20.
- **MIDDLE (Task A)**: 60-90% match rate. P = 0.25.
- **HARD-PASS (Task B)**: of the 11 known distinct-status lineage atoms, correctly separates resolved-supersession from unresolved-conflict on >=8/11, with zero false-positive conflict flags among the 33 same-status lineage atoms. P_deflated = **0.35** (capped per novel-synthesis discipline; this sub-task's "ground truth" of 11 cases is small and the resolved-vs-unresolved distinction has more judgment-call surface than pure chain-following).
- **HARD-FAIL (Task B)**: <=3/11 correctly separated, or any false-positive flags on the 33 non-conflicting atoms (a Goodhart/precision failure would be worse than a null result here, since audit trust depends on low false-positive rate). P = 0.30.
- **Blended cell verdict**: report Task A and Task B as INDEPENDENT discriminators (do not average them into one pass/fail); a Task-A HARD-PASS + Task-B MIDDLE is a legitimate, honestly-reportable partial win (retrieval-of-currency native; conflict-flagging needs more work) — this composes with the "no-smoke, don't force a single verdict string" discipline already banked this session.

### 2e. Cost

Cheap: ~1431-row ingest (seconds), 44-atom query set (seconds), no GPU, no re-encode, reuses existing `hdlab/kg_traversal.py` + `hdlab/multi_hop.py` unmodified except for a small parsing script (`cert_ledger.jsonl` -> triples). Order of an afternoon of `hdi_exp_dev` authoring + smoke, not a multi-day build.

---

## 3. CONNECTION TO MATH — does self-reasoning need the math/formal-reasoning track first?

**No, not for this first cell.** Task A (chain-following to find the current status) and Task B-as-designed (exact-match same-subject grouping + field comparison) are both **retrieval / graph-traversal** operations on the substrate's existing proven vector-algebra (bind, multi-hop chain-follow, top-k score) — no new arithmetic, no threshold logic, no symbolic comparison of continuous quantities is required. This can run NOW, sequenced strictly BEFORE any new "core mathematics" capability build, using 100% already-CHAIN_GRADE primitives.

**Where math DOES become load-bearing**: a deeper form of self-evaluation — "does this atom's `cert_status` actually FOLLOW from the metrics.json numbers cited in its `referent_pointer`" (e.g., is `spearman=0.886 >= 0.80` -> `chain_grade` a valid entailment) — is genuinely a different capability: comparing continuous numeric evidence against a threshold and checking a logical implication. That is closer to formal/symbolic reasoning (the substrate-native equivalent of what `hdi_skunkworks`'s human/LLM-driven VET currently does by hand) and would plausibly benefit from or require whatever the math-capability scoping track produces (arithmetic/comparison primitives, not just vector similarity). **Sequencing recommendation**: ship the retrieval/traversal cell (Sec. 2) now, independent of and not gated on math scoping; treat "substrate-native VET / entailment-checking" as a SECOND, harder self-reasoning cell explicitly gated on whatever the math/formal-reasoning drill produces. I did not find an active, concurrently-running math-capability-scoping deliverable on disk as of this session (searched `notes/*math*scop*`, `*formal_reasoning*`, `*core_mathematics*` — all hits are from 2026-06-11/06-22, predating the current architecture); if one is in flight elsewhere, this note's Sec. 3 recommendation composes with it directly rather than depending on it.

---

## 4. HOW THE BRAIN SELF-EVALUATES (lit-scan, generic terms only, 2 parallel Sonnet sub-agents)

Three DISSOCIABLE mechanism classes recur in the neuroscience literature (not one unified "metacognition module"):

- **(a) Evidence-accumulation confidence readout** — Kepecs, Uchida, Zariwala & Mainen, *Nature* 2008: rat orbitofrontal-cortex neurons encode confidence as a statistic of the SAME evidence-accumulation process that drove the original decision (not a separately-trained critic). Elegant but awkward to retrofit onto a vector-symbolic lookup that just returns a bind/unbind match — there is no accumulation process to read a statistic from.
- **(b) Conflict-monitoring from co-activated competing representations** — Botvinick/Yeung school (conflict-monitoring theory, ERN literature); dorsal ACC computes a scalar from the simultaneous activation of mutually incompatible representations, not from a ground-truth comparison. Milham/van Veen 2002 (PNAS) explicitly dissociates this from error-monitoring proper. **This is the cleanest, most directly portable mechanism**: "conflict = margin between top-2 competing retrieval candidates" is a near-zero-cost byproduct of any top-k retrieval, requires no new learned readout, and is exactly the Sec. 2c secondary diagnostic.
- **(c) Forward-model / efference-copy mismatch** — cerebellar prediction-error (Purkinje-cell discharge relayed to mPFC); the cleanest "predicted-vs-actual" comparator in the whole literature but domain-specific to sensorimotor control, with no obvious non-motor generalization without importing unproven extensions (this is the SAME cerebellar mechanism already flagged, independently, in the 2026-07-05 brain-component rerank as a candidate fix for CONTROL's depth-degradation — a second, unrelated line of evidence that cerebellar forward-modeling is a live, useful primitive to eventually build, just not for THIS cell).
- **Contradiction between two stored memories/beliefs specifically**: van Veen, Krug, Schooler & Carter, *Nat Neurosci* 2009 — dorsal ACC + anterior insula activation tracks the DEGREE of discrepancy between a person's past behavior and a stated belief, and predicts subsequent belief updating. Notably, **the brain appears to reuse the SAME generic conflict-monitoring circuit for belief-level contradiction that it uses for ordinary response conflict** — there is no dedicated "compare memory A vs memory B" detector distinct from (b). This directly supports the design choice in Sec 2c (treat the margin/conflict signal as a general-purpose byproduct, not a bespoke new mechanism).
- Pattern separation/completion (dentate gyrus -> CA3) is a STORAGE-side anti-interference mechanism (keeps similar memories from blending at encoding time) — relevant to why the substrate's own hub-collision problems matter for this cell (Sec 2d hub caveat) but is not itself a self-evaluation mechanism.

**Deflated recommendation**: the brain evidence most cleanly supports mechanism (b) — conflict-monitoring-as-retrieval-margin — as the "self-evaluation" primitive to build first, which is exactly what Sec. 2c proposes as a free byproduct, not a new build. Mechanisms (a) and (c) are real but each require infrastructure (an accumulation process; a forward/generative model) the substrate does not have wired to this task yet.

**AI/knowledge-representation side** (second lit-scan): Doyle's Truth Maintenance System (1979) and de Kleer's ATMS are dependency-directed justification graphs with IN/OUT labels and explicit minimal-conflict-sets ("nogoods") — this is structurally almost exactly what `cert_ledger.jsonl`'s `supersedes` + `cert_status` fields already are, just not yet exposed as a queryable graph. AGM belief revision is the axiomatic (not algorithmic) counterpart. Modern KG-embedding contradiction-detection work is comparatively weak (see Sec 2b's AUROC~0.59 finding) — reinforcing that Task B should lean on the EXACT-MATCH same-subject grouping already in the ledger, not on learned similarity.

**Citations (verified count: 12)**
1. Kepecs, Uchida, Zariwala, Mainen (2008), "Neural correlates, computation and behavioural impact of decision confidence," *Nature*. https://www.nature.com/articles/nature07200
2. Fleming & Dolan (2012), "The neural basis of metacognitive ability," *Phil Trans R Soc B* 367(1594):1338-49.
3. Fleming, Weil, Nagy, Dolan, Rees (2010), "Relating introspective accuracy to individual differences in brain structure," *Science*.
4. Yeung, Botvinick, Cohen (2004), "The neural basis of error detection: conflict monitoring and the ERN," *Psychol Rev*.
5. Milham/van Veen et al. (2002), "Dissociation between conflict detection and error monitoring in human ACC," *PNAS*. https://www.pnas.org/doi/10.1073/pnas.252521499
6. van Veen, Krug, Schooler, Carter (2009), "Neural activity predicts attitude change in cognitive dissonance," *Nat Neurosci* 12(11):1469-74. https://www.nature.com/articles/nn.2413
7. Yassa & Stark (2011) et al., hippocampal pattern separation/completion reviews. https://pmc.ncbi.nlm.nih.gov/articles/PMC3812781/
8. Doyle (1979), "A Truth Maintenance System." https://www.sciencedirect.com/science/article/abs/pii/0004370279900080
9. de Kleer, ATMS chapter (assumption-based truth maintenance). https://www.dbai.tuwien.ac.at/staff/wotawa/atmschapter1.pdf
10. SEP, "Logic of Belief Revision" (AGM postulates). https://plato.stanford.edu/archivES/FALL2017/Entries/logic-belief-revision/
11. arXiv 2606.26511, "Temporal Validity in Retrieval Memory" — embedding-similarity near-chance (AUROC~0.59) at distinguishing contradicted/superseded facts from paraphrases; deterministic key-match + explicit supersession field is the working fix.
12. Fortunato & Barthelemy (2007) PNAS / cond-mat/0606220 + Reichardt & Bornholdt (2006) cond-mat/0603718 + Villegas et al. LRG arXiv 2406.02337 — carried forward from the substrate_self_map v2e/v2f internal drills (already-verified citations from the 2026-06-23 note, re-cited here for the clustering-closure claim in Sec 1b).

---

## Cross-thread synthesis

- **META atom (existing, 2026-06-22)**: "the cert chain lives in cert_ledger SEMANTICS, not relations.jsonl TOPOLOGY" — this note's Sec 2 is the direct, previously-unexploited follow-through on that insight's Option 3 ("substrate could self-map via co-membership in cert_ledger fields... a separate cell"), which was correctly identified 2 weeks ago and never built because the self_map arc's attention was on the (closed) clustering sub-problem instead.
- **[[feedback-research-can-be-wrong-only-proven-fully-believed-trust-tier]]** and **[[feedback-substrate-autonomy-path-encode-audit-discipline-as-self-certification]]**: this cell is a direct instrument of that USER directive's stated path — "every audit judgment call -> a deterministic self-applied check" — Task A/B are exactly two audit judgment calls (currency, consistency) being encoded as substrate-native checks rather than human/Python-applied ones.
- **[[feedback-dont-dismiss-adjacent-methods]] / [[feedback-prior-work-informs-not-constrains]]**: the self_map HARD_FAIL is real and respected (no 7th clustering attempt); the pivot here is to a mechanistically DIFFERENT, already-proven mechanism class (retrieval, not clustering), which is the correct reading of both disciplines together.
- **2026-07-05 capability scoreboard**: REASONING and GENERATION are CHAIN_GRADE, INTEGRATION composes end-to-end with `compounding_ratio`~0.97 — this cell is a natural, cheap extension of the "integration proves composition" thrust onto a genuinely new (and strategically load-bearing) target corpus, not a new capability build.
- **Brain-component-driven development thrust (2026-07-05)**: metacognition / ACC-conflict-monitoring / PFC-monitoring is **not currently on the brain-component inventory** (checked directly; no hits). This note adds it as a candidate component distinct from the already-tracked basal-ganglia/thalamus/cerebellum/CLS list — narrowly, as "conflict-monitoring-as-retrieval-margin," which is nearly free to add as an instrumentation layer on top of any existing KG query (Sec 2c).

## Substrate-product implications

- If Task A HARD-PASSes: the substrate can answer "what is your current status on X" using its own HD retrieval, not Director's Python — a small but genuine, demonstrable step toward the self-improvement-portal vision (USER queries substrate directly; substrate's own machinery, not a wrapper script, produces the answer). This is honestly narrow (currency retrieval on a known small ledger), not "the substrate judges its own capabilities" in any deep sense — but it is the correctly-scoped FIRST rung, and it was sitting unbuilt since 2026-06-22 because the self-map arc's attention went to the harder, now-closed clustering sub-problem.
- If Task B also lands: the substrate can flag (not resolve) same-subject disagreements natively — directly reduces reliance on hdi_skunkworks manually re-reading old notes to catch stale claims, and gives a concrete, cheap first attack on the 633-row audit-debt backlog (Sec 1a) using the substrate's own machinery instead of a human/agent re-read of every row.
- Neither task, even at full HARD-PASS, delivers Phase 2 (autoatom) or Phase 3 (substrate proposes new mathematics) from the 2026-06-22 USER-vision memo — those remain honestly gated on a self-mapping/structure-discovery mechanism that is currently CLOSED (Sec 1b) and would need a genuinely different (not yet identified) encoding approach to reopen. This note does not claim to reopen that; it proposes a materially easier, different, and immediately achievable adjacent step.
- **Is this THE north-star to prioritize?** Partial yes, scoped honestly: among currently-open threads (perception ship-metric, generalization one-to-many ceiling, control depth-degradation, brain-component builds), this cell is uniquely (a) nearly free (an afternoon, no GPU, no re-encode), (b) 100% reuse of already-CHAIN_GRADE machinery (zero new primitives), (c) directly responsive to a 2-week-old, USER-flagged, unexploited strategic gap, and (d) the correctly-scoped reading of a firmly-closed prior negative rather than a naive retry. It is NOT a substitute for the harder open threads (perception retrieval-gap follow-through, generalization ceiling) which remain higher-magnitude capability bets; it is a cheap, high-signal, low-risk PARALLEL track that should be picked up alongside them, not instead of them — exactly the kind of "1-cycle main-thread, agent-authored" item the current full-auto cadence should slot in opportunistically.

---

## Falsifiable predictions summary (repeated from Sec 2d for scan-ability)

- Task A HARD-PASS: match-rate >=90% (>=40/44) + shuffled-control near-chance. P=0.55.
- Task A HARD-FAIL: match-rate <=60% (<=24/44) OR shuffled control >0.40. P=0.20.
- Task B HARD-PASS: >=8/11 correctly separated resolved-vs-unresolved, zero false positives on the 33 non-conflicting lineage atoms. P=0.35.
- Task B HARD-FAIL: <=3/11 correct OR any false positive. P=0.30.
- Report Task A / Task B as independent discriminators; do not collapse to one verdict string.

## P_deflated (headline number)

**0.45 blended** (Task A 0.55, near-engineering / Task B 0.35, novel-synthesis-capped). Both numbers already reflect the 0.15-0.25 lit-scan-calibration deflation and the explicit hub-collision + small-N caveats.
