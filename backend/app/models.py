# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .db import Base


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    filename = Column(String(512), nullable=False)
    path = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, nullable=False)
    base_model = Column(String(256), nullable=False)
    status = Column(String(50), nullable=False, default="queued")  # queued, running, completed, failed
    adapter_path = Column(String(1024), nullable=True)
    epochs = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
