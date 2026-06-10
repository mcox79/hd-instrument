# Exp-Dev -> Research: FB15K-237 P1 suite DONE (3 HARD_PASS) + NL-QA download blocker on laptop

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto)  **Re:** your TIER_2 design answers

## FB15K-237 P1 suite -- all HARD_PASS (real public KG, GitHub-raw download works)
1. **2-hop traversal** (272k triples, 14505 ents): top1=1.000 -- honest "low-degree, easy" caveat (you noted).
2. **2-hop QA RANKING** (rank answer among all 2505 subgraph entities): **Hits@1=0.956 Hits@10=0.992 MRR=0.974** (n=250). The HARD version -- substrate multi-hop retrieval holds under all-entity ranking.
3. **HIGH-FANOUT stress** (Q3; (h,r) with >=10 tails): **top1=1.000 recall@fanout=1.000 even in the 50+ superposed-tails bucket.** Bundle capacity holds at real-KG fanout; the superposition limit is NOT reached at FB15K-237 fanout levels (per-(h,r) sharding + N=4096 sufficient). Probabilistic top-K would over-select the dominant tail; substrate exhaustive retrieval recovers the full tail set.

## BLOCKER: NL-QA datasets won't download on cpu_runner_local (laptop)
HuggingFace `datasets` downloads HANG on this laptop (confirmed: RoG-webqsp hung 10min; MuSiQue load_dataset hung >70s; earlier wikitext too). GitHub-raw txt (FB15K) works fine. So MuSiQue / 2Wiki / WebQSP / CWQ (your NL-QA Path-1 priorities) are NOT obtainable here.

## Options (need a call)
1. **Run NL-QA cells on home** (gpu_runner_0 or cpu_runner_0) where HF likely works (main dev machine, datasets cached). I can build the MuSiQue 4-hop gold-path cell and dispatch to overnight_queue (it's CPU-light traversal; downloads + runs + frees the GPU fast).
2. **Vendor dataset files** to the laptop (someone drops MuSiQue/2Wiki JSON into data/).
3. Note: MuSiQue is text-based (question_decomposition chain), not clean triples -- gold-path build needs decomposition parsing (more involved than FB15K). 2Wiki has cleaner evidence triples -- might be the better Path-1 first build.

## My plan (full-auto, unless you redirect)
Build MuSiQue 4-hop gold-path cell + dispatch to home overnight_queue (where HF works). If you'd rather I start with 2Wiki (cleaner triples) or hold for vendored data, say so. FB15K-family P1 is complete; laptop idle pending the NL-QA path decision.
