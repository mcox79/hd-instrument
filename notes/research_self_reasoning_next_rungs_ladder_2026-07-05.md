# Research — the ladder of NEXT rungs for substrate self-reasoning (preparatory roadmap, post Tier 0/1/2)

Date: 2026-07-05
Trigger: Director preparatory-roadmap request for the north-star ("the substrate reasoning about itself") — chart the NEXT rungs after this session's FIRST rungs, each narrow/buildable/honestly-scoped, explicitly avoiding the leap to autonomous self-improvement (USER-LOCKED).
Discipline: `python tools/orchestrator/research_field_advisor.py` run (no matching tracked field — all 22 tracked fields are physics/stat-mech adjacencies; same honest gap the three same-day sibling notes below already flagged; correctly not acted on). Generic-terms-only external queries (query-privacy); lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis cap 0.50); HARD-FAIL thresholds mandatory. Scoured on-disk prior work (read all three same-day sibling notes + both landed cells' full source + both metrics.json in full) before any external dispatch, per [[feedback-prior-work-informs-not-constrains]]. NO routing files emitted (ferry mechanism deprecated; everything actionable — including the ready cell spec — is delivered in this note).

---

## HEADLINE

**Two genuinely new, narrow, locally-smoke-buildable rungs sit directly on top of what landed today, both zero-gated on the parked remote-deploy blocker.** The top pick — **global cert-graph consistency** (cycle-freedom + fork-freedom + tier-monotonicity, swept across the WHOLE ledger rather than a hand-picked query) — is ~65-70% direct reuse of `exp_cert_ledger_self_query_v1`'s own proven primitives (KGStore, `currency_walk`+visited-set, `tier_family`, scrambled-edge control) plus a genuinely new invariant-detection layer (fork-detection and monotonicity-along-a-resolved-chain, neither of which self_query_v1 ever computed). Direct on-disk re-measurement this drill (not asserted) grounds its design: of the 44 real multi-row atoms, **12 hit a naive fork-heuristic and 0 show a silent PASS-to-FAIL regression** — both numbers are honest, both need a synthetic overlay to drive the actual discriminator (mirroring self_query_v1's own finding that "real PASS-vs-FAIL conflicts are essentially absent on disk"). The second rung — **substrate-native ledger-coverage self-detection** — reuses a DIFFERENT already-CHAIN_GRADE primitive (`KGStore.refuse_gate_calibrate`, CERT 585: refuse_OOD=0.999, in-KB-accept=0.997) pointed at a new corpus (the raw `exp_*` directory listing) to answer, natively, the exact audit-debt question `tools/audit_full_coverage.py` currently answers only in hand-written Python. A third rung — **justification/evidence retrieval** ("why does this verdict hold," the genuinely new 60%-novel mechanism class in this ladder) — is real and high long-term value but currently **data-starved**: `grep` this drill confirms **zero cells** besides the just-landed selftest actually populate the brand-new `gate_claims` field yet, so it is correctly sequenced AFTER an adoption/backfill wave, not built now. A fourth, lowest-priority rung (methodology-compliance cross-audit) is flagged honestly as the one closest to `hdi_skunkworks`'s existing job and the least novel of the four. **The honest line, restated concretely for all four:** every rung here only ever WRITES its own `metrics.json` (a report); none ever writes to `cert_ledger.jsonl`, edits a cell's code, or auto-dispatches a fix — in Nelson & Narens' (1990) terms, all four are pure **monitoring** (object-level -> meta-level), never **control** (meta-level -> object-level), which is the literature's own name for exactly the boundary the USER wants preserved.

---

## 0. WHERE WE ARE (verified on disk, not asserted)

| Tier | Cell | Verdict (verified this drill) | What it does |
|---|---|---|---|
| Tier 0 | `exp_math_rns_add_chain_v1` | FULL, HARD_PASS (`data/exp_math_rns_add_chain_v1/metrics.json`) | Exact-equality on a derived VALUE: decode + discrete `==` vs a claim. |
| Tier 1 | `exp_cert_ledger_self_query_v1` | SMOKE, HARD_PASS, Task A acc=1.000/gap=0.750, Task B precision=1.000/recall=1.000 (`data/exp_cert_ledger_self_query_v1_smoke/metrics.json`) | Currency retrieval (walk `SUPERSEDED_BY` to the current status) + same-subject conflict flagging, both via the substrate's own CHAIN_GRADE KGStore retrieval. |
| Tier 2 | `exp_cert_ledger_numeric_entailment_v1` | SMOKE, HARD_PASS, op_agreement=1.000, flag_recall=1.000, retrieval_hit_rate=0.145 (`data/exp_cert_ledger_numeric_entailment_v1/metrics.json`) | Numeric threshold entailment: does a cited `metric op threshold` actually hold — via exact-match ledger retrieval + the RNS half-range/CRT comparator. |
| Infra | `experiments/_seed_checkpoint.py` `record_gate()`/`write_metrics(..., gate_claims=)` | Landed, commit `0e871ff2a`, backward-compatible (verified: byte-identical selftest) | Opt-in structured `gate_claims` field so future cells self-document HARD-PASS/HARD-FAIL bands machine-cleanly, fixing Tier 2's free-text-audit weakness for FUTURE cells. **Adoption check this drill: `grep -rl "gate_claims=" experiments/*.py` returns only `_seed_checkpoint.py` itself — zero cells besides the infra's own selftest populate it yet.** |

