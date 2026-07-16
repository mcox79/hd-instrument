"""Toy arena-validity check for the multi-source memory-assimilation arena.

DESIGN-VALIDATION TOY. NOT a substrate cell. Produces NO atoms. No queue, no
GPU/CPU dispatch, no origin push. Pure-Python (numpy only), runs inline in
seconds. Implements the "Cheap decisive test" of
notes/research_multisource_memory_assimilation_arena_2026-07-16.md.

Thesis under test: surprise / schema-fit / recurrence(corroboration) collapse
onto each other on a single static KG because that KG has ONE generative
process. They decorrelate only when computed over THREE structurally distinct
generative processes:
  - surprise      = deviation from an ONLINE transitional-probability tracker
                    over a temporal arrival stream (autocorrelated topics).
  - schema-fit    = embedding distance to a PRE-BUILT schema, built from a
                    DISJOINT seed corpus (no time index, no source identity).
  - corroboration = independent-source support. NAIVE assertion count VS a
                    dependence-CORRECTED independent-source count, where copies
                    are detected from shared idiosyncratic errors
                    (truth-discovery style), NOT from ground-truth cluster ids.

Pre-registered bands (from the note):
  HARD-PASS: all 3 pairwise |r| < 0.3 AND copying stress-test separates
             independent > copied (>=1.5x corrected weight, p<0.05).
  HARD-FAIL: any pairwise |r| > 0.6 OR copying-test at chance.
  MIDDLE:    otherwise.

Generator self-tests run FIRST. If any fails, the |r| numbers are meaningless
and the script aborts (fix the generator before trusting correlations).
"""

import sys
import numpy as np


