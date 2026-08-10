# Pre-reg: exp_extraction_quality_gate_neural_foundation_v1

Filed by: exp_dev (Sonnet, foreground, no queue dispatch -- CPU-only glass-box measurement,
compute-proportionality: this is a GATE/diagnostic question, use the cheapest decisive method,
run FOREGROUND TO COMPLETION locally). Branch `dataprep/mcguffey-graded-corpus`.

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "neural extractor SRL AMR coref installability modern extraction
quality gate oracle parity"` -> top hits: (1) `extraction` (wordnet/concept atom, cosine=0.3457),
(2) `substrate_extraction_quality_1B_8B_70B_v2` (HARD_PASS metrics atom, cosine=0.3447). Both
>0.30, both read in full per the discipline. Hit #2 is a DIFFERENT topic on inspection: it
measures LLM-hidden-state DENSE-PASSAGE-RETRIEVAL quality (Llama 1B/8B/70B layer probes vs
MiniLM sentence embeddings for passage retrieval accuracy), not prose->structured-event
extraction for the situation-model organs. **Prior-work check verdict: NOVEL** (keyword-adjacent
overlap only, no rediscovery). The actually-relevant prior work is
`notes/research_islanded_comprehension_organs_audit_2026-08-10.md` (already cited by the design
note that spawned this cell): 9+ real-text organ cells all show the same oracle(0.93-1.00)->
self-extract(0.25-0.68) collapse. This cell is the first to test whether a BETTER EXTRACTOR
(not a better organ) closes that gap.

## Question

Per `notes/design_extraction_quality_gate_neural_foundation_2026-08-10.md`: does a modern
extractor produce the RIGHT KIND of structured data (PRED/AGENT/PATIENT/TENSE events, coref
clusters, grounded fillers) for the validated organs to consume -- measured, not assumed --
BEFORE building the full inference pipeline. USER refinement (mid-task): also probe whether
extraction quality degrades on genuinely UNPRODUCED/naturalistic text (the extractor itself is
trained on produced text too, so this stress-tests both the organs and the extractor).

## Installability-first (the gate's own first result -- see cell docstring for full detail)

- SRL/TENSE: spaCy 3.8.14 dependency-parse + morphology heuristic. Design note's explicitly-
  sanctioned fallback. Zero-conflict (already installed). Verified on 5 real sentences before
  committing.
- Coref: TWO modern-neural candidates attempted, BOTH FAILED TO RUN:
  1. `fastcoref` (biu-nlp/f-coref): `pip install --dry-run` clean (zero conflicts vs
     torch==2.12.0/transformers==5.10.1/spacy==3.8.14); installs; crashes at model-load with
     `AttributeError: 'FCorefModel' object has no attribute 'all_tied_weights_keys'` inside
     transformers 5.10.1's `PreTrainedModel.post_init()` -- a genuine version-skew bug (fastcoref
     last meaningfully updated ~2023 against `transformers>=4.11.3`; a plain `RobertaModel(cfg)`
     was control-tested and instantiates FINE under transformers 5.10.1, isolating the break to
     fastcoref's own model wrapper, not a general transformers regression). A non-invasive
     in-process monkeypatch was attempted and surfaced a DIFFERENT failure in the same internal
     path -- not pursued further (patching HF internals is out of scope for a GATE cell).
  2. `stanza` (`en`, coref processor): `pip install --dry-run` clean; installs; but
     `stanza.download(...)` hung with zero stdout/network/disk activity for 5+ minutes (no
     `~/stanza_resources` dir ever created) -- aborted as a non-starter.
  3. `spacy-experimental-coref`: NOT attempted -- its released pipeline is documented to require
     spaCy ~3.4/old-thinc, known-incompatible with this project's spacy==3.8.14/thinc==8.3.13
     (documented constraint, not empirically re-verified this session).
- **CONSEQUENCE: no modern neural coref extractor could be installed+run in this environment.**
  This is itself the headline finding for the coref half of the gate. To keep the measurement
  pipeline running, an INDEPENDENTLY-CODED rule-based fallback clusterer
  (`cluster_ids_rule_based_fallback`: gender/number-agreement + recency + exact-string-match) is
  used in its place, CLEARLY LABELED NOT-MODERN-NEURAL throughout the metrics and report. Any
  GO/NO-GO verdict on the coref-dependent gates below is CAVEATED accordingly.

## Target schema (from organ code, per design note)

`hdlab/event_bundle.py EventBundleCodec.encode_event`, `DEFAULT_ROLES=(PRED,AGENT,PATIENT,
TENSE)`; `hdlab/situation_model_accumulate.py AccumulateRegister.add_event(entity,role,
event_idx)`; `CausalLinkRegister.add_causal_link` (causal links: partial, descriptive only, not
gated per design note -- "HARDEST; may be partial").

## Gold corpora (author-constructed positive-control gold; OntoNotes/CoNLL-2012 not available
offline in this repo -- same convention as this repo's other islanded-organ cells, which
routinely use N=7-24 hand-curated real-English items)

