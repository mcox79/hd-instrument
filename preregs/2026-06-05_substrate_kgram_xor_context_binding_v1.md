# Prereg: substrate_kgram_xor_context_binding_v1
## Anchor
substrate_kgram_xor_context_binding_v1
## Routing
K2-XOR-1 (research kgram_xor rescue): XOR k-gram context binding rescues bigram-level prediction (retrieval-side only, all moats). 2nd-order Markov chain. CPU $0.
## Bands
HARD-PASS K2/K1>=1.20x. MIDDLE 1.05-1.20x. HARD-FAIL <=1.02x.
Smoke: K1=0.079 K2=0.358 (4.54x) -> HARD_PASS. Substrate is k-th-order via context encoding, not fundamentally bigram.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