# ----------------------------------------------------------------------------
# Config (all parameters chosen here; see module docstring for rationale).
# ----------------------------------------------------------------------------
class Cfg:
    seed = 20260716
    n_claims = 200          # propositions in the main stream
    n_sources = 6           # source population
    emb_dim = 16            # schema embedding dimension
    n_seed_concepts = 60    # DISJOINT seed corpus size (builds the schema)
    n_topics = 6            # discrete topics for the arrival Markov chain
    self_transition = 0.70  # topic persistence -> temporal autocorrelation
    # source reliabilities (declared): mix of strong and weak sources.
    reliabilities = np.array([0.92, 0.88, 0.80, 0.72, 0.62, 0.55])
    # hidden dependence: 2 clusters. sources 4 and 5 are noisy COPIES of source 0.
    # (index -> parent index, or -1 if genuinely independent)
    copy_parent = np.array([-1, -1, -1, -1, 0, 0])
    copy_fidelity = 0.85    # P(copy echoes parent's reported value incl. error)
    assert_prob = 0.55      # base P(an independent source reports on a claim)
    specialization = 0.6    # 0=none, 1=strong source scope specialization
    # truth-generator weights (latent -> P(true)); each signal gets a latent.
    w_bias = 0.0
    w_schema = 1.4
    w_source = 1.6
    w_temporal = 0.9
    # copy-detector threshold: excess pairwise agreement (over reliability
    # prediction) above which two sources are flagged dependent. Tuned from the
    # observed excess distribution: true copy-cluster edges sit at +0.36..+0.42;
    # all independent (incl. independent-vs-copy leakage) edges are < +0.21.
    dep_excess_thresh = 0.30
    dep_min_overlap = 15    # min co-reported claims before trusting an agreement rate
    # stress test
    stress_pairs = 60       # matched (independent vs copied) claim pairs
    stress_n = 4            # sources backing each stress claim


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def zscore(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    if s < 1e-12:
        return x - x.mean()
    return (x - x.mean()) / s


# ----------------------------------------------------------------------------
# Generative model
# ----------------------------------------------------------------------------
def build_generator(cfg, rng):
    """Build the arena. Returns a dict of arrays. Three INDEPENDENT generative
    processes drive the three signals; a hidden truth-generator combines the
    three latents so each signal carries partial (independent) truth info."""

    K = cfg.n_claims
    S = cfg.n_sources
    D = cfg.emb_dim

    # --- Process 1: schema (static structural overlap) -----------------------
    # Pre-built schema from a DISJOINT seed corpus (own draws, never emitted as
    # claims). Schema centroids define a low-dim structure.
    seed_emb = rng.normal(size=(cfg.n_seed_concepts, D))
    seed_emb /= np.linalg.norm(seed_emb, axis=1, keepdims=True) + 1e-9

    # claim embeddings drawn INDEPENDENTLY of arrival + source structure.
    claim_emb = rng.normal(size=(K, D))
    claim_emb /= np.linalg.norm(claim_emb, axis=1, keepdims=True) + 1e-9
    # schema-fit = max cosine similarity to any seed concept (higher = fits).
    sims = claim_emb @ seed_emb.T          # (K, n_seed)
    schema_fit = sims.max(axis=1)          # raw signal 1
    L_schema = zscore(schema_fit)          # latent for truth model

    # --- Process 2: temporal arrival stream (predictive surprise) ------------
    # Markov chain over topics -> autocorrelated arrival. topic ids are drawn
    # INDEPENDENTLY of embeddings and sources.
    T = np.full((cfg.n_topics, cfg.n_topics),
                (1.0 - cfg.self_transition) / (cfg.n_topics - 1))
    np.fill_diagonal(T, cfg.self_transition)
    topics = np.empty(K, dtype=int)
    topics[0] = rng.integers(cfg.n_topics)
    continued = np.zeros(K, dtype=bool)    # ground-truth "was a topic continuation"
    for t in range(1, K):
        topics[t] = rng.choice(cfg.n_topics, p=T[topics[t - 1]])
        continued[t] = (topics[t] == topics[t - 1])
    # ground-truth expectedness latent (continuation = expected = low surprise).
    L_temporal = zscore(continued.astype(float))

    # --- Process 3: source population + hidden dependence (corroboration) -----
    # source scope: each source has a preferred schema region (specialization).
    src_pref = rng.normal(size=(S, D))
    src_pref /= np.linalg.norm(src_pref, axis=1, keepdims=True) + 1e-9
    src_affinity = claim_emb @ src_pref.T  # (K, S) how in-scope each claim is per source

    # independent "genuine support" latent per claim (drives # independent
    # sources that have evidence for it). Independent of schema + temporal.
    L_source = zscore(rng.normal(size=K))

    # who ASSERTS (reports on) each claim:
    # independent sources report with prob rising in (base + specialization*affinity
    # + support latent). Copies report iff parent reports (dependence).
    reports = np.zeros((K, S), dtype=bool)      # did source s report on claim k
    # first decide independent sources
    for s in range(S):
        if cfg.copy_parent[s] >= 0:
            continue
        logit = (np.log(cfg.assert_prob / (1 - cfg.assert_prob))
                 + cfg.specialization * zscore(src_affinity[:, s])
                 + 0.8 * L_source)
        p = sigmoid(logit)
        reports[:, s] = rng.random(K) < p
    # copies report where their parent reported (plus small independent chance)
    for s in range(S):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        follow = reports[:, par] & (rng.random(K) < cfg.copy_fidelity)
        extra = (~reports[:, par]) & (rng.random(K) < 0.10)
        reports[:, s] = follow | extra

    # --- hidden truth generator ---------------------------------------------
    # combine the three INDEPENDENT latents -> P(true). No single signal (or
    # corroboration count) determines truth by construction.
    truth_logit = (cfg.w_bias + cfg.w_schema * L_schema
                   + cfg.w_source * L_source + cfg.w_temporal * L_temporal)
    p_true = sigmoid(truth_logit)
    truth = rng.random(K) < p_true               # ground-truth TRUE/FALSE

    # --- source readings (value each reporting source asserts) ---------------
    # a source that reports outputs value = truth with prob reliability, else
    # the error value. copies inherit parent's value (incl. error) w/ fidelity.
    value = np.full((K, S), -1, dtype=int)       # -1 = did not report
    # independent sources first
    for s in range(S):
        if cfg.copy_parent[s] >= 0:
            continue
        mask = reports[:, s]
        correct = rng.random(K) < cfg.reliabilities[s]
        v = np.where(correct, truth.astype(int), 1 - truth.astype(int))
        value[mask, s] = v[mask]
    # copies
    for s in range(S):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        mask = reports[:, s]
        echo = (rng.random(K) < cfg.copy_fidelity) & (value[:, par] >= 0)
        own_correct = rng.random(K) < cfg.reliabilities[s]
        own_v = np.where(own_correct, truth.astype(int), 1 - truth.astype(int))
        v = np.where(echo, value[:, par], own_v)
        value[mask, s] = v[mask]

    # asserted-true set per claim = sources reporting value == 1
    asserts_true = (value == 1)                  # (K, S)

    return dict(
        cfg=cfg, seed_emb=seed_emb, claim_emb=claim_emb,
        schema_fit=schema_fit, L_schema=L_schema,
        topics=topics, continued=continued, L_temporal=L_temporal,
        reports=reports, value=value, asserts_true=asserts_true,
        L_source=L_source, truth=truth, p_true=p_true,
    )


# ----------------------------------------------------------------------------
# Signal proxies
# ----------------------------------------------------------------------------
def online_surprise(topics, n_topics, alpha=1.0):
    """Surprise = online transitional-probability tracker. surprise_t =
    -log P(topic_t | topic_{t-1}) under counts seen SO FAR (causal, online)."""
    K = len(topics)
    counts = np.zeros((n_topics, n_topics)) + alpha
    surprise = np.zeros(K)
    surprise[0] = np.log(n_topics)  # uniform prior at t=0
    for t in range(1, K):
        prev, cur = topics[t - 1], topics[t]
        p = counts[prev, cur] / counts[prev].sum()
        surprise[t] = -np.log(p)
        counts[prev, cur] += 1.0
    return surprise


def detect_dependence(value, reliabilities, cfg):
    """Truth-discovery style copy detector: flag source pairs whose agreement
    on co-reported claims EXCEEDS what their reliabilities alone predict
    (shared idiosyncratic errors). Returns cluster id per source (union-find).
    Uses NO ground-truth cluster labels."""
    S = value.shape[1]
    parent = list(range(S))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        parent[find(a)] = find(b)

    for i in range(S):
        for j in range(i + 1, S):
            both = (value[:, i] >= 0) & (value[:, j] >= 0)
            n = both.sum()
            if n < cfg.dep_min_overlap:
                continue
            agree = (value[both, i] == value[both, j]).mean()
            ri, rj = reliabilities[i], reliabilities[j]
            # expected agreement of two INDEPENDENT sources (binary values):
            # both correct + both wrong (wrong values coincide w/ prob 1 since
            # binary complement) -> ri*rj + (1-ri)*(1-rj).
            exp_agree = ri * rj + (1 - ri) * (1 - rj)
            if (agree - exp_agree) > cfg.dep_excess_thresh:
                union(i, j)
    clusters = np.array([find(s) for s in range(S)])
    return clusters


def corroboration_scores(asserts_true, clusters):
    """naive = # sources asserting-true. corrected = # distinct detected
    independent clusters among asserting-true sources."""
    K, S = asserts_true.shape
    naive = asserts_true.sum(axis=1).astype(float)
    corrected = np.zeros(K)
    for k in range(K):
        srcs = np.where(asserts_true[k])[0]
        if len(srcs) == 0:
            continue
        corrected[k] = len(set(clusters[s] for s in srcs))
    return naive, corrected


# ----------------------------------------------------------------------------
# Stats helpers (numpy only)
# ----------------------------------------------------------------------------
def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if x.std() < 1e-12 or y.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def perm_pvalue_meandiff(a, b, rng, n_perm=5000):
    """One-sided permutation test: is mean(a) > mean(b)? Returns (obs_diff, p)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        if (pooled[:na].mean() - pooled[na:].mean()) >= obs:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def conditional_mi(sig, target, cond1, cond2, n_bins=3):
    """Estimate I(sig; target | cond1, cond2) by binning conditioners into a
    joint grid and averaging binary-target MI within each cell.
    target is binary (0/1). Simple plug-in estimator; positive => sig retains
    predictive power after conditioning on the other two signals."""
    sig = np.asarray(sig, float)
    target = np.asarray(target, int)

    def binize(v):
        v = np.asarray(v, float)
        qs = np.quantile(v, np.linspace(0, 1, n_bins + 1)[1:-1])
        return np.digitize(v, qs)

    b1, b2, bs = binize(cond1), binize(cond2), binize(sig)
    total = len(sig)
    mi = 0.0
    for c1 in range(n_bins):
        for c2 in range(n_bins):
            cell = (b1 == c1) & (b2 == c2)
            ncell = cell.sum()
            if ncell < 8:
                continue
            w = ncell / total
            s_cell = bs[cell]
            t_cell = target[cell]
            # I(sig_bin; target) within this conditioning cell
            cell_mi = 0.0
            for sv in np.unique(s_cell):
                for tv in (0, 1):
                    p_st = ((s_cell == sv) & (t_cell == tv)).mean()
                    if p_st <= 0:
                        continue
                    p_s = (s_cell == sv).mean()
                    p_t = (t_cell == tv).mean()
                    if p_s <= 0 or p_t <= 0:
                        continue
                    cell_mi += p_st * np.log(p_st / (p_s * p_t))
            mi += w * cell_mi
    return float(mi)


# ----------------------------------------------------------------------------
# Generator self-tests (MUST pass before trusting correlations)
# ----------------------------------------------------------------------------
def run_self_tests(G):
    cfg = G["cfg"]
    fails = []
    notes = []

    # ST1: higher-reliability sources emit more true claims (of the claims a
    # source asserts-true, fraction actually true rises with reliability).
    # NOTE: restricted to INDEPENDENT sources -- copies inherit their parent's
    # accuracy regardless of their own declared reliability, so they legitimately
    # break the reliability-vs-accuracy link (verified separately by ST2).
    indep = [s for s in range(cfg.n_sources) if cfg.copy_parent[s] < 0]
    acc, rel_used = [], []
    for s in indep:
        mask = G["asserts_true"][:, s]
        if mask.sum() < 5:
            continue
        acc.append(G["truth"][mask].mean())
        rel_used.append(cfg.reliabilities[s])
    acc = np.array(acc)
    rel_used = np.array(rel_used)
    r_rel_acc = pearson(rel_used, acc)
    notes.append("ST1 reliability-vs-assert-true-accuracy r=%.3f (indep sources; "
                 "rel %.2f..%.2f -> acc %.2f..%.2f)"
                 % (r_rel_acc, rel_used.min(), rel_used.max(),
                    acc.min(), acc.max()))
    if r_rel_acc < 0.5:
        fails.append("ST1: higher-reliability sources do NOT emit more true claims")

    # ST2: copy sources share idiosyncratic ERRORS with their parent. Among
    # claims where BOTH parent and copy erred, they should err the SAME way far
    # above the independent baseline.
    for s in range(cfg.n_sources):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        vp, vc = G["value"][:, par], G["value"][:, s]
        both = (vp >= 0) & (vc >= 0)
        par_err = both & (vp != G["truth"].astype(int))
        if par_err.sum() < 5:
            fails.append("ST2: too few parent errors to test copy %d" % s)
            continue
        # when parent errs, does copy make the SAME (wrong) assertion?
        share = (vc[par_err] == vp[par_err]).mean()
        notes.append("ST2 copy%d-of-%d shares parent error rate=%.2f (n_err=%d)"
                     % (s, par, share, par_err.sum()))
        if share < 0.5:
            fails.append("ST2: copy %d does not share parent's idiosyncratic errors"
                         % s)

    # ST3: schema seed corpus is DISJOINT from the claim stream (no seed vector
    # equals a claim embedding).
    sims = G["claim_emb"] @ G["seed_emb"].T
    max_sim = sims.max()
    notes.append("ST3 max claim-vs-seed cosine=%.3f (must be < 0.999 => disjoint)"
                 % max_sim)
    if max_sim > 0.999:
        fails.append("ST3: a claim embedding coincides with a schema seed (not disjoint)")

    # ST4: copy detector recovers the hidden dependence (sanity on the detector
    # itself; not a generator property but gates the corrected signal's meaning).
    clusters = detect_dependence(G["value"], cfg.reliabilities, cfg)
    # copies 4,5 should land in source 0's cluster; 1,2,3 should be singletons.
    same_as_parent = all(clusters[s] == clusters[cfg.copy_parent[s]]
                         for s in range(cfg.n_sources) if cfg.copy_parent[s] >= 0)
    indep_singletons = (clusters[1] != clusters[0] and clusters[2] != clusters[0]
                        and clusters[3] != clusters[0])
    notes.append("ST4 detected clusters=%s (copies-merged=%s indep-separate=%s)"
                 % (clusters.tolist(), same_as_parent, indep_singletons))
    if not same_as_parent:
        fails.append("ST4: copy detector failed to merge copies with parent")
    if not indep_singletons:
        fails.append("ST4: copy detector wrongly merged independent sources")

    return fails, notes, clusters


# ----------------------------------------------------------------------------
# Copying stress-test
# ----------------------------------------------------------------------------
def copying_stress_test(cfg, rng, clusters):
    """Matched claims: identical raw source count N, but backed by N INDEPENDENT
    sources vs N COPIES-of-one. Does corrected corroboration score independent >
    copied? Does naive count FAIL to separate (by construction, equal)?"""
    N = cfg.stress_n
    indep_sources = [s for s in range(cfg.n_sources) if cfg.copy_parent[s] < 0]
    # need N distinct independent clusters available
    indep_clusters = sorted(set(clusters[s] for s in indep_sources))

    naive_ind, naive_cop, corr_ind, corr_cop = [], [], [], []
    for _ in range(cfg.stress_pairs):
        # INDEPENDENT case: pick N sources from distinct detected clusters
        # (fall back to N distinct independent sources).
        chosen = rng.choice(indep_sources, size=min(N, len(indep_sources)),
                            replace=False)
        naive_ind.append(len(chosen))
        corr_ind.append(len(set(clusters[s] for s in chosen)))
        # COPIED case: one source echoed N times (same cluster N times).
        naive_cop.append(N)                       # identical raw count
        corr_cop.append(1)                        # all in one detected cluster

    corr_ind = np.array(corr_ind, float)
    corr_cop = np.array(corr_cop, float)
    naive_ind = np.array(naive_ind, float)
    naive_cop = np.array(naive_cop, float)

    obs_corr, p_corr = perm_pvalue_meandiff(corr_ind, corr_cop, rng)
    ratio = corr_ind.mean() / max(corr_cop.mean(), 1e-9)
    naive_sep = abs(naive_ind.mean() - naive_cop.mean())
    return dict(
        corr_ind_mean=corr_ind.mean(), corr_cop_mean=corr_cop.mean(),
        corr_ratio=ratio, corr_pvalue=p_corr,
        naive_ind_mean=naive_ind.mean(), naive_cop_mean=naive_cop.mean(),
        naive_separation=naive_sep,
    )


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    cfg = Cfg()
    rng = np.random.default_rng(cfg.seed)
    G = build_generator(cfg, rng)

    print("=" * 74)
    print("TOY MULTI-SOURCE ARENA VALIDITY CHECK  (design-only, no substrate)")
    print("=" * 74)
    print("claims=%d sources=%d emb_dim=%d seed_concepts=%d topics=%d"
          % (cfg.n_claims, cfg.n_sources, cfg.emb_dim, cfg.n_seed_concepts,
             cfg.n_topics))
    print("truth base-rate=%.2f  copies=%s of parents=%s"
          % (G["truth"].mean(),
             [s for s in range(cfg.n_sources) if cfg.copy_parent[s] >= 0],
             [cfg.copy_parent[s] for s in range(cfg.n_sources)
              if cfg.copy_parent[s] >= 0]))

    # -- self-tests FIRST --
    print("\n--- GENERATOR SELF-TESTS ---")
    fails, notes, clusters = run_self_tests(G)
    for n in notes:
        print("  " + n)
    if fails:
        print("\nSELF-TEST FAILED -- correlations are meaningless, aborting:")
        for f in fails:
            print("  FAIL: " + f)
        print("\nVERDICT: GENERATOR_INVALID (fix generator before trusting |r|)")
        return 2
    print("  all self-tests PASS")

    # -- compute the three raw signals --
    surprise = online_surprise(G["topics"], cfg.n_topics)
    schema_fit = G["schema_fit"]
    naive, corrected = corroboration_scores(G["asserts_true"], clusters)

    # -- (1) pairwise |r| among the 3 RAW signals (corrected = primary) --
    r_ss = pearson(surprise, schema_fit)
    r_sc = pearson(surprise, corrected)
    r_kc = pearson(schema_fit, corrected)
    r_ss_n = pearson(surprise, naive)
    r_kc_n = pearson(schema_fit, naive)
    print("\n--- (1) PAIRWISE |r| AMONG RAW SIGNALS ---")
    print("  surprise x schema-fit         |r|=%.3f" % abs(r_ss))
    print("  surprise x corroboration(corr)|r|=%.3f" % abs(r_sc))
    print("  schema-fit x corrob(corrected)|r|=%.3f" % abs(r_kc))
    print("  (naive corrob for reference: surprise|r|=%.3f schema|r|=%.3f"
          " naive-vs-corrected r=%.3f)"
          % (abs(r_ss_n), abs(r_kc_n), pearson(naive, corrected)))
    max_abs_r = max(abs(r_ss), abs(r_sc), abs(r_kc))

    # -- (2) copying stress-test --
    print("\n--- (2) COPYING STRESS-TEST (matched raw-count, indep vs copies) ---")
    st = copying_stress_test(cfg, rng, clusters)
    print("  corrected: independent mean=%.2f  copied mean=%.2f  ratio=%.2fx  p=%.4f"
          % (st["corr_ind_mean"], st["corr_cop_mean"], st["corr_ratio"],
             st["corr_pvalue"]))
    print("  naive    : independent mean=%.2f  copied mean=%.2f  separation=%.2f"
          " (expected ~0 => naive FAILS by construction)"
          % (st["naive_ind_mean"], st["naive_cop_mean"], st["naive_separation"]))

    # -- (3) conditional MI with should-assimilate (= is_true) --
    target = G["truth"].astype(int)
    cmi_surprise = conditional_mi(-surprise, target, schema_fit, corrected)
    cmi_schema = conditional_mi(schema_fit, target, -surprise, corrected)
    cmi_corr = conditional_mi(corrected, target, -surprise, schema_fit)
    print("\n--- (3) CONDITIONAL MI WITH should-assimilate | OTHER TWO (nats) ---")
    print("  surprise    : %.4f" % cmi_surprise)
    print("  schema-fit  : %.4f" % cmi_schema)
    print("  corroboration: %.4f" % cmi_corr)
    n_signals_informative = sum(v > 1e-3 for v in
                                (cmi_surprise, cmi_schema, cmi_corr))
    print("  signals retaining conditional info (>1e-3): %d/3" % n_signals_informative)

    # -- verdict against pre-registered bands --
    print("\n" + "=" * 74)
    hard_pass = (max_abs_r < 0.3
                 and st["corr_ratio"] >= 1.5
                 and st["corr_pvalue"] < 0.05)
    hard_fail = (max_abs_r > 0.6
                 or st["corr_pvalue"] >= 0.05
                 or st["corr_ratio"] < 1.05)
    if hard_pass:
        verdict = "HARD-PASS"
    elif hard_fail:
        verdict = "HARD-FAIL"
    else:
        verdict = "MIDDLE"
    print("VERDICT BLOCK")
    print("  pairwise |r|: surprise-schema=%.3f surprise-corr=%.3f schema-corr=%.3f"
          " (max=%.3f, band<0.3)" % (abs(r_ss), abs(r_sc), abs(r_kc), max_abs_r))
    print("  copying stress: corrected %.2fx (indep>copied) p=%.4f; naive sep=%.2f"
          % (st["corr_ratio"], st["corr_pvalue"], st["naive_separation"]))
    print("  conditional-MI informative signals: %d/3" % n_signals_informative)
    print("  PRE-REG VERDICT: %s" % verdict)
    if verdict == "HARD-PASS":
        print("  CALL: GREENLIGHT the full multi-source arena build.")
    elif verdict == "HARD-FAIL":
        print("  CALL: REDESIGN -- arena still collapses signals; do not build yet.")
    else:
        print("  CALL: MIDDLE -- partial decorrelation; tune generator before build.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