Direct re-measurement this drill (read-only, no repo writes, same method the tier2_selfcheck sibling note used):

| Measurement | Value |
|---|---|
| `cert_ledger.jsonl` total rows / unique atom_ids | 1446 / 1362 |
| Multi-row atoms (real revision/lineage candidates) | 44 |
| Multi-row atoms with >1 distinct `cert_status` | 11 (matches the capability-gap sibling note) |
| Multi-row atoms hitting a naive fork-heuristic (>1 row with no `supersedes` predecessor) | 12 of 44 — **honest caveat**: this heuristic cannot yet distinguish a genuine fork (two unlinked claims about the same lineage) from an innocuous atom_id-string collision across two otherwise-unrelated independent atoms (e.g. `math::T3/EXP_u1_fb15k237_ingest_eval_v1` appearing twice is very plausibly two separate landed passes, not a contested lineage) — exactly the same "candidate, not confirmed" honesty the numeric_entailment cell already applies to its own free-text audit byproduct. |
| Multi-row atoms showing a later-row PASS-family -> FAIL-family transition (silent regression pattern) | **0 of 44** — consistent with the self_query sibling note's finding that genuine PASS-vs-FAIL conflicts are essentially absent on real data; any monotonicity-violation discriminator needs a constructed synthetic overlay to fire at all, same design pattern self_query_v1 already used. |
| Real ledger rows whose free-text `note` field contains regression/override/revert-style language | 46 (e.g. `"...non_regressing_proof_..."`) | Informal, unstructured — the SAME structured-vs-free-text gap the `gate_claims` fix addresses for Tier 2 exists here too; a future structured `lineage_override` field would strengthen a monotonicity check the same way `gate_claims` strengthens numeric entailment. Not built now (out of scope; noted for sequencing). |
| Ledger-coverage gap (from the tier2_selfcheck sibling note, re-cited not re-measured) | 950/5744 (16.5%) of on-disk `exp_*` dirs are ever atomized into the ledger — a known, independently-audited (`tools/audit_full_coverage.py`, 2026-06-28) systemic gap. |

---

## 1. THE LADDER (ranked by value x feasibility x not-gated-on-the-parked-remote-deploy)

