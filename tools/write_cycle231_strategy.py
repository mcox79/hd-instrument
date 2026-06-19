import sys

entry = """

## v564 -> v565 CYCLE 231 9-VERDICT BATCH (2026-06-11)

tier4_multiseed_sweep + math_light_substrate + codegen_light_substrate + codegen_repair_substrate + codegen_subgoal_substrate + math_wordproblem_extract_gate + depparse_gate_substrate + pos_oov_diagnostic + lang_math_coexist. All on cpu_runner_local (FrameworkMPC). Mix: Tier-4 multi-seed sweep + NLP gates (POS-OOV, depparse) + codegen variants + lang-math coexistence.

### Step 0 honest re-read

Metrics source: LOCAL (all 9 files at d:/AI/hd-instrument/data/exp_<name>/metrics.json). 1 LVH catch.

**tier4_multiseed_sweep_cpu_v1 HARD_PASS (HONEST -- 5-seed):** 4/4 anchors (crystallized, excitability, code2-adv, key-rot-10k) all 5/5 HARD_PASS. promote=4, fragile=0, fail=0. n_seeds=5. HONEST.

**[LVH-282] math_light_substrate_cpu_v1 MIDDLE_BAND (band-description mislabel):** verdict_msg says "accuracy 0.20-0.35 on curated subset" -- WRONG band description. Actual: accuracy=0.947, coverage=0.086 (<0.15 threshold -- this is the failing axis). MIDDLE_BAND verdict correct (coverage too low) but band label text misrepresents the failing axis. Honest reading: MIDDLE_BAND due to coverage=0.086 not accuracy. LVH-282 filed. Verdict tag stands MIDDLE_BAND.

**codegen_light_substrate_cpu_v1 HARD_FAIL (HONEST):** pass@1=0.150 (6/40) < 0.20 threshold. 25 patterns insufficient on substrate-natural HumanEval. HONEST.

**codegen_repair_substrate_cpu_v1 HARD_FAIL (HONEST):** oracle-ceiling=0.175, docstring-pass@1=0.150, selection-gap=0.025. Pattern library ceiling below 0.20. HONEST.

**codegen_subgoal_substrate_cpu_v1 HARD_FAIL (HONEST):** pass@1=0.025 (1/40), 20 composition-attempts. Filter/map/reduce chains fail on substrate-natural HumanEval. HONEST.

**math_wordproblem_extract_gate_cpu_v1 HARD_FAIL (HONEST):** accuracy=0.023 (4/177 correct of attempted), coverage=0.801. Keyword+number extraction fails; multi-step reasoning required. HONEST.

**depparse_gate_substrate_cpu_v1 UNKNOWN (HONEST -- corpus_load_failed):** uas=0.0, elapsed_s=0.046, error=corpus_load_failed. Same infrastructure failure as cycle-230 PTB anchors. No cap_map credit.

**pos_oov_diagnostic_cpu_v1 UNKNOWN (HONEST -- corpus_load_failed):** tag_acc=0.0, elapsed_s=0.0, error=corpus_load_failed. Same corpus infra failure. No cap_map credit.

**lang_math_coexist_cpu_v1 HARD_PASS (HONEST):** language_recall=1.000, math_recall=1.000, cross_domain_recall=1.000, KL=150, KM=150. All >= 0.95 threshold. n_seeds=1 full. HONEST. exp_dev commit d358f6e8 consistent.

HONEST: 1740 -> 1749 (+9). LVH: 281 -> 282 (+1, LVH-282 math_light band-description mislabel accuracy=0.20-0.35 text vs actual failing axis coverage=0.086). 1 LVH catch.

### Cap_map decisions (v564 -> v565)

**(A) tier4_multiseed_sweep_cpu_v1 (HARD_PASS 5-seed -- 4x Tier-C seed-robust promotions; Sprint-4 Tier-4 anchor sweep complete):**
tier4_multiseed_sweep v565 HARD_PASS (5-seed): crystallized, excitability, code2-adv, key-rot-10k all 5/5 HARD_PASS, promote=4, fragile=0, fail=0 (cycle 231). These 4 anchors individually validated cycle 230 (PP-365 crystallized, PP-366 excitability, PP-344/PP-361 code2/key-rotation adversarial). Sprint-4 Tier-4 anchor cohort COMPLETE -- all Sprint-4 primitives (write-lock, RS-parity, per-tier-importance, per-role-isolation, crystallized, excitability-gate, 3x-redundant) now have 5-seed confirmation. PP-365/PP-366 promoted seed-robust EXPLORATORY (n=5). PP-344/PP-361 adversarial annotations upgraded to seed-robust n=5. No new PP rows; tier-robustness upgrade on PP-344/PP-361/PP-365/PP-366.

**(B) [LVH-282] math_light_substrate_cpu_v1 (MIDDLE_BAND -- coverage gap; extraction approach fails):**
[LVH-282] math_light_substrate_cpu_v1 MIDDLE_BAND v565: accuracy=0.947 on covered subset (19/221), coverage=0.086 (<0.15 threshold) (cycle 231). Band description mislabeled in verdict_msg. COVERAGE IS BLOCKING AXIS: substrate retrieves math facts at 94.7% accuracy on matched patterns, but only 8.6% of 221 math problems match stored patterns. math_wordproblem_extract_gate (item F) also fails: extraction does not close coverage gap. No new PP row (MIDDLE_BAND, coverage below bar). LVH-282 filed.

**(C) codegen_light_substrate_cpu_v1 (HARD_FAIL -- PROT-004/006 rescue sketches; 25-pattern library insufficient):**
codegen_light_substrate_cpu_v1 HARD_FAIL v565: pass@1=0.150 (6/40), n_patterns=25 (cycle 231). Pattern library insufficient; PP-363 Gate-1 used 70 patterns (60%); 25 patterns gives only 15%. No new PP row. PROT-004/006 rescue sketches (cheapest first):
RESCUE-1 (cheapest/subsumption): re-run with 70-pattern Tier-1 library (already exists per PP-363) -- subsumes codegen_light.
RESCUE-2: pattern coverage audit -- map 40 curated HumanEval to nearest substrate-natural template; identify uncovered categories.
RESCUE-3: template generalization -- relax matching to allow partial slot-fill for wider coverage.
RESCUE-4: add Tier-2 composition patterns (research-authorized fc62d8f1).
RESCUE-5: hybrid substrate Gate-1 + LLM fallback for uncovered problems.
Route RESCUE-1 to Exp-Dev (trivial re-run with full Tier-1 library).

**(D) codegen_repair_substrate_cpu_v1 (HARD_FAIL -- oracle ceiling 0.175; same root cause as codegen_light):**
codegen_repair_substrate_cpu_v1 HARD_FAIL v565: oracle-ceiling=0.175, docstring-pass@1=0.150, selection-gap=0.025 (cycle 231). Oracle ceiling confirms pattern library is blocker, not selection strategy. No new PP row. PROT-004/006 rescue: RESCUE-1 same as codegen_light (expand to 70-pattern Tier-1 library). Shared root cause.

**(E) codegen_subgoal_substrate_cpu_v1 (HARD_FAIL -- filter/map/reduce insufficient; slot-chain templates needed):**
codegen_subgoal_substrate_cpu_v1 HARD_FAIL v565: pass@1=0.025 (1/40), n_attempted=20 (cycle 231). Composition chains with 25 patterns fail as expected. No new PP row. PROT-004/006 rescue sketches (cheapest first):
RESCUE-1 (cheapest): expand to 70-pattern Tier-1 library first.
RESCUE-2: function-call composition vs pipeline composition.
RESCUE-3 (primary): slot-chain templates (Tier-2 per research authorization fc62d8f1) -- 2-3-step chains pre-stored as patterns.
RESCUE-4: test on HumanEval subproblems that are purely filter/map/reduce semantics.
RESCUE-5: hybrid -- substrate subgoal decomposition + LLM synthesis per subgoal.
Route RESCUE-3 (slot-chain Tier-2) to Exp-Dev as research-authorized next step.

**(F) math_wordproblem_extract_gate_cpu_v1 (HARD_FAIL -- extraction fails; multi-step reasoning required not extraction):**
math_wordproblem_extract_gate_cpu_v1 HARD_FAIL v565: accuracy=0.023 (4/177), coverage=0.801 (cycle 231). High coverage (80%) but near-zero accuracy confirms: math coverage gap is NOT closable by extraction; word problems require multi-step reasoning. No new PP row. PROT-004/006 rescue sketches (cheapest first):
RESCUE-1 (cheapest): curated simple arithmetic subset (add/subtract only) -- find lower bound.
RESCUE-2: template-matching word-problem schemas stored as substrate patterns.
RESCUE-3: chain-of-operations encoding as HD vectors decoding to program traces.
RESCUE-4: hybrid dep-parse + substrate symbolic evaluation (dep-parse extracts NL structure, substrate evaluates arithmetic).
RESCUE-5: routing to math_light only after NL-to-expression pre-parse (dep-parser or slot-filler first-stage).
RESCUE-4 and RESCUE-5 blocked pending corpus fix (item G).

**(G) depparse_gate_substrate_cpu_v1 (UNKNOWN -- corpus_load_failed; dep-parse build deferred):**
depparse_gate_substrate_cpu_v1 UNKNOWN v565: corpus_load_failed, uas=0.0, elapsed_s=0.046 (cycle 231). Same corpus failure as cycle-230 PTB anchors. Research commit 41e0bf24 authorized dep-parse Phase 1 (UD-English-EWT UAS>=0.85). Corpus fix is gating dep-parse gate + pos_oov_diagnostic + math_wordproblem rescue paths RESCUE-4/5. No cap_map credit. PROT-004/006 RESCUE-1 (NLTK download or UD-English-EWT substitution) is prerequisite for entire NLP benchmark next phase.

**(H) pos_oov_diagnostic_cpu_v1 (UNKNOWN -- corpus_load_failed; PP-364 OOV characterization deferred):**
pos_oov_diagnostic_cpu_v1 UNKNOWN v565: corpus_load_failed, tag_acc=0.0, elapsed_s=0.0 (cycle 231). exp_dev commit af0f024b reports in-vocab=0.946, OOV=0.749, projected@2.5%OOV=0.941 (LOCAL authoritative: UNKNOWN). No cap_map credit. If confirmed: PP-364 OOV gap (0.946-0.749=0.197pp) is path to STRONG 0.95+ bar; requires full-PTB + richer in-vocab modeling. Deferred pending corpus fix.

**(I) lang_math_coexist_cpu_v1 (HARD_PASS -- NEW ROW PP-367; unified domain-agnostic algebra):**
NEW ROW PP-367: lang_math_coexist_cpu_v1 HARD_PASS v565: language_recall=1.000, math_recall=1.000, cross_domain_recall=1.000, KL=150, KM=150, n_seeds=1 (cycle 231). UNIFIED SUBSTRATE ALGEBRA LANGUAGE+MATH: one substrate, one codebook, one set of binding ops handles language (1.000), math (1.000), AND cross-domain math-result-to-language-label (1.000) with zero interference. KL=150 + KM=150 coexist in N=4096 shared space. Confirms domain agnosticism: NL and math do NOT require per-role substrates (PP-356) -- single substrate suffices. Extends PP-351 (v3.1 unified) by domain-axis. exp_dev commit d358f6e8 consistent. Product implication: unified multi-domain knowledge (language + math + code) in single store. 0.80-0.92 EXPLORATORY n=1 seed full CPU elapsed=1.3s. Cross-ref PP-356 (per-role isolation), PP-364 (POS tagger NL), PP-363 (codegen math), PP-351 (v3.1 unified).

Cap_map: v564 -> v565 CYCLE 231 (2 HP [CPU:2; 1x5-seed + 1x n=1 full]; 1 MIDDLE_BAND [LVH-282 math_light]; 4 HF [CPU:4]; 2 UNKNOWN [corpus_load_failed depparse+pos_oov]; 1 LVH-282 filed [math_light band-description mislabel]; 1 NEW PP ROW PP-367 [lang_math_coexist unified algebra]; 4x Tier-C seed-robust promotion (PP-344/PP-361/PP-365/PP-366 via tier4_multiseed_sweep); 5x codegen_light PROT-004/006 rescue sketches; 2x codegen_repair shared RESCUE-1; 5x codegen_subgoal PROT-004/006 rescue sketches; 5x math_wordproblem PROT-004/006 rescue sketches; corpus_load_failed NLP blocking: dep-parse+pos_oov+math_rescue gated on corpus RESCUE-1; 0 row closures; Portfolio 32+366 -> 32+367 +1; HONEST 1740->1749 +9; LVH 281->282 +1; 459th PROT-009 paired commit) (2026-06-11)
"""

with open("d:/AI/hd-instrument/notes/strategy_decisions_2026-06-11.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)
print("strategy_decisions appended OK")
