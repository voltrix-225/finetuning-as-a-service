# backend/app/tasks.py
from celery import Celery
from .config import settings
from .db import SessionLocal
from . import models
import traceback

celery_app = Celery("ftaas", broker=settings.BROKER_URL, backend=settings.RESULT_BACKEND)


@celery_app.task(bind=True)
def enqueue_training_job(self, job_id: int):
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return {"error": "job not found"}

        # update job status to running
        job.status = "running"
        db.add(job)
        db.commit()
        db.refresh(job)

        # Import training logic (worker will run this)
        from .lora_train import train_on_job

        adapter_path = train_on_job(job_id=job.id, dataset_id=job.dataset_id, base_model=job.base_model, epochs=job.epochs)

        job.adapter_path = adapter_path
        job.status = "completed"
        db.add(job)
        db.commit()
        return {"status": "ok", "adapter_path": adapter_path}
    except Exception as exc:
        # mark failed
        try:
            job = db.query(models.Job).filter(models.Job.id == job_id).first()
            if job:
                job.status = "failed"
                db.add(job)
                db.commit()
        except Exception:
            pass
        traceback.print_exc()
        raise self.retry(exc=exc, countdown=10, max_retries=1)
    finally:
        db.close()
