"""
Module N - PDF Parser
Extracts metadata from PDF files using PyMuPDF (fitz) and Camelot
"""

import fitz  # PyMuPDF
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from ..models.schemas import (
    PDFMetadata,
    NormalizedMetadata,
    FileType,
    MATERIAL_MAP,
    MATERIAL_CODE_MAP
)

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF files using PyMuPDF (fitz) and Camelot."""
    
    # Material detection patterns (reuse from DXF parser)
    MATERIAL_PATTERNS = {
        'Galvanized Steel': ['galv', 'galvanized'],
        'Stainless Steel': ['stainless', 'inox', 'ss '],
        'Mild Steel': ['mild steel', 'mild', 'ms '],
        'Aluminum': ['aluminum', 'aluminium', 'alu', 'al '],
        'Brass': ['brass'],
        'Copper': ['copper'],
        'Carbon Steel': ['carbon steel', 'carbon'],
    }
    
    # Thickness detection patterns
    THICKNESS_PATTERN = re.compile(
        r't[=:\s]*(\d+\.?\d*)\s*mm|(\d+\.?\d*)\s*mm|thickness[:\s]*(\d+\.?\d*)',
        re.IGNORECASE
    )
    
    # Quantity detection patterns
    QUANTITY_PATTERN = re.compile(
        r'qty[:\s]*(\d+)|quantity[:\s]*(\d+)|x\s*(\d+)|(\d+)\s*pcs?',
        re.IGNORECASE
    )
    
    # Client/Project code patterns
    CLIENT_CODE_PATTERN = re.compile(r'CL[-\s]?(\d{4})', re.IGNORECASE)
    PROJECT_CODE_PATTERN = re.compile(
        r'(JB|PR|PO)[-\s]?(\d{4}[-\s]\d{2}[-\s]\w+[-\s]\d{3})',
        re.IGNORECASE
    )
    
    def parse(self, file_path: str, filename: str, client_code: Optional[str] = None,
              project_code: Optional[str] = None) -> NormalizedMetadata:
        """
        Parse PDF file and extract comprehensive metadata.
        
        Args:
            file_path: Path to the PDF file
            filename: Original filename
            client_code: Optional client code override
            project_code: Optional project code override
            
        Returns:
            NormalizedMetadata object with extracted data
        """
        try:
            # Open PDF document
            doc = fitz.open(file_path)
            
            # Extract PDF-specific metadata
            pdf_meta = self._extract_pdf_metadata(doc, file_path)
            
            # Parse filename for metadata
            filename_meta = self._parse_filename(filename)
            
            # Enhance metadata from PDF content
            enhanced_meta = self._enhance_from_pdf(pdf_meta, filename_meta)
            
            # Override with provided codes
            if client_code:
                enhanced_meta.client_code = client_code
            if project_code:
                enhanced_meta.project_code = project_code
            
            # Add PDF metadata to extracted field
            enhanced_meta.extracted = {
                'page_count': pdf_meta.get('page_count', 0),
                'text_content': pdf_meta.get('text_content', ''),
                'tables': pdf_meta.get('tables', []),
                'images_count': pdf_meta.get('images_count', 0),
                'pdf_metadata': pdf_meta.get('metadata', {}),
                'pdf_version': pdf_meta.get('pdf_version'),
            }
            
            # Calculate confidence score
            enhanced_meta.confidence_score = self._calculate_confidence(enhanced_meta)
            
            # Set file type
            enhanced_meta.detected_type = FileType.PDF
            enhanced_meta.source_file = filename
            
            # Get file size
            enhanced_meta.file_size = Path(file_path).stat().st_size
            enhanced_meta.mime_type = 'application/pdf'
            
            doc.close()
            
            logger.info(f"PDF parsed successfully: {filename} (confidence: {enhanced_meta.confidence_score:.2f})")
            return enhanced_meta
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {filename}: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def _extract_pdf_metadata(self, doc: fitz.Document, file_path: str) -> Dict[str, Any]:
        """Extract PDF-specific metadata from document."""
        metadata = {}
        
        try:
            # Basic document info
            metadata['page_count'] = len(doc)
            metadata['pdf_version'] = doc.metadata.get('format', 'Unknown')
            
            # Document metadata
            metadata['metadata'] = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'mod_date': doc.metadata.get('modDate', ''),
            }
            
            # Extract text from all pages
            text_content = []
            images_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    text_content.append(page_text)
                
                # Count images
                images_count += len(page.get_images())
            
            metadata['text_content'] = '\n'.join(text_content)
            metadata['images_count'] = images_count
            
            # Try to extract tables using Camelot (if available)
            metadata['tables'] = self._extract_tables(file_path)
            
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def _extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF using Camelot."""
        tables = []
        
        try:
            import camelot
            
            # Extract tables from all pages
            table_list = camelot.read_pdf(file_path, pages='all', flavor='lattice')
            
            for i, table in enumerate(table_list):
                tables.append({
                    'table_number': i + 1,
                    'page': table.page,
                    'rows': len(table.df),
                    'columns': len(table.df.columns),
                    'data': table.df.to_dict('records') if len(table.df) < 100 else [],
                    'accuracy': table.accuracy,
                })
            
            logger.info(f"Extracted {len(tables)} tables from PDF")
            
        except ImportError:
            logger.warning("Camelot not available for table extraction")
        except Exception as e:
            logger.warning(f"Failed to extract tables: {str(e)}")
        
        return tables
    
    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """Parse metadata from filename."""
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.pdf
        pattern1 = r'^(CL\d{4})-([\w-]+)-([\w-]+)-([A-Z]+)-(\d+\.?\d*)mm-x(\d+)-v(\d+)$'
        match = re.match(pattern1, name_without_ext, re.IGNORECASE)
        
        if match:
            material_code = match.group(4)
            material = None
            for full_name, code in MATERIAL_CODE_MAP.items():
                if material_code.upper() == code.upper():
                    material = full_name
                    break
            
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.PDF,
                client_code=match.group(1),
                project_code=match.group(2),
                part_name=match.group(3),
                material=material,
                thickness_mm=float(match.group(5)),
                quantity=int(match.group(6)),
                version=int(match.group(7)),
                extracted={}
            )
        
        # Try old format: 0001-Full Gas Box-Galv-1mm-x1.pdf
        pattern2 = r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)$'
        match = re.match(pattern2, name_without_ext, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.PDF,
                part_name=match.group(2),
                material=MATERIAL_MAP.get(match.group(3), 'Other'),
                thickness_mm=float(match.group(4)),
                quantity=int(match.group(5)),
                extracted={}
            )
        
        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.PDF,
            extracted={}
        )
    
    def _enhance_from_pdf(self, pdf_meta: Dict[str, Any], 
                          filename_meta: NormalizedMetadata) -> NormalizedMetadata:
        """Enhance metadata using PDF content."""
        text_content = pdf_meta.get('text_content', '')
        
        # Start with filename metadata
        enhanced = filename_meta
        
        # Detect material from text if not already set
        if not enhanced.material:
            material = self._detect_material_from_text(text_content)
            if material:
                enhanced.material = material
        
        # Detect thickness from text if not already set
        if not enhanced.thickness_mm:
            thickness = self._detect_thickness_from_text(text_content)
            if thickness:
                enhanced.thickness_mm = thickness
        
        # Detect quantity from text if not already set
        if enhanced.quantity == 1:
            quantity = self._detect_quantity_from_text(text_content)
            if quantity:
                enhanced.quantity = quantity
        
        # Detect client code from text if not already set
        if not enhanced.client_code:
            client_code = self._detect_client_code(text_content)
            if client_code:
                enhanced.client_code = client_code
        
        # Detect project code from text if not already set
        if not enhanced.project_code:
            project_code = self._detect_project_code(text_content)
            if project_code:
                enhanced.project_code = project_code
        
        # Try to extract part name from PDF title or text
        if not enhanced.part_name:
            part_name = self._detect_part_name(pdf_meta, text_content)
            if part_name:
                enhanced.part_name = part_name

        return enhanced

    def _detect_material_from_text(self, text: str) -> Optional[str]:
        """Detect material from text content."""
        text_lower = text.lower()

        # Check patterns in order (more specific first)
        for material, patterns in self.MATERIAL_PATTERNS.items():
            for pattern in patterns:
                # For short codes like 'ss ', 'ms ', check word boundaries
                if pattern.endswith(' '):
                    # Check if pattern appears at start or after a space
                    if text_lower.startswith(pattern.strip() + ' ') or ' ' + pattern in text_lower:
                        return material
                else:
                    # For longer patterns, simple substring match
                    if pattern in text_lower:
                        return material

        return None

    def _detect_thickness_from_text(self, text: str) -> Optional[float]:
        """Detect thickness from text content."""
        match = self.THICKNESS_PATTERN.search(text)
        if match:
            # Extract the first non-None group
            for group in match.groups():
                if group:
                    try:
                        return float(group)
                    except ValueError:
                        continue
        return None

    def _detect_quantity_from_text(self, text: str) -> Optional[int]:
        """Detect quantity from text content."""
        match = self.QUANTITY_PATTERN.search(text)
        if match:
            # Extract the first non-None group
            for group in match.groups():
                if group:
                    try:
                        qty = int(group)
                        # Sanity check: quantity should be reasonable
                        if 1 <= qty <= 10000:
                            return qty
                    except ValueError:
                        continue
        return None

    def _detect_client_code(self, text: str) -> Optional[str]:
        """Detect client code from text content."""
        match = self.CLIENT_CODE_PATTERN.search(text)
        if match:
            return f"CL{match.group(1)}"
        return None

    def _detect_project_code(self, text: str) -> Optional[str]:
        """Detect project code from text content."""
        match = self.PROJECT_CODE_PATTERN.search(text)
        if match:
            # Normalize the project code format
            prefix = match.group(1).upper()
            code = match.group(2).replace(' ', '-')
            return f"{prefix}-{code}"
        return None

    def _detect_part_name(self, pdf_meta: Dict[str, Any], text: str) -> Optional[str]:
        """Detect part name from PDF metadata or text."""
        # Try PDF title first
        title = pdf_meta.get('metadata', {}).get('title', '')
        if title and len(title) > 3 and len(title) < 100:
            # Clean up title
            title = title.strip()
            # Remove common suffixes
            title = re.sub(r'\.(pdf|dxf|lbrn2)$', '', title, flags=re.IGNORECASE)
            return title

        # Try to find part name in first few lines of text
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            # Look for lines that might be part names (not too short, not too long)
            if 5 <= len(line) <= 50:
                # Skip lines that look like headers or metadata
                if not any(keyword in line.lower() for keyword in
                          ['page', 'date', 'quote', 'invoice', 'total', 'price']):
                    return line

        return None

    def _calculate_confidence(self, metadata: NormalizedMetadata) -> float:
        """Calculate confidence score based on extracted metadata completeness."""
        score = 0.0

        # Base score for successful parsing
        score += 0.2

        # Add points for each field
        if metadata.client_code:
            score += 0.1
        if metadata.project_code:
            score += 0.1
        if metadata.part_name:
            score += 0.15
        if metadata.material:
            score += 0.15
        if metadata.thickness_mm:
            score += 0.15
        if metadata.quantity and metadata.quantity > 1:
            score += 0.05

        # Add points for PDF-specific data
        extracted = metadata.extracted or {}
        if extracted.get('page_count', 0) > 0:
            score += 0.05
        if extracted.get('tables'):
            score += 0.05

        return min(score, 1.0)