- `data/eval_gold_extraction_quality_gate_v1/gold_srl_tense_modern_v1.jsonl` -- 30 items, MODERN
  produced/clean English (10 past / 10 pres / 10 fut, all transitive). PRED/AGENT/PATIENT gold
  lemmas computed via spaCy's OWN lemmatizer at authoring time (so SRL-F1 measures role/predicate
  SELECTION, not lemmatizer spelling idiosyncrasy). TENSE gold authored independently by the
  human (not derived from the extractor -- avoids circularity).
- `data/eval_gold_extraction_quality_gate_v1/gold_coref_modern_v1.jsonl` -- 10 mini passages, 42
  mentions, MODERN produced/clean English, gold entity clusters.
- `data/eval_gold_extraction_quality_gate_v1/sample_unproduced_ud_ewt_v1.jsonl` -- 8 passages / 32
  sentences from `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu` (already in-repo, CC BY-SA
  4.0, "English Web Treebank -- weblogs, newsgroups, emails, reviews, Yahoo! Answers, general web
  register" per its own PROVENANCE.md; genuinely naturalistic/informal text; held-out, never used
  for training anything in this repo). Per-sentence UD gold Tense morphology on the ROOT/main
  VERB doubles as a real tense reference on this text too (bonus: no new hand-authoring needed for
  the unproduced tense-coverage check). Sampled deterministically (even index-spread across
  documents with >=4 Past/Pres-tensed sentences) -- spans 5 genres: weblog, email, newsgroup,
  answers(x3), reviews.

## DECISIVE reuse target

`experiments/exp_wire_coref_accumulate_situation_model_v1.py` (oracle=0.9298, earned=0.6842,
strict_cb=0.7193 on `query_accuracy_identity_demanding`, headline "powered" eval, 36 McGuffey
passages -- MEASURED@data/exp_wire_coref_accumulate_situation_model_v1/metrics.json). This cell
IMPORTS (does not reimplement) `build_mention_stream_with_role` / `event_slots_for` /
`run_arm_on_passage` / `_agg_arm` / `load_passages` / `EVALS` / `HEADLINE_EVAL` / `ROLE_VOCAB` /
`D` / `MAX_EVENT_SLOTS` / `SEED`, and adds ONE new arm (`rule_based_fallback`) over the SAME
gold-supplied mention stream the oracle/earned/recency/singleton arms already use (mention
DETECTION is gold-supplied in that cell for every arm; only IDENTITY/clustering differs -- no
text-reconstruction or char-offset alignment needed).

## The 5 metrics + pre-registered GO/NO-GO bands (declared BEFORE running)

| metric | band | scope |
|---|---|---|
| `shape_conformance` | >= 0.80 | produced SRL gold (30 items) |
| `srl_role_f1` (content-F1, tuple-match over PRED/AGENT/PATIENT) | >= 0.80 | produced SRL gold |
| `coref_b3_f1` | >= 0.70 | produced coref gold (10 passages, 42 mentions) |
| `coverage_all_tenses` (min across past/pres/fut buckets) | >= 0.85 | produced SRL gold |
| `grounding_coverage` (WordNet lemma-has-synset, thin grounder built for this gate -- see caveat below) | >= 0.90 | produced SRL gold fillers |
| `oracle_parity_fraction` = lift(`rule_based_fallback` over singleton_floor) / lift(oracle over singleton_floor) | >= 0.80 | DECISIVE McGuffey reuse, headline "powered" eval |

