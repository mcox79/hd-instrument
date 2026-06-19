import sys

# Visibility entry
vis_entry = """
## CYCLE 231 (2026-06-11) -- v564->v565

[cycle-231] CYCLE 231 9-verdict batch processed: tier4_multiseed_sweep HARD_PASS 5-seed (Sprint-4 Tier-4 complete; PP-344/PP-361/PP-365/PP-366 seed-robust n=5); [LVH-282] math_light_substrate MIDDLE_BAND (coverage=0.086, accuracy=0.947, band-description mislabel in verdict_msg); codegen_light HARD_FAIL (25-pattern library insufficient, pass@1=0.150); codegen_repair HARD_FAIL (oracle-ceiling=0.175); codegen_subgoal HARD_FAIL (pass@1=0.025, filter/map/reduce fail); math_wordproblem_extract_gate HARD_FAIL (accuracy=0.023, extraction not the right axis for multi-step word problems); depparse_gate UNKNOWN (corpus_load_failed -- same PTB infra issue, NLP next-phase blocked); pos_oov_diagnostic UNKNOWN (corpus_load_failed); lang_math_coexist HARD_PASS PP-367 NEW (lang=1.000 math=1.000 cross=1.000, unified domain-agnostic algebra). Net: +1 PP row (PP-367), +9 HONEST, +1 LVH-282, 4 HF (codegen 3x + math_wordproblem), corpus_load_failed gates NLP benchmark phase (dep-parse + pos_oov + math_rescue). Portfolio 32+366->32+367. Sprint-4 Tier-4 cohort complete (all 5-seed). Codegen root cause: pattern library size (25 vs 70 Tier-1 patterns); RESCUE-1 trivial (re-run with full library).
"""

with open("d:/AI/hd-instrument/notes/visibility_decisions_2026-06-11.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(vis_entry)
print("visibility appended OK")

# Cap_map append
capmap_entry = """

## v564 -> v565 @ CYCLE 231 9-VERDICT BATCH Tier-4-multiseed-sweep + NLP-gates-corpus-fail + codegen-HF-batch + lang-math-coexist (verdict_handler 459th PROT-009 paired commit; 2 HP 1 MB 4 HF 2 UNKNOWN; 1 LVH-282 filed; 1 new PP row PP-367; Portfolio 32+366->32+367; HONEST 1740->1749; LVH 281->282)

**tier4_multiseed_sweep_cpu_v1 HARD_PASS v565 (5-seed):** crystallized (5/5), excitability (5/5), code2-adv (5/5), key-rot-10k (5/5). Sprint-4 Tier-4 anchor cohort COMPLETE. PP-344/PP-361/PP-365/PP-366 upgraded to seed-robust n=5. No new PP rows.

**[LVH-282] math_light_substrate_cpu_v1 MIDDLE_BAND v565:** accuracy=0.947 on covered subset, coverage=0.086 (<0.15 threshold). Band description mislabeled (verdict_msg says "accuracy 0.20-0.35" but failing axis is coverage=0.086). Coverage is blocking axis; extraction approach (item F) does not close gap. No new PP row.

**codegen_light_substrate_cpu_v1 HARD_FAIL v565:** pass@1=0.150 (6/40), n_patterns=25. Pattern library insufficient (PP-363 used 70, gave 60%). RESCUE-1: re-run with full 70-pattern Tier-1 library. No new PP row.

**codegen_repair_substrate_cpu_v1 HARD_FAIL v565:** oracle-ceiling=0.175 <0.20. Same root cause as codegen_light. RESCUE-1 shared. No new PP row.

**codegen_subgoal_substrate_cpu_v1 HARD_FAIL v565:** pass@1=0.025 (1/40). Filter/map/reduce chains insufficient. RESCUE-3 slot-chain Tier-2 (research-authorized fc62d8f1) is primary next step. No new PP row.

**math_wordproblem_extract_gate_cpu_v1 HARD_FAIL v565:** accuracy=0.023, coverage=0.801. Extraction approach wrong axis; multi-step reasoning required. RESCUE-4/5 blocked pending corpus fix. No new PP row.

**depparse_gate_substrate_cpu_v1 UNKNOWN v565:** corpus_load_failed, uas=0.0. Same PTB corpus failure as cycle-230. NLP benchmark next phase (dep-parse + pos_oov + math_rescue RESCUE-4/5) all gated on corpus RESCUE-1 fix. No cap_map credit.

**pos_oov_diagnostic_cpu_v1 UNKNOWN v565:** corpus_load_failed, tag_acc=0.0. exp_dev commit af0f024b claims in-vocab=0.946, OOV=0.749 (LOCAL authoritative: UNKNOWN). No cap_map credit.

**NEW ROW PP-367:** lang_math_coexist_cpu_v1 HARD_PASS v565: language_recall=1.000, math_recall=1.000, cross_domain_recall=1.000, KL=150, KM=150, n_seeds=1 (cycle 231). UNIFIED SUBSTRATE ALGEBRA LANGUAGE+MATH: one substrate, one codebook, one set of binding ops handles NL + math + cross-domain with zero interference. KL=150 + KM=150 coexist in N=4096. Domain agnosticism confirmed: NL+math do NOT require per-role substrates (PP-356). Extends PP-351 (v3.1 unified) by domain-axis. Product implication: unified multi-domain knowledge in single store. 0.80-0.92 EXPLORATORY n=1 seed full CPU elapsed=1.3s. Cross-ref PP-356, PP-364, PP-363, PP-351.

Cap_map: v564 -> v565 CYCLE 231 (2 HP [CPU:2; 1x5-seed + 1x n=1 full]; 1 MIDDLE_BAND [LVH-282]; 4 HF [CPU:4]; 2 UNKNOWN [corpus_load_failed depparse+pos_oov]; 1 LVH-282 filed [math_light band-description mislabel]; 1 NEW PP ROW PP-367 [lang_math_coexist unified algebra]; 4x Tier-C seed-robust promotion (PP-344/PP-361/PP-365/PP-366 via tier4_multiseed_sweep); 5x codegen_light + 2x codegen_repair + 5x codegen_subgoal + 5x math_wordproblem PROT-004/006 rescue sketches; corpus_load_failed NLP blocking: dep-parse+pos_oov+math_rescue gated on corpus RESCUE-1; 0 row closures; Portfolio 32+366 -> 32+367 +1; HONEST 1740->1749 +9; LVH 281->282 +1; 459th PROT-009 paired commit) (2026-06-11)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up."""

with open("d:/AI/hd-instrument/notes/substrate_capability_map.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(capmap_entry)
print("cap_map appended OK")
