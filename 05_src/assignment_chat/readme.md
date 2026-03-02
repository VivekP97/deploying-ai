## Assignment 2 Chatbot Overview

---

### General Overview

This chatbot fulfills the guidelines and requirements described for Assignment 2. 

The chatbot is implemented with gradio and it's designed to speak in a friendly tone and incorporate humor into its responses. A special tone is specified when engaging with the Pokemon service, in which case it will provide responses as if speaking to a child. The chatbot is also informed of restricted topics and is instructed to provide a clear statement that it knows nothing of the requested topic and to ask about something else.

These restricted topics are:

- Cats or dogs
- Horoscopes or Zodiac Signs
- Taylor Swift

This chatbot leverages concepts learned in class to implement 3 unique services with a conversational interface. Users can speak with the chatbot and ask questions or make requests pertaining to the following:

1. Learn about Pokemon and their special abilities.
2. Find music recommendations based on your current mood or vibe.
3. Perform encryption, decryption, and hashing.

**Main files:**

- `main.py` -> Contains the chat agent model definition and configures the tools for it.
- `app.py` -> Initializes the chat agent interface.
- `prompts.py` -> Contains the system prompt defined for the chat agent model.

### (1) API Calls: Pokemon Service

This service provides information about pokemon and their special abilities. It integrates with the free API described at https://pokeapi.co/ to retrieve the information. Responses from the API are rewritten in a more friendly tone, as if speaking to a child.

**Relevant files:**

- `pokemon_tools.py` -> Contains the definitions of the tools that interact with the API
- `pokemon_types.py` -> Contains the definitions of custom types (TypedDict) used to represent data returned from the API

### (2) Semantic Query: Music Recommendation Service

This service provides music recommendations to the user based on the kind of vibe or mood they are looking for. Users can ask the model what to listen to for a "relaxed weekend in the home", "working out at the gym", or other similar phrases. Additionally, they can specify vibes like "futuristic" or "jazzy".

The chatbot will return the top n results from the query and provide brief descriptions in the model's own words. 

The music albums are stored in an in-memory chromadb instance that is configured with file persistence. My original intention was to set up the chromadb instance in docker and have my model interact with that to retrieve the data, but I was having trouble getting it to work correctly when following the instructions in `02_7_vectordb_docker.ipynb`. You can see my attempts in that Jupyter notebook which I have committed and included in this PR. As an alternative, I used the in-memory DB instead.

The `assignment_chat` app will check if the `music_albums` collection exists and contains data. If it does not contain data, it will be populated with the data from `music_data.json`. If there is data in the collection, we simply skip. Therefore, running the `assignment_chat` app will automatically ensure the database is set up correctly for the semantic search. 

**Relevant files/folders:**

- `music_data.json` -> Contains an array of various albums from various artists with descriptions defining the overall mood or theme of the album. This data is loaded in to the vector DB.
- `music_search.py` -> Contains the tools and functions required to interact with the chromadb instance and the model to create the embeddings.
- `music_db` -> This folder contains the files relevant to the local chromadb instance.

### (3) Your Choice: Cryptography Service

This service implements basic cryptography functions: encryption, decryption, and hashing. Each of those functions is implemented as a tool and invoked by the model when necessary.

I chose to have the chatbot return and accept ciphertext as a hexadecimal value instead of bytes to avoid issues with bytes not being represented correctly in the chat. Hex values are lossless so it will ensure that users can encrypt and decrypt text without any issues.

**Relevant files:**

- `crypto_tools.py` -> Contains the definitions of the tools for the model to leverage and the function definitions

_In the `assignment_chat` folder, you will find the `basketball_teams.py` and `basketball_tools.py` files. These files were my initial attempt to implement the "Your Choice" service. I tried to use a free API for NBA data to enable users to ask questions about NBA teams, players, and schedules and invoke function calls for them, but I was not able to get it working correctly. Instead, I decided to implement the cryptography functions. I left the code there just to show my attempts._

## Running the application

---

All of the files required to run my chatbot are contained within the `05_src/assignment_chat` folder, with the exception of the the `.env` and `.secrets` files which are contained in the `05_src` folder.

The `assignment_chat` application can be run by doing the following:

1. Open a Git Bash terminal (or regular terminal for mac).
2. Navigate to the `05_src` folder of this repository using `cd`.
3. Execute the command `python -m assignment_chat.app`. Alternatively, you can run the starter script I created for convenience: `./start_a2.sh`.
  - Note: The command in the `start_a2.sh` script contains the flag `-u` which makes python not buffer output and instead output it immediately. I had to do this in order to view logs in my Git Bash terminal (Windows).
4. Open a browser and enter `http://localhost:7860` into the navigation bar to open the gradio chat interface.