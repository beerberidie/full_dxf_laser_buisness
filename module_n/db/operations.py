"""
Module N - Database Operations
CRUD operations for file ingestion and metadata storage
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, FileIngest, FileExtraction, FileMetadata
from ..config import get_database_url
from ..models.schemas import NormalizedMetadata

# Configure logging
logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionFactory = None


def init_db(database_url: Optional[str] = None) -> None:
    """
    Initialize database connection and create tables
    
    Args:
        database_url: Database URL (defaults to config)
    """
    global _engine, _SessionFactory
    
    if database_url is None:
        database_url = get_database_url()
    
    logger.info(f"Initializing database: {database_url}")
    
    # Create engine
    _engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,  # Verify connections before using
        connect_args={'check_same_thread': False} if 'sqlite' in database_url else {}
    )
    
    # Create session factory
    _SessionFactory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    
    # Create all tables
    Base.metadata.create_all(_engine)
    logger.info("Database tables created successfully")


def get_session() -> Session:
    """
    Get a new database session
    
    Returns:
        SQLAlchemy Session object
    """
    if _SessionFactory is None:
        init_db()
    
    return _SessionFactory()


def save_file_ingest(
    normalized_metadata: NormalizedMetadata,
    original_filename: str,
    stored_filename: str,
    file_path: str,
    status: str = 'completed',
    project_id: Optional[int] = None,
    client_id: Optional[int] = None
) -> Optional[FileIngest]:
    """
    Save file ingest record to database

    Args:
        normalized_metadata: Normalized metadata from parser
        original_filename: Original uploaded filename
        stored_filename: Normalized filename for storage
        file_path: Path where file is stored
        status: Processing status
        project_id: Optional project ID
        client_id: Optional client ID

    Returns:
        FileIngest object or None on error
    """
    session = get_session()

    try:
        # Create file ingest record
        file_ingest = FileIngest(
            project_id=project_id,
            client_id=client_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=normalized_metadata.file_size,
            file_type=normalized_metadata.detected_type.value if normalized_metadata.detected_type else 'unknown',
            mime_type=normalized_metadata.mime_type,
            status=status,
            processing_mode='AUTO',
            confidence_score=normalized_metadata.confidence_score,
            detected_type=normalized_metadata.detected_type.value if normalized_metadata.detected_type else None,
            client_code=normalized_metadata.client_code,
            project_code=normalized_metadata.project_code,
            part_name=normalized_metadata.part_name,
            material=normalized_metadata.material,
            thickness_mm=normalized_metadata.thickness_mm,
            quantity=normalized_metadata.quantity,
            version=normalized_metadata.version,
            processed_at=datetime.utcnow() if status == 'completed' else None
        )
        
        session.add(file_ingest)
        session.commit()
        session.refresh(file_ingest)
        
        logger.info(f"Saved file ingest: {file_ingest.id} - {original_filename}")
        return file_ingest
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving file ingest: {e}")
        return None
    finally:
        session.close()


def save_file_extraction(
    file_ingest_id: int,
    extraction_type: str,
    extracted_data: Dict[str, Any],
    confidence_score: Optional[float] = None,
    parser_name: Optional[str] = None,
    parser_version: Optional[str] = None
) -> Optional[FileExtraction]:
    """
    Save raw extraction data to database
    
    Args:
        file_ingest_id: ID of the file ingest record
        extraction_type: Type of extraction (e.g., 'dxf_metadata', 'pdf_text')
        extracted_data: Raw extracted data (will be JSON serialized)
        confidence_score: Confidence score
        parser_name: Name of the parser
        parser_version: Version of the parser
    
    Returns:
        FileExtraction object or None on error
    """
    session = get_session()
    
    try:
        # Serialize extracted data to JSON
        extracted_json = json.dumps(extracted_data, default=str)
        
        # Create extraction record
        extraction = FileExtraction(
            file_ingest_id=file_ingest_id,
            extraction_type=extraction_type,
            extracted_data=extracted_json,
            confidence_score=confidence_score,
            parser_name=parser_name,
            parser_version=parser_version
        )
        
        session.add(extraction)
        session.commit()
        session.refresh(extraction)
        
        logger.info(f"Saved extraction: {extraction.id} for file {file_ingest_id}")
        return extraction
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving extraction: {e}")
        return None
    finally:
        session.close()


def save_file_metadata(
    file_ingest_id: int,
    metadata_dict: Dict[str, Any],
    source: str = 'parser'
) -> bool:
    """
    Save metadata key-value pairs to database
    
    Args:
        file_ingest_id: ID of the file ingest record
        metadata_dict: Dictionary of metadata key-value pairs
        source: Source of the metadata
    
    Returns:
        True on success, False on error
    """
    session = get_session()
    
    try:
        for key, value in metadata_dict.items():
            if value is None:
                continue
            
            # Determine data type
            if isinstance(value, bool):
                data_type = 'boolean'
                value_str = str(value)
            elif isinstance(value, (int, float)):
                data_type = 'number'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                data_type = 'json'
                value_str = json.dumps(value, default=str)
            else:
                data_type = 'string'
                value_str = str(value)
            
            # Create metadata record
            metadata = FileMetadata(
                file_ingest_id=file_ingest_id,
                key=key,
                value=value_str,
                data_type=data_type,
                source=source
            )
            
            session.add(metadata)
        
        session.commit()
        logger.info(f"Saved {len(metadata_dict)} metadata entries for file {file_ingest_id}")
        return True
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving metadata: {e}")
        return False
    finally:
        session.close()


def get_file_ingest(file_id: int, include_deleted: bool = False) -> Optional[FileIngest]:
    """
    Get a file ingest record by ID

    Args:
        file_id: File ingest ID
        include_deleted: Whether to include soft-deleted records

    Returns:
        FileIngest object or None if not found
    """
    session = get_session()

    try:
        query = session.query(FileIngest).options(
            joinedload(FileIngest.extractions),
            joinedload(FileIngest.file_metadata)
        ).filter(FileIngest.id == file_id)

        if not include_deleted:
            query = query.filter(FileIngest.is_deleted == False)

        file_ingest = query.first()

        # Expunge from session to avoid detached instance errors
        if file_ingest:
            session.expunge(file_ingest)

        return file_ingest

    except SQLAlchemyError as e:
        logger.error(f"Error getting file ingest: {e}")
        return None
    finally:
        session.close()


def get_file_ingests(
    client_code: Optional[str] = None,
    project_code: Optional[str] = None,
    file_type: Optional[str] = None,
    material: Optional[str] = None,
    thickness_mm: Optional[float] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    include_deleted: bool = False
) -> List[FileIngest]:
    """
    Get file ingest records with optional filters

    Args:
        client_code: Filter by client code
        project_code: Filter by project code
        file_type: Filter by file type
        material: Filter by material
        thickness_mm: Filter by thickness
        status: Filter by status
        limit: Maximum number of records to return
        offset: Number of records to skip
        include_deleted: Whether to include soft-deleted records

    Returns:
        List of FileIngest objects
    """
    session = get_session()

    try:
        query = session.query(FileIngest)

        # Apply filters
        if not include_deleted:
            query = query.filter(FileIngest.is_deleted == False)

        if client_code:
            query = query.filter(FileIngest.client_code == client_code)

        if project_code:
            query = query.filter(FileIngest.project_code == project_code)

        if file_type:
            query = query.filter(FileIngest.file_type == file_type)

        if material:
            query = query.filter(FileIngest.material == material)

        if thickness_mm is not None:
            query = query.filter(FileIngest.thickness_mm == thickness_mm)

        if status:
            query = query.filter(FileIngest.status == status)

        # Order by created_at descending
        query = query.order_by(FileIngest.created_at.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        file_ingests = query.all()
        return file_ingests

    except SQLAlchemyError as e:
        logger.error(f"Error getting file ingests: {e}")
        return []
    finally:
        session.close()


def update_file_ingest(
    file_id: int,
    **kwargs
) -> Optional[FileIngest]:
    """
    Update a file ingest record

    Args:
        file_id: File ingest ID
        **kwargs: Fields to update

    Returns:
        Updated FileIngest object or None on error
    """
    session = get_session()

    try:
        file_ingest = session.query(FileIngest).filter(FileIngest.id == file_id).first()

        if not file_ingest:
            logger.warning(f"File ingest {file_id} not found")
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(file_ingest, key):
                setattr(file_ingest, key, value)

        # Update timestamp
        file_ingest.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(file_ingest)

        logger.info(f"Updated file ingest: {file_id}")
        return file_ingest

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating file ingest: {e}")
        return None
    finally:
        session.close()


def delete_file_ingest(file_id: int, hard_delete: bool = False) -> bool:
    """
    Delete a file ingest record (soft delete by default)

    Args:
        file_id: File ingest ID
        hard_delete: If True, permanently delete; if False, soft delete

    Returns:
        True on success, False on error
    """
    session = get_session()

    try:
        file_ingest = session.query(FileIngest).filter(FileIngest.id == file_id).first()

        if not file_ingest:
            logger.warning(f"File ingest {file_id} not found")
            return False

        if hard_delete:
            # Permanently delete
            session.delete(file_ingest)
            logger.info(f"Hard deleted file ingest: {file_id}")
        else:
            # Soft delete
            file_ingest.is_deleted = True
            file_ingest.updated_at = datetime.utcnow()
            logger.info(f"Soft deleted file ingest: {file_id}")

        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error deleting file ingest: {e}")
        return False
    finally:
        session.close()


def re_extract_file(file_id: int) -> Optional[FileIngest]:
    """
    Mark a file for re-extraction

    Args:
        file_id: File ingest ID

    Returns:
        Updated FileIngest object or None on error
    """
    return update_file_ingest(
        file_id,
        status='pending',
        retry_count=FileIngest.retry_count + 1,
        error_message=None
    )

