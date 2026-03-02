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
        "description": "Retrieve the roster of the specified basketball team, which is a list of players.",
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
        "parameters": {
            "type": "object",
            "properties": {

            },
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_team_info",
        "description": "Retrieve info about a given NBA team.",
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
    }
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
def get_basketball_roster_info(team_name: str) -> str:
    """
    Retrieve information about NBA basketball team rosters. Use this tool for questions about:
    - Which players are on a team (example: "Who is on the Toronto Raptors?")
    - Team rosters and player lists
    """

    input_info = f"Retrieve the roster for the team: {team_name}"

    _logs.debug(f"[get_basketball_roster_info] Tool invoked!")
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=input_info
    )
    return response.output_text

# Tool to get a list of players for a given team.
def get_basketball_players_list(team_name: str = "toronto raptors") -> str:
    """
    Retrieve the list of players on the roster for the specified team in the NBA.
    """

    # Use the team name to get the team ID
    team_obj = find_team_by_name(team_name)

    url = f"https://api.balldontlie.io/v1/players?team_ids[]={team_obj.id}"
    response = requests.get(url, headers={'Authorization': balldontlie_api_key})
    return response.text

@tool
def get_basketball_games_schedule_info(schedule_question: str) -> str:
    """
    Retrieve information about NBA basketball games and the schedule. Use this tool for questions about:
    - What date specific teams faced each other.
    - What dates a team was scheduled to play during the NBA season.
    """
    _logs.debug(f"[get_basketball_games_schedule_info] Tool invoked!")
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=schedule_question
    )
    return response.output_text

# Tool to get information about games this NBA season.
def get_basketball_games_info() -> str:
    """
    Retrieve information about basketball games for the 2025 NBA season.
    """

    url = f"https://api.balldontlie.io/v1/games?start_date=2025-10-01"
    response = requests.get(url, headers={'Authorization': balldontlie_api_key})
    return response.text

@tool
def get_basketball_team_info(team_name: str) -> str:
    """
    Retrieve information about an NBA basketball team. Use this tool for questions like:
    - Tell me about a basketball team
    """

    input_info = f"Retrieve information about the team: {team_name}"

    _logs.debug(f"[get_basketball_games_schedule_info] Tool invoked!")
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=input_info
    )
    return response.output_text

# Tool to get information about a given NBA team.
def get_team_info(team_name: str = "toronto raptors") -> str:
    """
    Retrieve information about a specified NBA team.
    """

    # Use the team name to get the team ID
    team_obj = find_team_by_name(team_name)

    return str(team_obj)