"""
Module N - Database Models
SQLAlchemy ORM models for file ingestion and metadata storage
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    ForeignKey, Index, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FileIngest(Base):
    """
    Tracks all uploaded files and their processing status
    """
    __tablename__ = 'file_ingests'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys (optional - for future integration with Laser OS)
    project_id = Column(Integer, nullable=True, index=True)
    client_id = Column(Integer, nullable=True, index=True)
    
    # File Information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=False, index=True)  # 'dxf', 'lbrn2', 'pdf', 'excel', 'image'
    mime_type = Column(String(100), nullable=True)
    
    # Processing Information
    status = Column(String(20), nullable=False, default='pending', index=True)  # 'pending', 'processing', 'completed', 'failed'
    processing_mode = Column(String(20), default='AUTO')  # 'AUTO', 'dxf', 'pdf', 'excel', etc.
    confidence_score = Column(Float, nullable=True)  # 0.00 to 1.00
    
    # Extracted Metadata (Quick Access)
    detected_type = Column(String(50), nullable=True)
    client_code = Column(String(50), nullable=True, index=True)
    project_code = Column(String(100), nullable=True, index=True)
    part_name = Column(String(200), nullable=True)
    material = Column(String(100), nullable=True, index=True)
    thickness_mm = Column(Float, nullable=True, index=True)
    quantity = Column(Integer, default=1)
    version = Column(Integer, default=1)
    
    # Error Handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    extractions = relationship("FileExtraction", back_populates="file_ingest", cascade="all, delete-orphan")
    file_metadata = relationship("FileMetadata", back_populates="file_ingest", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FileIngest(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'status': self.status,
            'processing_mode': self.processing_mode,
            'confidence_score': self.confidence_score,
            'detected_type': self.detected_type,
            'client_code': self.client_code,
            'project_code': self.project_code,
            'part_name': self.part_name,
            'material': self.material,
            'thickness_mm': self.thickness_mm,
            'quantity': self.quantity,
            'version': self.version,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }


class FileExtraction(Base):
    """
    Stores raw extraction data from parsers (JSON format)
    """
    __tablename__ = 'file_extractions'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    file_ingest_id = Column(Integer, ForeignKey('file_ingests.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Extraction Information
    extraction_type = Column(String(50), nullable=False, index=True)  # 'dxf_metadata', 'pdf_text', 'excel_data', etc.
    extracted_data = Column(Text, nullable=False)  # JSON format
    confidence_score = Column(Float, nullable=True)
    
    # Parser Information
    parser_version = Column(String(20), nullable=True)
    parser_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    file_ingest = relationship("FileIngest", back_populates="extractions")
    
    def __repr__(self):
        return f"<FileExtraction(id={self.id}, type='{self.extraction_type}', file_ingest_id={self.file_ingest_id})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'file_ingest_id': self.file_ingest_id,
            'extraction_type': self.extraction_type,
            'extracted_data': self.extracted_data,
            'confidence_score': self.confidence_score,
            'parser_version': self.parser_version,
            'parser_name': self.parser_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FileMetadata(Base):
    """
    Normalized key-value pairs for fast querying
    """
    __tablename__ = 'file_metadata'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    file_ingest_id = Column(Integer, ForeignKey('file_ingests.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Metadata
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=True)
    data_type = Column(String(20), default='string')  # 'string', 'number', 'boolean', 'date', 'json'
    
    # Source Information
    source = Column(String(50), nullable=True)  # 'filename', 'dxf_parser', 'pdf_parser', 'user_override', etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    file_ingest = relationship("FileIngest", back_populates="file_metadata")
    
    def __repr__(self):
        return f"<FileMetadata(id={self.id}, key='{self.key}', value='{self.value}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'file_ingest_id': self.file_ingest_id,
            'key': self.key,
            'value': self.value,
            'data_type': self.data_type,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# Indexes for performance
Index('idx_file_ingests_status', FileIngest.status)
Index('idx_file_ingests_client_code', FileIngest.client_code)
Index('idx_file_ingests_project_code', FileIngest.project_code)
Index('idx_file_ingests_material', FileIngest.material)
Index('idx_file_ingests_thickness', FileIngest.thickness_mm)
Index('idx_file_ingests_file_type', FileIngest.file_type)
Index('idx_file_ingests_is_deleted', FileIngest.is_deleted)

Index('idx_file_extractions_ingest', FileExtraction.file_ingest_id)
Index('idx_file_extractions_type', FileExtraction.extraction_type)

Index('idx_file_metadata_ingest', FileMetadata.file_ingest_id)
Index('idx_file_metadata_key', FileMetadata.key)

