# backend/app/models_available.py

"""
List of supported base models users can fine-tune.
Ordered: tiny/testing → small GPUs → large GPUs.
"""

AVAILABLE_MODELS = [

    # -------- Tiny Models (CPU Testing) --------
    {"id": "sshleifer/tiny-gpt2", "name": "Tiny GPT-2 (Test/CPU)"},
    {"id": "distilgpt2", "name": "DistilGPT-2 (Small / CPU OK)"},

    # -------- GPT-2 Classic Series --------
    {"id": "gpt2", "name": "GPT-2 Base"},
    {"id": "gpt2-medium", "name": "GPT-2 Medium"},

    # -------- Meta / LLaMA --------
    {"id": "meta-llama/Llama-3.2-1B", "name": "LLaMA-3.2 1B (Light / Laptop GPU)"},
    {"id": "meta-llama/Llama-3.1-7B", "name": "LLaMA-3.1 7B"},

    # -------- Mistral --------
    {"id": "mistralai/Mistral-7B-v0.1", "name": "Mistral 7B"},

    # -------- Qwen (Newest) --------
    {"id": "Qwen/Qwen2.5-0.5B", "name": "Qwen-2.5 0.5B (CPU / Entry GPU)"},
    {"id": "Qwen/Qwen2.5-7B", "name": "Qwen-2.5 7B"},

    # -------- Gemma --------
    {"id": "google/gemma-2b", "name": "Gemma-2B"},
    {"id": "google/gemma-7b", "name": "Gemma-7B"},

    # -------- Falcon --------
    {"id": "tiiuae/falcon-7b", "name": "Falcon-7B"},

]
