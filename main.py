#!/usr/bin/env python3
"""
Art Processor - Main CLI Entry Point
Orchestrates the complete painting processing workflow.
"""

import sys
from pathlib import Path

import click
from rich.console import Console

from src.image_analyzer import ImageAnalyzer
from src.file_manager import FileManager
from src.metadata_manager import MetadataManager
from src.cli_interface import CLIInterface
from config.settings import PAINTINGS_BIG_PATH, PAINTINGS_INSTAGRAM_PATH


console = Console()


@click.group()
def cli():
    """Art Processor - Automated painting metadata generation and management."""
    pass


@cli.command()
@click.option(
    '--category',
    '-c',
    help='Category folder to process (e.g., landscapes, abstract)',
)
@click.option(
    '--all',
    'process_all',
    is_flag=True,
    help='Process all categories',
)
def process(category: str, process_all: bool):
    """
    Process paintings: generate titles, descriptions, and metadata.
    
    Examples:
        python main.py process --category landscapes
        python main.py process --all
    """
    try:
        # Initialize components
        ui = CLIInterface()
        file_mgr = FileManager()
        analyzer = ImageAnalyzer()
        metadata_mgr = MetadataManager()
        
        ui.print_header("Art Processor - Phase 1")
        
        # Verify paths exist
        if not PAINTINGS_BIG_PATH.exists():
            ui.print_error(f"Big paintings folder not found: {PAINTINGS_BIG_PATH}")
            ui.print_info("Please update PAINTINGS_BIG_PATH in your .env file")
            return
        
        # Get available categories
        available_categories = file_mgr.get_available_categories()
        
        if not available_categories:
            ui.print_error("No categories found in paintings folder")
            return
        
        # Determine which categories to process
        if process_all:
            categories_to_process = available_categories
        elif category:
            if category not in available_categories:
                ui.print_error(f"Category '{category}' not found")
                ui.print_info(f"Available categories: {', '.join(available_categories)}")
                return
            categories_to_process = [category]
        else:
            # Interactive selection
            selected_cat = ui.select_category(available_categories)
            if not selected_cat:
                ui.print_warning("Processing cancelled")
                return
            categories_to_process = [selected_cat]
        
        # Process each category
        for cat in categories_to_process:
            ui.print_header(f"Processing Category: {cat}")
            
            # Find all paintings in category
            painting_pairs = file_mgr.find_painting_files(cat)
            
            if not painting_pairs:
                ui.print_warning(f"No paintings found in {cat}")
                continue
            
            ui.print_info(f"Found {len(painting_pairs)} painting(s)")
            
            # Process each painting
            for big_file, instagram_file in painting_pairs:
                process_single_painting(
                    big_file,
                    instagram_file,
                    cat,
                    ui,
                    file_mgr,
                    analyzer,
                    metadata_mgr,
                )
        
        ui.print_success("\nProcessing complete!")
        
    except KeyboardInterrupt:
        ui.print_warning("\nProcessing interrupted by user")
        sys.exit(0)
    except Exception as e:
        ui.print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def process_single_painting(
    big_file: Path,
    instagram_file: Path,
    category: str,
    ui: CLIInterface,
    file_mgr: FileManager,
    analyzer: ImageAnalyzer,
    metadata_mgr: MetadataManager,
):
    """
    Process a single painting through the complete workflow.
    
    Args:
        big_file: Path to big version
        instagram_file: Path to instagram version (or None)
        category: Category name
        ui: CLI interface
        file_mgr: File manager
        analyzer: Image analyzer
        metadata_mgr: Metadata manager
    """
    ui.print_header(f"\nProcessing: {big_file.name}")
    ui.show_file_info(big_file, instagram_file)
    
    # Check if already processed
    filename_stem = big_file.stem
    if metadata_mgr.metadata_exists(category, filename_stem):
        skip = not ui.confirm_processing(
            f"Metadata already exists for {big_file.name}. Reprocess?"
        )
        if skip:
            ui.print_info("Skipping")
            return
    else:
        # Ask for confirmation
        if not ui.confirm_processing(big_file.name):
            ui.print_info("Skipping")
            return
    
    try:
        # Import DIMENSION_UNIT from settings
        from config.settings import DIMENSION_UNIT
        
        # Step 1: Generate titles
        ui.print_info("Generating titles...")
        titles = analyzer.generate_titles(big_file)
        
        # Step 2: User selects title
        selected_index = ui.select_title(titles)
        selected_title = titles[selected_index]
        
        # Step 3: User inputs dimensions manually (width, height, depth)
        width, height, depth, dimensions_formatted = ui.input_dimensions(unit=DIMENSION_UNIT)
        
        # Step 4: User selects substrate
        substrate = ui.select_substrate()
        
        # Step 5: User selects medium
        medium = ui.select_medium()
        
        # Step 6: User selects subject
        subject = ui.select_subject()
        
        # Step 7: User selects style
        style = ui.select_style()
        
        # Step 8: User selects collection
        collection = ui.select_collection()
        
        # Step 9: User inputs price
        price = ui.input_price(default=0.0)
        
        # Step 10: Get creation date
        suggested_date = file_mgr.get_creation_date(big_file)
        creation_date = ui.input_creation_date(suggested_date)
        
        # Step 11: Generate description
        ui.print_info("Generating description...")
        # Build full medium description for AI
        full_medium = f"{medium} on {substrate}"
        description = analyzer.generate_description(
            big_file,
            selected_title,
            full_medium,
            dimensions_formatted,
            category,
        )
        
        # Step 12: Rename files
        ui.print_info("Renaming files...")
        sanitized_name = file_mgr.sanitize_filename(selected_title)
        new_big_path, new_instagram_path = file_mgr.rename_painting_pair(
            big_file,
            instagram_file,
            sanitized_name,
        )
        ui.print_success(f"Renamed to: {sanitized_name}{big_file.suffix}")
        
        # Step 13: Create metadata
        metadata = metadata_mgr.create_metadata(
            filename_base=sanitized_name,
            category=category,
            big_file_path=new_big_path,
            instagram_file_path=new_instagram_path,
            selected_title=selected_title,
            all_titles=titles,
            description=description,  # Only once!
            width=width,
            height=height,
            depth=depth,
            dimension_unit=DIMENSION_UNIT,
            dimensions_formatted=dimensions_formatted,
            substrate=substrate,
            medium=medium,
            subject=subject,
            style=style,
            collection=collection,
            price_eur=price,
            creation_date=creation_date,
        )
        
        # Step 14: Save metadata files
        json_path = metadata_mgr.save_metadata_json(metadata, category)
        txt_path = metadata_mgr.save_metadata_text(metadata, category)
        
        ui.print_success(f"Metadata saved: {json_path.name}")
        ui.print_success(f"Text file saved: {txt_path.name}")
        
        # Show summary
        ui.show_processing_summary(metadata)
        
    except Exception as e:
        ui.print_error(f"Error processing {big_file.name}: {e}")
        raise


