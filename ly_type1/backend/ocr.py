"""
backend/ocr.py
OCR module for LY‑Type1.

Strategy:
  1. Try pdfminer.six for PDF text extraction.
  2. Try pytesseract (Tesseract OCR) for image files.
  3. If neither is installed, return a structured error payload
     so the UI can still display something meaningful.
"""

from __future__ import annotations
import io


def process_document(content: bytes, content_type: str) -> dict:
    """Extract text (and simple table hints) from a document.

    Parameters
    ----------
    content : bytes
        Raw file bytes.
    content_type : str
        MIME type, e.g. 'application/pdf', 'image/png'.

    Returns
    -------
    dict  with keys: text, tables, source, bytes_received
    """
    text = ""
    tables: list = []

    if "pdf" in (content_type or "").lower():
        text = _extract_pdf(content)
    else:
        text = _extract_image(content)

    return {
        "text": text or "[No text extracted]",
        "tables": tables,
        "source": content_type,
        "bytes_received": len(content),
    }


def _extract_pdf(content: bytes) -> str:
    """Extract text from PDF bytes using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text
        return extract_text(io.BytesIO(content))
    except ImportError:
        return (
            "[pdfminer.six not installed] "
            "Install with: pip install pdfminer.six"
        )
    except Exception as exc:
        return f"[PDF extraction error] {exc}"


def _extract_image(content: bytes) -> str:
    """Extract text from image bytes using pytesseract."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(img)
    except ImportError:
        return (
            "[pytesseract / Pillow not installed] "
            "Install with: pip install pytesseract pillow"
        )
    except Exception as exc:
        return f"[Image OCR error] {exc}"
