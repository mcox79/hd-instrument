# Research drill: the EXACT brain mechanism of event segmentation (2026-09-07)

Full-text drill of the primary sources, to replicate the brain's computation glass-box (NO LLM at inference).
Prompted by the human-boundary validation (SOLVED §4h) showing our flat content monitors are near chance vs actual
human boundaries. This note pins WHAT the brain computes and HOW we differed, and grounds the implementations (§4l).

## 1. Kumar, Toneva, Norman, Zacks, Hasson et al. 2023 (Cognitive Science) -- Bayesian surprise, NOT surprisal
Run GPT-2 over a spoken story; at each word get the full next-word distribution P_t (softmax over ~50k, no top-k).
Three candidate signals vs human button-press boundary rates:
- **Surprisal** `S_t = -log p_w`, p_w = prob under P_{t-1} of the word actually presented at t. (prediction error)
- **Entropy** `E_t = -sum_v p_v log p_v` (spread of P_t).
- **Bayesian surprise** `BS(P_t,P_{t-1}) = -sum_v p_v log(q_v/p_v) = KL(P_t || P_{t-1})`, p in P_t (posterior), q in
  P_{t-1} (prior). = how much the whole forward distribution MOVED after hearing word t.
"Transient" = each divided by its leaky running-average baseline (Reynolds Eq.7; drift 0.03-0.10), regressed (LASSO,
trailing window 20-200 words, leave-one-story-out) onto smoothed human boundaries; circular-shift null.
**RESULT: transient Bayesian surprise predicts human boundaries (rho ~0.10-0.12, >=95th pct null); SURPRISAL does
NOT (near-zero/negative).** Cognitive reading: surprisal conflates "locally hard to predict" with "the world
changed"; only a shift in the forward BELIEF (KL, Itti-Baldi surprise) is a model update = a boundary.

## 2. Franklin, Norman, Ranganath, Zacks & Gershman 2020 (Psych Review) -- SEM, the structured segmenter
Generative model: (a) sticky-CRP prior over which schema is active -- `Pr(e_n=k) ~ C_k + lam*I[e_{n-1}=k]` for
existing k, `~ alpha` for a new schema (alpha = simplicity/concentration, lam = stickiness/event-length); (b) per-
schema scene DYNAMICS `Pr(x_{n+1}|x_1:n,e) = N(x_{n+1}; f(x_1:n; theta_e), diag(sigma^2))`, f = a learned forward
model (GRU in their sims; "agnostic to the shape of f"); at a fresh event the transition uses a learned initial
state f_0. Log-likelihood `log N = -1/(2 sigma^2) ||x_{n+1} - f_e(x_1:n)||^2 + const` (Eq.6) = NEGATIVE squared
prediction error. Online inference = local MAP (single forward sweep, point estimate of the past):
`score(k) = log(C_k + lam*I[k=cur]) - ||x_next - f_k||^2/(2 sigma^2)` ; `score(new) = log alpha - ||x_next-f_0||^2/(2 sigma^2)`.
**BOUNDARY iff the argmax schema SWITCHES: `e_hat_{n+1} != e_hat_n`** -- fires when the current schema's prediction
error grows enough that a different existing schema, or a new one (log alpha + f_0 constant), wins the MAP.

## 3. Reynolds, Zacks & Braver 2007 -- the gating ancestor
Feed-forward predictor of the next perceptual frame + a gated event layer. `AvgPredErr_t = AvgPredErr_{t-1} +
0.05*(SSE_t - AvgPredErr_{t-1})` (running baseline, ~20 steps). **Gate = 1 iff SSE_t / AvgPredErr_{t-1} > 1.5** (a
transient RATIO, robust 0.5-2.5; ROC AUC 0.94). Gate open -> overwrite the event layer with current input (new event);
closed -> hold (maintain). SEM's -||error||^2 IS this SSE; SEM's CRP switch IS this gate, made Bayesian.

## 4. What is the brain's FORWARD MODEL? (the load-bearing answer)
NOT a token predictor. SEM: a LIBRARY of event schemas, each a learned dynamical system over STRUCTURED scene
embeddings (agents/actions/objects bound via HRR circular convolution = the substrate's FHRR). Discrete inventory
indexed by the nonparametric prior (a growing library of construction competencies -- matches the substrate framing).
Acquired offline over a lifetime -> an ADMISSIBLE static asset (the invariant is no LLM at INFERENCE; offline schema
learning + online MAP is fine). Baldassano 2017: complementary data-driven view -- an event = a temporally stable
multivariate pattern; boundaries = latent-HMM state transitions.

## 5. HOW WE DIFFERED, and what we implemented (§4l)
Our monitors compute PREDICTION ERROR (surprisal/cosine) over a POINT prediction with a FLAT gist -- three exact
gaps vs (distribution-shift KL) x (rich distribution) x (latent-schema switch). Implemented glass-box: (a) the KL
Bayesian-surprise monitor -- correct computation, but our sparse PPMI distribution is too weak (below chance vs
humans; best on the proxy); (b) minimal SEM (linear per-schema dynamics + sticky-CRP MAP switch) -- **the structured
architecture WINS vs actual humans (AUC 0.60-0.65 vs incumbent 0.53, cross-story + default-param robust), while being
worse on the GUM proxy** -- proving the proxy misled us and the schema-switch architecture is genuinely human-aligned.

## Sources
- Kumar et al. 2023, Cognitive Science: https://pmc.ncbi.nlm.nih.gov/articles/PMC11654724/ (DOI 10.1111/cogs.13343)
- Franklin, Norman, Ranganath, Zacks & Gershman 2020, Psych Review: https://gershmanlab.com/pubs/Franklin20.pdf (DOI 10.1037/rev0000177)
- Reynolds, Zacks & Braver 2007: DOI 10.1080/15326900701399913
- Baldassano et al. 2017, Neuron: DOI 10.1016/j.neuron.2017.06.041
