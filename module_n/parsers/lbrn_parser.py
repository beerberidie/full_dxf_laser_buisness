"""
Module N - LightBurn Parser
Extracts metadata from LightBurn (.lbrn2) files using XML parsing
"""

import xml.etree.ElementTree as ET
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from decimal import Decimal

from ..models.schemas import (
    NormalizedMetadata,
    FileType,
    MATERIAL_MAP,
    MATERIAL_CODE_MAP
)

logger = logging.getLogger(__name__)


class LBRNParser:
    """Parser for LightBurn files (.lbrn2) using XML parsing."""
    
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
        Parse LightBurn file and extract comprehensive metadata.
        
        Args:
            file_path: Path to the LightBurn file
            filename: Original filename
            client_code: Optional client code override
            project_code: Optional project code override
            
        Returns:
            NormalizedMetadata object with extracted data
        """
        try:
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract LightBurn-specific metadata
            lbrn_meta = self._extract_lbrn_metadata(root)
            
            # Parse filename for metadata
            filename_meta = self._parse_filename(filename)
            
            # Enhance metadata from LightBurn content
            enhanced_meta = self._enhance_from_lbrn(lbrn_meta, filename_meta)
            
            # Override with provided codes
            if client_code:
                enhanced_meta.client_code = client_code
            if project_code:
                enhanced_meta.project_code = project_code
            
            # Add LightBurn metadata to extracted field
            enhanced_meta.extracted = {
                'app_version': lbrn_meta.get('app_version', 'Unknown'),
                'device_name': lbrn_meta.get('device_name', 'Unknown'),
                'material_height': lbrn_meta.get('material_height', 0),
                'cut_settings': lbrn_meta.get('cut_settings', []),
                'layer_count': lbrn_meta.get('layer_count', 0),
                'shape_count': lbrn_meta.get('shape_count', 0),
                'shape_types': lbrn_meta.get('shape_types', {}),
                'bounding_box': lbrn_meta.get('bounding_box', {}),
                'text_elements': lbrn_meta.get('text_elements', []),
            }
            
            # Calculate confidence score
            enhanced_meta.confidence_score = self._calculate_confidence(enhanced_meta)
            
            # Set file type
            enhanced_meta.detected_type = FileType.LBRN2
            enhanced_meta.source_file = filename
            
            # Get file size
            enhanced_meta.file_size = Path(file_path).stat().st_size
            enhanced_meta.mime_type = 'application/xml'
            
            logger.info(f"LightBurn parsed successfully: {filename} (confidence: {enhanced_meta.confidence_score:.2f})")
            return enhanced_meta
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse LightBurn XML {filename}: {str(e)}")
            raise ValueError(f"Failed to parse LightBurn XML: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse LightBurn {filename}: {str(e)}")
            raise ValueError(f"Failed to parse LightBurn: {str(e)}")
    
    def _extract_lbrn_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """Extract LightBurn-specific metadata from XML root."""
        metadata = {}
        
        try:
            # Get root attributes
            metadata['app_version'] = root.get('AppVersion', 'Unknown')
            metadata['device_name'] = root.get('DeviceName', 'Unknown')
            metadata['material_height'] = float(root.get('MaterialHeight', 0))
            
            # Extract cut settings
            cut_settings = []
            for cut_setting in root.findall('.//CutSetting'):
                setting = {
                    'type': cut_setting.get('type', 'Unknown'),
                    'name': cut_setting.find('name').get('Value') if cut_setting.find('name') is not None else 'Unknown',
                    'max_power': float(cut_setting.find('maxPower').get('Value', 0)) if cut_setting.find('maxPower') is not None else 0,
                    'speed': float(cut_setting.find('speed').get('Value', 0)) if cut_setting.find('speed') is not None else 0,
                }
                cut_settings.append(setting)
            metadata['cut_settings'] = cut_settings
            metadata['layer_count'] = len(cut_settings)
            
            # Count shapes and types
            shapes = root.findall('.//Shape')
            metadata['shape_count'] = len(shapes)
            
            shape_types = {}
            for shape in shapes:
                shape_type = shape.get('Type', 'Unknown')
                shape_types[shape_type] = shape_types.get(shape_type, 0) + 1
            metadata['shape_types'] = shape_types
            
            # Extract text elements
            text_elements = []
            for text_shape in root.findall('.//Shape[@Type="Text"]'):
                text_elem = text_shape.find('.//Text')
                if text_elem is not None:
                    text_elements.append(text_elem.text or '')
            metadata['text_elements'] = text_elements
            
            # Calculate bounding box (simplified - would need full shape parsing for accuracy)
            # For now, extract from XForm elements if available
            metadata['bounding_box'] = self._calculate_bounding_box(root)
            
            # Collect all text for pattern matching
            all_text = []
            all_text.extend(text_elements)
            all_text.append(metadata['device_name'])
            metadata['all_text'] = ' '.join(all_text)
            
        except Exception as e:
            logger.warning(f"Error extracting LightBurn metadata: {str(e)}")
        
        return metadata
    
    def _calculate_bounding_box(self, root: ET.Element) -> Dict[str, float]:
        """Calculate approximate bounding box from shapes."""
        # This is a simplified version - full implementation would parse all shape coordinates
        bbox = {
            'width': 0.0,
            'height': 0.0,
            'min_x': 0.0,
            'min_y': 0.0,
            'max_x': 0.0,
            'max_y': 0.0
        }
        
        try:
            # Look for XForm elements and extract coordinates
            xforms = root.findall('.//XForm')
            if xforms:
                x_coords = []
                y_coords = []
                
                for xform in xforms[:10]:  # Sample first 10 for performance
                    text = xform.text or ''
                    parts = text.split()
                    if len(parts) >= 6:
                        try:
                            x_coords.append(float(parts[4]))
                            y_coords.append(float(parts[5]))
                        except (ValueError, IndexError):
                            continue
                
                if x_coords and y_coords:
                    bbox['min_x'] = min(x_coords)
                    bbox['max_x'] = max(x_coords)
                    bbox['min_y'] = min(y_coords)
                    bbox['max_y'] = max(y_coords)
                    bbox['width'] = bbox['max_x'] - bbox['min_x']
                    bbox['height'] = bbox['max_y'] - bbox['min_y']
        
        except Exception as e:
            logger.warning(f"Error calculating bounding box: {str(e)}")
        
        return bbox
    
    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """Parse metadata from filename."""
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.lbrn2
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
                detected_type=FileType.LBRN2,
                client_code=match.group(1),
                project_code=match.group(2),
                part_name=match.group(3),
                material=material,
                thickness_mm=float(match.group(5)),
                quantity=int(match.group(6)),
                version=int(match.group(7)),
                extracted={}
            )
        
        # Try old format: 0001-Full Gas Box-Galv-1mm-x1.lbrn2
        pattern2 = r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)$'
        match = re.match(pattern2, name_without_ext, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.LBRN2,
                part_name=match.group(2),
                material=MATERIAL_MAP.get(match.group(3), 'Other'),
                thickness_mm=float(match.group(4)),
                quantity=int(match.group(5)),
                extracted={}
            )
        
        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.LBRN2,
            extracted={}
        )

    def _enhance_from_lbrn(self, lbrn_meta: Dict[str, Any],
                           filename_meta: NormalizedMetadata) -> NormalizedMetadata:
        """Enhance metadata using LightBurn content."""
        # Start with filename metadata
        enhanced = filename_meta

        # Get all text for pattern matching
        all_text = lbrn_meta.get('all_text', '')

        # Detect from text if not found in filename
        if not enhanced.material:
            material = self._detect_material_from_text(all_text)
            if material:
                enhanced.material = material

        if not enhanced.thickness_mm:
            thickness = self._detect_thickness_from_text(all_text)
            if thickness:
                enhanced.thickness_mm = thickness
            elif lbrn_meta.get('material_height', 0) > 0:
                # Use material height from LightBurn if available
                enhanced.thickness_mm = lbrn_meta['material_height']

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

        # Try to extract part name from text elements
        if not enhanced.part_name:
            text_elements = lbrn_meta.get('text_elements', [])
            if text_elements:
                # Use first non-empty text element
                for text in text_elements:
                    if text and len(text) > 2:
                        enhanced.part_name = text[:50]  # Limit length
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

        # Add points for LightBurn-specific data
        extracted = metadata.extracted or {}
        if extracted.get('layer_count', 0) > 0:
            score += 0.05
        if extracted.get('shape_count', 0) > 0:
            score += 0.05

        return min(score, 1.0)

