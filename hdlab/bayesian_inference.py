"""Bayesian inference + EM -- substrate-internal probabilistic primitives.

Per Director DECISION 24 Tier 2 Item 4 (parallel with Item 5): integrate
bayesian_inference + em_algorithm into hdlab/ as inference primitives.

Atoms grounded as executable:
  T2/bayesian_inference     -- posterior from prior + likelihood
  T2/em_algorithm           -- iterative MLE under latent variables
  T3/map_estimation         -- argmax posterior
  T3/conditional_probability (via Bayes update)
  T3/maximum_likelihood     (via EM)

Public API:
  bayes_update(prior, likelihood) -> posterior
  bayes_update_categorical(prior, likelihoods) -> normalized posterior
  map_estimate(posterior) -> argmax label
  EMMixture(K, n_features) -> fit, predict, log_likelihood
    (Gaussian mixture for clustering / latent-variable inference)

USER 11th rule: pure-Python + optional numpy fallback. No LLM/bge/torch.
USER 18th rule: refuses-when-no-evidence (zero-mass posterior raises;
no spurious predictions).

NO LLM. NO bge. NO torch.
"""
from __future__ import annotations

import math
from typing import Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============================================================
# Bayesian inference primitives
# ============================================================

def bayes_update(prior: float, likelihood: float, marginal: float | None = None) -> float:
    """Bayes' rule for a single hypothesis.

    P(H|E) = P(E|H) * P(H) / P(E)

    If marginal not provided, returns un-normalized posterior P(E|H)*P(H).
    """
    if prior < 0.0 or prior > 1.0:
        raise ValueError(f"prior must be in [0, 1]; got {prior}")
    if likelihood < 0.0:
        raise ValueError(f"likelihood must be non-negative; got {likelihood}")
    joint = prior * likelihood
    if marginal is None:
        return joint
    if marginal <= 0.0:
        # USER 18th rule: refuse zero-mass posterior
        raise ValueError(
            f"marginal P(E)={marginal} is non-positive; "
            "evidence has no support under prior; refuse update"
        )
    return joint / marginal


def bayes_update_categorical(
    prior: Sequence[float],
    likelihoods: Sequence[float],
) -> list[float]:
    """Bayes' rule for a categorical distribution.

    prior:        P(H_k), k=1..K
    likelihoods:  P(E|H_k), k=1..K
    Returns:      P(H_k|E), normalized

    USER 18th rule: refuses if total marginal is zero (no hypothesis has
    any support under the evidence).
    """
    if len(prior) != len(likelihoods):
        raise ValueError(
            f"prior length {len(prior)} != likelihoods length {len(likelihoods)}"
        )
    if not prior:
        raise ValueError("prior is empty")
    joint = [p * l for p, l in zip(prior, likelihoods)]
    marginal = sum(joint)
    if marginal <= 0.0:
        raise ValueError(
            "all hypotheses have zero posterior mass under this evidence; "
            "refuse update (USER 18th rule)"
        )
    return [j / marginal for j in joint]


def map_estimate(posterior: Sequence[float]) -> int:
    """MAP estimate: argmax of posterior distribution.

    Returns index k* = argmax_k P(H_k | E).
    Raises if posterior is empty.
    """
    if not posterior:
        raise ValueError("posterior is empty")
    best_idx = 0
    best_val = posterior[0]
    for i in range(1, len(posterior)):
        if posterior[i] > best_val:
            best_val = posterior[i]
            best_idx = i
    return best_idx


# ============================================================
# EM algorithm: Gaussian mixture (most-used latent-variable estimator)
# ============================================================

