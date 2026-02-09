# Generate a single simulation draw from a bivariate normal distribution.
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

# Simulate: draw from bivariate normal
n_draws <- 100
x <- rnorm(n_draws, mean = -1, sd = 1)
y <- rnorm(n_draws, mean = 1, sd = 2)

# Compute summary statistics
result <- data.frame(
    seed = seed,
    mean_x = mean(x),
    mean_y = mean(y),
    sd_x = sd(x),
    sd_y = sd(y),
    cor_xy = cor(x, y),
    n = n_draws
)

# Save result
output_file <- file.path(output_dir, sprintf("res_%d.csv", seed))
write.csv(result, file = output_file, row.names = FALSE)

cat(sprintf("  Result saved to: %s\n", output_file))
cat(sprintf("Simulation %d complete\n", seed))
