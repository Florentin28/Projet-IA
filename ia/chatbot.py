import requests
import json
import os

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Construction du chemin absolu vers le fichier system_prompt.json
# __file__ correspond au chemin du fichier Python actuel
# os.path.dirname(__file__) donne le dossier où se trouve ce script
# os.path.join assemble ce dossier avec "system_prompt.json" pour former un chemin complet
chemin_prompt = os.path.join(os.path.dirname(__file__), "system_prompt.json")

# Lecture du contenu du fichier JSON contenant le prompt système
with open(chemin_prompt, "r", encoding="utf-8") as f:
    system_prompt_data = json.load(f)  # Charge les données JSON en dictionnaire Python

# Extraction de la valeur associée à la clé "content" dans le JSON
# C’est le texte du prompt système qu’on va utiliser pour guider l’IA
system_prompt = system_prompt_data.get("content", "")

def envoyer_message(message):
    """
    Envoie un message utilisateur au serveur LM Studio via l'API REST et retourne la réponse de l'IA.

    Args:
        message (str): Le message saisi par l'utilisateur.

    Returns:
        str: La réponse générée par le modèle d'IA ou un message d'erreur.
    """
    # On combine le prompt système et le message utilisateur en un seul contenu
    # Cela permet de contextualiser la requête pour l'IA en donnant des instructions avant la question
    prompt_complet = system_prompt + "\n\n" + message

    # Construction du payload JSON à envoyer à l'API
    payload = {
        "model": "mistral-7b-instruct-v0.3",  # Modèle utilisé
        "messages": [
            {"role": "user", "content": prompt_complet}  # Message utilisateur avec prompt intégré
        ],
        "temperature": 0.7,  # Paramètre qui contrôle la créativité des réponses
        "max_tokens": 300    # Limite du nombre de tokens générés par la réponse
    }
    
    try:
        # Envoi de la requête POST à l’API LM Studio
        response = requests.post(LM_STUDIO_URL, json=payload)
        response.raise_for_status()  # Vérifie que la requête s’est bien passée (code 200)
        data = response.json()       # Parse la réponse JSON en dict Python

        # Vérifie si la réponse contient bien des choix (réponses générées)
        if "choices" in data and len(data["choices"]) > 0:
            # Retourne le texte contenu dans la première réponse du modèle
            return data["choices"][0]["message"]["content"]
        else:
            return "[Erreur] Réponse inattendue du serveur."
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs liées à la requête HTTP (ex : serveur inaccessible)
        return f"[Erreur HTTP] {e}"
    except Exception as e:
        # Gestion des autres erreurs possibles (ex : erreurs de parsing JSON)
        return f"[Erreur inattendue] {e}"

# Cette condition vérifie que le script est exécuté directement (pas importé en module)
if __name__ == "__main__":
    print("Chatbot prêt. Tape 'quit' pour sortir.")
    # Boucle principale du chatbot en console
    while True:
        user_input = input("Vous : ")  # Lecture de l'entrée utilisateur
        if user_input.lower() == "quit":  # Condition pour quitter la boucle
            break
        reponse = envoyer_message(user_input)  # Envoi du message et réception de la réponse IA
        print("Bot :", reponse)  # Affichage de la réponse
