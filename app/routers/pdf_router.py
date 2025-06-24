from typing import Literal

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi import Form

from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.services.vector_service import VectorService


def get_pdf_service():
    return PDFService()


def get_llm_service():
    return LLMService()

def get_vector_service():
    return VectorService()


pdf_router = APIRouter()


@pdf_router.post("/upload-pdf")
async def upload_and_summarize(
        file: UploadFile = File(...),
        operation: Literal["summarize", "chat"] = Form("chat"),
        pdf_service: PDFService = Depends(get_pdf_service),
):
    try:
        result = pdf_service.process_pdf(file)
        if result.status == "success":
            if operation == "summarize":
                llm_service = get_llm_service()
                llm_response = await llm_service.summarize_nudge(result.pdf_filename)
                return llm_response
            vector_service = get_vector_service()
            vector_response = vector_service.vectorize_nudge(result)
            return vector_response
        else:
            return result

    except Exception as e:
        raise e



