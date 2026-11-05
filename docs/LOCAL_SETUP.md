# Local zero-API-fee setup

This mode runs a DeepSeek R1 model on the developer's own machine through Ollama. The model itself is downloaded once; inference does not call a paid model API. Hardware and electricity costs still apply.

## Install and start

1. Install Ollama for your operating system from https://ollama.com.
2. Start the Ollama service.
3. Pull the model: `ollama pull deepseek-r1:8b`.
4. Verify the model: `ollama list`.
5. Create a Python virtual environment and install `requirements.txt`.
6. Copy `.env.example` to `.env`; the local endpoint, model and local placeholder key are preconfigured.
7. Add a fine-grained GitHub token with Contents: Read-only and Pull requests: Read-only for the 11 project repositories.
8. Run `uvicorn superagent.main:app --host 127.0.0.1 --port 8787`.
9. Open `http://127.0.0.1:8787`.

## Hardware note

The 8B model requires several GB of available RAM/VRAM and may run slowly on CPU-only machines. If it does not fit, select a smaller DeepSeek distilled model available in Ollama and set `LLM_MODEL` accordingly. Keep the endpoint local.

## Optional cloud endpoint

To use DeepSeek's hosted API instead, set `LLM_BASE_URL=https://api.deepseek.com`, provide a real `LLM_API_KEY`, and set `LLM_MODEL=deepseek-chat`. This can incur usage charges; local Ollama remains the no-provider-fee option.

## GitHub access

The current MVP only reads repository metadata, open pull requests and branch names. It does not read private source files, write branches, create pull requests or merge code. Keep GitHub writes disabled.
