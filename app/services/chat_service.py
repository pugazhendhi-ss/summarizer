import textwrap
from collections import OrderedDict

from app.services.vector_service import VectorService
from app.templates.prompt_template import OperationType

vector_service = VectorService()

class ChatService:
    def __init__(self):
        self.memory = OrderedDict()
        self.query_count = 0
        self.max_memory_size = 7  # Last 7 chat pairs

    def add_user_message(self, query: str):
        self.query_count += 1
        self.memory[f"User (query_num -> {self.query_count})"] = query

    def add_bot_message(self, response: str):
        self.memory[f"AI (response_num -> {self.query_count})"] = response
        self._manage_memory()

    def _manage_memory(self):
        if len(self.memory) > self.max_memory_size * 2:
            # Pop the first two items (oldest chat pairs)
            self.memory.popitem(last=False)  # Oldest user message
            self.memory.popitem(last=False)  # Oldest bot/MSP response

    def get_history(self):
        if not self.memory:
            return "No history found for the user, as they are just started their conversation."
        max_key_length = max(len(key) for key in self.memory)
        indent_space = max_key_length + 2
        history_str = ""

        for i, (key, value) in enumerate(self.memory.items()):
            wrapped = textwrap.fill(
                value,
                width=130,
                initial_indent=' ' * (max_key_length - len(key)) + f"{key}: ",
                subsequent_indent=' ' * indent_space
            )
            history_str += f"{wrapped}\n"
            # Add an extra newline after every 2 entries (a pair)
            if i % 2 == 1:
                history_str += '\n'
        # print(f"History str ---> {history_str}")
        return history_str


    def get_dynamic_prompt(self, query):
        history = self.get_history()
        prompt_template = OperationType(type="chat")
        query = self.augment_query(query)
        semantic_finding = vector_service.semantic_search(query)
        top_k_match = semantic_finding["result"]
        chat_prompt = prompt_template.dynamic_prompt(query=query, history=history, context=top_k_match)
        return chat_prompt


    def augment_query(self, user_query):
        """Enhances the user's query by adding the context from previous bot messages."""

        previous_response = self.memory.get(f"AI (response_num -> {self.query_count})")
        if len(user_query.split()) > 3 or not previous_response:
            return user_query

        redefined_query = "previous_response: " + previous_response + ". user_query: " + user_query
        return redefined_query








