"""
Metadata management module.
Handles creation of JSON and text metadata files.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from config.settings import METADATA_OUTPUT_PATH


class MetadataManager:
    """Manages artwork metadata files."""
    
    def __init__(self):
        """Initialize metadata manager."""
        self.output_path = METADATA_OUTPUT_PATH
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def create_metadata(
        self,
        filename_base: str,
        category: str,
        big_file_path: Path,
        instagram_file_path: Path,
        selected_title: str,
        all_titles: List[str],
        description: str,
        dimensions: str,
        medium: str,
        price_eur: float,
        creation_date: str,
    ) -> Dict[str, Any]:
        """
        Create metadata dictionary.
        
        Args:
            filename_base: Base filename without extension
            category: Artwork category
            big_file_path: Path to big version
            instagram_file_path: Path to instagram version
            selected_title: The title selected by user
            all_titles: All 5 generated title options
            description: Gallery description
            dimensions: Dimensions string
            medium: Medium used
            price_eur: Price in euros
            creation_date: Creation date
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "filename_base": filename_base,
            "category": category,
            "files": {
                "big": str(big_file_path),
                "instagram": str(instagram_file_path) if instagram_file_path else None,
            },
            "title": {
                "selected": selected_title,
                "all_options": all_titles,
            },
            "description": description,
            "dimensions": dimensions,
            "medium": medium,
            "price_eur": price_eur,
            "creation_date": creation_date,
            "processed_date": datetime.now().isoformat(),
            "analyzed_from": "big",
        }
        
        return metadata
    
    def save_metadata_json(self, metadata: Dict[str, Any], category: str) -> Path:
        """
        Save metadata as JSON file.
        
        Args:
            metadata: Metadata dictionary
            category: Category name for subfolder
            
        Returns:
            Path to saved JSON file
        """
        # Create category subfolder
        category_path = self.output_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = category_path / f"{metadata['filename_base']}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return json_path
    
    def save_metadata_text(self, metadata: Dict[str, Any], category: str) -> Path:
        """
        Save human-readable text version of metadata.
        
        Args:
            metadata: Metadata dictionary
            category: Category name for subfolder
            
        Returns:
            Path to saved text file
        """
        # Create category subfolder
        category_path = self.output_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Format text content
        text_content = f"""ARTWORK METADATA
{'=' * 60}

Title: {metadata['title']['selected']}
Category: {metadata['category']}
Medium: {metadata['medium']}
Dimensions: {metadata['dimensions']}
Price: €{metadata['price_eur']}
Creation Date: {metadata['creation_date']}

DESCRIPTION
{'-' * 60}
{metadata['description']}

ALTERNATIVE TITLES
{'-' * 60}
"""
        
        for i, title in enumerate(metadata['title']['all_options'], 1):
            text_content += f"{i}. {title}\n"
        
        text_content += f"""
FILES
{'-' * 60}
Big Version: {metadata['files']['big']}
Instagram Version: {metadata['files']['instagram'] or 'N/A'}

PROCESSING INFO
{'-' * 60}
Processed: {metadata['processed_date']}
Analyzed From: {metadata['analyzed_from']}
"""
        
        # Save text file
        txt_path = category_path / f"{metadata['filename_base']}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return txt_path
    
    def load_metadata(self, category: str, filename_base: str) -> Dict[str, Any]:
        """
        Load existing metadata from JSON file.
        
        Args:
            category: Category name
            filename_base: Base filename
            
        Returns:
            Metadata dictionary
        """
        json_path = self.output_path / category / f"{filename_base}.json"
        
        if not json_path.exists():
            raise FileNotFoundError(f"Metadata not found: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def metadata_exists(self, category: str, filename_base: str) -> bool:
        """
        Check if metadata already exists for a file.
        
        Args:
            category: Category name
            filename_base: Base filename
            
        Returns:
            True if metadata exists
        """
        json_path = self.output_path / category / f"{filename_base}.json"
        return json_path.exists()
