# Pre-reg: parser-SNR Technique-1 de-risk (structured query) (GPU/bge)
Date 2026-06-12. Cell exp_parser_snr_structured_query_derisk_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
De-risks Cycle-52 nl_to_hrr_parser Technique 1 (structured Tier-A query parse). Compare RAW-text vs STRUCTURED-term query ->
bge query->atom retrieval (gold rank/cos/recall) on A+E+G free-text Qs. HARD-PASS structured beats raw (recall@3 +0.05 or
median-rank +1). HARD-FAIL no improvement (raw bge saturates retrieval; parser payoff is in compose/decode not retrieval).
