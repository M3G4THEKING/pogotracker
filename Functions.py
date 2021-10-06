from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Auth import denyCommand, permLevel
from Database import addRaid, addUser, findGym, getCodesList, getGym, getRaid, getUsersListByAuth, getUser
from JSONParser import getConfig, getListaRaid, getPermessi
from Raid import Raid
from User import User

import re
#comandi

def codice_amico(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUser(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo codice amico è:{chr(10)}<code>{utente.CodiceAmico}</code>" if utente.CodiceAmico else "/codice_amico CODICE")
	codice = ''.join(command[1:])
	if codice.isdigit() and len(codice) == 12:
		utente.setFriendCode(int(codice))
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo codice amico è ora:{chr(10)}<code>{codice}</code>")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/codice_amico CODICE")

def convertiParametri(text: str):
	return ' '.join(text.split()[1:]).split(':') if len(text.split()) > 1 else []

def distance(utente: User, pos: dict):
	return round(100 * pow(pow((utente.Posizione[0]-pos[0]) * 77.4, 2) + pow((utente.Posizione[1]-pos[1]) * 111.3, 2), 0.5)) / 100

def filterDistance(Palestre: dict, utente: User, limitekm: int, mappa: bool):
	newPal = []
	for pal in Palestre:
		dist = distance(utente, [pal[2], pal[3]]) if (mappa and utente.Posizione) else None
		if (not dist) or (not limitekm) or dist <= limitekm:
			newPal.append([pal, dist])
	#return newPal
	return sorted(newPal, key=lambda pd: pd[1]) if (mappa and utente.Posizione) else sorted(newPal, key=lambda pd: pd[0][1])

def gym(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	filters = []
	command = sanification(update.message.text).split()
	for i in range (1, len(command)):
		filters.append(f'%{command[i].lower()}%')
	Palestre = findGym(filters)
	config = getConfig()
	utente = getUser(update.message.from_user.id)
	Palestre = filterDistance(Palestre, utente, config["limitekm"], config["location"])
	if len(Palestre) == 0:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"""Nessuna palestra trovata{f" col nome {' '.join(command[1:])}" if len(command) > 1 else ""}{f" entro{config['limitekm']}km" if config['limitekm'] else ''}""")
	if len(Palestre) == 1:
		if config["mappa"]:
			context.bot.sendLocation(chat_id = update.message.chat_id, longitude = Palestre[0][0][2], latitude = Palestre[0][0][3])
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Palestra trovata (#{Palestre[0][0][0]}):{chr(10)}{Palestre[0][0][1]}{chr(10)}<code>{Palestre[0][0][3]}, {Palestre[0][0][2]}</code>", parse_mode = "HTML")
	toSendText = f"""Palestre trovate {f" col nome {' '.join(command[1:])}" if len(command) > 1 else ""}{f" entro{config['limitekm']}km" if config['limitekm'] else ''}"""
	numMess = int((len(Palestre) - (len(Palestre) % 50)) / 50) + 1
	for j in range(0, numMess):
		for i in range(50 * j, min(len(Palestre), 50 * (j + 1))):
			toSendText += f"{chr(10)}- {Palestre[i][0][1]} (#{Palestre[i][0][0]}{f', {Palestre[i][1]}km' if Palestre[i][1] else ''})"
		context.bot.sendMessage(chat_id = update.message.chat_id, text = toSendText)
		toSendText = ""

def info(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	config = getConfig()
	command = sanification(update.message.text).split()
	target = (getUser(int(command[1])) if command[1].isdigit() else getUser(None, command[1])) if len(command) > 1 else None
	if len(command) > 1 and (not target):
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Utente non trovato")
	Permessi = getPermessi()
	target = target if target else getUser(update.message.from_user.id)
	toSendText = f"<i>{target.Nome}</i>{f'{chr(10)}<b>Username</b>: @{target.Username}' if target.Username else ''}{chr(10)}<b>ID</b>: {target.IDUtente}{chr(10)}<b>Nickname PoGo</b>: {target.Nickname if target.Nickname else 'Nessuno'} (LV {target.Livello if target.Livello else 'X'}){chr(10)}<b>Team</b>: {config['team'][str(target.Team)]}{f'{chr(10)}<b>Codice amico</b>: <code>{target.CodiceAmico}</code>' if target.CodiceAmico else ''}{chr(10)}<b>Stato</b>: {Permessi[str(target.Autorizzazione)]}"
	return context.bot.sendPhoto(chat_id = update.message.chat_id, photo = target.Screen, caption = toSendText, parse_mode = "HTML") if config["screen"] and target.Screen else context.bot.sendMessage(chat_id = update.message.chat_id, text = toSendText, parse_mode = "HTML")

def livello(update: Update, context: CallbackContext):
	if denyCommand(update, True):
		return
	utente = getUser(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo livello è: <b>{utente.Livello}</b>", parse_mode = "HTML")
	if command[1].isdigit() and int(command[1]) > 0 and int(command[1]) <= 50:
		utente.setLevel(int(command[1]))
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo livello è ora: <b>{int(command[1])}</b>", parse_mode = "HTML")
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
	utente = getUser(update.message.from_user.id)
	command = sanification(update.message.text, True).split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo nickname PoGo è:{chr(10)}<b>{utente.Nickname}</b>" if utente.Nickname else "/nickname NICK", parse_mode = "HTML")
	if not (command[1].isdigit()) and command[1].isalnum():
		utente.setNickname(command[1])
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo nickname PoGo è ora: <b>{command[1]}</b>", parse_mode = "HTML")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/nickname NICK")

def raid(update: Update, context: CallbackContext):
	config = getConfig()
	if permLevel(update.message.from_user.id) < config["raidperm"]:
		return
	param = convertiParametri(sanification(update.message.text))
	if len(param) < 2:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/raid palestra:pokemon:orarioinizio\nEs:\n/raid Queen:Charizard:18.32\noppure\n/raid Fontana:Blastoise:12.50:13.35")
	filters = []
	for i in range (0, len(param[0].split())):
		filters.append(f'%{param[0].split()[i].lower()}%')
	palestra = findGym(filters)
	if len(palestra) != 1:
		sendMessage(context.bot, update.message.chat_id, f"Troppe palestre col nome: {param[0]}" if len(palestra) > 1 else f"Nessuna palestra trovata col nome: {param[0]}")
	palestra = palestra[0] if len(palestra) == 1 else None
	orainizio = transformTime(param[1]) if len(param) > 1 else None
	pokemon = ((param[1] if len(param[1]) <= 64 else param[1][:64]) if len(param) > 1 else None) if not orainizio else None
	orainizio = (transformTime(param[2]) if len(param) > 2 else None) if not orainizio else orainizio
	if not orainizio:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"{param[2 if len(param) > 2 else 1]} non è un orario valido, prova il formato 12.30")
	orafine = transformTime(param[3 if pokemon else 2]) if len(param) > (3 if pokemon else 2) else standardEnding(orainizio)
	orafine = standardEnding(orainizio) if not orafine else orafine
	IDRaid = addRaid(update.message.from_user.id, {"presenti":{}, "invitati": {}, "fly": {}, "rimossi": {}}, pokemon, palestra[0] if palestra else palestra, orainizio, orafine)
	keyboard = [[InlineKeyboardButton("1", callback_data = f"raid {IDRaid} livello 1"), InlineKeyboardButton("3", callback_data = f"raid {IDRaid} livello 3"), InlineKeyboardButton("5", callback_data = f"raid {IDRaid} livello 5"), InlineKeyboardButton("Mega", callback_data = f"raid {IDRaid} livello 6")]]
	if config["mappa"] and palestra:
		context.bot.sendLocation(chat_id = update.message.chat_id, longitude = palestra[2], latitude = palestra[3])
	return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Per prima cosa, scegli il livello del Raid!", reply_markup = InlineKeyboardMarkup(keyboard))

def raidbutton(update: Update, context: CallbackContext):
	utente = getUser(update.callback_query.from_user.id)
	if utente and utente.Autorizzazione < 0:
		return update.callback_query.answer("Non autorizzato")
	if not utente:
		addUser(update.callback_query.from_user.id, update.callback_query.from_user.username, update.callback_query.from_user.first_name)
		utente = getUser(update.callback_query.from_user.id)
	else:
		if utente.Username != update.callback_query.from_user.username:
			utente.setUsername(update.callback_query.from_user.username)
		if utente.Nome != update.callback_query.from_user.name:
			utente.setName(update.callback_query.from_user.name)
	raid = getRaid(int(update.callback_query.data.split()[1]))
	if not raid:
		return update.callback_query.edit_message_text(text = "Raid non trovato!")
	keyboard = []
	config = getConfig()
	keyboard.append([InlineKeyboardButton("Presente", callback_data = f"raid {raid.IDRaid} presenti"), InlineKeyboardButton("Invitami", callback_data = f"raid {raid.IDRaid} invitati")])
	if config["fly"]:
		keyboard.append([InlineKeyboardButton("Remoto", callback_data = f"raid {raid.IDRaid} fly"), InlineKeyboardButton("Toglimi", callback_data = f"raid {raid.IDRaid} remove")])
	else:
		keyboard.append([InlineKeyboardButton("Toglimi", callback_data = f"raid {raid.IDRaid} remove")])
	azione = update.callback_query.data.split()[2]
	if azione == "presenti" or azione == "invitati" or azione == "fly":
		if raid.Partecipanti["rimossi"].get(str(utente.IDUtente), False):
			del raid.Partecipanti["rimossi"][str(utente.IDUtente)]
		raid.Partecipanti[azione][str(utente.IDUtente)] = raid.Partecipanti[azione].get(str(utente.IDUtente), 0) + 1
		raid.setPartecipanti(raid.Partecipanti)
	elif azione == "remove":
		if raid.Partecipanti["presenti"].get(str(utente.IDUtente), 0) or raid.Partecipanti["invitati"].get(str(utente.IDUtente), 0) or raid.Partecipanti["fly"].get(str(utente.IDUtente), 0):
			if raid.Partecipanti["presenti"].get(str(utente.IDUtente), 0):
				del raid.Partecipanti["presenti"][str(utente.IDUtente)]
			if raid.Partecipanti["invitati"].get(str(utente.IDUtente), 0):
				del raid.Partecipanti["invitati"][str(utente.IDUtente)]
			if raid.Partecipanti["fly"].get(str(utente.IDUtente), 0):
				del raid.Partecipanti["fly"][str(utente.IDUtente)]
			raid.Partecipanti["rimossi"][str(utente.IDUtente)] = True
			raid.setPartecipanti(raid.Partecipanti)
		else:
			sendMessage(context.bot, utente.IDUtente, "Non puoi rimuoverti se non stai partecipando!")
			return update.callback_query.answer("Non rimovibile")
	elif azione == "team":
		for color in config["team"]:
			if color == update.callback_query.data.split()[3] and color != utente.Team:
				utente.setTeam(color)
			if update.callback_query.data.split()[3] == utente.Team:
				return update.callback_query.answer("Team non cambiato!")
	else:
		if utente.Autorizzazione < 3 and utente.IDUtente != raid.IDCreatore:
			return update.callback_query.answer("Non autorizzato all'azione")
		if azione == "passex":
			raid.PassEX = not raid.PassEX
			raid.setPassEX(raid.PassEX)
		elif azione == "delete":
			raid.Pokemon = f"<b>CHIUSO</b> da {utente.Username}"
			raid.Stato = "Chiuso"
			keyboard = []
			raid.setPokemon(raid.Pokemon)
			raid.setStato(raid.Stato)
			return update.callback_query.edit_message_text(text = testoRaid(raid), parse_mode = "HTML")
		elif azione == "livello":
			raid.Livello = int(update.callback_query.data.split()[3])
			raid.setLivello(raid.Livello)
		elif azione == "pokemon":
			raid.Pokemon = ' '.join(update.callback_query.data.split()[3:])[:64]
			raid.setPokemon(raid.Pokemon)
		elif azione == "ora":
			raid.OraConfermata = True
			raid.setOraConfermata(True)
		elif azione == "rimossi":
			toSendText = f"I seguenti si sono segnati e rimossi dal raid #{raid.IDRaid}" if len(raid.Partecipanti["rimossi"]) > 0 else "Nessuno si è rimosso dal raid"
			for ID in raid.Partecipanti["rimossi"]:
				toSendText += f"{chr(10)}<code>/info {ID}</code>"
			sendMessage(context.bot, utente.IDUtente, toSendText)
			return update.callback_query.answer("Messaggio rimossi")
		else:
			return update.callback_query.answer("Pulsante non riconosciuto")
	if (not raid.Livello) and raid.Stato != "Chiuso":
		keyboard.append([InlineKeyboardButton("1", callback_data = f"raid {raid.IDRaid} livello 1"), InlineKeyboardButton("2", callback_data = f"raid {raid.IDRaid} livello 2"), InlineKeyboardButton("3", callback_data = f"raid {raid.IDRaid} livello 3"), InlineKeyboardButton("4", callback_data = f"raid {raid.IDRaid} livello 4")])
		keyboard.append([InlineKeyboardButton("5", callback_data = f"raid {raid.IDRaid} livello 5"), InlineKeyboardButton("Mega", callback_data = f"raid {raid.IDRaid} livello 6")])
	if raid.Livello and (not raid.Pokemon) and raid.Stato != "Chiuso":
		listapok = getListaRaid()[str(raid.Livello)]
		righe = int((len(listapok) - 1) / 4) + 1
		for j in range(0, righe):
			riga = []
			for i in range(j * 4, min(len(listapok), (j + 1) * 4)):
				riga.append(InlineKeyboardButton(listapok[i], callback_data = f"raid {raid.IDRaid} pokemon {listapok[i]}"))
			keyboard.append(riga)
	if not raid.OraConfermata:
		keyboard.append([InlineKeyboardButton("Pass Ex?", callback_data = f"raid {raid.IDRaid} passex"), InlineKeyboardButton("Cancella raid", callback_data = f"raid {raid.IDRaid} delete")])
	else:
		keyboard.append([InlineKeyboardButton(config["team"]["giallo"], callback_data = f"raid {raid.IDRaid} team giallo"), InlineKeyboardButton(config["team"]["rosso"], callback_data = f"raid {raid.IDRaid} team rosso"), InlineKeyboardButton(config["team"]["blu"], callback_data = f"raid {raid.IDRaid} team blu")])
		riga = []
		if config["tastorimossi"]:
			riga.append(InlineKeyboardButton("Chi si è tolto?", callback_data = f"raid {raid.IDRaid} rimossi"))
		if config["location"] and raid.IDPalestra:
			riga.append(InlineKeyboardButton("Distanza", url = f"https://telegram.me/raidhelpbot?start=dist{raid.IDPalestra}"))
		if len(riga) > 0:
			keyboard.append(riga)
	if raid.Livello and (not raid.OraConfermata) and raid.Stato != "Chiuso":
		keyboard.append([InlineKeyboardButton("Conferma Raid", callback_data = f"raid {raid.IDRaid} ora conferma")])
	if azione == "ora" and update.callback_query.message.chat_id != config["chatraid"]:
		sent = sendMessage(context.bot, config["chatraid"], testoRaid(raid), keyboard)
		if sent and raid.IDPalestra and config["mappa"]:
			palestra = getGym(raid.IDPalestra)
			context.bot.sendLocation(chat_id = config["chatraid"], longitude = palestra[2], latitude = palestra[3])
		return update.callback_query.edit_message_text(text = "Raid inoltrato nel gruppo!" if sent else "Errore nell'inoltro!")
	return update.callback_query.edit_message_text(text = testoRaid(raid), parse_mode = "HTML", reply_markup = InlineKeyboardMarkup(keyboard))

def readChat(update: Update, context: CallbackContext):
	config = getConfig()
	if update.edited_message:
		return
	if (not update.callback_query) and (not (update.message.chat_id == config["chatadmin"] or update.message.chat.type == "private")):
		return
	perm = permLevel(update.callback_query.from_user.id if update.callback_query else update.message.from_user.id)
	if perm < 0:
		return
	if not perm:
		data = update.callback_query if update.callback_query else update.message
		addUser(data.from_user.id, data.from_user.username, data.from_user.first_name)
		if update.callback_query:
			return
		if config["molestachat"]:
			context.bot.sendMessage(chat_id = update.message.chat_id, text = f"<b>Ciao {update.message.from_user.first_name}!</b>{chr(10)}Invia a {config['userbot']} lo screen del tuo personaggio con nickname, livello e colore del team visibili!{f'{chr(10)}Inoltre, poiché non hai un username telegram, sarebbe comodo che tu ne scegliessi uno' if update.message.from_user.username else ''}", parse_mode = "HTML")
	elif (not update.callback_query) and update.message.chat.type == "private" and perm:
		if config["location"] and update.message.location:
			utente = getUser(update.message.from_user.id)
			return utente.setLocation(update.message.location)
		command = sanification(update.message.text).split()
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
			utente = getUser(update.message.from_user.id)
			if utente.Username != update.message.from_user.username:
				utente.setUsername(update.message.from_user.username)
			if utente.Nome != update.message.from_user.first_name:
				utente.setName(update.message.from_user.first_name)
			if config["screen"] and update.message.photo and update.message.photo[-1] and update.message.photo[-1].file_id:
				utente.setScreen(update.message.photo[-1].file_id)
				context.bot.sendPhoto(chat_id = update.message.from_user.id, photo = update.message.photo[-1].file_id, caption = "Screen impostato!")

def sanification(text: str, hard: bool = False):
	if hard:
		return re.sub("[^0-9a-zA-Z ]+", "", text)
	return re.sub("[^0-9a-zA-Z'.:,@àèéìòù! ]+", "", text)

def sendMessage(bot: Bot, IDChat: int, toSendText: str, keyboard: dict = []):
	try:
		bot.sendMessage(chat_id = IDChat, text = toSendText, parse_mode = "HTML", reply_markup = InlineKeyboardMarkup(keyboard))
		return True
	except:
		return False

def standardEnding(orario: dict):
	term = [orario[0], orario[1] + 45]
	if term[1] >= 60:
		term = [term[0] + 1, term[1] - 60]
		term[0] -= 24 if term[0] > 23 else 0
	return term

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
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Per iniziare, imposta /livello, /nickname in gioco e /team\nSe hai dubbi chiedi agli admin del gruppo!")
	elif len(update.message.text.split()) > 1 and update.message.text.split()[1].replace("dist","").isdigit():
		palestra = getGym(int(update.message.text.split()[1].replace("dist","")))
		if not palestra:
			return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Palestra non trovata")
		else:
			utente = getUser(update.message.from_user.id)
			config = getConfig()
			if ["mappa"]:
				context.bot.sendLocation(chat_id = update.message.chat_id, longitude = palestra[2], latitude = [3])
			return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"""Palestra trovata (#{palestra[0]}):{chr(10)}{palestra[1]}{chr(10)}<code>{palestra[3]}, {palestra[2]}</code>{(f"{chr(10)}Distante {distance(utente, [palestra[2], palestra[3]])}km" if utente.Posizione else f"{chr(10)}Invia la tua posizione per sapere quanto sei distante") if config['location'] else ''}""", parse_mode = "HTML")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "Sei già registrato!")

