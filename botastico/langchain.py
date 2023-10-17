from __future__ import annotations
import json
import requests
from aiohttp import ClientSession

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from pydantic import Field, root_validator

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    ChatGeneration,
    ChatResult,
)
from langchain.schema.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.utils import get_from_dict_or_env


class ChatBotastico(BaseChatModel):
    """Wrapper around Botastico Chat service."""

    base_url: str = Field(default="https://api.botasti.co")
    botastico_api_key: str
    botastico_agent_id: str
    temperature: float = 0.7
    max_response_tokens: int = 0
    context_ratio_limit: float = 0.7
    dfp: str = ""
    model_name: str = "gpt-4"
    request_timeout: Optional[Union[float, Tuple[float, float]]] = 600

    class Config:
        """Configuration for this pydantic object."""

        allow_population_by_field_name = True

    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Botastico API."""
        return {
            "temperature": self.temperature,
            "max_response_tokens": self.max_response_tokens,
            "context_ratio_limit": self.context_ratio_limit,
            "dfp": self.dfp,
            "model_name": self.model_name,
        }

    def _create_message_dicts(self, messages: List[BaseMessage]) -> List[dict]:
        message_dicts = [_convert_message_to_dict(message) for message in messages]
        return message_dicts

    def _prepare_request(self, messages: List[BaseMessage], **kwargs: Any):
        message_dicts = self._create_message_dicts(messages)

        headers = {
            "Authorization": f"Bearer {self.botastico_api_key}",
            "Content-Type": "application/json",
        }

        params = self._default_params()
        params.update(
            {
                "prompt": message_dicts[-1]["content"],
                "history": message_dicts[:-1],
            }
        )

        return headers, params

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        headers, params = self._prepare_request(messages, **kwargs)

        response = requests.post(
            f"{self.base_url}/v1/agents/{self.botastico_agent_id}/interactions",
            headers=headers,
            data=json.dumps(params),
            timeout=self.request_timeout,
        )

        if response.status_code == 200:
            resp_json = response.json()
            message = AIMessage(role="ai", content=resp_json["choices"][0]["message"]["content"])
            return ChatResult(generations=[ChatGeneration(message=message)])
        else:
            # Handle the error case here
            pass

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        headers, params = self._prepare_request(messages, **kwargs)

        # Use aiohttp to make the request
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/v1/agents/{self.botastico_agent_id}/interactions",
                json=params,
                headers=headers,
            ) as resp:
                # Check for HTTP errors
                resp.raise_for_status()

                # Parse the JSON response
                response = await resp.json()

        # Extract and return the result
        message = AIMessage(role="ai", content=response["choices"][0]["message"]["content"])
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "botastico"

@root_validator()
def validate_environment(cls, values: Dict) -> Dict:
    """Validate that api key and agent id exist."""
    values["botastico_api_key"] = get_from_dict_or_env(
        values, "botastico_api_key", "BOTASTICO_API_KEY"
    )
    values["botastico_agent_id"] = get_from_dict_or_env(
        values, "botastico_agent_id", "BOTASTICO_AGENT_ID"
    )
    return values

def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if "function_call" in message.additional_kwargs:
            message_dict["function_call"] = message.additional_kwargs["function_call"]
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, FunctionMessage):
        message_dict = {
            "role": "function",
            "content": message.content,
            "name": message.name,
        }
    else:
        raise ValueError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]
    return message_dict