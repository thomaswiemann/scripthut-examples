# Local LLM server (vLLM)

Serve a local, OpenAI-compatible LLM as a ScriptHut job on a GPU node — no bespoke
feature needed, it's just a workflow. Launch [`hut.vllm_qwen.json`](hut.vllm_qwen.json)
with **New Run**; the job stays running until you cancel it (or it hits `time_limit`).

## How it works

The single `serve` task:

1. Prints its endpoint to `$SCRIPTHUT_RUN_SUMMARY`, so the **run page shows**
   `OpenAI-compatible endpoint: http://<node>:8000/v1` once it's up.
2. Runs `vllm serve <model>` in the foreground — the job (and the GPU allocation)
   lives as long as the server does.

The `vllm` env_group bootstraps a conda env with vLLM on first use (idempotent —
a no-op once the env exists).

## Using the endpoint

The server listens on `http://<node>:8000/v1` (OpenAI-compatible). To reach it:

- **From another cluster job / node**: use the `http://<node>:8000/v1` URL directly.
- **From your laptop**: forward the port, e.g.
  `ssh -N -L 8000:<node>:8000 <login-host>`, then use `http://localhost:8000/v1`.
- **Console/logs**: use ScriptHut's **Attach** button on the running job.

Point any OpenAI-compatible client at it (`OPENAI_BASE_URL=http://<node>:8000/v1`,
`OPENAI_API_KEY=dummy`), including coding agents such as `aider`. To drive Claude
Code with it you'd need an Anthropic↔OpenAI shim (e.g. LiteLLM) in front — out of
scope here.

## Adapt to your cluster

This example is intentionally cluster-agnostic — adjust before running:

- **`partition` / `gres`** — set to your GPU partition and GPU count (`"gpu:2"`, `"gpu:a100:1"`, …).
- **`env_group`** — replace the conda bootstrap with your site's way of getting vLLM
  (a module load, a prebuilt env, an Apptainer image, …).
- **model** — change `Qwen/Qwen2.5-Coder-7B-Instruct` to any HF model; add flags like
  `--tensor-parallel-size N`, `--max-model-len`, `--gpu-memory-utilization`.
- **gated models** — add an `HF_TOKEN` to the env_group:
  `{ "set": { "HF_TOKEN": "${HF_TOKEN}" } }`.
- **presets** — drop in one `hut.*.json` per model to build a menu of launchable models.
