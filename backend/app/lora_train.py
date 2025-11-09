import os
import json
import zipfile
import torch
import chardet
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, PeftModel, prepare_model_for_kbit_training
from datasets import Dataset

from .db import SessionLocal
from . import models


# -------- Detect encoding & read dataset safely -------
def read_text_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(enc, errors="ignore")


# -------- Choose LoRA target modules depending on model ------
def get_lora_target_modules(model_name):
    name = model_name.lower()

    # GPT-2 family
    if "gpt2" in name and "distil" not in name:
        return ["c_attn", "c_proj"]

    # DistilGPT2
    if "distilgpt2" in name:
        return ["c_attn", "c_proj"]

    # GPT-Neo family
    if "gpt-neo" in name:
        return ["attention.query_key_value"]

    # Pythia family
    if "pythia" in name:
        return ["q_proj", "k_proj", "v_proj"]

    # Phi-1.5 / Phi-2
    if "phi" in name:
        return ["q_proj", "k_proj", "v_proj", "o_proj"]

    # Qwen small models (GPT-like)
    if "qwen" in name:
        return ["c_attn", "c_proj"]

    # Falcon 1B
    if "falcon" in name:
        return ["query_key_value"]

    # LLaMA / Mistral / Gemma
    if "llama" in name or "mistral" in name or "gemma" in name:
        return ["q_proj", "k_proj", "v_proj", "o_proj"]
    
    else:
        return ["q_proj", "v_proj"]  # fallback-safe


# -------- Train on job ----------
def train_on_job(job_id: int, dataset_id: int, base_model: str, epochs: int):

    db = SessionLocal()
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    db.close()

    ds_path = dataset.path
    print(f"[job {job_id}] Loading dataset from {ds_path}")

    text = read_text_file(ds_path)
    dataset = Dataset.from_dict({"text": [text]})

    print(f"[job {job_id}] Loaded dataset, {len(dataset)} samples")

    # ------- GPU / CPU device check -------
    device_label = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[job {job_id}] CUDA: {torch.cuda.is_available()} | Device: {device_label}")

    # ------- Load tokenizer -------
    hf_token = os.getenv("HF_TOKEN")
    token_kwargs = {"use_auth_token": hf_token} if hf_token else {}

    tokenizer = AutoTokenizer.from_pretrained(base_model, **token_kwargs)
    model = AutoModelForCausalLM.from_pretrained(base_model, **token_kwargs)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id


    # ------- Tokenize dataset -------
    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=512)

    dataset = dataset.map(tokenize, batched=True)

    # ------- BitsAndBytes 4-bit QLoRA config -------
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    # ------- Load base model -------
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto"
    )

    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules=get_lora_target_modules(base_model),
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ------- Trainer settings -------
    output_dir = f"/data/models/job_{job_id}"
    os.makedirs(output_dir, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=epochs,
        logging_steps=5,
        save_strategy="no",
        bf16=torch.cuda.is_available(),
        fp16=not torch.cuda.is_available(),
        optim="paged_adamw_32bit"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    trainer.train()

    # ------- Save adapter -------
    adapter_path = os.path.join(output_dir, "adapter")
    model.save_pretrained(adapter_path)

    # ZIP LoRA weights for download
    zip_path = f"/data/models/job_{job_id}/adapter.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for root, _, files in os.walk(adapter_path):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, adapter_path)
                z.write(full, rel)

    print(f"[job {job_id}] ✅ Training completed. Adapter: {zip_path}")
    return zip_path
