# Exp-Dev -> Testbed: ColBERT-v2 install + index + pre-test HANDOFF (dependency hell -- needs a clean focused env)

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** Research, Orchestrator  **Date:** 2026-06-07
**Re:** ColBERT-v2 multi-hop pretest -- Research-authorized (research_to_exp_dev_colbert_pretest_authorize +
colbert_ragatouille_install_authorize). Porting to Testbed per user direction: GPU-infra + dependency resolution is your lane.

## Why this is yours
ColBERT-v2 = retrieval-infra + GPU indexing + a gnarly dependency tree. I hit dependency hell on the local runner and the
clean fix belongs in a focused env (cloud or isolated), not bolted onto the local substrate pipeline.

## What I already did (so you don't repeat it)
- Created an ISOLATED venv on the runner (C:\dev\hd-instrument\.venv-colbert) so the MAIN venv (torch 2.5.1, the 50-cell
  pipeline) stays untouched. Confirmed main venv unaffected.
- `pip install ragatouille` SUCCEEDED into that venv: ragatouille-0.0.9.post2, colbert-ai-0.2.22, faiss-cpu-1.14.2,
  torch-2.12.0, transformers-5.10.2, langchain-1.3.4, llama-index-0.14.22, sentence-transformers-5.5.1.
- BUT it WON'T IMPORT: `ModuleNotFoundError: No module named 'langchain.retrievers'`. ragatouille 0.0.9 expects the OLD
  langchain API (langchain.retrievers.*), but pip pulled langchain 1.3.x (new namespaced API). Classic version skew.

## The fix you need to resolve
Pin a compatible set. Likely one of:
- ragatouille's own pinned langchain (try `pip install "langchain<0.2"` or `langchain-community` shim in the same venv), OR
- a known-good ColBERT-v2 stack without ragatouille (use colbert-ai directly: `from colbert import Indexer, Searcher`),
  which sidesteps ragatouille's langchain dependency entirely -- this is probably the cleaner path.
- Also note torch-2.12.0 got pulled (fine in the isolated venv; needs a CUDA build matching the GPU).

## The actual experiment (once the env imports)
- Build a ColBERT-v2 index over HotpotQA-distractor passages (data on runner: data/datasets/hotpot_qa_distractor_dev_1k.jsonl;
  flatten context.sentences into passages). Or use hotpot_fullwiki (staged in HF cache).
- 100 HotpotQA bridge questions; measure **recall@2 and recall@10**.
- Compare to bge-small baseline: recall@2=0.42, recall@10=0.74.
- **HARD-PASS: recall@2 >= 0.55** (gates the 2-3 week ColBERT integration). BORDER 0.50-0.55. HARD-FAIL <0.50 (ColBERT path
  closed; pivot to LongMemEval/FActScore where substrate audit+persistence dominate without multi-hop precision).
- Wall: ~2-3 hr GPU (install fix + index + pretest). File the verdict to Research.

## Context: the multi-hop ladder this gates
bge-small recall@2 plateaus at 0.42; cross-encoder rerank + BM25-RRF + LLM-decomp all FAIL to lift it (filed). ColBERT
late-interaction is the architectural candidate. If it clears 0.55, it's the v1 multi-hop retrieval upgrade; if not, multi-hop
is conceded at fair size and the demo leans on hotpot_3baseline answer-F1 (substrate +0.28 vs bare, ties RAG -- already HP).

I keep the substrate/benchmark cells on the local runner (hotpot_fullwiki_3baseline HP, trivia_rc queued, entropy-max
re-queued). Ping me if you need the HotpotQA passage-flattening snippet or the bge baseline numbers.
