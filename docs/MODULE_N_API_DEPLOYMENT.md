# Module N - API & Deployment Guide
## FastAPI Endpoints, Integration, and Deployment Instructions

**Version:** 1.0  
**Date:** 2025-10-21  
**Companion to:** MODULE_N_SPECIFICATION.md, MODULE_N_IMPLEMENTATION.md

---

## Table of Contents

1. [FastAPI Endpoints](#fastapi-endpoints)
2. [File Naming Logic](#file-naming-logic)
3. [Integration with Laser OS](#integration-with-laser-os)
4. [Security & Validation](#security--validation)
5. [Deployment Guide](#deployment-guide)
6. [Testing Strategy](#testing-strategy)
7. [Example Usage](#example-usage)

---

## FastAPI Endpoints

### Main Application

```python
# module_n/main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
from pathlib import Path

from .parsers.dxf_parser import DXFParser
from .parsers.pdf_parser import PDFParser
from .parsers.excel_parser import ExcelParser
from .parsers.lbrn_parser import LBRNParser
from .parsers.image_parser import ImageParser
from .models import FileIngestRequest, FileIngestResponse, ProcessingStatus
from .utils import validate_file, detect_file_type, save_file, generate_filename
from .database import create_ingest_record, notify_laser_os

app = FastAPI(
    title="Module N - File Ingest & Extract",
    description="Intelligent file ingestion and metadata extraction for Laser OS",
    version="1.0.0"
)

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
        mode: Processing mode (AUTO, excel, pdf, dxf, etc.)
        override_metadata: JSON string with metadata overrides
    
    Returns:
        List of FileIngestResponse objects
    """
    results = []
    
    for file in files:
        try:
            # Validate file
            validation_result = await validate_file(file)
            if not validation_result['valid']:
                results.append(FileIngestResponse(
                    success=False,
                    filename=file.filename,
                    status=ProcessingStatus.FAILED,
                    error=validation_result['error']
                ))
                continue
            
            # Save temporary file
            temp_path = await save_temp_file(file)
            
            # Detect file type
            file_type = detect_file_type(file.filename, mode)
            
            # Process file based on type
            metadata = None
            if file_type == 'dxf':
                parser = DXFParser()
                metadata = parser.parse(temp_path, file.filename)
            elif file_type == 'lbrn2':
                parser = LBRNParser()
                metadata = parser.parse(temp_path, file.filename)
            elif file_type == 'pdf':
                parser = PDFParser()
                metadata = parser.parse(temp_path, file.filename)
            elif file_type in ['xlsx', 'xls']:
                parser = ExcelParser()
                metadata = parser.parse(temp_path, file.filename)
            elif file_type in ['jpg', 'jpeg', 'png']:
                parser = ImageParser()
                metadata = parser.parse(temp_path, file.filename)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Apply overrides
            if client_code:
                metadata.client_code = client_code
            if project_code:
                metadata.project_code = project_code
            
            # Generate normalized filename
            normalized_filename = generate_filename(metadata)
            
            # Save file to final location
            file_path = await save_file(
                temp_path,
                normalized_filename,
                metadata.client_code,
                metadata.project_code
            )
            
            # Store in database
            ingest_record = await create_ingest_record(
                file=file,
                file_path=file_path,
                metadata=metadata,
                client_code=client_code,
                project_code=project_code
            )
            
            # Send webhook to Laser OS
            await notify_laser_os(ingest_record)
            
            results.append(FileIngestResponse(
                success=True,
                ingest_id=ingest_record.id,
                filename=file.filename,
                normalized_filename=normalized_filename,
                status=ProcessingStatus.COMPLETED,
                metadata=metadata
            ))
            
        except Exception as e:
            results.append(FileIngestResponse(
                success=False,
                filename=file.filename,
                status=ProcessingStatus.FAILED,
                error=str(e)
            ))
    
    return results

@app.get("/ingest/{ingest_id}")
async def get_ingest_status(ingest_id: int):
    """Get status of a file ingestion."""
    from .database import get_ingest_record
    
    record = await get_ingest_record(ingest_id)
    if not record:
        raise HTTPException(status_code=404, detail="Ingest record not found")
    
    return record

@app.post("/extract/{ingest_id}")
async def re_extract(ingest_id: int, mode: str = "AUTO"):
    """Re-run extraction on an existing file."""
    from .database import get_ingest_record, update_ingest_record
    
    record = await get_ingest_record(ingest_id)
    if not record:
        raise HTTPException(status_code=404, detail="Ingest record not found")
    
    # Re-process file
    # ... (similar logic to ingest_files)
    
    return {"message": "Re-extraction started", "ingest_id": ingest_id}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "module-n",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Module N - File Ingest & Extract",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "/ingest",
            "status": "/ingest/{ingest_id}",
            "re_extract": "/extract/{ingest_id}",
            "health": "/health",
            "docs": "/docs"
        }
    }
```

---

## File Naming Logic

### Filename Generator

```python
# module_n/utils/filename_generator.py

import re
from pathlib import Path
from typing import Optional
from ..models import NormalizedMetadata

MATERIAL_CODE_MAP = {
    'Aluminum': 'AL',
    'Brass': 'BR',
    'Carbon Steel': 'CS',
    'Copper': 'CU',
    'Galvanized Steel': 'GALV',
    'Mild Steel': 'MS',
    'Stainless Steel': 'SS',
    'Vastrap': 'VAST',
    'Zinc': 'ZN',
    'Other': 'OTH'
}

def generate_filename(metadata: NormalizedMetadata) -> str:
    """
    Generate standardized filename from metadata.
    
    Format: {ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}
    Example: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf
    """
    parts = []
    
    # Client code (required)
    if metadata.client_code:
        parts.append(metadata.client_code.replace('-', ''))
    else:
        parts.append('UNKNOWN')
    
    # Project code (required)
    if metadata.project_code:
        parts.append(metadata.project_code)
    else:
        parts.append('NOPROJECT')
    
    # Part name (required)
    if metadata.part_name:
        # Sanitize part name
        part_name = re.sub(r'[^a-zA-Z0-9_-]', '', metadata.part_name)
        parts.append(part_name)
    else:
        parts.append('Part')
    
    # Material (required)
    if metadata.material:
        material_code = MATERIAL_CODE_MAP.get(metadata.material, 'UNK')
        parts.append(material_code)
    else:
        parts.append('UNK')
    
    # Thickness (optional)
    if metadata.thickness_mm:
        parts.append(f'{metadata.thickness_mm}mm')
    
    # Quantity (optional)
    if metadata.quantity:
        parts.append(f'x{metadata.quantity}')
    
    # Version (optional)
    if metadata.version and metadata.version > 1:
        parts.append(f'v{metadata.version}')
    
    # Extension
    ext = metadata.source_file.rsplit('.', 1)[-1] if '.' in metadata.source_file else 'bin'
    
    filename = '-'.join(parts) + '.' + ext
    
    return filename

def handle_filename_collision(
    filename: str,
    client_code: str,
    project_code: str,
    base_path: Path
) -> str:
    """
    Handle filename collisions by appending -v2, -v3, etc.
    """
    target_path = base_path / 'inputs' / filename
    
    if not target_path.exists():
        return filename
    
    # File exists, increment version
    name, ext = filename.rsplit('.', 1)
    version = 2
    
    while True:
        new_filename = f'{name}-v{version}.{ext}'
        new_path = base_path / 'inputs' / new_filename
        
        if not new_path.exists():
            return new_filename
        
        version += 1
        
        if version > 100:  # Safety limit
            raise ValueError(f"Too many versions of file: {filename}")
```

---

## Integration with Laser OS

### Flask Integration (Option 1: Microservice)

```python
# app/services/module_n_client.py

import requests
from typing import List, Dict, Any, Optional
from flask import current_app
from werkzeug.datastructures import FileStorage

class ModuleNClient:
    """Client for communicating with Module N service."""

    def __init__(self):
        self.base_url = current_app.config.get('MODULE_N_URL', 'http://localhost:8081')
        self.timeout = 30

    def ingest_files(
        self,
        files: List[FileStorage],
        client_code: Optional[str] = None,
        project_code: Optional[str] = None,
        mode: str = "AUTO"
    ) -> List[Dict[str, Any]]:
        """Send files to Module N for ingestion."""
        url = f"{self.base_url}/ingest"

        files_data = []
        for file in files:
            files_data.append(
                ('files', (file.filename, file.stream, file.content_type))
            )

        data = {'mode': mode}
        if client_code:
            data['client_code'] = client_code
        if project_code:
            data['project_code'] = project_code

        try:
            response = requests.post(url, files=files_data, data=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Module N request failed: {str(e)}")
            raise
```

### Webhook Handler

```python
# app/routes/webhooks.py

from flask import Blueprint, request, jsonify, current_app
from app.models import Project, DesignFile
from app import db

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/module-n/event', methods=['POST'])
def module_n_event():
    """Receive webhook events from Module N."""
    try:
        data = request.get_json()

        if data.get('event') == 'file_ingested':
            project_code = data['metadata'].get('project_code')
            project = Project.query.filter_by(project_code=project_code).first()

            if not project:
                return jsonify({'error': 'Project not found'}), 404

            design_file = DesignFile(
                project_id=project.id,
                original_filename=data['filename'],
                stored_filename=data['normalized_filename'],
                file_path=data['file_path'],
                file_type=data['metadata'].get('detected_type'),
                part_name=data['metadata'].get('part_name'),
                material=data['metadata'].get('material'),
                thickness_mm=data['metadata'].get('thickness_mm'),
                quantity=data['metadata'].get('quantity', 1)
            )

            db.session.add(design_file)
            db.session.commit()

            return jsonify({'success': True, 'design_file_id': design_file.id})

        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Webhook failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

---

## Deployment Guide

### Option 1: Microservice Deployment

#### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Module N dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0
pip install pandas==2.1.3 openpyxl==3.1.2 xlrd==2.0.1
pip install PyMuPDF==1.23.8 camelot-py[cv]==0.11.0 pdf2image==1.16.3
pip install ezdxf==1.1.0 Pillow==10.1.0 pytesseract==0.3.10
pip install python-magic==0.4.27 python-dotenv==1.0.0
pip install sqlalchemy==2.0.23 requests==2.31.0
```

#### 2. Configuration

```bash
# .env file for Module N
MODULE_N_PORT=8081
MODULE_N_HOST=0.0.0.0
DATABASE_URL=sqlite:///data/laser_os.db
LASER_OS_WEBHOOK_URL=http://localhost:8080/webhooks/module-n/event
UPLOAD_FOLDER=data/files
MAX_UPLOAD_SIZE=52428800
TESSERACT_LANGUAGES=eng+afr
CONFIDENCE_THRESHOLD=0.70
```

#### 3. Run Module N Service

```bash
# Development
uvicorn module_n.main:app --reload --port 8081

# Production
uvicorn module_n.main:app --host 0.0.0.0 --port 8081 --workers 4
```

#### 4. Configure Laser OS

```python
# config.py (add to Laser OS)

MODULE_N_ENABLED = True
MODULE_N_URL = 'http://localhost:8081'
MODULE_N_AUTO_PROCESS = True
```

### Option 2: Flask Blueprint Integration

```python
# app/__init__.py (Laser OS)

from module_n.blueprint import module_n_bp

app.register_blueprint(module_n_bp, url_prefix='/module-n')
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_dxf_parser.py

import pytest
from module_n.parsers.dxf_parser import DXFParser

def test_dxf_parser_valid_file():
    parser = DXFParser()
    metadata = parser.parse('tests/fixtures/bracket.dxf', 'bracket.dxf')

    assert metadata.detected_type == 'dxf'
    assert metadata.extracted['layers'] is not None
    assert metadata.confidence_score > 0.5

def test_dxf_parser_filename_extraction():
    parser = DXFParser()
    metadata = parser.parse(
        'tests/fixtures/test.dxf',
        'CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf'
    )

    assert metadata.client_code == 'CL0001'
    assert metadata.project_code == 'JB-2025-10-CL0001-001'
    assert metadata.part_name == 'Bracket'
    assert metadata.material == 'Mild Steel'
    assert metadata.thickness_mm == 5.0
    assert metadata.quantity == 10
```

### Integration Tests

```python
# tests/test_api.py

from fastapi.testclient import TestClient
from module_n.main import app

client = TestClient(app)

def test_ingest_endpoint():
    with open('tests/fixtures/bracket.dxf', 'rb') as f:
        response = client.post(
            '/ingest',
            files={'files': ('bracket.dxf', f, 'application/dxf')},
            data={'mode': 'AUTO'}
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['success'] is True
```

---

## Example Usage

### cURL Examples

```bash
# Upload single DXF file
curl -X POST http://localhost:8081/ingest \
  -F "files=@bracket.dxf" \
  -F "client_code=CL-0001" \
  -F "project_code=JB-2025-10-CL0001-001" \
  -F "mode=AUTO"

# Upload multiple files
curl -X POST http://localhost:8081/ingest \
  -F "files=@bracket.dxf" \
  -F "files=@quote.pdf" \
  -F "files=@parts_list.xlsx" \
  -F "mode=AUTO"

# Check ingestion status
curl http://localhost:8081/ingest/123

# Health check
curl http://localhost:8081/health
```

### Python Client Example

```python
import requests

# Upload files
files = [
    ('files', open('bracket.dxf', 'rb')),
    ('files', open('quote.pdf', 'rb'))
]

data = {
    'client_code': 'CL-0001',
    'project_code': 'JB-2025-10-CL0001-001',
    'mode': 'AUTO'
}

response = requests.post('http://localhost:8081/ingest', files=files, data=data)
results = response.json()

for result in results:
    print(f"File: {result['filename']}")
    print(f"Status: {result['status']}")
    print(f"Normalized: {result['normalized_filename']}")
```

---

## Summary

Module N provides a comprehensive file ingestion and metadata extraction system with:

✅ **Multi-format support** (DXF, LBRN2, PDF, Excel, images)
✅ **Intelligent parsing** with confidence scoring
✅ **Standardized file naming** with collision handling
✅ **RESTful API** with FastAPI
✅ **Webhook integration** with Laser OS
✅ **Security validation** (file type, size, MIME)
✅ **Database tracking** (ingests, extractions, metadata)
✅ **Flexible deployment** (microservice or blueprint)

**Next Steps:**
1. Review specifications
2. Set up development environment
3. Implement parsers incrementally
4. Test with real files
5. Deploy to production

