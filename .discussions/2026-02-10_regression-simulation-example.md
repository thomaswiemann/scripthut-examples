# Replacing the Bivariate Normal Simulation with a Regression Simulation

**Date:** 2026-02-10

## Context

The current `r_simulation` example draws from a bivariate normal distribution
(`gen_results.R` generates 1M draws, computes means/SDs/correlation). This runs
in seconds on any compute node, so users can't really see ScriptHut managing
real work.

We want the example to demonstrate ScriptHut handling a pipeline where each task
takes meaningful wall-clock time (tens of seconds to minutes).

## Options Considered

### Option A: Increase `n_draws` in the existing example

- **Pro:** Minimal code changes.
- **Con:** Still conceptually trivial — drawing from `rnorm` doesn't showcase
  a real-world workload. We'd need billions of draws to eat meaningful time, and
  memory would become the bottleneck rather than compute.

### Option B: Monte Carlo comparison of regression estimators

Replace the bivariate normal draw with a proper regression Monte Carlo study:

1. **DGP** — Generate data from a linear model with `p` covariates, some
   irrelevant, with optional heteroskedasticity or correlation structure.
2. **Estimators** — Fit OLS, Ridge (CV), and Lasso (CV) on each replication.
   The cross-validation in `glmnet` is what drives real compute time.
3. **Metrics** — Each replication saves bias, RMSE, and coverage for each
   estimator.
4. **Aggregation** — Fan-in step computes average bias, RMSE, and coverage
   across replications.

- **Pro:** Genuinely compute-heavy (CV for penalized regression); mirrors
  real-world simulation studies; demonstrates that ScriptHut handles R packages
  beyond base R.
- **Con:** Requires `glmnet` (but it's available on most HPC R installations).

### Option C: Bootstrap inference simulation

Run a bootstrap for a nonparametric estimator.

- **Pro:** Naturally parallelizable, CPU-heavy.
- **Con:** Less interesting as a demo — the fan-out result is a single
  confidence interval, not a multi-estimator comparison table.

## Decision

**Option B — Monte Carlo regression estimator comparison.**

This is the most natural "regression simulation" that:
- Creates real compute load per task (cross-validation)
- Produces interesting output (estimator comparison table)
- Demonstrates ScriptHut managing a non-trivial pipeline
- Stays self-contained (only needs `glmnet`)

### Proposed DGP

```
Y = X %*% beta + epsilon

- n = 500 observations
- p = 200 covariates (X ~ N(0, Sigma) with Toeplitz correlation rho = 0.5)
- beta: first 10 coefficients = 1, rest = 0  (sparse)
- epsilon ~ N(0, 1)
```

### Proposed estimators

| Estimator | Method | Why it's expensive |
|-----------|--------|--------------------|
| OLS       | `lm()` | Baseline (fast) |
| Ridge     | `cv.glmnet(alpha=0)` | 10-fold CV |
| Lasso     | `cv.glmnet(alpha=1)` | 10-fold CV |

### Proposed metrics per replication

- Estimation error: `||beta_hat - beta||_2`
- Prediction error: `||X_test %*% (beta_hat - beta)||_2 / sqrt(n_test)`
- Support recovery (Lasso): true positive rate, false positive rate

### Task structure (unchanged fan-out/fan-in)

```
sflow.json
  └── generate (writes task JSON)
        ├── sim-0  ──┐
        ├── sim-1  ──┤
        ├── ...    ──┼──▶ aggregate
        ├── sim-98 ──┤
        └── sim-99 ──┘
```

Default count bump from 5 → 100 replications, to make the pipeline feel substantial.