**GROUNDING CAVEAT**: the design note's pointer ("REUSE the existing WordNet-Tier2 open-vocab
grounder, ~94% coverage") could not be located by name within this session's search budget --
`hdlab/lexical_similarity.py`'s Tier1/Tier2 pooling is a CLOSED 89-concept lexicon that explicitly
disclaims open-vocabulary coverage in its own docstring (not a match); `hdlab/animacy_lexicon.py`
is WordNet-backed but animacy-scoped. A fresh thin grounder (`wordnet_grounded`, nltk WordNet
synset-existence check) was built for this gate instead, using the SAME underlying resource in
spirit but disclosed as NOT a direct reuse of a specific prior promoted module. Band lowered to
0.90 (from the design note's ~0.94) to reflect this is a fresh, less-tuned wrapper.

Secondary (descriptive, not gated): `causal_connective_frac` (discourse-connective heuristic);
`gap_closure_fraction_vs_prior_earned` (does `rule_based_fallback` move the ORIGINAL cell's cited
earned=0.6842 toward oracle=0.9298 -- the design note's literal framing, reported alongside the
singleton-floor-lift framing used for the formal band).

**NO-GO handling**: localize + report the single weakest of the 6 gated metrics; do not proceed
to a full-pipeline build on bad structure.

## USER-refinement addition: UNPRODUCED-TEXT probe (bounded, secondary, does not replace the core gate)

Metrics that don't need gold (computed on the 8 UD-EWT passages): `shape_conformance`,
`coverage_by_tense` (using UD's own gold Tense morphology as reference), `grounding_coverage`,
`hand_verified_accuracy` (15 sentences hand-inspected by the cell-author, judgments fixed BEFORE
this run into `HAND_VERIFIED_JUDGMENTS` for reproducibility -- 12/15 correct, 3 genuine
dependency-heuristic failure classes found: present-perfect Tense-tagged past, passive-raising
nsubjpass-as-AGENT, fronted-participle AGENT/PATIENT role reversal), plus deltas vs the produced
gold's shape/coverage/grounding numbers, plus a coref shape/coverage proxy (fraction of detected
pronouns linked into a multi-mention cluster; no gold clusters exist for this text, so no F1).

## Compute architecture

(b) sequential-CPU with justification: this cell is a diagnostic/measurement GATE (compute-
proportionality discipline), not a training fit or capacity sweep. All operations are (i) spaCy
CPU dependency parses over ~90 short sentences (<1s total warm), (ii) FHRR bind/unbind at d=1024
over 144 (passage,arm) units reusing the wire_coref cell's own formula (<50ms/unit, <10s total),
(iii) WordNet synset lookups (microseconds each). No GPU-batchable matmul-heavy workload exists
in this cell. Storage strategy: no_storage / no_composition beyond what `run_arm_on_passage`
(imported, already-certified) does internally.

## Cell-template mandates (per exp_dev.md ADDITIONAL CELL-TEMPLATE MANDATES 2026-06-27)

- `arms_differ_verified: true` -- self-test asserts `rule_based_fallback` cluster ids differ from
  an all-same-cluster (recency_floor-equivalent) control on a stream with a genuine gender split
  (META_RULE_AF).
- `final_metrics_atomicity: "tmp_replace"` -- single-shot atomic write, `metrics.json.tmp` +
  `os.replace`.
- `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE `except Exception` in the
  CLI entrypoint; no bare `except:` or `except BaseException:` anywhere (grep-gate verified clean
  before self-test).
- `crlb_n_a`: "descriptive extraction-quality GATE, no quantitative noise-floor threshold
  applies" -- no capacity-feasibility ceiling is being tested.
- `real_code_path_exercised`: self-test constructs the REAL `hdlab.situation_model_accumulate.
  AccumulateRegister` at tiny scale (d=64) AND calls the REAL imported
  `exp_wire_coref_accumulate_situation_model_v1.build_mention_stream_with_role` /
  `event_slots_for` / `run_arm_on_passage` on a 2-clause toy passage -- not a synthetic-only
  branch.
- `substrate_signature_checked`: `AccumulateRegister(role_vocab, d, generator, max_event_slots)`
  called with base/portable kwargs only, matching the promoted module's public constructor.
- `deterministic_seeding: true` -- `torch.Generator().manual_seed(SEED)` throughout (reuses the
  wire_coref cell's own `SEED=20260802`); no `hash()`-derived seeding or `list(set())` ordering
  anywhere in this cell (grep-scannable, PROT-023-compliant).
- `cell_chunked: false` -- single-shot cell, not a multi-seed sweep; the DECISIVE sub-loop (36
  passages x 4 arms = 144 units) uses `tools/exp_checkpoint.py` per-unit resumability (CLAUDE.md
  mandatory multi-unit rule) via `ckpt.unit_key/completed_units/record_unit/load_units`. The
  SRL/coref/unproduced loops (<90 total items, pure in-memory spaCy/WordNet calls, no external
  service dependency that could hang) are NOT separately checkpointed -- disclosed scoped
  deviation from the letter of the multi-unit rule, justified by sub-second total runtime and no
  crash-prone external call in those loops.
- `start_marker_written: true`, `crash_diagnostic_present: true` (both implemented per §13).
- `progress_logging`: not required (`timeout_s=240 < 1800`) but `print(..., flush=True)` progress
  lines included anyway as good practice.

## Self-test -> installability smoke -> the measurement (mandatory sequencing)

1. `python experiments/exp_extraction_quality_gate_neural_foundation_v1.py --self-test` (MUST
   PASS before any full run): SRL heuristic shape-correctness on 2 sentences, grounding sanity,
   coref clusterer discriminates (correct-gold B3-F1 > scrambled-gold B3-F1, a must-fail control),
   arms-must-differ, real AccumulateRegister + real wire_coref entrypoints exercised at toy scale,
   all 3 gold files present with expected cardinality (30/10/8).
2. Installability smoke (already run, ad hoc, THIS document): fastcoref/stanza failure findings
   above; spaCy SRL heuristic verified on 5 real sentences.
3. `python experiments/exp_extraction_quality_gate_neural_foundation_v1.py --timeout 240` (FULL,
   run FOREGROUND to completion, no queue dispatch -- light CPU-only compute per compute-
   proportionality).

Resumable (DECISIVE sub-loop via `tools/exp_checkpoint.py`). VET on disk
(`data/exp_extraction_quality_gate_neural_foundation_v1/metrics.json`).
