# Cascade synapse + replay-driven consolidation: the pinned mathematics

Literature drill for ORGAN 5 (D8 synapse + D4 replay schedule) of `notes/ORGAN_MAP.md`.
Date: 2026-08-14. No code written, no cells dispatched, no `hdlab/` files touched.

Every claim below is marked **PINNED** (equation + citation, read off a source I actually opened),
**DERIVED** (my consistency argument from pinned facts, not in the literature verbatim), or
**UNPINNED** (the literature does not fix it, or I could not verify it in this drill). Nothing is
filled with plausible prose.

**Sources actually opened and text-extracted in this drill** (PDF -> text, `scratch/pdfdrill/`):
Benna & Fusi 2016 *Nat Neurosci* 19:1697 (full paper incl. Online Methods); Ben Dayan Rubin & Fusi
2007 *Front Comput Neurosci* 1:7; Fusi 2021 arXiv:2108.07839 "Memory capacity of neural network
models"; Zenke & Fusi-lineage review arXiv:1706.04946; Lahiri & Ganguli 2013 NIPS "A memory
frontier for complex synapses"; McClelland, McNaughton & O'Reilly 1995 *Psych Rev* 102:419;
Landauer & Bjork 1978; Davis & Gaskell 2009 *Phil Trans R Soc B* 364:3773; ar5iv HTML of
arXiv:1507.07580 (Benna & Fusi preprint).

**Source I could NOT open:** Fusi, Drew & Abbott 2005 *Neuron* 45:599 itself. cell.com returns 403 /
HTML; the "open access BRONZE" URL Semantic Scholar advertises serves a login page; ScienceDirect
403s. The NYU-hosted `fusi_etal2005.pdf` is a **journal-club slide deck by Dani Marti**, not the
paper -- it is usable as a secondary source but is NOT the primary. Everything attributed to Fusi
2005 below therefore comes from **Fusi's own later restatements** (Ben Dayan Rubin & Fusi 2007
Figure 1 legend and section "Complexity reduces the initial S/N"; Fusi 2021 review S3.3), plus that
slide deck. Where a constant depends on reading the 2005 paper directly, it is flagged.

---

## 0. PRIOR-WORK CHECK (required by the brief)

```
bash D:/AI/hd-instrument/tools/substrate_query.sh \
  "cascade synapse metaplasticity consolidation replay catastrophic interference memory lifetime"
```

Result: `kb_version=v1 schema=v2 encoder=char_trigram_v1 confidence=0.3086 refused=False`

| rank | entity | cosine | class |
|---|---|---|---|
| 1 | `regulation of synaptic metaplasticity` (GO:0031916) | 0.3086 | gene_ontology |
| 2 | `cataplastic` | 0.3008 | wordnet |
| 3 | `negative regulation of synaptic metaplasticity` (GO:0031917) | 0.2949 | gene_ontology |
| 4 | `regulation of synapse structural plasticity` (GO:0051823) | 0.2803 | gene_ontology |
| 5 | `notes/research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md::chunk010` | 0.2793 | note |

**Prior-work check: NONE above cosine 0.30 that is prior project work.** The three hits above 0.30
are ontology/lexicon entries, not prior arcs. The nearest prior project note is at **0.2793**.

`grep -i` over `notes/` for `Benna|Fusi, Drew|cascade synapse|Fusi 2005|Fusi et al` returns 15 files.
The only substantive prior treatment is
`D:/AI/hd-instrument/notes/research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md`
(sub-question 3, "METAPLASTICITY -- STATE VARIABLE COST"). What it already had: Benna-Fusi named;
`SNR ~ t^{-1/2}` vs exponential; "geometrically increasing time constants"; a memory-cost estimate
(`K=3` variables -> ~50 MB at N=2048); the observation that one replay event has ~1% effect on `u_3`
at `tau_2 ~ 100 tau_1`; verdict **"metaplasticity is biologically richest but NOT justified for
first-pass"**. What it did NOT have, and this drill adds: the cascade state space and transition
rules at all; the coupled ODEs with `C_k` / `g_{k,k+1}`; the geometric constants; the discrete-time
recurrence; the SNR formula with its prefactors and regime of validity; the initial-SNR COST; the
capacity-scaling attributions. Also note that note's `K=3-5` is **far below** what the paper
requires -- `m` must grow like `log N` and the published figures use `m = 4, 6, 8, 10, 12`.

Also relevant and already in-repo: `notes/research_to_exp_dev_B5_decay_model_palimpsest_spec_2026-06-04.md`
(Fusi-Abbott 2007 bounded-synapse lifetimes `~m^2` hard bounds / `~m` soft bounds).

---

## 1. FUSI, DREW & ABBOTT 2005 -- THE CASCADE MODEL

### 1.1 State space -- PINNED

**PINNED.** Two synaptic **efficacies** (weak `-` / strong `+`), and for *each* efficacy a **cascade
of `n` metaplastic states**. Total `2n` states.

```
strong: g1+, g2+, ..., gn+
weak  : g1-, g2-, ..., gn-
```

A state is the pair `(s, k)` with `s in {+1,-1}` the *efficacy actually read out by the neuron* and
`k in {1..n}` the *depth*, which is invisible to the readout. `k = 1` is the top: most plastic.
`k = n` is the bottom: most rigid. **Depth changes nothing about the synapse's output** -- it changes
only the probability of future changes. That is the definition of metaplasticity here.

Figure examples in the literature use `n = 5` (Fusi 2005 Fig. 1), `n = 10` and `n = 15`
(Ben Dayan Rubin & Fusi 2007), `n = 15` (Zenke review simulation).

Source: Ben Dayan Rubin & Fusi 2007 Fig. 1 legend + section "Synaptic models"; slide deck
"Cascade Models (II)": *"Each synaptic strength is associated to a cascade of n states: Strong (+)
strength: {g1+, g2+, ... gn+}; Weak (-) strength: {g1-, g2-, ... gn-}. Plastic transitions
(weak <-> strong) with prob. q1, ..., qn. Metaplastic transitions (labile <-> resistant) with prob.
p1+-, ..., pn+-."*

### 1.2 Transition rules -- MATCHED vs MISMATCHED -- PINNED in form, one power UNPINNED

Event model (**PINNED**, slide deck "General approach"): candidate plasticity events arrive at rate
`r ~ 0.2 Hz`; each becomes an actual modification with probability `q`; the modification is
potentiation with probability `f+` and depression with `f- = 1 - f+`. Balanced case `f+ = f- = 1/2`.

For a synapse in state `(s, k)` receiving an event of sign `e`:

**MATCHED (`e == s`, i.e. the event agrees with the current efficacy) -> METAPLASTIC step DOWN:**
```
(s, k) -> (s, k+1)   with probability p_k     [efficacy UNCHANGED]
(s, n) -> (s, n)                              [absorbing at the bottom]
```

**MISMATCHED (`e != s`) -> PLASTIC transition, and it is a RESET, not a step:**
```
(s, k) -> (-s, 1)    with probability q_k     [efficacy FLIPS, depth resets to the TOP]
```

This reset-to-the-top is the single most easily got-wrong detail. Ben Dayan Rubin & Fusi 2007,
verbatim: *"If the conditions for depression are satisfied, then a transition to the top of the
cascade is induced, and the synaptic efficacy changes."* A depressing event does **not** walk a
potentiated synapse up its own cascade one rung -- it throws it to `(-s, 1)`, the most labile state
of the opposite efficacy.

