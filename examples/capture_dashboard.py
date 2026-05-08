"""
examples/capture_dashboard.py – Dashboard-Screenshot für README.

Startet das Streamlit-Dashboard, wartet bis es bereit ist,
macht Screenshots aller 5 Tabs und speichert sie nach docs/screenshots/.

Voraussetzungen:
    pip install playwright
    playwright install chromium

Verwendung:
    python examples/capture_dashboard.py
    python examples/capture_dashboard.py --port 8502 --wait 8
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def capture(port: int = 8501, wait: int = 10) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright nicht installiert.\n"
            "Führe aus: pip install playwright && playwright install chromium"
        )
        sys.exit(1)

    out_dir = Path("docs") / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    dashboard = Path("src") / "emergent_noise" / "visualization" / "dashboard.py"
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(dashboard),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.runOnSave", "false",
    ]

    print(f"🚀 Starte Dashboard auf Port {port} …")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(wait)

    url = f"http://localhost:{port}"
    tabs = [
        ("simulation",  None),
        ("spurenlesen",  "text=🧭 Spurenlesen"),
        ("partikel",    "text=⚗️ Partikel"),
        ("lernen",      "text=🎓 Lernen"),
        ("graph",       "text=🕸️ Graph"),
    ]

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(url, timeout=30_000)
            page.wait_for_load_state("networkidle", timeout=30_000)

            for tab_name, tab_selector in tabs:
                if tab_selector:
                    try:
                        page.click(tab_selector, timeout=5_000)
                        page.wait_for_timeout(2_000)
                    except Exception:
                        print(f"  ⚠️  Tab '{tab_name}' nicht gefunden, überspringe.")
                        continue

                path = out_dir / f"dashboard_{tab_name}.png"
                page.screenshot(path=str(path), full_page=False)
                print(f"  ✅  {path}")

            browser.close()
    finally:
        proc.terminate()
        print(f"\n✅ Screenshots gespeichert in: {out_dir.resolve()}")
        print("   README.md einbinden mit:")
        for tab_name, _ in tabs:
            print(f"   ![{tab_name}](docs/screenshots/dashboard_{tab_name}.png)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard-Screenshots für README")
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--wait", type=int, default=10,
                        help="Sekunden warten bis Dashboard bereit (default: 10)")
    args = parser.parse_args()
    capture(port=args.port, wait=args.wait)


if __name__ == "__main__":
    main()
