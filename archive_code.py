import requests
import os

# ------------------------
# CONFIG
# ------------------------
ECHO_API = "http://127.0.0.1:8080/api/echo/chat"
SESSION_ID = "local_session"  # session name for history, can be per user
SAVE_DIR = "./generated_code"  # where to save outputs

# Make sure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def generate_code(prompt: str) -> str:
    """
    Sends a prompt to Echo API and returns the code output.
    """
    system_prompt = (
        "SYSTEM: You are a code-generation engine.\n"
        "Rules:\n"
        "- Output full working code ONLY\n"
        "- No greetings\n"
        "- No explanations\n\n"
    )

    payload = {
        "message": system_prompt + prompt,
        "session_id": SESSION_ID
    }

    try:
        response = requests.post(ECHO_API, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[Echo] No response returned")
    except Exception as e:
        return f"[Error] {e}"

def save_code(code: str, filename: str):
    """
    Save the generated code to a file.
    """
    path = os.path.join(SAVE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[Saved] {path}")

# ------------------------
# MAIN LOOP
# ------------------------
def main():
    print("=== Local Code Generator ===")
    print("Type your instructions. Type 'exit' to quit.\n")

    counter = 1
    while True:
        prompt = input("Prompt> ").strip()
        if prompt.lower() in ("exit", "quit"):
            break
        if not prompt:
            continue

        print("\n[Generating...]\n")
        code_output = generate_code(prompt)
        print(code_output)

        # Automatically save output to disk
        filename = f"output_{counter}.txt"
        save_code(code_output, filename)
        counter += 1
        print("\n---\n")

if __name__ == "__main__":
    main()