**Is the `2^-d` factor on the plastic transition, the metaplastic transition, or both?**
**PINNED: BOTH.** Ben Dayan Rubin & Fusi 2007, verbatim: *"The probability for **both** transitions
decreases exponentially as the synapse moves down along the cascade of states."* The same paper's
Fig. 1 legend: *"[the learning rates] decrease as 1/2^k for the cascade model, where k is the
metaplastic level (number of states from the top of the cascade)."* Fusi 2021 review: *"the values
of the qs decrease exponentially (q_k = Q^k where Q is a constant)."*

So the base is `x = 1/2` and both families fall geometrically in depth. The ORGAN_MAP gloss
`p(write | d) = 2^-d` is therefore **directionally right but under-specified**: it names one
probability where there are two, and it does not say the plastic transition is a reset.

**The remaining one-power ambiguity, and how to resolve it -- DERIVED.** The two sentences quoted
above disagree by one power of `x` about which family carries `x^k` and which carries `x^{k-1}`
(OCR of superscripts in the 2007 PDF is not fully reliable, and I could not open the 2005 original).
The offset is fixable from a stated property of the model: Ben Dayan Rubin & Fusi 2007 state
*"at the equilibrium distribution all metaplastic states are equally occupied (see Fusi et al. 2005
for more details)."* Uniform steady-state occupancy `P_k = 1/n` requires the down-flux into level
`k+1` to equal the reset-flux out of it:

```
P_k * p_k  =  P_{k+1} * q_{k+1}      =>      p_k = q_{k+1}
```

which is satisfied exactly by

```
q_k = q * x^{k-1}        (PLASTIC, efficacy-flipping, reset to depth 1)
p_k = q * x^{k}          (METAPLASTIC, depth k -> k+1, same efficacy)
x   = 1/2
```

**Use this pair.** It is self-consistent with the uniform-occupancy fact, which is in turn the fact
that produces the `1/n` initial-SNR cost in section 1.3 -- so getting it wrong breaks a quantity we
want to measure. Marked DERIVED, not PINNED: the exact prefactors and the `k = n` boundary
convention need the 2005 paper, which I could not open. **This is the one number in this document a
build should verify against the primary source before it is load-bearing.**

### 1.3 Initial SNR as a function of N and n -- PINNED, with a closed form

**PINNED.** Signal `S(t)` = overlap of the tracked memory's intended modification pattern with the
current weights; noise = its standard deviation across the ensemble of subsequently stored random
uncorrelated memories.

Closed form, Ben Dayan Rubin & Fusi 2007 **equation (2)** (verbatim, `C` = synapses per neuron,
`f` = coding sparseness, `n` = cascade depth, `r` = storage rate, `t` = time since storage):

```
                14 * sqrt(C) * f          1                    (  - r t f^2  )
S/N_cascade  =  ------------------  *  ---------  *  exp       ( ----------- )
                       5 n             1 + r t f^2             (   2^(n-2)   )
```

Reported goodness of fit 0.97 over `S/N > 1e-6`, `n in [5,15]`, `f in [1e-4, 0.5]`; the numerical
coefficients `14/5` are fitted, the initial value was determined analytically.

Reading the three factors:
- **Initial SNR** (`t = 0`): `SNR(0) = 14 f sqrt(C) / (5 n) ~ 2.8 f sqrt(C) / n`. Scales as
  **`sqrt(N)`** in the number of synapses, **linearly in `f`**, and **inversely in `n`**.
  Cross-check from the same paper: the minimal sparseness allowing retrieval is
  `f_0 = 5n / (14 sqrt(C))`, which is exactly `SNR(0) = 1`. Internally consistent.
- **Power-law factor** `1/(1 + r t f^2)` -> `~ t^-1` at large `t`.
- **Exponential cutoff** at `r t f^2 ~ 2^(n-2)`: the power-law regime is valid while
  `r t < 2^(n-2)/f^2`, i.e. **the power-law window grows EXPONENTIALLY in `n`**, and beyond it the
  decay is exponential and fast.

For the dense case `f = 1/2` this reduces to `SNR(0) ~ 1.4 sqrt(C)/n` -- i.e. the plain bistable
synapse's `sqrt(N)` initial trace, **divided by `n`**.

### 1.4 The forgetting exponent alpha -- PINNED as a RANGE, and the range is not a vagueness

`SNR(t) ~ t^-alpha`. Three different published fits, and they differ because they fit different
time ranges of the same curve:

| alpha | source | note |
|---|---|---|
| **3/4** | **Fusi, Drew & Abbott 2005** | the original paper's own estimate |
| **1** | Ben Dayan Rubin & Fusi 2007 eq (2) | mean-field fit "determined to describe the S/N decay in a different range" |
| **1** | Fusi 2021 review S3.3 | *"The cascade model is characterized by a memory signal that decays as 1/t."* |
| **1/2** | Benna & Fusi 2016 | a DIFFERENT model (section 2), not the cascade |

The 2007 paper is explicit about the discrepancy, verbatim: *"The power of the first term (-1),
estimated by fitting the formula to the mean field results, is slightly different from the one
estimated in Fusi et al. (2005) (-3/4) as it has been determined to describe the S/N decay in a
different range."*

**For a build: use alpha = 1 for the cascade** (two independent Fusi-lab statements, and it is the
exponent of the closed form in 1.3). **alpha = 3/4 is the primary paper's number and should be
quoted whenever "Fusi 2005" is cited.** ORGAN_MAP's "alpha ~ 0.5-1.0" is a correct interval but its
`0.5` endpoint belongs to Benna-Fusi 2016, not to the cascade.

The slide deck also reports the corresponding lifetime under alpha = 3/4: `t_max ~ N_syn^(2/3)`
(from `sqrt(N) t^-3/4 = 1`). Under alpha = 1 it is `t_max ~ sqrt(N)`. Both are internally consistent
with `SNR(0) ~ sqrt(N)`; they differ only through alpha.

### 1.5 The binary synapse it is compared against -- PINNED

**PINNED** (slide deck "Binary model"; Ben Dayan Rubin & Fusi 2007; Amit & Fusi 1994):

```
Signal(t)  ~  q * N_syn * exp(-q r t)          Noise ~ sqrt(N_syn)
SNR(t)     ~  q * sqrt(N_syn) * exp(-q r t)    [dense]
SNR(0)     ~  f * q * sqrt(C)                  [sparse]
tau        =  1 / (q r)                        [dense]   =  1 / (q r f^2)  [sparse]
t_max      ~  ln(q N_syn) / (q r)
```

**The trade-off, stated exactly.** The binary synapse's lifetime can be made arbitrarily long by
shrinking `q` -- *"but this reduces dramatically S0/N0"*, by the same factor `q`. The decay is
**exponential with time constant `tau = 1/(q r)`**, so the lifetime grows only **logarithmically**
in `N_syn`. Long `t_max` and a strong initial trace are **not simultaneously achievable** in a
binary synapse. That is the entire problem the cascade exists to solve.

### 1.6 Capacity scaling -- PINNED, and ORGAN_MAP MISATTRIBUTES IT

