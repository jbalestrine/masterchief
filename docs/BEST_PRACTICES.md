Best Practices for MasterChief / Echo Chat

This short guide covers practical, immediate best practices for running local GGUF models, secure persona ingestion, logging, and next steps for production-grade fine-tuning.

1) Environment & prerequisites
- Use the project virtualenv: `venv\Scripts\Activate.ps1` (Windows PowerShell).
- Keep `requirements.txt` current; for native bindings you'll need `llama-cpp-python` and a built `llama.cpp`.

2) Installing `llama-cpp-python` (recommended for performance)
- Upgrade pip: `python -m pip install --upgrade pip setuptools wheel`
- Install: `pip install llama-cpp-python`
- Build `llama.cpp` per platform; on Windows follow the `llama.cpp` README (MSVC/CMake build). See upstream docs if build errors occur.

3) CPU-only usage
- Models will run on CPU but are slower; prefer smaller quantized GGUF models for responsiveness (4-bit quantized models like `*_q4_*` are common).
- Use `ECHO_MODEL_PATH` environment var to point at a specific GGUF file to avoid automatic discovery if desired.

4) Running the server (example)
- Start inside the project root with venv activated:

```powershell
& .\venv\Scripts\Activate.ps1
python -u main.py --port 8080
```

- Use test ports (8081, 8082) when iterating to avoid conflicts.

5) Health checks & quick verification
- List models: `GET http://127.0.0.1:8080/api/echo/models`
- Preload current model: `POST http://127.0.0.1:8080/api/echo/preload_model`
- Chat test: `POST http://127.0.0.1:8080/api/echo/chat` with JSON `{ "session_id":"test", "message":"Hello" }`

6) Secure uploading and persona ingestion
- Enforce server-side checks: allowed extensions (.txt, .jsonl), maximum size (e.g. 2–10MB), and filename sanitization.
- Store uploads in `data/personality/` and `data/echo_training/` with unique safe filenames (UUIDs + original suffix).
- Validate content: simple heuristics for JSONL (one JSON per line) and plain-text persona length limits.

7) Worker robustness & logging
- Keep model inference isolated in `echo/llm_worker.py` as done. Ensure:
  - All stdout is JSON-escaped or sanitized before parsing.
  - stderr and critical events are written to `logs/worker-debug.log`.
  - Implement rotating logs (Python `logging.handlers.RotatingFileHandler`).

8) Model selection persistence
- Persist selected model path to `data/echo_model.json` or in DB session meta. The `/api/echo/select_model` endpoint should update this and the running bot should pick it up without restart.

9) Fine-tuning recommendations
- CPU-only fine-tuning is very slow; prefer GPU. For LoRA/QLoRA use `transformers` + `peft` + `accelerate`.
- Validate training data and keep a compact dev set for quick iterations.
- Provide checkpointing and artifact storage under `data/models_output/<job_id>/`.

PEFT / LoRA Quick Start (optional, GPU recommended)
- Create a fresh virtualenv and install required packages:

```powershell
python -m venv venv-finetune
& .\venv-finetune\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install transformers accelerate peft bitsandbytes datasets
```

- Prepare your training data as JSONL or HF datasets. Keep a small dev set for quick iterations.
- Run a LoRA/PEFT training script (example pipelines are available in the Hugging Face docs). If you want, I can add a `tools/peft_train.py` wrapper that follows a recommended training recipe and reads the same `api/echo/train_model` parameters.

Notes:
- On Windows, GPU training with bitsandbytes may require CUDA and compatible drivers; building on CPU-only Windows is possible but extremely slow.
- If you call the server with `engine=peft` but the environment lacks `transformers`/`peft`, the API will return an install hint so you can set up the environment.

10) Tests & CI
- Add tests for:
  - Model discovery and `/api/echo/models` output.
  - Worker subprocess invocation and JSON parsing (simulate worker stdout).
  - Upload endpoints validation and ingestion flow.
- Add GitHub Actions (or equivalent) to run tests and lint on push.

11) Next steps (priority)
- Implement secure persona UI and apply/preview persona in the chat UI.
- Finish rotating logging and ensure `logs/worker-debug.log` is writable.
- Decide whether to install `llama-cpp-python`; if yes, follow step 2 and test with a small model.
- Replace training stub with a GPU-aware LoRA/QLoRA pipeline when resources permit.

If you want, I can now:
- Add server-side upload validation code and UI changes to manage personas, or
- Add an automated RotatingFileHandler logging config and wire `echo/llm_worker.py` stderr to `logs/worker-debug.log`, or
- Prepare a Windows-specific `llama.cpp` build/script and a `requirements-native.txt` with `llama-cpp-python` for you to install.

Tell me which of those you want next and I will implement it.