import os
import logging
from openai import AsyncOpenAI

from app.pydantics.models import ChatResponse
from app.services.chat_service import ChatService
from app.templates.prompt_template import OperationType

logger = logging.getLogger(__name__)

CLIENT = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""), base_url="https://api.openai.com/v1")

global_memory = {} # To store non-persisted chat

class LLMService:
    """LLM Service for summarizing PDF content"""

    def __init__(self):
        self.active_model = "gpt-4o-mini"
        self.utils_dir = "app/utils"

    async def summarize_nudge(self, pdf_name: str) -> dict:
        """
        Process all parts of a PDF and summarize each part

        Args:
            pdf_name: Name of the PDF (directory name in utils)

        Returns:
            dict: Processing result
        """
        try:
            # Find PDF directory
            pdf_dir = os.path.join(self.utils_dir, pdf_name)

            # Get all part files
            part_files = [f for f in os.listdir(pdf_dir) if f.startswith('part_') and f.endswith('.txt')]
            part_files.sort()

            grouped_summary = ""
            # Process each part
            for part_file in part_files:
                print(f"Summarizing -> {part_file}")
                part_path = os.path.join(pdf_dir, part_file)

                # Read the part content
                with open(part_path, 'r', encoding='utf-8') as f:
                    extracted_data = f.read()

                # Getting part name (e.g., "part_1" from "part_1.txt")
                part_name = os.path.splitext(part_file)[0]

                # Summarize the data
                summarized_data = await self.invoke_llm(extracted_data, OperationType(type="part"))
                grouped_summary += f"{part_file}\n\n {summarized_data}\n\n"
                await self._save_summary(pdf_name, part_name, summarized_data)

            # print(grouped_summary)
            final_summary = await self.invoke_llm(grouped_summary, OperationType(type="final"))
            print(f"Final_summary ---> {final_summary}")

            return {
                "success": True,
                "pdf_name": pdf_name,
                "summary": final_summary
            }

        except Exception as e:
            logger.error(f"Error in summarize_nudge: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def invoke_llm(self,
              input_content: str,
              current_operation: OperationType,
              pdf_name: str|None = None
    ):
        """
        Summarize extracted data or generate chat response using OpenAI

        Args:
            input_content: Text content from PDF part | user_query
            current_operation: OperationType (defines chat, part summary or final summary),
            pdf_name: name of the pdf file

        Returns:
            Summarized text or llm_reply in a pydantic way
        """
        try:
            if current_operation.in_chat_mode():
                prompt = self._build_chat_prompt(input_content, pdf_name)
            else:
                prompt = current_operation.dynamic_prompt()
            response = await CLIENT.chat.completions.create(
                model=self.active_model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": input_content
                    }
                ],
                response_format={"type": "text"},
                max_tokens=16000,
                temperature=0.2
            )

            llm_response =  response.choices[0].message.content
            print(llm_response)
            if current_operation.in_chat_mode():
                return self.chat_response(llm_response, pdf_name)
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in _summarize_data: {str(e)}")
            return f"Error summarizing data: {str(e)}"

    async def _save_summary(self, pdf_name: str, part: str, summarized_data: str):
        """
        Save summarized data to file

        Args:
            pdf_name: Name of the PDF
            part: Part name (e.g., "part_1")
            summarized_data: Summarized content
        """
        try:
            # Create summary directory
            summary_dir = os.path.join(self.utils_dir, f"{pdf_name}_summary")
            os.makedirs(summary_dir, exist_ok=True)

            # Save summary file
            summary_filename = f"{part}_summary.txt"
            summary_path = os.path.join(summary_dir, summary_filename)

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summarized_data)

            logger.info(f"Saved summary: {summary_path}")

        except Exception as e:
            logger.error(f"Error in _save_summary: {str(e)}")
            raise e

    @staticmethod
    def _build_chat_prompt(user_query, pdf_name):
        chat_service = global_memory.get(pdf_name, None)
        if not chat_service:
            chat_service = ChatService()
            global_memory[pdf_name] = chat_service
        chat_service.add_user_message(user_query)
        dynamic_prompt = chat_service.get_dynamic_prompt(user_query)
        print(dynamic_prompt)
        return dynamic_prompt

    def chat_response(self, llm_response: str, pdf_name: str):
        chat_service = global_memory.get(pdf_name, None)
        if not chat_service:
            chat_service = ChatService()
            global_memory[pdf_name] = chat_service
        chat_service.add_bot_message(llm_response)
        return ChatResponse(llm_reply=llm_response)