| model | signal decay | initial SNR | memory lifetime / capacity |
|---|---|---|---|
| binary, fast (`q = O(1)`) | `exp(-q r t)` | `O(1)` | **`log N`** |
| binary, slow (`q = O(1/sqrt N)`) | `exp(-q r t)` | at threshold | `sqrt N` (but ~no info per memory) |
| multistate, `n` states | `exp(...)` | `~sqrt(N)/n` | `n^2` x binary |
| **cascade (Fusi 2005)** | **`1/t`** | **`sqrt(N)/n`** | **`sqrt(N)`** |
| **bidirectional cascade (Benna-Fusi 2016)** | **`1/sqrt(t)`** | **`sqrt(N)/sqrt(m)`** | **`N`** (`N/log N` optimised) |

Sources: Fusi 2021 review Table 1 and S3.3-3.4, verbatim -- *"The cascade model is characterized by
a memory signal that decays as 1/t. **Both the initial SNR and the maximum memory lifetime scale as
sqrt(N)**, where N is the number of synapses."* And Benna & Fusi 2016 -- *"The memory lifetime in
previous models of complex synapses with bounded weights scales at most as sqrt(N). A memory
lifetime that scales (almost) linearly with the number of synapses constitutes a major improvement."*

**=> ORGAN_MAP D8 (line 574) is wrong on this row.** It writes *"capacity scaling ~N instead of
~sqrt(N) (Fusi, Drew & Abbott 2005; Roxin & Fusi 2012)"*. The `~N` is **Benna & Fusi 2016's**
result; the thing it improves on (`sqrt(N)`) **is the Fusi 2005 cascade**. The cascade's own
improvement is `log N -> sqrt(N)`, over the fast binary synapse. Two further citation notes: Roxin &
Fusi is **2013** (*PLoS Comput Biol* 9:e1003146), not 2012; and its multistage model shares the
cascade's scaling, it does not beat it. (I am reporting this; per the brief I have NOT edited
ORGAN_MAP.)

Also worth carrying: Fusi 2021 notes the cascade's *scaling* is no better than a heterogeneous
population of simple synapses with different `q`, though the cascade's *numerical* SNR is
substantially better. Scaling class is not the whole story.

### 1.7 The hard upper bound that frames all of this -- PINNED (bonus)

Lahiri & Ganguli 2013 (NIPS, "A memory frontier for complex synapses") prove a **model-independent
envelope**: for `N` synapses with `M` internal states, no synaptic model's memory curve can exceed
an envelope whose late-time form is

```
SNR_envelope(t)  =  O( sqrt(N M) / (r t) )        memory lifetime <= sqrt(N) (M-1) / (e r)
```

Both the envelope and the lifetime bound are **linear in `M`** and **`sqrt(N)` in `N`**. Note this
does not contradict Benna-Fusi's `1/sqrt(t)`: Benna-Fusi's discretised `M` grows *exponentially*
with `m`, which is exactly how it buys a shallower exponent. Useful sanity rail: **if a proposed
synapse claims a better-than-`sqrt(N M)` late-time SNR, it is wrong.**

---

## 2. BENNA & FUSI 2016 -- THE BIDIRECTIONAL CASCADE

Everything in this section is **PINNED** from the full text of the paper.

### 2.1 The variable chain

`m` dynamical variables `u_1, ..., u_m`.

- **`u_1` IS the synaptic weight.** Verbatim: *"The first variable `u_1` represents the strength of
  the synaptic weight."* It is **not** bistable; it takes multiple graded values.
- **`u_2 ... u_m` are hidden biochemical processes** not coupled to neural activity, arranged in a
  **linear chain**, each interacting only with its two nearest neighbours. Verbatim: *"The dynamical
  variables `u_k` represent different biochemical processes that are responsible for memory
  consolidation."* One interpretation offered by the authors: *"deviations from equilibrium of
  chemical concentrations."*
- **The interactions are BIDIRECTIONAL** -- the slow variables push back on the fast one. This is
  the whole difference from Fusi 2005 and is where metaplasticity comes from for free.
- `u_m` has a **leak**, implemented as `u_{m+1} = 0`.

