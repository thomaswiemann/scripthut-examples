# Local LLM server (vLLM)

Serve a local, OpenAI-compatible LLM as a ScriptHut job on a GPU node — no
bespoke feature needed, it's just a workflow. Submit
[`.hut/workflows/vllm_qwen.json`](../.hut/workflows/vllm_qwen.json); the job
stays running until you cancel it (or it hits `time_limit`).

This example is **excluded from `all.json`** on purpose: it is a long-running
GPU server, not a fan-out/fan-in simulation.

## Quick start

```bash
scripthut workflow run vllm_qwen.json \
  --source scripthut-examples --backend <your-gpu-backend>
```

Adjust `partition` / `gres` in the workflow for your cluster before the first
run. On Booth mercury the defaults are `gpu_h100` + `gpu:h100:1` (see
`sinfo`); other sites will differ.

## How it works

The single `serve` task:

1. Prints its endpoint to `$SCRIPTHUT_RUN_SUMMARY`, so the **run page shows**
   `OpenAI-compatible endpoint: http://<node>:8000/v1` once it's up.
2. Runs `vllm serve <model>` in the foreground — the job (and the GPU
   allocation) lives as long as the server does.

The `vllm` env group in the repo-root `scripthut.yaml` bootstraps a conda env
with vLLM on first use (idempotent — a no-op once the env exists). Replace that
bootstrap with your site's module / image / prebuilt env when you have one.

## Using the endpoint

The server listens on `http://<node>:8000/v1` (OpenAI-compatible). `--host
0.0.0.0` is deliberate here: peer jobs on the cluster need to reach the GPU
node. That is not the ScriptHut control plane.

- **From another cluster job / node**: use the `http://<node>:8000/v1` URL
  directly.
- **From your laptop**: forward the port, e.g.
  `ssh -N -L 8000:<node>:8000 <login-host>`, then use `http://localhost:8000/v1`.
- **Console/logs**: use ScriptHut's **Attach** button on the running job.

Point any OpenAI-compatible client at it
(`OPENAI_BASE_URL=http://<node>:8000/v1`, `OPENAI_API_KEY=dummy`).

## Adapt to your cluster

- **`partition` / `gres`** — defaults target Booth mercury (`gpu_h100`,
  `gpu:h100:1`). Change to your GPU partition and count (`"gpu:2"`,
  `"gpu:a100:1"`, …). Check with `sinfo` — a wrong combo fails at submit with
  "Requested node configuration is not available".
- **`vllm` env group** — the conda bootstrap in `scripthut.yaml` needs `conda`
  on the node. Mercury login/compute images may not have it; replace with a
  site module or an Apptainer/`image:` stack that already contains vLLM.
- **model** — change `Qwen/Qwen2.5-Coder-7B-Instruct` in the workflow; add
  flags like `--tensor-parallel-size N`, `--max-model-len`,
  `--gpu-memory-utilization`.
- **gated models** — add to the env group:
  `{ "set": { "HF_TOKEN": "${HF_TOKEN}" } }` (and put the token in the
  environment that launches ScriptHut).
- **presets** — add one `.hut/workflows/vllm_*.json` per model for a menu of
  launchable servers.
