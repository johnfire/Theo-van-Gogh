"""
Configuration settings for the art processor.
All extensible lists are defined here for easy modification.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# File Paths
PAINTINGS_BIG_PATH = Path(os.getenv("PAINTINGS_BIG_PATH", "~/Pictures/my-paintings-big")).expanduser()
PAINTINGS_INSTAGRAM_PATH = Path(os.getenv("PAINTINGS_INSTAGRAM_PATH", "~/Pictures/my-paintings-instagram")).expanduser()
METADATA_OUTPUT_PATH = Path(os.getenv("METADATA_OUTPUT_PATH", "~/Pictures/processed-metadata")).expanduser()

# ============================================================================
# MEASUREMENT UNITS
# ============================================================================
# Default unit for dimensions
# Options: "cm" for centimeters or "in" for inches
DIMENSION_UNIT = "cm"

# ============================================================================
# EXTENSIBLE ARTWORK METADATA FIELDS
# Add new options to any of these lists as needed
# ============================================================================

# Substrate options
SUBSTRATES = [
    "paper",
    "board",
    "canvas",
    "linen",
]

# Medium options
MEDIUMS = [
    "acrylic",
    "oil",
    "watercolor",
    "pen and ink",
    "pencil",
]

# Subject options
SUBJECTS = [
    "abstract",
    "landscape",
    "cityscape",
    "sea beasties",
    "fantasy",
    "portrait",
]

# Style options
STYLES = [
    "abstract",
    "figurative",
    "surrealism",
    "impressionism",
    "landscape",
    "cityscape",
]

# Collection options
COLLECTIONS = [
    "Sea Beasties from Titan",
    "Fachwerkhauser",
    "imaginary places",
    "oils",
    "abstracts",
]

# Extensible Categories (legacy - kept for backwards compatibility)
CATEGORIES = [
    "abstract",
    "landscapes",
    "cityscapes",
    "fantasy",
    "botanicals",
    "surreal",
]

# Image Processing Settings
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png"]
MAX_IMAGE_SIZE_MB = 100  # Maximum file size for processing

# AI Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000

# File Naming
SANITIZE_RULES = {
    " ": "_",
    ":": "",
    ";": "",
    "?": "",
    "!": "",
    "/": "_",
    "\\": "_",
    "*": "",
    '"': "",
    "'": "",
    "<": "",
    ">": "",
    "|": "",
}

# Ensure output directory exists
METADATA_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
