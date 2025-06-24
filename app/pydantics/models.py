from pydantic import BaseModel

class PDFSuccessResponse(BaseModel):
    status: str = "success"
    pdf_filename: str
    total_pages: int

class PDFErrorResponse(BaseModel):
    status: str = "error"
    error: str

class ChatPayload(BaseModel):
    file_name: str
    query: str

class ChatResponse(BaseModel):
    status: str = "success"
    llm_reply: str