def stringaOrario(ora):
	return f"{'0' if ora[0] < 10 else ''}{ora[0]}:{'0' if ora[1] < 10 else ''}{ora[1]}"

def team(update: Update, context: CallbackContext):
	if denyCommand(update):
		return
	utente = getUser(update.message.from_user.id)
	command = update.message.text.split()
	if len(command) == 1:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo Team è:{chr(10)}<b>{str(utente.Team)}</b> {getConfig()['team'][str(utente.Team)]}", parse_mode = "HTML")
	if (command[1].lower() == "rosso" or command[1].lower() == "blu" or command[1].lower() == "giallo"):
		utente.setTeam(command[1].lower())
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = f"Il tuo Team è ora:{chr(10)}<b>{command[1].lower()}</b> {getConfig()['team'][command[1].lower()]}", parse_mode = "HTML")
	else:
		return context.bot.sendMessage(chat_id = update.message.chat_id, text = "/team blu/giallo/rosso")

def testoRaid(raid: Raid):
	toSendText = ""
	config = getConfig()
	if raid.IDPalestra:
		pal = getGym(raid.IDPalestra)
		toSendText += f"<b>{pal[1]}</b>{chr(10)}<code>{pal[3]}, {pal[2]}</code>{chr(10)}"
	toSendText += f"{chr(10)}Raid {'MEGA' if raid.Livello == 6 else f'livello {raid.Livello}'} " if raid.Livello else ""
	toSendText += f"{f': <b>{raid.Pokemon}</b>' if raid.Pokemon else ''}{f'{chr(10)}Questo raid potrebbe essere valido per un <b>PASS EX!</b>' if raid.PassEX else ''}"
	toSendText += f"{chr(10)}{chr(10)}<b>Presenti</b>: {sum(raid.Partecipanti['presenti'].values())}"
	for ID in raid.Partecipanti["presenti"]:
		utente = getUser(int(ID))
		toSendText += f"""{chr(10)}{utente.Nickname if utente.Nickname else (utente.Username if utente.Username else utente.Nome)} ({f'{utente.Livello} ' if utente.Livello else ''} {config['team'][str(utente.Team)]}){f" +{raid.Partecipanti['presenti'][str(ID)]} account" if raid.Partecipanti['presenti'][str(ID)] > 1 else ''}"""
	toSendText += f"{chr(10)}{chr(10)}<b>Da Invitare</b>: {sum(raid.Partecipanti['invitati'].values())}"
	for ID in raid.Partecipanti["invitati"]:
		utente = getUser(int(ID))
		toSendText += f"""{chr(10)}{utente.Nickname if utente.Nickname else (utente.Username if utente.Username else utente.Nome)} ({f'{utente.Livello} ' if utente.Livello else ''} {config['team'][str(utente.Team)]}){f" +{raid.Partecipanti['invitati'][str(ID)]} account" if raid.Partecipanti['invitati'][str(ID)] > 1 else ''}"""
	toSendText += f"{chr(10)}{chr(10)}<b>Remoti</b>: {sum(raid.Partecipanti['fly'].values())}"
	for ID in raid.Partecipanti["fly"]:
		utente = getUser(int(ID))
		toSendText += f"""{chr(10)}{utente.Nickname if utente.Nickname else (utente.Username if utente.Username else utente.Nome)} ({f'{utente.Livello} ' if utente.Livello else ''} {config['team'][str(utente.Team)]}){f" +{raid.Partecipanti['fly'][str(ID)]} account" if raid.Partecipanti['fly'][str(ID)] > 1 else ''}"""
	toSendText += f"{chr(10)}{chr(10)}<b>Orario raid</b>: {stringaOrario(raid.OraInizio)} - {stringaOrario(raid.OraFine)}{chr(10)}<b>Partecipanti</b>: {sum(raid.Partecipanti['presenti'].values())+sum(raid.Partecipanti['invitati'].values())+sum(raid.Partecipanti['fly'].values())}{'' if raid.OraConfermata else f'{chr(10)}{chr(10)}Raid non confermato'}{chr(10)}#{raid.IDRaid}"
	return toSendText

def transformTime(text):
	text = text.replace(" ","")
	return [min(23, max(0, int(text.split('.')[0]))), min(59, max(0, int(text.split('.')[1])))] if len(text.split('.')) == 2 and text.split('.')[0].isdigit() and text.split('.')[1].isdigit() else None