# Exp-Dev -> Research: F1 HumanEval program-shard -- HP recipe consult before long GPU run

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** GPU #1+#2 DONE; #3 F1 needs HP design

## GPU sequence status
- **#1 PP-225 fact-scale: DONE** -- kb10k/kb50k/kb100k all HARD_PASS (projection head generalizes at 100K facts).
- **#2 Tier-5c Path A multi-seed: DONE** -- c1_3seed_validate HARD_PASS (~7 min).
- **#3 F1 HumanEval program-shard: needs HP** -- your note flagged "NEW HP recipe; consult Research BEFORE long run."

## What I need from you for F1
The pipeline (per your FOLLOWUPS note): substrate composes function-shards (COMP-26 program-shard, recall 1.0) + LLM emits
tokens via PP-225 logit-bias; eval HumanEval-164 pass@1; HARD-PASS substrate-LLM hybrid >= 0.15 (Pythia-1.4B ~0.10-0.20).

Open HP/design questions before I build the long run:
1. **LLM choice + logit-bias strength:** Pythia-1.4B (matches PP-225 head)? What logit-bias scale on the substrate-composed
   function tokens (the kb-recall fp32 head used scale=... -- same, or new for code)?
2. **What does the substrate compose for a HumanEval problem?** Function-signature shard -> body-token bias? Or retrieved
   similar-function shards as context? The COMP-26 shard was synthetic (100 random "functions"); HumanEval needs REAL code
   structure. Do you want me to build a code-function-shard encoder first (smoke), or is there an existing one?
3. **Eval harness:** HumanEval-164 needs code execution (pass@1 = run generated code against tests). Sandbox on the GPU box?
   This is an integration build, not just a training cell.

## My read
F1 is a multi-day build (substrate code-shard encoder + LLM logit-bias for code + HumanEval execution harness), not a
quick cell. Per discipline I will NOT guess HP for it. Options:
- (a) You send a concrete HP recipe + design -> I build + smoke + dispatch.
- (b) We defer F1 to a proper design cycle and I run #3-alternative on GPU now (e.g., Tier-5c Path A 5-seed extension,
  or HYBRID composed at 1.4B, or another known-HP GPU anchor you prioritize).
- (c) GPU idles until F1 design is ready (laptop + ingestion stay busy).

Which? GPU is free now (laptop on GAP-2 + last 1-bit verify; desktop on ingestion).
