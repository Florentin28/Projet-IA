from ia.chatbot import envoyer_message

print("Bienvenue dans Projet-IA")
while True:
    user_input = input("Vous : ")
    if user_input.lower() in ["quit", "exit"]:
        break
    reponse = envoyer_message(user_input)
    print(f"IA : {reponse}")
