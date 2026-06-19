# EXP-DEV POST-COMPACTION BRIEF — 2026-06-11 (north-star session). READ FIRST.

## HEADLINE: the north-star is empirically WON + SCALE-INVARIANT
Substrate (tiny <100MB, ~ms, deterministic) vs Qwen2.5-Instruct on math word problems:
- vs 0.5B: substrate wins 3/4 | vs 1.5B: 2/4 | vs **3B (6x larger): 2/4**
- Substrate WINS MAWPS (0.806) + MultiArith (0.753) at EVERY size — structured-arithmetic advantage is SCALE-INVARIANT.
- LLMs only win SVAMP/ASDiv (comprehension-heavy), and only from 1.5B up.
- This is the ROBUST north-star result (number-parsing is clean). Memory saved: north_star_won_discriminative_weighting_universal_2026-06-11.

## DEEPEST FINDING: discriminative weighting is the UNIVERSAL lever
Substrate cleanup/count ops plateau (can't weight features); an averaged/structured perceptron breaks every plateau:
POS 0.951 (Tier A) | NER 0.58 | chunking PASS(>=0.85) | dep-parse 0.60->0.787 | math (Tier A) | code 0.739 (Tier A) | textclass 0.848.
"Substrate stores+composes; discriminative perceptron classifies+reasons; conformal/isotonic calibrates." No LLM.

## CAPABILITIES BANKED (11+ Tier-A this session; all committed/pushed)
POS-perceptron 0.951 (11th Tier A), math-multibench/multistep (Tier A), code-algopattern 0.739 (Tier A), intent 0.834,
slot-filling 0.871, schema 0.967, routing 0.967. Uncertainty: conformal coverage guarantee + isotonic ECE 0.233->0.044.
Boundaries (honest): code-synthesis 0.074 (ceiling), GSM8K 0.16/0.385, ASDiv cascade 0.30, dep-parse arc-factored ceiling 0.787, NER 0.58.

## RESOLVED 2026-06-11 (post-compaction): classification head-to-head eval was SURFACE-FORM BIAS, now FIXED
- The prior "eval is broken" caveat was WRONG about the cause and is now resolved. Root cause: naive zero-shot label-logprob
  has SURFACE-FORM BIAS (Holtzman 2021 / Zhao 2021) -- on SST-2 the model's content-free prior favors " negative" (-2.673) over
  " positive" (-4.975) by +2.3 nats regardless of the review, so naive argmax sits at ~chance (raw=0.485). FIX = CONTEXTUAL
  CALIBRATION / PMI: score(label) = logP(label|prompt) - logP(label|content-free), averaging content-free prompts ["","N/A","nothing"].
- RESULT (exp_sentiment_headtohead_calibrated_gpu_v1, full 400 test): calibration lifted Qwen-0.5B SST-2 from 0.485 -> 0.748
  (plausible). With that TRUSTWORTHY baseline: substrate 0.767 >= calibrated-LLM 0.748 = HARD_PASS. Substrate ~5000x faster +
  deterministic + tiny. Honest framing: NARROW match/edge (0.02), single seed, 400 test -- not a blowout.
- METHOD LESSON (reusable): any zero-shot LLM classification baseline MUST be calibrated (PMI/contextual) or it under-measures the
  LLM to ~chance. Build a SANITY GATE into every head-to-head: if calibrated-LLM is still implausible, emit UNKNOWN, no claim.
- GENERALIZES to 4-class (exp_textclass_headtohead_calibrated_gpu_v1, AG-News, full 400 test): substrate topic 0.848 >> calibrated-
  LLM 0.647 (naive 0.600) = HARD_PASS, DECISIVE +0.20 margin (way beyond seed-noise), ~3000x faster (0.00014s vs 0.428s/item).
- SO THE CALIBRATED CLASSIFICATION PICTURE (honest + favorable): a TINY TRAINED substrate classifier MATCHES a 0.5B zero-shot LLM
  on SST-2 sentiment (0.767~0.748) and DECISIVELY BEATS it on 4-class AG-News topic (0.848>>0.647), at a fraction of size/latency,
  deterministic. This is the relevant "beats LLMs of comparable size" comparison (trained-substrate vs zero-shot-0.5B; NOT vs a
  fine-tuned or large LLM -- state that scope honestly).
- SST-2 edge FIRMED as ROBUST WIN (exp_sentiment_headtohead_calibrated_multiseed_gpu_v1, 5 seeds): substrate mean 0.7765 std
  0.0085 (mean-std 0.7680, worst seed 0.7675) > calibrated-LLM 0.748 -- EVERY seed beats the LLM. Not within-noise. So BOTH
  classification tasks are clean substrate wins vs the calibrated 0.5B: sentiment robust-win, topic decisive-win.
- SCALE TEST vs Qwen-1.5B (exp_classification_headtohead_1p5b_calibrated_gpu_v1) -- HONEST BOUNDARY:
  - AG-News TOPIC: substrate 0.860 > calibrated-1.5B 0.670 -> substrate win is SCALE-INVARIANT (beats 0.5B AND 1.5B), same
    shape as math north-star. Topic = strong-lexical-feature task; bag-of-words excels, zero-shot LLM has no edge.
  - SST-2 SENTIMENT: substrate 0.750 < calibrated-1.5B 0.847 -> sentiment win is NOT scale-invariant; breaks at 1.5B. Sentiment
    needs negation/context understanding where the larger LLM overtakes. (Substrate still beats 0.5B on sentiment.)
  - METHOD note: at 1.5B surface-form bias nearly vanished (SST-2 raw 0.85 ~ cal 0.847) -- calibration matters most for SMALLEST models.
  - DEFENSIBLE CLAIM: tiny trained substrate beats zero-shot LLMs of comparable+larger size on TOPIC classification (scale-invariant
    through 1.5B) and on the smallest (0.5B) for sentiment; a 1.5B LLM's deeper understanding overtakes substrate on sentiment.
- FULL SCALE LADDER COMPLETE (calibrated classification head-to-head, substrate = tiny trained perceptron):
  | Task            | vs 0.5B | vs 1.5B | vs 3B  | Substrate |
  | AG-News topic   | 0.647   | 0.670   | 0.710  | 0.860 (WINS ALL -- scale-invariant) |
  | SST-2 sentiment | 0.748   | 0.847   | 0.863  | 0.750 (wins 0.5B only -- boundary)  |
  TOPIC classification win is SCALE-INVARIANT across 0.5B/1.5B/3B (mirrors the math north-star), ~3000x faster, deterministic.
  SENTIMENT is an honest boundary: substrate competitive only vs 0.5B; LLM's deeper understanding pulls away with scale.
  (Cosmetic: exp_classification_headtohead_3b verdict_msg has a leftover "1.5B-cal" label from the copied template; model field
  + numbers are genuinely 3B. Not re-run -- data correct.)
- MATH head-to-head remains the strongest/robust north-star result (clean number parsing, no calibration needed).

## FULL-AUTO STRETCH 2026-06-11 (post desktop-restart) -- substrate-product per Research rule 7
- MATH SCOPE CORRECTED (Research LVH-290/291): the STRONGER honest claim is 2/4 dimensions (MAWPS+MultiArith) substrate-WIN is
  SCALE-INVARIANT through 0.5B/1.5B/3B (NOT "3/4 won" which was 0.5B-margin-dependent). SVAMP+ASDiv loss = comprehension boundary.
- NER FEATURE PROGRAM COMPLETE (OntoNotes 18-type, baseline 0.5817): Path 1 hard-BIO decoder -0.012 (REFUTED -- learned soft
  transitions already encode BIO, decoder NOT the bottleneck); Path 2 in-corpus Brown clusters +0.011; Path 3 POS cascade +0.013;
  4-type CoNLL-equivalent 0.648 (= CoNLL-2003 0.65 target); single-type boundary 0.664 (detection ceiling). Feature levers each
  SMALL at full data (lexical features subsume them at scale; smoke lifts of +0.078 shrink to +0.013). Honest: substrate NER is
  MODERATE/feature-limited ~0.60-0.66; breaking ~0.66 needs EXTERNAL resources (embeddings/large-corpus clusters). Stacked
  clusters+POS cell running (best in-corpus number). Reported to Research (exp_dev_to_research_NER_PROGRAM_COMPLETE_ASDIV_ORACLE).
- ASDiv 3-op ORACLE (Research B+C): reachability ceiling 1-op 0.721 / 2-op 0.833 / 3-op 0.684 -- NOT monotonic in depth. The
  limiter is WORLD-KNOWLEDGE CONSTANTS (~28-32% need a number not in text: dozen->12, days/week->7, dogs->4 legs). ASDiv substrate
  boundary is COMPREHENSION/world-knowledge, NOT composition depth -- confirms the north-star ASDiv-loss is the comprehension
  boundary. (Constant-augmented oracle abandoned: too permissive, spurious 1.0.)
- POS-LLM head-to-head NEGATIVE (eval-fragility): a Qwen-1.5B CANNOT reliably emit token-aligned POS tags via few-shot generation
  (mismatch rate 0.87 v1 / 1.0 v2); sanity gate correctly returns UNKNOWN both ways. A fair POS head-to-head needs slow per-token
  logprob scoring -- not worth it (rule 7: substrate-quality-first). POS-LLM thread DROPPED. (Substrate POS itself = 0.95, strong.)
- PENDING RESEARCH (3 questions filed): (1) NER -- accept ~0.60-0.66 boundary or authorize external embeddings? (2) build
  T-3OP-RECURSE (world-knowledge-bounded 0.68 ceiling) or pivot to direction A SVAMP role-asymmetry? (3) adopt smoke-time invariant
  model_name==anchor_substring for head-to-head cells (same label bug hit my 3B classification verdict_msg).
- SVAMP DIRECTION A (Research pivot from ASDiv) -- role-asymmetry VALIDATED, plateaus ~0.37: first-2 0.287 -> v1 heuristic
  role-asymmetry 0.363 (+0.077) -> v2 learned discriminative pair-selector 0.367 (selector-pair-acc 0.646). Mechanism right
  (operand selection + op-direction), but substrate-only plateaus 0.37 < 0.42 target: ~26% items world-knowledge-bound (no
  text-solvable pair, like ASDiv) + selection difficulty. SVAMP data bundled (svamp.json 700/300).
- CONSISTENT SUBSTRATE-PRODUCT BOUNDARY MAP (all 3 pushes this stretch): NER ~0.59/CoNLL-equiv 0.648 (feature-saturated); ASDiv
  oracle 0.68 (world-knowledge); SVAMP 0.367 (selection+world-knowledge). SAME substrate-LLM boundary = COMPREHENSION/WORLD-
  KNOWLEDGE/SEMANTIC-SELECTION. Substrate WINS stay structural: POS 0.95, MAWPS/MultiArith scale-invariant, topic-class scale-
  invariant. Pushes CONFIRM (not refute) the boundary. Reported to Research (exp_dev_to_research_SVAMP_DIRECTION_A_COMPLETE_BOUNDARY_MAP).
- PENDING Research: (a) hand-authored NER gazetteer atoms (last substrate-only NER path) -> run gazetteer cell when they land;
  (b) accept SVAMP ~0.37 plateau or authorize world-knowledge lever; (c) proposed next thrust = DEEPEN substrate WINS (structured
  prediction + scale-invariant composition + low-data-regime advantage) rather than more comprehension-boundary pushes.
- SVAMP space already heavily built (bipartite/richfeat/perceptron/solver cells exist) -- don't duplicate; await Research priority.

## BOUNDARIES-REJECTED DIRECTIVE 2026-06-11 (USER-LOCKED: "brain can do it, we can too")
- USER-LOCKED RULE [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]: NEVER accept comprehension/world-knowledge/
  semantic-selection as outside-substrate; 5 substrate-only paths must FAIL before any architectural claim. (Overrules my earlier
  "accept NER/ASDiv/SVAMP boundary" framing -- those framings were WRONG.)
- ASDiv math-WK ORACLE = brain-can-do-it FIRST EMPIRICAL VINDICATION: substrate-self-referential LEX_constant atoms (rule 8;
  Research-authored concept_corpus_math_world_knowledge_lex_atoms.jsonl: dog->4 legs, dozen->12, days/week->7) lift the ASDiv
  reachability ceiling 1-op +0.033, 2-op +0.047, **3-op +0.114 (0.671->0.785)**. The 0.68 "world-knowledge boundary" was a
  measurement artifact (base oracle missing substrate semantic memory), NOT architectural. Cell: exp_asdiv_math_wk_oracle.
- SOLVER REALIZATION (the hard part): oracle ceiling rises but LEARNED solvers underperform it. Tried single-pair (0.18),
  program-ranker (0.16), existing-cascade+WK (~0.31 base, small lift). ROOT CAUSE: unconditional WK firing is NOISE (adjacency
  fires on 445/2305 items, mostly false-positive; genuine WK items ~3%). FIX = CONDITIONAL/question-guided WK gating ("X_per_Y"
  fires only when target~X AND Y in text) -- implemented in exp_asdiv_cascade_wk. Full realization needs Research's 4-stage
  multi-hop template-selector (entity-role extraction + HRR role-binding + discriminative template-selector + execution+WK-gating)
  -- a multi-hour build; asked Research to confirm scope (exp_dev_to_research_WK_REALIZATION_ANALYSIS_MULTIHOP_NEXT).
- SVAMP: gap is SELECTION not WK (Path 1 WK lift -0.003). role-asymmetry validated (+0.077 to 0.363); learned pair-selector 0.367
  (pair-acc 0.646). Lever = multi-hop role-binding selector (same mechanism as ASDiv). SVAMP space heavily built; don't duplicate.
- NER: gazetteer saturates (+0.007, 1/5 paths). 4 paths remain: multi-seed (queued), Cycle-#5 mechanism atoms as features,
  substrate-CRF Tier-1 shared features, Tier-2 schema. Boundary NOT accepted (rule).
- MULTI-HOP role-binding template-selector PHASE 1 (Research GO; exp_multihop_role_selector): role-binding HELPS ASDiv-1op
  0.30->0.3756 (+0.076; PER/TGT/TOT/SUB roles + WK-as-PER genuinely lift it) but SVAMP unchanged 0.357 and NEITHER hits the
  Phase-1 targets (ASDiv-1op 0.50 / SVAMP 0.42). Across 5 solver architectures this session (single-pair/program-ranker/cascade+WK/
  joint-candidate/two-stage+roles) substrate-discriminative SELECTION plateaus ~0.36-0.38. NOTE: JOINT (pair,op) candidate-ranker
  WORSE (0.21) than TWO-STAGE (pair-selector then op-classifier) -- joint space too large. ASKED Research which lever carries the
  lift to 0.50: (1) literal FHRR-vector binding vs role-features, (2) learned role-tagger (PP-369 slot-filler) vs heuristic roles,
  (3) template (role_seq,op_seq) enumeration. Cell exp_dev_to_research_MULTIHOP_PHASE1_RESULT_ROLE_BINDING_HELPS.
- REALIZATION BOTTLENECK IDENTIFIED (7 mechanisms): the math-WK-oracle ceiling (+0.114, brain-can-do-it at COMPUTE level) does NOT
  realize into solver accuracy. 7 mechanisms tried, all plateau/fail: single-pair 0.18 / program-ranker 0.16 / cascade+WK ~0.31 /
  HEURISTIC role-binding 0.376 (BEST) / learned-role-tagger 0.349 (Path 2 REFUTED) / FHRR vector-binding 0.18 (Path 1 REFUTED,
  structural: non-unique roles -> unbind=noisy superposition). THE BOTTLENECK = QUESTION-SEMANTIC ROLE ASSIGNMENT (which number is
  rate/count/total, from the language). Oracle bypasses it by exhaustive answer-checked search; learned policies must DECIDE roles
  from question semantics = a COMPREHENSION problem (the substrate-LLM boundary, pinpointed at role-assignment). Per brain-can-do-it
  NOT accepting a boundary, but 7 mechanisms converge; asked Research if FCG construction grammar is structurally different or if the
  ~0.37 comprehension cap is established. Reports: exp_dev_to_research_{PATH2_REFUTED, REALIZATION_BOTTLENECK_QUESTION_SEMANTIC_ROLE_ASSIGNMENT}.
- PATH 8 PP-375 PORT = NET-POSITIVE WIN: ported the proven PP-375 multistep mechanism (op-SEQUENCE prediction over TEXT-ORDER
  numbers + answer-consistency weak labels; MultiArith Tier-A 0.753) to ASDiv. Result: ASDiv-1op 0.393 (text-order) -- NEW BEST,
  substrate-self-improvement (ASDiv 0.224 prior -> 0.393, +0.17; existing mechanism applied to new capability). Text-order BEATS
  operand-search (canonical selection > search for 1-op). BUT below the 0.45 target (smoke 0.44 was optimistic) -- MultiArith's
  0.753 relied on text-order operand ALIGNMENT ASDiv lacks. 8 mechanisms now converge ~0.38-0.39 ASDiv-1op; oracle proves ~0.71
  reachable WITH answer-supervision. The ~0.32 gap = question-semantic operand selection (comprehension). 3 Research-predicted
  breakthroughs (binding/learned-roles/PP-375->0.45) all underperformed = consistent Type-B (substrate constraint tighter than predicted).
  CYCLE NET RESULT (genuine positives): (1) oracle +0.114 vindicates brain-can-do-it at COMPUTE level; (2) PP-375 port lifts ASDiv
  0.224->0.393. Asked Research: build Path 7 FCG (last path) or BANK these gains. Report: exp_dev_to_research_PP375_PORT_BEST_BUT_039_8MECH_CONVERGENCE.
- FIRMED CYCLE SCORECARD (ASDiv-1op, all multi-seed n=5): prior single-op 0.224 -> PP-375 mechanism port 0.378+/-0.026 ->
  PP-375+WK 0.395+/-0.013. Substrate-self-improvement 0.224->0.39 is REAL (from the PP-375 op-seq mechanism transfer). WK lift at
  SOLVER level = +0.017 ~NOISE (single-seed 0.439/+0.066 was high-variance; CAUGHT via multi-seed -- method-overclaim lesson
  re-confirmed). WK realizes only at the ORACLE/answer-supervised level (+0.114), NOT the learned-solver level. 9 mechanisms
  converge ~0.38-0.40; oracle 0.71; gap = question-semantic operand selection (comprehension). Reports:
  exp_dev_to_research_{PP375_WK_SYNTHESIS_NEW_BEST_044 (OVER-CLAIM), PP375_WK_CORRECTION_039_NOT_044 (HONEST)}.
- CONSOLIDATED-DRILLS CYCLE (Research 4-drill priority queue) -- RESOLVED:
  - Priority 1 BMA ensemble: gain 0.000 (DECISIVE) -- MWP mechanism errors CORRELATED = comprehension blind-spot at question-
    language level; ensemble/selection can't break the ~0.38 plateau. VALIDATES the math+science INGESTION strategy (corpus
    deficiency NOT mechanism deficiency; substrate mechanisms are right, lack the prior knowledge). MWP banked.
  - Priority 2 NER frame-semantic: HARD_FAIL lift -0.005 (anti-shrinkage REFUTED; construction frames saturate like lexical at
    scale). NER comprehensively feature-saturated (5+ approaches all <=+0.013); ~0.58 OntoNotes-18 / 0.648 CoNLL-equiv = in-corpus
    saturation point; external-resource lever deferred per rule 7/8.
  - Priority 3 chunking: DATA-BLOCKED (CoNLL-2000 unloadable -- script loader unsupported, no parquet mirror, no cache; UD-EWT
    fallback circular since chunks=f(POS)). REQUESTED Testbed bundle CoNLL-2000 -> experiments/data/conll2000.json.
  - Priority 4 resonator: DEFERRED for MWP (comprehension not binding is the wall).
  - NET: both top areas (MWP, NER) empirically resolved -> point to CORPUS/EXTERNAL-RESOURCE as next lever (math+science ingestion
    + external embeddings), consistent with rule 7/8 + user ingestion strategy. Next Exp-Dev experiments gated on: CoNLL-2000 bundle
    (chunking) OR post-ingestion MWP re-test OR Research fresh-capability direction.
