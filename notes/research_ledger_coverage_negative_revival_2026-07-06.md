# Research note: 2x negative-result revival drill -- cert-ledger self-audit coverage HARD_FAIL

Filed by: research (2x drill, USER-triggered "drill negative results")
Trigger: `exp_cert_ledger_retrieval_coverage_v1` HARD_FAIL (near-vacuous self-audit coverage; ceiling_recoverable_frac ~0.04-0.16)
Scope: mechanism deepening (substrate scour) + internet lit-scan (3 parallel Sonnet sub-agents, generic terms only) + revival ranking

---

## (a) HEADLINE

**The bottleneck is not retrieval, and it is not even mainly "non-atomized cells." It is that the cert-ledger's own append-only WRITER SCHEMA has no field to carry a structured numeric claim through — so even the ONE cell in the entire 5822-file corpus that already computes clean structured gate-claims never gets them into the ledger; only a free-text SENTENCE saying "this cell adopted structured claims" survives atomization.** The fix is not a better search algorithm (already proven sound + bounded, confirming the CROSS-CELL LAW again) — it's a two-line schema addition (ledger writer) plus a design change to the audit itself: skip retrieval/matching entirely and re-verify each cell's OWN structured claims directly against its OWN metrics.json (no cross-file join, no cosine cleanup, no ambiguity margin needed, because there is no separate reference set to search — every metrics.json is its own referent). This is confirmed by a concrete demonstration (below): on the one adopting cell, direct entailment recovers all 15 gate-claims with zero retrieval steps and 0 mismatches, while the existing regex-over-free-text harvester finds **zero** claims in that same file's `verdict_msg` (284 chars, no inline numbers) — i.e. the current audit design is **structurally blind** to the best-instrumented cell in the corpus.

P_deflated (that this is the correct diagnosis and ranking) = **0.55** (mechanism confirmation is a direct filesystem measurement, high confidence; the ranking recommendation is calibrated per lit-scan discipline, deflated 0.15-0.25 from raw confidence, capped <=0.50 on any "obviously correct design" sub-claim).

---

## (b) Cheap decisive test

**Already run (read-only, no cell dispatch) as part of this drill, against the one real corpus file that has structured gate-claims** (`data/exp_cert_ledger_global_consistency_v1/metrics.json`):

```
n structured_gate_claims: 15
direct-entailment mismatches (re-eval op(measured,threshold) vs stored gate_verdict): 0
regex NUM-op-NUM hits in verdict_msg of the SAME file: 0     <- the existing harvester used by
                                                                 both landed audit cells gets ZERO signal here
verdict_msg length: 284 chars (terse; no inline numbers -- the numbers live ONLY in structured_gate_claims)
```

This is the whole finding in miniature: a retrieval-free, direct-recomputation audit (glob `data/**/metrics.json` -> filter to files carrying `structured_gate_claims` -> re-evaluate `op(measured, threshold) == gate_verdict` with the SAME already-VET'd comparator primitive used by `exp_cert_ledger_numeric_entailment_v1`) needs **no retrieval, no ledger join, no ambiguity margin, and no regex** — and it already works, today, on the one cell that has adopted the pattern.

**Next cheap test (for exp_dev, if picked up):** run the identical loop above across all 5822 `metrics.json` files (not just the one) as a SMOKE, confirming `recomputation_agreement` stays 1.0 and coverage-of-present-claims stays 100% at corpus scale, i.e. a trivial glob+re-eval with no capacity/N_DIM sweep needed (this removes an entire axis of complexity the retrieval-coverage cell had to carry).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL)

