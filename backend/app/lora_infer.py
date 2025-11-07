import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from peft import PeftModel


def generate_text(base_model: str, job_id: int, prompt: str):
    print(f"[INF] Inference started: model={base_model}, job={job_id}")

    # ✅ Adapter path
    adapter_path = f"/data/models/job_{job_id}/adapter"
    if not os.path.exists(adapter_path):
        raise FileNotFoundError(f"Adapter folder not found: {adapter_path}")

    # ✅ Use HF token if available (needed for LLaMA/Mistral/Qwen gated)
    token = os.getenv("HF_TOKEN")
    token_kwargs = {"use_auth_token": token} if token else {}

    # ✅ Load tokenizer safely
    tokenizer = AutoTokenizer.from_pretrained(base_model, **token_kwargs)

    # fix no pad token issue
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ✅ 4-bit memory efficient loading
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

    # ✅ Load base model
    print("[INF] Loading base model…")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        **token_kwargs
    )

    # ✅ Load LoRA adapter
    print("[INF] Loading LoRA adapter…")
    model = PeftModel.from_pretrained(
        model,
        adapter_path,
        **token_kwargs
    )

    model.eval()

    # ✅ Tokenize & move to correct device
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    print("[INF] Generating output…")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.8,
            do_sample=True,
            top_p=0.9
        )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    print("[INF] Inference complete")

    return text
