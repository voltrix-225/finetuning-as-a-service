# backend/app/models_available.py

"""
List of supported base models users can fine-tune.
Ordered: tiny/testing → small GPUs → large GPUs.
"""

AVAILABLE_MODELS = [
    # -------- Tiny / Debug Models --------
    {"id": "sshleifer/tiny-gpt2", "name": "Tiny GPT-2 (Debug / CPU / Fastest)"},
    {"id": "distilgpt2", "name": "DistilGPT-2 (Small / CPU Friendly)"},

    # -------- GPT-2 Family (Stable & Lightweight) --------
    {"id": "gpt2", "name": "GPT-2 Base (124M)"},
    {"id": "gpt2-medium", "name": "GPT-2 Medium (345M)"},

    # -------- Microsoft Phi Series (Extremely High Quality) --------
    {"id": "microsoft/phi-1_5", "name": "Phi 1.5 (1.3B, Best Small LM)"},
    {"id": "microsoft/phi-2", "name": "Phi 2 (2.7B, High Quality, still fits QLoRA)"},

    # -------- Qwen (Small Only — fully open-source) --------
    {"id": "Qwen/Qwen2.5-0.5B", "name": "Qwen 2.5 (0.5B, CPU+Low GPU safe)"},
    {"id": "Qwen/Qwen2-1.5B", "name": "Qwen 2 (1.5B GPU Friendly)"},
    {"id": "Qwen/Qwen2.5-7B", "name": "Qwen-2.5 7B"},

    # -------- Stability / Falcon (Only small one is safe) --------
    {"id": "tiiuae/falcon-1b", "name": "Falcon 1B (Lightweight alternative)"},

    # -------- Mistral --------
    {"id": "mistralai/Mistral-7B-v0.1", "name": "Mistral 7B"},
]
