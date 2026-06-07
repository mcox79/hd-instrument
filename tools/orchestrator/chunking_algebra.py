import math

# === WIKIPEDIA CORPUS PARAMETERS ===
N_articles = 7_200_000
words_per_article_mean = 717
tokens_per_word = 1.35  # BPE subword inflation
tokens_per_article = words_per_article_mean * tokens_per_word
total_tokens = N_articles * tokens_per_article
print(f'Wikipedia articles: {N_articles:,}')
print(f'Tokens per article (mean): {tokens_per_article:.0f}')
print(f'Total tokens: {total_tokens/1e9:.2f}B')

# === BASELINE: SINGLE H100, 1B MODEL (known) ===
h100_1b_s_per_doc = 5.7 * 60 / 10_000
h100_cost_per_hr = 2.5
h100_1b_total_hr = (N_articles * h100_1b_s_per_doc) / 3600
h100_1b_cost = h100_1b_total_hr * h100_cost_per_hr
print(f'\n=== BASELINE H100 + 1B model ===')
print(f's/doc: {h100_1b_s_per_doc:.4f}')
print(f'Total wall (single H100): {h100_1b_total_hr:.1f} hr')
print(f'Total cost: ${h100_1b_cost:.2f}')

# === H100 + 70B MODEL ===
toks_per_sec_70b_h100 = 100
s_per_doc_70b = tokens_per_article / toks_per_sec_70b_h100
h100_70b_total_hr = (N_articles * s_per_doc_70b) / 3600
n_gpus_70b = 8
h100_70b_cost = h100_70b_total_hr * h100_cost_per_hr * n_gpus_70b
print(f'\n=== H100 x8 + 70B model ===')
print(f's/doc: {s_per_doc_70b:.3f}')
print(f'Total wall: {h100_70b_total_hr:.1f} hr')
print(f'Total cost (8x H100): ${h100_70b_cost:.0f}')

# === H100 + 405B MODEL ===
toks_per_sec_405b_h100x16 = 30
s_per_doc_405b = tokens_per_article / toks_per_sec_405b_h100x16
h100_405b_total_hr = (N_articles * s_per_doc_405b) / 3600
n_gpus_405b = 16
h100_405b_cost = h100_405b_total_hr * h100_cost_per_hr * n_gpus_405b
print(f'\n=== H100 x16 + 405B model ===')
print(f's/doc: {s_per_doc_405b:.3f}')
print(f'Total wall: {h100_405b_total_hr:.1f} hr')
print(f'Total cost (16x H100): ${h100_405b_cost:.0f}')

# === CHUNKED DISTRIBUTION SCENARIOS ===
print('\n=== CHUNKED DISTRIBUTION SCENARIOS ===')

# SCENARIO A: 100 CPU instances (AWS t4g.xlarge ~$0.04/hr each)
n_cpu_workers = 100
toks_per_sec_cpu_7b = 60
s_per_doc_cpu = tokens_per_article / toks_per_sec_cpu_7b
docs_per_worker = N_articles / n_cpu_workers
wall_cpu_hr = (docs_per_worker * s_per_doc_cpu) / 3600
cost_per_worker_hr = 0.04
total_cost_cpu = wall_cpu_hr * cost_per_worker_hr * n_cpu_workers
model_load_s = 300
wall_cpu_total_hr = wall_cpu_hr + model_load_s/3600
print(f'\n[A] 100 CPU workers (t4g.xlarge), 7B Q4:')
print(f'  s/doc per worker: {s_per_doc_cpu:.4f}')
print(f'  Wall time: {wall_cpu_total_hr:.1f} hr')
print(f'  Total cost: ${total_cost_cpu:.2f}')

# SCENARIO B: 100 idle M-series laptops (M2/M4 Max, 70B Q4)
n_mac_workers = 100
toks_per_sec_mac_70b = 10
s_per_doc_mac = tokens_per_article / toks_per_sec_mac_70b
docs_per_mac = N_articles / n_mac_workers
wall_mac_hr = (docs_per_mac * s_per_doc_mac) / 3600
wall_mac_total_hr = wall_mac_hr + 900/3600
electricity_cost_per_mac_hr = 0.001
total_cost_mac = wall_mac_total_hr * electricity_cost_per_mac_hr * n_mac_workers
print(f'\n[B] 100 idle Macs (M2-M4 mix), 70B Q4:')
print(f'  s/doc per worker: {s_per_doc_mac:.4f}')
print(f'  Wall time: {wall_mac_total_hr:.1f} hr')
print(f'  Total cost (electricity only): ${total_cost_mac:.2f}')

