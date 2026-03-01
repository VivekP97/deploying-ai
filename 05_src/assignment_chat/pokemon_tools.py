import os
from typing import Literal
from dotenv.main import logger
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from assignment_chat.pokemon_types import *
import operator

from dotenv import load_dotenv
import json
import requests
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")

pokemon_api_v2_base_url = "https://pokeapi.co/api/v2"

@tool
def get_pokemon_info(pokemon_name: str = "flygon"):
    """
    Returns information about the specified pokemon from the Pokemon API.
    """
    _logs.debug(f"[get_pokemon_info] Tool invoked!")
    # Make pokemon name lowercase and strip whitespace
    pokemon_name = pokemon_name.lower().strip()

    url = f"{pokemon_api_v2_base_url}/pokemon/{pokemon_name}"
    response = requests.get(url)
    
    # Check if response is non-200
    if not response.ok:
        _logs.debug(f"Failed to get pokemon info with status: {response.status_code}")
        return PokemonInfoResponseData(name="", types=[], abilities=[], height=0, weight=0);

    data = response.json()

    pokemon_info: PokemonInfoResponseData = {
        "name": data["name"],
        "types": data.get("types", []),
        "abilities": data.get("abilities", []),
        "height": data["height"],
        "weight": data["weight"],
    }

    return pokemon_info

@tool
def get_pokemon_ability_info(ability_name: str = "battle-armor"):
    """
    Returns information about the specified ability from the Pokemon API.
    """
    _logs.debug(f"[get_pokemon_ability_info] Tool invoked!")
    # Make ability lowercase and strip whitespace
    ability_name = ability_name.lower().strip()

    url = f"{pokemon_api_v2_base_url}/ability/{ability_name}"
    response = requests.get(url)
    
    # Check if response is non-200
    if not response.ok:
        _logs.debug(f"Failed to get ability info with status: {response.status_code}")
        return AbilityInfoResponseData(name="", effect_entries=[])

    data = response.json()

    # Filter effect_entries for the English version
    effect_entries: list[EffectEntriesElement] = [
        {
            "effect": entry["effect"],
            "language": {"name": entry["language"]["name"]},
        }
        for entry in data.get("effect_entries", [])
        if entry["language"]["name"] == "en"
    ]

    ability_info: AbilityInfoResponseData = {
        "name": data["name"],
        "effect_entries": effect_entries,
    }

    return ability_info
