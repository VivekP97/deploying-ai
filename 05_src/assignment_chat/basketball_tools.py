from typing import Dict
from openai import OpenAI
from langchain.tools import tool
import requests
import json
import os
from utils.logger import get_logger
from assignment_chat.basketball_teams import all_nba_teams

_logs = get_logger(__name__)

# Define the BallDontLie API key here so that this code works for others that run it.
# Normally, it would go in the .secrets file.
balldontlie_api_key = "6712f035-bd42-4cf8-88e4-fc7bffdbf25e"

# Define the model client
client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
            api_key='any value',
            default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# Define the web_search tool for retrieving information about basketball and the NBA.
tools = [
    {
        "type": "function",
        "name": "get_basketball_players_list",
        "description": "Retrieve the list of players for the specified basketball team.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the basketball team.",
                }
            },
            "required": ["team_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_basketball_games_info",
        "description": "Retrieve information about basketball games in the 2025 NBA season.",
        "strict": True,
    },
]

# This function searches the all_nba_teams list for the given team name.
def find_team_by_name(team_name: str) -> Dict:
    for tm in all_nba_teams:
        if team_name.lower() in tm["full_name"].lower():
            return tm["id"]

    return {}

# Initiate the input list which we will append the tool output to later.
input_list = [
    {"role": "user", "content": "Who are the top 3 players on the #1 seed in the Eastern Conference?"}
]

@tool
def get_nba_info(search_query: str) -> str:
    """
    Retrieve information about teams, players, and games in the National Basketball Association.
    """
    _logs.debug(f"[get_nba_info] Getting answer for: '{search_query}'")
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=search_query
    )
    return response.output

# Tool to get a list of players for a given team.
def get_basketball_players_list(team_name: str = "toronto raptors") -> str:
    """
    Retrieve the list of players for the specified team in the National Basketball Association.
    """

    # Use the team name to get the team ID
    team_obj = find_team_by_name(team_name)

    url = f"https://api.balldontlie.io/v1/players?team_ids[]={team_obj.id}"
    response = requests.get(url, headers={'Authorization': balldontlie_api_key})
    return response.text

# Tool to get information about games this NBA season.
def get_basketball_games_info() -> str:
    """
    Retrieve information about basketball games for the 2025 NBA season.
    """

    url = f"https://api.balldontlie.io/v1/games?start_date=2025-10-01"
    response = requests.get(url, headers={'Authorization': balldontlie_api_key})
    return response.text