"""
Document Ingestion Engine Demo
================================
Runs the injestion engine on test documents in Modules/__ingest_file/

Usage:
    cd C:/Users/Philip/Documents/GitHub/4260_presentation
    C:/Users/Philip/AppData/Local/Programs/Python/Python314/python.exe demo_injest.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use absolute paths
INPUT_DIR = str(PROJECT_ROOT / "Modules" / "___ingest_file")
OUTPUT_DIR = str(PROJECT_ROOT / "Modules" / "___processed_file")

# Patch ollama to use localhost instead of Docker internal hostname
import httpx
_original_get = httpx.get
def _patched_get(url, *args, **kwargs):
    url = url.replace("http://ollama:", "http://localhost:")
    return _original_get(url, *args, **kwargs)
httpx.get = _patched_get

import ollama
_original_chat = ollama.chat
def _patched_chat(*args, **kwargs):
    if "host" not in kwargs:
        import ollama as _ollama
        client = _ollama.Client(host="http://localhost:11434")
        return client.chat(*args, **kwargs)
    return _original_chat(*args, **kwargs)
ollama.chat = _patched_chat

# Also patch pull
_original_pull = ollama.pull
def _patched_pull(*args, **kwargs):
    client = ollama.Client(host="http://localhost:11434")
    return client.pull(*args, **kwargs)
ollama.pull = _patched_pull

# Patch OCR to skip on Windows
def _skip_ocr(self):
    print("[ocr] Skipping OCR step (Windows environment)")
    return

from Modules.engine_injesting import injest_engine
injest_engine.Injest_Engine._Injest_Engine__ocr_my_pdf = _skip_ocr


from Modules.engine_injesting.injest_engine import Injest_Engine


class DemoInjestEngine(Injest_Engine):
    """Concrete implementation for demo purposes."""

    def injest_local_file(self):
        pass

    def injest_gmail(self, max_emails=10):
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("  Document Ingestion Engine Demo")
    print("=" * 60)
    print(f"\n  Input folder:  {INPUT_DIR}")
    print(f"  Output folder: {OUTPUT_DIR}")
    print(f"\n  Starting ingestion engine...")
    print("  (OCR PDFs + local Ollama LLM analysis)")
    print("-" * 60)

    # Ensure output dir exists
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    engine = DemoInjestEngine(
        input_files_path=INPUT_DIR,
        output_files_path=OUTPUT_DIR,
    )

    print("\n" + "=" * 60)
    print("  Ingestion complete!")
    print("  DB: Modules/engine_injesting/data_base/4260_BigData_db.db")
    print("=" * 60)
