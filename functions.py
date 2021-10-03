#functions
#Funzioni principali del bot atte ad interagire con l'utente(o meglio, gli admin del bot)
import authorized, utility

import string

from telegram.ext import CommandHandler

from uuid import uuid4

configfile = open("config.txt", "r")
config = configfile.read().split()

chat_dedicata = str(config[1])
flyflag = str(config[3])
if flyflag == "True":
	flyflag = True
else:
	flyflag = False
botusername = str(config[5])
raidperm = str(config[7])
molestachat = str(config[9])
mappa = str(config[11])
if mappa == "True":
	mappa = True
else:
	mappa = False
tastorimossi = str(config[13])
if tastorimossi == "True":
	tastorimossi = True
else:
	tastorimossi = False
limitedistanza = int(config[15]) #numero in chilometri, non c'è se impostato a 0

from utility import cur,conn

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle

import time

#try:
#	import Image
#except:
#	from PIL import Image
#import pytesseract

def codice_amico(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	if len(command) > 3:
		command = update.message.text.replace(" ","")
		command = command.replace("/codice_amico","/codice_amico ")
	else:
		command = update.message.text
	command = command.split()
	reply = update.message.reply_to_message
	codice_amico = "0"
	utente = utility.getUtente(update.message.from_user.id)
	if str(reply) == "None":
		if len(command) > 1:
			try:
				if len(command) > 3:
					codice_amico = int(command[1]+command[2]+command[3])
					codice_amico = command[1]+command[2]+command[3]
					if len(command) > 4 and authorized.admin(utente.id_utente):
						id_target = utility.gettarget(command[4])
						if id_target == 0:
							return
					else:
						id_target = utente.id_utente
				else:
					codice_amico = int(command[1])
					codice_amico = command[1]
					if len(command) > 2 and authorized.admin(utente.id_utente):
						id_target = utility.gettarget(command[2])
						if id_target == 0:
							return
					else:
						id_target = utente.id_utente
			except:
				tosendtext = "Rispondi ad un messaggio preinviato o manda il messaggio come:\n/codice 123456789012"
		else:
			tosendtext = "Rispondi ad un messaggio preinviato o manda il messaggio come:\n/codice 123456789012"
	else:
		testo = reply.text.split()
		try:
			codice_amico = int(testo[0])
			codice_amico = testo[0]	
		except:
			tosendtext = "Manda un valore numerico"
	if len(str(codice_amico)) != 12:
		tosendtext = "Il codice_amico deve essere lungo 12 caratteri."
		codice_amico = "0"
	if codice_amico != "0":
		cur.execute("update utenti set codice_amico = (%(codice_amico)s) where id_utente = (%(id_utente)s)", {'codice_amico':str(codice_amico), 'id_utente':id_target})
		tosendtext = "Codice impostato correttamente: <b>" + str(codice_amico) + "</b>"
		conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def comandi(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	chat_id = update.message.chat_id
	cur.execute("select nome from comandi order by nome asc")
	found = cur.fetchall()
	if len(found) == 0:
		return
	tosendtext = "<b>Comandi rapidi:</b>\n"
	for i in range(0, len(found)):
		tosendtext += "\n!" + found[i][0]
	bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")

def comandiPersonalizzati(bot, update):
	chat_id = update.message.chat_id
	comando = update.message.text.split()[0][1:]
	cur.execute("select * from comandi where nome = (%(nome)s)", {'nome':comando.lower()})
	found = cur.fetchall()
	if len(found) == 0:
		return
	if found[0][2]:
		bot.sendPhoto(chat_id = chat_id, photo = found[0][1])
	else:
		bot.sendMessage(chat_id = chat_id, text = found[0][1], parse_mode = "HTML")

def database(bot, update):
	getuser(bot, update)
	chat_id = update.message.chat_id
	command = update.message.text.split()
	length = len(command)
	messagefilter = 0
	if not utility.checkGroup(bot, update):
		if length != 3:
			if length == 5 and command[3] == "#":
				try:
					messagefilter = int(command[4])
				except:
					messagefilter = 0
			else:
				bot.sendMessage(chat_id = chat_id, text = "Sintassi errata: /database utenti/admin/bannati nomeGruppo")
				return
		group_id = utility.groupID(command[2])
		if group_id == 0:
			bot.sendMessage(chat_id = chat_id, text = "Gruppo non trovato, consulta la lista con /gruppi")
			return
	else:
		group_id = chat_id
		if length != 2:
			bot.sendMessage(chat_id = chat_id, text = "Sintassi errata: /database utenti/admin/bannati/assenti")
			return
	if not authorized.moderator(update.message.from_user.id, group_id):
		bot.sendMessage(chat_id=chat_id, text = "Non hai giurisdizione in quel gruppo")
		return
	if command[1] == "utenti":
		lista_utenti = []
		lista_provv = utility.groupNoBanned(group_id)
		for i in range(0, len(lista_provv)):
			if lista_provv[i].messaggi >= messagefilter:
				lista_utenti.append(lista_provv[i])
		tosendtext = "Abbiamo " + str(len(lista_utenti)) + " utenti in lista:\n"
		bot.sendMessage(chat_id = chat_id, text = tosendtext)
		countLines = len(lista_utenti)
		lpm = 50
		countMessages = int(countLines/lpm)
		if countLines % lpm != 0:
			countMessages += 1
		for i in range(0, countMessages):		
			tosendtext = ""
			#Calcolo il massimo di righe da mettere nel messaggio che segue, se è minore del massimo per messaggio lo mette com massimo del ciclo
			maxim = lpm
			cap = countLines - i*lpm
			if cap < maxim:
				maxim = cap
			for k in range(0, maxim):
				if (i*lpm+k) < countLines:
					tosendtext += "ID:" + str(lista_utenti[i*lpm+k].id_utente) + ", <b>@" + lista_utenti[i*lpm+k].username + "</b>, Messaggi: " + str(lista_utenti[i*lpm+k].messaggi) + ", Warn: " + str(lista_utenti[i*lpm+k].warn) + "\n" 
			bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
		return
	if command[1] == "assenti":
		lista_utenti = []
		lista_provv = utility.groupNoBanned(group_id)
		aggiornaAssenze(bot, group_id, lista_provv)
		lista_provv = utility.groupAbsent(group_id)
		for i in range(0, len(lista_provv)):
			if lista_provv[i].messaggi >= messagefilter:
				lista_utenti.append(lista_provv[i])
		tosendtext = "Abbiamo " + str(len(lista_utenti)) + " utenti in lista:\n"
		bot.sendMessage(chat_id = chat_id, text = tosendtext)
		countLines = len(lista_utenti)
		lpm = 50
		countMessages = int(countLines/lpm)
		if countLines % lpm != 0:
			countMessages += 1
		for i in range(0, countMessages):		
			tosendtext = ""
			#Calcolo il massimo di righe da mettere nel messaggio che segue, se è minore del massimo per messaggio lo mette com massimo del ciclo
			maxim = lpm
			cap = countLines - i*lpm
			if cap < maxim:
				maxim = cap
			for k in range(0, maxim):
				if (i*lpm+k) < countLines:
					tosendtext += "ID:" + str(lista_utenti[i*lpm+k].id_utente) + ", <b>@" + lista_utenti[i*lpm+k].username + "</b>, Messaggi: " + str(lista_utenti[i*lpm+k].messaggi) + ", Warn: " + str(lista_utenti[i*lpm+k].warn) + "\n" 
			bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
		return
	elif command[1] == "admin":
		lista_admin = utility.groupAdmins(group_id)
		tosendtext = "Amministratori:\n"
		for i in range(0, len(lista_admin)):
			tosendtext += "ID:" + str(lista_admin[i].id_utente) + ", <b>@" + lista_admin[i].username + "</b>, Messaggi: " + str(lista_admin[i].messaggi) + ", Ruolo: " + str(lista_admin[i].autorizzazione) + "\n" 
		bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode="HTML")
	elif command[1] == "bannati":
		lista_bannati = utility.groupBanned(group_id)
		countLines = len(lista_bannati)
		tosendtext = "Abbiamo " + str(countLines) + " bannati in lista:\n"
		bot.sendMessage(chat_id = chat_id, text = tosendtext)
		lpm = 50
		#line per message
		countMessages = int(countLines/lpm)
		if countLines % lpm != 0:
			countMessages = countMessages + 1
		for i in range(0, countMessages):		
			tosendtext = ""
			#Calcolo il massimo di righe da mettere nel messaggio che segue, se è minore del massimo per messaggio lo mette com massimo del ciclo
			maxim = lpm
			cap = countLines - i*lpm
			if cap < maxim:
				maxim = cap
			for k in range(0, maxim):
				if (i*lpm+k) < countLines:
					tosendtext += "ID:" + str(lista_bannati[i*lpm+k].id_utente) + ", <b>@" + lista_bannati[i*lpm+k].username + "</b>, Messaggi: " + str(lista_bannati[i*lpm+k].messaggi) + ", Ban: " + str(lista_bannati[i*lpm+k].ban) + "\n"
			bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode="HTML")

