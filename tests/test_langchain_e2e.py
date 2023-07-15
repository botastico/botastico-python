import pytest
from botastico.langchain import ChatBotastico
from langchain.schema import ChatResult, ChatGeneration, AIMessage
from langchain.schema.messages import HumanMessage

@pytest.fixture
def botastico_instance():
    return ChatBotastico(
        botastico_api_key="test_api_key",
        botastico_agent_id="test_agent_id",
        base_url="http://localhost:8000"   # Point to mock server
    )

def test_generate(botastico_instance):
    # Create a HumanMessage object
    human_message = HumanMessage(role="user", content="Hi")

    # Test _generate method
    result = botastico_instance._generate([human_message])
    assert isinstance(result, ChatResult)
    assert isinstance(result.generations[0], ChatGeneration)
    assert isinstance(result.generations[0].message, AIMessage)
    assert result.generations[0].message.content == "Hello, I am the Botastico service!"

@pytest.mark.asyncio
async def test_agenerate(botastico_instance):
    # Create a HumanMessage object
    human_message = HumanMessage(role="user", content="Hi")

    # Test _agenerate method
    result = await botastico_instance._agenerate([human_message])
    assert isinstance(result, ChatResult)
    assert isinstance(result.generations[0], ChatGeneration)
    assert isinstance(result.generations[0].message, AIMessage)
    assert result.generations[0].message.content == "Hello, I am the Botastico service!"