# exp_dev hand-off -- research: scientific concept corpora landscape (GO-5k starter ingest)

filed-by: research (Opus drill synthesis)
date: 2026-06-18
trigger: deep research drill identified GO-5k starter as the cheap-decisive-test for first scientific corpus ingest parallel to WordNet APPLY pattern (notes/research_drill_scientific_corpora_landscape_substrate_ingestion_2026-06-18.md)
pause-state: respects data/orchestrator_paused.flag. If paused, this hand-off STAGES the experiment design; exp_dev does not ship until pause lifted.

per [[feedback-no-experiment-design-in-prompts]]: research files anchor candidates with pre-registered bands; exp_dev owns the experiment design + cell + ship.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (priority): GO-5k starter ingest

- anchor pointer: Gene Ontology (go-basic.obo) top-5k-most-referenced terms subset
- substrate-product reading: science-side parallel to WordNet 5k high-frequency noun synsets queued for morning APPLY; tests substrate ingest pipeline on biology-domain typed-relation corpus
- tier hint: TIER-2 conjecture (lit-supported ingest pattern; no direct precedent at this scale for HDC + GO; HDReason 2024 establishes ceiling)
- why-now: WordNet APPLY queued for morning APPLY pattern; symmetric science-side ingest follows naturally; USER overnight 12h directive "ingest language AND science"
- pre-registered HARD-PASS / HARD-FAIL bands: see [[research_drill_scientific_corpora_landscape_substrate_ingestion_2026-06-18]] section (c)
- corpus source: https://geneontology.org/docs/download-ontology/ (go-basic.obo, ~150MB single file, CC BY 4.0)
- ingest scale: ~5000 atoms + ~14000 typed bears_on edges (3 rels/atom est.); substrate 31283 -> ~36283
- compute classification: super-fast laptop OK (single-file parse + atom Store add); no heavy NxN matrix ops; no remote dispatch needed for ingest pass
- post-ingest cert verification: needs the project .venv per [[reference_hd_instrument_cert_suite_requires_venv_not_system_python_duckdb_2026-06-17]]

### ANCHOR 2 (complement): CSO-5k starter ingest

- anchor pointer: CSO Computer Science Ontology top-5k-most-referenced topics subset
- substrate-product reading: CS-domain orthogonal complement to GO biology + WordNet language; ~11 rels/concept density tests high-edge-density ingest path
- tier hint: TIER-2 conjecture
- why-now: queue AFTER ANCHOR 1 verdict; sequential ingest enables single-corpus-attribution of any structural-guard regression
- pre-registered bands: same template as GO-5k; tighter upper edge-budget given CSO density (target band [25000, 80000] reflecting 5-15 rels/atom)
- corpus source: https://www.salatino.org/wp/computer-science-ontology/ (Turtle, ~few MB, CC BY 4.0)

### ANCHOR 3 (math anchor): OEIS-core ingest

- anchor pointer: OEIS core ~500 sequences w/ xref / keyword / formula edges
- substrate-product reading: math-domain anchor; smaller scale ~500 atoms; pairs with future MSC2020 SKOS (CC-BY-NC-SA) or Stacks Project tag-DAG (GFDL) for math depth
- tier hint: TIER-2 conjecture; smaller scale than the 5k starter band so MIDDLE_BAND interpretation if used standalone
- why-now: queue AFTER ANCHOR 2 verdict
- pre-registered bands: edge budget [1500, 6000] (3-12 rels/atom on 500 atoms); zero-phantom-edge gate same
- corpus source: https://github.com/oeis/oeisdata (git clone; CC BY-SA 4.0)

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_scientific_corpora_landscape_substrate_ingestion_2026-06-18.md (parent drill, full table + 41-citation lit-scan)
- WordNet APPLY queued for morning: see PRIORITY_QUEUE_LIVE.md and active_priorities.md for pre-registered bands
- d:/AI/hd-instrument/notes/reference_substrate_bulk_ingest_concurrency_gotcha_2026-06-16.md (Store.add_atom per-atom auto-flush; bulk ingest needs SERIAL + per-batch fresh-load + os.replace-race retry-fresh)
- d:/AI/hd-instrument/notes/reference_substrate_corpus_completeness_remote_vs_local_half_data_2026-06-17.md (post-ingest raw-count check)
- d:/AI/hd-instrument/notes/feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17.md (verify ATOMS arrive, not just script-ran)
- d:/AI/hd-instrument/notes/reference_remote_dispatch_cell_readiness_checklist_2026-06-17.md (NOT remote-dispatch -- laptop super-fast OK)
- d:/AI/hd-instrument/notes/reference_hd_instrument_cert_suite_requires_venv_not_system_python_duckdb_2026-06-17.md (cert via .venv python)

## Contract section

This hand-off file:
- Names anchor candidates with substrate-product readings and pre-registered HARD-PASS / HARD-FAIL bands.
- Does NOT design the experiment cell (per [[feedback-no-experiment-design-in-prompts]] -- that's exp_dev's autonomy).
- Does NOT dispatch automatically -- exp_dev picks up this file on the next emergency-refill cycle OR explicit routing.
- Respects [[orchestrator_paused.flag]] -- if pause active, file stages but does not ship.

## Autonomy declaration

exp_dev owns:
- experiment cell design (atomizer cell; go-basic.obo parser; top-5k-most-referenced cut algorithm)
- pre-reg verification + smoke gate + ship via queue_add.sh
- post-ship REMOTE VERIFY (if applicable) + filesystem-ground-truth atom count check
- self-test per formula-selftests
- VET registration + VERIFY-THE-REFERENT confirmation post-ingest

research owns:
- corpus identity + license verification (DONE in parent drill)
- pre-registered HARD-PASS / HARD-FAIL bands (DONE in parent drill section (c))
- cross-thread synthesis (DONE in parent drill section (f))

USER owns:
- whether to queue ANCHOR 2 + ANCHOR 3 after ANCHOR 1 verdict (sequential ingest decision; default = wait for GO-5k verdict before queueing CSO-5k)

---

End hand-off.
