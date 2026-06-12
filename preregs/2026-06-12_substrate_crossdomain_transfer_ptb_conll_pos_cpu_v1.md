# Pre-reg: 3rd-appearance cross-domain POS transfer (PTB -> CoNLL-2003)

Date 2026-06-12 Cycle 50. Cell exp_substrate_crossdomain_transfer_ptb_conll_pos_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
3rd-appearance candidate for meta::RULE_cross_domain_transfer_tail_shape (open-vocab persists / closed-feature converges).
POS = OPEN-VOCAB sequence labeling -> predicted NON-CONVERGING tail (like NER). discriminative_perceptron POS tagger, PTB (WSJ)
warm-start -> CoNLL-2003 POS (Reuters), Penn tagset aligned; token accuracy; fractions {1,2.5,5,10,100}pct, 3 seeds.
Bands (discriminator = TAIL ratio@100pct): HARD-PASS ratio@100pct>=1.02 AND ratio@2.5pct>=1.02 (tail persists -> rule confirmed).
MIDDLE ratio@100pct in [0.99,1.02]. HARD-FAIL ratio@100pct<0.99 (POS converges -> refines rule: tagset-closedness vs open-vocab).
UNKNOWN if CoNLL download fails. Smoke: zero-shot 0.80; ratio@2.5pct=1.67.