def getuser(bot, update):
	mess = str(update.message)
	if mess == "None":
		return
	chat_id = update.message.chat_id
	id_utente = update.message.from_user.id
	nome = update.message.from_user.first_name
	nome = nome[:30]
	username = str(update.message.from_user.username)
	if len(username) < 5:
		username = "None"
	if str(chat_id) == chat_dedicata:	
		if utility.userPresence(id_utente):
			utente = utility.getUtente(id_utente)
			if username != utente.username:
				utility.changeUsername(id_utente, username)
			if nome != utente.nome:
				utility.changeName(id_utente, nome)
			try:
				command = update.message.text.split()
				if command[0] == "!admin":
					admin = utility.adminList()
					tosendtext = "Admin:"
					for i in range(0, len(admin)):
						tosendtext += "\n@" + admin[i].username
					bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext)
				elif command[0] == "!codici":
					mostraCodici(bot, update)
				elif command[0][0] == "!":
					comandiPersonalizzati(bot, update)
			except:
				pass
		else:
			utility.addUser(id_utente, username, nome)
			if molestachat != "no":
				tosendtext = "<b>Ciao " + nome + "!</b>"
				tosendtext += "\nInvia a " + botusername + " lo screen del tuo personaggio con nickname, livello e colore del team visibili!"
				if username == "None":
					tosendtext += "\nInoltre, poiché non hai un username telegram, sarebbe comodo che tu ne mettessi uno"
				bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
	elif chat_id > 0:
		if utility.userPresence(id_utente):
			try:
				command = update.message.text.split()
				if command[0] == "!codici":
					mostraCodici(bot, update)
				elif command[0][0] == "!":
					comandiPersonalizzati(bot, update)
			except:
				pass
			utente = utility.getUtente(id_utente)
			if username != utente.username:
				utility.changeUsername(id_utente, username)
			if nome != utente.nome:
				utility.changeName(id_utente, nome)
			if str(update.message.location) != "None":
				utility.updateLocation(id_utente, update.message.location)
			#tesseract(bot, update)
			try:
				screen = update.message.photo[-1].file_id
				cur.execute("update utenti set screen = (%(screen)s) where id_utente = (%(id_utente)s)", {'screen':screen, 'id_utente':id_utente})
				conn.commit()
				bot.sendPhoto(chat_id = update.message.chat_id, photo = screen)
				bot.sendMessage(chat_id = update.message.chat_id, text = "Screen impostato correttamente")
				if molestachat != "no":
					bot.sendMessage(chat_id = 119444006, text = nome + " (" + str(id_utente) + ") ha mandato un'immagine nel bot!")
			except:
				pass

