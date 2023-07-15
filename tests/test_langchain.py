import pytest
from unittest.mock import patch, Mock
import asyncio
from botastico.langchain import ChatBotastico
from langchain.schema import ChatGeneration, AIMessage, ChatResult
from langchain.schema.messages import HumanMessage

@pytest.fixture
def botastico_instance():
    return ChatBotastico(
        botastico_api_key="test_api_key",
        botastico_agent_id="test_agent_id"
    )

@patch('requests.post')
def test_generate(mock_post, botastico_instance):
    # Mock the API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello"}}]
    }
    mock_post.return_value = mock_response

    # Create a HumanMessage object
    human_message = HumanMessage(role="user", content="Hi")

    # Test _generate method
    result = botastico_instance._generate([human_message])
    assert isinstance(result, ChatResult)
    assert isinstance(result.generations[0], ChatGeneration)
    assert isinstance(result.generations[0].message, AIMessage)
    assert result.generations[0].message.content == "Hello"

@patch('aiohttp.ClientSession.post')
@pytest.mark.asyncio
async def test_agenerate(mock_post, botastico_instance):
    # Mock the API response
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = mock_json  # Use our mock json function

    mock_post.return_value.__aenter__.return_value = mock_response

    # Create a HumanMessage object
    human_message = HumanMessage(role="user", content="Hi")

    # Test _agenerate method
    result = await botastico_instance._agenerate([human_message])
    assert isinstance(result, ChatResult)
    assert isinstance(result.generations[0], ChatGeneration)
    assert isinstance(result.generations[0].message, AIMessage)
    assert result.generations[0].message.content == "Hello"


async def mock_json():
    return {
        "choices": [{"message": {"content": "Hello"}}]
    }