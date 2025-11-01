# backend/app/predict.py
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .db import SessionLocal
from . import models
from .config import settings

router = APIRouter()

# Global model caches (RAM)
LOADED_MODELS = {}        # base_model -> (tokenizer, model)
LOADED_ADAPTERS = {}      # (base_model, job_id) -> adapter-applied model

class PredictReq(BaseModel):
    job_id: int
    text: str


@router.post("/predict/")
async def predict(req: PredictReq):
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == req.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        base_model = job.base_model
        adapter_zip = job.adapter_path  # ✅ avoid undefined variable

        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # ---- Load base model from cache or HF ----
        if base_model not in LOADED_MODELS:
            print(f"[PREDICT] Loading base model: {base_model}")
            from transformers import AutoTokenizer, AutoModelForCausalLM

            tokenizer = AutoTokenizer.from_pretrained(
                base_model,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                cache_dir=settings.MODEL_CACHE_DIR,
                low_cpu_mem_usage=True
            ).to(device)

            LOADED_MODELS[base_model] = (tokenizer, model)
        else:
            tokenizer, model = LOADED_MODELS[base_model]

        # ---- Load LoRA adapter if exists ----
        key = (base_model, job.id)

        if adapter_zip and os.path.exists(adapter_zip):
            if key not in LOADED_ADAPTERS:
                print(f"[PREDICT] Loading LoRA adapter for job {job.id} from {adapter_zip}")
                try:
                    import tempfile, zipfile, shutil
                    from peft import PeftModel

                    temp_dir = tempfile.mkdtemp()
                    with zipfile.ZipFile(adapter_zip, "r") as z:
                        z.extractall(temp_dir)

                    lora_model = PeftModel.from_pretrained(model, temp_dir).to(device)
                    LOADED_ADAPTERS[key] = lora_model

                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"[PREDICT] Warning: failed to load LoRA adapter, using base model -> {e}")
                    LOADED_ADAPTERS[key] = model

            model = LOADED_ADAPTERS[key]
        else:
            print("[PREDICT] No adapter found — using base model")
            model = LOADED_MODELS[base_model][1]

        # ---- Run inference ----
        inputs = tokenizer(req.text, return_tensors="pt").to(device)
        output = model.generate(
            **inputs,
            max_new_tokens=80,
            temperature=0.7,
            do_sample=True
        )
        reply = tokenizer.decode(output[0], skip_special_tokens=True)
        return {"input": req.text, "output": reply}

    finally:
        db.close()