Physical analogy (the authors', not a gloss): communicating vessels. `C_k` = beaker cross-sectional
area, `g_{k,k+1}` = connecting-tube cross-section, `u_k` = deviation of liquid level from
equilibrium. `u_1`'s level is the synaptic strength; potentiation pours liquid in, depression
removes it.

### 2.2 The coupled differential equations -- Figure 1a, verbatim

```
      du_k
C_k * ----  =  g_{k-1,k} (u_{k-1} - u_k)  +  g_{k,k+1} (u_{k+1} - u_k)
       dt
```

with `u_{m+1} = 0` (the leak) and, for `k = 1`, the `g_{0,1}` term replaced by the input `I(t)`
(the plasticity events).

### 2.3 The geometric progression -- PINNED with exact constants

From Figure 2 (the three-step construction: homogeneous chain -> merge beakers -> shrink tubes):

```
C_k        =  2^(k-1)          (beaker areas GROW by 2 per level)
g_{k,k+1}  =  2^(-k-2)         (tube cross-sections SHRINK by 2 per level)
```

Verbatim from the Fig. 2 legend: *"leading to successively larger ones (`C_k = 2^(k-1)`)"* and
*"Their sizes are progressively reduced (by powers of two) to slow the decay
(`g_{k,k+1} = 2^(-k-2)`)."* The homogeneous starting point (Fig. 2a) is `C_k = 1`,
`g_{k,k+1} = 1/8`.

**=> the TIMESCALES therefore go up by a factor of 4, not 2, per level** (this is the single most
build-relevant constant in the section):

```
tau_k  =  C_k / g_{k,k+1}  =  2^(k-1) / 2^(-k-2)  =  2^(2k+1)
tau_1 = 8, tau_2 = 32, tau_3 = 128, ... ratio 4x per level
T     =  tau_m  =  C_m / g_{m,m+1}  =  2^(2m+1)      <- the longest timescale
```

`T = 2^(2m+1)` is stated verbatim in the paper.

The two-step construction matters conceptually and is worth reproducing in a build: merging beakers
alone (Fig. 2b) gives the right *number* of variables but the *wrong* decay (`~1/t`, too fast);
shrinking the tubes (Fig. 2c) restores `~1/sqrt(t)` **without adding variables**. A build that gets
`C_k` right and `g_{k,k+1}` wrong will silently produce the wrong exponent.

### 2.4 SNR(t) -- equation (2), and ORGAN_MAP's version is WRONG IN THE EXPONENT OF N

Verbatim, Benna & Fusi 2016 **equation (2)**:

```
                sqrt(N)  *  exp(-t/T)
SNR(t)  ~  ------------------------------ ,        T = C_m / g_{m,m+1} = 2^(2m+1)
              sqrt(t) * sqrt(log T)
```

Supporting statements from the same paper, all verbatim:
- *"the SNR decays approximately as `1/sqrt(t)` over a time interval that increases exponentially
  with the complexity of the synapse, before the decay accelerates and becomes exponential"*
- *"`SNR(0)` grows as `sqrt(N)`, as in the best previous synaptic models"* (Fig. 4f)
- *"As `m` increases, the initial SNR slowly degrades (as `~1/sqrt(m)`)"* (Fig. 4d)

Note `log T = (2m+1) ln 2`, so `sqrt(log T) ~ sqrt(m)` -- the formula's `1/sqrt(log T)` and the
figure's `1/sqrt(m)` are the same statement. `SNR(0)` means `t = 1` (one memory per unit time), not
`t = 0`; the formula diverges at `t = 0` and is not meant to be evaluated there.

**=> ORGAN_MAP's `SNR(t) ~ N/(sqrt(K) t^0.5)` is wrong in the exponent of N: it is `sqrt(N)`, not
`N`.** The `sqrt(K)` part is right if `K = m` (the number of chain variables), since
`sqrt(log T) ~ sqrt(m)`. The error matters for exactly the reason SNRs are computed: it changes a
predicted retention level by a factor of `sqrt(N)`, which at `N = 1024` is 32x.

**=> ORGAN_MAP's "vs `N/t` for a single-state synapse" is also wrong.** A single-state *bounded* or
binary synapse decays **exponentially**, not as `N/t` (section 1.5). The `sqrt(N)/t` form is (a) the
Fusi-2005 cascade and (b) the Lahiri-Ganguli envelope. There is one single-state model with a
power law -- the **unbounded** perfect integrator, `SNR = sqrt(N/t)` -- and see section 4.4, because
that one is directly relevant to what our substrate already does.

### 2.5 Regime of validity and the crossover -- PINNED

```
t << T = 2^(2m+1)   ->  power law, SNR ~ sqrt(N/t) / sqrt(log T)
t ~> T              ->  exponential, SNR ~ exp(-t/T), the curve visibly bends down on log-log
```

Memory lifetime (SNR crossing threshold 1), verbatim reasoning from the paper:
- If `T << N`: the threshold is crossed **in the exponential regime**, so `lifetime ~ T`, i.e.
  exponential in `m`. Increasing `N` then buys only a **logarithmic** lifetime increase.
- If `T >> N`: the threshold is crossed **in the power-law regime**, where the exponential factor is
  ~constant, so `lifetime ~ N` (from `sqrt(N)/sqrt(t) = 1`).
- Tuning `T` to track `N`: `lifetime ~ N / log N` (Supplementary Note 1).

**Design consequence, PINNED: pick `m` so that `T = 2^(2m+1)` is of order the number of items you
intend to ingest.** Bigger `m` past that is wasted and costs `1/sqrt(m)` of initial SNR. Concretely:
`m = 6 -> T = 8192`; `m = 8 -> T = 131072`; `m = 10 -> T = 2.1e6`; `m = 12 -> T = 3.4e7`.

### 2.6 The discrete-time form actually usable in code -- PINNED, equations (10) and (11)

This is the version the paper itself simulates. **One time step = one stored memory.** Base `n = 2`,
free parameter `alpha = 1/4` (the paper writes `alpha`, uses `alpha = 1/4` "below and in all
numerical experiments"; it must be small enough that the transition matrix has no negative
eigenvalues, else the chain oscillates).

For `i = 2 ... m` (equation 10):
```
u_i(t+1) = u_i(t) + n^(-2i+2) * alpha * (u_{i-1}(t) - u_i(t))
                  - n^(-2i+1) * alpha * (u_i(t)     - u_{i+1}(t))
```
For `i = 1` (equation 11), with the binary input `I(t)` of unit magnitude:
```
u_1(t+1) = u_1(t) + I(t) - n^(-1) * alpha * (u_1(t) - u_2(t))
```
For `i = m`: set `u_{m+1} = 0` for all `t` (this is the leak).

With `n = 2, alpha = 1/4` the coefficients collapse to pure powers of two:
```
forward  coefficient (from i-1 into i):  2^(-2i)
backward coefficient (from i into i+1):  2^(-2i-1)
i = 1 coupling to u_2:                   1/8
```
Consistency check against section 2.3: `g_{k-1,k}/C_k = 2^(-k-1)/2^(k-1) = 2^(-2k)` and
`g_{k,k+1}/C_k = 2^(-k-2)/2^(k-1) = 2^(-2k-1)`. Both match exactly. The two descriptions are the
same model.

`I(t)` is `+1` for potentiation, `-1` for depression, `0` if this synapse is not touched by the
current memory. Potentiation and depression must be **balanced in expectation** -- the model is
explicitly *"significantly less robust to biases in the input statistics"*; an imbalance shifts the
whole SNR curve down.

**Quantisation (optional, and the paper says so).** Each `u_i` restricted to a finite set of
integer-spaced levels symmetric about zero. Update: compute the continuous right-hand side, then
**stochastically round** to one of the two neighbouring levels with odds equal to the inverse ratio
of the distances (so `E[quantised] = continuous`); clip at the extremes with probability 1. Number
of levels needed scales as `log T`; published runs use 20-50 levels, and the number can **decrease
linearly with `k`** -- the paper shows `u_m` working with only **2 levels**, because the slow
variables' equilibrium distributions are narrower. Verbatim: *"the quantization of the variables is
neither necessary for the model to work nor required for a plausible biophysical implementation. In
fact the SNR will be somewhat higher without the additional noise."*

**=> for a first build: do NOT quantise. Use float `u_k`.** It is simpler and strictly better in
SNR; quantisation exists in the paper only to prove no implausible precision is hidden anywhere.

### 2.7 Two behaviours that fall out for free -- PINNED, and one of them is a design hazard

- **Metaplasticity**: verbatim, *"a natural consequence of the existence of hidden variables."* A
  synapse that has undergone a long series of LTP becomes resistant to subsequent LTD, with
  identical *efficacy* but different *hidden state* (Fig. 7b).
- **Spacing effect with an INVERTED U** (Fig. 7c): massed repetitions are less effective (a variable
  hits its bound / liquid spills); very long lags are less effective (liquid settles back to
  equilibrium between repetitions, so nothing accumulates); there is an intermediate optimum.

**HAZARD for the ORGAN_MAP STEP-5 "ONE VARIABLE" design.** ORGAN_MAP proposes running D8 (synapse)
and D4 (schedule) as separate arms because "the cascade should change the *shape* of forgetting, the
schedule should change the *level*." That separation is **only partly safe**: the spacing effect
above is produced by the SYNAPSE alone, with no schedule machinery. So a cascade-only arm run on a
non-uniform ingest schedule will already show schedule-like effects, and a schedule arm run on a
single-state synapse cannot show the inverted U at all. To keep one variable, **the cascade-only arm
must be run at a FIXED, uniform inter-repetition spacing**, and the schedule arm must be run on both
synapse types (2x2), or the two effects will be confounded in the direction that flatters the
schedule.

---

## 3. REPLAY / CLS SCHEDULE

This is where the pinning quality drops sharply. Sections 1 and 2 are equations; most of section 3
is phenomenology, and the parts a build most needs are the parts the literature has NOT fixed.

### 3.1 How many times is a given experience replayed? -- **UNPINNED**

ORGAN_MAP D4 states *"each waking experience replayed only 1-3 times (Liu 2024 PMC11068097; Neuron
2025)."* **I could not verify this.** I fetched PMC11068097 and it *"does not provide specific
quantitative data on how many times waking experiences are replayed during sleep... The study
emphasizes the relationship between awake and sleep replay content rather than sleep replay
quantification."* The only quantitative statement in it on this axis is qualitative ordering:
*"During postexperience sleep, SPW-Rs continued to replay those trial blocks that were reactivated
most frequently during waking SPW-Rs."*

Targeted searching did not find a source that pins a per-experience replay count. What IS findable
and adjacent:
- replay/reactivation rates are highest in the **first 10-30 min** of post-encoding sleep;
- cell assemblies reactivate for **up to ~10 h** with a half-maximum around **~6 h** after a novel
  experience;
