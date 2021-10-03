from telegram import Update
from telegram.ext import CallbackContext

from Auth import denyCommand, permLevel
from Database import addUser, getCodesList, getUsersListByAuth, getUtente

from JSONParser import getConfig, getPermessi

#comandi, gym, legit, multi, raid, raidbutton

def getUser(update: Update, context: CallbackContext):
	perm = permLevel(update.message.from_user.id)
	if perm < 0:
		return
	config = getConfig()
	if (not perm) and (update.message.chat_id == config["chatadmin"] or update.message.chat.type == "private"):
		addUser(update.message.from_user.id, update.message.from_user.username, update.message.from_user.first_name)
		if config["molestachat"] and update.message.chat_id == config["chatadmin"]:
			context.bot.sendMessage(chat_id = update.message.chat_id, text = f"<b>Ciao {update.message.from_user.first_name}!</b>{chr(10)}Invia a {config['userbot']} lo screen del tuo personaggio con nickname, livello e colore del team visibili!{f'{chr(10)}Inoltre, poiché non hai un username telegram, sarebbe comodo che tu ne scegliessi uno' if update.message.from_user.username else ''}", parse_mode = "HTML")
	elif update.message.chat.type == "private" and perm:
		command = update.message.text.split()
		if command[0][0] == "!":
			if command[0].lower() == "!admin":
				context.bot.sendMessage(chat_id = update.message.chat_id, text = mostraUtenti(getUsersListByAuth(2)))
			elif command[0].lower() == "!codici":
				context.bot.sendMessage(chat_id = update.message.chat_id, text = mostraCodici(getCodesList(command[1].lower() if (command[1].lower() == "rosso" or command[1].lowe() == "blu" or command[1].lower() == "giallo") else None)))
			#elif command[0][0] == "!comandi":
			#	context.bot.sendMessage(chat_id = update.message.chat_id, text = commandsList())
			#else:
			#	personalizedCommand(context.bot, update, command[0][1:])
		else:
			utente = getUtente(update.message.from_user.id)
			if utente.username != update.message.from_user.username:
				utente.setUsername(update.message.from_user.username)
			if utente.nome != update.message.from_user.first_name:
				utente.setName(update.message.from_user.first_name)
			if config["screen"] and update.message.photo and update.mesage.photo[-1] and update.mesage.photo[-1].file_id:
				utente.setScreen(update.message.photo[-1].file_id)
				context.bot.sendPhoto(chat_id = update.message.from_user.id, photo = update.message.photo[-1].file_id, caption = "Screen impostato!")

def codice_amico(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUtente(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo codice amico è:{chr(10)}<code>{utente.CodiceAmico}</code>" if utente.CodiceAmico else "/codice_amico CODICE")
	codice = ''.join(command[1:])
	if codice.isdigit() and len(codice) == 12:
		utente.setFriendCode(int(codice))
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo codice amico è ora:{chr(10)}<code>{codice}</code>")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/codice_amico CODICE")

def info(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	config = getConfig()
	command = update.message.text.split()
	target = (getUtente(int(command[1])) if command[1].isdigit() else getUtente(None, command[1])) if len(command) > 1 else None
	if len(command) > 1 and (not target):
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Utente non trovato")
	Permessi = getPermessi()
	target = target if target else getUtente(update.message.from_user.id)
	toSendText = f"<i>{target.Nome}</i>{f'{chr(10)}<b>Username</b>: @{target.Username}' if target.Username else ''}{chr(10)}<b>ID</b>: {target.IDUtente}{chr(10)}<b>Nickname PoGo</b>: {target.Nickname if target.Nickname else 'Nessuno'} (LV {target.Livello if target.Livello else 'X'}){chr(10)}<b>Team</b>: {config['team'][str(target.Team)]}{f'{chr(10)}<b>Codice amico</b>: <code>{target.CodiceAmico}</code>' if target.CodiceAmico else ''}{chr(10)}<b>Stato</b>: {Permessi[str(target.Autorizzazione)]}{f'{chr(10)}Multiaccount: {target.Multi}' if target.Multi else ''}"
	return context.bot.sendPhoto(chat_id = update.message.chat_id, photo = target.Screen, caption = toSendText, parse_mode = "HTML") if config["screen"] and target.Screen else context.bot.sendMessage(chat_id = update.message.chat_id, text = toSendText, parse_mode = "HTML")

def livello(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUtente(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo livello è: <b>{utente.Livello}</b>")
	if command[1].isdigit() and int(command[1]) > 0 and int(command[1]) <= 50:
		utente.setLevel(int(command[1]))
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo livello è ora: <b>{int(command[1])}</b>")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Il livello deve essere compreso tra 1 e 50")

def mostraCodici(codici):
	toSendText = "<b>CODICI AMICO</b>"
	for utente in codici:
		toSendText += f"{chr(10)}<i>{utente[0]}</i>{f' ({utente[2] if utente[2] else utente[3]})' if (utente[2] or utente[3]) else ''}:<code>{utente[1]}</code>"
	return toSendText

def mostraUtenti(lista):
	toSendText = "<b>Lista Utenti</b>"
	for utente in lista:
		toSendText += f"{chr(10)}<i>{utente[11]}</i>{f' ({utente[1]})' if utente[1] else ''}{f' (LV {utente[3]})' if utente[3] else ''}"
	return toSendText

def nickname(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUtente(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo nickname PoGo è:{chr(10)}<b>{utente.Nickname}</b>" if utente.Nickname else "/nickname NICK")
	if not (command[1].isdigit()) and command[1].isalnum():
		utente.setNickname(command[1])
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo nickname PoGo è ora: <b>{command[1]}</b>")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/nickname NICK")

def raid(update: Update, context: CallbackContext):
	return

def raidbutton(update: Update, context: CallbackContext):
	return

def start(update: Update, context: CallbackContext):
	if update.message.chat.type != "private":
		return
	perm = permLevel(update.message.from_user.id)
	if perm < 0:
		return
	#if len(update.message.text.split()) > 1:
	#	return functions.addtoraid(bot, update)
	if not perm:
		addUser(update.message.from_user.id, update.message.from_user.username, update.message.from_user.first_name)
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Per iniziare, imposta in privato livello, nickname in gioco e squadra. Per sapere come funzionano i comandi, inviami !guida o /help\nSe hai dubbi chiedi agli admin del gruppo, dopo che avrai inviato tutto questo il tuo account verrà verificato e saremo pronti per iniziare!")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Sei già registrato!")

def team(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUtente(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo Team è:{chr(10)}<b>{str(utente.Team)}</b> {getConfig()['team'][str(utente.Team)]}")
	if (command[1].lower() == "rosso" or command[1].lower() == "blu" or command[1].lower() == "giallo"):
		utente.setTeam(command[1].lower())
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo Team è ora:{chr(10)}<b>{command[1].lower()}</b> {getConfig()['team'][command[1].lower()]}")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/team blu/giallo/rosso")