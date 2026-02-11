"""
FASO artwork uploader - uploads paintings and fills metadata forms.
Uses persistent browser profile from manual_login.py (no automated login needed).
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()


class FASOUploader:
    """Handles uploading artwork to FASO with metadata."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start_browser(self) -> bool:
        """Start browser with persistent profile. Returns False if profile missing/expired."""
        from config.settings import COOKIES_DIR

        profile_dir = COOKIES_DIR / "faso_browser_profile"
        marker = profile_dir / ".logged_in"

        if not marker.exists():
            console.print("[red]No browser profile found. Run manual_login.py first.[/red]")
            return False

        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=self.headless,
            viewport={'width': 1920, 'height': 1080},
            args=['--disable-blink-features=AutomationControlled'],
        )

        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

        # Verify session is valid
        await self.page.goto('https://data.fineartstudioonline.com/')
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        if '/login' in self.page.url.lower():
            console.print("[red]Session expired! Run manual_login.py again.[/red]")
            await self.close_browser()
            return False

        # Check if we got redirected away from the admin backend
        if 'data.fineartstudioonline.com' not in self.page.url:
            console.print(f"[yellow]Redirected to {self.page.url} — trying direct URL...[/yellow]")
            await self.page.goto('https://data.fineartstudioonline.com/home/')
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            if 'data.fineartstudioonline.com' not in self.page.url:
                console.print("[red]Cannot reach FASO dashboard. Run manual_login.py again.[/red]")
                await self.close_browser()
                return False

        console.print("[green]Browser started, session valid[/green]")
        return True

    async def close_browser(self):
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()

    async def upload_painting(self, metadata: Dict[str, Any]) -> bool:
        """
        Upload a single painting to FASO.

        Args:
            metadata: Full metadata dict loaded from JSON file.

        Returns:
            True on success, False on failure.
        """
        title = metadata.get("title", {}).get("selected", "Unknown")
        console.print(f"\n[bold cyan]Uploading: {title}[/bold cyan]")

        if not await self._navigate_to_upload_page():
            return False

        image_path = self.get_image_path(metadata)
        if not image_path or not Path(image_path).exists():
            console.print(f"[red]Image file not found: {image_path}[/red]")
            return False

        if not await self._upload_image_file(image_path):
            return False

        if not await self._wait_for_upload_success():
            return False

        if not await self._click_continue():
            return False

        if not await self._fill_metadata_form(metadata):
            return False

        if not await self._save_form():
            return False

        console.print(f"[bold green]Successfully uploaded: {title}[/bold green]")
        return True

    async def _navigate_to_upload_page(self) -> bool:
        """Click 'Upload Art Now' to get to the upload page."""
        try:
            # Go to dashboard first (in case we're on another page)
            await self.page.goto('https://data.fineartstudioonline.com/')
            await self.page.wait_for_load_state('networkidle')

            upload_btn = await self.page.wait_for_selector(
                'a:has-text("Upload Art Now")', timeout=5000
            )
            await upload_btn.click()
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            console.print("[green]On upload page[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Could not navigate to upload page: {e}[/red]")
            await self._take_error_screenshot("navigate")
            return False

    async def _upload_image_file(self, file_path: str) -> bool:
        """Upload an image file to FASO."""
        try:
            # Try hidden file input first (most reliable)
            file_input = await self.page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(file_path)
            else:
                # Fallback: use filechooser event
                async with self.page.expect_file_chooser() as fc_info:
                    upload_area = await self.page.wait_for_selector(
                        'text=Select Files to Upload', timeout=5000
                    )
                    await upload_area.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(file_path)

            await asyncio.sleep(2)

            # Click the Upload confirmation button
            upload_btn = await self.page.wait_for_selector(
                'button:has-text("Upload"), input[value="Upload"]', timeout=5000
            )
            await upload_btn.click()

            console.print("[cyan]Image uploading...[/cyan]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to upload image: {e}[/red]")
            await self._take_error_screenshot("upload_image")
            return False

    async def _wait_for_upload_success(self) -> bool:
        """Wait for the 'Upload succeeded' confirmation."""
        try:
            await self.page.wait_for_selector(
                'text=Upload succeeded', timeout=60000
            )
            console.print("[green]Image upload succeeded[/green]")
            await asyncio.sleep(2)
            return True
        except Exception as e:
            console.print(f"[red]Upload did not complete in time: {e}[/red]")
            await self._take_error_screenshot("upload_wait")
            return False

    async def _click_continue(self) -> bool:
        """Click the Continue button after upload success."""
        try:
            continue_btn = await self.page.wait_for_selector(
                'a:has-text("Continue"), button:has-text("Continue")', timeout=5000
            )
            await continue_btn.click()
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            console.print("[green]On metadata form[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Could not click Continue: {e}[/red]")
            await self._take_error_screenshot("continue")
            return False

    async def _fill_metadata_form(self, metadata: Dict[str, Any]) -> bool:
        """Fill in all metadata form fields."""
        try:
            # Title - clear existing (filename-based) and type the real title
            title = metadata.get("title", {}).get("selected", "")
            if title:
                await self._fill_text_field('input[name="Title"]', title)

            # Collection dropdown
            collection = metadata.get("collection")
            if collection:
                await self._select_dropdown('select[name="Collection"]', collection)

            # Medium dropdown
            medium = metadata.get("medium")
            if medium:
                await self._select_dropdown('select[name="Medium"]', medium)

            # Substrate dropdown
            substrate = metadata.get("substrate")
            if substrate:
                await self._select_dropdown('select[name="Substrate"]', substrate)

            # Dimensions - VerticalSize = height, HorizontalSize = width
            dims = metadata.get("dimensions", {})
            height = dims.get("height")
            width = dims.get("width")
            depth = dims.get("depth")

            if height is not None:
                await self._fill_text_field(
                    'input[name="VerticalSize"]', str(height)
                )
            if width is not None:
                await self._fill_text_field(
                    'input[name="HorizontalSize"]', str(width)
                )
            if depth is not None:
                await self._fill_text_field(
                    'input[name="Depth"]', str(depth)
                )

            # YearCreated dropdown
            creation_date = metadata.get("creation_date")
            year = self.extract_year(creation_date)
            if year:
                await self._select_dropdown('select[name="YearCreated"]', year)

            # Subject dropdown
            subject = metadata.get("subject")
            if subject:
                await self._select_dropdown('select[name="Subject"]', subject)

            # Style dropdown
            style = metadata.get("style")
            if style:
                await self._select_dropdown('select[name="Style"]', style)

            # RetailPrice
            price = metadata.get("price_eur")
            if price is not None:
                await self._fill_text_field(
                    'input[name="RetailPrice"]', str(int(price))
                )

            # Description (rich text editor)
            description = metadata.get("description")
            if description:
                await self._fill_description(description)

            console.print("[green]Form fields filled[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error filling form: {e}[/red]")
            await self._take_error_screenshot("fill_form")
            return False

    async def _save_form(self) -> bool:
        """Click Save Changes."""
        try:
            save_btn = await self.page.wait_for_selector(
                'input[value="Save Changes"], button:has-text("Save Changes"), '
                'a:has-text("Save Changes")',
                timeout=5000
            )
            await save_btn.click()
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            console.print("[green]Changes saved[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Could not save form: {e}[/red]")
            await self._take_error_screenshot("save")
            return False

    async def _fill_text_field(self, selector: str, value: str):
        """Clear a text field and type a new value."""
        try:
            field = await self.page.wait_for_selector(selector, timeout=3000)
            await field.click(click_count=3)  # Select all existing text
            await field.fill(value)
        except Exception as e:
            console.print(f"[yellow]Warning: could not fill {selector}: {e}[/yellow]")

    async def _select_dropdown(self, selector: str, value: str):
        """Select a dropdown option by visible text label."""
        try:
            await self.page.select_option(selector, label=value)
        except Exception as e:
            # If exact match fails, try to find a close match
            console.print(
                f"[yellow]Warning: could not select '{value}' in {selector}: {e}[/yellow]"
            )

    async def _fill_description(self, description: str):
        """Fill the rich text description editor."""
        html_content = self.markdown_to_html(description)

        try:
            # Strategy 1: Click HTML toggle button, paste into textarea
            html_toggle = await self.page.query_selector(
                'a:has-text("HTML"), button:has-text("HTML")'
            )
            if html_toggle:
                await html_toggle.click()
                await asyncio.sleep(1)
                # Look for a textarea that appeared
                textarea = await self.page.query_selector(
                    'textarea[class*="html"], textarea[id*="Description"], '
                    'textarea.mce-textbox'
                )
                if textarea:
                    await textarea.fill(html_content)
                    console.print("[green]Description filled via HTML mode[/green]")
                    return

            # Strategy 2: Use TinyMCE JavaScript API
            result = await self.page.evaluate(f'''
                () => {{
                    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {{
                        tinymce.activeEditor.setContent({json.dumps(html_content)});
                        return true;
                    }}
                    if (typeof tinyMCE !== 'undefined' && tinyMCE.activeEditor) {{
                        tinyMCE.activeEditor.setContent({json.dumps(html_content)});
                        return true;
                    }}
                    return false;
                }}
            ''')
            if result:
                console.print("[green]Description filled via TinyMCE API[/green]")
                return

            # Strategy 3: Direct iframe injection
            iframes = await self.page.query_selector_all('iframe')
            for iframe in iframes:
                iframe_id = await iframe.get_attribute('id') or ''
                if 'description' in iframe_id.lower() or 'editor' in iframe_id.lower() or 'mce' in iframe_id.lower():
                    frame = await iframe.content_frame()
                    if frame:
                        await frame.evaluate(
                            f'document.body.innerHTML = {json.dumps(html_content)}'
                        )
                        console.print("[green]Description filled via iframe[/green]")
                        return

            # Strategy 4: Try any iframe
            if iframes:
                frame = await iframes[0].content_frame()
                if frame:
                    await frame.evaluate(
                        f'document.body.innerHTML = {json.dumps(html_content)}'
                    )
                    console.print("[green]Description filled via first iframe[/green]")
                    return

            console.print("[yellow]Warning: could not fill description field[/yellow]")

        except Exception as e:
            console.print(f"[yellow]Warning: description fill failed: {e}[/yellow]")

    async def _take_error_screenshot(self, name: str):
        """Save a screenshot for debugging."""
        from config.settings import SCREENSHOTS_DIR
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"faso_error_{name}_{timestamp}.png"
        try:
            await self.page.screenshot(path=str(path), full_page=True)
            console.print(f"[yellow]Error screenshot: {path}[/yellow]")
        except Exception:
            pass

    # --- Static helper methods ---

    @staticmethod
    def get_image_path(metadata: Dict[str, Any]) -> Optional[str]:
        """Get the image file path from metadata (handles string or list)."""
        big = metadata.get("files", {}).get("big")
        if isinstance(big, list):
            return big[0] if big else None
        return big

    @staticmethod
    def extract_year(creation_date: Optional[str]) -> str:
        """Extract year from ISO date string, or return current year."""
        if creation_date and len(creation_date) >= 4:
            return creation_date[:4]
        return str(datetime.now().year)

    @staticmethod
    def markdown_to_html(text: str) -> str:
        """Convert simple markdown to HTML for the description editor."""
        if not text:
            return ""
        # Convert **bold** to <strong>
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Convert *italic* to <em>
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        # Split into paragraphs on double newlines
        paragraphs = html.split('\n\n')
        html = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
        return html

    @staticmethod
    def is_upload_ready(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if metadata has all required fields for FASO upload.

        Returns:
            (is_ready, list_of_missing_field_names)
        """
        missing = []

        if not metadata.get("title", {}).get("selected"):
            missing.append("title")

        big_path = metadata.get("files", {}).get("big")
        if not big_path:
            missing.append("image file path")
        else:
            path = big_path[0] if isinstance(big_path, list) else big_path
            if not Path(path).exists():
                missing.append(f"image file missing: {Path(path).name}")

        for field in ["medium", "substrate", "subject", "style", "collection"]:
            if not metadata.get(field):
                missing.append(field)

        dims = metadata.get("dimensions", {})
        if not dims.get("width") or not dims.get("height"):
            missing.append("dimensions")

        if not metadata.get("description"):
            missing.append("description")

        return (len(missing) == 0, missing)


async def _do_uploads(
    paintings: List[Tuple[str, Dict[str, Any]]],
    tracker,
) -> Dict[str, int]:
    """Run the actual browser uploads."""
    results = {"success": 0, "failed": 0}

    async with FASOUploader(headless=False) as uploader:
        if not await uploader.start_browser():
            return results

        for filename, metadata in paintings:
            success = await uploader.upload_painting(metadata)

            if success:
                tracker.mark_uploaded(filename, "FASO")
                results["success"] += 1
            else:
                results["failed"] += 1

            # Small delay between uploads
            if paintings.index((filename, metadata)) < len(paintings) - 1:
                await asyncio.sleep(2)

    return results


def upload_faso_cli():
    """CLI entry point for FASO upload. Called from admin mode or CLI command."""
    from src.upload_tracker import UploadTracker
    from config.settings import UPLOAD_TRACKER_PATH

    # Load tracker and get pending FASO uploads
    tracker = UploadTracker(UPLOAD_TRACKER_PATH)
    pending = tracker.get_pending_uploads("FASO")

    if not pending:
        console.print("[yellow]No paintings pending FASO upload.[/yellow]")
        return

    # Load metadata for each pending painting and check readiness
    ready_paintings = []
    not_ready = []

    for filename in pending:
        painting_data = tracker.data["paintings"][filename]
        metadata_path = painting_data.get("metadata_path")

        if not metadata_path or not Path(metadata_path).exists():
            not_ready.append((filename, ["metadata file not found"]))
            continue

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            is_ready, missing = FASOUploader.is_upload_ready(metadata)
            if is_ready:
                ready_paintings.append((filename, metadata))
            else:
                not_ready.append((filename, missing))
        except Exception as e:
            not_ready.append((filename, [str(e)]))

    # Display table of paintings
    table = Table(title="Pending FASO Uploads")
    table.add_column("No.", style="dim", width=5)
    table.add_column("Title")
    table.add_column("Status")

    for i, (filename, metadata) in enumerate(ready_paintings, 1):
        title = metadata.get("title", {}).get("selected", filename)
        table.add_row(str(i), title, "[green]Ready[/green]")

    for filename, missing in not_ready:
        table.add_row("-", filename, f"[red]Missing: {', '.join(missing)}[/red]")

    console.print(table)

    if not ready_paintings:
        console.print("[yellow]No paintings are ready for upload.[/yellow]")
        return

    # Let user choose
    console.print(f"\n[bold]{len(ready_paintings)} painting(s) ready for upload[/bold]")

    if len(ready_paintings) == 1:
        choice = "1"
        if not Confirm.ask(
            f"Upload '{ready_paintings[0][1]['title']['selected']}' to FASO?",
            default=True
        ):
            return
    else:
        choices = ["all"] + [str(i) for i in range(1, len(ready_paintings) + 1)] + ["0"]
        choice = Prompt.ask(
            "Upload which? (number, 'all', or 0 to cancel)",
            choices=choices,
            default="all"
        )

        if choice == "0":
            return

    if choice == "all":
        to_upload = ready_paintings
    else:
        idx = int(choice) - 1
        to_upload = [ready_paintings[idx]]

    if len(to_upload) > 1:
        if not Confirm.ask(
            f"Upload {len(to_upload)} painting(s) to FASO?", default=True
        ):
            return

    # Run async uploads
    console.print("\n[cyan]Starting browser for upload...[/cyan]")
    results = asyncio.run(_do_uploads(to_upload, tracker))

    # Summary
    console.print(f"\n[bold]Upload Results:[/bold]")
    console.print(f"  Succeeded: [green]{results['success']}[/green]")
    if results['failed'] > 0:
        console.print(f"  Failed: [red]{results['failed']}[/red]")
