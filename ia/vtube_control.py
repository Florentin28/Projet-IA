import websocket
import json
import os
import threading

PLUGIN_NAME = "MonPluginPython"
PLUGIN_DEVELOPER = "Moi"
TOKEN_FILE = "vtube_token.txt"

token = None

# Liste des expressions disponibles (avec noms simples associés)
EXPRESSIONS = {
    "angry": "Angry.exp3.json",
    "blushing": "Blushing.exp3.json",
    "f01": "f01.exp3.json",
    "f02": "f02.exp3.json",
    "normal": "Normal.exp3.json",
    "sad": "Sad.exp3.json",
    "smile": "Smile.exp3.json",
    "surprised": "Surprised.exp3.json"
}

def load_token():
    global token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
            if token:
                print(f"Token chargé depuis fichier : {token}")

def save_token(new_token):
    with open(TOKEN_FILE, "w") as f:
        f.write(new_token)
    print("Token sauvegardé.")

def send_expression(ws, expression_name, disable_others=True):
    """Active une expression, désactive les autres si disable_others=True"""
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "activate_expression",
        "messageType": "ExpressionActivationRequest",
        "data": {
            "expressionFile": expression_name,
            "active": True,
            "disableOthers": disable_others
        }
    }
    ws.send(json.dumps(request))
    print(f"Expression '{expression_name}' activée (disableOthers={disable_others}).")

def deactivate_all_expressions(ws):
    """Désactive toutes les expressions"""
    for exp in EXPRESSIONS.values():
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": f"deactivate_{exp}",
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": exp,
                "active": False,
                "disableOthers": False
            }
        }
        ws.send(json.dumps(request))
    print("Toutes les expressions ont été désactivées.")

def activate_expression(ws, simple_name):
    """Active une expression si elle existe dans la map"""
    expression_name = EXPRESSIONS.get(simple_name.lower())
    if expression_name:
        send_expression(ws, expression_name, disable_others=True)
    else:
        print(f"⚠️ Expression '{simple_name}' inconnue, impossible de l'activer.")

def request_expressions(ws):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "list_expressions",
        "messageType": "ExpressionStateRequest",
        "data": {
            "details": True,
            "expressionFile": ""
        }
    }
    ws.send(json.dumps(request))
    print("Demande de la liste des expressions envoyée.")

def on_open(ws):
    print("Connecté à VTube Studio !")

    if token:
        print("Authentification avec token existant...")
        auth = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEVELOPER,
                "authenticationToken": token
            }
        }
        ws.send(json.dumps(auth))
    else:
        print("Demande de nouveau token...")
        token_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "token_request",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEVELOPER
            }
        }
        ws.send(json.dumps(token_request))

def on_message(ws, message):
    global token
    print("Message reçu :", message)
    response = json.loads(message)

    message_type = response.get("messageType")

    if message_type == "AuthenticationTokenResponse":
        token = response["data"].get("authenticationToken")
        print(f"Token reçu : {token}")
        save_token(token)
        print("Authentification en cours...")

        auth = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth_final",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEVELOPER,
                "authenticationToken": token
            }
        }
        ws.send(json.dumps(auth))

    elif message_type == "AuthenticationResponse":
        if response["data"].get("authenticated"):
            print("✅ Authentification réussie !")
            request_expressions(ws)
        else:
            print("❌ Authentification échouée.")

    elif message_type == "ExpressionStateResponse":
        expressions = response["data"].get("expressions", [])
        if expressions:
            print("Expressions disponibles dans le modèle :")
            for exp in expressions:
                print(f" - {exp['file']} (active: {exp['active']})")
        else:
            print("Aucune expression trouvée dans le modèle.")

        # Active "angry" par défaut
        activate_expression(ws, "angry")

    elif message_type == "ExpressionActivationResponse":
        print("Activation d'expression réussie.")

    elif message_type == "APIError":
        print("Erreur API :", response["data"].get("message"))

def on_error(ws, error):
    print("Erreur :", error)

def on_close(ws):
    print("Connexion fermée.")

def console_loop(ws):
    while True:
        print("\nExprime-toi : entre un nom d'expression parmi :")
        for key in EXPRESSIONS.keys():
            print(f" - {key}")
        print(" - reset (désactive toutes les expressions)")
        expr = input("Expression à activer (ou 'quit' pour quitter) > ").strip()
        if expr.lower() == "quit":
            print("Fermeture du programme.")
            ws.close()
            break
        elif expr.lower() == "reset":
            deactivate_all_expressions(ws)
        else:
            activate_expression(ws, expr)

if __name__ == "__main__":
    load_token()
    url = "ws://127.0.0.1:8001"

    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    threading.Thread(target=console_loop, args=(ws,), daemon=True).start()

    ws.run_forever()
