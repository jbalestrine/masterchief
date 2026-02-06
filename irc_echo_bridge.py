import socket
import requests
import time

# =========================
# IRC CONFIG
# =========================
IRC_SERVER = "127.0.0.1"
IRC_PORT = 6667
IRC_NICK = "EchoAI"
IRC_CHANNEL = "#masterchief"

# =========================
# ECHO CONFIG
# =========================
ECHO_API = "http://127.0.0.1/api/echo/chat"

# Track initialized sessions
initialized_sessions = set()

# =========================
# IRC CONNECT
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IRC_SERVER, IRC_PORT))

def send(line):
    sock.sendall((line + "\r\n").encode("utf-8"))

send(f"NICK {IRC_NICK}")
send(f"USER {IRC_NICK} 0 * :Echo AI Bridge")
time.sleep(1)
send(f"JOIN {IRC_CHANNEL}")

print("[Bridge] Connected and ready")

# =========================
# MAIN LOOP
# =========================
while True:
    data = sock.recv(4096).decode("utf-8", errors="ignore")

    for line in data.split("\r\n"):
        if not line:
            continue

        # Keepalive
        if line.startswith("PING"):
            send("PONG " + line.split()[1])
            continue

        # Only handle /ai
        if "PRIVMSG" in line and "/ai " in line:
            try:
                # Parse nick
                prefix = line.split("!", 1)[0]
                nick = prefix[1:] if prefix.startswith(":") else "user"
                session_id = f"irc_{nick}"

                # Extract prompt
                prompt = line.split("/ai ", 1)[1].strip()

                # -------------------------------------------------
                # STEP 1: PRIME SESSION (Echo greeting is consumed)
                # -------------------------------------------------
                if session_id not in initialized_sessions:
                    requests.post(
                        ECHO_API,
                        json={
                            "message": "",
                            "session_id": session_id
                        },
                        timeout=30
                    )
                    initialized_sessions.add(session_id)

                # -------------------------------------------------
                # STEP 2: REAL REQUEST
                # -------------------------------------------------
                r = requests.post(
                    ECHO_API,
                    json={
                        "message": prompt,
                        "session_id": session_id
                    },
                    timeout=180
                )

                data = r.json()
                reply = data.get("response", "").strip()

                if not reply:
                    reply = "[Echo] Empty response"

                # IRC-safe chunking
                for i in range(0, len(reply), 380):
                    send(f"PRIVMSG {IRC_CHANNEL} :{reply[i:i+380]}")

            except Exception as e:
                send(f"PRIVMSG {IRC_CHANNEL} :[Bridge Error] {e}")
