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
summary_result <- data.frame(
    n_simulations = nrow(all_results),
    grand_mean_x = mean(all_results$mean_x),
    grand_mean_y = mean(all_results$mean_y),
    se_mean_x = sd(all_results$mean_x) / sqrt(nrow(all_results)),
    se_mean_y = sd(all_results$mean_y) / sqrt(nrow(all_results))
)

# Save aggregated results
write.csv(summary_result, file = "results.csv", row.names = FALSE)

cat("\nAggregated Results:\n")
print(summary_result)
cat(sprintf("\nResults saved to: results.csv\n"))
