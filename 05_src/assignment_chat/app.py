from assignment_chat.main import get_assignment_chat_agent
from assignment_chat.music_search import init_music_database
from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr
from dotenv import load_dotenv
import os

from utils.logger import get_logger

_logs = get_logger(__name__)

# Initialize the chat agent
llm = get_assignment_chat_agent()

# Initialize the chromadb database (for the Music Search service)
init_music_database()

load_dotenv('.secrets')

def assignment_chat(message: str, history: list[dict]) -> str:
    langchain_messages = []
    n = 0
    _logs.debug(f"History: {history}")
    for msg in history:
        if msg['role'] == 'user':
            langchain_messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            langchain_messages.append(AIMessage(content=msg['content']))
            n += 1
    langchain_messages.append(HumanMessage(content=message))

    state = {
        "messages": langchain_messages,
        "llm_calls": n
    }

    response = llm.invoke(state)
    return response['messages'][len(response['messages']) - 1].content

# Define the chat interface
chat = gr.ChatInterface(
    fn=assignment_chat,
    type="messages",
)

# Launch the chat interface
if __name__ == "__main__":
    _logs.info('Starting Assignment Chat App...')
    chat.launch()
