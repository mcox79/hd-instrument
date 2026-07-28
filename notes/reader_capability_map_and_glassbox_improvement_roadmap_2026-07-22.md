# Reader / NLP Capability Map + Glass-Box Improvement Roadmap (disk-verified) — 2026-07-22

**Discipline applied:** every accuracy below was read from the cell's own `data/<anchor>/metrics.json` on disk. Claimed-vs-disk discrepancies are flagged. "Classical glass-box ceiling" = best NON-neural structured method (averaged/structured perceptron, CRF, MaltParser/MSTParser, IMS-SVM), the honest target for a no-gradient-at-runtime substrate. Neural ceiling noted only as context (the "glass-box tax").

---

## STEP 1+2 — INVENTORY (disk-verified) + CEILING CLASSIFICATION

| Function | On-disk best (metrics.json) | Verdict | Cell path (`data/…`) | Classical glass-box ceiling | Neural ceiling (context) | Classification |
|---|---|---|---|---|---|---|
| **POS tagging** (PTB 45-tag, standalone) | **tag-acc 0.9063** mean n=5 | HARD_PASS | `exp_pos_tagger_multiseed_cpu_v1` (and `_ptb_substrate_cpu_v1` 0.9066) | ~0.97 (struct-perceptron/TnT) | ~0.978 | **UNDER-BUILT** (−0.064) |
| POS (internal to chunk cascade, coarser) | pos_acc 0.9768 | (internal) | `exp_chunking_conll2000_cascade_cpu_v1` | — | — | shows ceiling reachable w/ proper train/features |
| **Chunking / shallow parse** (CoNLL-2000) | **F1 0.9257** (richfeat, full); 0.9304 substrate arm | MIDDLE_BAND | `exp_chunking_conll2000_richfeat_lean_cpu_v1`; `exp_chunking_headtohead_llm_gpu_v1` (substrate_f1=0.9304) | ~0.94 (CRF) | ~0.955 | **UNDER-BUILT** (−0.01 to −0.015, near ceiling) |
| Chunking (discriminative arm) | F1 0.9019 | HARD_PASS | `exp_chunking_discriminative_cpu_v1` | ~0.94 | — | under-built |
| **Dependency parse — local-argmax** | **UAS 0.7875** mean n=5 (std 0.0008) | MIDDLE_BAND | `exp_depparse_hashed_multiseed_cpu_v1` | ~0.885 (Malt transition) / ~0.916 (MST) | ~0.96 | **UNDER-BUILT** (−0.10, biggest structural headroom) |
| Dependency parse — global MST arm | UAS 0.7895 | MIDDLE_BAND | `exp_depparse_v2_mst_cpu_v1` | ~0.916 | — | UNDER-BUILT |
| Dependency parse — discriminative | UAS 0.735 | MIDDLE_BAND | `exp_depparse_discriminative_cpu_v1` | — | — | UNDER-BUILT |
| Dependency parse — 2nd-order | UAS 0.7783 | HARD_FAIL | `exp_depparse_2ndorder_cpu_v1` | — | — | 2nd-order alone didn't help |
| **SRL / semantic role** (reader relation-F1, real held-out McGuffey) | **RELF1 0.710** held-out | MIDDLE_BAND | `exp_learned_role_assigner_reader_heldout_v2` | ~0.80 (CoNLL-2005 classical) | ~0.86 | **UNDER-BUILT / task-specific** |
| SRL — composition (constructed, freq-decorrelated) | CMP 0.875, RELF1 0.727 | HARD_PASS | `exp_learned_role_assigner_reader_composition_v3` | — | — | passes on constructed |
| SRL — wild real text | RELF1 0.217 | HARD_FAIL | `exp_learned_role_assigner_reader_wildtext_v4` | — | — | GENUINELY-HARD on wild text |
| SRL — role-slot summarization (synthetic) | ROLE 0.792 | HARD_PASS | `exp_cortex_summarization_role_slot_v1_seed_7` | — | — | synthetic binding |
| SRL — linguistic MWP arm | F1 0.327 | HARD_FAIL | `exp_path1_srl_mwp_cpu_v1` | — | — | corpus-deficient niche |
| **NER** (CoNLL-equiv 4-type) | **F1 0.6541** (4-type); 0.5817 (18-type) | MIDDLE_BAND | `exp_lb_ner_fewshot_curve_cpu_v1` | ~0.88–0.91 (CRF+gazetteer+Brown) | ~0.93 | **UNDER-BUILT** (−0.23, feature gap; cell says "proceed Brown-cluster features") |
| **Coreference** (reader, salience-rank) | ref-acc 0.912, RELF1 0.58 | HARD_PASS (salience cue) | `exp_coref_salience_rank_topicality_v1`; base `exp_base_reader_grounded_relations_coref_v1` coref_lift 0.714 | ~0.60 MUC / ~0.70 B³ (deterministic sieve) | ~0.80 | **GENUINELY-HARD** (classical ceiling itself low; real-slice levers HARD_FAIL — animacy/margin-gated/attachment all net-break) |
| **WSD** (SemCor verbs, learned-context) | **acc 0.5691 vs MFS 0.5679** (lift +0.0012, p=0.51) | HARD_FAIL | `exp_learned_context_wsd_semcor_verbs_v1` | ~0.71–0.75 (IMS-SVM supervised) | ~0.79 | **GENUINELY-HARD for beat-frequency** (sits at MFS wall; classical SVM headroom exists but every glass-box feature tested fails to beat frequency) |
| WSD — entity-typing selectional | 0.5558 vs base 0.5546 (p=0.81) | HARD_FAIL | `exp_entity_typing_selectional_wsd_v1` | — | — | no lift |
| WSD — McGuffey frame+selectional | 0.8684 (N=38) BUT UD-EWT 0.209–0.237 | HARD_PASS_WSD (tiny) | `exp_mcguffey_whoaffected_wsd_frame_selectional_v1` | — | — | ⚠️ 0.868 is N=38 single-annotator; generalizes to 0.21 on UD-EWT |
| **Subject-verb agreement** (buried subject — session wall) | held-out 0.7913 aggregate; **SNF-buried 0.5803 vs majority 0.6269** | MIDDLE_BAND (fails genuine CG) | `exp_agreement_attractor_role_binding_cg_viability_v1` | n/a (no classical benchmark; n-gram≈majority) | LSTM ~0.99 | **GENUINELY-HARD** (structure-not-used; needs new mechanism, not classical decode) |
| Agreement — depth-rule diagnostic | buried 0.5276 vs maj 0.6117 (−0.084) | HARD_FAIL | `exp_agreement_glassbox_depth_rule_diagnostic_v1` | — | — | depth-rule refuted; **the maintained parse-stack is the missing feature** |
| **Intent classification** (ATIS gold) | **acc 0.8345** mean n=5 (std 0.004) | HARD_PASS | `exp_intent_atis_multiseed_cpu_v1` | ~0.95 (SVM) | ~0.97 | **UNDER-BUILT** (−0.12) |
| Intent (a1 substrate, 5k train) | 0.754 | HARD_PASS | `exp_a1_substrate_intent_classifier_v1` | ~0.95 | — | under-built |
| Slot filling (frame k=16, synthetic binding) | retrieval 1.000 | HARD_PASS | `exp_frame_slot_fill_k16_v1` | ~0.94 F1 (real ATIS-slot CRF) | ~0.96 | ⚠️ synthetic binding, NOT real ATIS slot-F1 → **real slot-filling UNDER-BUILT / untested** |
| **Morphology / inflection** (wug, novel stems) | 8/8 rules ≥0.90, min 1.000; dual-route 1.000 | HARD_PASS | `exp_morph_ruleset_wug_v2_cpu` | ~0.95 | — | **AT-CEILING** |
| Number (dual-route dissociation) | clean acc 1.000 / 0.993 | HARD_PASS | `exp_dual_number_double_dissociation_v1` | — | — | **AT-CEILING** |
| **Grounding** (learned lexicon, benign codes) | map_acc 0.936–0.96; obj 0.940 vs oracle 1.0 | HARD_PASS | `exp_lexicon_learned_grounding_scaled_v1` | — | — | works on benign codes |
| Grounding — multi-hop | hop@1 0.42 → hop@2 collapses ~0.06–0.17 | MIDDLE_BAND | `exp_grounding_multihop_decisive_win_v1` | — | — | **UNDER-BUILT** (additive-store crosstalk bottleneck; sharded-store queued) |
| Reader — context-driven sense (held-out) | a=0.234, gap 0.064, p=0.195 (dict ceiling 0.979) | MIDDLE_BAND | `exp_base_first_reader_heldout_context_learn_v1` | — | — | GENUINELY-HARD (context adds little over dict-lookup) |
| Reader — cross-sentence thematic | a_cross 0.527 vs within 0.522 | HARD_FAIL | `exp_base_first_reader_crosssentence_thematic_overlay_v1` | — | — | no cross-sentence signal captured |
| Next-token (Markov transition) | recall 0.85 @N4096 | MIDDLE_BAND | `exp_markov_transition_nscale_cpu_v1` | — | — | under-built |
| Tokenization / sentence-seg | — | (no dedicated cell; handled trivially by rule) | — | ~0.99 rule-based | — | AT-CEILING (not a bottleneck) |

