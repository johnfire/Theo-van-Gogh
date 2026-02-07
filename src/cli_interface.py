"""
Interactive CLI interface for user input.
Uses rich library for beautiful terminal output.
"""

from typing import Optional, List
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.table import Table
from rich.panel import Panel

from config.settings import MEDIUMS, CATEGORIES


console = Console()


class CLIInterface:
    """Handles interactive command-line interface."""
    
    def __init__(self):
        """Initialize CLI interface."""
        self.console = console
    
    def print_header(self, text: str):
        """Print a styled header."""
        self.console.print(f"\n[bold cyan]{text}[/bold cyan]")
        self.console.print("=" * len(text))
    
    def print_success(self, text: str):
        """Print success message."""
        self.console.print(f"[green]✓[/green] {text}")
    
    def print_warning(self, text: str):
        """Print warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {text}")
    
    def print_error(self, text: str):
        """Print error message."""
        self.console.print(f"[red]✗[/red] {text}")
    
    def print_info(self, text: str):
        """Print info message."""
        self.console.print(f"[blue]→[/blue] {text}")
    
    def select_category(self, available_categories: List[str]) -> Optional[str]:
        """
        Let user select a category from available options.
        
        Args:
            available_categories: List of discovered categories
            
        Returns:
            Selected category name or None if cancelled
        """
        self.print_header("Available Categories")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim", width=6)
        table.add_column("Category")
        table.add_column("Path")
        
        for i, cat in enumerate(available_categories, 1):
            table.add_row(str(i), cat, f".../{cat}")
        
        self.console.print(table)
        
        # Get user selection
        choice = IntPrompt.ask(
            "\nSelect category number (0 to cancel)",
            default=1,
            show_default=True,
        )
        
        if choice == 0 or choice > len(available_categories):
            return None
        
        return available_categories[choice - 1]
    
    def select_title(self, titles: List[str]) -> int:
        """
        Let user select a title from generated options.
        
        Args:
            titles: List of 5 title options
            
        Returns:
            Index of selected title (0-4)
        """
        self.print_header("Generated Title Options")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim", width=6)
        table.add_column("Title")
        
        for i, title in enumerate(titles, 1):
            table.add_row(str(i), title)
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSelect title number",
            default=1,
            choices=[str(i) for i in range(1, 6)],
        )
        
        return choice - 1
    
    def select_medium(self) -> str:
        """
        Let user select medium from predefined options.
        
        Returns:
            Selected medium
        """
        self.print_header("Select Medium")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim", width=6)
        table.add_column("Medium")
        
        for i, medium in enumerate(MEDIUMS, 1):
            table.add_row(str(i), medium)
        
        self.console.print(table)
        
        choice = IntPrompt.ask(
            "\nSelect medium number",
            default=1,
            choices=[str(i) for i in range(1, len(MEDIUMS) + 1)],
        )
        
        return MEDIUMS[choice - 1]
    
    def input_price(self, default: float = 0.0) -> float:
        """
        Get price input from user.
        
        Args:
            default: Default price value
            
        Returns:
            Price in euros
        """
        return FloatPrompt.ask(
            "Enter price (EUR)",
            default=default,
        )
    
    def input_creation_date(self, suggested_date: str) -> str:
        """
        Get creation date from user.
        
        Args:
            suggested_date: Suggested date from EXIF/file
            
        Returns:
            Date string in YYYY-MM-DD format
        """
        self.console.print(f"\n[dim]Suggested date from EXIF: {suggested_date}[/dim]")
        
        date_input = Prompt.ask(
            "Enter creation date (YYYY-MM-DD) or press Enter to accept suggested",
            default=suggested_date,
        )
        
        return date_input
    
    def confirm_processing(self, filename: str) -> bool:
        """
        Ask for confirmation before processing.
        
        Args:
            filename: Name of file to process
            
        Returns:
            True if user confirms
        """
        return Confirm.ask(f"\nProcess {filename}?", default=True)
    
    def show_processing_summary(self, metadata: dict):
        """
        Display summary of processed artwork.
        
        Args:
            metadata: Metadata dictionary
        """
        self.console.print("\n")
        panel_content = f"""[bold]{metadata['title']['selected']}[/bold]

[dim]Category:[/dim] {metadata['category']}
[dim]Medium:[/dim] {metadata['medium']}
[dim]Dimensions:[/dim] {metadata['dimensions']}
[dim]Price:[/dim] €{metadata['price_eur']}
[dim]Date:[/dim] {metadata['creation_date']}

[dim]Description:[/dim]
{metadata['description']}
"""
        
        panel = Panel(
            panel_content,
            title="Processing Complete",
            border_style="green",
        )
        
        self.console.print(panel)
    
    def show_file_info(self, big_file, instagram_file):
        """
        Display information about file pair.
        
        Args:
            big_file: Path to big version
            instagram_file: Path to instagram version or None
        """
        self.console.print(f"\n[bold]File:[/bold] {big_file.name}")
        self.console.print(f"[dim]Big version:[/dim] {big_file}")
        
        if instagram_file:
            self.console.print(f"[dim]Instagram version:[/dim] {instagram_file}")
        else:
            self.console.print(f"[yellow]Instagram version: Not found[/yellow]")