# SCENARIO C: 1000 consumer GPUs (4090, 30B Q4)
n_consumer_gpus = 1000
toks_per_sec_4090_30b = 200
s_per_doc_4090 = tokens_per_article / toks_per_sec_4090_30b
docs_per_gpu = N_articles / n_consumer_gpus
wall_4090_hr = (docs_per_gpu * s_per_doc_4090) / 3600
electricity_per_4090_hr = 250 * 0.12 / 1000
total_cost_4090 = wall_4090_hr * electricity_per_4090_hr * n_consumer_gpus
print(f'\n[C] 1000 consumer GPUs (4090), 30B Q4:')
print(f'  s/doc per worker: {s_per_doc_4090:.4f}')
print(f'  Wall time: {wall_4090_hr:.1f} hr')
print(f'  Total cost (electricity only): ${total_cost_4090:.2f}')

# SCENARIO D: 10000 smartphone NPUs (1B Q4)
n_phones = 10000
toks_per_sec_npu_1b = 50
s_per_doc_phone = tokens_per_article / toks_per_sec_npu_1b
docs_per_phone = N_articles / n_phones
wall_phone_hr = (docs_per_phone * s_per_doc_phone) / 3600
electricity_per_phone_hr = 0.0002
total_cost_phone = wall_phone_hr * electricity_per_phone_hr * n_phones
print(f'\n[D] 10000 smartphone NPUs, 1B Q4:')
print(f'  s/doc per worker: {s_per_doc_phone:.4f}')
print(f'  Wall time: {wall_phone_hr:.1f} hr')
print(f'  Total cost (electricity only): ${total_cost_phone:.2f}')

# === OUTPUT DATA VOLUME ===
print('\n=== OUTPUT DATA VOLUME ===')
N_substrate = 10_000
bytes_per_doc_bf16 = N_substrate * 2
total_output_gb_bf16 = N_articles * bytes_per_doc_bf16 / (1e9)
total_output_gb_fp32 = N_articles * N_substrate * 4 / (1e9)
print(f'Output volume (bf16, N=10K): {total_output_gb_bf16:.1f} GB')
print(f'Output volume (fp32, N=10K): {total_output_gb_fp32:.1f} GB')

per_worker_output_100 = total_output_gb_bf16 / 100
upload_mbps = 10
upload_time_s = (per_worker_output_100 * 8 * 1000) / upload_mbps
print(f'Per-worker output (100 workers, bf16): {per_worker_output_100:.2f} GB')
print(f'Upload time per worker at 10Mbps: {upload_time_s:.0f} s = {upload_time_s/3600:.2f} hr')

# === OPTIMAL CHUNK SIZE ===
print('\n=== OPTIMAL CHUNK SIZE ===')
model_load_s_7b_cpu = 300
extract_s_per_doc_cpu = s_per_doc_cpu
min_chunk_90pct_cpu = 9 * model_load_s_7b_cpu / extract_s_per_doc_cpu
print(f'Min chunk for >90% efficiency (7B CPU, load=300s): {min_chunk_90pct_cpu:.0f} docs')

model_load_s_70b_mac = 900
min_chunk_90pct_mac = 9 * model_load_s_70b_mac / s_per_doc_mac
print(f'Min chunk for >90% efficiency (70B Mac, load=900s): {min_chunk_90pct_mac:.0f} docs')

# === FAULT TOLERANCE ===
print('\n=== FAULT TOLERANCE OVERHEAD ===')
redundancy = 0.10
sentinel_pct = 0.02
effective_factor = 1 / (1 + redundancy + sentinel_pct)
print(f'Effective throughput factor with FT: {effective_factor:.3f}  (~{(1-effective_factor)*100:.0f}% overhead)')

# === RECOMMENDED ARCHITECTURE: 70B Wikipedia <$50 ===
print('\n=== RECOMMENDED ARCHITECTURE: 70B Wiki <$50 ===')
# Mix: 20 cloud CPU workers at $0.04/hr (7B Q4 for cheap docs)
# + 10 H100 hours for high-value docs / spot GPU burst
# Strategy: 2-tier extraction
# Tier A: 7B Q4 on CPU fleet for 80% of docs (body-only, cheap)
# Tier B: 70B on remote GPU burst for top 20% high-info articles
n_cpu_A = 100
cost_cpu_A = wall_cpu_total_hr * 0.04 * n_cpu_A
print(f'Tier A (100 CPU x 7B): ${cost_cpu_A:.2f} for full corpus')
# If we use spot instances at $0.02/hr:
cost_cpu_spot = wall_cpu_total_hr * 0.02 * n_cpu_A
print(f'Tier A (100 CPU x 7B, spot): ${cost_cpu_spot:.2f}')
# Spot pricing + preemption recovery: multiply by 1.15
print(f'Tier A with 15pct FT overhead: ${cost_cpu_spot * 1.15:.2f}')
