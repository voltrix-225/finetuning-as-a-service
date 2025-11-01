# backend/app/download.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from .db import SessionLocal
from . import models
import os

router = APIRouter()

@router.get("/download/{job_id}")
def download_adapter(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if not job.adapter_path or not os.path.exists(job.adapter_path):
            raise HTTPException(status_code=400, detail="Adapter not ready or missing")

        return FileResponse(
            path=job.adapter_path,
            filename=f"job_{job_id}_adapter.zip",
            media_type="application/zip"
        )
    finally:
        db.close()
