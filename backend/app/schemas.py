# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DatasetCreate(BaseModel):
    name: str


class DatasetOut(BaseModel):
    id: int
    name: str
    filename: str
    path: str
    uploaded_at: datetime

    class Config:
        orm_mode = True


class JobCreate(BaseModel):
    dataset_id: int
    base_model: str
    epochs: Optional[int] = 1


class JobOut(BaseModel):
    id: int
    dataset_id: int
    base_model: str
    status: str
    adapter_path: Optional[str]
    epochs: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
