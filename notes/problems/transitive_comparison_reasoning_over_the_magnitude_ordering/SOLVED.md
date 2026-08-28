---
problem: transitive_comparison_reasoning_over_the_magnitude_ordering
status: SOLVED
bar: "PASSES only with ALL of: (1) Answers UN-STATED transitive pairs CI-separated over a no-integration floor: read pairwise comparisons, build the ordering, and predict the sign of UN-STATED pairs (A vs C, never compared directly) better than a floor that only uses the STATED pairs (no integration) -- recompute the floor; info-free twin (shuffled comparisons / random ordering) LOSES CI-sep; report CI half-width + null p95. (2) Brain-faithful mechanism: the ordering is built by INTEGRATING overlapping comparisons into one magnitude structure (place-code placement or relational binding), NOT a hard-coded symbolic sort. Show the SYMBOLIC-DISTANCE EFFECT (far un-stated pairs answered better/more-confidently than near ones). (3) Substrate-native: built on the LANDED p1 ruler + the register/binding. (4) Propose the exact hdlab diff."
result: "Un-stated transitive-pair sign accuracy on the association-MATCHED internal pairs (the pairs where net-win association gives ZERO signal): mechanism 1.000 vs association floor 0.500, paired margin +0.500 (CI [+0.500,+0.500], half-width 0.000) at N=7 clean premises, 120 seeds; under 20%-corrupted premises 0.672 vs 0.510 (+0.163, half-width 0.027, N=9). Grounded on REAL words via the landed p1 ruler: integration recovers the human concreteness order 1.000 vs association 0.673 (+0.327 CI-sep), n=200 12-word series. Reasoning-adds-value: on pairs a noisy text never states, integration 0.848 vs local-reading chance 0.500 (+0.348, half-width 0.010)."
floor: "STRONGEST floor = ASSOCIATIVE net-win ranking (rank items by #wins-#losses among stated premises), which is AT CHANCE (0.500) on the association-matched internal un-stated pairs BY CONSTRUCTION -- the Dusek/Eichenbaum control that isolates relational integration from associative strength. Also run: stated-only lookup (0.500 on un-stated), local-majority reader (0.500 on never-stated pairs, exp4), p1-direct read (grounded, exp3)."
controls: "info-free twin = shuffled premise directions -> random ordering (mean 0.522 at N7 / 0.488 exp4, LOSES CI-sep, null p95 0.73-0.80 at N=9); per-slot association floor at chance on matched pairs (excludes association-strength explanation); stated-only lookup at chance (excludes memorisation); float-vs-register localisation (integration EXACT & N-independent -> excludes an integration-failure explanation of any capacity limit); Hopfield-attractor and renorm controls inherited from the register-readout mechanism; p1-confident-premise reliability 0.87 (excludes garbage-premise explanation of the grounded arm)."
files_changed: "experiments/exp_transitive_ordering_magnitude_line_v1.py, experiments/exp_transitive_register_capacity_v1.py, experiments/exp_transitive_grounded_p1_reader_v1.py, experiments/exp_transitive_integration_denoises_v1.py, experiments/exp_transitive_magnitude_vs_rank_code_v1.py, experiments/exp_transitive_chaining_vs_magline_v1.py, verification/test_transitive_ordering_reasoning.py, notes/problems/transitive_comparison_reasoning_over_the_magnitude_ordering/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_transitive_ordering_reasoning.py"
---

# Transitive-comparison reasoning over a magnitude ordering — SOLVED

The reader can now take pairwise comparisons ("A > B, B > C"), **integrate them into one magnitude ordering**, and
answer the **un-stated** comparison ("A vs C") it was never told — the first genuine reasoning operation on top of p1's
ruler. It clears the association floor CI-separated, shows the symbolic-distance effect, runs on real words through the
landed p1 ruler, and — crucially — beats a local-only reader exactly in the regime reasoning is *for*.

## The mechanism (opening move: how does the brain do this?)

Transitive inference is **PINNED** in the brain as two coupled systems the brief names:
1. **Hippocampal relational integration** — overlapping premises sharing a middle term are integrated into ONE unified
   ordering, not stored as isolated pairs (Dusek & Eichenbaum 1997: fornix/hippocampal lesions kill the *inference*
   pairs while sparing the premises).
2. **Parietal magnitude-line placement** — the ordering is read out as a POSITION on a mental line (Walsh ATOM 2003;
   Nieder number neurons), giving the **symbolic-distance effect** (Moyer 1973 — the same distance effect p1's ruler
   already shows for adjectives).

