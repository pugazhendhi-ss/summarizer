import os

import fitz  # PyMuPDF

from app.pydantics.models import PDFSuccessResponse, PDFErrorResponse


class PDFService:
    """PDF Service to extract and store text in parts"""

    def __init__(self):
        self.utils_dir = "app/utils"
        self.ensure_utils_directory()

    def ensure_utils_directory(self):
        """Ensure the utils directory exists"""
        os.makedirs(self.utils_dir, exist_ok=True)

    def process_pdf(self, file) -> PDFSuccessResponse | PDFErrorResponse:
        """
        Process uploaded PDF file and save text in 10-page per part

        Args:
            file: FastAPI UploadFile object

        Returns:
            dict: Processing result with details
        """
        try:
            # Get PDF filename without extension
            pdf_filename = os.path.splitext(file.filename)[0]

            # Create directory for this PDF
            pdf_dir = os.path.join(self.utils_dir, pdf_filename)
            os.makedirs(pdf_dir, exist_ok=True)

            # Read file content and open PDF
            file_content = file.file.read()
            doc = fitz.open(stream=file_content, filetype="pdf")
            total_pages = len(doc)

            # Process in chunks of 10 pages
            pages_per_chunk = 10
            part_number = 1

            for start_page in range(0, total_pages, pages_per_chunk):
                end_page = min(start_page + pages_per_chunk, total_pages)

                # Extract text from this chunk
                chunk_text = ""
                for page_num in range(start_page, end_page):
                    page = doc[page_num]
                    text = page.get_text()
                    chunk_text += f"--- PAGE {page_num + 1} ---\n{text}\n\n"

                # Save chunk to file
                part_filename = f"part_{part_number}.txt"
                part_path = os.path.join(pdf_dir, part_filename)

                with open(part_path, 'w', encoding='utf-8') as f:
                    f.write(chunk_text)

                part_number += 1
            doc.close()
            return PDFSuccessResponse(pdf_filename=pdf_filename, total_pages=total_pages)


        except Exception as e:
            error_message = f"Error occurred while extracting the text from the PDF: {str(e)}"
            return PDFErrorResponse(error=error_message)