**P1 -- Direct-entailment recomputation (the core revival mechanism).**
For any cell that adopts `record_gate()` (computes `structured_gate_claims` in its own metrics.json), a retrieval-free audit re-evaluating `op(measured,threshold)==gate_verdict` against the SAME VET'd `decode_then_compare` comparator:
- HARD-PASS: `recomputation_agreement >= 0.999` AND coverage-of-present-claims `== 1.0` (100% of what's there is checked; no matching problem exists by construction).
- HARD-FAIL: `recomputation_agreement < 0.99` (would mean the audit's op-eval disagrees with `record_gate`'s own formula -- a real bug) OR coverage `< 1.0` (would mean the direct-read step itself is broken -- e.g. a schema/parsing regression).

**P2 -- Ledger-schema propagation (additive, backward-compatible field).**
After adding an OPTIONAL `gate_claims` field to `tools/cert_ledger_writer.py`'s schema (mirroring `write_metrics`'s existing opt-in design; reusing `_seed_checkpoint._validate_gate_claims` for validation, DRY) and wiring at least the next atomize wave to pass it through:
- HARD-PASS: >=1 ledger row carries a genuine (non-string, non-empty) `structured_gate_claims` list that matches its source metrics.json verbatim, AND `python tools/cert_ledger_writer.py --self-test` still passes clean (no regression to idempotency/hash/A5 checks).
- HARD-FAIL: the self-test regresses, OR the new field breaks the existing enum/required-field validation for any of the 1467 pre-existing rows (schema must be additive-only).

**P3 -- Adoption-lift under a cell-template convention nudge.**
If `record_gate()` becomes the default HP/HF-gate emission convention for NEW cells (a template/CLAUDE.md convention change, not a retrofit):
- Falsifiable claim: distinct-cell adoption count (currently 1/5822) grows monotonically per landing wave.
- HARD-FAIL (refutes the "soft convention nudge is enough" lever): if after 10 subsequent NEW cell landings adoption count is still <=2, a soft nudge is insufficient and a harder enforcement (CI lint / `write_metrics` warning-on-missing-gate_claims) is needed instead.

**P4 -- Regex-blindness inversion (CONFIRMED, not merely predicted, by the test in (b)).**
Cells that successfully adopt structured gate-claims tend to write terser `verdict_msg` (the numbers moved OUT of prose and INTO the structured field) -- so the EXISTING regex-based harvesters used by `exp_cert_ledger_numeric_entailment_v1` / `exp_cert_ledger_retrieval_coverage_v1` will show **declining** apparent coverage for exactly the best-instrumented cells, unless those cells (or a successor cell) are updated to read `structured_gate_claims` directly. This is a real measurement-inversion risk for whoever owns those two cells' dashboards, flagged here so it isn't mistaken for regression when it's actually adoption succeeding.

---

## Mechanism (deepened; MEASURED@ off-disk 2026-07-06)