@cli.command()
def list_categories():
    """List all available categories."""
    ui = CLIInterface()
    file_mgr = FileManager()
    
    categories = file_mgr.get_available_categories()
    
    if not categories:
        ui.print_warning("No categories found")
        return
    
    ui.print_header("Available Categories")
    for cat in categories:
        paintings = file_mgr.find_painting_files(cat)
        ui.print_info(f"{cat}: {len(paintings)} painting(s)")


@cli.command()
def verify_config():
    """Verify configuration and paths."""
    ui = CLIInterface()
    
    ui.print_header("Configuration Verification")
    
    # Check paths
    checks = [
        ("Big paintings path", PAINTINGS_BIG_PATH),
        ("Instagram paintings path", PAINTINGS_INSTAGRAM_PATH),
    ]
    
    for name, path in checks:
        if path.exists():
            ui.print_success(f"{name}: {path}")
        else:
            ui.print_error(f"{name} not found: {path}")
    
    # Check API key
    from config.settings import ANTHROPIC_API_KEY
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_api_key_here":
        ui.print_success("Anthropic API key: configured")
    else:
        ui.print_error("Anthropic API key: NOT configured")
        ui.print_info("Set ANTHROPIC_API_KEY in your .env file")


if __name__ == '__main__':
    cli()
