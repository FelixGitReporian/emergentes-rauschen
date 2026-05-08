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
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print(
            "Playwright not installed.\n"
            "Run:  python -m pip install playwright\n"
            "Then: python -m playwright install chromium"
        )
        sys.exit(1)
    from playwright.sync_api import sync_playwright

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
    tab_names = ["simulation", "spurenlesen", "partikel", "lernen", "graph"]  # defined before try for finally scope

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(url, timeout=30_000)
            page.wait_for_load_state("networkidle", timeout=60_000)
            page.wait_for_timeout(3_000)

            tab_buttons = page.locator('[data-baseweb="tab"]').all()

            for idx, tab_name in enumerate(tab_names):
                if idx < len(tab_buttons):
                    try:
                        tab_buttons[idx].click(timeout=5_000)
                        page.wait_for_timeout(2_500)
                    except Exception as e:
                        print(f"  ⚠️  Tab {idx} ('{tab_name}') konnte nicht geklickt werden: {e}")
                else:
                    print(f"  ⚠️  Tab {idx} ('{tab_name}') nicht vorhanden.")

                path = out_dir / f"dashboard_{tab_name}.png"
                page.screenshot(path=str(path), full_page=False)
                print(f"  ✅  {path}")

            browser.close()
    finally:
        proc.terminate()
        print(f"\n✅ Screenshots gespeichert in: {out_dir.resolve()}")
        print("   README.md einbinden mit:")
        for tab_name in tab_names:
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