1. **The gate-claims machinery already exists and is sound.** `experiments/_seed_checkpoint.py` added (2026-07-05) `record_gate(gate_name, measured, threshold, op, note=None)` -- computes `gate_verdict` at the cell's OWN runtime from its own in-scope values (never re-derived later) -- plus `_validate_gate_claims()` (fail-fast schema check: required keys, valid op enum, non-bool numerics, bool verdict) plus an opt-in `gate_claims` kwarg on `write_metrics()` that persists a `"structured_gate_claims"` top-level key. Fully backward-compatible: `gate_claims=None` (default) produces byte-identical output to the pre-2026-07-05 writer.
2. **Adoption is 1 cell out of the whole corpus.** `grep -rln "gate_claims=" experiments/*.py` (excluding the machinery file itself and the two audit cells under test) returns exactly one hit: `experiments/exp_cert_ledger_global_consistency_v1.py`. A full corpus scan (`glob data/**/metrics.json`, 5822 files) confirms exactly 3 files have a non-empty `structured_gate_claims` key -- the smoke/full/localverify run-variants of that SAME one cell. This matches (and sharpens) the retrieval-coverage cell's own `"corpus_gate_claims_structured": 0` diagnosis field -- which is actually a **hardcoded literal, not a live recomputation** (worth a small honesty note for VET: the true corpus count is 3 files / 1 distinct cell, not 0; doesn't change the verdict, since 1/5822 rounds to the same "near-zero adoption" finding).
3. **Even that one adopter's structured data never reaches the ledger.** `tools/cert_ledger_writer.py` (the sole writer of `data/substrate_index/meta/cert_ledger.jsonl`) has a FIXED, enum-validated schema: `REQUIRED_FIELDS = (op, atom_id, cert_status, cert_class, verified_off_data, atomized_by, cell_commit, verdict, cert_increment_delta, cv, referent_pointer, supersedes, note)`. There is no slot for a claims list. `grep -n "structured_gate_claims" data/substrate_index/meta/cert_ledger.jsonl` returns exactly 5 lines out of 1467 rows, and every one of them is a PROSE MENTION baked into the free-text `atom_id`/`note` sentence-blob (e.g. `"...FIRST_cell_to_adopt_the_structured_gate_claims_field_15_of_15_PASS..."`) -- zero of the 5 carry an actual `structured_gate_claims` JSON key with the 15 claim dicts. The fact was narrated; the data was dropped.
4. **Atomization is not a pipeline, it's dozens of hand-authored one-off scripts.** `tools/atomize_*.py` and `tools/skunkworks_atomize_*.py` (30+ files, one per landing wave) each call `append_cert_ledger_row` / `build_*_row` and hand-compose the `note`/`atom_id` strings (evidenced by the giant snake-case-sentence `atom_id` values seen throughout the ledger). Fixing `cert_ledger_writer.py`'s schema alone would not automatically fix anything -- every future one-off atomize script would ALSO need to remember to read `structured_gate_claims` off the source `metrics.json` and pass it through the new field.
5. **Net effect: the achievable "structured audit" ceiling right now is closer to 0% of the corpus, not the previously-reported ~17%.** The retrieval-coverage cell's "83% of citations are non-atomized" framing is real but incomplete: even the certified/atomized ~17% would ALSO carry zero numeric content today, because atomization drops structured claims at the ledger-write step regardless of whether the source cell computed them.
6. **This directly sharpens the standing roadmap** (`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-06.md`, roadmap `8b90c6667`: "...then justification-retrieval which needs a gate_claims adoption-wave; then methodology-audit"). The roadmap already anticipated needing an adoption-wave -- this drill's filesystem evidence shows the blocker is worse than "need more cells to adopt": even the one adopter's data is currently un-recoverable because the ledger schema has nowhere to put it.

---

## Revival routes, ranked

**#1 -- (c) Retrieval-free direct entailment (build this next; NEW top recommendation).**
Skip cross-file matching entirely. A per-file self-consistency check: for each `metrics.json` that carries `structured_gate_claims`, re-evaluate `op(measured,threshold)==gate_verdict` directly, reusing the SAME `decode_then_compare` comparator already MEASURED_MECHANISM-certified in `exp_math_rns_subtract_compare_v1` / used by `exp_cert_ledger_numeric_entailment_v1`. No cosine cleanup, no `cleanup_family`, no ambiguity refuse-gate, no ledger join at all -- because every file is its own referent (glob already gives full, exact, non-fuzzy access; nothing needs to be "found"). This is the exact design the cross-domain lit-scan (event-sourcing "replay from primary source over projection," golden-record vs materialized-view literature; P=0.55 calibrated) recommends whenever the primary source is fully enumerable without fuzzy matching -- which it is here. It also structurally avoids the CROSS-CELL LAW failure mode (noisy associative readout over near-duplicate identity strings) this same drill just re-confirmed, by removing the associative-readout step altogether rather than trying to make it more precise. Cost: cheap (reuse of an already-VET'd primitive; no capacity/N_DIM sweep needed since there's no encoding/retrieval axis). Coverage denominator becomes "fraction of corpus with non-empty structured_gate_claims" (currently ~0.02%) rather than "fraction of claims matched to a lossy ledger record" (~15-17%) -- smaller today, but sound, monotonically improving, and zero-retrieval-noise.

