import hashlib
from openai import OpenAI
from cryptography.fernet import Fernet
from langchain.tools import tool
import os
import json
from utils.logger import get_logger
_logs = get_logger(__name__)

key = Fernet.generate_key()
fernet = Fernet(key)

# Define the model client
client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
            api_key='any value',
            default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# Define the system instructions for the local model to use the defined tools
sys_instructions = "You MUST only use the tools provided to you to complete the given task. If the tools do not enable you to complete the task, then say that."

# Define the list of tools available for cryptography actions
tools = [
    {
        "type": "function",
        "name": "encrypt_text",
        "description": "Encrypts the provided text and returns the ciphertext bytes in hexadecimal format.",
        "parameters": {
            "type": "object",
            "properties": {
                "plaintext": {
                    "type": "string",
                    "description": "The plaintext to encrypt.",
                }
            },
            "required": ["plaintext"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "decrypt_text",
        "description": "Convert the given hexadecimal string to bytes, then decrypt the bytes and return the plaintext string.",
        "parameters": {
            "type": "object",
            "properties": {
                "ciphertext_hex": {
                    "type": "string",
                    "description": "The ciphertext, represented in hexadecimal format, that needs to be decrypted.",
                }
            },
            "required": ["ciphertext_hex"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "generate_hash",
        "description": "Generate a hash value for the given text.",
        "parameters": {
            "type": "object",
            "properties": {
                "plaintext": {
                    "type": "string",
                    "description": "The text to generate a hash for.",
                }
            },
            "required": ["plaintext"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

def _run_inner_llm_with_tool_loop(prompt: str, max_turns: int = 3) -> str:
    """
    Call the inner LLM with the crypto tools and feed the results back to the model to execute the correct tool.
    """
    input_list = [{"role": "user", "content": prompt}]

    # Use a max_turns limit to prevent infinite loops with tool calls
    for _ in range(max_turns):
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=sys_instructions,
            tools=tools,
            input=input_list,
        )

        # Append the model's output (e.g. reasoning, function_call) to context
        input_list = input_list + list(response.output)

        # Execute any encrypt_text tool calls and append their outputs
        has_tool_call = False
        for item in response.output:
            # Skip non-function calls
            if item.type != "function_call":
                continue

            has_tool_call = True

            args = json.loads(item.arguments)

            # Execute the appropriate tool function and store the result
            if item.name == "encrypt_text":
                tool_output = encrypt_text(**args)
            elif item.name == "decrypt_text":
                tool_output = decrypt_text(**args)
            elif item.name == "generate_hash":
                tool_output = generate_hash(**args)
            else:
                _logs.error("[_run_inner_llm_with_tool_loop] Unknown tool call: %s", item.name)
                continue

            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": tool_output,
            })

        # If no tool calls were made, return the model's output
        if not has_tool_call:
            return response.output_text

    return response.output_text


@tool
def get_encryption(plaintext: str) -> str:
    """
    Encrypt the provided plaintext and return the ciphertext in hexadecimal format.
    """
    _logs.debug("[get_encryption] Tool invoked!")
    _logs.debug("[get_encryption] Encrypting plaintext: %s", plaintext)

    prompt = f"Encrypt the provided plaintext into hexadecimal ciphertext: {plaintext}"
    return _run_inner_llm_with_tool_loop(prompt)

@tool
def get_decryption(ciphertext_hex: str) -> str:
    """
    Convert the given hexadecimal string to bytes, then decrypt the bytes and return the plaintext string.
    """
    _logs.debug("[get_decryption] Tool invoked!")
    _logs.debug("[get_decryption] Decrypting hex ciphertext: %s", ciphertext_hex)

    prompt = f"Decrypt the provided hexadecimal ciphertext into plaintext: {ciphertext_hex}"
    return _run_inner_llm_with_tool_loop(prompt)

@tool
def get_hash(plaintext: str) -> str:
    """
    Generate a hash value for the provided plaintext.
    """
    _logs.debug("[get_hash] Tool invoked!")
    _logs.debug("[get_hash] Generating hash for plaintext: %s", plaintext)
    
    prompt = f"Generate a hash value for the provided plaintext: {plaintext}"
    return _run_inner_llm_with_tool_loop(prompt)

# Function to encrypt the given plaintext
def encrypt_text(plaintext: str) -> str:
    val = fernet.encrypt(plaintext.encode())
    _logs.debug(f"[encrypt_text] Encrypted text in hexadecimal: {val.hex()}")
    return val.hex()

# Function to decrypt the given ciphertext
def decrypt_text(ciphertext_hex: str) -> str:
    ciphertext = bytes.fromhex(ciphertext_hex)
    val = fernet.decrypt(ciphertext)
    _logs.debug(f"[decrypt_text] Decrypted text: {val.decode()}")
    return val.decode()

# Function to generate a hash value for the given plaintext
def generate_hash(plaintext: str) -> str:
    val = hashlib.sha256(plaintext.encode()).hexdigest()
    _logs.debug(f"[generate_hash] Hash value: {val}")
    return val