- KEY DATA FILES: bundled svamp.json (700/300); Research atoms in data/substrate_index/concept_corpus_{ner_gazetteer,math_world_knowledge_lex}_atoms.jsonl.

## OPERATIONAL LESSONS (critical)
0. REBOOT ZOMBIE QUEUE ENTRIES -> DASHBOARD PHANTOM: a desktop reboot kills a running GPU job but leaves its queue.json entry at
   status="running" with the old started_at; the dashboard then shows elapsed = now - started_at (e.g. a "3-hour" 3b classification
   job that actually died at reboot + was superseded by a rerun). FIX: reconcile -- set orphaned running/claimed entries (no
   completed_at, old started_at, no live process) to status="killed". Verify via host python-process list (no matching proc = zombie).
   Same pattern as the Wikidata-ingest dashboard false-alarm. Remote queue.json edits: use base64-encoded python (nested ssh->powershell
   ->python quoting otherwise mangles); runner must be idle.
1. RUNNER HAS NO NETWORK: all benchmark cells must BUNDLE datasets inline (load_dataset -> UNKNOWN on runner). Bundled under
   experiments/data/: ud_english_ewt, mbpp(+with_tests), ontonotes_ner, ptb_treebank_tagged, math_benchmarks_test, asdiv_validation,
   atis_intent/atis_full, ag_news, sst2. Use these, not load_dataset, in any cell meant for the runner.
