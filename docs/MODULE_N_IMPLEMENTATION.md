# Module N - Implementation Guide
## Parsers, API Endpoints, and Integration Code

**Version:** 1.0  
**Date:** 2025-10-21  
**Companion to:** MODULE_N_SPECIFICATION.md

---

## Table of Contents

1. [Data Models (Pydantic)](#data-models-pydantic)
2. [File Processing Engines](#file-processing-engines)
3. [API Endpoints](#api-endpoints)
4. [File Naming Logic](#file-naming-logic)
5. [Integration with Laser OS](#integration-with-laser-os)
6. [Security & Validation](#security--validation)
7. [Example Usage](#example-usage)

---

## Data Models (Pydantic)

### Core Models

```python
# module_n/models.py

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class FileType(str, Enum):
    """Supported file types."""
    EXCEL = "excel"
    PDF = "pdf"
    DXF = "dxf"
    LBRN2 = "lbrn2"
    IMAGE = "image"
    TEXT = "text"
    GDOC = "gdoc"
    GSHEET = "gsheet"
    UNKNOWN = "unknown"

class ProcessingMode(str, Enum):
    """Processing modes."""
    AUTO = "AUTO"
    EXCEL = "excel"
    PDF = "pdf"
    DXF = "dxf"
    LBRN2 = "lbrn2"
    IMAGE = "image"
    TEXT = "text"

class ProcessingStatus(str, Enum):
    """Processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class NormalizedMetadata(BaseModel):
    """Normalized file metadata."""
    client_code: Optional[str] = None
    project_code: Optional[str] = None
    part_name: Optional[str] = None
    material: Optional[str] = None
    thickness_mm: Optional[Decimal] = None
    quantity: Optional[int] = 1
    version: int = 1
    due_date: Optional[date] = None
    source_file: str
    detected_type: FileType
    extracted: Dict[str, Any] = {}
    confidence_score: Optional[Decimal] = None
    
    @validator('material')
    def validate_material(cls, v):
        """Validate material against known types."""
        valid_materials = [
            'Aluminum', 'Brass', 'Carbon Steel', 'Copper',
            'Galvanized Steel', 'Mild Steel', 'Stainless Steel',
            'Vastrap', 'Zinc', 'Other'
        ]
        if v and v not in valid_materials:
            return 'Other'
        return v

class DXFMetadata(BaseModel):
    """DXF-specific metadata."""
    layers: List[str] = []
    entity_counts: Dict[str, int] = {}
    bounding_box: Optional[Dict[str, float]] = None
    dimensions_mm: Optional[List[float]] = None
    text_notes: List[str] = []
    blocks: List[str] = []
    perimeter_length_mm: Optional[float] = None
    hole_count: int = 0
    hole_diameters: List[float] = []
    area_mm2: Optional[float] = None

class LBRNMetadata(BaseModel):
    """LightBurn-specific metadata."""
    job_name: Optional[str] = None
    material_settings: Optional[Dict[str, Any]] = None
    layer_info: List[Dict[str, Any]] = []
    cut_settings: Optional[Dict[str, Any]] = None
    preview_image_path: Optional[str] = None

class PDFMetadata(BaseModel):
    """PDF-specific metadata."""
    page_count: int
    text_content: str
    tables: List[Dict[str, Any]] = []
    images_extracted: int = 0
    po_number: Optional[str] = None
    detected_fields: Dict[str, Any] = {}

class ExcelMetadata(BaseModel):
    """Excel-specific metadata."""
    sheet_names: List[str]
    row_count: int
    column_count: int
    headers: List[str] = []
    data_rows: List[Dict[str, Any]] = []
    detected_schema: Optional[Dict[str, str]] = None

class ImageMetadata(BaseModel):
    """Image-specific metadata."""
    width: int
    height: int
    format: str
    mode: str
    exif_data: Optional[Dict[str, Any]] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
```

---

## File Processing Engines

### 1. DXF Parser

```python
# module_n/parsers/dxf_parser.py

import ezdxf
from typing import Dict, Any, List, Optional
from decimal import Decimal
from ..models import DXFMetadata, NormalizedMetadata, FileType

class DXFParser:
    """Parser for DXF files using ezdxf."""
    
    MATERIAL_MAP = {
        'Galv': 'Galvanized Steel',
        'SS': 'Stainless Steel',
        'MS': 'Mild Steel',
        'Al': 'Aluminum',
        'Brass': 'Brass',
        'Copper': 'Copper',
        'CS': 'Carbon Steel',
    }
    
    def parse(self, file_path: str, filename: str) -> NormalizedMetadata:
        """Parse DXF file and extract metadata."""
        try:
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # Extract DXF-specific metadata
            dxf_meta = self._extract_dxf_metadata(doc, msp)
            
            # Extract normalized metadata from filename
            normalized = self._parse_filename(filename)
            
            # Enhance with DXF data
            if dxf_meta.text_notes:
                normalized = self._enhance_from_notes(normalized, dxf_meta.text_notes)
            
            # Add DXF metadata to extracted field
            normalized.extracted = dxf_meta.dict()
            normalized.detected_type = FileType.DXF
            normalized.source_file = filename
            normalized.confidence_score = Decimal('0.85')
            
            return normalized
            
        except Exception as e:
            raise ValueError(f"Failed to parse DXF: {str(e)}")
    
    def _extract_dxf_metadata(self, doc, msp) -> DXFMetadata:
        """Extract DXF-specific metadata."""
        metadata = DXFMetadata()
        
        # Extract layers
        metadata.layers = [layer.dxf.name for layer in doc.layers]
        
        # Count entities by type
        entity_counts = {}
        for entity in msp:
            entity_type = entity.dxftype()
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        metadata.entity_counts = entity_counts
        
        # Calculate bounding box
        try:
            extents = msp.extents()
            if extents:
                metadata.bounding_box = {
                    'min_x': extents.extmin.x,
                    'min_y': extents.extmin.y,
                    'max_x': extents.extmax.x,
                    'max_y': extents.extmax.y
                }
                metadata.dimensions_mm = [
                    extents.extmax.x - extents.extmin.x,
                    extents.extmax.y - extents.extmin.y
                ]
        except:
            pass
        
        # Extract text notes
        text_notes = []
        for entity in msp.query('TEXT'):
            if hasattr(entity.dxf, 'text'):
                text_notes.append(entity.dxf.text)
        metadata.text_notes = text_notes
        
        # Extract blocks
        metadata.blocks = [block.name for block in doc.blocks if not block.name.startswith('*')]
        
        # Count holes (circles on HOLES layer)
        holes = []
        for entity in msp.query('CIRCLE'):
            if hasattr(entity.dxf, 'layer') and 'HOLE' in entity.dxf.layer.upper():
                holes.append(entity.dxf.radius * 2)  # Diameter
        metadata.hole_count = len(holes)
        metadata.hole_diameters = holes
        
        # Calculate perimeter (approximate from OUTLINE layer)
        perimeter = 0.0
        for entity in msp.query('LINE POLYLINE LWPOLYLINE'):
            if hasattr(entity.dxf, 'layer') and 'OUTLINE' in entity.dxf.layer.upper():
                try:
                    perimeter += entity.dxf.length if hasattr(entity.dxf, 'length') else 0
                except:
                    pass
        if perimeter > 0:
            metadata.perimeter_length_mm = perimeter
        
        return metadata
    
    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """Parse filename to extract metadata."""
        import re
        
        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf
        pattern1 = r'^([A-Z]{2}\d{4})-([A-Z]{2}-\d{4}-\d{2}-[A-Z]{2}\d{4}-\d{3})-(.+?)-([A-Z]{2,4})-(\d+\.?\d*)mm-x(\d+)(?:-v(\d+))?\.dxf$'
        match = re.match(pattern1, filename, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                client_code=match.group(1),
                project_code=match.group(2),
                part_name=match.group(3),
                material=self.MATERIAL_MAP.get(match.group(4), 'Other'),
                thickness_mm=Decimal(match.group(5)),
                quantity=int(match.group(6)),
                version=int(match.group(7)) if match.group(7) else 1,
                source_file=filename,
                detected_type=FileType.DXF,
                extracted={}
            )
        
        # Try old format: 0001-Full Gas Box-Galv-1mm-x1.dxf
        pattern2 = r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)\.dxf$'
        match = re.match(pattern2, filename, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                part_name=match.group(2),
                material=self.MATERIAL_MAP.get(match.group(3), 'Other'),
                thickness_mm=Decimal(match.group(4)),
                quantity=int(match.group(5)),
                source_file=filename,
                detected_type=FileType.DXF,
                extracted={}
            )
        
        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.DXF,
            extracted={}
        )
```

---

### 2. PDF Parser

```python
# module_n/parsers/pdf_parser.py

import fitz  # PyMuPDF
import camelot
from typing import Dict, Any, List
from ..models import PDFMetadata, NormalizedMetadata, FileType

class PDFParser:
    """Parser for PDF files using PyMuPDF and Camelot."""

    def parse(self, file_path: str, filename: str) -> NormalizedMetadata:
        """Parse PDF file and extract metadata."""
        try:
            # Open PDF
            doc = fitz.open(file_path)

            # Extract PDF-specific metadata
            pdf_meta = self._extract_pdf_metadata(doc, file_path)

            # Try to extract structured data
            normalized = self._extract_structured_data(pdf_meta)

            # Add PDF metadata to extracted field
            normalized.extracted = pdf_meta.dict()
            normalized.detected_type = FileType.PDF
            normalized.source_file = filename
            normalized.confidence_score = self._calculate_confidence(pdf_meta)

            doc.close()
            return normalized

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def _extract_pdf_metadata(self, doc, file_path: str) -> PDFMetadata:
        """Extract PDF-specific metadata."""
        # Extract text from all pages
        text_content = ""
        for page in doc:
            text_content += page.get_text()

        # Extract tables using Camelot
        tables = []
        try:
            camelot_tables = camelot.read_pdf(file_path, pages='all', flavor='lattice')
            for i, table in enumerate(camelot_tables):
                tables.append({
                    'page': table.page,
                    'rows': len(table.df),
                    'columns': len(table.df.columns),
                    'data': table.df.to_dict('records')[:10]  # First 10 rows
                })
        except:
            # Fallback to stream flavor
            try:
                camelot_tables = camelot.read_pdf(file_path, pages='all', flavor='stream')
                for i, table in enumerate(camelot_tables):
                    tables.append({
                        'page': table.page,
                        'rows': len(table.df),
                        'columns': len(table.df.columns),
                        'data': table.df.to_dict('records')[:10]
                    })
            except:
                pass

        # Extract images
        images_extracted = 0
        for page in doc:
            images_extracted += len(page.get_images())

        # Detect common fields
        detected_fields = self._detect_fields(text_content)

        return PDFMetadata(
            page_count=len(doc),
            text_content=text_content[:5000],  # First 5000 chars
            tables=tables,
            images_extracted=images_extracted,
            po_number=detected_fields.get('po_number'),
            detected_fields=detected_fields
        )

    def _detect_fields(self, text: str) -> Dict[str, Any]:
        """Detect common fields in PDF text."""
        import re
        from datetime import datetime

        fields = {}

        # PO Number
        po_match = re.search(r'P[O|o][\s#:-]*(\d{4,})', text)
        if po_match:
            fields['po_number'] = po_match.group(1)

        # Due Date
        date_patterns = [
            r'due[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'delivery[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['due_date'] = match.group(1)
                break

        # Material
        material_keywords = ['mild steel', 'stainless', 'galvanized', 'aluminum', 'brass']
        for keyword in material_keywords:
            if keyword in text.lower():
                fields['material'] = keyword.title()
                break

        # Thickness
        thickness_match = re.search(r'(\d+\.?\d*)\s*mm', text)
        if thickness_match:
            fields['thickness_mm'] = float(thickness_match.group(1))

        # Quantity
        qty_match = re.search(r'qty[\s:]*(\d+)', text, re.IGNORECASE)
        if qty_match:
            fields['quantity'] = int(qty_match.group(1))

        return fields

    def _extract_structured_data(self, pdf_meta: PDFMetadata) -> NormalizedMetadata:
        """Extract structured data from PDF metadata."""
        return NormalizedMetadata(
            material=pdf_meta.detected_fields.get('material'),
            thickness_mm=pdf_meta.detected_fields.get('thickness_mm'),
            quantity=pdf_meta.detected_fields.get('quantity'),
            source_file="",
            detected_type=FileType.PDF,
            extracted={}
        )

    def _calculate_confidence(self, pdf_meta: PDFMetadata) -> float:
        """Calculate confidence score based on extracted data."""
        score = 0.5  # Base score

        if pdf_meta.po_number:
            score += 0.1
        if pdf_meta.detected_fields.get('material'):
            score += 0.1
        if pdf_meta.detected_fields.get('thickness_mm'):
            score += 0.1
        if pdf_meta.detected_fields.get('quantity'):
            score += 0.1
        if pdf_meta.tables:
            score += 0.1

        return min(score, 1.0)
```

### 3. Excel Parser

```python
# module_n/parsers/excel_parser.py

import pandas as pd
from typing import Dict, Any, List
from ..models import ExcelMetadata, NormalizedMetadata, FileType

class ExcelParser:
    """Parser for Excel files using pandas."""

    def parse(self, file_path: str, filename: str) -> NormalizedMetadata:
        """Parse Excel file and extract metadata."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)

            # Extract Excel-specific metadata
            excel_meta = self._extract_excel_metadata(excel_file)

            # Try to extract structured data
            normalized = self._extract_structured_data(excel_meta)

            # Add Excel metadata to extracted field
            normalized.extracted = excel_meta.dict()
            normalized.detected_type = FileType.EXCEL
            normalized.source_file = filename
            normalized.confidence_score = self._calculate_confidence(excel_meta)

            return normalized

        except Exception as e:
            raise ValueError(f"Failed to parse Excel: {str(e)}")

    def _extract_excel_metadata(self, excel_file) -> ExcelMetadata:
        """Extract Excel-specific metadata."""
        sheet_names = excel_file.sheet_names

        # Read first sheet
        df = excel_file.parse(sheet_names[0])

        # Get headers
        headers = df.columns.tolist()

        # Get data rows (first 100)
        data_rows = df.head(100).to_dict('records')

        # Detect schema
        detected_schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype:
                detected_schema[col] = 'integer'
            elif 'float' in dtype:
                detected_schema[col] = 'number'
            elif 'datetime' in dtype:
                detected_schema[col] = 'date'
            else:
                detected_schema[col] = 'string'

        return ExcelMetadata(
            sheet_names=sheet_names,
            row_count=len(df),
            column_count=len(df.columns),
            headers=headers,
            data_rows=data_rows,
            detected_schema=detected_schema
        )

    def _extract_structured_data(self, excel_meta: ExcelMetadata) -> NormalizedMetadata:
        """Extract structured data from Excel metadata."""
        # Look for common column names
        normalized = NormalizedMetadata(
            source_file="",
            detected_type=FileType.EXCEL,
            extracted={}
        )

        # Map common column names
        column_map = {
            'part': 'part_name',
            'part name': 'part_name',
            'material': 'material',
            'thickness': 'thickness_mm',
            'qty': 'quantity',
            'quantity': 'quantity'
        }

        # Try to find matching columns
        for header in excel_meta.headers:
            header_lower = header.lower()
            for key, field in column_map.items():
                if key in header_lower and excel_meta.data_rows:
                    value = excel_meta.data_rows[0].get(header)
                    if value:
                        setattr(normalized, field, value)

        return normalized

    def _calculate_confidence(self, excel_meta: ExcelMetadata) -> float:
        """Calculate confidence score."""
        score = 0.6  # Base score for structured data

        if excel_meta.detected_schema:
            score += 0.2
        if excel_meta.row_count > 0:
            score += 0.1
        if len(excel_meta.headers) > 3:
            score += 0.1

        return min(score, 1.0)
```

---