### ⚠️ CLAIMED-vs-DISK FLAGS (propagation hazards caught)
1. **Parser "0.85 / highly effective"** → on disk **UAS 0.7875–0.7895, MIDDLE_BAND** across all arms (local, MST, 2nd-order, discriminative). Confirms the earlier flag; the parser is the single most under-built core function.
2. **POS "Tier-A works"** → real, but **0.906 on PTB-45**, which is **−0.064 below the 0.97 classical ceiling** — under-built, not at-ceiling. (The 0.977 that appears in cap-map prose is the *coarser internal* pos_acc from the chunk cascade, a different tagset — do not cite it as the standalone POS number.)
3. **WSD "HARD_PASS 0.868"** → that is **N=38 single-annotator McGuffey**; the same method scores **0.21–0.24 on UD-EWT**. General WSD sits at the MFS frequency wall (~0.57 verbs), HARD_FAIL to beat frequency.
4. **Slot-filling "1.0"** → **synthetic k=16 binding**, not real ATIS slot-F1. Real slot-filling is untested/under-built.
5. **Chunking "beats LLM 0.9304"** → substrate 0.9304 is real, but the head-to-head verdict is **UNKNOWN** (LLMs failed the format, not a clean substrate win); classical CRF ceiling is 0.94, so chunking is still marginally under-built.

