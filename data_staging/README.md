# Data Staging

Stage a directory that only exists on your machine onto the cluster, then fan
out over it. This is the only example here that starts from data instead of
generating it on the compute node.

`sample_data/observations.csv` holds 100 rows of `x,y`. Four chunk tasks each
summarize a disjoint quarter of the rows, and an aggregation task pools the
results into one OLS fit. The chunks exchange sufficient statistics
(n, Σx, Σy, Σxx, Σxy, Σyy), which add exactly, so the pooled answer is the same
one you would get fitting all 100 rows at once:

```
Intercept: 2.6782   Slope: 1.7644   R-squared: 0.9251
```

The compute is trivial on purpose. This example is about moving data.

## How staging works

ScriptHut hashes the *local* file list — relative paths and sizes, not file
contents — and copies the directory to `<scratch>/example-panel/<hash12>` on the
backend. Because the destination is derived from the hash:

- The first run transfers the data and shows a `_data.example-panel` item.
- Every later run finds the directory already there and skips the transfer
  entirely. No staging item appears at all.
- Editing the CSV changes the hash, so the next run stages a *new* copy beside
  the old one rather than overwriting it. Runs already referring to the old copy
  keep working.

Tasks find the data through `$DATA_DIR`, which ScriptHut sets when a workflow
declares exactly one dataset. `$DATA_EXAMPLE_PANEL` is always set and is what
you would use with more than one.

## Setup

Datasets are declared **user-global**, in `~/.config/scripthut/scripthut.yaml` —
not in this repo's `scripthut.yaml`, which would be rejected. That split is
deliberate: `path` describes your machine, so it cannot travel in a repo.

Add the dataset, editing `path` to point at *your* clone of this repository:

```yaml
datasets:
  - name: example-panel
    path: ~/Documents/GitHub/scripthut-examples/data_staging/sample_data
```

You may also need a scratch root. ScriptHut looks for the dataset's own `root`,
then a literal `SCRATCH` env rule on the backend, then the login shell's
`$SCRATCH`, and fails naming all three rather than guessing a path. If your
cluster does not export `$SCRATCH`, set one explicitly:

```yaml
datasets:
  - name: example-panel
    path: ~/Documents/GitHub/scripthut-examples/data_staging/sample_data
    root: /scratch/your-username/data   # literal path, no $VARS
```

## Run

```bash
RUN_ID=$(scripthut workflow run data_staging.json --source scripthut-examples --backend mercury --json | jq -r .id)
scripthut run watch "$RUN_ID" --exit-status
```

On the first run you will see `_data.example-panel` complete before `generate`
starts. Run it a second time and that item is gone — the copy is already there.

To watch re-staging happen, change a number in `sample_data/observations.csv`
and submit again: the hash changes, so a fresh copy is staged next to the first.
`scripthut disk scan` will then report the earlier copy as superseded, and
`scripthut disk clean` reclaims it.

## Do not write into `$DATA_DIR`

The staged copy is shared by every run whose data hashes the same, and its path
is a promise about its contents. Writing into it would break that promise for
runs that have already been told the data is present. Task output goes to the
working directory instead — here, `temp/` and `results.csv`.

## Run it locally

The scripts have no dependencies beyond the standard library, so you can check
them without a cluster:

```bash
cd data_staging
DATA_DIR="$PWD/sample_data" python3 summarize_chunk.py 0 4 temp
DATA_DIR="$PWD/sample_data" python3 summarize_chunk.py 1 4 temp
DATA_DIR="$PWD/sample_data" python3 summarize_chunk.py 2 4 temp
DATA_DIR="$PWD/sample_data" python3 summarize_chunk.py 3 4 temp
python3 aggregate.py temp
```

## Files

| File | Role |
|---|---|
| `sample_data/observations.csv` | The dataset — 100 rows, `x,y` |
| `generate_tasks.py` | Reports the staged dataset, then emits the chunk + aggregate tasks |
| `summarize_chunk.py` | Sufficient statistics for one slice of rows |
| `aggregate.py` | Pools the statistics into the OLS fit |

## A note on the committed CSV

Shipping the data in the repo keeps the example runnable straight after a clone,
but it does mean the git source carries the file to the cluster anyway. At 1.4 KB
that costs nothing, and the mechanism is what matters. The realistic use is a
dataset that is far too large to commit, living outside any repository — point
`path` at such a directory and nothing else about this example changes.
