from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Job

router = APIRouter()

@router.get("/models/trained")
def get_trained_models(db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .filter(Job.status == "completed")
        .order_by(Job.id.desc())
        .all()
    )

    return [
        {
            "job_id": j.id,
            "base_model": j.base_model,
            "adapter_id": j.adapter_path.split("/")[-1] if j.adapter_path else None,
            "finished_at": j.updated_at,
        }
        for j in jobs
    ]
