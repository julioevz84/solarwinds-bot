from flask import Flask, request
import requests
import orionsdk

TOKEN = "TU_TOKEN"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
SOLARWINDS_HOST = "IP_O_HOST_SOLARWINDS"
SW_USER = "usuario_api"
SW_PASS = "password_api"

swis = orionsdk.SwisClient(SOLARWINDS_HOST, SW_USER, SW_PASS)
app = Flask(__name__)

def send_message(chat_id, text, thread_id=None):
    data = {"chat_id": chat_id, "text": text}
    if thread_id:
        data["message_thread_id"] = thread_id
    requests.post(f"{TELEGRAM_API}/sendMessage", data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    message = update.get("message", {})
    chat_id = message["chat"]["id"]
    thread_id = message.get("message_thread_id")
    text = message.get("text", "")

    if text.startswith("/estado"):
        node_name = text.split(" ")[1]
        result = swis.query(f"SELECT Caption, StatusDescription FROM Orion.Nodes WHERE Caption LIKE '{node_name}'")
        if result["results"]:
            node = result["results"][0]
            send_message(chat_id, f"Nodo: {node['Caption']} Estado: {node['StatusDescription']}", thread_id)
        else:
            send_message(chat_id, "Nodo no encontrado", thread_id)

    return "OK"
