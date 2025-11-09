"""
Module N - Main FastAPI Application
File Ingest & Extract System for Laser OS
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from pathlib import Path
import tempfile
import shutil

from .models import (
    FileIngestResponse,
    IngestStatusResponse,
    ProcessingStatus,
    FileType
)
from .utils import validate_file, detect_file_type, generate_filename
from .parsers import DXFParser, PDFParser, ExcelParser, LBRNParser, ImageParser
from .config import settings
from .db import (
    init_db,
    save_file_ingest,
    save_file_extraction,
    save_file_metadata,
    get_file_ingest,
    get_file_ingests,
    update_file_ingest,
    delete_file_ingest,
    re_extract_file
)
from .storage import save_file, get_file_path, delete_file as delete_stored_file
from .webhooks import send_webhook, WebhookEventType
from .webhooks.monitor import get_webhook_monitor
from .webhooks.queue import get_webhook_queue

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Module N - File Ingest & Extract",
    description="Intelligent file ingestion and metadata extraction for Laser OS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Module N starting up...")
    logger.info(f"Upload folder: {settings.UPLOAD_FOLDER}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Create upload folder if it doesn't exist
    upload_path = Path(settings.UPLOAD_FOLDER)
    upload_path.mkdir(parents=True, exist_ok=True)

    # Create logs folder if it doesn't exist
    log_path = Path(settings.LOG_FILE).parent
    log_path.mkdir(parents=True, exist_ok=True)

    logger.info("Module N startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Module N shutting down...")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Module N - File Ingest & Extract",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "ingest": "POST /ingest",
            "status": "GET /ingest/{ingest_id}",
            "re_extract": "POST /extract/{ingest_id}",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "module-n",
        "version": "1.0.0",
        "upload_folder": settings.UPLOAD_FOLDER,
        "database": settings.DATABASE_URL
    }


@app.post("/ingest", response_model=List[FileIngestResponse])
async def ingest_files(
    files: List[UploadFile] = File(...),
    client_code: Optional[str] = Form(None),
    project_code: Optional[str] = Form(None),
    mode: str = Form("AUTO"),
    override_metadata: Optional[str] = Form(None)
):
    """
    Ingest one or more files and extract metadata.
    
    Args:
        files: List of uploaded files
        client_code: Optional client code (e.g., "CL-0001")
        project_code: Optional project code (e.g., "JB-2025-10-CL0001-001")
        mode: Processing mode (AUTO, dxf, pdf, excel, etc.)
        override_metadata: JSON string with metadata overrides
    
    Returns:
        List of FileIngestResponse objects
    """
    logger.info(f"Ingesting {len(files)} file(s)")
    logger.info(f"Client code: {client_code}, Project code: {project_code}, Mode: {mode}")
    
    results = []

    for file in files:
        temp_file_path = None
        try:
            logger.info(f"Processing file: {file.filename}")

            # Validate file
            validation_result = await validate_file(file)
            if not validation_result['valid']:
                logger.warning(f"Validation failed for {file.filename}: {validation_result['error']}")
                results.append(FileIngestResponse(
                    success=False,
                    filename=file.filename,
                    status=ProcessingStatus.FAILED,
                    error=validation_result['error']
                ))
                continue

            # Detect file type
            file_type = detect_file_type(file.filename, mode)
            logger.info(f"Detected file type: {file_type} for {file.filename}")

            # Process file based on type
            metadata = None
            normalized_filename = None

            if file_type == "dxf":
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as temp_file:
                        temp_file_path = temp_file.name
                        # Reset file pointer and copy content
                        await file.seek(0)
                        content = await file.read()
                        temp_file.write(content)

                    # Parse DXF file
                    parser = DXFParser()
                    metadata = parser.parse(temp_file_path, file.filename, client_code, project_code)

                    # Generate normalized filename
                    normalized_filename = generate_filename(metadata)

                    logger.info(f"DXF parsed successfully. Confidence: {metadata.confidence_score:.2f}")
                    logger.info(f"Generated filename: {normalized_filename}")

                except Exception as parse_error:
                    logger.error(f"DXF parsing error: {str(parse_error)}", exc_info=True)
                    results.append(FileIngestResponse(
                        success=False,
                        filename=file.filename,
                        status=ProcessingStatus.FAILED,
                        error=f"DXF parsing failed: {str(parse_error)}"
                    ))
                    continue
                finally:
                    # Clean up temp file
                    if temp_file_path and Path(temp_file_path).exists():
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass

            elif file_type == "pdf":
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                        temp_file_path = temp_file.name
                        # Reset file pointer and copy content
                        await file.seek(0)
                        content = await file.read()
                        temp_file.write(content)

                    # Parse PDF file
                    parser = PDFParser()
                    metadata = parser.parse(temp_file_path, file.filename, client_code, project_code)

                    # Generate normalized filename
                    normalized_filename = generate_filename(metadata)

                    logger.info(f"PDF parsed successfully. Confidence: {metadata.confidence_score:.2f}")
                    logger.info(f"Generated filename: {normalized_filename}")

                except Exception as parse_error:
                    logger.error(f"PDF parsing error: {str(parse_error)}", exc_info=True)
                    results.append(FileIngestResponse(
                        success=False,
                        filename=file.filename,
                        status=ProcessingStatus.FAILED,
                        error=f"PDF parsing failed: {str(parse_error)}"
                    ))
                    continue
                finally:
                    # Clean up temp file
                    if temp_file_path and Path(temp_file_path).exists():
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass

            elif file_type in ["xlsx", "xls", "excel"]:
                try:
                    # Determine file extension
                    file_ext = Path(file.filename).suffix.lower()
                    if not file_ext:
                        file_ext = '.xlsx' if file_type == 'xlsx' else '.xls'

                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                        temp_file_path = temp_file.name
                        # Reset file pointer and copy content
                        await file.seek(0)
                        content = await file.read()
                        temp_file.write(content)

                    # Parse Excel file
                    parser = ExcelParser()
                    metadata = parser.parse(temp_file_path, file.filename, client_code, project_code)

                    # Generate normalized filename
                    normalized_filename = generate_filename(metadata)

                    logger.info(f"Excel parsed successfully. Confidence: {metadata.confidence_score:.2f}")
                    logger.info(f"Generated filename: {normalized_filename}")

                except Exception as parse_error:
                    logger.error(f"Excel parsing error: {str(parse_error)}", exc_info=True)
                    results.append(FileIngestResponse(
                        success=False,
                        filename=file.filename,
                        status=ProcessingStatus.FAILED,
                        error=f"Excel parsing failed: {str(parse_error)}"
                    ))
                    continue
                finally:
                    # Clean up temp file
                    if temp_file_path and Path(temp_file_path).exists():
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass

            elif file_type in ["lbrn2", "lbrn"]:
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.lbrn2') as temp_file:
                        temp_file_path = temp_file.name
                        await file.seek(0)
                        content = await file.read()
                        temp_file.write(content)

                    # Parse LightBurn file
                    parser = LBRNParser()
                    metadata = parser.parse(temp_file_path, file.filename, client_code, project_code)

                    # Generate normalized filename
                    normalized_filename = generate_filename(metadata)

                    logger.info(f"LightBurn parsed successfully. Confidence: {metadata.confidence_score:.2f}")
                    logger.info(f"Generated filename: {normalized_filename}")

                except Exception as parse_error:
                    logger.error(f"LightBurn parsing error: {str(parse_error)}", exc_info=True)
                    results.append(FileIngestResponse(
                        success=False,
                        filename=file.filename,
                        status=ProcessingStatus.FAILED,
                        error=f"LightBurn parsing failed: {str(parse_error)}"
                    ))
                    continue
                finally:
                    # Clean up temp file
                    if temp_file_path and Path(temp_file_path).exists():
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass

            elif file_type in ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "image"]:
                try:
                    # Determine file extension
                    file_ext = Path(file.filename).suffix.lower()
                    if not file_ext:
                        file_ext = '.png'

                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                        temp_file_path = temp_file.name
                        await file.seek(0)
                        content = await file.read()
                        temp_file.write(content)

                    # Parse image file
                    parser = ImageParser()
                    metadata = parser.parse(temp_file_path, file.filename, client_code, project_code)

                    # Generate normalized filename
                    normalized_filename = generate_filename(metadata)

                    logger.info(f"Image parsed successfully. Confidence: {metadata.confidence_score:.2f}")
                    logger.info(f"Generated filename: {normalized_filename}")

                except Exception as parse_error:
                    logger.error(f"Image parsing error: {str(parse_error)}", exc_info=True)
                    results.append(FileIngestResponse(
                        success=False,
                        filename=file.filename,
                        status=ProcessingStatus.FAILED,
                        error=f"Image parsing failed: {str(parse_error)}"
                    ))
                    continue
                finally:
                    # Clean up temp file
                    if temp_file_path and Path(temp_file_path).exists():
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass

            # Save file to storage
            stored_filename = None
            file_path_str = None

            if metadata and normalized_filename:
                try:
                    # Save file to storage with versioning
                    storage_result = save_file(
                        source_path=temp_file_path,
                        normalized_filename=normalized_filename,
                        client_code=metadata.client_code,
                        project_code=metadata.project_code,
                        auto_version=settings.AUTO_VERSION
                    )

                    if storage_result:
                        stored_filename, file_path_str = storage_result
                        logger.info(f"File saved to storage: {file_path_str}")
                    else:
                        logger.error("Failed to save file to storage")

                except Exception as storage_error:
                    logger.error(f"Storage error: {storage_error}")

            # Save to database
            ingest_id = None
            if metadata and stored_filename and file_path_str:
                try:
                    file_ingest = save_file_ingest(
                        normalized_metadata=metadata,
                        original_filename=file.filename,
                        stored_filename=stored_filename,
                        file_path=file_path_str,
                        status='completed'
                    )

                    if file_ingest:
                        ingest_id = file_ingest.id
                        logger.info(f"Saved to database with ID: {ingest_id}")

                        # Save raw extraction data
                        save_file_extraction(
                            file_ingest_id=ingest_id,
                            extraction_type=f"{metadata.detected_type.value}_metadata",
                            extracted_data=metadata.extracted,
                            confidence_score=metadata.confidence_score,
                            parser_name=f"{metadata.detected_type.value}_parser",
                            parser_version="1.0.0"
                        )

                        # Save metadata key-value pairs
                        metadata_dict = {
                            'client_code': metadata.client_code,
                            'project_code': metadata.project_code,
                            'part_name': metadata.part_name,
                            'material': metadata.material,
                            'thickness_mm': metadata.thickness_mm,
                            'quantity': metadata.quantity,
                            'version': metadata.version
                        }
                        save_file_metadata(
                            file_ingest_id=ingest_id,
                            metadata_dict=metadata_dict,
                            source=f"{metadata.detected_type.value}_parser"
                        )

                        # Send webhook notification to Laser OS
                        if settings.WEBHOOK_ENABLED and file_ingest:
                            try:
                                webhook_sent = await send_webhook(
                                    event_type=WebhookEventType.FILE_PROCESSED,
                                    file_ingest=file_ingest
                                )
                                if webhook_sent:
                                    logger.info(f"Webhook sent successfully for file {ingest_id}")
                                else:
                                    logger.warning(f"Webhook failed for file {ingest_id}")
                            except Exception as webhook_error:
                                logger.error(f"Webhook error: {webhook_error}")
                                # Don't fail the whole process if webhook fails
                    else:
                        logger.error("Failed to save to database")

                except Exception as db_error:
                    logger.error(f"Database error: {db_error}")

            # Build response
            results.append(FileIngestResponse(
                success=True,
                ingest_id=ingest_id,
                filename=file.filename,
                normalized_filename=stored_filename or normalized_filename,
                status=ProcessingStatus.COMPLETE if metadata else ProcessingStatus.PENDING,
                metadata=metadata,
                error=None
            ))

            logger.info(f"File {file.filename} processed successfully")

        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}", exc_info=True)
            results.append(FileIngestResponse(
                success=False,
                filename=file.filename,
                status=ProcessingStatus.FAILED,
                error=str(e)
            ))
        finally:
            # Ensure temp file cleanup
            if temp_file_path and Path(temp_file_path).exists():
                try:
                    Path(temp_file_path).unlink()
                except:
                    pass

    logger.info(f"Ingestion complete: {len(results)} results")
    return results


@app.get("/files")
async def list_files(
    client_code: Optional[str] = None,
    project_code: Optional[str] = None,
    file_type: Optional[str] = None,
    material: Optional[str] = None,
    thickness_mm: Optional[float] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all ingested files with optional filters

    Args:
        client_code: Filter by client code
        project_code: Filter by project code
        file_type: Filter by file type
        material: Filter by material
        thickness_mm: Filter by thickness
        status: Filter by status
        limit: Maximum number of records
        offset: Number of records to skip

    Returns:
        List of file ingest records
    """
    logger.info(f"Listing files with filters: client={client_code}, project={project_code}, type={file_type}")

    try:
        file_ingests = get_file_ingests(
            client_code=client_code,
            project_code=project_code,
            file_type=file_type,
            material=material,
            thickness_mm=thickness_mm,
            status=status,
            limit=limit,
            offset=offset
        )

        return {
            "success": True,
            "count": len(file_ingests),
            "limit": limit,
            "offset": offset,
            "files": [fi.to_dict() for fi in file_ingests]
        }

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{file_id}")
async def get_file_details(file_id: int):
    """
    Get details of a specific file by ID

    Args:
        file_id: File ingest ID

    Returns:
        File ingest record with details
    """
    logger.info(f"Getting file details for ID: {file_id}")

    try:
        file_ingest = get_file_ingest(file_id)

        if not file_ingest:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        return {
            "success": True,
            "file": file_ingest.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{file_id}/metadata")
async def get_file_metadata_endpoint(file_id: int):
    """
    Get extracted metadata for a file

    Args:
        file_id: File ingest ID

    Returns:
        Extracted metadata and extractions
    """
    logger.info(f"Getting metadata for file ID: {file_id}")

    try:
        file_ingest = get_file_ingest(file_id)

        if not file_ingest:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Get extractions and metadata
        extractions = [ext.to_dict() for ext in file_ingest.extractions]
        metadata = [meta.to_dict() for meta in file_ingest.file_metadata]

        return {
            "success": True,
            "file_id": file_id,
            "filename": file_ingest.original_filename,
            "extractions": extractions,
            "metadata": metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ingest/{ingest_id}", response_model=IngestStatusResponse)
async def get_ingest_status(ingest_id: int):
    """
    Get status of a file ingestion.

    Args:
        ingest_id: ID of the ingestion record

    Returns:
        IngestStatusResponse object
    """
    logger.info(f"Getting status for ingest ID: {ingest_id}")

    try:
        file_ingest = get_file_ingest(ingest_id)

        if not file_ingest:
            raise HTTPException(status_code=404, detail=f"Ingest {ingest_id} not found")

        return IngestStatusResponse(
            ingest_id=file_ingest.id,
            filename=file_ingest.original_filename,
            status=ProcessingStatus(file_ingest.status),
            confidence_score=file_ingest.confidence_score,
            error_message=file_ingest.error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ingest status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/files/{file_id}/re-extract")
async def re_extract_endpoint(file_id: int, mode: str = "AUTO"):
    """
    Re-run extraction on an existing file.

    Args:
        file_id: ID of the file ingest record
        mode: Processing mode

    Returns:
        Status message
    """
    logger.info(f"Re-extracting file ID: {file_id} with mode: {mode}")

    try:
        file_ingest = get_file_ingest(file_id)

        if not file_ingest:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Get file path
        file_path = get_file_path(file_ingest.file_path)

        if not file_path:
            raise HTTPException(status_code=404, detail=f"File not found in storage: {file_ingest.file_path}")

        # Mark for re-extraction
        updated = re_extract_file(file_id)

        if not updated:
            raise HTTPException(status_code=500, detail="Failed to mark file for re-extraction")

        # Send webhook notification
        if settings.WEBHOOK_ENABLED:
            try:
                await send_webhook(
                    event_type=WebhookEventType.FILE_RE_EXTRACTED,
                    file_ingest=file_ingest
                )
            except Exception as webhook_error:
                logger.error(f"Webhook error: {webhook_error}")

        return {
            "success": True,
            "message": f"File {file_id} marked for re-extraction",
            "file_id": file_id,
            "status": "pending"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-extracting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{file_id}")
async def delete_file_endpoint(file_id: int, hard_delete: bool = False):
    """
    Delete a file record (soft delete by default)

    Args:
        file_id: File ingest ID
        hard_delete: If True, permanently delete; if False, soft delete

    Returns:
        Status message
    """
    logger.info(f"Deleting file ID: {file_id} (hard_delete={hard_delete})")

    try:
        file_ingest = get_file_ingest(file_id, include_deleted=True)

        if not file_ingest:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Delete from database
        success = delete_file_ingest(file_id, hard_delete=hard_delete)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file from database")

        # If hard delete, also delete from storage
        if hard_delete:
            delete_stored_file(file_ingest.file_path)

        # Send webhook notification
        if settings.WEBHOOK_ENABLED:
            try:
                await send_webhook(
                    event_type=WebhookEventType.FILE_DELETED,
                    file_ingest=file_ingest,
                    additional_data={"hard_delete": hard_delete}
                )
            except Exception as webhook_error:
                logger.error(f"Webhook error: {webhook_error}")

        return {
            "success": True,
            "message": f"File {file_id} {'permanently deleted' if hard_delete else 'soft deleted'}",
            "file_id": file_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/{ingest_id}")
async def re_extract(ingest_id: int, mode: str = "AUTO"):
    """
    Re-run extraction on an existing file (legacy endpoint).

    Args:
        ingest_id: ID of the ingestion record
        mode: Processing mode

    Returns:
        Status message
    """
    # Redirect to new endpoint
    return await re_extract_endpoint(ingest_id, mode)


@app.get("/webhooks/stats")
async def webhook_stats(hours: int = 24):
    """
    Get webhook statistics.

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        Webhook statistics
    """
    monitor = get_webhook_monitor()
    stats = monitor.get_stats(hours=hours)
    return JSONResponse(content=stats)


@app.get("/webhooks/health")
async def webhook_health():
    """
    Get webhook health status.

    Returns:
        Health status with metrics
    """
    monitor = get_webhook_monitor()
    health = monitor.get_health_status()
    return JSONResponse(content=health)


@app.get("/webhooks/queue/stats")
async def webhook_queue_stats():
    """
    Get webhook queue statistics.

    Returns:
        Queue statistics
    """
    queue = get_webhook_queue()
    stats = queue.get_stats()
    return JSONResponse(content=stats)


@app.get("/webhooks/failures")
async def webhook_failures(limit: int = 10):
    """
    Get recent webhook failures.

    Args:
        limit: Maximum number of failures to return (default: 10)

    Returns:
        List of recent failures
    """
    monitor = get_webhook_monitor()
    failures = monitor.get_recent_failures(limit=limit)
    return JSONResponse(content={"failures": failures})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.MODULE_N_HOST,
        port=settings.MODULE_N_PORT,
        reload=settings.MODULE_N_RELOAD,
        workers=1 if settings.MODULE_N_RELOAD else settings.MODULE_N_WORKERS
    )

