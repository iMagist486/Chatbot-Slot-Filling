import copy
import json
from typing import Any, Dict, List
from pydantic import Field
from datetime import datetime
from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.entity import BaseEntityStore, InMemoryEntityStore
from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseLanguageModel
from langchain.schema.messages import get_buffer_string
from chains.prompt import SLOT_EXTRACTION_PROMPT

# define the slots dict and assign to null
SLOT_DICT = {"name": "null", "origin": "null", "destination": "null", "departure_time": "null"}


class SlotMemory(BaseChatMemory):
    llm: BaseLanguageModel
    slot_extraction_prompt: BasePromptTemplate = SLOT_EXTRACTION_PROMPT
    k: int = 10
    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    chat_history_key: str = "history"
    slot_key: str = "slots"
    inform_check_key: str = "check"
    return_messages: bool = False
    default_slots = SLOT_DICT
    current_slots = copy.deepcopy(default_slots)
    inform_check = False
    entity_store: BaseEntityStore = Field(default_factory=InMemoryEntityStore)
    current_datetime = datetime.now().strftime("%Y/%m/%d %H:%M")

    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        if self.return_messages:
            return self.chat_memory.messages
        else:
            return get_buffer_string(
                self.chat_memory.messages,
                human_prefix=self.human_prefix,
                ai_prefix=self.ai_prefix,
            )

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
        return [self.slot_key, self.chat_history_key, self.inform_check_key]

    def information_check(self):
        self.inform_check = True
        for value in self.current_slots.values():
            if value == "null":
                self.inform_check = False
                break

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        buffer_string = get_buffer_string(
            self.chat_memory.messages[-self.k * 2:],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        slots = self.current_slots
        chain = LLMChain(llm=self.llm, prompt=self.slot_extraction_prompt)
        output = chain.predict(
            history=buffer_string, input=inputs[prompt_input_key], slots=slots, current_datetime=self.current_datetime
        )
        output = output.replace("None", "null")
        try:
            output_json = json.loads(output)
        except Exception:
            print(f"error output: {output}")
            output_json = slots
        for k, v in output_json.items():
            if v is not None and v != "null":
                self.current_slots[k] = v
        self.information_check()
        return {
            self.chat_history_key: buffer_string,
            self.slot_key: str(self.current_slots),
            self.inform_check_key: str(self.inform_check)
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        super().save_context(inputs, outputs)

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
        self.entity_store.clear()
        self.current_slots = copy.deepcopy(self.default_slots)
        self.current_datetime = datetime.now().strftime("%Y/%m/%d %H:%M")
