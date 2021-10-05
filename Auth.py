from Database import getAuth
from JSONParser import getConfig

def denyCommand(update):
	config = getConfig()
	if permLevel(update.message.from_user.id) > 0 and (update.message.chat_id == config["chatadmin"] or update.message.chat.type == "private"):
		return False
	return True

def permLevel(IDUtente: int):
	perm = getAuth(IDUtente)
	return perm if perm else 0