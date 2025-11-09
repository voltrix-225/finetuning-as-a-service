# backend/app/main.py
import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi.responses import FileResponse

from .lora_infer import generate_text
from .download import router as download_router
from .predict import router as predict_router
from .tasks import enqueue_training_job
from .routes import trained_models
from .models import Dataset, Job
from .config import settings
from .db import get_db, Base, engine, SessionLocal
from . import models, schemas, tasks
from .models_available import AVAILABLE_MODELS   # ✅ NEW LINE

Base.metadata.create_all(bind=engine)

# ensure directories
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.MODEL_DIR, exist_ok=True)

app = FastAPI(title=settings.APP_NAME)
app.include_router(predict_router)
app.include_router(download_router)
app.include_router(trained_models.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/models")  # ✅ NEW ENDPOINT
def get_models():
    return {"models": AVAILABLE_MODELS}


@app.post("/datasets/upload", response_model=schemas.DatasetOut)
async def upload_dataset(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    uid = str(uuid4())
    saved_name = f"{uid}_{file.filename}"
    path = os.path.join(settings.DATA_DIR, saved_name)
    with open(path, "wb") as f:
        f.write(contents)

    ds = models.Dataset(name=name, filename=saved_name, path=path)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


@app.post("/start_training/", response_model=schemas.JobOut)
def start_training(
    dataset_id: int = Form(...),
    base_model: str = Form(...),
    epochs: int = Form(1),
    db: Session = Depends(get_db),
):
    ds = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    job = models.Job(dataset_id=dataset_id, base_model=base_model, status="queued", epochs=epochs)
    db.add(job)
    db.commit()
    db.refresh(job)

    tasks.enqueue_training_job.delay(job.id)
    return job

@app.post("/job/")
def create_job(
    dataset_id: int = Form(...),
    base_model: str = Form(...),
    epochs: int = Form(...),
    db: Session = Depends(get_db)
):
    # verify dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return {"error": "Dataset not found"}

    # create job entry
    job = Job(
        dataset_id=dataset_id,
        base_model=base_model,
        epochs=epochs,
        status="queued"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # enqueue background training task
    enqueue_training_job.delay(job.id)

    return {"job_id": job.id, "status": job.status}\
    
@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).order_by(models.Job.id.desc()).all()
    return [
        {
            "id": j.id,
            "base_model": j.base_model,
            "status": j.status,
            "adapter_path": j.adapter_path
        }
        for j in jobs
    ]

@app.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/download/adapter/{job_id}")
def download_adapter(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job or not job.adapter_path:
        raise HTTPException(404, "Adapter not ready")

    path = job.adapter_path
    if not os.path.exists(path):
        raise HTTPException(404, "File missing")

    return FileResponse(path, filename=f"adapter_job_{job_id}.zip")
@app.post("/infer")
def infer(
    base_model: str = Form(...),
    adapter_job_id: int = Form(...),
    prompt: str = Form(...)
):
    try:
        output = generate_text(base_model, adapter_job_id, prompt)
        return {"response": output}

    except Exception as e:
        import traceback
        print("[ERR] Inference failed:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))