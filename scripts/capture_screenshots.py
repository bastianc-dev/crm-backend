"""Capture the real CRM frontend through its demo login.

Requires an accessible running CRM with DEMO_MODE=true and Playwright:
    pip install playwright
    playwright install chromium
    python scripts/capture_screenshots.py --url http://localhost:8000

Optional: --url https://crm-backend-kpcb.onrender.com
Screenshots are saved to docs/images unless --output is specified.
"""

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture(url: str, output: Path, chromium_path: str | None = None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chromium_path)
        try:
            desktop = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            desktop.goto(url, wait_until="domcontentloaded", timeout=60_000)
            desktop.locator("#login-form").wait_for(timeout=25_000)
            desktop.screenshot(path=str(output / "login.png"), full_page=True)

            desktop.get_by_role("button", name="Admin demo").click()
            desktop.locator("#dashboard-view .stat-card").first.wait_for(timeout=45_000)
            desktop.screenshot(path=str(output / "dashboard.png"), full_page=True)

            desktop.get_by_role("button", name="Leads", exact=True).click()
            desktop.locator("#leads-view .data-table").wait_for(timeout=30_000)
            desktop.screenshot(path=str(output / "leads.png"), full_page=True)

            desktop.get_by_role("button", name="Nuevo lead", exact=True).click()
            desktop.get_by_role("dialog").wait_for()
            desktop.screenshot(path=str(output / "lead-form.png"), full_page=True)
            desktop.get_by_role("button", name="Cancelar").click()

            desktop.get_by_role("button", name="Usuarios", exact=True).click()
            desktop.locator("#users-view .data-table").wait_for(timeout=30_000)
            desktop.screenshot(path=str(output / "users.png"), full_page=True)

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
            mobile.goto(url, wait_until="domcontentloaded", timeout=60_000)
            mobile.locator("#login-form").wait_for(timeout=25_000)
            mobile.screenshot(path=str(output / "mobile-login.png"), full_page=True)
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=Path("docs/images"))
    parser.add_argument("--chromium-path", help="Path to an existing Chromium executable")
    args = parser.parse_args()
    capture(args.url.rstrip("/"), args.output, args.chromium_path)
    print(f"Capturas guardadas en {args.output.resolve()}")
