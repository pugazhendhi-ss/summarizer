from fastapi import APIRouter, Depends

from app.pydantics.models import ChatPayload
from app.services.llm_service import LLMService
from app.templates.prompt_template import OperationType

def get_llm_service():
    return LLMService()


chat_router = APIRouter()

@chat_router.post("/chat")
async def setup_chat(
        chat_data: ChatPayload = ChatPayload,
        llm_service: LLMService = Depends(get_llm_service)
):
    try:
        response = await llm_service.invoke_llm(chat_data.query, OperationType(type="chat"), chat_data.file_name)
        return response
    except Exception as e:
        raise e

