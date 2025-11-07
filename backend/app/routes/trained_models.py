# backend/app/routes/trained_models.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app import models

router = APIRouter()

@router.get("/models/trained")
def get_trained_models(db: Session = Depends(get_db)):
    """Return list of completed fine-tuning jobs and their adapter paths."""
    jobs = db.query(models.Job).filter(models.Job.status == "completed").all()

    return [
        {
            "job_id": job.id,
            "base_model": job.base_model,
            "dataset_id": job.dataset_id,
            "adapter_path": job.adapter_path or None,
            "status": job.status,
            "trained_at": getattr(job, "created_at", None),
        }
        for job in jobs
    ]
