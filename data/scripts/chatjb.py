from flask import Flask, request, jsonify
import socket
import os

app = Flask(__name__)

# IRC server configuration (replace with your actual details)
IRC_SERVER = os.getenv("IRC_SERVER", "127.0.0.1")
IRC_PORT = int(os.getenv("IRC_PORT", 6667))
IRC_NICK = os.getenv("IRC_NICK", "FlaskBot")
IRC_USER = os.getenv("IRC_USER", "FlaskBot")
IRC_CHANNEL = os.getenv("IRC_CHANNEL", "#test")

def send_irc_message(message):
    """Connect to IRC server, join channel, send message, then quit."""
    try:
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        irc.connect((IRC_SERVER, IRC_PORT))

        # IRC login sequence
        irc.sendall(f"NICK {IRC_NICK}\r\n".encode("utf-8"))
        irc.sendall(f"USER {IRC_USER} 0 * :Flask IRC Bot\r\n".encode("utf-8"))

        # Wait for server welcome
        while True:
            resp = irc.recv(4096).decode("utf-8", errors="ignore")
            if " 001 " in resp:  # 001 = welcome message
                break

        # Join channel
        irc.sendall(f"JOIN {IRC_CHANNEL}\r\n".encode("utf-8"))

        # Send message
        irc.sendall(f"PRIVMSG {IRC_CHANNEL} :{message}\r\n".encode("utf-8"))

        # Quit
        irc.sendall(b"QUIT\r\n")
        irc.close()
        return True
    except Exception as e:
        print(f"Error sending IRC message: {e}")
        return False

@app.route("/send", methods=["POST"])
def send_message():
    """API endpoint to send a message to the IRC channel."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    if send_irc_message(data["message"]):
        return jsonify({"status": "Message sent"}), 200
    else:
        return jsonify({"error": "Failed to send message"}), 500

if __name__ == "__main__":
    app.run(debug=True)