**#2 -- (a) Emit + propagate structured claims (the upstream feed for #1, not a competitor).**
Two sub-parts, both cheap:
  - (a-i) **Ledger schema fix**: add an OPTIONAL `gate_claims` field to `cert_ledger_writer.py` (additive/nullable field -- the "expand-contract" / parallel-change pattern that schema-evolution literature treats as close to a solved problem for exactly this situation: Confluent/Avro/Protobuf schema-registry docs, P=0.65 calibrated, the highest-confidence finding of the whole scan). Reuse `_seed_checkpoint._validate_gate_claims` for validation (DRY, no new parsing logic). Estimated cost: hours, not days.
  - (a-ii) **Per-cell adoption wave**: make `record_gate()` the default convention for NEW cells (template/CLAUDE.md change), not a retrofit campaign. The record-linkage lit-scan (Fellegi-Sunter and successors; P=0.50 calibrated) explicitly favors "fix reference-set completeness" over "improve the matching algorithm further" once the matcher/margin-gate is already sound (it is -- the retrieval-coverage cell's own scrambled-control collapse + margin-refuse-gate proved that) -- this reframes the fix as growing the referent population, not building a cleverer search.

**#3 -- (b) Regex retrofit-backfill of historical claims into the ledger -- NOT RECOMMENDED as primary route.**
The closest real-world analog in the literature (retrospective clinical-chart NLP/regex abstraction vs prospective structured capture; P=0.45 calibrated) shows retrospective extraction is measurably more error-prone (96%->91% accuracy drop even in the best-studied real case) and the literature separately warns that regex-extracted data that LOOKS structured is MORE dangerous than obviously-free-text data, because it silently encodes parser errors under an authoritative-looking key. This substrate already caught exactly that failure class by hand in `exp_cert_ledger_numeric_entailment_v1`'s own `audit_note` (config-count-vs-metric confusion, garbled shorthand, malformed inline annotations, precision ties -- ALL classified 0/N confirmed on manual review). Automating that same regex into a permanent WRITE-BACK against the ledger would bake those exact error classes into the record of truth. If pursued at all, any retrofit claim must carry an explicit `"source": "regex_retrofit_unconfirmed"` provenance tag, never silently equal-weighted with `record_gate()`-computed claims. Since #1 makes forward progress possible without retrofit (an ever-growing N is enough), rank this last.

---

## (d) Cross-thread synthesis with prior entries

- **CROSS-CELL LAW** (`reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_2026-07-06.md`): this drill is another confirming instance -- the content-addressable retrieval mechanism is sound-but-bounded (scrambled control collapses to 0.0 as expected, margin-refuse-gate correctly rejects ambiguous near-duplicate matches), exactly as the law predicts for noisy associative readout. The revival route (#1) is the natural corollary the law implies but hadn't yet been stated explicitly: **when the referent is fully and exactly enumerable (no fuzzy identity resolution required), route around noisy associative readout entirely rather than trying to make it more precise.**
- **Tier-2 numeric-entailment canonical FULL HARD_PASS** (`exp_cert_ledger_numeric_entailment_v1`, 518 real triples, op_agreement 1.000): confirms the `decode_then_compare` comparator leg is exact and reusable verbatim -- route #1 reuses this SAME primitive, just drops the weak retrieval leg (measured `retrieval_hit_rate=0.0328` at canonical FULL) that this drill's subject cell tried and failed to lift structurally.
- **Roadmap 8b90c6667** (`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-06.md`): declared next rungs were "coverage-gap [this drill's subject] -> justification-retrieval (needs a gate_claims adoption-wave) -> methodology-audit." This drill sharpens that plan: the adoption-wave blocker is a **two-gap** problem (per-cell adoption AND ledger-writer schema), not the one-gap problem the roadmap assumed, and proposes a retrieval-free audit design that doesn't have to wait for either gap to fully close before producing a real (if initially small) signal.
- **Session cumulative self-reasoning ladder status** (status log, last `research_delivery`-adjacent entries): Tier-1 self-query HARD_PASS, Tier-2 numeric-entailment HARD_PASS (both canonical), Tier-3 global-consistency PARTIAL, this coverage cell HARD_FAIL. The "NEXT IMPROVEMENT TARGET" named in that log entry was explicitly "Tier-2 retrieval-coverage (0.033 -> the real lever for a meaningful self-audit)" -- this note's route #1 is the concrete answer to that named target.

---

## (e) Substrate-product implications

A substrate that can audit its own certification claims without fragile text-parsing is a concrete trust/compliance capability, not a research curiosity: it's the mechanism that would let an "explain your confidence" or "show your work" product surface re-verify a specific claim on demand, deterministically, without brittle NLP over log prose. The retrieval-free direct-entailment design (#1) plus additive structured-claim emission (#2) is the SAME practice (schema-on-write, write-time structured capture over retrospective free-text parsing) that compliance- and audit-focused literature treats as close to a solved-problem norm for any system that needs to answer "does this recorded decision actually follow from the number behind it" -- which is exactly the auditable-memory-subsystem product direction already on file. The near-term product-visible effect of NOT fixing this: any "self-audit" or "confidence provenance" feature built on the current ledger would be citing a near-empty audit trail (an honesty risk if ever surfaced to a customer) rather than a genuinely checkable one.

---

## (f) Citations (verified count)

**24 distinct external sources** verified across 3 parallel Sonnet lit-scans (generic terms only, per query-privacy discipline):
- Software/data-engineering + provenance-standards scan (9 sources): Dremio schema-on-read-vs-write; DriveDataScience; Microsoft Azure Architecture Center (Event Sourcing pattern); Mia-Platform (Event Sourcing/CQRS); ACM/EDBT PROV paper; arXiv PROV-AGENT; dev.to structured-logging best practices; Last9 log-parsing; Confluent schema-evolution docs; Conduktor; Decodable; Sesame Disk (regex log-parsing risk); PMC retrospective chart-review study; PMC NLP chart-abstraction study; Improving.com (GIGO/automation bias); youngju.dev + Bytebase (schema-migration CI/CD playbooks).
- Record-linkage / entity-resolution scan (7 sources): Fellegi-Sunter (1969) via Science Advances survey; arXiv open-world entity-matching discussion; JMLR 2023 optimal reject-option strategies; Dalitz (reject options for k-NN); Christen (blocking methods survey); Christen quality/complexity measures for linkage; Herzog/Scheuren/Winkler *Data Quality and Record Linkage* (cited); PMC attractor-network stability review (near-duplicate interference analogy).
- Direct-recomputation / metacognition scan (13 sources): Microsoft Azure event-sourcing docs; CodeOpinion (projections in event sourcing); Marten event-sourcing docs; Data-Doctrine "Myth of the Golden Record"; Wikipedia (golden record, test oracle); ScienceDirect (source monitoring); PMC (source monitoring and memory distortion); PMC (metacognition in human decision-making, Fleming & Dolan); ResearchGate (neural basis of error detection / ERN); academia.edu (oracle problem survey); Atlan + DataHub (data lineage for regulatory audits/compliance).

All three sub-agent reports applied the mandatory lit-scan calibration penalty (deflated 0.15-0.25 from raw confidence; novel-synthesis claims capped <=0.50). No claim in this note is presented above that cap.

---

## Load-bearing determination

**YES -- flag for 3x follow-on.** This gates the declared north-star (a meaningful self-audit / the substrate reasoning over its own records) directly, and it gates the standing roadmap's next-declared rung (justification-retrieval / methodology-audit, both of which presuppose a working gate-claims pathway). The fix is cheap (schema addition measured in hours; the direct-entailment audit cell reuses an already-VET'd comparator with no new capacity axis) but strategically load-bearing (without it, "self-audit" stays measured-mechanism-but-near-vacuous-coverage indefinitely, which is the exact status quo this drill was triggered to investigate).

P_deflated = 0.55 (mechanism diagnosis, filesystem-verified) / 0.50 (ranking + design recommendation, capped per novel-synthesis discipline).
