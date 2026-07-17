# Pre-reg: exp_read_grow_foundation_endtoend_v1 (THE MAIN-LINE JOIN: read text -> grow a foundation)

Cell: `experiments/exp_read_grow_foundation_endtoend_v1.py`
Question: wire the three separately-proven pieces into ONE loop for the first time -- the substrate READS a
small graded text corpus, PARSES it glass-box, uses its LEARNED lexicon to EXTRACT (s,r,o) facts, runs each
through the INGEST GATE (schema-fit / novelty / provisional-hold), and BUILDS a queryable foundation from
scratch. Glass-box, NO LLM, local numpy.

## Pieces composed (reuse of mechanism, with provenance)
- LEARNED LEXICON: `exp_lexicon_learned_grounding_scaled_v1.py::learn_lexicon` + `lexicon_top` -- IMPORTED.
- SVO parse+bind: `exp_nativelang_svo_vsa_probe_v1.py::encode_meaning`/`decode_meaning` + FHRR primitives -- IMPORTED.
- INGEST GATE: FAITHFUL RE-EXPRESSION over TYPED TRIPLES of the banked schema-fit / provisional-hold /
  PERMISSIVE->SELECTIVE gate (`exp_curriculum_order_ingest_schema_fit_v1.py::ingest`,
  `exp_provisional_hold_bootstrap_arbitrary_order_v1.py`, `exp_multisource_arena_v1.py`). Re-expressed (not
  the geometric ingest() verbatim) because the banked data format is a displacement graph, not typed triples.

## Loop (per read sentence, curriculum order)
glass-box positional SVO parse -> learned-lexicon words->concepts -> encode role-filler bundle ->
decode (unbind+cleanup) EXTRACT triple -> GATE accept/hold/reject -> grow SHARDED VSA foundation store -> query.

## Arms / controls
FULL_LOOP (gate) ; NO_GATE (accept-all) ; ORACLE_LEXICON (perfect map -> isolates parse) ;
RANDOM_LEXICON (chance map -> lexicon load-bearing check). Corpus injects 2 type-violating FALSE facts
mid-stream, 1 out-of-order HOLD fact, and a NOVEL entity (owl) late.

## Metrics (reported separately)
(a) extraction_acc ; (b) foundation precision + true_recall ; (c) query_acc (VSA retrieval) ;
(d) gate accept_true_rate + accept_false_rate. Plus localization diagnostics (mapping_acc, oracle-lexicon
extraction, store round-trip) so a fail attributes to parse->lexicon / lexicon->triple / triple->gate /
gate->store / store->query.

## Bands
- HARD-PASS: extract>=0.90 & FULL prec==1.0 & true_recall>=0.90 & accept_false_rate==0 &
  accept_true_rate>=0.85 & (FULL-NOGATE prec)>=0.05 & novel_owl queryable & hold released & query_acc>=0.85.
- HARD-FAIL: extract<0.50 | accept_false_rate==1.0 | accept_true_rate<0.50 | FULL prec<0.70 | query<0.50.
- MIDDLE otherwise. On HARD-FAIL: localize the broken interface; do NOT over-read a partial loop.

## Schema-vet fields
- compute_architecture: sequential-CPU (genuine sequential dependency: foundation grows fact-by-fact; gate
  state depends on prior admissions). wall < 10s (MEASURED 1.22s full).
- storage_strategy: sharded (one VSA vector per accepted fact) per META_STORAGE_STRATEGY.
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true. deterministic_seeding: true
  (fixed int seeds; sorted() vocab; no hash()/list(set())). start_marker + crash_diagnostic present.
- real_code_path (F.1): self_test constructs the REAL imported objects (learn_lexicon, encode/decode_meaning,
  make_phasors, FoundationStore, run_loop) at tiny scale and asserts.
- crlb_n/a: no quantitative noise floor; FHRR cleanup among ~25 concepts at N=1024 (z ~ 26 sigma) ->
  decode reachable ~1.0; extraction gated by LEXICON map errors, not cleanup noise.
- discriminator-fires: verified at smoke -- NO_GATE admits both FALSE facts (n_false=2); FULL rejects both
  (n_false=0); FULL vs NO_GATE accepted-store hashes differ (META_RULE_AF).

## Result (MEASURED @ data/exp_read_grow_foundation_endtoend_v1/metrics.json, 5 seeds, run_mode=full)
HARD_PASS. extraction=1.000 (oracle=1.000, random=0.000); foundation precision FULL=1.000 vs NO_GATE=0.913
(gate gain +0.087); true_recall=0.952; accept_false_rate=0.000; accept_true_rate=0.950; query_acc=1.000;
novel(owl) accepted+queryable; out-of-order fact held then released. The single conservative rejection
(`fish lives_in pond`, recall 0.952 not 1.0) is an HONEST gate decision, not an interface break: fish had
appeared only as an eats-OBJECT (prey), so the self-grown schema typed it prey-like and rejected it in the
lives_in-SUBJECT (predator) slot. Left as-is; loosening the gate to force 1.0 would risk admitting false facts.
