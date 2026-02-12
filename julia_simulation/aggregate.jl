# Aggregate bootstrap results and compute confidence intervals.
#
# Usage: julia aggregate.jl <input_dir>
#
# Arguments:
#   input_dir - Directory containing res_*.csv files from bootstrap.jl
#
# Output: results.csv in the current working directory

using DelimitedFiles
using Statistics

input_dir = ARGS[1]

println("Aggregating bootstrap results")
println("  Input directory: $input_dir")

# Find all result files
files = filter(f -> startswith(f, "res_") && endswith(f, ".csv"), readdir(input_dir))
sort!(files)
println("  Found $(length(files)) result files")

if isempty(files)
    error("No result files found!")
end

# Read all results — extract estimation errors and first 3 coefficients
errors = Float64[]
betas_1 = Float64[]
betas_2 = Float64[]
betas_3 = Float64[]

for file in files
    path = joinpath(input_dir, file)
    lines = readlines(path)
    if length(lines) < 2
        continue
    end
    values = split(lines[2], ",")
    push!(errors, parse(Float64, values[2]))   # estimation_error
    push!(betas_1, parse(Float64, values[3]))   # beta_1
    push!(betas_2, parse(Float64, values[4]))   # beta_2
    push!(betas_3, parse(Float64, values[5]))   # beta_3
end

n_reps = length(errors)

# Compute bootstrap confidence intervals (percentile method)
function ci_95(x)
    sorted = sort(x)
    lo = sorted[max(1, Int(floor(0.025 * length(sorted))))]
    hi = sorted[min(length(sorted), Int(ceil(0.975 * length(sorted))))]
    return (lo, hi)
end

# Write summary
open("results.csv", "w") do io
    println(io, "variable,mean,std,ci_lower,ci_upper")
    for (name, vals) in [("beta_1", betas_1), ("beta_2", betas_2), ("beta_3", betas_3)]
        lo, hi = ci_95(vals)
        println(io, "$name,$(mean(vals)),$(std(vals)),$lo,$hi")
    end
    println(io, "estimation_error,$(mean(errors)),$(std(errors)),,")
end

println("\nBootstrap Results ($(n_reps) replications):")
println("  β₁: $(round(mean(betas_1), digits=4)) [$(round(ci_95(betas_1)[1], digits=4)), $(round(ci_95(betas_1)[2], digits=4))]")
println("  β₂: $(round(mean(betas_2), digits=4)) [$(round(ci_95(betas_2)[1], digits=4)), $(round(ci_95(betas_2)[2], digits=4))]")
println("  β₃: $(round(mean(betas_3), digits=4)) [$(round(ci_95(betas_3)[1], digits=4)), $(round(ci_95(betas_3)[2], digits=4))]")
println("  Mean estimation error: $(round(mean(errors), digits=6))")
println("\nResults saved to: results.csv")