| Rank | Rung | Anchor (proposed) | Gated on remote deploy? | Recombination vs new (Q3, see Sec. 3) | P_deflated |
|---|---|---|---|---|---|
| **1 (TOP)** | Global cert-graph consistency (cycle-freedom + fork-freedom + tier-monotonicity, swept over the WHOLE ledger) | `exp_cert_ledger_global_consistency_v1` | No — pure local ledger data, same ~1450-row scale as landed self_query_v1 | ~65-70% reuse / ~30-35% new | **0.50** (capped, novel-synthesis) |
| 2 | Substrate-native ledger-coverage self-detection ("which of my own atoms have I never certified") | `exp_cert_ledger_coverage_gap_v1` | No — filesystem scan + refuse-gate, no GPU, no live remote referent | ~80% reuse / ~20% new | **0.45** |
| 3 | Justification / supporting-evidence retrieval ("why does this verdict hold" — retrieve the premise-set, not just re-check a scalar) | `exp_cert_ledger_justification_retrieval_v1` | No, but **data-starved**: needs a `gate_claims` adoption/backfill wave first (currently zero real cells populate it) | ~40% reuse / ~60% new (genuinely different query SHAPE: returns a set, not a boolean/scalar) | 0.35 (deferred, not scoped to a full cell yet) |
| 4 (lowest priority) | Methodology-compliance cross-audit (re-verify a cell's own self-reported `arms_differ_verified`/`cardinality_ok`/`controls_collapsed` booleans against its own underlying arrays, independently of its internal assert) | `exp_cert_ledger_methodology_audit_v1` | No | ~85% reuse / ~15% new — **flagged: this is the rung closest to automating part of `hdi_skunkworks`'s existing AUDIT-ONLY role**; still monitoring-only, but the role-overlap is real and worth naming explicitly rather than glossing over | 0.30 (not scoped to a full cell yet) |

**Why Rung 1 outranks Rung 2** despite Rung 2 being cheaper to build (80% vs 65-70% reuse): Rung 1 closes a gap that is DIRECTLY on the same corpus and mechanism family as both landed cells (extends Tier 1's exact query-answering into whole-graph invariant-checking, the natural next step in the SAME lineage), while Rung 2 opens a NEW corpus (the raw directory listing has never been ingested as a KG before) — slightly more net-new ingest work for a comparable payoff, and its underlying question ("which experiments were never atomized") already has a working, if non-substrate-native, answer (`tools/audit_full_coverage.py`) — so Rung 2's marginal product value is "make an existing answer substrate-native," while Rung 1's is "answer a question nobody has asked yet" (no tool anywhere currently checks the ledger for cycles/forks/silent regressions). Both are legitimate, cheap, PARALLEL next steps; Rung 1 is recommended first only on marginal value, not because Rung 2 is unready.

**Why Rung 3 is real but not built now:** its core mechanism (retrieve the SET of `structured_gate_claims`/dependency-cells that justify a stored verdict) is the single most genuinely-novel item in this ladder — a query that returns a JUSTIFICATION SET rather than a boolean or scalar, structurally the closest thing in this ladder to actual "explain yourself" capability, and the natural completion of the Doyle/de Kleer TMS analogy already banked in the self-reasoning capability-gap sibling note. But it needs real `gate_claims` data to test against, and `grep` this drill confirms there is none yet (the field landed hours ago, opt-in, zero adopters). Recommend revisiting once either (a) >=10-20 newly-authored cells populate `gate_claims` in the normal course of work, or (b) the already-scoped backfill sidecar (`tools/backfill_structured_gate_claims.py`, spec'd in the tier2_selfcheck sibling note, not yet executed) lands and populates the ~476 cleanly-named historical files.

---

## 2. THE TOP-RUNG CELL SPEC — `exp_cert_ledger_global_consistency_v1` (ready for exp_dev pickup, local-smoke-buildable now)

**Design principle**: reuse `exp_cert_ledger_self_query_v1`'s exact graph-build (`build_graph`, `SUPERSEDED_BY`/`HAS_STATUS`/`SAME_SUBJECT` relations, `KGStore`), its `currency_walk` (already carries a `visited` set that halts on revisit — never previously surfaced as an explicit flag), and its `tier_family`/`is_contradiction` logic — VERBATIM import, not reimplementation — and add a GLOBAL SWEEP wrapper plus two new invariant classes the landed cell never checked. This is the same "point the proven mechanism at a new but structurally analogous question" move that made Tier 1 correctly-scoped in the first place.

**Ingest**: identical to self_query_v1 — real `cert_ledger.jsonl` (44 real multi-row atoms) + a constructed synthetic overlay (needed because real conflicts/forks are sparse-to-absent, per Sec. 0's measured numbers — exactly the same "constructed drives the discriminator, real data is the false-positive check" design self_query_v1 already used).

**Three tasks, reported as THREE INDEPENDENT discriminators** (per the "don't collapse to one verdict string" discipline both landed sibling cells already follow):

- **GS-1 (cycle detection)**: for every subject with >=2 rows, run `currency_walk` with its existing `visited`-set logic promoted to an explicit output (`cycle_detected: bool`, true iff the walk revisits a node before `MAX_WALK`). Ground truth: constructed subjects with an injected cyclic `SUPERSEDED_BY` loop (A supersedes B supersedes C supersedes A, label=True) vs constructed proper linear chains (label=False). Real-data byproduct: report (not gate on) cycle count over the real 44 lineage atoms — expected 0, a null/false-positive check like self_query_v1's own real-conflict check.
- **GS-2 (fork detection)**: for every subject, count rows with NO `supersedes` predecessor within that subject's own row-set; >1 such "root" = a FORK (two unlinked claimed-lineages under one subject label, i.e. no path connects them). Ground truth: constructed subjects with two genuinely independent, deliberately-unlinked 2-row lineages sharing one subject label (label=True) vs constructed single properly-linked chains (label=False). Real-data byproduct: report the measured 12/44 naive-fork-heuristic hits as an **UNCONFIRMED audit candidate list** (mirroring numeric_entailment's own `candidate_miscited_inequalities` framing exactly) — explicitly flagged that manual review is needed to separate genuine forks from atom_id-string collisions across unrelated independent atoms, since this drill's own quick heuristic cannot yet distinguish them. Do NOT gate HARD-PASS on the real-data count; gate only on the constructed ground truth.
- **GS-3 (tier-monotonicity along a resolved chain)**: for every chain with a genuine, LINKED `SUPERSEDED_BY` path (excludes fork rows from GS-2), walk oldest -> newest and check `tier_family` never regresses PASS -> FAIL without an explicit override annotation. Ground truth: constructed chains with an injected silent regression (label=True) vs constructed normal upgrades/same-family transitions (label=False) vs constructed chains with an EXPLICIT override note (should NOT be flagged — a documented revision, not a silent one). Real-data byproduct: 0/44 — a null check, not a discriminator driver (same honest limitation self_query_v1's Task B already disclosed for real PASS-vs-FAIL conflicts).

**Discriminator (all three tasks)**: reuse self_query_v1's exact scrambled-`SUPERSEDED_BY`-target-permutation control, unmodified. Must collapse GS-1/GS-2/GS-3 detection accuracy toward chance on all three.

**Pre-registered bands (deflated per role discipline; independent per task, not blended into one verdict string):**

| Task | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| GS-1 cycle detection | recall >= 0.90 on injected cycles AND zero false-positives on the 32/44 real forkless/cycle-free chains AND scrambled control <= 0.20 | recall <= 0.60 OR any false positive on real cycle-free chains OR scrambled control > 0.40 | 0.60-0.90 recall |
| GS-2 fork detection | recall >= 0.90 on constructed genuine forks AND zero false positives on constructed proper chains (real-data 12/44 candidates reported, not gated) | recall <= 0.60 on constructed forks OR any false positive on constructed proper chains | 0.60-0.90 recall |
| GS-3 tier-monotonicity | recall >= 0.90 on constructed silent regressions AND zero false positives on constructed documented-override chains and on the real 0/44 null set | recall <= 0.60 OR any false positive on documented-override chains (a Goodhart/precision failure, worse than a null result — same framing self_query_v1's own Task B band table already used) | 0.60-0.90 recall |

**Overall verdict**: report GS-1/GS-2/GS-3 as three independent tiers exactly as self_query_v1 reports Task A/Task B independently; a GS-1 HARD-PASS + GS-2 MIDDLE + GS-3 HARD-PASS is a legitimate, honestly-reportable partial result, not a forced single collapse.

**Cost**: cheap, CPU-only, same ~1450-row ledger scale as the landed cell; reuses `build_graph`/`currency_walk`/`tier_family` by import, not reimplementation; estimated ~100-150 new lines for the sweep wrapper, the two new invariant-detection heads, and the three synthetic injectors. Order of an afternoon of `hdi_exp_dev` authoring + smoke — not gated on the parked remote-deploy blocker (pure local ledger read, same as self_query_v1, unlike numeric_entailment's FULL which reads the live autonomous-pipeline referent).

**Honest scope note (restated per USER-LOCKED discipline)**: this cell only ever FLAGS a cycle/fork/regression in its own `metrics.json` output. It never edits `cert_ledger.jsonl`, never re-labels a row's `cert_status`, never triggers a re-dispatch. A human or `hdi_skunkworks` acts on the flag; the substrate only monitors.

---

## 3. HONESTY AUDIT (Q3) — recombination vs genuinely new, per rung

None of the four rungs invents a wholly new substrate PRIMITIVE from scratch. All four compose or extend mechanisms that are ALREADY chain-graded (KGStore multi-hop retrieval + `visited`-set cycle-guard; `refuse_gate_calibrate` confidence-threshold OOD refusal, CERT 585; the exact CRT/half-range comparator) and point them at a new but structurally analogous QUESTION or CORPUS. This is by design — Sec 2a of the self-reasoning capability-gap sibling note established "reuse the proven retrieval mechanism, don't chase a new one" as the correctly-scoped move after the closed `substrate_self_map` clustering negative — and it is also the cleanest, most honest way to state why none of this crosses into self-improvement (Sec. 5).

- **Rung 1 (global consistency)**: ~65-70% recombination (self_query_v1's exact graph-build, walk, tier_family, and scramble control, verbatim) + ~30-35% genuinely new: (a) a GLOBAL SWEEP wrapper that evaluates the invariant across the WHOLE graph simultaneously rather than answering one hand-picked query, and (b) two invariant CLASSES self_query_v1 never checked — fork-detection (self_query_v1 only ever walked FORWARD from a single named start) and monotonicity-along-an-established/LINKED chain (Task B only ever checked disagreement between UNLINKED rows, never regression within a RESOLVED lineage).
- **Rung 2 (coverage-gap self-detection)**: ~80% recombination (`refuse_gate_calibrate` is copy-paste-proven, already CHAIN_GRADE at CERT 585) + ~20% new: a corpus never before ingested as a KG (the raw `exp_*` directory listing, ~5744 entities) and one new relation type (`HAS_LEDGER_ROW`).
- **Rung 3 (justification retrieval)**: ~40% recombination (the underlying multi-hop retrieval machinery) + ~60% genuinely new: a new relation type linking a verdict-entity to a SET of evidence/premise-entities, and a fundamentally different query SHAPE (return a justification set, not a scalar/boolean) — the first rung in this ladder that is genuinely "explanation" rather than "check."
- **Rung 4 (methodology-compliance audit)**: ~85% recombination (re-reads the SAME per-seed/per-unit arrays a cell's own internal `assert` already checked at authorship time) + ~15% new: doing it as an INDEPENDENT SECOND pass via substrate retrieval rather than trusting the original process's own internal check — a "verify the verifier" pattern, real but the least novel of the four, and the one with the most direct role-overlap with `hdi_skunkworks`'s existing AUDIT-ONLY job (named explicitly, not glossed over).

---

## 4. BRAIN GROUNDING (Q4) — honest analog, not task analog

Reused from the two same-day sibling notes (not re-derived): dorsal-ACC conflict-monitoring as a retrieval-margin byproduct (Botvinick et al. 2001; van Veen et al. 2009), Nelson & Narens' (1990) monitoring/control split, Fleming et al.'s (2010) anterior-PFC structural correlate of metacognitive accuracy, Johnson & Raye's (1981) reality/source monitoring, Koriat's (1993) accessibility model. Two TARGETED new lit-scans this drill (generic terms only, no substrate-novel names off-platform) extend this grounding specifically for Rungs 1 and 2, which needed genuinely different citations (checking a SET of beliefs jointly, and reasoning correctly about ABSENCE, are both distinct literatures from pairwise conflict-monitoring):

**For Rung 1 (global/joint consistency over a SET, not a pair):**
- **Thagard's Explanatory Coherence / ECHO** (Thagard 1989, *Behavioral and Brain Sciences* 12(3):435-467; Thagard & Verbeurgt 1998, *Cognitive Science* 22(1):1-24) — a connectionist constraint-satisfaction network where propositions are nodes, positive/negative links encode mutual support/contradiction, and the WHOLE network relaxes to a joint stable state (Hopfield-like), not pairwise iteration. Directly the right mechanism-class citation for "does a SET of claims cohere," distinct from ACC pairwise-conflict-monitoring. Honest caveat (fetch-verified): Thagard & Verbeurgt proved maximizing total coherence is equivalent to MAX-CUT (NP-hard) — ECHO is a heuristic relaxation, not a guaranteed solver; the substrate's cycle/fork/monotonicity checks below are much narrower, exactly-decidable graph properties (P-time, not NP-hard), which is an honest STRENGTH of the narrow scoping, not an oversight — GS-1/2/3 are deliberately NOT attempting general coherence maximization.
- **Coherentism as philosophy vs. algorithm** (BonJour; Lehrer; SEP entry on coherentist justification, fetch-verified) gives no computable procedure on its own; Cherniak's *Minimal Rationality* (MIT Press, 1986) sharpens this into an explicit computability objection — full belief-set consistency-checking is intractable for a realistic agent in general, motivating BOUNDED checks (exactly what GS-1/2/3's narrow, decidable graph invariants are) rather than a claim of general coherence-checking.
- **de Kleer's ATMS** (*Artificial Intelligence* 28(2), 1986) computing N-ARY "nogoods" (minimal jointly-inconsistent sets of 3+ elements, not just pairs) and Doyle's original TMS (1979) requiring GLOBAL acyclicity of the justification graph — these are the direct AI-literature ancestors of GS-1 (cycle/acyclicity) and the multi-way generalization GS-2/3 aim at.
- **Dalege et al.'s Causal Attitude Network (CAN) model** (*Psychological Review* 123(1), 2016; tutorial *Soc. Psych. & Personality Sci.* 8(5), 2017, fetch-verified) — an Ising-type network where attitude coherence is a joint energy function over the WHOLE configuration, and "network dissonance" (a whole-network quantity) predicts belief change better than any single pairwise conflict, in real longitudinal human data (vaccine/GMO-skepticism studies). Honest gap flagged by the lit-scan: no single-neuron/fMRI mechanism was found that computes this joint signal directly (as opposed to psychometric network modeling) — this is real behavioral/formal evidence for joint coherence-tracking mattering, not confirmed neural-locus evidence, an honest boundary not to over-claim past.

**For Rung 2 (reasoning correctly about ABSENCE / coverage gaps):**
- **Confidence-threshold OOD/open-set detection** (Hendrycks & Gimpel 2017, ICLR/arXiv:1610.02136; Bendale & Boult 2016 CVPR "OpenMax"; Liu et al. 2020 NeurIPS energy-based OOD; Geng et al. TPAMI open-set-recognition survey) — direct precedent for "a calibrated confidence threshold separates in-index accept from out-of-index refuse," which is exactly `refuse_gate_calibrate`'s own mechanism. Sharp, load-bearing caveat from this literature: naive confidence thresholds are known to be brittle specifically when an unindexed real-world item happens to be FEATURE-SIMILAR to an indexed one — a genuine risk for Rung 2's design that should be an explicit control arm (a near-miss unindexed-but-similar directory name) when this rung is eventually built.
- **Reiter's Closed-World Assumption** (1978, *Logic and Data Bases*) and the standard CWA-vs-OWA distinction (Brachman & Levesque) — the conceptually correct framing for Rung 2's semantics: the refuse-gate must output "not covered / unknown" (OWA-style), never "does not exist" (CWA-style negation) — Reiter's own soundness result (CWA-negation is safe only for Horn/complete fragments) is useful ammunition for exactly when a low-confidence refuse score is trustworthy as a genuine completeness signal vs. merely a confidence artifact.
- **Razniewski & Nutt's database-completeness calculus** (VLDB 2011, PVLDB 4(11):749-760; CIKM 2012 follow-up) — a genuinely DIFFERENT, DECLARATIVE approach (a database can prove certain sub-answers are complete against explicitly-declared complete regions) rather than a statistical confidence signal — flagged as structurally complementary to, not a replacement for, `refuse_gate_calibrate`'s confidence-threshold approach; worth a future v2 enhancement (declare which ledger regions are known-complete) rather than relying on tau alone.
- **Coane & Umanath (2019, *J. Memory and Language* 107:152-168)** — the clean, more specific-than-Koriat human-cognition split between accessibility failure ("don't remember" — encoded, retrieval failed) and availability failure ("don't know" — never encoded at all). Directly supports a two-way design for Rung 2's tau-gate: distinguish a CONFIDENTLY-low score (genuinely never indexed) from an AMBIGUOUS/contested score (indexed but noisy) rather than collapsing both to one threshold — a concrete, literature-grounded refinement for when Rung 2 is built, not glossed over as "just lower the threshold."

**Honest disanalogy (restated, standing discipline)**: none of the human/psychometric mechanisms above are claimed to transfer at the level of implementation detail — ECHO's Hopfield-style relaxation is a heuristic approximator of an NP-hard objective, while GS-1/2/3 are exact, P-time, narrowly-scoped graph checks; the brain's OOD/absence-detection machinery is continuous and graded (Weber's-law-style), while `refuse_gate_calibrate`'s tau is a single hard threshold. The literature is used at the level it is genuinely well-supported (joint/set-level coherence-tracking exists and matters; absence-reasoning is dissociable from retrieval-failure-reasoning) — not over-extended to claim the substrate replicates brain mechanism, per standing [[feedback-mechanism-abstraction-lossy]] discipline.

---

## 5. THE HONEST LINE (Q5) — where narrow self-CHECK ends and self-improvement begins

Two independent, mutually-reinforcing ways to state the same boundary, so no rung in this ladder (or any future one built on this pattern) can drift across it unnoticed:

1. **Monitor vs. control (Nelson & Narens 1990, already banked).** Cognition splits into an object-level (doing/producing) and a meta-level (modeling the object-level), linked by two DISSOCIABLE flows: monitoring (object -> meta, "what is the state of X") and control (meta -> object, "change X based on what I found"). Every rung in this ladder — landed Tier 0/1/2 and all four proposed next rungs — implements ONLY monitoring. None ever writes to `cert_ledger.jsonl`, edits a cell's code, relabels a `cert_status`, or auto-dispatches a follow-up cell based on what it finds. A human or `hdi_skunkworks` reads the flag and decides what, if anything, to do. The moment any future rung closes that loop itself (auto-relabels a flagged fork, auto-triggers a "fix" cell without review, or uses its own detected gaps to autonomously change which mechanism it deploys next time) — that crosses from monitoring into control, i.e. into self-improvement, and is explicitly out of scope for this whole ladder.
2. **Reuse-of-proven-mechanism vs. autonomous-creation-of-new-mechanism (restated from Sec. 3).** Every rung here — including the most novel one, Rung 3's justification retrieval — takes a mechanism ALREADY validated (by a human-authored, human-reviewed cell) and points it, via human/`research`/`hdi_exp_dev` authorship, at a new but structurally analogous question. None of these rungs has the substrate itself autonomously invent, select, or compose a NEW mechanism in response to a gap it detected, without a human designing that response. That is the genuine, structural difference between "the substrate checks itself" (this ladder) and "the substrate improves itself" (still fully USER-locked out, per the standing directive) — not merely a scope label applied after the fact.

Both framings independently agree on the same answer for all four rungs in this note: all are safely on the monitoring/reuse side of the line.

---

## Cheap decisive test

Build and run `exp_cert_ledger_global_consistency_v1 --smoke` locally (no GPU, no queue dispatch). If GS-1/GS-2/GS-3 each independently clear their HARD-PASS bands (Sec. 2) with the scrambled control collapsing on all three, that is the decisive confirmation that the "single hand-picked query" -> "whole-graph sweep" generalization composes cleanly on top of the two already-landed cells, with no new failure mode introduced by scaling the SAME mechanism from one query to ~1450 rows swept exhaustively. This is a single afternoon's local smoke run, independent of and not gated on the parked USER-auth remote-deploy blocker.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, repeated from Sec. 2 for scan-ability)

- GS-1 HARD-PASS: cycle-recall >= 0.90 on injected cycles, zero false positives on the 32/44 real cycle-free chains, scrambled control <= 0.20. HARD-FAIL: recall <= 0.60 OR any real false positive OR scrambled control > 0.40.
- GS-2 HARD-PASS: fork-recall >= 0.90 on constructed genuine forks, zero false positives on constructed proper chains (real 12/44 candidates reported, not gated). HARD-FAIL: recall <= 0.60 on constructed forks OR any false positive on constructed proper chains.
- GS-3 HARD-PASS: regression-recall >= 0.90 on constructed silent regressions, zero false positives on constructed documented-override chains and the real 0/44 null set. HARD-FAIL: recall <= 0.60 OR any false positive on documented-override chains.
- Report GS-1/GS-2/GS-3 as three independent discriminators; do not collapse to one verdict string.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_self_reasoning_capability_gap_2026-07-05.md`**: that note's Sec 2a design principle ("reuse the retrieval mechanism, not the closed clustering mechanism") is the exact move Rung 1 and Rung 2 both make again, one level up the ladder; its Sec 4 brain-grounding (ACC-conflict-monitoring-as-margin, Nelson & Narens, Johnson & Raye, Koriat, Doyle/de Kleer TMS) is reused, not re-derived, here.
- **With `notes/research_entailment_self_check_first_cell_2026-07-05.md`**: that note's Tier 0/1/2 taxonomy is the direct scaffold Sec. 0 of this note extends; its comparison-specific brain grounding (symbolic distance effect, Dehaene double-dissociation, parietal/PFC magnitude-vs-rule split) is a distinct, non-overlapping citation set from this note's coherence-theory and OOD-detection additions.
- **With `notes/research_tier2_selfcheck_structured_field_2026-07-05.md`**: that note's `gate_claims` infra spec is what Rung 3 is sequenced behind; its Koriat-derived three-way failure taxonomy (indexing/access failure, matching/evaluation failure, conflict-detection) is extended here by Coane & Umanath's sharper accessibility-vs-availability distinction for Rung 2.
- **With `hdlab/kg_traversal.py`**: `refuse_gate_calibrate` (CERT 585, refuse_OOD=0.999) — read in full this drill — is confirmed as the exact reusable mechanism for Rung 2, not a new build.
- **With [[feedback-research-every-finding-for-mechanism-and-envelope-push]]**: the honest null findings this drill measured directly (0/44 real regressions, 12/44 real fork-candidates needing a caveat) are treated as design inputs for the synthetic-overlay discriminator, not glossed over as "nothing to report."
- **Brain-component-driven development thrust (2026-07-05 standing USER thrust)**: this note adds "joint/set-level coherence-tracking" (Thagard ECHO / Dalege CAN-model) and "calibrated-confidence absence-reasoning" (OOD/CWA/completeness literature) as two candidate framings for the still-untracked "metacognition" brain-component slot the self-reasoning capability-gap note first flagged as absent from the inventory — not a new build target itself, but two additional literature anchors for whenever that component is formally scoped.

## SUBSTRATE-PRODUCT IMPLICATIONS

- If Rung 1 (`exp_cert_ledger_global_consistency_v1`) HARD-PASSes: the substrate gains a native, whole-ledger integrity check — catching cycles, forks, and silent regressions across its ENTIRE certification history using its own retrieval machinery, not a hand-written Python audit script. This is a genuine, demonstrable strengthening of "canon-1st" trust in the cert-ledger as the substrate's own record, at near-zero marginal engineering cost (an afternoon, no GPU).
- If Rung 2 lands next: the substrate can answer "which of your own experiments have you never certified" natively — directly upgrades the existing hand-rolled `tools/audit_full_coverage.py` answer into a substrate-native one, reusing an already-CHAIN_GRADE primitive on a new corpus.
- Rung 3 (justification retrieval) is the correctly-sequenced NEXT step after a `gate_claims` adoption wave — the genuinely novel "explain yourself" capability this ladder is building toward, not skipped, just honestly gated on data that does not exist yet.
- None of the four rungs, even at full HARD-PASS, reopens Phase 2/3 (autoatom, substrate-proposed new mathematics) of the USER's core-mathematics strategic vision, nor the still-CLOSED structure-discovery/self-mapping problem (`substrate_self_map` v2-v2f) — this ladder stays entirely within Tier 0/1/2's honest scope, extended to whole-graph and whole-corpus questions rather than single hand-picked ones.

---

## CITATIONS (verified external count this drill: 9 new for Rung 1 + 10 new for Rung 2 = 19, plus reused citations from same-day sibling notes not re-counted)

**New this drill — Rung 1 (coherence/global-consistency lit-scan):**
1. Thagard, P. (1989). "Explanatory Coherence." *Behavioral and Brain Sciences*, 12(3), 435-467.
2. Thagard, P. & Verbeurgt, K. (1998). "Coherence as Constraint Satisfaction." *Cognitive Science*, 22(1), 1-24.
3. Stanford Encyclopedia of Philosophy, "Coherentist Theories of Epistemic Justification" (fetch-verified).
4. Cherniak, C. (1986). *Minimal Rationality*. MIT Press.
5. de Kleer, J. (1986). "An Assumption-Based TMS." *Artificial Intelligence*, 28(2), 127-162.
6. Doyle, J. (1979). "A Truth Maintenance System." *Artificial Intelligence*, 12(3), 231-272. (also cited by the capability-gap sibling note; re-confirmed here for the acyclicity requirement specifically)
7. Dalege, J. et al. (2016). "Toward a Formalized Account of Attitudes: The CAN Model." *Psychological Review*, 123(1), 2-22.
8. Dalege, J. et al. (2017). "Network Analysis on Attitudes: A Brief Tutorial." *Soc. Psychological and Personality Science*, 8(5), 528-537 (fetch-verified).
9. Dalege, J. & van der Does, T. (2022). "Using a Cognitive Network Model of Moral and Social Beliefs to Explain Belief Change." *Science Advances*, 8, eabm0137 (search-snippet-corroborated; not full-text fetch-verified, flagged).

**New this drill — Rung 2 (OOD/absence-reasoning lit-scan):**
10. Hendrycks, D. & Gimpel, K. (2017). "A Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks." ICLR / arXiv:1610.02136.
11. Bendale, A. & Boult, T. (2016). "Towards Open Set Deep Networks" (OpenMax). CVPR 2016.
12. Liu, W., Wang, X., Owens, J., & Li, Y. (2020). "Energy-based Out-of-Distribution Detection." NeurIPS 2020.
13. Geng, C., Huang, S., & Chen, S. (2020/2021). "Recent Advances in Open Set Recognition: A Survey." IEEE TPAMI.
14. Reiter, R. (1978). "On Closed World Data Bases." In *Logic and Data Bases*, Springer.
15. Brachman, R. & Levesque, H. *Knowledge Representation and Reasoning* (CWA vs. OWA treatment).
16. Razniewski, S. & Nutt, W. (2011). "Completeness of Queries over Incomplete Databases." PVLDB 4(11):749-760.
17. Nutt, W. & Razniewski, S. (2012). "Completeness of Queries over SQL Databases." CIKM 2012.
18. Coane, J.H. & Umanath, S. (2019). "'I Don't Remember' vs. 'I Don't Know': Phenomenological States Associated with Retrieval Failures." *Journal of Memory and Language*, 107, 152-168.
19. (Unverified, flagged not counted toward confirmed total) a bioRxiv preprint on preschooler "meta-ignorance" — fetch returned 403, not independently confirmed; not relied upon in Sec. 4's claims.

**Reused, not re-counted (already verified by same-day sibling notes)**: Botvinick et al. 2001/2004; van Veen et al. 2009; Nelson & Narens 1990; Fleming et al. 2010; Johnson & Raye 1981; Johnson/Hashtroudi/Lindsay 1993; Koriat 1993; Moyer & Landauer 1967; Dehaene & Cohen 1997; Nieder & Miller 2003/2004; Vallentin & Nieder 2013; Fellegi & Sunter 1969; Christen 2012.

**Substrate-internal (verified on disk this drill, not counted toward external total but load-bearing):**
- `data/exp_math_rns_add_chain_v1/metrics.json` (FULL, HARD_PASS, re-verified this drill)
- `data/exp_cert_ledger_self_query_v1_smoke/metrics.json` (SMOKE, HARD_PASS, re-verified this drill)
- `data/exp_cert_ledger_numeric_entailment_v1/metrics.json` (SMOKE, HARD_PASS, re-verified this drill)
- `experiments/exp_cert_ledger_self_query_v1.py`, `experiments/exp_cert_ledger_numeric_entailment_v1.py` (both read in full this drill)
- `experiments/_seed_checkpoint.py` (gate_claims/`record_gate` landed, 0e871ff2a; adoption-count verified this drill via grep: zero non-infra cells)
- `hdlab/kg_traversal.py` (`refuse_gate_calibrate`, CERT 585, read this drill)
- `data/substrate_index/meta/cert_ledger.jsonl` (1446 rows, direct re-measurement this drill: 44 multi-row atoms, 11 distinct-status, 12 fork-heuristic hits, 0 regressions, 46 informal-override-language rows)
- `notes/research_self_reasoning_capability_gap_2026-07-05.md`, `notes/research_entailment_self_check_first_cell_2026-07-05.md`, `notes/research_tier2_selfcheck_structured_field_2026-07-05.md` (all three read in full this drill)

---

*Research complete 2026-07-05. Field advisor run (no matching tracked field; noted, consistent with all three same-day sibling notes). Direct on-disk re-measurement performed via a read-only scratch script (no repo writes) before any external dispatch. 2 parallel Sonnet lit-scans (explanatory-coherence/global-consistency; OOD-detection/closed-world/absence-reasoning), generic terms only, no substrate-novel mechanism names off-platform. Lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis cap 0.50 — applied to Rung 1's P_deflated=0.50). HARD-FAIL thresholds specified for the top-rung cell spec. Notes-only drill per Director instruction — no cell built, no routing files (USER-locked ferry-deprecation override; all actionable content, including the ready cell spec, delivered in this note).*