class EMMixture:
    """Gaussian mixture model via Expectation-Maximization.

    Atom: T2/em_algorithm

    Args:
        K: number of mixture components
        n_features: dimensionality of observations
        rng_seed: seed for initialization

    Methods:
        fit(X, max_iter=100, tol=1e-4) -- EM training
        predict_proba(X) -- soft assignments (responsibilities)
        predict(X) -- hard assignments (argmax responsibility)
        log_likelihood(X) -- total log-likelihood of X under fitted mixture
    """

    def __init__(self, K: int, n_features: int, rng_seed: int = 1024):
        if K < 1:
            raise ValueError(f"K must be >= 1; got {K}")
        if n_features < 1:
            raise ValueError(f"n_features must be >= 1; got {n_features}")
        if not HAS_NUMPY:
            raise RuntimeError("EMMixture requires numpy")
        self.K = K
        self.n_features = n_features
        self._rng = np.random.default_rng(rng_seed)
        self.weights_ = None  # shape (K,)
        self.means_ = None    # shape (K, n_features)
        self.covs_ = None     # shape (K, n_features, n_features)
        self._fitted = False

    def _initialize(self, X):
        """K-means-style init: random samples as means + spherical cov."""
        n = X.shape[0]
        idx = self._rng.choice(n, size=self.K, replace=False)
        self.means_ = X[idx].copy()
        self.weights_ = np.full(self.K, 1.0 / self.K)
        var = X.var(axis=0).mean()
        if var <= 0:
            var = 1.0
        self.covs_ = np.array([np.eye(self.n_features) * var for _ in range(self.K)])

    def _gaussian_pdf(self, X, mean, cov):
        """Multivariate Gaussian PDF in log space for numerical stability."""
        d = X.shape[1]
        diff = X - mean
        try:
            cov_inv = np.linalg.inv(cov + 1e-6 * np.eye(d))
            log_det = np.linalg.slogdet(cov + 1e-6 * np.eye(d))[1]
        except np.linalg.LinAlgError:
            return np.full(X.shape[0], -1e30)
        mahal = np.einsum("ij,jk,ik->i", diff, cov_inv, diff)
        log_pdf = -0.5 * (d * math.log(2 * math.pi) + log_det + mahal)
        return log_pdf

    def fit(self, X, max_iter: int = 100, tol: float = 1e-4) -> dict:
        """Run EM until convergence or max_iter.

        Returns dict with final log-likelihood + iterations.
        """
        X = np.asarray(X, dtype=float)
        if X.shape[1] != self.n_features:
            raise ValueError(
                f"X has {X.shape[1]} features; expected {self.n_features}"
            )
        self._initialize(X)
        prev_ll = -float("inf")
        n_iter = 0
        for n_iter in range(1, max_iter + 1):
            # E-step: compute responsibilities
            log_resp = np.zeros((X.shape[0], self.K))
            for k in range(self.K):
                log_resp[:, k] = (
                    math.log(self.weights_[k] + 1e-30)
                    + self._gaussian_pdf(X, self.means_[k], self.covs_[k])
                )
            log_norm = np.logaddexp.reduce(log_resp, axis=1)
            resp = np.exp(log_resp - log_norm[:, None])
            ll = float(log_norm.sum())

            # M-step
            Nk = resp.sum(axis=0)
            self.weights_ = Nk / X.shape[0]
            for k in range(self.K):
                if Nk[k] < 1e-10:
                    continue
                self.means_[k] = (resp[:, k:k+1] * X).sum(axis=0) / Nk[k]
                diff = X - self.means_[k]
                self.covs_[k] = (
                    (resp[:, k:k+1] * diff).T @ diff / Nk[k]
                    + 1e-6 * np.eye(self.n_features)
                )

            if abs(ll - prev_ll) < tol:
                break
            prev_ll = ll

        self._fitted = True
        return {"log_likelihood": prev_ll, "n_iter": n_iter, "converged": n_iter < max_iter}

    def predict_proba(self, X):
        if not self._fitted:
            raise RuntimeError("EMMixture must be fit before predict_proba")
        X = np.asarray(X, dtype=float)
        log_resp = np.zeros((X.shape[0], self.K))
        for k in range(self.K):
            log_resp[:, k] = (
                math.log(self.weights_[k] + 1e-30)
                + self._gaussian_pdf(X, self.means_[k], self.covs_[k])
            )
        log_norm = np.logaddexp.reduce(log_resp, axis=1)
        return np.exp(log_resp - log_norm[:, None])

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def log_likelihood(self, X):
        X = np.asarray(X, dtype=float)
        log_resp = np.zeros((X.shape[0], self.K))
        for k in range(self.K):
            log_resp[:, k] = (
                math.log(self.weights_[k] + 1e-30)
                + self._gaussian_pdf(X, self.means_[k], self.covs_[k])
            )
        return float(np.logaddexp.reduce(log_resp, axis=1).sum())


