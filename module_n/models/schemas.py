"""
Module N - Pydantic Data Models
Defines all data validation schemas for file ingestion and metadata extraction
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Enums
# ============================================================================

class FileType(str, Enum):
    """Supported file types"""
    DXF = "dxf"
    LBRN2 = "lbrn2"
    PDF = "pdf"
    EXCEL = "excel"
    IMAGE = "image"
    TEXT = "text"
    WORD = "word"
    UNKNOWN = "unknown"


class ProcessingMode(str, Enum):
    """Processing mode for file ingestion"""
    AUTO = "AUTO"  # Auto-detect file type
    DXF = "dxf"
    LBRN2 = "lbrn2"
    PDF = "pdf"
    EXCEL = "excel"
    IMAGE = "image"
    TEXT = "text"


class ProcessingStatus(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Material Mapping
# ============================================================================

MATERIAL_MAP = {
    'Galv': 'Galvanized Steel',
    'Galvanized': 'Galvanized Steel',
    'SS': 'Stainless Steel',
    'Stainless': 'Stainless Steel',
    'MS': 'Mild Steel',
    'Mild': 'Mild Steel',
    'Al': 'Aluminum',
    'Aluminum': 'Aluminum',
    'Aluminium': 'Aluminum',
    'Brass': 'Brass',
    'Copper': 'Copper',
    'CS': 'Carbon Steel',
    'Carbon': 'Carbon Steel',
    'Vastrap': 'Vastrap',
    'Zinc': 'Zinc',
    'Other': 'Other'
}

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


# ============================================================================
# Base Metadata Model
# ============================================================================

class NormalizedMetadata(BaseModel):
    """Normalized metadata extracted from any file type"""
    
    # File Information
    source_file: str
    detected_type: FileType
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Project Information
    client_code: Optional[str] = None
    project_code: Optional[str] = None
    part_name: Optional[str] = None
    
    # Material Information
    material: Optional[str] = None
    thickness_mm: Optional[float] = None
    
    # Quantity & Version
    quantity: int = 1
    version: int = 1
    
    # Extracted Data (format-specific)
    extracted: Dict[str, Any] = Field(default_factory=dict)
    
    # Confidence & Metadata
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    extraction_notes: List[str] = Field(default_factory=list)
    
    # Timestamps
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('material')
    @classmethod
    def normalize_material(cls, v: Optional[str]) -> Optional[str]:
        """Normalize material names"""
        if v is None:
            return None
        return MATERIAL_MAP.get(v, v)
    
    @field_validator('thickness_mm')
    @classmethod
    def validate_thickness(cls, v: Optional[float]) -> Optional[float]:
        """Validate thickness is positive"""
        if v is not None and v <= 0:
            raise ValueError("Thickness must be positive")
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_file": "bracket.dxf",
                "detected_type": "dxf",
                "client_code": "CL0001",
                "project_code": "JB-2025-10-CL0001-001",
                "part_name": "Bracket",
                "material": "Mild Steel",
                "thickness_mm": 5.0,
                "quantity": 10,
                "confidence_score": 0.95
            }
        }


# ============================================================================
# Format-Specific Metadata Models
# ============================================================================

class DXFMetadata(BaseModel):
    """DXF-specific metadata"""
    layers: List[str] = Field(default_factory=list)
    entity_counts: Dict[str, int] = Field(default_factory=dict)
    bounding_box: Optional[Dict[str, float]] = None
    text_notes: List[str] = Field(default_factory=list)
    holes: List[Dict[str, Any]] = Field(default_factory=list)
    perimeter_mm: Optional[float] = None
    area_mm2: Optional[float] = None
    dxf_version: Optional[str] = None


class LBRNMetadata(BaseModel):
    """LightBurn .lbrn2 specific metadata"""
    app_version: Optional[str] = None
    format_version: Optional[str] = None
    material_height: Optional[float] = None
    cut_settings: List[Dict[str, Any]] = Field(default_factory=list)
    layer_count: int = 0
    has_variable_text: bool = False


class PDFMetadata(BaseModel):
    """PDF-specific metadata"""
    page_count: int = 0
    text_content: Optional[str] = None
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    detected_fields: Dict[str, Any] = Field(default_factory=dict)
    pdf_version: Optional[str] = None


class ExcelMetadata(BaseModel):
    """Excel-specific metadata"""
    sheet_names: List[str] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    headers: List[str] = Field(default_factory=list)
    data_rows: List[Dict[str, Any]] = Field(default_factory=list)
    detected_schema: Optional[str] = None


class ImageMetadata(BaseModel):
    """Image-specific metadata"""
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    mode: Optional[str] = None
    dpi: Optional[tuple] = None
    exif_data: Dict[str, Any] = Field(default_factory=dict)
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None


# ============================================================================
# API Request/Response Models
# ============================================================================

class FileIngestRequest(BaseModel):
    """Request model for file ingestion"""
    client_code: Optional[str] = None
    project_code: Optional[str] = None
    mode: ProcessingMode = ProcessingMode.AUTO
    override_metadata: Optional[Dict[str, Any]] = None


class FileIngestResponse(BaseModel):
    """Response model for file ingestion"""
    success: bool
    ingest_id: Optional[int] = None
    filename: str
    normalized_filename: Optional[str] = None
    status: ProcessingStatus
    metadata: Optional[NormalizedMetadata] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "ingest_id": 123,
                "filename": "bracket.dxf",
                "normalized_filename": "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
                "status": "completed",
                "metadata": {
                    "source_file": "bracket.dxf",
                    "detected_type": "dxf",
                    "confidence_score": 0.95
                }
            }
        }


class IngestStatusResponse(BaseModel):
    """Response model for ingestion status"""
    ingest_id: int
    status: ProcessingStatus
    filename: str
    normalized_filename: Optional[str] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

