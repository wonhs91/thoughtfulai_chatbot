# Thoughtful AI Chatbot

A CLI-based chatbot built using LangGraph, designed to interact with users and provide intelligent responses.

## Features

- Interactive chat interface in the terminal.
- Uses the LangGraph framework for natural language processing.
- Continuously processes user inputs until a quit command is issued.

## Requirements

- Python 3.12
- Required Python libraries (see `requirements.txt` for details).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/chatbot-program.git
    cd chatbot-program
    ```
2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv .venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the .env file:
    - Create a .env file in the root directory of the project:
    ```bash
    touch .env
    ```
    - Add the following line to the .env file:
    ```env
    GROQ_API_KEY=your_api_key_here
    ```
    Replace your_api_key_here with your actual API key. You can retrieve the key from the [GROQ Console](https://console.groq.com/keys).

## Usage
1. Run the chatbot program:
    ```bash
    python chatbot.py
2. Start chatting with the bot! Type `q` to quit.

## Example Interaction
```
Chat with your LangGraph agent. Type 'q' to quit.

You: Hello!
Agent: Hi there! How can I assist you today?

You: What's the weather like?
Agent: I'm not sure, but I can help you find that out.

You: q
Exiting chat. Goodbye!
```