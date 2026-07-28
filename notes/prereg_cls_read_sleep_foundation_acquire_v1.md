# PRE-REG: CLS READ->SLEEP foundation acquisition + no-catastrophic-interference

anchor: cls_read_sleep_foundation_acquire_v1
cell: experiments/exp_cls_read_sleep_foundation_acquire_v1.py
author: hdi_exp_dev  date: 2026-07-26
run: INLINE-LOCAL foreground-to-completion (no remote authorized; NO push; NO bank)

## Goal (the user-directed CLS loop, foundation scale)
READ (reader extracts facts from text) -> hippocampal fast-write (episodic store) ->
SLEEP (replay-gated consolidation into the SEMANTIC foundation store) -> the foundation
now answers probes requiring the NEW facts, WITHOUT losing the OLD facts.

## Components wired (REAL banked; no reinvention of the store)
- SEMANTIC store = hdlab/hd_fact_store.HDFactStore (glass-box HD fact store + trust-ranked
  ingest-vet: CLEAN_STORE / REPLACE / DROP / FLAG / COMBINE). This IS the foundation working copy.
- FLAG-unknowns = hdlab/clarify_gate.ClarifyGate (banked M1.6/M1.8 calibrated 3-band gate) on the
  extractor's per-sentence confidence: scrambled/ambiguous -> non-ACCEPT (flag), clean -> ACCEPT.
- EPISODIC store = a small attestation-counted list (hippocampal fast-write): each extracted
  candidate fact accrues attestations across replay cycles.
- SLEEP/replay = replay-gated consolidation: a fact promotes episodic->semantic only if
  attestations >= REPLAY_THRESHOLD (recurrence gate), then store.store() applies trust ingest-vet.

## Data (does NOT mutate the banked artifact)
- Working foundation slice = CONTROL facts sampled from data/cskg_foundation_v1/edges_shard_*.jsonl
  (present in foundation), TRUST_HIGH, deduped to unique (subject,relation) within the slice.
- HELD-OUT target facts = sampled from data/cskg_foundation_v1/heldout_edges.jsonl. VERIFIED
  0/24774 leakage into the 16 shards (measured this session) -> genuinely absent from the foundation.
- Curated relations (clean English templates): LocatedNear UsedFor CapableOf PartOf AtLocation
  HasA MadeOf Causes HasProperty Desires.

## TEXT SOURCE + CONSTRUCTION-DETERMINED CAVEAT (loud, honest)
Text is TEMPLATED from the held-out triples (no natural corpus mentions these exact CSKG edges).
Therefore the ACQUISITION axis is CONSTRUCTION-LEANING: a closed generate-from-triple ->
extract-triple loop. Extraction of the target facts is NOT a language-understanding result.
The GENUINELY can-fail science lives in the CONTROLS + the extractor discrimination:
  - the extractor must REJECT scrambled (token-shuffled) sentences (-> ~0 facts),
  - the extractor must REJECT distractor nouns planted in each sentence (must not emit the wrong span),
  - the pipeline must NOT leak held-out facts without reading (no-read) or without sleep (no-sleep),
  - the trust-gated consolidation must NOT corrupt high-trust control facts with a low-trust
    contradictory "update" read from text (retention-protection; genuinely can-fail).
Acquisition is reported as PLUMBING-VERIFICATION (does a fact flow read->episodic->sleep->semantic),
DEFLATED accordingly.

## Arms (each probes the SAME held-out + control sets)
1. BASE (no-read)        : semantic = control facts only. held-out probe -> base rate (0, absent).
2. READ_NO_SLEEP         : extract held facts -> episodic ONLY; semantic unchanged. held-out(semantic) -> ~0.
3. READ_SLEEP (mechanism): replay-gated consolidate episodic->semantic. held-out -> acquired; control -> retained.
4. SCRAMBLED_SLEEP       : read token-shuffled text -> ~0 valid extractions -> consolidate -> held-out still ~0.

## Metrics (sharded HDFactStore = primary)
- ACQUISITION = held-out exact-recovery acc (query(s,r) returns gold obj) in READ_SLEEP.
  base = BASE held-out (query empty -> 0).
- RETENTION = control exact-recovery acc in READ_SLEEP vs BASE (no catastrophic interference).
- RETENTION-PROTECTION = of N_CONFLICT control facts that receive a LOWER-trust contradictory
  read-update, fraction still recovering the ORIGINAL control obj after sleep (must be ~1.0 via DROP).
- TRUST-LIVE sentinel (reported, not gated) = a HIGH-trust contradiction DOES replace (proves DROP non-vacuous).
- EXTRACTION = precision/recall of extractor on clean sentences; distractor-rejection rate;
  scrambled-rejection rate.

## Diagnostic arm (reported, NOT gated): BUNDLED capacity interference
A naive superposed (bundled) semantic store at capacity pressure (small N_bundled) to demonstrate
the interference RISK is real: K-way cleanup control retrieval BASE vs after consolidating held-out.
Sharded (HDFactStore) predicted to hold; bundled predicted to degrade -> the CLS motivation, by contrast.
If bundled does not stress at this scale, reported honestly as "no interference observed" (no gate impact).

## Pre-registered bands (HARD; sharded arm)
HARD_PASS requires ALL:
- A ACQUISITION: READ_SLEEP held-out acc >= 0.80  AND  BASE held-out acc <= 0.10  (gap >= 0.70)
- B CONTROLS   : READ_NO_SLEEP held-out <= 0.10  AND  SCRAMBLED_SLEEP held-out <= 0.10
- C RETENTION  : READ_SLEEP control acc >= (BASE control acc - 0.05)
- D PROTECTION : retention-protection fraction >= 0.90
HARD_FAIL if:
- acquisition < 0.50 (plumbing broken), OR any control > 0.25 (leak), OR retention drop > 0.15
  (interference), OR protection < 0.70.
MIDDLE_BAND otherwise. (Acquisition band is construction-favored -> the load-bearing HARD_FAIL
guards are the CONTROLS + RETENTION + PROTECTION, not acquisition.)

## Discriminator-fires / baseline-in-band
- BASE held-out acc is 0 by construction (facts absent) -> the acquisition GAP is the discriminator;
  it fires iff READ_SLEEP moves held-out from ~0 to high AND controls stay ~0 (guards leak).
- baseline-in-band: control BASE acc must be > 0.05 (facts genuinely stored/retrievable) and the
  bundled diagnostic control-BASE targeted into [0.30,0.85] by N_bundled (adaptive calibration, declared).

## Cell-template compliance
- deterministic seeding (fixed int seeds + sorted(set); NO python hash / list(set))
- except SystemExit: raise before except Exception (no BaseException); crash-diagnostic metrics
- atomic tmp+os.replace final metrics (META_RULE_AH: tmp_replace)
- start_marker written; progress via print(flush=True)
- arms_must_differ verified (semantic store contents differ across arms; hashed)
- self_test constructs REAL HDFactStore + ClarifyGate at tiny scale (real_code_path)
- calibration_check: adaptive_with_gate (N_bundled tuned to land bundled-BASE in band; discriminator = sharded-vs-bundled)
- crlb_n/a: exact-recovery on a sharded per-fact store has no bundle-noise floor; bundled arm capacity noted inline.
- run foreground-to-completion; verdict with numbers in report.
