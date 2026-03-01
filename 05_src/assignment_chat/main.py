import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from assignment_chat.pokemon_tools import get_pokemon_info, get_pokemon_ability_info
#from assignment_chat.basketball_tools import get_basketball_roster_info, get_basketball_games_schedule_info, get_basketball_team_info
from assignment_chat.crypto_tools import get_encryption, get_decryption, get_hash
from assignment_chat.prompts import chat_system_prompt
import operator

from dotenv import load_dotenv
import json
import requests

load_dotenv(".env")
load_dotenv(".secrets")

all_tools = [get_pokemon_info, get_pokemon_ability_info, get_encryption, get_decryption, get_hash]

def get_model_with_tools():
    model = init_chat_model(
        "openai:gpt-4o-mini",
        temperature=0.7,
        base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
        default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
    )
    # Augment the LLM with tools
    model_with_tools = model.bind_tools(all_tools)
    return model_with_tools

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""
    model_with_tools = get_model_with_tools()
    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content=chat_system_prompt
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Performs the tool call"""
    tools_by_name = {tool.name: tool for tool in all_tools}

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

def get_assignment_chat_agent():
    """Returns the assignment chat agent"""    
    # Build workflow
    agent_builder = StateGraph(MessagesState)

    # Add nodes
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END]
    )
    agent_builder.add_edge("tool_node", "llm_call")
    return agent_builder.compile()