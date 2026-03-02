from dotenv import load_dotenv
import chromadb
from langchain.tools import tool
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
collection = chroma_client.get_or_create_collection(name=albums_collection_name)

# This function loads the music albums from the json file into memory
def load_music_albums() -> list[dict[str, str]]:
    _logs.info("Loading music albums from json file")
    with open("./assignment_chat/music_data.json", "r") as f:
        data: list[dict[str, str]] = json.load(f)
    _logs.info(f"Loaded {len(data)} albums")
    return data

# This function generates embeddings for the provided list of data
def generate_embeddings_for_albums(data: list[dict[str, str]]):
    # Create a list of strings to represent the album data (which are currently dictionaries)
    documents = [json.dumps(item) for item in data]

    # Generate the embeddings all at once instead of individual calls
    response = model_client.embeddings.create(
        input = documents, 
        model = "text-embedding-3-small"
    )
    # Return the embeddings as a list of float lists
    return [item.embedding for item in response.data]

# This function generates embeddings for the provided query
def generate_embedding_for_query(query: str):
    query = query.replace("\n", " ")
    response = model_client.embeddings.create(
        input = query, 
        model = "text-embedding-3-small"
    )
    # Return the embedding as a single list of floats
    return response.data[0].embedding

# This function adds the data to the collection
def add_data_to_collection(data: list[dict[str, str]], collection: chromadb.Collection):
    # Generate embeddings for the albums
    embeddings = generate_embeddings_for_albums(data)

    # Generate ids for the albums
    ids = [f"id{i}" for i in range(len(data))]

    # Create a list of strings to represent the albums (which are currently dictionaries)
    documents = [json.dumps(item) for item in data]

    # Add the data to the collection
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids)

# This function initializes the vector DB collection data
def init_music_database():
    _logs.info("[init_music_database] Initializing music database")
    _logs.info(f"[init_music_database] Existing collections: {chroma_client.list_collections()}")

    if collection.count() == 0:
        _logs.info(f"[init_music_database] Collection {albums_collection_name} is empty, loading data")

        # Get the list of albums from the file
        albums_list = load_music_albums()

        # Call the function to add these albums to the collection
        add_data_to_collection(albums_list, collection)
        _logs.info(f"[init_music_database] Collection {albums_collection_name} initialized with {collection.count()} albums")

    else:
        _logs.info(f"[init_music_database] Collection {albums_collection_name} already has {collection.count()} albums")

    return

@tool
def search_music_albums(query: str, top_n: int = 3) -> str:
    """
    Searches for music albums based on a particular vibe or mood, as indicated by the user's query.
    Returns a text summary of up to top_n albums that match the user's query.
    Example terms that a user may include in the query include, but are not limited to, "electronic", "futuristic", "jazz", and "rock".
    """
    _logs.info(f"[search_music_albums] Searching for music albums with query: {query}")

    # Generate the embedding for the query
    query_embedding = generate_embedding_for_query(query)

    # Query the collection for the albums matching the query
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n)
    rows = list(zip(results['ids'][0], results['distances'][0], results['documents'][0]))

    # Convert the rows into a list of strings
    lines = []
    for _id, _distance, doc_str in rows:
        try:
            doc = json.loads(doc_str) if isinstance(doc_str, str) else doc_str
            lines.append(f"- {doc.get('album', '')} by {doc.get('artist', '')}: {doc.get('description', '')}")
        except (json.JSONDecodeError, TypeError):
            lines.append(str(doc_str))

    # Return the list of strings as a single, combined string
    return "\n".join(lines) if lines else "No matching albums found."