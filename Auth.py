from Database import getAuth
from JSONParser import getConfig

def denyCommand(update):
	config = getConfig()
	if permLevel(update.message.from_user.id) > 0 and (update.message.chat_id == config["admin"] or update.message.chat.type == "private"):
		return False
	return True

def permLevel(IDUtente: int):
	utente = getAuth(IDUtente)
	return utente.PermLevel if utente else 0