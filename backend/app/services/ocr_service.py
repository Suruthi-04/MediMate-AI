import os
import shutil
import logging
from pathlib import Path
from typing import Tuple, List, Optional
from pypdf import PdfReader
from PIL import Image

try:
    import pytesseract
    # Check if standard Windows Tesseract path exists
    common_tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    for p in common_tesseract_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break
except ImportError:
    pytesseract = None

logger = logging.getLogger(__name__)

class OCRService:
    @staticmethod
    def is_tesseract_available() -> bool:
        """Check if Tesseract binary is accessible."""
        if not pytesseract:
            return False
        try:
            cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
            if os.path.exists(cmd) or shutil.which("tesseract"):
                return True
            return False
        except Exception:
            return False

    @classmethod
    def extract_text_from_pdf(cls, file_path: Path) -> Tuple[str, float]:
        """
        Extract text from PDF pages using pypdf.
        Returns: (extracted_text, confidence_score)
        """
        try:
            reader = PdfReader(str(file_path))
            pages_text: List[str] = []
            
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"--- [Page {idx + 1}] ---\n{text.strip()}")
            
            combined_text = "\n\n".join(pages_text).strip()
            
            if len(combined_text) > 20:
                # Text PDF extraction is direct and highly reliable
                return combined_text, 0.98
            
            # Scanned PDF without text layer: attempt page image OCR if tesseract is available
            if cls.is_tesseract_available() and len(reader.pages) > 0:
                ocr_texts = []
                for idx, page in enumerate(reader.pages):
                    for img in page.images:
                        pil_img = Image.open(img.name)
                        img_text = pytesseract.image_to_string(pil_img)
                        ocr_texts.append(img_text)
                if ocr_texts:
                    return "\n\n".join(ocr_texts).strip(), 0.85
            
            return combined_text or "[Empty or Image-Only Scanned PDF Document]", 0.50
        except Exception as e:
            logger.error(f"Error extracting PDF text from {file_path}: {e}")
            raise ValueError(f"Could not read PDF file: {str(e)}")

    @classmethod
    def extract_text_from_image(cls, file_path: Path) -> Tuple[str, float]:
        """
        Extract text from PNG/JPG image using pytesseract if available,
        or fallback diagnostic text extractor.
        Returns: (extracted_text, confidence_score)
        """
        try:
            with Image.open(str(file_path)) as img:
                img_rgb = img.convert("RGB")
                
                if cls.is_tesseract_available():
                    text = pytesseract.image_to_string(img_rgb)
                    if text and len(text.strip()) > 10:
                        return text.strip(), 0.88
                
                # Check EXIF / embedded metadata or return fallback with notice
                return (
                    f"[Scanned Clinical Image: {file_path.name}]\n"
                    f"Dimensions: {img.size[0]}x{img.size[1]}px\n"
                    f"Format: {img.format}\n"
                    "Note: Tesseract OCR engine is not installed on this system. "
                    "For full image optical character recognition, install Tesseract OCR or use Digital PDF reports.",
                    0.60
                )
        except Exception as e:
            logger.error(f"Error reading image {file_path}: {e}")
            raise ValueError(f"Could not process image: {str(e)}")

    @classmethod
    def process_file(cls, file_path: Path, mime_type: str) -> Tuple[str, float]:
        """
        Dispatch extraction based on mime type or file extension.
        """
        ext = file_path.suffix.lower()
        if ext == ".pdf" or "pdf" in mime_type:
            return cls.extract_text_from_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg"] or "image" in mime_type:
            return cls.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Accepted formats: PDF, PNG, JPG.")

ocr_service = OCRService()
