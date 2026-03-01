## Assignment 2 Chatbot Overview

### General Overview

This chatbot fulfills the guidelines and requirements described for Assignment 2. 

The chatbot is implemented with gradio and it's designed to speak in a friendly tone and incorporate humor into its responses. A special tone is specified when engaging with the Pokemon service, in which case it will provide responses as speaking to a child. The chatbot is also informed of restricted topics and is instructed to provide a clear statement that it knows nothing of the requested topic and to ask about something else.

These restricted topics are:

- Cats or dogs
- Horoscopes or Zodiac Signs
- Taylor Swift

This chatbot leverages concepts learned in class to implement 3 unique services with a conversational interface. Users can speak with the chatbot and ask questions or make requests pertaining to the following:

1. Learn about Pokemon and their special abilities
2. (Not yet completed)
3. Perform encryption, decryption, and hashing.

### API Calls: Pokemon Service

This service provides information about pokemon and their special abilities. It integrates with the free API described at https://pokeapi.co/ to retrieve the information. Responses from the API are rewritten in a more friendly tone, as if speaking to a child.

### Semantic Query: _Not yet completed_

This service still needs to be implemented.

### Your Choice: Cryptography Service

This service implements basic cryptography functions: encryption, decryption, and hashing. Each of those functions is implemented as a tool and invoked by the model when necessary.

I chose to have the chatbot return and accept ciphertext as a hexadecimal value instead of bytes to avoid issues with bytes not being represented correctly in the chat. Hex values are lossless so it will ensure that users can encrypt and decrypt text without any issues.

_In the `assignment_chat` folder, you will find the `basketball_teams.py` and `basketball_tools.py` files. These files were my initial attempt to implement the "Your Choice" service. I tried to use a free API for NBA data to enable users to ask questions about NBA teams, players, and schedules, but I was not able to get it working correctly. Instead, I decided to implement the cryptography functions. I left the code there just to show my attempts._

## Running the application

All of the files required to run my chatbot are contained within the `05_src/assignment_chat` folder, with the exception of the the `.env` and `.secrets` files which are contained in the `05_src` folder.

The `assignment_chat` application can be run by doing the following:

1. Open a terminal (or Git Bash for Windows).
2. Navigate to the `05_src` folder of this repository.
3. Execute the command `python -m assignment_chat.app`. Alternatively, you can run the starter script I created for convenience: `./start_a2.sh`.
4. Open a browser and enter `http://localhost:7860` into the navigation bar to open the gradio chat interface.