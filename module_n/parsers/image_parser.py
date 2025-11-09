"""
Module N - Image Parser
Extracts metadata from image files (PNG, JPG, BMP, TIFF) using Pillow and Tesseract OCR
"""

import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image, ImageEnhance
import io

from ..models.schemas import (
    NormalizedMetadata,
    FileType,
    MATERIAL_MAP,
    MATERIAL_CODE_MAP
)

logger = logging.getLogger(__name__)

# Try to import pytesseract, but handle gracefully if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - OCR functionality will be disabled")


class ImageParser:
    """Parser for image files (PNG, JPG, BMP, TIFF) using Pillow and optional Tesseract OCR."""
    
    # Material detection patterns (reuse from other parsers)
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
        Parse image file and extract comprehensive metadata.
        
        Args:
            file_path: Path to the image file
            filename: Original filename
            client_code: Optional client code override
            project_code: Optional project code override
            
        Returns:
            NormalizedMetadata object with extracted data
        """
        try:
            # Open image
            img = Image.open(file_path)
            
            # Extract image-specific metadata
            image_meta = self._extract_image_metadata(img, file_path)
            
            # Parse filename for metadata
            filename_meta = self._parse_filename(filename)
            
            # Enhance metadata from image content (OCR)
            enhanced_meta = self._enhance_from_image(image_meta, filename_meta, img)
            
            # Override with provided codes
            if client_code:
                enhanced_meta.client_code = client_code
            if project_code:
                enhanced_meta.project_code = project_code
            
            # Add image metadata to extracted field
            enhanced_meta.extracted = {
                'width': image_meta.get('width', 0),
                'height': image_meta.get('height', 0),
                'format': image_meta.get('format', 'Unknown'),
                'mode': image_meta.get('mode', 'Unknown'),
                'dpi': image_meta.get('dpi', (0, 0)),
                'exif': image_meta.get('exif', {}),
                'ocr_text': image_meta.get('ocr_text', ''),
                'ocr_available': image_meta.get('ocr_available', False),
            }
            
            # Calculate confidence score
            enhanced_meta.confidence_score = self._calculate_confidence(enhanced_meta)
            
            # Set file type
            enhanced_meta.detected_type = FileType.IMAGE
            enhanced_meta.source_file = filename
            
            # Get file size
            enhanced_meta.file_size = Path(file_path).stat().st_size
            enhanced_meta.mime_type = self._get_mime_type(filename, image_meta.get('format'))
            
            img.close()
            
            logger.info(f"Image parsed successfully: {filename} (confidence: {enhanced_meta.confidence_score:.2f})")
            return enhanced_meta
            
        except Exception as e:
            logger.error(f"Failed to parse image {filename}: {str(e)}")
            raise ValueError(f"Failed to parse image: {str(e)}")
    
    def _extract_image_metadata(self, img: Image.Image, file_path: str) -> Dict[str, Any]:
        """Extract image-specific metadata."""
        metadata = {}
        
        try:
            # Basic image properties
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['format'] = img.format or 'Unknown'
            metadata['mode'] = img.mode
            
            # DPI information
            dpi = img.info.get('dpi', (0, 0))
            metadata['dpi'] = dpi
            
            # Extract EXIF data if available
            exif_data = {}
            try:
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        # Convert to string to avoid serialization issues
                        exif_data[str(tag_id)] = str(value)[:100]  # Limit length
            except (AttributeError, KeyError):
                pass
            metadata['exif'] = exif_data
            
            # Perform OCR if Tesseract is available
            ocr_text = ''
            ocr_available = False
            
            if TESSERACT_AVAILABLE:
                try:
                    # Preprocess image for better OCR
                    processed_img = self._preprocess_for_ocr(img)
                    ocr_text = pytesseract.image_to_string(processed_img)
                    ocr_available = True
                    logger.info(f"OCR extracted {len(ocr_text)} characters")
                except Exception as ocr_error:
                    logger.warning(f"OCR failed: {str(ocr_error)}")
                    ocr_text = ''
            
            metadata['ocr_text'] = ocr_text
            metadata['ocr_available'] = ocr_available
            metadata['all_text'] = ocr_text
            
        except Exception as e:
            logger.warning(f"Error extracting image metadata: {str(e)}")
        
        return metadata
    
    def _preprocess_for_ocr(self, img: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if img.mode != 'L':
                img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            return img
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            return img
    
    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """Parse metadata from filename."""
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.png
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
                detected_type=FileType.IMAGE,
                client_code=match.group(1),
                project_code=match.group(2),
                part_name=match.group(3),
                material=material,
                thickness_mm=float(match.group(5)),
                quantity=int(match.group(6)),
                version=int(match.group(7)),
                extracted={}
            )
        
        # Try old format: 0001-Full Gas Box-Galv-1mm-x1.png
        pattern2 = r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)$'
        match = re.match(pattern2, name_without_ext, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.IMAGE,
                part_name=match.group(2),
                material=MATERIAL_MAP.get(match.group(3), 'Other'),
                thickness_mm=float(match.group(4)),
                quantity=int(match.group(5)),
                extracted={}
            )
        
        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.IMAGE,
            extracted={}
        )
    
    def _enhance_from_image(self, image_meta: Dict[str, Any],
                            filename_meta: NormalizedMetadata,
                            img: Image.Image) -> NormalizedMetadata:
        """Enhance metadata using image content (OCR)."""
        # Start with filename metadata
        enhanced = filename_meta
        
        # Get OCR text for pattern matching
        all_text = image_meta.get('all_text', '')
        
        # Only attempt detection if OCR text is available
        if all_text:
            # Detect from text if not found in filename
            if not enhanced.material:
                material = self._detect_material_from_text(all_text)
                if material:
                    enhanced.material = material
            
            if not enhanced.thickness_mm:
                thickness = self._detect_thickness_from_text(all_text)
                if thickness:
                    enhanced.thickness_mm = thickness
            
            if enhanced.quantity == 1:
                quantity = self._detect_quantity_from_text(all_text)
                if quantity:
                    enhanced.quantity = quantity
            
            if not enhanced.client_code:
                client_code = self._detect_client_code(all_text)
                if client_code:
                    enhanced.client_code = client_code
            
            if not enhanced.project_code:
                project_code = self._detect_project_code(all_text)
                if project_code:
                    enhanced.project_code = project_code
            
            # Try to extract part name from OCR text
            if not enhanced.part_name:
                # Look for lines that might be part names (simple heuristic)
                lines = all_text.split('\n')
                for line in lines[:5]:  # Check first 5 lines
                    line = line.strip()
                    if 5 < len(line) < 50 and not line.isdigit():
                        enhanced.part_name = line
                        break

        return enhanced

    def _detect_material_from_text(self, text: str) -> Optional[str]:
        """Detect material from text content."""
        text_lower = text.lower()

        # Check patterns in order (more specific first)
        for material, patterns in self.MATERIAL_PATTERNS.items():
            for pattern in patterns:
                # For short codes like 'ss ', 'ms ', check word boundaries
                if pattern.endswith(' '):
                    if text_lower.startswith(pattern.strip() + ' ') or ' ' + pattern in text_lower:
                        return material
                else:
                    if pattern in text_lower:
                        return material

        return None

    def _detect_thickness_from_text(self, text: str) -> Optional[float]:
        """Detect thickness from text content."""
        match = self.THICKNESS_PATTERN.search(text)
        if match:
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
            for group in match.groups():
                if group:
                    try:
                        qty = int(group)
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
            prefix = match.group(1).upper()
            code = match.group(2).replace(' ', '-')
            return f"{prefix}-{code}"
        return None

    def _get_mime_type(self, filename: str, image_format: Optional[str]) -> str:
        """Get MIME type based on file extension or image format."""
        ext = Path(filename).suffix.lower()

        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.gif': 'image/gif',
        }

        return mime_types.get(ext, 'image/unknown')

    def _calculate_confidence(self, metadata: NormalizedMetadata) -> float:
        """Calculate confidence score based on extracted metadata completeness."""
        score = 0.0

        # Base score for successful parsing
        score += 0.15  # Lower base score for images due to OCR uncertainty

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

        # Add points for image-specific data
        extracted = metadata.extracted or {}
        if extracted.get('width', 0) > 0 and extracted.get('height', 0) > 0:
            score += 0.05

        # Bonus for successful OCR
        if extracted.get('ocr_available', False) and extracted.get('ocr_text', ''):
            score += 0.1
        else:
            # Penalty if OCR not available (less reliable)
            score -= 0.1

        return max(min(score, 1.0), 0.0)  # Clamp between 0 and 1

