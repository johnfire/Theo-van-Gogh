"""
Explore FASO pages with persistent browser profile - uploads a test image
and captures the metadata form HTML for selector discovery.
Run locally: python explore_faso.py
"""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright
from rich.console import Console

from config.settings import COOKIES_DIR, SCREENSHOTS_DIR, PAINTINGS_BIG_PATH, SUPPORTED_IMAGE_FORMATS

console = Console()

BROWSER_PROFILE_DIR = COOKIES_DIR / "faso_browser_profile"


def pick_test_image() -> Path:
    """Find a test image to upload from the paintings directory."""
    for subfolder in sorted(PAINTINGS_BIG_PATH.iterdir()):
        if not subfolder.is_dir() or subfolder.name.startswith('.'):
            continue
        for f in sorted(subfolder.iterdir()):
            if f.suffix.lower() in SUPPORTED_IMAGE_FORMATS:
                return f
    return None


async def explore():
    console.print("\n[bold cyan]FASO Page Explorer (Full Flow)[/bold cyan]\n")

    marker = BROWSER_PROFILE_DIR / ".logged_in"
    if not marker.exists():
        console.print("[red]No browser profile found. Run manual_login.py first.[/red]")
        return

    # Find a test image
    test_image = pick_test_image()
    if not test_image:
        console.print("[red]No image found in paintings directory to test with.[/red]")
        return
    console.print(f"[cyan]Test image: {test_image}[/cyan]")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            args=['--disable-blink-features=AutomationControlled'],
        )

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = context.pages[0] if context.pages else await context.new_page()

        # Step 1: Go to FASO dashboard
        console.print("[cyan]Navigating to FASO dashboard...[/cyan]")
        await page.goto('https://data.fineartstudioonline.com/cfgeditwebsite.asp?new_login=y&faso_com_auth=y')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        console.print(f"[yellow]Current URL: {page.url}[/yellow]")

        if '/login' in page.url.lower():
            console.print("[red]Session expired! Run manual_login.py again.[/red]")
            await context.close()
            return

        # Step 2: Click "Upload Art Now"
        console.print("\n[cyan]Clicking 'Upload Art Now'...[/cyan]")
        try:
            upload_btn = await page.wait_for_selector('a:has-text("Upload Art Now")', timeout=30000)
            await upload_btn.click()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            console.print(f"[yellow]Current URL: {page.url}[/yellow]")
        except Exception as e:
            console.print(f"[red]Could not find Upload Art Now: {e}[/red]")
            await context.close()
            return

        # Step 3: Upload a test image
        console.print(f"\n[cyan]Uploading test image: {test_image.name}...[/cyan]")
        try:
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                console.print("[green]Found file input element[/green]")
                await file_input.set_input_files(str(test_image))
            else:
                console.print("[yellow]No file input found, trying filechooser...[/yellow]")
                async with page.expect_file_chooser() as fc_info:
                    upload_area = await page.wait_for_selector('text=Select Files to Upload', timeout=5000)
                    await upload_area.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(str(test_image))

            await asyncio.sleep(2)

            screenshot_path = SCREENSHOTS_DIR / "faso_file_selected.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            console.print(f"[green]Screenshot: {screenshot_path}[/green]")

            console.print("[cyan]Clicking Upload button...[/cyan]")
            upload_confirm = await page.wait_for_selector('button:has-text("Upload"), input[value="Upload"]', timeout=5000)
            await upload_confirm.click()

            console.print("[cyan]Waiting for upload to complete...[/cyan]")
            await page.wait_for_selector('text=Upload succeeded', timeout=60000)
            console.print("[green]Upload succeeded![/green]")
            await asyncio.sleep(2)

        except Exception as e:
            console.print(f"[red]Upload failed: {e}[/red]")
            screenshot_path = SCREENSHOTS_DIR / "faso_upload_error.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            html = await page.content()
            with open(SCREENSHOTS_DIR / "faso_upload_error.html", 'w') as f:
                f.write(html)
            console.print(f"[yellow]Error screenshot + HTML saved to {SCREENSHOTS_DIR}[/yellow]")
            input("Press Enter to close...")
            await context.close()
            return

        # Step 4: Click Continue
        console.print("\n[cyan]Clicking Continue...[/cyan]")
        try:
            continue_btn = await page.wait_for_selector('a:has-text("Continue"), button:has-text("Continue")', timeout=5000)
            await continue_btn.click()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            console.print(f"[yellow]Current URL: {page.url}[/yellow]")
        except Exception as e:
            console.print(f"[red]Could not find Continue: {e}[/red]")

        # Step 5: Capture the metadata form
        console.print("\n[bold green]Metadata form loaded! Capturing...[/bold green]")

        screenshot_path = SCREENSHOTS_DIR / "faso_metadata_form.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        console.print(f"[green]Screenshot: {screenshot_path}[/green]")

        html = await page.content()
        html_path = SCREENSHOTS_DIR / "faso_metadata_form.html"
        with open(html_path, 'w') as f:
            f.write(html)
        console.print(f"[green]Form HTML saved: {html_path}[/green]")

        # Extract and display form field info
        console.print("\n[bold cyan]Form Fields Found:[/bold cyan]")

        selects = await page.query_selector_all('select')
        for select in selects:
            name = await select.get_attribute('name') or await select.get_attribute('id') or '???'
            console.print(f"  [cyan]SELECT[/cyan] name={name}")

        inputs = await page.query_selector_all('input[type="text"], input[type="number"], input:not([type])')
        for inp in inputs:
            name = await inp.get_attribute('name') or await inp.get_attribute('id') or '???'
            inp_type = await inp.get_attribute('type') or 'text'
            console.print(f"  [yellow]INPUT[/yellow] type={inp_type} name={name}")

        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            iframe_id = await iframe.get_attribute('id') or '???'
            iframe_src = await iframe.get_attribute('src') or '???'
            console.print(f"  [magenta]IFRAME[/magenta] id={iframe_id} src={iframe_src}")

        textareas = await page.query_selector_all('textarea')
        for ta in textareas:
            name = await ta.get_attribute('name') or await ta.get_attribute('id') or '???'
            console.print(f"  [green]TEXTAREA[/green] name={name}")

        console.print("\n[bold yellow]IMPORTANT: Delete the test upload from FASO manually![/bold yellow]")
        console.print("[cyan]Browser staying open so you can inspect and clean up.[/cyan]")
        input("Press Enter to close...")

        await context.close()


if __name__ == "__main__":
    asyncio.run(explore())
