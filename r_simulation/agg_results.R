# Aggregate simulation results from all individual runs.
#
# Usage: Rscript --vanilla agg_results.R <input_dir>
#
# Arguments:
#   input_dir - Directory containing res_*.csv files from gen_results.R
#
# Output: results.csv in the current working directory

args <- commandArgs(trailingOnly = TRUE)
input_dir <- args[1]

cat("Aggregating simulation results\n")
cat(sprintf("  Input directory: %s\n", input_dir))

# Read all result files
files <- list.files(path = input_dir, pattern = "^res_.*\\.csv$", full.names = TRUE)
cat(sprintf("  Found %d result files\n", length(files)))

if (length(files) == 0) {
    stop("No result files found!")
}

# Combine all results into one data frame
all_results <- do.call(rbind, lapply(files, read.csv))

# Compute aggregate statistics
n_reps <- nrow(all_results)
summary_result <- data.frame(
    n_simulations = n_reps,
    mean_estimation_error = mean(all_results$estimation_error),
    se_estimation_error = sd(all_results$estimation_error) / sqrt(n_reps),
    mean_r_squared = mean(all_results$r_squared),
    se_r_squared = sd(all_results$r_squared) / sqrt(n_reps)
)

# Save aggregated results
write.csv(summary_result, file = "results.csv", row.names = FALSE)

cat("\nAggregated Results:\n")
print(summary_result)
cat(sprintf("\nResults saved to: results.csv\n"))
