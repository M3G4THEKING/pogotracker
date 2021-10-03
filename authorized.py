#Cose utili per il bot
import utility

#Agg
def owner(id_utente):
	if id_utente == 119444006:
		return True
	return False

#Agg
def admin(id_utente):
	utente = utility.getUtente(id_utente)
	auth = utente.stato
	if auth == "admin" or owner(id_utente):
		return True
	return False

#Agg
def banned(id_utente):
	utente = utility.getUtente(id_utente)
	auth = utente.stato
	if auth == "bannato":
		return True
	return False

#Agg
def verified(id_utente):
	utente = utility.getUtente(id_utente)
	auth = utente.stato
	if auth == "verificato" or auth == "admin":
		return True
	return False

def sameAuthorization(autorizzazione, id_utente, chat_id):
	if autorizzazione == "moderator" and moderator(id_utente, chat_id):
		return True
	elif autorizzazione == "admin" and admin(id_utente, chat_id):
		return True
	elif autorizzazione == "superadmin" and superadmin(id_utente, chat_id):
		return True
	elif autorizzazione == "basic":
		return False
	elif autorizzazione == "owner":
		return True
	else:
		return False