---

## STEP 3 — GLASS-BOX IMPROVEMENT PATH (per under-built function, no gradient at runtime)

- **DEPENDENCY PARSER (0.7875, USER-priority, biggest headroom −0.10):** replace graph/local-argmax with **incremental TRANSITION parsing** (arc-eager or arc-standard; stack+buffer; O(n) glass-box) — this alone typically reaches **~0.88+ UAS**, past weak graph parsers. Add **averaged/structured perceptron with beam** + **richer features** (word+POS bigrams over stack-top/buffer-front, distance-bucketed, morphology suffix, Brown/word-cluster of head+dependent, valency) + **more epochs & full train** (current uses 12.3k tokens; classical MaltParser uses full PTB). **Bonus:** the maintained STACK yields the embedding-depth / c-command feature the agreement wall needs — one build closes two frontiers.
- **CHUNKER (0.9257, USER-priority):** move from per-token independent tags to **CRF-style global decode** (Viterbi over BIO with transition scores) + **richer features** (POS bigrams/trigrams, capitalization, 2–4-char affixes, gazetteers) → target **~0.94**. Small absolute gain but cheap.
- **POS (0.906):** add **structured Viterbi decode + suffix-tree/affix backoff + word-cluster features** (the standalone tagger is a lexicon+suffix backoff, not a structured perceptron) → target **~0.97**.
- **NER (0.654):** the cell itself names the fix — **Brown-cluster features + gazetteers + affix/shape features + CRF decode**; this is a pure feature gap, target **~0.88**. Highest ROI per point after the parser.
- **INTENT/ATIS (0.834):** richer n-gram + prototype features, more training, or a structured/margin classifier → target **~0.92+**.
- **REAL SLOT-FILLING (untested):** build a real ATIS-slot **BIO CRF** on the shared sequence backbone (the synthetic 1.0 does not count) → target **~0.94 F1**.
- **GROUNDING multi-hop (collapses at hop-2):** **sharded/partitioned store** to kill additive-store crosstalk (already queued) + per-hop cleanup gating.
- **SRL reader-relF1 (0.71 held-out, 0.22 wild):** depends on the parser (predicate-argument paths); lift the parser first, then add path/voice/selectional features. Wild-text failure is partly genuinely-hard.
- **GENUINELY-HARD (not a classical-features fix):** WSD-beyond-frequency, agreement-buried-subject CG, coreference on real slices, cross-sentence comprehension. These sit at or above the *classical* ceiling; the session's evidence says they need a *different mechanism* (role-binding relational feature, importance-weighting), not better structured features. Do not spend parser-grade effort here expecting classical gains.