- cortical/hippocampal/thalamic/putamen ensemble patterns recur for **up to 48 h**;
- the *rate* of replay events for a track scales with the number of trajectories actually run.

**Verdict: the "1-3 times" figure should be treated as UNSOURCED until someone produces the primary
citation.** For a build, replay count is a **free parameter to sweep**, not a pinned constant --
which is fine, and is more honest than hard-coding 1-3 from a citation that does not say it.

**PINNED and adjacent, and this one is real:** only a **subset of LARGE-amplitude SWRs** carries
memory reactivation, their rate selectively increases in post-learning sleep and correlates with
memory performance, and closed-loop optogenetic boosting of them causally improves retrieval
(Robinson, Todorova, Fernandez-Ruiz et al., *Neuron*, 2025/2026,
doi 10.1016/j.neuron.2025.10.003; bioRxiv 2025.06.27.662061). So replay is **selective at the event
level**, which is a stronger and better-sourced statement than any count.

Also **NOT VERIFIED in this drill**: ORGAN_MAP's *"~5-10 SWRs per ~1 s up-state (Helfrich 2021 PNAS
118 e2012075118)"*. Searching returned Helfrich's 2018/2019 work (Nat Commun / Neuron) on
SO-spindle-ripple coupling, not a 2021 PNAS with that number. Flagging, not asserting a correction.

### 3.2 Interval structure: expanding? doubling? -- PINNED, but not as ORGAN_MAP states it

ORGAN_MAP: *"Optimal rehearsal = expanding intervals, approximately doubling (Landauer & Bjork
1978)."* I opened Landauer & Bjork 1978. The actual schedules, verbatim from the Method:

