"""
Shared pytest fixtures for Theo-van-Gogh tests.
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def mock_paintings_structure(temp_dir):
    """
    Create a mock paintings directory structure.
    
    Returns:
        Dict with paths to big, instagram, and metadata folders
    """
    structure = {
        "big": temp_dir / "my-paintings-big",
        "instagram": temp_dir / "my-paintings-instagram",
        "metadata": temp_dir / "processed-metadata",
    }
    
    # Create directory structure
    for path in structure.values():
        (path / "new-paintings").mkdir(parents=True)
    
    return structure


@pytest.fixture
def sample_image_file(temp_dir):
    """
    Create a sample image file for testing.
    
    Returns:
        Path to sample image
    """
    from PIL import Image
    
    img = Image.new('RGB', (800, 600), color='blue')
    img_path = temp_dir / "test_image.jpg"
    img.save(img_path)
    
    return img_path


@pytest.fixture
def sample_metadata():
    """
    Sample metadata dictionary for testing.
    
    Returns:
        Dict with sample metadata
    """
    return {
        "filename_base": "test_painting",
        "category": "new-paintings",
        "files": {
            "big": "/path/to/big/test_painting.jpg",
            "instagram": "/path/to/instagram/test_painting.jpg",
        },
        "title": {
            "selected": "Test Painting",
            "all_options": ["Test Painting", "Blue Sky", "Abstract Work", "Study in Blue", "Untitled"]
        },
        "description": "A test painting for unit tests.",
        "dimensions": {
            "width": 60.0,
            "height": 80.0,
            "depth": None,
            "unit": "cm",
            "formatted": "60cm x 80cm"
        },
        "substrate": "canvas",
        "medium": "oil",
        "subject": "abstract",
        "style": "abstract",
        "collection": "Test Collection",
        "price_eur": 100.0,
        "creation_date": "2025-02-08",
        "processed_date": "2025-02-08T10:00:00",
        "analyzed_from": "instagram"
    }


@pytest.fixture
def sample_metadata_file(temp_dir, sample_metadata):
    """
    Create a sample metadata JSON file.
    
    Returns:
        Path to metadata file
    """
    metadata_dir = temp_dir / "processed-metadata" / "new-paintings"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_file = metadata_dir / "test_painting.json"
    with open(metadata_file, 'w') as f:
        json.dump(sample_metadata, f, indent=2)
    
    return metadata_file


@pytest.fixture
def mock_anthropic_response():
    """
    Mock response from Anthropic API.
    
    Returns:
        Dict simulating API response
    """
    return {
        "content": [
            {
                "type": "text",
                "text": '["Sunset Over Mountains", "Evening Glow", "Alpine Twilight", "Golden Hour", "Mountain Vista"]'
            }
        ],
        "model": "claude-sonnet-4-20250514",
        "stop_reason": "end_turn"
    }


@pytest.fixture
def mock_upload_tracker_data():
    """
    Sample upload tracker data.
    
    Returns:
        Dict with tracker structure
    """
    return {
        "paintings": {
            "test_painting_1": {
                "metadata_path": "/path/to/metadata/test_painting_1.json",
                "processed_date": "2025-02-08T10:00:00",
                "uploads": {
                    "FASO": False,
                    "Instagram": False
                }
            },
            "test_painting_2": {
                "metadata_path": "/path/to/metadata/test_painting_2.json",
                "processed_date": "2025-02-08T11:00:00",
                "uploads": {
                    "FASO": True,
                    "Instagram": False
                }
            }
        },
        "platforms": ["FASO", "Instagram"],
        "last_updated": "2025-02-08T12:00:00"
    }


@pytest.fixture
def mock_env_file(temp_dir):
    """
    Create a mock .env file for testing.
    
    Returns:
        Path to .env file
    """
    env_file = temp_dir / ".env"
    env_content = """
ANTHROPIC_API_KEY=test_key_12345678
PAINTINGS_BIG_PATH={big_path}
PAINTINGS_INSTAGRAM_PATH={instagram_path}
METADATA_OUTPUT_PATH={metadata_path}
""".format(
        big_path=temp_dir / "my-paintings-big",
        instagram_path=temp_dir / "my-paintings-instagram",
        metadata_path=temp_dir / "processed-metadata"
    )
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    return env_file


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset any singleton instances between tests.
    Runs automatically for every test.
    """
    yield
    # Add any cleanup needed between tests


@pytest.fixture
def mock_cli_input(monkeypatch):
    """
    Mock CLI user input for testing interactive prompts.
    
    Usage:
        mock_cli_input(["1", "yes", "Test Title"])
    """
    def _mock_input(responses):
        responses_iter = iter(responses)
        
        def mock_input(*args, **kwargs):
            try:
                return next(responses_iter)
            except StopIteration:
                raise ValueError("Not enough mock responses provided")
        
        monkeypatch.setattr('builtins.input', mock_input)
        return mock_input
    
    return _mock_input
