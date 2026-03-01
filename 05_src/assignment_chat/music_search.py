from dotenv import load_dotenv
import chromadb
from openai import OpenAI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from utils.logger import get_logger

_logs = get_logger(__name__)

import json

import os

load_dotenv(".env")
load_dotenv(".secrets")

model_client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

chroma_client = chromadb.PersistentClient(path="./assignment_chat/music_db")
albums_collection_name = "music_albums"

# This function loads the music albums from the json file into memory
def load_music_albums() -> list[dict[str, str]]:
    _logs.info("Loading music albums from json file")
    with open("./music_data.json", "r") as f:
        data: list[dict[str, str]] = json.load(f)
    _logs.info(f"Loaded {len(data)} albums")
    return data

# This function generates embeddings for the provided list of data
def generate_embeddings(data: list[dict[str, str]]):
    response = model_client.embeddings.create(
        input = data, 
        model = "text-embedding-3-small"
    )
    return response.data

# This function initializes the vector database client and the collection
def init_music_database():
    _logs.info("[init_music_database] Initializing music database")
    _logs.info(f"[init_music_database] Existing collections: {chroma_client.list_collections()}")

    # Check if collection exists and create it if not
    collection = chroma_client.get_or_create_collection(name=albums_collection_name)
    

        # # Load music data from file
        # albums_list = load_music_albums()

        # # Create embeddings for each album
        # embeddings = [item["embedding"] for item in albums_list]
        # ids = [f"id{i}" for i in range(len(albums_list))]

        # collection.add(
        #     documents=[item["description"] for item in albums_list],
        #     embeddings=embeddings,
        #     ids=ids
        # )
        
    return