---

## STEP 4 — TOP 3 CROSS-CUTTING MOVES (highest leverage)

1. **Incremental transition-parsing paradigm on a structured-perceptron backbone.** Lifts the parser 0.79→~0.88+ (USER #1), and its maintained stack *is* the c-command/depth feature the agreement wall lacks, and the transition framing generalizes to joint tag+chunk+parse. One paradigm, three payoffs. **Highest leverage.**
2. **A shared rich-feature library** (Brown/word-clusters, 2–4-char affixes, capitalization/shape, gazetteers, morphology suffix, distance buckets) exposed to *every* sequence labeler. The same library lifts POS 0.906→~0.97, NER 0.654→~0.88, chunking 0.93→0.94, and feeds the parser. NER's entire −0.23 gap is this.
3. **CRF-style global structured decode** (Viterbi/beam with transition scores) replacing independent per-token argmax across POS, chunking, NER, and real slot-filling simultaneously. Cheap, glass-box, and every sequence function inherits the gain.

*(All three are classical, inspectable, and gradient-free at runtime — squarely inside the substrate's glass-box invariant.)*

---

## BOTTOM LINE

The **biggest, cheapest wins are structural-parse, not meaning.** The dependency parser is the crown bottleneck — verified **UAS 0.7875 (MIDDLE_BAND), ~0.10 below the classical transition/MST ceiling**, and switching to **incremental arc-eager transition parsing with a structured-perceptron backbone and richer features** is a well-trodden glass-box path to ~0.88+ that simultaneously hands the subject-verb-agreement wall the maintained-stack depth feature it has been missing. Second-cheapest is **NER (0.654 → ~0.88)**, whose entire gap is a **Brown-cluster/gazetteer feature** deficit the cell already diagnosed. **POS (0.906→~0.97)** and **chunking (0.926→0.94)** are near-ceiling tidy-ups via **Viterbi/CRF decode + the same shared feature library**. All four are captured by the three cross-cutting moves (transition paradigm, shared rich-feature library, global CRF decode) — recombination of credited classical prior art, no gradient at runtime. By contrast, **WSD-beyond-frequency, buried-subject agreement CG, real-slice coreference, and cross-sentence comprehension are genuinely-hard**: they sit at or above the *classical* ceiling and the disk evidence says they need a *different mechanism* (relational role-binding, importance-weighting), so they should not be funded as classical-feature work. **Fund the parser first.**