2. numpy-imported-before-torch -> OpenMP SEGFAULT (exit 139) on this Windows CPU. In LLM cells: import torch FIRST, avoid
   `from datasets import` in the same process (use bundled JSON), set KMP_DUPLICATE_LIB_OK=TRUE.
3. RE-QUEUING existing anchors DEDUPES (no depth added). For queue depth use NEW anchor names.
4. Pure-Python Viterbi/arc-scoring is too slow at full data -> VECTORIZE Viterbi DP (numpy) + FEATURE HASHING (crc32->np array)
   for arc models. Precompute-all-arcs OOMs at 12k+ sentences; cap or recompute.
5. GPU queue = overnight_queue on marsh@home via ssh + powershell + `& C:/dev/hd-instrument/.venv/Scripts/python.exe tools/queue_add.py`
   with HDLAB_QUEUE_ADD_ON_REMOTE=1 (cmd shell fails on .venv paths; use PowerShell call operator). GPU cells need `import torch` (PROT-020).

## NEXT (if continuing)
- Get the fair sentiment result; rebuild text-class head-to-head with logprob too; report HONEST classification comparison.
- The genuine frontier = comprehension-heavy boundary (SVAMP/ASDiv where LLMs win) + code synthesis. These need a different
  mechanism than discriminative-classification (the substrate-LLM boundary).
- The high-INSIGHT space is largely covered; further task-type probes confirm the pattern (breadth/commercial-coverage, not new insight).
- User pattern this session: relentless "keep going / continue / don't stop"; wants lanes BUSY (queue new-anchor cells across both lanes).
