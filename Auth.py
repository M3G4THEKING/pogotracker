from Database import getAuth
from JSONParser import getConfig

def denyCommand(update, raidGroup = False):
	config = getConfig()
	if raidGroup and update.message.chat_id == config["chatraid"]:
		return False
	if update.message.chat_id == config["chatadmin"] or update.message.chat.type == "private":
		return False
	return True

def permLevel(IDUtente: int):
	perm = getAuth(IDUtente)
	return perm if perm else 0