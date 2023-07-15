# Botastico python SDK

[![PyPI version](https://badge.fury.io/py/botastico.svg)](https://badge.fury.io/py/botastico)

## Introduction

This is the official python SDK for Botastico, a sophisticated conversational AI service. The SDK enables developers to easily integrate Botastico's powerful conversational capabilities into their applications, products, or services.

This SDK is designed to interact with the Botastico API, offering an easy and user-friendly way to send and receive messages, manage conversations, and much more. Whether you're building a chatbot, a virtual assistant, or any other kind of conversational application, this SDK will simplify your work and increase your productivity.

## Current Version

The current version of this SDK is designed to work seamlessly with the Langchain ecosystem. It implements the `langchain.chat_models` interface, offering compatibility with other components in the Langchain ecosystem. This ensures you can easily leverage Botastico's conversational abilities within Langchain-powered applications.

Please note that this version of the SDK is primarily focused on conversation management. Features include sending and receiving messages, managing conversational history, and configuring the behavior of the conversational AI.

## Future Plans

This SDK will be expanded in the future to cover the full range of the Botastico API. This will provide additional capabilities such as detailed analytics, advanced conversation management, AI training and customization, and more.

Stay tuned for updates!

## Usage

Here is a basic example of how to use the Botastico SDK:

```python
from botastico.langchain import ChatBotastico
from langchain.schema import HumanMessage

chat = ChatBotastico(
    botastico_agent_id='your_agent_id',
    botastico_api_key='your_api_key'
)

ai_message = chat([
    HumanMessage(content="Please provide me with a SWOT analysis of Unity!")
])

print(ai_message.content)
```

Remember to replace `'your_agent_id'` and `'your_api_key'` with your actual Botastico agent ID and API key.

## Feedback

Your feedback is highly appreciated. If you have any suggestions, questions, or bug reports, please feel free to submit an issue on our GitHub page.

Enjoy building amazing conversational experiences with Botastico!