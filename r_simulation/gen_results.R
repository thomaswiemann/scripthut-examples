# Run a single OLS regression on a high-dimensional design matrix.
#
# Usage: Rscript --vanilla gen_results.R <seed> <output_dir>
#
# Arguments:
#   seed       - Integer seed for reproducibility
#   output_dir - Directory to write the result CSV
#
# Output: <output_dir>/res_<seed>.csv

args <- commandArgs(trailingOnly = TRUE)
seed <- as.integer(args[1])
output_dir <- args[2]

# Create output directory if it doesn't exist
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}

# Set seed for reproducibility
set.seed(seed)

cat(sprintf("Simulation %d started\n", seed))
cat(sprintf("  Hostname: %s\n", Sys.info()["nodename"]))
cat(sprintf("  Time: %s\n", Sys.time()))

# DGP: Y = X %*% beta + epsilon
n <- 1000000
K <- 10000
beta_true <- seq(-1, 1, length.out = K)

X <- matrix(rnorm(n * K), nrow = n)
epsilon <- rnorm(n)
y <- X %*% beta_true + epsilon

# Fit OLS
fit <- lm.fit(X, y)
beta_hat <- fit$coefficients

# Compute summary statistics
result <- data.frame(
    seed = seed,
    estimation_error = sqrt(sum((beta_hat - beta_true)^2)),
    r_squared = 1 - sum(fit$residuals^2) / sum((y - mean(y))^2),
    n = n,
    K = K
)

# Save result
output_file <- file.path(output_dir, sprintf("res_%d.csv", seed))
write.csv(result, file = output_file, row.names = FALSE)

cat(sprintf("  Result saved to: %s\n", output_file))
cat(sprintf("Simulation %d complete\n", seed))