def gym(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	chat_id = update.message.chat_id
	param = parametri(update.message.text)
	if len(param) > 0:
		id_palestre = riconosciPalestra(param[0])
	else:
		id_palestre = []
	limitekm = limitedistanza
	if len(command) > 1:
		limitekm *= 2
	if len(id_palestre) == 0:
		palestre = utility.listaPalestre()
		paldis = palestreVicine(update, palestre, limitekm)
		tosendtext = "Palestre fino a " + str(limitekm) + "km (" + str(len(paldis)) + "):"
		numMess = round((len(paldis)-(len(paldis)%50))/50)+1
		for i in range(0, numMess):
			for j in range(50*i, min(len(paldis),50*(i+1))):
				tosendtext += "\n- " + paldis[50*i+j][0].nome + " (#" + str(paldis[50*i+j][0].id_palestra) + ", " + str(paldis[50*i+j][1]) + "km)"
			bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
			tosendtext = ""
	elif len(id_palestre) == 1:
		id_palestra = id_palestre[0]
		palestra = utility.getpalestra(id_palestra)
		tosendtext = "Palestra trovata (#" + str(id_palestra) + "):\n" + palestra.nome
		tosendtext += "\n<code>" + str(palestra.latitudine) + ", " + str(palestra.longitudine) + "</code>"
		bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
		if mappa:
			bot.sendLocation(chat_id = chat_id, longitude = palestra.longitudine, latitude = palestra.latitudine)
	else:
		palestre = []
		for i in range(0, len(id_palestre)):
			palestre.append(utility.getpalestra(id_palestre[i]))
		paldis = palestreVicine(update, palestre, limitekm)
		tosendtext = "Palestre fino a " + str(limitekm) + "km (" + str(len(paldis)) + "):"
		numMess = round((len(paldis)-(len(paldis)%50))/50)+1
		for i in range(0, numMess):
			for j in range(50*i, min(len(paldis),50*(i+1))):
				tosendtext += "\n- " + paldis[50*i+j][0].nome + " (#" + str(paldis[50*i+j][0].id_palestra) + ", " + str(paldis[50*i+j][1]) + "km)"
			bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
			tosendtext = ""

def info(bot, update):
	getuser(bot, update)
	command = update.message.text.split()
	if len(command) > 1:
		username = "None"
		id_utente = 0
		id_utente, username = utility.checkUser(bot, update, id_utente, username)
		if id_utente == 0:
			return
	else:
		id_utente = update.message.from_user.id
		username = update.message.from_user.username
	utente = utility.getUtente(id_utente)
	username = utente.username
	if username != "None":
		username = "@" + username
	text = "<i>" + utente.nome + "</i>"
	text += "\n<b>Username</b>: " + username + "\n<b>ID</b>: " + str(utente.id_utente) + "\n<b>Nickname in gioco</b>: " + utente.nickname + " (L" + str(utente.livello) + ")\n<b>Team</b>: " + utente.team
	if utente.team == "giallo":
		text += " 🟡"
	elif utente.team == "rosso":
		text += " 🔴"
	elif utente.team == "blu":
		text += " 🔵"
	else:
		text += " 🥐"
	#"\n<b>Legit</b>: " 
	#if utente.legit:
	#	text += "Sì"
	#else:
	#	text += "No"
	if utente.codice_amico != "0":
		text += "\n<b>Codice amico</b>: <code>" + str(utente.codice_amico) + "</code>"
	text += "\n<b>Stato</b>: " + utente.stato
	if utente.screen != "Nessuno" and update.message.chat_id > 0:
		bot.sendPhoto(chat_id = update.message.chat_id, photo = utente.screen)
	bot.sendMessage(chat_id = update.message.chat_id, text = text, parse_mode = "HTML")
	if utente.multi != "Nessuno":
		bot.sendMessage(chat_id = update.message.chat_id, text = "Multi: " + utente.multi, parse_mode = "HTML")

def inlineraid(bot, update):
	queryText = update.inline_query.query
	if len(queryText.split()) == 0:
		return
	id_utente = update.inline_query.from_user.id
	if not authorized.admin(id_utente):
		return
	id_raid = queryText.split()[0]
	try:
		id_raid = int(id_raid)
	except:
		return
	raid = utility.getraid(id_raid)
	results = []
	keyboard = []
	if raid.id_raid == -1:
		resultText = "Raid non trovato"
		results.append(InlineQueryResultArticle(id = uuid4(), title = "Non trovato", input_message_content = InputTextMessageContent(resultText)))
	else:	
		resultText = testoRaid(raid)
		keyboard.append([InlineKeyboardButton("Presente", callback_data = "raid " + str(id_raid) + " present"),InlineKeyboardButton("Invitami", callback_data = "raid " + str(id_raid) + " invited")])
		if flyflag:
			keyboard.append([InlineKeyboardButton("Remoto", callback_data = "raid " + str(id_raid) + " fly"),InlineKeyboardButton("Toglimi", callback_data = "raid " + str(id_raid) + " remove")])
		else:
			keyboard.append([InlineKeyboardButton("Toglimi", callback_data = "raid " + str(id_raid) + " remove")])
		if not raid.ora_confermata:
			keyboard.append([InlineKeyboardButton("Pass Ex?", callback_data = "raid " + str(id_raid) + " passex"),InlineKeyboardButton("Cancella raid", callback_data = "raid " + str(id_raid) + " delete")])
		else: #fixato
			keyboard.append([InlineKeyboardButton("🟡", callback_data = "raid " + str(id_raid) + " team giallo"), InlineKeyboardButton("🔴", callback_data = "raid " + str(id_raid) + " team rosso"), InlineKeyboardButton("🔵", callback_data = "raid " + str(id_raid) + " team blu")])
		reply_markup= InlineKeyboardMarkup(keyboard)
		results.append(InlineQueryResultArticle(id = uuid4(), title = "Invia: " + raid.pokemon, input_message_content = InputTextMessageContent(resultText, parse_mode = "HTML"), reply_markup = reply_markup))	
		
	update.inline_query.answer(results, cache_time = 2)

def legit(bot, update):
	if update.message.chat_id < 0:
		return
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	utente = utility.getUtente(update.message.from_user.id)
	if utente.legit:
		legit = False
	else:
		legit = True
	if legit:
		tosendtext = "Hai impostato legit! Per impostare fly rimanda questo comando."
	else:
		tosendtext = "Hai impostato fly! Per impostare legit rimanda questo comando."
	cur.execute("update utenti set legit = (%(legit)s) where id_utente = (%(id_utente)s)", {'legit':legit, 'id_utente':utente.id_utente})
	conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def livello(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	livello = 1
	utente = utility.getUtente(update.message.from_user.id)
	if str(reply) == "None":
		if len(command) > 1:
			try:
				livello = int(command[1])
				if livello > 50 or livello < 1:
					tosendtext = "Il livello può andare solo da 1 a 50."
					livello = 1
			except:
				tosendtext = "Rispondi ad un messaggio preinviato o manda il messaggio come:\n/livello 30"
		else:
			tosendtext = "Rispondi ad un messaggio preinviato o manda il messaggio come:\n/livello 30"
	else:
		testo = reply.text.split()
		try:
			livello = int(testo[0])	
			if livello > 50 or livello < 1:
				tosendtext = "Il livello può andare solo da 1 a 50."
				livello = 1	
		except:
			tosendtext = "Manda un valore numerico"
	if livello != 1:
		if len(command) > 2 and authorized.admin(utente.id_utente):
			id_target = utility.gettarget(command[2])
			if id_target == 0:
				return
			cur.execute("update utenti set livello = (%(livello)s) where id_utente = (%(id_utente)s)", {'livello':livello, 'id_utente':id_target})
		else:
			cur.execute("update utenti set livello = (%(livello)s) where id_utente = (%(id_utente)s)", {'livello':livello, 'id_utente':utente.id_utente})
		tosendtext = "Livello impostato correttamente: <b>" + str(livello) + "</b>"
		conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def mostraCodici(bot, update):
	cur.execute("select nome, codice_amico, nickname, username from utenti where codice_amico != 'None'")
	found = cur.fetchall()
	tosendtext = "<b>CODICI AMICO</b>"
	for i in range(0, len(found)):
		tosendtext += "\n" + found[i][0]
		if found[i][2] != "Nessuno":
			tosendtext += " (" + found[i][2] + ")"
		elif found[i][3] != "None":
			tosendtext += " (" + found[i][3] + ")"
		tosendtext += " <code>"  + found[i][1] + "</code>"
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def multi(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	if str(reply) == "None":
		tosendtext = "Rispondi ad un messaggio preinviato."
	else:
		testo = reply.text
		utente = utility.getUtente(update.message.from_user.id)
		if not utility.inputSanification(testo):
			return
		cur.execute("update utenti set multi = (%(multi)s) where id_utente = (%(id_utente)s)", {'multi':testo, 'id_utente':utente.id_utente})
		tosendtext = "Messaggio impostato correttamente: <b>" + testo + "</b>"
		conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def nickname(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	testo = "None"
	if str(reply) == "None":
		if len(command) > 1:
			testo = command[1]
		else:
			tosendtext = "Rispondi ad un messaggio preinviato o manda il messaggio come:\n/nickname Player"
	else:
		testo = reply.text
	if testo != "None":
		utente = utility.getUtente(update.message.from_user.id)
		if not utility.inputSanification(testo):
			return
		if len(testo) > 20:
			tosendtext = "Nickname troppo lungo."
		else:
			if len(command) > 2 and authorized.admin(update.message.from_user.id):
				id_target = utility.gettarget(command[2])
				if id_target == 0:
					return
				cur.execute("update utenti set nickname = (%(testo)s) where id_utente = (%(id_utente)s)", {'testo':testo, 'id_utente':id_target})
			else:
				cur.execute("update utenti set nickname = (%(testo)s) where id_utente = (%(id_utente)s)", {'testo':testo, 'id_utente':utente.id_utente})
			tosendtext = "Nickname impostato correttamente: <b>" + testo + "</b>"
			conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def palestreVicine(update, palestre, limitekm):
	distanze = []
	utente = utility.getUtente(update.message.from_user.id)
	for i in range(0, len(palestre)):
		dist = utility.distanza(utente.posizione, palestre[i])
		dist = round(dist*100)
		dist = dist/100
		distanze.append(dist)
	paldis = []
	for i in range(0, len(palestre)):
		if distanze[i] <= limitekm or limitekm == 0:
			paldis.append([palestre[i],distanze[i]])
	paldis = sorted(paldis, key=lambda pd: pd[1])
	return paldis

def parametri(text):
	command = text.split()
	inizio = len(command[0])+1
	parametri = []
	parametro = ""
	#Divide i parametri sfruttando i due punti
	for i in range(inizio, len(text)):
		if text[i] != ":":
			#if not (parametro == "" and text[i] == " "):
			parametro = parametro + text[i]
		else:
			simbolo = False
			rimossi = 0
			for j in range(0, len(parametro)):
				if parametro[j] != " ":
					simbolo = True
				if parametro[j] == " " and (not simbolo):
					rimossi += 1
			parametri.append(parametro[rimossi:])
			parametro = ""
	if len(parametro) > 0:
		simbolo = False
		rimossi = 0
		for j in range(0, len(parametro)):
			if parametro[j] != " ":
				simbolo = True
			if parametro[j] == " " and (not simbolo):
				rimossi += 1
		parametri.append(parametro[rimossi:])
	#parametri_completi = []
	#Ridefinisco un array con coppie di parametro e numero
	#parametro = ""
	#for i in range(0, len(parametri)):
	#	numero = 1
	#	if ":" in parametri[i]:
	#		numeroTrovato = False
	#		for j in range(0, len(parametri[i])):
	#			if not numeroTrovato:
	#				if parametri[i][j] != ":":
	#					parametro = parametro + parametri[i][j]
	#				else:
	#					parametri.append(parametro)
	#					try:
	#						numero = int(parametri[i][j+1:])
	#						if numero < 1:
	#							numero = 1
	#					except:
	#						numero = 1
	#					numeroTrovato = True
	#		parametri_completi.append([parametro, numero])
	#	else:	
	#		parametri_completi.append([parametri[i], numero])
	#	parametro = ""
	return parametri

def raid(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	chat_id = update.message.chat_id
	id_utente = update.message.from_user.id
	#if str(chat_id) != chat_dedicata:
	if raidperm == "verified":
		if not authorized.verified(id_utente):
			return
	elif raidperm == "admin":
		if not authorized.admin(id_utente):
			return
	param = parametri(update.message.text)
	pokem = "None"
	orarioinizio = "."
	orariofine = "."
	if len(param) > 0:
		id_palestra = riconosciPalestra(param[0]) #command
		if len(id_palestra) > 0:
			id_palestra = id_palestra[0]
		else:
			id_palestra = 0
		if len(param) > 1:
			pokem = False
			try:
				num = int(param[1][0])
			except:
				pokem = True
			if pokem:
				pokem = param[1]
				index = 2
			else:
				index = 1
			if len(param) > index:
				orarioinizio = param[index]
				if len(param) > index+1:
					orariofine = param[index+1]
	else:
		id_palestra = 0	
	id_raid = utility.newraidid()
	if len(orarioinizio) > 1:
		orarioinizio = orarioinizio.replace("."," ")
		orarioinizio = orarioinizio.split()
		if len(orarioinizio) == 2:
			try:
				num = int(orarioinizio[0])
				num = int(orarioinizio[1])
				orarioinizio = [int(orarioinizio[0]),num]
			except:
				orarioinizio = "."
			if len(orarioinizio) > 1 and len(orariofine) > 1:
				orariofine = orariofine.replace("."," ")
				orariofine = orariofine.split()
				if len(orariofine) == 2:
					try:
						num = int(orariofine[0])
						num = int(orariofine[1])
						orariofine = [int(orariofine[0]),num]
					except:
						orariofine = "."
		else:
			orarioinizio = "."
	if len(orarioinizio) == 1:
		bot.sendMessage(chat_id = chat_id, text = "/raid palestra:pokemon:orarioinizio\nEs:\n/raid Queen:Charizard:18.32")
		return
	if len(orariofine) == 1:
		orariofine = utility.oraTermine(orarioinizio)
	tosendtext = ""
	keyboard = []
	for i in range(1, len(command)):
		tosendtext += " " + command[i]
	#keyboard.append([InlineKeyboardButton("Ci sono!", callback_data = "raid " + str(id_raid) + " join"),InlineKeyboardButton("Toglimi", callback_data = "raid " + str(id_raid) + " remove")],[InlineKeyboardButton("Pass Ex?", callback_data = "raid " + str(id_raid) + " passex"),InlineKeyboardButton("Cancella raid", callback_data = "raid " + str(id_raid) + " delete")])
	#keyboard.append([InlineKeyboardButton("1", callback_data = "raid " + str(id_raid) + " livello 1"),InlineKeyboardButton("2", callback_data = "raid " + str(id_raid) + " livello 2"),InlineKeyboardButton("3", callback_data = "raid " + str(id_raid) + " livello 3"),InlineKeyboardButton("4", callback_data = "raid " + str(id_raid) + " livello 4"),InlineKeyboardButton("5", callback_data = "raid " + str(id_raid) + " livello 5")])
	keyboard.append([InlineKeyboardButton("1", callback_data = "raid " + str(id_raid) + " livello 1"),InlineKeyboardButton("3", callback_data = "raid " + str(id_raid) + " livello 3"),InlineKeyboardButton("5", callback_data = "raid " + str(id_raid) + " livello 5"),InlineKeyboardButton("Mega", callback_data = "raid " + str(id_raid) + " livello 6")])
	RM = InlineKeyboardMarkup(keyboard)
	if id_palestra != 0 and chat_id < 0:
		palestra = utility.getpalestra(id_palestra)
		if mappa:
			bot.sendLocation(chat_id = chat_id, longitude = palestra.longitudine, latitude = palestra.latitudine)
	if pokem == "None":
		cur.execute("insert into raid (id_raid, id_creatore, informazioni, id_palestra, ora_termine, ora_inizio) values ((%(id_raid)s),(%(id_utente)s), (%(info)s), (%(id_palestra)s), (%(orat)s), (%(orai)s))", {'id_raid':id_raid, 'id_utente':id_utente, 'info':tosendtext, 'id_palestra':id_palestra, 'poke':pokem, 'orat':orariofine, 'orai':orarioinizio})
	else:
		cur.execute("insert into raid (id_raid, id_creatore, informazioni, id_palestra, pokemon, ora_termine, ora_inizio) values ((%(id_raid)s),(%(id_utente)s), (%(info)s), (%(id_palestra)s), (%(poke)s), (%(orat)s), (%(orai)s))", {'id_raid':id_raid, 'id_utente':id_utente, 'info':tosendtext, 'id_palestra':id_palestra, 'poke':pokem, 'orat':orariofine, 'orai':orarioinizio})
	conn.commit()
	tosendtext = "Per prima cosa, scegli il livello del raid!"
	bot.sendMessage(chat_id = chat_id, text = tosendtext, reply_markup=RM)

def raidbutton(bot, query):
	data = query.data.split()
	id_raid = int(data[1])
	raid = utility.getraid(id_raid)
	id_utente = query.from_user.id
	utente = utility.getUtente(id_utente)
	#if not authorized.verified(id_utente):
	#	return
	nome = query.from_user.first_name
	nome = nome[:30]
	username = str(query.from_user.username)
	if len(username) < 5:
		username = "None"
	if utility.userPresence(id_utente):
		if username != utente.username:
			utility.changeUsername(id_utente, username)
		if nome != utente.nome:
			utility.changeName(id_utente, nome)
	else:
		utility.addUser(id_utente, username, nome)
		utente = utility.getUtente(id_utente)
	azione = data[2]
	presente = False
	edit = True
	if id_utente in raid.presenti or id_utente in raid.invitati or id_utente in raid.fly:
		presente = True
	#for i in range(0, len(raid.presenti)):
	#	if raid.presenti[i] == id_utente:
	#		presente = True
	keyboard = []
	keyboard.append([InlineKeyboardButton("Presente", callback_data = "raid " + str(id_raid) + " present"),InlineKeyboardButton("Invitami", callback_data = "raid " + str(id_raid) + " invited")])
	if flyflag:
		keyboard.append([InlineKeyboardButton("Remoto", callback_data = "raid " + str(id_raid) + " fly"),InlineKeyboardButton("Toglimi", callback_data = "raid " + str(id_raid) + " remove")])
	else:
		keyboard.append([InlineKeyboardButton("Toglimi", callback_data = "raid " + str(id_raid) + " remove")])	
	if azione == "present" or azione == "invited" or azione == "fly":
		if presente:
			aggiunto = False
			if azione == "present":
				for i in range(0, len(raid.presenti)):
					if raid.presenti[i] == id_utente:
						aggiunto = True
						raid.numero_presenze[i] += 1
				if not aggiunto:
					raid.presenti.append(id_utente)
					raid.numero_presenze.append(1)
			if azione == "invited":
				for i in range(0, len(raid.invitati)):
					if raid.invitati[i] == id_utente:
						aggiunto = True
						raid.numero_invitati[i] += 1
				if not aggiunto:
					raid.invitati.append(id_utente)
					raid.numero_invitati.append(1)
			if azione == "fly":
				for i in range(0, len(raid.fly)):
					if raid.fly[i] == id_utente:
						aggiunto = True
						raid.numero_fly[i] += 1
				if not aggiunto:
					raid.fly.append(id_utente)
					raid.numero_fly.append(1)
			cur.execute("update raid set presenti = (%(pres)s), remoti = (%(remo)s), fly = (%(fly)s), numero_presenze = (%(numero_presenze)s), numero_invitati = (%(numero_invitati)s), numero_fly = (%(numero_fly)s) where id_raid = (%(id_raid)s)", {'pres':raid.presenti, 'remo':raid.invitati, 'fly':raid.fly, 'numero_presenze':raid.numero_presenze, 'numero_invitati':raid.numero_invitati, 'numero_fly':raid.numero_fly, 'id_raid':id_raid})
			conn.commit()
		else:
			if azione == "present": 
				raid.presenti.append(id_utente)
				raid.numero_presenze.append(1)
			if azione == "invited": 
				raid.invitati.append(id_utente)
				raid.numero_invitati.append(1)
			if azione == "fly": 
				raid.fly.append(id_utente)
				raid.numero_fly.append(1)
			if id_utente in raid.rimossi:
				temprim = []
				for i in range(0, len(raid.rimossi)):
					if not raid.rimossi[i] == id_utente:
						temprim.append(raid.rimossi[i])
				raid.rimossi = temprim
			cur.execute("update raid set presenti = (%(pres)s), remoti = (%(remo)s), fly = (%(fly)s), numero_presenze = (%(numero_presenze)s), numero_invitati = (%(numero_invitati)s), numero_fly = (%(numero_fly)s), rimossi = (%(rim)s) where id_raid = (%(id_raid)s)", {'pres':raid.presenti, 'remo':raid.invitati, 'fly':raid.fly, 'numero_presenze':raid.numero_presenze, 'numero_invitati':raid.numero_invitati, 'numero_fly':raid.numero_fly, 'rim':raid.rimossi, 'id_raid':id_raid})
			conn.commit()	
	elif azione == "remove":
		if not presente:
			return
		else:
			if not id_utente in raid.rimossi:
				raid.rimossi.append(id_utente)
			listapresenti = []
			listanumeropresenze = []
			for i in range(0, len(raid.presenti)):
				if raid.presenti[i] != id_utente:
					listapresenti.append(raid.presenti[i])
					listanumeropresenze.append(raid.numero_presenze[i])
			raid.presenti = listapresenti
			raid.numero_presenze = listanumeropresenze
			listainvitati = []
			listanumeroinvitati = []
			for i in range(0, len(raid.invitati)):
				if raid.invitati[i] != id_utente:
					listainvitati.append(raid.invitati[i])
					listanumeroinvitati.append(raid.numero_invitati[i])
			raid.invitati = listainvitati
			raid.numero_invitati = listanumeroinvitati
			listafly = []
			listanumerofly = []
			for i in range(0, len(raid.fly)):
				if raid.fly[i] != id_utente:
					listafly.append(raid.fly[i])
					listanumerofly.append(raid.numero_fly[i])
			raid.fly = listafly
			raid.numero_fly = listanumerofly
			cur.execute("update raid set presenti = (%(pres)s), remoti = (%(remo)s), fly = (%(fly)s), numero_presenze = (%(numero_presenze)s), numero_invitati = (%(numero_invitati)s), numero_fly = (%(numero_fly)s), rimossi = (%(rim)s) where id_raid = (%(id_raid)s)", {'pres':raid.presenti, 'remo':raid.invitati, 'fly':raid.fly, 'numero_presenze':raid.numero_presenze, 'numero_invitati':raid.numero_invitati, 'numero_fly':raid.numero_fly, 'rim':raid.rimossi, 'id_raid':id_raid})
			conn.commit()		
	elif azione == "passex":
		if authorized.admin(id_utente) or id_utente == raid.id_creatore:
			if raid.passex:
				raid.passex = False
			else:
				raid.passex = True
			cur.execute("update raid set passex = (%(passex)s) where id_raid = (%(id_raid)s)", {'passex':raid.passex, 'id_raid':id_raid})
			conn.commit()
		else:
			return
	elif azione == "delete":
		if authorized.admin(id_utente) or id_utente == raid.id_creatore:
			raid.informazioni = "<b>CHIUSO</b>\n" + raid.informazioni	
			raid.stato = "Chiuso"
			cur.execute("update raid set stato = 'Chiuso' where id_raid = (%(id_raid)s)", {'id_raid':id_raid})
			conn.commit()
			keyboard = []
		else:
			return
	elif azione == "livello":
		if authorized.admin(id_utente) or id_utente == raid.id_creatore:
			raid.livello = int(data[3])
			cur.execute("update raid set livello = (%(livello)s) where id_raid = (%(id_raid)s)", {'livello':raid.livello, 'id_raid':id_raid})
			#Inserisco l'ora attuale
			#ora = int(time.strftime("%-H"))+3
			#minuto = int(time.strftime("%-M"))
			#raid.ora_termine = [ora,minuto]
			#cur.execute("update raid set ora_termine = (%(ora_termine)s) where id_raid = (%(id_raid)s)", {'ora_termine':raid.ora_termine, 'id_raid':id_raid})
			#conn.commit()
	elif azione == "pokemon":
		if authorized.admin(id_utente) or id_utente == raid.id_creatore:
			raid.pokemon = data[3]
			cur.execute("update raid set pokemon = (%(pokemon)s) where id_raid = (%(id_raid)s)", {'pokemon':raid.pokemon, 'id_raid':id_raid})
			conn.commit()
	#elif azione == "ora":
	#	sottoazione = data[3]
	#	if sottoazione == "ora":
	#		raid.ora_termine[0] += int(data[4])
	#		if raid.ora_termine[0] < 0:
	#			raid.ora_termine[0] += 24
	#		elif raid.ora_termine[0] > 23:
	#			raid.ora_termine[0] -= 24
	#		cur.execute("update raid set ora_termine[1] = (%(ora)s)", {'ora':raid.ora_termine[0]})
	#	elif sottoazione == "minuto":
	#		raid.ora_termine[1] += int(data[4])
	#		if raid.ora_termine[1] < 0:
	#			raid.ora_termine[0] -= 1
	#			if raid.ora_termine[0] < 0:
	#				raid.ora_termine[0] += 24
	#			raid.ora_termine[1] += 60
	#		elif raid.ora_termine[1] > 59:
	#			raid.ora_termine[0] += 1
	#			if raid.ora_termine[0] > 23:
	#				raid.ora_termine[0] -= 24
	#			raid.ora_termine[1] -= 60
	#		cur.execute("update raid set ora_termine[1] = (%(ora)s)", {'ora':raid.ora_termine[0]})
	#		cur.execute("update raid set ora_termine[2] = (%(ora)s)", {'ora':raid.ora_termine[1]})
	elif azione == "ora":	
		if authorized.admin(id_utente) or id_utente == raid.id_creatore:
			sottoazione = data[3]
			if sottoazione == "conferma":
				raid.ora_confermata = True
				cur.execute("update raid set ora_confermata = (%(ora)s)", {'ora':raid.ora_confermata})	
				conn.commit()
		else:
			return
	elif azione == "team":
		team = data[3]
		cur.execute("update utenti set team = (%(team)s) where id_utente = (%(id_utente)s)", {'team':team, 'id_utente':id_utente})
		conn.commit()
	elif azione == "rimossi":
		edit = False
		if not authorized.admin(id_utente):
			return
		if len(raid.rimossi) > 0:
			tosendtext = "I seguenti si sono segnati e rimossi dal raid:"
			for i in range(0, len(raid.rimossi)):
				tosendtext += "\n(" + str(raid.rimossi[i]) + ")"
				utente = utility.getUtente(raid.rimossi[i])
				if utente.nickname != "Nessuno":
					tosendtext += ", " + utente.nickname 
				if utente.username != "None":
					tosendtext += ", @" + utente.username
				if utente.nome != "Nessuno":
					tosendtext += ", " + utente.nome
		else:
			tosendtext = "Nessuno si è rimosso dal raid!"
	if raid.livello == 0 and raid.stato != "Chiuso":
		keyboard.append([InlineKeyboardButton("1", callback_data = "raid " + str(id_raid) + " livello 1"),InlineKeyboardButton("2", callback_data = "raid " + str(id_raid) + " livello 2"),InlineKeyboardButton("3", callback_data = "raid " + str(id_raid) + " livello 3"),InlineKeyboardButton("4", callback_data = "raid " + str(id_raid) + " livello 4"),InlineKeyboardButton("5", callback_data = "raid " + str(id_raid) + " livello 5")])
	if raid.livello > 0 and raid.pokemon == "Nessuno" and raid.stato != "Chiuso":
		listapokemon = utility.arrayRaid(raid.livello)
		righe = int((len(listapokemon) - 1)/4)+1
		for j in range(0, righe):
			listapulsanti = []
			for i in range(j*4, min(len(listapokemon),(j+1)*4)):
				listapulsanti.append(InlineKeyboardButton(listapokemon[i], callback_data = "raid " + str(id_raid) + " pokemon " + listapokemon[i]))
			keyboard.append(listapulsanti)
	if not raid.ora_confermata:
		keyboard.append([InlineKeyboardButton("Pass Ex?", callback_data = "raid " + str(id_raid) + " passex"),InlineKeyboardButton("Cancella raid", callback_data = "raid " + str(id_raid) + " delete")])
	else:
		keyboard.append([InlineKeyboardButton("🟡", callback_data = "raid " + str(id_raid) + " team giallo"), InlineKeyboardButton("🔴", callback_data = "raid " + str(id_raid) + " team rosso"), InlineKeyboardButton("🔵", callback_data = "raid " + str(id_raid) + " team blu")])
		if tastorimossi:
			keyboard.append([InlineKeyboardButton("Chi si è tolto?", callback_data = "raid " + str(id_raid) + " rimossi")])	
	if raid.livello > 0 and (not raid.ora_confermata) and raid.stato != "Chiuso":
		#keyboard.append([InlineKeyboardButton("-1 ora", callback_data = "raid " + str(id_raid) + " ora ora -1"),InlineKeyboardButton("+1 ora", callback_data = "raid " + str(id_raid) + " ora ora 1")])
		#keyboard.append([InlineKeyboardButton("-10 min", callback_data = "raid " + str(id_raid) + " ora minuto -10"),InlineKeyboardButton("-5 min", callback_data = "raid " + str(id_raid) + " ora minuto -5"),InlineKeyboardButton("-1 min", callback_data = "raid " + str(id_raid) + " ora minuto -1"),InlineKeyboardButton("+1 min", callback_data = "raid " + str(id_raid) + " ora minuto 1"),InlineKeyboardButton("+5 min", callback_data = "raid " + str(id_raid) + " ora minuto 5"),InlineKeyboardButton("+10 min", callback_data = "raid " + str(id_raid) + " ora minuto 10")])
		keyboard.append([InlineKeyboardButton("Conferma Raid", callback_data = "raid " + str(id_raid) + " ora conferma")])
	if azione != "rimossi":
		tosendtext = testoRaid(raid)
	if raid.stato == "Chiuso":
		keyboard = []
	reply_markup= InlineKeyboardMarkup(keyboard)
	if azione == "ora":
		sottoazione = data[3]
		if sottoazione == "conferma" and str(query.message.chat_id) != chat_dedicata:
			edit = False
	if edit:
		try:
			bot.edit_message_text(text = tosendtext, chat_id = query.message.chat_id, message_id = query.message.message_id, parse_mode = "HTML", reply_markup = reply_markup)
		except:
			bot.edit_message_text(text = tosendtext, inline_message_id = query.inline_message_id, parse_mode = "HTML", reply_markup = reply_markup)
	elif azione == "ora":
		bot.edit_message_text(text = "Raid inoltrato nel gruppo!", chat_id = query.message.chat_id, message_id = query.message.message_id, parse_mode = "HTML")
		bot.sendMessage(chat_id = int(chat_dedicata), text = tosendtext, parse_mode = "HTML", reply_markup = reply_markup)
		if raid.id_palestra != 0 and mappa:
			palestra = utility.getpalestra(raid.id_palestra)
			bot.sendLocation(chat_id = int(chat_dedicata), longitude = palestra.longitudine, latitude = palestra.latitudine)
	elif azione == "rimossi":
		try:
			bot.sendMessage(chat_id = id_utente, text = tosendtext)
		except:
			pass

def screen(bot, update):
	getuser(bot, update)
	if update.message.chat_id < 0:
		return
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	if str(reply) == "None":
		tosendtext = "Rispondi ad una foto preinviata."
	else:
		try:
			screen = reply.photo[-1].file_id
			utente = utility.getUtente(update.message.from_user.id)
			cur.execute("update utenti set screen = (%(screen)s) where id_utente = (%(id_utente)s)", {'screen':screen, 'id_utente':id_utente})
			tosendtext = "Screen impostato correttamente"
			conn.commit()
			bot.sendPhoto(chat_id = update.message.chat_id, photo = screen)
		except:
			tosendtext = "Non è una foto"
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def team(bot, update):
	getuser(bot, update)
	if not utility.inputSanification(update.message.text):
		return
	if authorized.banned(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	testo = "Nessuno"
	if str(reply) == "None":
		if len(command) > 1:
			testo = command[1]
		else:
			tosendtext = "Rispondi ad un messaggio preinviato o manda il comando come:\n/team blu"
	else:
		testo = reply.text
	if not utility.inputSanification(testo):
		return
	team = testo.lower()
	if not (team == "giallo" or team == "rosso" or team == "blu"):
		tosendtext = "Errore, i team permessi sono: rosso/giallo/blu"
	else:
		if len(command) > 2 and authorized.admin(update.message.from_user.id):
			id_target = utility.gettarget(command[2])
			if id_target == 0:
				return
			cur.execute("update utenti set team = (%(team)s) where id_utente = (%(id_utente)s)", {'team':team, 'id_utente':id_target})
		else:
			cur.execute("update utenti set team = (%(team)s) where id_utente = (%(id_utente)s)", {'team':team, 'id_utente':update.message.from_user.id})
		tosendtext = "Team impostato correttamente: <b>" + team + "</b>"
		conn.commit()
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def riconosciPalestra(parametro):
	#if len(command) == 1:
	#	return []
	if parametro[0] == "#": #command[1][0]
		try:
			id_palestra = int(parametro[1:])
			return [id_palestra]
		except:
			return []
	palestre = []
	command = parametro.split()
	cur.execute("select id_palestra,nome from palestre where lower(nome) like (%(parola)s)", {'parola':'%'+command[0].lower()+'%'})
	found = cur.fetchall()
	for i in range(0, len(found)):
		palestre.append(found[i])
	if len(command) > 1: #2
		if len(palestre) == 1:
			return [found[0][0]]
		#if command[2][0] == "#":
		#	try:
		#		id_palestra = int(command[2][1:])
		#		return [id_palestra]
		#	except:
		#		return [0]
		for i in range(1, len(command)): #2
			precedenti = []
			nuove = []
			for j in range(0, len(palestre)):
				precedenti.append(palestre[j][0])
				if command[i].lower() in palestre[j][1].lower():
					nuove.append(palestre[j])
			palestre = nuove
			if len(palestre) == 1:
				return [palestre[0][0]]
			elif len(palestre) == 0:
				return precedenti
		nuove = []
		for i in range(0, len(palestre)):
			nuove.append(palestre[i][0])
		return nuove
	else:
		if len(palestre) == 1:
			return [found[0][0]]
		elif len(palestre) == 0:
			return []
		else:
			nuove = []
			for i in range(0, len(palestre)):
				nuove.append(palestre[i][0])
			return nuove

def tesseract(bot, update):
	photo = update.message.photo[-1]
	print("A")
	remote_file = bot.getFile(file_id=photo.file_id)
	print("B")
	name = "fotoprova"
	print("C")
	indirizzo = "elah900"
	print("D")
	remote_file.download(indirizzo)
	print("E")
	text =pytesseract.image_to_string(Image.open(indirizzo), config='-psm 7')
	print("F")
	print(len(text))

def testoRaid(raid):
	tosendtext = ""
	if raid.id_palestra != 0:
		palestra = utility.getpalestra(raid.id_palestra)
		tosendtext += "<b>" + palestra.nome + "</b>\n"
		tosendtext += "<code>" + str(palestra.latitudine) + ", " + str(palestra.longitudine) + "</code>\n"
	if raid.livello != 0:
		if raid.livello == 6:
			tosendtext += "\nRaid MEGA"
		else:
			tosendtext += "\nRaid livello " + str(raid.livello)
	if raid.pokemon != "Nessuno":
		tosendtext += ": <b>" + raid.pokemon + "</b>"
	if raid.passex:
		tosendtext += "\nQuesto raid potrebbe essere valido per un <b>PASS EX!</b>"
	tosendtext += "\n\n<b>Presenti</b>:"
	partecipanti = 0
	partparz = 0
	for i in range(0, len(raid.presenti)):
		utente = utility.getUtente(raid.presenti[i])
		if utente.nickname != "None":
			tosendtext += "\n" + utente.nickname + " (" + str(utente.livello)
		elif utente.username != "None":
			tosendtext += "\n" + utente.username + " (" + str(utente.livello)
		else:
			tosendtext += "\n" + utente.nome + " (" + str(utente.livello)
		if utente.team == "giallo":
			tosendtext += " 🟡"
		elif utente.team == "rosso":
			tosendtext += " 🔴"
		elif utente.team == "blu":
			tosendtext += " 🔵"
		else:
			tosendtext += " 🥐"
		tosendtext += ")"
		if raid.numero_presenze[i] > 1:
			tosendtext += " +" + str(raid.numero_presenze[i]-1) + " account"
		partecipanti += raid.numero_presenze[i]
		partparz += raid.numero_presenze[i]
	tosendtext += "\n<b>Presenti </b>" + str(partparz)
	partparz = 0
	tosendtext += "\n<b>Da Invitare </b>:"
	for i in range(0, len(raid.invitati)):
		utente = utility.getUtente(raid.invitati[i])
		if utente.nickname != "None":
			tosendtext += "\n" + utente.nickname + " (" + str(utente.livello)
		elif utente.username != "None":
			tosendtext += "\n" + utente.username + " (" + str(utente.livello)
		else:
			tosendtext += "\n" + utente.nome + " (" + str(utente.livello)
		if utente.team == "giallo":
			tosendtext += " 🟡"
		elif utente.team == "rosso":
			tosendtext += " 🔴"
		elif utente.team == "blu":
			tosendtext += " 🔵"
		else:
			tosendtext += " 🥐"
		tosendtext += ")"
		if raid.numero_invitati[i] > 1:
			tosendtext += " +" + str(raid.numero_invitati[i]-1) + " account"
		partecipanti += raid.numero_invitati[i]
		partparz += raid.numero_invitati[i]
	tosendtext += "\n<b>Da Invitare </b>" + str(partparz)
	partparz = 0
	if flyflag:
		tosendtext += "\n<b>Remoti</b>:"
		for i in range(0, len(raid.fly)):
			utente = utility.getUtente(raid.fly[i])
			if utente.nickname != "None":
				tosendtext += "\n" + utente.nickname + " (" + str(utente.livello)
			elif utente.username != "None":
				tosendtext += "\n" + utente.username + " (" + str(utente.livello)
			else:
				tosendtext += "\n" + utente.nome + " (" + str(utente.livello)
			if utente.team == "giallo":
				tosendtext += " 🟡"
			elif utente.team == "rosso":
				tosendtext += " 🔴"
			elif utente.team == "blu":
				tosendtext += " 🔵"
			else:
				tosendtext += " 🥐"
			tosendtext += ")"
			if raid.numero_fly[i] > 1:
				tosendtext += " +" + str(raid.numero_fly[i]-1) + " account"
			partecipanti += raid.numero_fly[i]
			partparz += raid.numero_fly[i]
		tosendtext += "\n<b>Remoti </b>" + str(partparz)
	tosendtext += "\n\n<b>Orario raid</b>: " + utility.orario(raid.ora_inizio) + " - " + utility.orario(raid.ora_termine)
	tosendtext += "\n<b>Partecipanti</b>: " + str(partecipanti)
	if not raid.ora_confermata:
		tosendtext += "\n\nRaid non confermato"
	tosendtext += "\n#" + str(raid.id_raid)
	#tosendtext += "\n" + raid.informazioni
	return tosendtext