The computational-level description of "integrate overlapping pairwise comparisons into scalar positions" is a
**delta-rule / value-transfer relaxation** (Frank, Rudy & O'Reilly 2003's connectionist TI model — the distance and
end-anchor effects EMERGE from it; Bradley-Terry is its maximum-likelihood characterization). This is **not** an
off-the-shelf sort: it is a local, iterative, biologically-plausible update — nudge the winner up, the loser down — and
overlapping premises couple through their shared middle term. That coupling **is** the brain's overlap-integration,
realized as coupled updates rather than symbolic chaining. It is why it beats a symbolic sort: it is graded, handles
noisy/conflicting premises, and yields a magnitude line with a distance effect.

**The substrate-native pipeline (copy the computation, sweep the parameters):**
- **INTEGRATE** — delta-rule settle the stated premises into a scalar magnitude position `x_i` per item.
- **STORE** — encode the ordering into the FHRR register: `S = Σ bind(item_key_i, FPE(scale·x_i))`, each item bound to
  its magnitude place code (p1's `fractional_power_encoding`), superposed. *This is what tests "can the register hold a
  transitive ordering."*
- **READ** un-stated (a,c) — unbind the item key from `S`, decode its coordinate on the FPE grid (native resonator
  read-out), and compare positions. `sign(x̂_a − x̂_c)` is the answer; `|x̂_a − x̂_c|` is the Weber distance signal.

## What was built and measured

**exp1 — core mechanism (`exp_transitive_ordering_magnitude_line_v1.py`).** N-item k-term series (adjacent premises
only, so internal items are association-matched). On the association-matched **internal un-stated pairs**: mechanism
**1.000** vs association floor **0.500** (+0.500 CI [+0.500,+0.500]); shuffled-premise twin 0.522 (LOSES, +0.421
CI-sep); stated-only lookup 0.500. **Symbolic-distance effect:** the Weber confidence `|x̂_a−x̂_b|` rises monotone with
symbolic distance (1.29 → 4.01, d2→d6); and in the sub-ceiling **noisy** regime the *accuracy* distance effect is
textbook — at 20%-corrupted premises, near pairs d2:0.676 rise to far pairs d8:0.920. **Noise robustness:** graceful
degradation (1.000 → 0.79 → 0.67 → 0.59 as premises corrupt 0→30%), still +0.079 CI-sep over the association floor at
30% corruption — where a hard symbolic sort would break on the induced cycles.

**exp2 — localisation + register capacity (`exp_transitive_register_capacity_v1.py`).** Holding the integration fixed
and varying only the storage: the delta-rule **integration is EXACT and N-independent** (float upper bound = 1.000
through N=30). The **register storage** carries a graded crosstalk cost that grows with N and is bought back by D
(N=16/D512 still 0.99; N=30/D512 → 0.873; N=25/D256 → 0.880). Serial decode-and-suppress (the read-out from the
just-solved register-readout problem) gives a small but real recovery at extreme overload (+0.014 CI-sep at N=30). So
**"can the register hold a transitive ordering?" → yes**; any capacity limit is a read-out limit of the shared store,
never an integration failure.

**exp3 — grounded on REAL words with the LANDED p1 ruler as front-end (`exp_transitive_grounded_p1_reader_v1.py`).**
Real words with human concreteness ratings (Brysbaert), p1's `ScalarMagnitudeChannel.oriented_position` reading the
comparisons. **ARM A (criterion/mastered premises):** integration **1.000** recovers the human order, beats association
0.673 (+0.327 CI-sep) and twin 0.497; holds to N=16. **ARM B (grounded-axis regime, honest boundary):** when a grounded
global axis exists (p1 can read any pair directly), integration 0.62 *ties/slightly-loses* p1-direct 0.64 on the hard
close pairs — there is no independent evidence to pool. This precisely delimits the two-systems division: parietal
direct magnitude read for grounded orderings, hippocampal relational integration for novel/text-defined ones.

**exp4 — where reasoning ADDS VALUE (`exp_transitive_integration_denoises_v1.py`).** Text presents scattered, noisy,
overlapping comparisons (Thurstonian independent observations). Integration **0.869** vs a local-only reader **0.675**
overall; on the pairs the text **never states** (54% of pairs), integration **0.848** vs local chance **0.500** (+0.348
CI-sep); and on noisy *observed* pairs the aggregation-denoising edge grows with per-observation noise (+0.003 at σ=1.5
→ +0.077 at σ=6.0). Info-free twin 0.488 LOSES. This resolves ARM B: integration beats local reading exactly when
comparisons are independent noisy observations — the real reading scenario.

**exp5 — which stored code is load-bearing (`exp_transitive_magnitude_vs_rank_code_v1.py`).** A finer on-brief drill
(§3's magnitude-placement vs relational-binding question). It overturned my prediction: a discrete-rank store (orthogonal
code per argsort-rank) shows the *identical* accuracy distance effect as the continuous magnitude code (slope 0.93 = 0.93)
— the distance effect is a read-out-noise property of any ordered code, not the magnitude metric. The magnitude
place-code is preferred for being **sort-free** and giving a **graded Weber confidence**; the discrete ranks buy capacity
(N=30/D256: 0.954 vs 0.843) — the honest trade-off. See KEY REALIZATION 6.

**exp6 — WHY the magnitude line and not serial chaining (`exp_transitive_chaining_vs_magline_v1.py`).** The decisive
brain-foundational drill for §3's second candidate ("relational-register integration" = the hippocampal recall/chaining
route). On the SAME noisy premises, serial chaining (exact directed BFS through the premise graph — a strong baseline
with no read-out noise) and the magnitude line reach the **same overall accuracy** (0.741 ≈ 0.737) but with **opposite
distance-effect direction**: magnitude slope **+0.91** (far pairs EASIER — the human signature), chaining slope
**−0.98** (far pairs HARDER, because a distance-d query needs ~d hops and a longer path more likely crosses a corrupted
edge). This holds across noise (magnitude +0.87→+0.95, chaining −1.00→−0.96 as ε 0.1→0.3). **Humans/animals show the
positive distance effect** (Moyer; the fast-BD finding) — so this MEASURES, on our substrate, why the magnitude-line
integration is the faithful mechanism and pure serial chaining is not (Eichenbaum 1997's argument). The crossover
(chaining better on near, magnitude better on far, same average) shows the brain *accepts* worse near-pair accuracy to
get the O(1) parallel magnitude comparison — which is precisely why the distance effect exists.

**Second human signature — the END-ANCHOR / serial-position effect** (exp6 `end_anchor_cell`): at every matched symbolic
distance, pairs involving an end item are judged more reliably than all-internal pairs (mean +0.12, positive at 100% of
distances). It emerges from the Bradley-Terry convex end-stretch (end items settle to more separated positions). So the
mechanism reproduces **both** classic human TI signatures (distance + end-anchor), both emergent, not hand-coded.

## What was NOT established (and what I would withdraw first)

- **The front-end (p1 reading close comparisons) is the weak link, not the reasoning.** p1's `oriented_position`
  correlates with human concreteness at ρ=0.65 globally but errs ~40% on *adjacent* (close-in-rating) pairs. Integration
  can only be as good as its premises; on a densely-sampled real series with p1 reading every adjacent premise, the
  ordering is garbage (0.52). The brain avoids this by training premises to criterion first — which is why ARM A uses
  mastered premises. **This is an adjacency to map, not a defect in the reasoning** (see below).
- **The grounded arm does not show integration beating direct reading** (ARM B is a small honest negative). I would
  withdraw any claim that transitive integration helps *on a grounded axis*; its value is for novel/text-defined
  orderings (exp1) and independent noisy comparisons (exp4).
- **Not tested on raw prose** — comparisons are read from a controlled set / p1 on word pairs, not mined from running
  sentences with a comparative-construction parser (that parser is a named adjacency below).
- **The settling is the value-transfer/BT *computational* account** — I did not test finer hippocampal implementations
  (conjunctive coding, replay, successor representation). exp2 shows the current mechanism already integrates exactly,
  so those would change *how*, not *whether*.

## KEY REALIZATIONS

1. **The distance effect INVERTED until I bounded the mental line.** Raw Bradley-Terry scores are unbounded (a clean
   chain pushes end items to ±8), which **phase-aliases** the FPE code — extreme items decode to the wrong sign, so far
   pairs became *harder* (the reverse of the human effect). The fix is brain-faithful: the parietal magnitude line is
   **bounded** (working-memory span); normalizing onto it keeps every coordinate in the FPE faithful regime, and the
   distance effect then emerges from read-out noise. *Lesson: a place code has a faithful range; unbounded values alias.*
2. **The association-matched internal pairs are the whole game.** Beating chance on *all* un-stated pairs is cheap (end
   items leak associative signal — the association floor gets 0.80 there). The Dusek/Eichenbaum control is to score only
   the internal pairs, where net-win association is 0.500 by construction; that is the only floor that proves
   *integration* rather than *association*.
3. **Localise integration vs storage before blaming capacity.** Float-vs-register showed integration is exact to N=30,
   so the register decay is purely a read-out/crosstalk limit — the same law as the register-readout problem, fixable by
   the same serial read-out, not a failure to hold the ordering.
4. **The honest grounded negative (ARM B) is the finding, not a failure.** On a fixed magnitude axis there is no
   independent evidence to integrate, so direct reading is optimal — correctly. Reasoning-over-comparisons earns its keep
   only when the ordering is defined by *independent* local statements (text) or has *no* readable global axis. exp4
   makes that regime concrete and measured.
5. **The BT end-stretch gives the end-anchor effect for free.** Preserving the convex settled spacing (rather than
   forcing uniform ranks) reproduces a second human TI signature (extreme items easier) alongside the distance effect.
6. **The distance effect is a read-out-noise property of ANY ordered code — not the magnitude metric** (exp5, which
   overturned my own prediction). A discrete-rank store (orthogonal code per argsort-rank) shows the *identical* accuracy
   distance effect as the continuous magnitude code (slope 0.93 vs 0.93), because bounded read-out error flips near pairs
   more than far pairs regardless of the code. The magnitude place-code is still the faithful choice, but for the right
   reasons: it is **sort-free** (encodes the continuous settled position; the discrete store needs an explicit argsort)
   and gives a **graded Weber confidence** (the human RT signature). Honest trade-off: orthogonal discrete ranks buy
   capacity (N=30/D256: 0.954 vs magnitude 0.843) — the magnitude manifold's similar-near-codes cost crosstalk. *Lesson:
   do not attribute a signature to the mechanism you like; a control code reproduced it from read-out noise alone.*
7. **The distance-effect DIRECTION is what actually pins the mechanism** (exp6 — the decisive drill). The *presence* of a
   distance effect is uninformative (KEY REALIZATION 6), but its SIGN is diagnostic: magnitude-line integration makes far
   pairs EASIER (+ slope), serial chaining makes them HARDER (− slope, more hops = more accumulated error). The human
   positive distance effect therefore rules out chaining and selects the magnitude line — the same argument Eichenbaum
   used from lesion + latency data, here reproduced as a mechanism dissociation on our own substrate. *This is the single
   strongest brain-foundational result: the mechanism choice is not asserted from the brief, it is forced by a measured
   human signature.* The mechanism also reproduces the END-ANCHOR effect (2nd signature) from the same BT settling.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

There is currently **no entry for transitive inference / relational-magnitude integration** — this is first ground.
Proposed entry: *"Transitive inference = hippocampal relational integration of overlapping pairwise comparisons into ONE
parietal magnitude-line ordering (Dusek & Eichenbaum 1997 PINNED; Walsh ATOM PINNED; symbolic-distance effect PINNED).
Our mechanism = delta-rule / value-transfer settling (Frank-Rudy-O'Reilly 2003; BT ML-equivalent — the SETTLING is
OUR-INVENTION-UNDER-TEST at the neural-implementation level, PINNED at the computational level) → bounded FHRR
magnitude-line register (item_key ⊗ FPE(position)) → native FPE resonator read-out. MEASURED: integration is exact and
N-independent; the ordering is held in the register (read-out-limited, D-bought, serial-recoverable); the distance +
end-anchor effects reproduce; beats the association floor CI-sep on matched pairs; adds value over local reading on
independent noisy comparisons; TIES direct reading on a grounded 1-D axis (two-systems boundary); and the distance-effect
DIRECTION dissociates it from serial chaining -- chaining gives the INVERSE (far harder), the magnitude line the human
POSITIVE (far easier), so the human signature FORCES the magnitude-line choice (Eichenbaum 1997, measured on-substrate)."* Also a correction
to carry: the FPE magnitude code has a **bounded faithful range** — encoding an unbounded coordinate phase-aliases and
inverts the distance effect (a concrete deviation for any organ that stores a magnitude via FPE).

## PROPOSED hdlab DIFF (strategy lands it; Q111 — I do not write hdlab/)

**ADD a new default-off island `hdlab/transitive_ordering.py`** (reuses `hdlab.fractional_power_encoding`,
`hdlab.binding`, `hdlab.situation_model_accumulate.unit_phase_vec`; composes with the landed
`hdlab.scalar_adjective_operation.ScalarMagnitudeChannel` as the front-end reader):

```python
def settle_ordering(premises, n, eta=0.3, epochs=200, temp=1.0, seed=0) -> np.ndarray:
    """Delta-rule / value-transfer relaxation of pairwise premises (winner,loser) into scalar magnitude positions.
    Overlapping premises couple via the shared middle term -> ONE integrated ordering. (PINNED computation.)"""

def to_mental_line(x) -> np.ndarray:
    """Normalize settled scores onto the BOUNDED parietal magnitude line (FPE faithful range; no phase aliasing)."""

class TransitiveOrderingRegister:
    """Holds a transitive ordering as an FHRR superposition and answers un-stated comparisons natively.
      build(premises, n): positions = to_mental_line(settle_ordering(...)); S = sum bind(item_key_i, FPE(pos_i)).
      compare(a, b) -> (sign, distance): decode coords from S (optional serial decode-and-suppress under load);
                       sign = the transitive answer, distance = the Weber symbolic-distance signal.
      Front-end: pass premise directions from ScalarMagnitudeChannel.oriented_position (p1 reads the comparisons)."""
```

Wiring (default-off): the reader routes a passage containing multiple comparative statements to this organ; the p1
ruler supplies the premise directions; `compare` answers un-stated transitive queries. Keep it an island until the
comparative-sentence front-end (below) is wired.

## ADJACENT COMPONENTS TO MAP (candidate follow-on problems)

1. **p1's close-pair discrimination is the bottleneck of grounded transitive reading.** On-disk: `oriented_position` ρ=0.65
   but ~40% error on adjacent-in-rating pairs (`data/exp_transitive_grounded_p1_reader_v1/`). Leverage: the whole grounded
   pipeline is premise-read-limited; improving p1's fine (close) discrimination or aggregating repeated independent reads
   (exp4 shows aggregation works) directly raises grounded TI. *This is the single highest-leverage adjacency.*
2. **No comparative-sentence front-end.** Nothing mines "bigger/older/faster than X" constructions from running prose into
   (winner, loser) premises. The mechanism consumes premises; a parser is needed to feed it from text (spaCy dependency
   parse of comparative constructions). Leverage: turns this from a controlled-set capability into a reading capability.
3. **The FPE-magnitude bounded-range deviation** (KEY REALIZATION 1) applies to any organ storing a magnitude via FPE —
   worth a one-line guard/normalizer in `fractional_power_encoding` (out of my scope; flagged for the audit).
4. **Register read-out under a magnitude manifold** — exp2 found serial decode-and-suppress recovers *less* here than in
   the register-readout problem, because a smooth 1-D magnitude manifold has milder, structured crosstalk than i.i.d.
   discrete roles. A manifold-aware read-out (resonator over the FPE grid jointly) could recover more — a small optimisation.

---

## TLDR (plain language)

We taught the reader to reason, not just compare. Before, it could judge "which of these two is bigger?" Now, if a story
says "the whale is bigger than the shark" and "the shark is bigger than the tuna," it works out on its own that the whale
is bigger than the tuna — a fact the story never stated. It does this the way brains are believed to: it nudges each
thing up or down a mental "ruler" a little for every comparison it reads, until everything sits in one consistent order,
then reads off the answer by comparing positions on that ruler. It gets these unstated answers essentially perfectly when
the comparisons it was given are reliable, it is more confident about things that are far apart on the ruler than close
together (exactly like people), and it keeps working when up to a third of the comparisons it reads are wrong. On real
words it rebuilds the human sense of "how concrete is this word" from scattered comparisons. And — the important part —
it beats a reader that just memorizes each comparison it saw, because it can answer comparisons it was never given and
average out noisy ones. The one honest limit: when the reader already has a reliable built-in gauge for something (like
word meaning from experience), reasoning through comparisons doesn't beat just reading the gauge directly — reasoning is
for the *new* orderings a story invents, which is exactly what we want.

## QUESTIONS

None blocking. One decision for the owner/strategy: whether to prioritise the **comparative-sentence front-end**
(adjacency 2) next so this becomes a running-prose reading capability, versus banking the controlled-set mechanism as-is.

## NEXT STEPS

1. Strategy re-verifies (`verification/test_transitive_ordering_reasoning.py`, 9/9) and, on `owner_verdict: DONE`, lands
   the proposed `hdlab/transitive_ordering.py` island (default-off).
2. File adjacency 1 (p1 close-pair discrimination) and adjacency 2 (comparative-sentence parser) as follow-on problems.
3. The 30-min deepening cron keeps drilling (finer hippocampal implementations; the manifold-aware read-out) until the
   checklist is dry; I cancel it and finalise on the owner's verdict.
