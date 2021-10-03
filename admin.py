#admin.py	SORGENTE COMANDI per ADMIN

import string, authorized, utility
from utility import cur, conn

def admin(bot, update):
	chat_id = update.message.chat_id
	if not authorized.owner(update.message.from_user.id):
		return
	command = update.message.text.split()
	if len(command) != 2:
		return
	target = command[1]
	if target == "@":
		target = target[1:]
	target_id = utility.findID(target)
	if target_id == 0:
		return
	if target_id == "None":
		bot.sendMessage(chat_id = chat_id, text = "Utente non registrato.")
		return
	targetutente = utility.getUtente(target_id)
	powerup = True
	if authorized.admin(target_id):
		powerup = False
		targetutente.stato = "verificato"
	else:
		targetutente.stato = "admin"
	utility.setStato(targetutente.id_utente, targetutente.stato)
	if powerup:
		tosendtext = update.message.from_user.username + ", hai reso @" + targetutente.username + " admin!"
	else:
		tosendtext = update.message.from_user.username + ", hai rimosso @" + targetutente.username + " dagli admin!"
	bot.sendMessage(chat_id=chat_id, text = tosendtext)

def ban(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	command = update.message.text.split()
	if update.message.chat_id < 0:
		return
	if len(command) == 1:
		mostraLista(bot, update, utility.verifyList())
	else:	
		username = "None"
		id_utente = 0
		id_utente, username = utility.checkUser(bot, update, id_utente, username)
		if id_utente == 0:
			return
		utente = utility.getUtente(id_utente)
		username = utente.username
		if username != "None":
			username = "@" + username
		tosendtext = "<b>" + utente.nickname + "</b> " + username + " segnato tra i bannati (questo non lo banna automaticamente dal gruppo)!"
		utility.setStato(id_utente, "bannato")
		bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def blu(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.teamList("blu"))

def giallo(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.teamList("giallo"))

def rosso(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.teamList("rosso"))

def Legit(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.legitList(True))

def fly(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.legitList(False))

def mancanti(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	mostraLista(bot, update, utility.missingList())

def verifica(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	command = update.message.text.split()
	if len(command) == 1:
		mostraLista(bot, update, utility.verifyList())
	else:	
		username = "None"
		id_utente = 0
		id_utente, username = utility.checkUser(bot, update, id_utente, username)
		if id_utente == 0:
			return
		utente = utility.getUtente(id_utente)
		username = utente.username
		if username != "None":
			username = "@" + username
		if utente.stato == "verificato":
			stato = "in attesa"
			tosendtext = "<b>" + utente.nickname + "</b> " + username + " rimosso dalla lista verificati!"
		else:
			stato = "verificato"
			tosendtext = "<b>" + utente.nickname + "</b> " + username + " verificato!"
			try:
				bot.sendMessage(chat_id = utente.id_utente, text = "I dati sono stati verificati, puoi usare il bot!", parse_mode = "HTML")
			except:
				bot.sendMessage(chat_id = 119444006, text = str(utente.id_utente) + " ha bloccato il bot")
		utility.setStato(id_utente, stato)
		bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext, parse_mode = "HTML")

def listaraid(bot, update):
	chat_id = update.message.chat_id
	if not authorized.admin(update.message.from_user.id):
		return
	command = update.message.text.split()
	if len(command) < 2:
		tosendtext = "Questa è la lista dei boss raid che conosco al momento:\n"
		cur.execute("select * from listaraid order by livello asc")
		found = cur.fetchall()
		for j in range(0, len(found)):
			tosendtext += "\nRaid di livello " + str(found[j][0]) + ":\n"
			for i in range(0, len(found[j][1])):	
				tosendtext += " " + found[j][1][i]
		bot.sendMessage(chat_id = chat_id, text = tosendtext)
		return
	if len(command) == 2:
		try:
			livello = int(command[1])
			if livello < 1 or livello > 5:
				return
			cur.execute("select * from listaraid where livello = (%(liv)s)", {'liv':livello})
			found = cur.fetchall()
			tosendtext = "Raid di livello " + str(livello) + ":\n"
			for i in range(0, len(found[0][1])):	
				tosendtext += "\n" + found[0][1][i]
			bot.sendMessage(chat_id = chat_id, text = tosendtext)
		except:
			return
	elif authorized.admin(update.message.from_user.id):
		try:
			livello = int(command[1])
			if livello < 1 or livello > 5:
				return
		except:
			return
		pokemon = []
		for i in range(2, len(command)):
			pokemon.append(command[i])
		cur.execute("update listaraid set pokemon =(%(pokemon)s) where livello = (%(livello)s)", {'pokemon':pokemon, 'livello':livello})
		conn.commit()
		bot.sendMessage(chat_id = chat_id, text = "Lista aggiornata!")

def mostraLista(bot, update, lista):
	chat_id = update.message.chat_id
	if len(lista) == 0:
		tosendtext = "Nessun utente registrato in questa lista."
	else:
		tosendtext = "Lista per <i>" + update.message.text.split()[0][1:] + "</i>"
		for i in range(0, len(lista)):
			tosendtext += "\n(L" + str(lista[i].livello) + ") "
			tosendtext += "<b>" + lista[i].nickname + "</b> "
			if chat_id > 0 and lista[i].username != "None":
				tosendtext += "@"
			if lista[i].username != "None":
				tosendtext += lista[i].username
			if lista[i].username == "None" or lista[i].username == "" or lista[i].nickname == "None":
				tosendtext += " (" + str(lista[i].id_utente) + ")"
	bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")

def palestra(bot, update):
	chat_id = update.message.chat_id
	if not authorized.admin(update.message.from_user.id):
		return
	command = update.message.text.split()
	reply = update.message.reply_to_message
	check = False
	try:
		posizione = reply.location
	except:
		return
	if str(posizione) == "None":
		testo = reply.text
		testo = testo.replace("<","")
		testo = testo.replace(">","")	
		testo = testo.replace(","," ")
		testo = testo.split()
		if len(testo) == 2:
			try:
				latit = float(testo[0])
				longit = float(testo[1])
				check = True
			except:
				tosendtext = "Nel testo inserisci le coordinate"
		else:
			tosendtext = "Rispondi ad un messaggio contenente una posizione"
	else:
		longit = posizione.longitude
		latit = posizione.latitude
		check = True
	if check:
		if len(command) < 2:
			tosendtext = "Scrivi anche il nome della palestra, per esempio:\n<i>/palestra The Kiss</i>"
		else:
			id_palestra = utility.newpalestraid()
			nome = ""
			for i in range(1, len(command)-1):
				nome += command[i] + " "
			nome += command[len(command)-1]	
			cur.execute("insert into palestre (id_palestra, nome, longitudine, latitudine) values ((%(id_palestra)s), (%(nome)s), (%(longit)s), (%(latit)s) )", {'id_palestra':id_palestra, 'nome':nome, 'longit':longit, 'latit':latit})
			conn.commit()
			tosendtext = "Palestra aggiunta correttamente!"
	bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")

def eliminapalestra(bot, update):
	if not utility.inputSanification(update.message.text):
		return
	if not authorized.admin(update.message.from_user.id):
		return
	command = update.message.text.split()
	chat_id = update.message.chat_id
	if len(command) > 1:
		id_palestra = int(command[1])
	else:
		id_palestre = 0
	if id_palestra != 0:
		palestra = utility.getpalestra(id_palestra)
		if id_palestra == -1:
			tosendtext = "Id non riconosciuto"
		else:
			tosendtext = "Palestra eliminata (#" + str(id_palestra) + "):\n" + palestra.nome
			tosendtext += "\n<code>" + str(palestra.latitudine) + ", " + str(palestra.longitudine) + "</code>"
			cur.execute("delete from palestre where id_palestra = (%(idp)s)", {'idp':palestra.id_palestra})
			conn.commit()
	else:
		tosendtext = "/eliminapalestra id"
	bot.sendMessage(chat_id = chat_id, text = tosendtext, parse_mode = "HTML")
