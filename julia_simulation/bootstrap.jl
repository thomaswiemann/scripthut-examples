# Bootstrap OLS regression on a simulated dataset.
#
# Usage: julia bootstrap.jl <seed> <output_dir>
#
# Arguments:
#   seed       - Integer seed for reproducibility
#   output_dir - Directory to write the result CSV
#
# Output: <output_dir>/res_<seed>.csv
#
# Uses only Julia stdlib: LinearAlgebra, DelimitedFiles, Random, Statistics.

using LinearAlgebra
using DelimitedFiles
using Random
using Statistics
using Dates

seed = parse(Int, ARGS[1])
output_dir = ARGS[2]

# Create output directory if it doesn't exist
if !isdir(output_dir)
    mkpath(output_dir)
end

println("Bootstrap replication $seed started")
println("  Hostname: $(gethostname())")
println("  Time: $(Dates.now())")


# ── DGP: Y = X * β + ε ──────────────────────────────────────────────

n = 500_000        # observations
K = 50             # regressors
β_true = range(-1, 1, length=K) |> collect

rng = MersenneTwister(seed)

X = randn(rng, n, K)
ε = randn(rng, n)
y = X * β_true + ε

# ── Bootstrap resample and fit OLS ───────────────────────────────────

# Draw bootstrap sample (resample with replacement)
boot_rng = MersenneTwister(seed + 1_000_000)
idx = rand(boot_rng, 1:n, n)
X_boot = X[idx, :]
y_boot = y[idx]

# OLS via the normal equations: β̂ = (X'X)⁻¹ X'y
β_hat = (X_boot' * X_boot) \ (X_boot' * y_boot)

# ── Save results ─────────────────────────────────────────────────────

# Write seed, estimation error, and all K coefficients
estimation_error = norm(β_hat - β_true)

output_file = joinpath(output_dir, "res_$(seed).csv")

open(output_file, "w") do io
    # Header
    coef_headers = join(["beta_$k" for k in 1:K], ",")
    println(io, "seed,estimation_error,$coef_headers")
    # Values
    coef_values = join(β_hat, ",")
    println(io, "$seed,$estimation_error,$coef_values")
end

println("  Estimation error: $(round(estimation_error, digits=6))")
println("  Result saved to: $output_file")
println("Bootstrap replication $seed complete")
