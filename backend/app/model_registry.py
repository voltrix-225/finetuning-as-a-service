# backend/app/model_registry.py

BASE_MODELS = [
    # ---------- Tiny / CPU Testing Models ----------
    {
        "id": "tiny-gpt2",
        "hf_id": "sshleifer/tiny-gpt2",
        "description": "Tiny GPT-2 for testing (fast CPU)",
        "params": "15M",
        "recommended": "testing_only"
    },
    {
        "id": "distilgpt2",
        "hf_id": "distilgpt2",
        "description": "Distilled GPT-2 (small, good for demo CPU fine-tuning)",
        "params": "82M",
        "recommended": "cpu_ok"
    },

    # ---------- GPT-2 Variants ----------
    {
        "id": "gpt2",
        "hf_id": "gpt2",
        "description": "GPT-2 base model",
        "params": "124M",
        "recommended": "gpu_or_fast_cpu"
    },
    {
        "id": "gpt2-medium",
        "hf_id": "gpt2-medium",
        "description": "GPT-2 Medium",
        "params": "355M",
        "recommended": "gpu_required"
    },

    # ---------- LLaMA Family ----------
    {
        "id": "llama-3.2-1b",
        "hf_id": "meta-llama/Llama-3.2-1B",
        "description": "LLaMA 3.2 Small (good consumer GPU)",
        "params": "1B",
        "recommended": "gpu_6gb"
    },
    {
        "id": "llama-3.1-7b",
        "hf_id": "meta-llama/Llama-3.1-7B",
        "description": "LLaMA 3.1 7B",
        "params": "7B",
        "recommended": "gpu_16gb"
    },

    # ---------- Mistral Family ----------
    {
        "id": "mistral-7b",
        "hf_id": "mistralai/Mistral-7B-v0.1",
        "description": "Mistral 7B (efficient 7B model)",
        "params": "7B",
        "recommended": "gpu_16gb"
    },

    # ---------- Qwen Family ----------
    {
        "id": "qwen2.5-0.5b",
        "hf_id": "Qwen/Qwen2.5-0.5B",
        "description": "Qwen small model (great for CPU demo)",
        "params": "0.5B",
        "recommended": "cpu_or_gpu"
    },
    {
        "id": "qwen2.5-7b",
        "hf_id": "Qwen/Qwen2.5-7B",
        "description": "Qwen 2.5 7B",
        "params": "7B",
        "recommended": "gpu_16gb"
    },

    # ---------- Gemma Family ----------
    {
        "id": "gemma-2b",
        "hf_id": "google/gemma-2b",
        "description": "Gemma 2B",
        "params": "2B",
        "recommended": "gpu_8gb"
    },
    {
        "id": "gemma-7b",
        "hf_id": "google/gemma-7b",
        "description": "Gemma 7B",
        "params": "7B",
        "recommended": "gpu_16gb"
    },
]


def get_base_model_list():
    return BASE_MODELS