```
Uniform, short   : (0,0,0) and (1,1,1)
Uniform, moderate: (4,4,4) and (5,5,5)
Uniform, long    : 9 < (x,y,z) < 11, mean 9.3-10.3
Expanding        : (0,3,10) and (1,4,10)
Contracting      : (10,3,0) and (10,4,1)
```
(numbers = intervening items between successive tests; the uniform-moderate mean matches the
expanding and contracting means, which is the design's control).

So the expanding schedules are **1 -> 4 -> 10**, i.e. ratios of roughly **4x then 2.5x**, not
"approximately doubling". Result: *"The expanding pattern produced almost twice as many correct"*
responses as uniform-short, and beat uniform-moderate at `z = 2.6, p < .01`. Crucially the paper's
own scope condition: expanding wins **for TEST-type practice** (retrieval attempts), while
*"uniform spacing was slightly better if the information was repeated"* (study-type practice).

**Honesty flag that ORGAN_MAP does not carry:** the expanding-retrieval advantage is **contested in
the modern literature**. Karpicke & Roediger 2007 (*"Is expanding retrieval a superior form of
spaced retrieval?"*) and Storm, Bjork & Storm 2010 find equal-interval spacing matches or beats
expanding at long retention intervals; expanding tends to win only at short delays. So: **expanding
intervals are PINNED as a real 1978 effect for test-type practice at short delay, and UNPINNED as a
general optimum.** Do not build "expanding, doubling" in as a fixed law.

### 3.3 Forward vs reverse, and which scales with reward -- PINNED, but the citation is wrong

**PINNED:** *"the number of reverse-ordered, but not forwards-ordered, replays was significantly
correlated to reward level."*

**Correct citation: Ambrose, Pfeiffer & Foster 2016, *Neuron* 91:1124-1136, "Reverse Replay of
Hippocampal Place Cells Is Uniquely Modulated by Changing Reward."** ORGAN_MAP attributes the
reward-scaling claim to **Foster & Wilson 2006 *Nature* 440:680** -- that paper *discovered* reverse
replay (reverse-order reactivation at the end of a run), it did **not** show the reward modulation.
Both citations are needed; only one supports the claim as ORGAN_MAP writes it.

Functional reading worth carrying into a build: reverse replay runs *backwards from the reward*,
which is the credit-assignment direction (it is the sweep a TD/eligibility update wants); forward
replay is more plausibly prospective/planning. That is consistent with only the reverse one being
reward-sensitive.

### 3.4 What is replayed -- veridical episodes or generative samples? -- **PARTLY PINNED, contested**

The classical CLS assumption (McClelland, McNaughton & O'Reilly 1995) is **veridical**: the
hippocampus is *"treated as a source of training data"* replaying stored patterns to cortex.

The modern position is **generative, and the evidence is direct**: internally generated hippocampal
sequences depict paths never taken -- optimised routes never exploited, shortcuts, Brownian-diffusion-like
random trajectories, and future goal locations. Reviews frame this as
*"the offline resampling of fictive sequences from the generative model"* rather than *"verbatim
replay of memories from a buffer"* (Stoianov, Maisto & Pezzulo 2022 *Prog Neurobiol*, "The
hippocampal formation as a hierarchical generative model supporting generative replay and continual
learning"; Barron et al. 2023 *Cell*, "Generative replay underlies compositional inference in the
hippocampal-prefrontal circuit").

**Verdict: both are real; the mixture is UNPINNED.** No source I found quantifies the fraction of
replay events that are veridical vs constructed. For a build this is a genuine design fork, not a
detail: veridical replay = a stored-episode buffer; generative replay = sampling from the current
model. They have opposite storage costs and opposite failure modes (buffer = no generalisation
pressure; generative = the model can reinforce its own errors).

### 3.5 Interleaving ratio (McClelland, McNaughton & O'Reilly 1995) -- **UNPINNED as a number**

I read the paper. It PINS the **principle** and does **not** pin a ratio.

What is pinned, verbatim:
- *"Incorporation of new material without interference can occur if new material is incorporated
  gradually, interleaved with ongoing exposure to examples of the domain embodying the content
  already learned."* (numbered conclusion 3)
- The penguin demonstration: focused learning (new facts repeatedly, alone) -> fast acquisition,
  large interference with existing concepts. Interleaved learning -> *"the new information about
  penguins is simply added to the training set so that it is interleaved with continued exposure to
  the full database"* -> slower acquisition, *"very little interference"*, and eventually full
  acquisition.
- Where the old material comes from: *"events reactivated in the hippocampus during slow wave sleep
  prime related neocortical patterns, so that these in turn become available for activation during
  REM sleep. This could permit both new and old information to be played back in closely interleaved
  fashion."* Also environmental re-exposure and reminiscence -- explicitly *"several (nonexclusive)
  possibilities."*

**The operative ratio is therefore just "one presentation of the new item per sweep of the existing
corpus"** -- the new item becomes an ordinary member of the training set. That is an implicit ratio
of `1 : |corpus|` per epoch, not a tuned hyperparameter, and the paper says so implicitly by
treating background exposure rate as *"independent of the status of the hippocampal system"* "for
simplicity". **Any specific new:old ratio in a build is ours to choose and to sweep; it is NOT
prescribed by CLS.** Report it as a swept parameter, never as "the brain's ratio".

### 3.6 Davis & Gaskell 2009, and what sleep does to a newly learned word -- PINNED

**The two-stage claim (Davis & Gaskell 2009, *Phil Trans R Soc B* 364:3773):** word learning has
*"two stages of lexical acquisition: rapid initial familiarization followed by slow lexical
consolidation"*, mapped onto CLS (hippocampal fast episodic acquisition -> neocortical lexical
integration), with overnight sleep-associated consolidation as part of the learning process.

**The measurable signature is LEXICAL COMPETITION, and its timing is the pin** (Dumay & Gaskell 2007
*Psych Sci* 18:35, the study Davis & Gaskell build on):
- A novel word (`cathedruke`) is *learned* immediately -- recognition and recall are available at
  once.
- It does **not** compete with its phonological neighbour (`cathedral`) immediately.
- Words learned at **8 p.m. show competition after a 12-h interval containing sleep**, and still at
  24 h.
- Words learned at **8 a.m. show NO competition immediately and NONE after 12 h of wakefulness**,
  but **do** show it at 24 h -- i.e. after sleep has intervened.

**This is the cleanest available dissociation of ACQUISITION from INTEGRATION**, and it is the exact
shape our own foundation problem has: storage works, meaning/integration does not. **The
sleep-dependence is the discriminator: time awake does not do it, sleep does.** For a build, the
directly transferable experimental form is: measure a *competition/interference* effect on
pre-existing neighbours, not a recall score on the new item -- recall is available before
consolidation and so cannot detect it.

### 3.7 The 2021 meta-analysis, g = 0.50 -- PINNED, with the full breakdown

**Schimke, E. A. E., Angwin, A. J., Cheng, B. B. Y., & Copland, D. A. (2021). "The effect of sleep
on novel word learning in healthy adults: A systematic review and meta-analysis." *Psychonomic
Bulletin & Review* 28:1811-1838.** doi 10.3758/s13423-021-01980-3.

```
25 unique studies, 42 outcome measures, k = 29 between-group comparisons, n = 1,396 participants
omnibus:                       g = 0.50   (sleep > wake for novel word learning)
recall:                        g = 0.57
recognition memory:            g = 0.52
lexical integration:           "a small effect"  (numeric value not captured in this drill)
```

**Two things this changes about how ORGAN_MAP quotes it.** (a) The comparison is **sleep vs
wakefulness**, i.e. an *interval-content* contrast, not "consolidation vs none". (b) The **largest**
effects are on plain recall and recognition; the **lexical-integration** measures -- the ones that
actually index the CLS claim of 3.6 -- show the **smallest** effect. So `g = 0.50` is *not* an
effect size for "integration into the lexicon"; quoting it as such over-claims. The honest headline
is: sleep reliably helps novel-word memory at a moderate effect size, and helps *integration*
measurably less.

### 3.8 The selection function -- which traces get replayed? -- **UNPINNED (confirmed)**

ORGAN_MAP's *"THE SELECTION FUNCTION -- which traces get replayed -- is UNPINNED"* is **correct and
this drill confirms it.** There is no consensus equation. What exists:

- **Reward**: pinned as a modulator of *reverse* replay only (3.3).
- **Event-level selectivity**: pinned -- large SWRs specifically (3.1).
- **Experience frequency**: replay rate scales with how much a trajectory was actually run; waking
  reactivation frequency predicts sleep replay content (PMC11068097).
- **Novelty**: reactivation is elevated after novel experience (multi-hour reverberation results).
- **A NORMATIVE candidate equation, and this is the closest thing to a pinned selection rule:**
  **Mattar & Daw 2018, *Nat Neurosci* 21:1609, "Prioritized memory access explains planning and
  hippocampal replay."** Memories are accessed in order of **expected value of a backup**, factored
  as
  ```
  priority(s,a)  =  GAIN(s,a)  x  NEED(s)
  ```
  where GAIN = the improvement in future reward from correcting the policy at `(s,a)` (large when the
  backup would change the action -- i.e. a surprise / prediction-error-like term) and NEED = the
  discounted expected future occupancy of `s` (the successor representation -- note this is
  **ORGAN_MAP's own D7**, `M = (I - gamma P)^-1`). The paper reproduces forward/reverse asymmetries,
  reward modulation and remote replay from this one rule.

**Verdict: the selection function is UNPINNED as biology and PINNED as a normative theory.** That is
a real distinction and should be preserved: Mattar-Daw is a *model that explains* replay statistics,
not a measured mechanism. Also note the dependency it implies -- a principled selection rule wants a
successor representation, and D7 is currently MISSING in our substrate. If STEP 5 wants a
non-arbitrary selection function it will either borrow GAIN x NEED (and therefore need D7) or sweep
a heuristic (recency / surprise / frequency) and say so.

---

## 4. THE PROBLEM SOLVED, AND THE SHAPE AN EXPERIMENT MUST DETECT

### 4.1 The failure mode without the machinery -- PINNED

**McCloskey & Cohen 1989** (*Psychol Learn Motiv* 24:109), the sequential-learning experiment:
train a standard backprop network to criterion on **17 "ones" addition facts** (1+1..9+1, 1+2..1+9),
then train to criterion on **17 "twos" facts**; performance on the "ones" set collapses. **Honesty
note: I could NOT verify a specific "dropped to 0%" number** -- and a secondary source explicitly
records that *"a second simulation by these authors indicated that learning the twos does not
completely destroy all memory of the ones."* So: the collapse is real and severe; the exact
percentage is **UNPINNED** in this drill and should not be quoted as a number.

**French 1999** (*Trends Cogn Sci* 3:128-135), the definition and the diagnostic contrast, verbatim:
learning a new set of patterns *"suddenly and completely erased a network's knowledge of what it had
already learned"*; and the contrast that makes it a *fidelity* failure rather than a nuisance --
*"all natural cognitive systems gradually forget previously learned information... natural cognitive
systems do not, in general, forget 'catastrophically'."*

**McClelland, McNaughton & O'Reilly 1995's own demonstration** (section 3.5): focused learning of
"penguins can swim / cannot fly" produces fast acquisition **and** a large rise in absolute error on
the 15 pre-existing `can`-relation items; interleaved learning produces slow acquisition and *"never
more than a slight hint of interference"*. Their measure is **absolute error summed over output
units**, and the interference is **not uniform** -- verbatim, *"the interference falls predominantly
on those output units in which the correct answer for the pre-existing memory differs from the
correct answer for the penguin."* **That non-uniformity is itself a testable signature** and a
better discriminator than a mean: catastrophic interference should concentrate on the
*contradicting* dimensions, whereas generic capacity loss should not.

### 4.2 The predicted SHAPE difference -- this is the deliverable

Learn set A, then stream `t` new items (set B, then C, ...), retest A. Plot **retention of A vs `t`
on LOG-LOG axes**. The pinned models predict *qualitatively different curve families*, not "better":

| system | SNR(t) | shape on LOG-LOG | shape on SEMI-LOG |
|---|---|---|---|
| naive / sign-quantised single-state | `SNR_0 e^(-t/tau)`, `tau = 1/(q r f^2)` | **convex, bends down, no straight segment** | **STRAIGHT LINE** |
| cascade, depth `n` | `(SNR_0/n) * t^-alpha`, `alpha ~ 3/4..1` | **STRAIGHT LINE, slope -alpha**, knee at `t ~ 2^(n-2)/f^2` | curved |
| Benna-Fusi, `m` vars | `(SNR_0/sqrt(m)) * t^(-1/2)`, knee at `T=2^(2m+1)` | **STRAIGHT LINE, slope -1/2**, knee at `T` | curved |

**Four concrete, falsifiable predictions, in order of how hard they are to fake:**

1. **THE SIGN FLIPS.** The cascade arm must start **BELOW** the naive arm by a factor of **exactly
   `1/n`** (`1/sqrt(m)` for Benna-Fusi). *An arm that is better everywhere has not implemented a
   cascade* -- it has implemented something else, or the naive baseline is broken. **This is the
   single best fraud detector in the whole design, and it is the reason to run it: the theory
   predicts our treatment arm is WORSE at t=0 by a computable factor.**
2. **THERE IS A CROSSOVER at a computable `t*`**, solving `e^(-t/tau) = n^-1 t^-alpha`
   (to leading order `t* ~ tau (ln n + alpha ln tau)`). Predict `t*` from `n` and `tau` **before**
   running; scoring it is a genuinely can-fail test that a level-shift cannot pass.
3. **THE LOG-LOG SLOPE IS THE MEASURAND, and it is a fitted number with a predicted value:**
   `-1/2` for Benna-Fusi, `-3/4` to `-1` for the cascade, **undefined (curved)** for the naive arm.
   Fit the slope over the pre-knee window and report it with a CI. This is what "changes the SHAPE"
   means operationally.
4. **THE KNEE MOVES WITH `m` (or `n`), NOT WITH `N`.** Doubling `m` should move the knee right by
   `4x` (`T = 2^(2m+1)`) and cost `sqrt(m/(m+1))` of initial SNR. Doubling `N` should shift the whole
   curve UP without moving the knee. Two orthogonal, cheap manipulations that no level-effect
   confound reproduces.

**Replay (D4) is predicted to move the LEVEL, cascade (D8) to move the SLOPE** -- ORGAN_MAP's framing
is right, with the section-2.7 caveat that the spacing effect leaks across the boundary and must be
controlled by fixing the inter-repetition interval in the synapse-only arm.

### 4.3 The honesty point: is the cascade's initial-SNR COST stated in the literature? -- **YES, verbatim**

**Ben Dayan Rubin & Fusi 2007, abstract:**
> *"However, the initial memory trace, the one experienced immediately after memory storage, becomes
> weaker both when the number of metaplastic states increases and when the neural representations
> become sparser."*

**Same paper, introduction, with the cost quantified:**
> *"there is a great advantage of increasing the complexity of the synapse at the cost of only a
> 1/n reduction of the initial, most vivid memory trace, the one experienced immediately after
> storage."*

**Same paper, section "Complexity reduces the initial S/N", with the MECHANISM:**
> *"The initial S/N decreases with sparseness, but it is also reduced when complexity increases
> (larger n). This is a general property of a large class of metaplastic synapses and it is an
> obvious consequence of the existence of multiple synaptic states. Indeed, if all the states are
> visited with a nonzero probability, the synapse will spend only a fraction of its time roughly
> proportional to 1/n in the most plastic states."*

And the same paper shows the cost can **dominate** in a small system:
> *"for such a relatively small number of synapses [C = 10,000], there is a wide interval of time in
> which the multistate model outperforms the cascade model with the same number of states... it
> might appear to be deleterious when a single neuron with a relatively small number of synapses is
> considered."*
> *"for C = 10,000 the initial S/N is very close to the critical threshold, and most of the power law
> decay occurs in a region in which memories cannot be retrieved."*
> *"The best performance is obtained for the smallest n, because for a single neuron with a
> relatively small number of synapses the maximum memory lifetimes are anyway small and any
> additional complexity would not help."*

**This is a direct, quantitative warning against our own default scale.** The cascade wins only when
`N` is large: the same paper computes the cascade beats the multistate model for `N > 1e6` at
`n = 10`, and `N > 1e8` at `n = 15`. Our substrate's `d = 256..4096` is **six to ten orders of
magnitude below** that crossover for a single readout unit. Benna-Fusi's published figures use
`N = 2.5e7` and `N = 5.4e9`.

**Implication for STEP 5, stated plainly:** a cascade or Benna-Fusi synapse at our scale is
predicted **BY ITS OWN AUTHORS** to lose to a simpler synapse over a wide early window, and the
initial-SNR division by `n` (or `sqrt(m)`) may push the trace below the retrieval threshold
entirely. **This does not mean don't build it.** It means (a) the experiment must be powered to see
a crossover, not a uniform win; (b) the retention horizon must extend past `t*`, or the result is
guaranteed negative *and uninformative*; (c) `n`/`m` should be chosen from `T ~ (items to ingest)`
(section 2.5), not maximised; and (d) **a negative at small `N` is NOT evidence against the organ**
-- it is the published prediction, and calling it a ceiling would be exactly the
"don't generalise a narrow implementation failure to impossible" error.

### 4.4 One thing our own substrate may already have, and a specific place it is thrown away -- ANALYSIS

**ANALYSIS, not literature -- flagged as such.** Benna & Fusi's Online Methods derive the target
kernel from first principles: with an additive rule `w(t) = sum_{t'<t} dw(t') r(t-t')`, the noise is
`integral r(t)^2 dt`, which converges only for `r(t) = t^-beta` with `beta > 1/2`. Hence, verbatim:
*"the slowest power-law decay we can afford is `r(t) ~ t^(-1/2)`, which is the critical case in
which the synaptic variance just starts to diverge."* And: an **unbounded** perfect integrator
(`r = const`) already gives `SNR = sqrt(N/t)` -- the same exponent -- it just has unbounded weights.
**The entire content of Benna-Fusi is achieving `t^-1/2` with BOUNDED, low-precision variables.**

Now read that against ORGAN_MAP B3: `hdlab/reading_grounding_loop.py::ConceptSpace.observe` does
`self._sums[lemma] += ctx_vec` -- **an unbounded graded accumulator, i.e. exactly the `r = const`
integrator** -- and then `anchor_matrix:450` / `bundle:460` apply `np.sign(...)`, a **1-bit hard
bound**, one line before use.

**Hypothesis (mine, pending VET, explicitly NOT a literature claim): the live substrate's forgetting
exponent is not absent, it is DESTROYED BY THE `sign()`.** The accumulator has the brain-faithful
kernel; the terminal quantiser converts a bounded-variance `t^-1/2` system into a saturating 1-bit
one. If that is right, then the **cheapest possible D8 arm is not a cascade at all** -- it is
`freeze_graded()` / the existing default-OFF graded path, measured on the *log-log retention slope*
of section 4.2 rather than on a task score. That is a one-flag experiment that (a) tests a pinned
prediction, (b) needs no new organ, and (c) if it PASSES, tells us the cascade is buying protection
against *weight-range growth*, not against forgetting -- which is a different and much more precise
justification for building it.

**Caveat, because this is a strategic read and those run ahead of evidence:** `+= ctx_vec` with a
*bounded* number of encounters per concept is not the same regime as the continuous
random-uncorrelated stream Benna-Fusi analyse, and our "time" axis (new concepts ingested) is not
their "time" axis (memories stored *at this synapse*). The hypothesis is worth ONE cheap
measurement, not a redesign.

---

## 5. SUMMARY OF CORRECTIONS THIS DRILL OWES ORGAN_MAP

Reported here, **not applied** -- the brief forbids editing `ORGAN_MAP.md`.

| # | ORGAN_MAP text | correction | confidence |
|---|---|---|---|
| 1 | `SNR(t) ~ N/(sqrt(K) t^0.5)` (D8, lines 160/577/1119) | `sqrt(N)`, not `N`. Exact: `SNR(t) ~ sqrt(N) e^(-t/T) / (sqrt(t) sqrt(log T))`, `T = 2^(2m+1)` | HIGH -- eq (2) read verbatim |
| 2 | "capacity ~N not ~sqrt(N) (Fusi 2005)" | `~N` is **Benna-Fusi 2016**. Fusi-2005 cascade is `~sqrt(N)`; fast binary is `~log N` | HIGH -- Fusi's own review |
| 3 | "vs `N/t` for a single-state synapse" | single-state bounded/binary decays **exponentially**, `tau = 1/(qr)`. `sqrt(N)/t` is the cascade / the Lahiri-Ganguli envelope | HIGH |
| 4 | "`p(write|d) = 2^-d`" | two probability families, **both** `~2^-d`; the plastic one **resets depth to 1 in the opposite cascade** | HIGH on form, MED on the one-power offset |
| 5 | "power-law `t^-alpha` (alpha ~ 0.5-1.0)" | cascade: 3/4 (2005 original) or 1 (2007/2021). 0.5 is **Benna-Fusi**, a different model | HIGH |
| 6 | "Roxin & Fusi 2012" | **2013**, *PLoS Comput Biol* 9:e1003146 | HIGH |
| 7 | "each waking experience replayed only 1-3 times (Liu 2024 PMC11068097)" | **not in that source**; no count found anywhere. Treat as UNSOURCED / a free parameter | HIGH that the cited source lacks it |
| 8 | "expanding intervals, approximately doubling (Landauer & Bjork 1978)" | actual schedules `0,3,10` and `1,4,10` (~4x then 2.5x); scoped to **test-type** practice; the general superiority is **contested** (Karpicke & Roediger 2007) | HIGH -- primary read |
| 9 | "only REVERSE replays scale with reward (Foster & Wilson 2006)" | claim is **Ambrose, Pfeiffer & Foster 2016** *Neuron* 91:1124. Foster & Wilson 2006 discovered reverse replay, did not show reward modulation | HIGH |
| 10 | "meta-analysis ~1,396 participants g=0.50" | **Schimke, Angwin, Cheng & Copland 2021** *Psychon Bull Rev* 28:1811. 25 studies, k=29, n=1,396, omnibus g=0.50; recall 0.57, recognition 0.52, **lexical integration small**. Contrast is sleep vs **wake**, and the integration measures -- the CLS-relevant ones -- are the weakest | HIGH |
| 11 | "~5-10 SWRs per ~1 s up-state (Helfrich 2021 PNAS 118 e2012075118)" | **not verified in this drill** -- flagging only | LOW (absence of confirmation) |
| 12 | STEP 5 "run D8 and D4 as separate arms" | sound, but the **spacing effect is produced by the synapse alone** (Benna-Fusi Fig 7c inverted U). Fix inter-repetition spacing in the synapse-only arm, or run 2x2 | HIGH |

**Additions ORGAN_MAP does not currently have and that the build needs:**
`tau_k = 2^(2k+1)` (timescale ratio **4x** per level, not 2x); `C_k = 2^(k-1)`, `g_{k,k+1} = 2^(-k-2)`;
the discrete-time recurrence eqs (10)/(11) with `alpha = 1/4`; the closed-form cascade SNR
(Ben Dayan Rubin & Fusi 2007 eq 2) including its `2^(n-2)` knee; the initial-SNR cost `1/n` /
`1/sqrt(m)` **as a predicted, must-observe negative**; and the small-`N` warning of section 4.3.

---

## 6. REFERENCES

- Fusi S., Drew P. J., Abbott L. F. (2005). Cascade models of synaptically stored memories.
  *Neuron* 45(4):599-611. doi 10.1016/j.neuron.2005.02.001. **NOT OPENED -- see header.**
- Benna M. K., Fusi S. (2016). Computational principles of synaptic memory consolidation.
  *Nat Neurosci* 19(12):1697-1706. doi 10.1038/nn.4401. Preprint arXiv:1507.07580. **Opened, full text.**
- Ben Dayan Rubin D. D., Fusi S. (2007). Long memory lifetimes require complex synapses and limited
  sparseness. *Front Comput Neurosci* 1:7. doi 10.3389/neuro.10.007.2007. **Opened, full text.**
- Fusi S. (2021). Memory capacity of neural network models. arXiv:2108.07839. **Opened.**
- Zenke F. / Fusi lineage review (2017). Computational models of long term plasticity and memory.
  arXiv:1706.04946. **Opened** (Table 1 scaling summary).
- Lahiri S., Ganguli S. (2013). A memory frontier for complex synapses. *NIPS*. **Opened.**
- Fusi S., Abbott L. F. (2007). Limits on the memory storage capacity of bounded synapses.
  *Nat Neurosci* 10:485-493.
- Roxin A., Fusi S. (2013). Efficient partitioning of memory systems and its importance for memory
  consolidation. *PLoS Comput Biol* 9(7):e1003146.
- McClelland J. L., McNaughton B. L., O'Reilly R. C. (1995). Why there are complementary learning
  systems in the hippocampus and neocortex. *Psychol Rev* 102(3):419-457. **Opened, full text.**
- McCloskey M., Cohen N. J. (1989). Catastrophic interference in connectionist networks: the
  sequential learning problem. *Psychol Learn Motiv* 24:109-165.
- French R. M. (1999). Catastrophic forgetting in connectionist networks. *Trends Cogn Sci*
  3(4):128-135.
- Landauer T. K., Bjork R. A. (1978). Optimum rehearsal patterns and name learning. **Opened, full text.**
- Karpicke J. D., Roediger H. L. (2007). Is expanding retrieval a superior method for learning text
  materials? / Storm B. C., Bjork R. A., Storm J. C. (2010). *Mem Cognit* 38:244. (expanding-retrieval
  contest)
- Foster D. J., Wilson M. A. (2006). Reverse replay of behavioural sequences in hippocampal place
  cells during the awake state. *Nature* 440:680-683.
- Ambrose R. E., Pfeiffer B. E., Foster D. J. (2016). Reverse replay of hippocampal place cells is
  uniquely modulated by changing reward. *Neuron* 91(5):1124-1136.
- Mattar M. G., Daw N. D. (2018). Prioritized memory access explains planning and hippocampal replay.
  *Nat Neurosci* 21:1609-1617.
- Robinson H. L., Todorova R., Fernandez-Ruiz A. et al. (2025/2026). Large sharp-wave ripples promote
  hippocampo-cortical memory reactivation and consolidation during sleep. *Neuron*.
  doi 10.1016/j.neuron.2025.10.003.
- Stoianov I., Maisto D., Pezzulo G. (2022). The hippocampal formation as a hierarchical generative
  model supporting generative replay and continual learning. *Prog Neurobiol*.
- Barron H. C. et al. (2023). Generative replay underlies compositional inference in the
  hippocampal-prefrontal circuit. *Cell*.
- Dumay N., Gaskell M. G. (2007). Sleep-associated changes in the mental representation of spoken
  words. *Psychol Sci* 18(1):35-39.
- Davis M. H., Gaskell M. G. (2009). A complementary systems account of word learning: neural and
  behavioural evidence. *Phil Trans R Soc B* 364(1536):3773-3800. **Opened, full text.**
- Schimke E. A. E., Angwin A. J., Cheng B. B. Y., Copland D. A. (2021). The effect of sleep on novel
  word learning in healthy adults: a systematic review and meta-analysis. *Psychon Bull Rev*
  28:1811-1838. doi 10.3758/s13423-021-01980-3.
