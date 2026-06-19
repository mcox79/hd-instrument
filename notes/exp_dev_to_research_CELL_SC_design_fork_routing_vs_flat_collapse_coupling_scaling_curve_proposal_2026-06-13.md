# exp_dev -> research: CELL SC design fork -- routing-robustness vs flat-collapse are COUPLED; need a regime decision (scaling-curve vs defer)

**Filed-by:** exp_dev (Opus) 2026-06-13. **Scaffold:** `experiments/exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1.py` (HEAD 305c41dc). Logic + routing + within/between VALIDATED; not queued to GPU pending your design call (no tuned-to-pass).

## What I built + what the smoke revealed

Memory-bounded synthetic 10M probe (regenerates atom vectors per chunk from seed; never materializes 40GB). Categorical-partition model
(atom = normalize(beta*c_p + sqrt(1-beta^2)*unit_noise)); FLAT cleanup over all N vs ROUTED cleanup within the routed <=50K partition.

Smoke (N=200K, beta=0.55, retrieval-noise 0.50): routing accuracy **100%**, L1 within/between **12.03x**, max-partition 20K (<=50K). BUT
**flat recall@10 = 1.0 AND routed recall@10 = 1.0** -> the flat memory has not entered the interference-collapse regime, so the
partition-routing RESCUE is UNTESTED (both trivially succeed). Verdict honestly returns UNKNOWN(rescue-untested), not a fake pass.

## The design tension (why a single tuned point is wrong)

The existential claim is "flat cleanup collapses at scale (tau-limit), partition-routing rescues it." To make FLAT collapse you must push
the query into the interference regime where the target's recovery cosine `tau` is comparable to the max of N distractor cosines. The
distractor-max grows like sqrt(2 ln N / D). At D=1024:
- N=10M:  flat distractor-max ~ 0.177
- N'=40K (one partition): ~ 0.144
So the flat-collapses-AND-routed-survives window is **tau in (0.144, 0.177)** -- NARROW at D=1024. Outside it, both survive or both fail.

Worse, the SAME query-noise that lowers `tau` into that window also **degrades routing**: routing reads <query, c_p> ~ beta/sqrt(1+r^2),
which at the noise needed for tau~0.16 drops to ~0.09, competing with the cross-partition distractor-max ~0.10 over 250 partitions -> routing
starts to fail. So pushing flat to collapse simultaneously breaks routing. Routing-robustness and flat-collapse are COUPLED through the
single query-noise knob in the naive model.

In reality they are SEPARABLE (routing reads the category/L1 signal; cleanup reads the identity signal -- different cues), but modeling
that faithfully needs the query to carry a clean category cue + a noisy identity cue independently.

## Proposed honest redesign (the fork)

**Option A -- proper scaling-CURVE study (I build it, ~1 day GPU on remote):**
- Decouple the two cues: query = [clean category tag for routing] + [noisy identity for cleanup], so routing stays robust while `tau` is
  swept independently.
- Sweep N in {1e5, 1e6, 1e7} at a FIXED operating point; report recall@10 curves for FLAT(N) vs ROUTED (N-invariant, depends only on
  partition size). The robust, non-tuned finding = "routed recall is N-invariant; flat degrades monotonically" -- extrapolates decisively
  to the 100M-1B regime even where the 10M gap is modest. Also report the tau-window vs D (higher D widens the routing benefit).
- HARD-PASS = routed >=0.60 at 1e7 AND flat strictly degrading across the sweep AND routing acc >=0.9 AND max-partition<=50K.

**Option B -- defer SC until the mapper ships real atoms:** run the scaling probe on the REAL ingested codebook geometry (which has the
actual clustered/sub-free-Poisson structure from Cell C, not synthetic categories) -- arguably more faithful, but gated on Testbed mapper.

## My recommendation

**Option A now** (the architecture-survival question is worth answering before any real 10M pour, and the decoupled-cue design is the right
model), with the real-codebook version (B) as a follow-up post-mapper. But this is a genuine regime/design call with your name on the
pre-reg -- hence routing it to you rather than picking unilaterally. If you greenlight A I'll build the decoupled scaling-curve version
and queue the full sweep to the idle desktop GPU. If you'd rather I not spend ~1 day GPU on synthetic, I'll defer to B and pick up another
ungated cell meanwhile.

Scaffold stands (validated) either way; nothing tuned-to-pass shipped.
