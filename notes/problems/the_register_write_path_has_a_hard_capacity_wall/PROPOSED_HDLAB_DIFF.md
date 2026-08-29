# PROPOSED hdlab DIFF (strategy lands it, Q111) -- the register WRITE path + salience-gated hand-off

Solver builds+validates in `experiments/`+`verification/`; **strategy is the sole writer of `hdlab/`.** This file
states EXACTLY what would change and why. Two changes, both ADDITIVE / default byte-identical.

---

## Change 1 -- `hdlab/situation_model_accumulate.py`: an ASYMMETRIC leaky/recency WRITE option on `AccumulateRegister`

**Why:** the flat running sum (`register()` bundles ALL events with equal weight) has a HARD capacity wall -- recent
events become unrecoverable past ~0.25*D even under the landed serial crosstalk-cancellation readout. The brain's
sequential WM encoding is an asymmetric leaky recency gain (Warden & Miller 2007; Konecky 2017, PINNED-WEAK). Copy
the OPERATION `S = lambda*S + bind(role,item)`; sweep lambda. Default `leak=0.0` reproduces the flat sum byte-for-byte.

```python
class AccumulateRegister:
    def __init__(self, role_vocab, d, generator, max_event_slots=8, overwrite=False,
                 bundle_norm="percomp", leak=0.0):                 # <-- NEW: leak (0.0 = flat, byte-identical default)
        ...
        self.leak = float(leak)   # 0.0 = flat running sum (current path); >0 = asymmetric leaky recency WRITE

    def register(self, entity):
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        if len(events) == 1:
            return events[0]
        if self.leak > 0.0:
            # asymmetric leaky recency write: S_j = (1-leak) S_{j-1} + new  <=>  weight event i by (1-leak)^(k-1-i).
            # Read the RAW recency-weighted sum (argmax cleanup is scale-invariant; per-component renorm distorts
            # direction -- parent's measured rule). Recent events dominate; old events are geometrically suppressed.
            k = len(events)
            lam = 1.0 - self.leak
            w = torch.tensor([lam ** (k - 1 - i) for i in range(k)], dtype=torch.float32)
            wc = torch.complex(w, torch.zeros_like(w)).to(events[0].dtype)
            return (torch.stack(events, dim=0) * wc.unsqueeze(-1)).sum(dim=0)
        return bundling.bundle(torch.stack(events, dim=0), norm=self._bundle_norm_arg)
```

**Notes for the lander:**
- `decode()`/`decode_serial()`/`decode_set()` are UNCHANGED and still read `register()`/the raw event list. With
  `leak>0`, `decode()` (argmax on the weighted sum) is the RECENT readout -- this is the intended path.
- The existing OFF-by-default `recency` modulator in `hdlab/bundling.py` computes the SAME geometric decay as a
  batch reweight; it is the read-time equivalent. This diff makes the recency write a first-class, per-register
  option instead of a global modulator (a modulator would also reweight every OTHER bundle in scope). Prefer the
  per-register `leak` param.
- `make_situation_register(..., leak=...)` should thread `leak` through to the flat backend; the multibank backend
  can apply the same per-bank (composes with sharding -- each bank is smaller, so the leak is milder per bank).
- **FORM fidelity is confirmed on our organ:** the recovery-by-recency curve is GRADED/monotonic (3-bin
  newest/mid/oldest ~ [1.00, 0.96, 0.51] -- the primate 66/45/39 gradient shape), NOT a discrete-slot STEP (a hard
  bounded queue gives [1.00, 1.00, 0.01]). So `leak` (continuous), not a `maxlen` queue.
- **FIXED geometric `lambda^age` is the FAITHFUL per-trace form** (the research drill: a single-store power law is
  emergent from mixing many exponentials, so ONE store should carry a single geometric leak). It is the validated,
  better-pinned choice -- NOT a compromise.
- **Activity-adaptive lambda** (leak grows with buffer magnitude, a divisive-normalization-like gain) is an OPTIONAL
  variant. HONEST: my quick uncalibrated parameterization (`target=8`) UNDERPERFORMED the fixed leak (recent-4 ~0.5
  vs 1.0) -- a weak-impl result (poor target calibration), NOT a refutation of the form. Do NOT adopt `leak="adaptive"`
  without a proper target/gain sweep; and note the adaptive/divisive family is the same OUR-EXTENSION class as the
  read-side divnorm, so the fixed geometric leak is the more brain-pinned default.

## Change 2 -- a salience-gated hand-off from the register into the existing `HDFactStore`

**Why:** the leaky write buys recent recovery by DECAYING OLD events (a fundamental single-store trade). The brain
pairs the buffer with CONSOLIDATION to a permanent store, gated by CONTENT SALIENCE (prediction-error + schema-
congruence -- the SLIMM U-shape), **NOT by recency/eviction-order** (Tse 2007/2011; the brain positively rules out
eviction-order). Reuse the existing `HDFactStore` (never-forgets, content-addressed) -- do NOT build a new
consolidation mechanism (CLS/recency-chunking is research-refuted).

Recommended: a thin `register_consolidation.py` helper (NOT a change to `AccumulateRegister` itself), so the gate
policy lives in one place:

```python
def salience(pe_est, cong_est, w_pe=1.0, w_cong=1.0):
    """SLIMM U-shape: an event is consolidation-worthy iff it is at an EXTREME on EITHER independent channel."""
    return max(w_pe * pe_est, w_cong * cong_est)          # weighted-OR of prediction-error and schema-congruence

def maybe_commit(store, event, pe_est, cong_est, theta):
    """Commit an event to the durable store iff its salience clears theta (swept). Commit-most-salient, NOT
    oldest-evicted. CRITICAL: pe_est/cong_est MUST come from INDEPENDENT channels (a schema/prediction model +
    the MDL description-length drop), NEVER re-derived from the register's own accumulated code."""
    if salience(pe_est, cong_est) > theta:
        store.store(subject=event.entity, relation=event.role, obj=event.filler,
                    source="register_consolidation", trust="TRUST_MID")
```

**Notes for the lander:**
- `pe_est` = prediction-error / surprise of the item against the schema/script model (an independent predictor --
  reuse the prediction-error signal already in the stack). `cong_est` = the MDL description-length drop already
  computed by `script_grain_acquisition_loop`/`grounding_acquisition_loop` (Perfors-Tenenbaum two-part code).
- **HARD on-disk constraint (reproduced as the negative control):** a SELF-derived gate (salience read from the
  register's own readback confidence) HARD_FAILS -- it tracks RECENCY, not importance, and wastes the commit budget
  on events already safe in the buffer (matches `exp_attention_salience_reliability_gate_*` on disk, and the brain:
  VTA/LC compute PE in a separate circuit). The signal MUST be an independent channel.
- `theta` is a swept deployable PARAMETER (OUR-INVENTION), not a brain-pinned number.
- **Adjacent:** `HDFactStore.store` is a fine commit path as-is (glass-box, trust-tagged, content-addressed). No
  change needed to `hd_fact_store.py`.
