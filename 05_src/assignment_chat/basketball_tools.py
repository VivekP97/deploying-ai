from openai import OpenAI
from langchain.tools import tool
import requests
import json
import os
from utils.logger import get_logger

_logs = get_logger(__name__)

# Define the model client
client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
            api_key='any value',
            default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# Define the web_search tool for retrieving information about basketball and the NBA.
tools = [
    {
        "type": "web_search",
        "name": "get_basketball_updates",
        "description": "Perform a web search to get up-to-date information about the given question or query which pertains to basketball, specifically with the National Basketball Association.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "The question or query to search on the internet.",
                }
            },
            "required": ["search_query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

# Initiate the input list which we will append the tool output to later.
input_list = [
    {"role": "user", "content": "Who are the top 3 players on the #1 seed in the Eastern Conference?"}
]

def get_basketball_updates(search_query: str) -> str:
    """
    Search the internet to get up-to-date information about the given question or query about basketball, specifically with the National Basketball Association. 
    The response should contain the most up-to-date information as of the current date.
    """
    _logs.debug(f'[get_basketball_updates] Getting answer for: '{search_query}');
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=search_query,
    )
    return response.output



def get_horoscope_from_service(sign:str, day:str):
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {
        "sign": sign.capitalize(),
        "day": day.upper()
    }
    response = requests.get(url, params=params)
    return response



def get_horoscope_from_response(sign:str, response:requests.Response) -> str:
    resp_dict = json.loads(response.text)
    data = resp_dict.get("data")
    horoscope_data = data.get("horoscope_data", "No horoscope found.")
    date = data.get("date", "No date found.")
    horoscope = f"Horoscope for {sign.capitalize()} on {date}: {horoscope_data}"
    return horoscope