# ============================================================
# Live-query tests (DECISION 24 done-definition gate)
# ============================================================

def _live_query_test_bayes() -> dict:
    """Classic disease-test Bayes example."""
    # Prior: 1pct disease prevalence
    prior_disease = 0.01
    # Test: 99pct sensitivity, 95pct specificity
    p_pos_given_disease = 0.99
    p_pos_given_healthy = 0.05  # 1 - specificity
    # Posterior P(disease | positive test) via categorical Bayes
    prior = [prior_disease, 1 - prior_disease]
    likelihoods = [p_pos_given_disease, p_pos_given_healthy]
    posterior = bayes_update_categorical(prior, likelihoods)
    # Expected: ~0.167 (counter-intuitive low PPV because rare disease)
    return {
        "prior_disease": prior_disease,
        "p_pos_given_disease": p_pos_given_disease,
        "p_pos_given_healthy": p_pos_given_healthy,
        "posterior_disease_given_positive": posterior[0],
        "expected_posterior_approx": 0.167,
        "map_estimate": map_estimate(posterior),  # 0 = disease, 1 = healthy
    }


def _live_query_test_em() -> dict:
    """Cluster 2D Gaussian mixture via EM."""
    if not HAS_NUMPY:
        return {"skipped": "numpy not available"}
    rng = np.random.default_rng(0)
    # Three well-separated 2D Gaussians
    X1 = rng.normal(loc=[0, 0], scale=0.5, size=(60, 2))
    X2 = rng.normal(loc=[5, 5], scale=0.5, size=(60, 2))
    X3 = rng.normal(loc=[10, 0], scale=0.5, size=(60, 2))
    X = np.vstack([X1, X2, X3])
    model = EMMixture(K=3, n_features=2, rng_seed=42)
    fit_info = model.fit(X, max_iter=100)
    labels = model.predict(X)
    # Compute homogeneity-like metric: max cluster purity
    counts = [
        max(int((labels[i*60:(i+1)*60] == k).sum()) for k in range(3))
        for i in range(3)
    ]
    purity = sum(counts) / len(labels)
    return {
        "n_samples": 180,
        "K": 3,
        "log_likelihood": fit_info["log_likelihood"],
        "n_iter": fit_info["n_iter"],
        "purity": round(purity, 4),
    }


if __name__ == "__main__":
    print("=== BAYESIAN INFERENCE + EM -- DECISION 24 Item 4 live-query test ===")
    r1 = _live_query_test_bayes()
    print("Bayes (rare disease test):")
    print(f"  P(disease|positive) = {r1['posterior_disease_given_positive']:.4f} "
          f"(expected approx 0.17)")
    print(f"  MAP estimate (0=disease, 1=healthy) = {r1['map_estimate']}")
    assert abs(r1["posterior_disease_given_positive"] - 0.167) < 0.01, \
        "Bayes update wrong magnitude"
    assert r1["map_estimate"] == 1, "MAP should pick healthy (rare disease)"

    r2 = _live_query_test_em()
    print("\nEM (3-component 2D Gaussian mixture, 180 samples):")
    if "skipped" in r2:
        print(f"  SKIPPED: {r2['skipped']}")
    else:
        print(f"  log_likelihood = {r2['log_likelihood']:.4f}")
        print(f"  iterations     = {r2['n_iter']}")
        print(f"  cluster purity = {r2['purity']:.4f}")
        assert r2["purity"] >= 0.95, f"EM cluster purity {r2['purity']} below 0.95"

    print("\nLIVE QUERY PASS: bayesian_inference + EM primitives executable.")
