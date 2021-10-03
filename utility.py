#utility
#Funzioni non richiamate da handler ma solo a supporto degli altri sorgenti, sarebbe meglio
#	non avessero interazione con l'utente tramite messaggi

import string, authorized, time

import psycopg2

logdati = open("connectPsycopg2.txt", "r")
login = logdati.read().split()

conn = psycopg2.connect(database = login[0], user = login[1], password = login[2], host = "127.0.0.1", port = "5432")
#conn = psycopg2.connect(database = "pokemon", user = "postgres", password = "MetalsLug5", host = "127.0.0.1", port = "5432")
#conn = psycopg2.connect(database = "db_adventure", user = "db_u_elah", password = "intendente5trapassavamo2affondate", host = "127.0.0.1", port = "5432")


print("Database opened from utility")

cur = conn.cursor()

parolebandite = ["drop", "update", "delete", "insert", "create", "alter"]

class Raid:
	pass

class Utente:
	id_utente = 0
	username = "None"
	nickname = "Nessuno"
	livello = 0
	team = "Nessuno" #Possibili 'giallo', 'blu', 'rosso'
	multi = "Nessuno"
	legit = False #Possibili True/False
	stato = 'bannato' #Possibili 'In attesa', 'Verificato', 'Bannato','Admin', 'Owner'
	screen = "Nessuno"
	emoji = ""
	pass

def adminList():
	cur.execute("select * from utenti where stato = 'admin'")
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found)):
		lista.append(getUserFromLine(found[i]))
	return lista

def arrayRaid(livello):
	cur.execute("select * from listaraid where livello = (%(livello)s)", {'livello':livello})
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found[0][1])):
		lista.append(found[0][1][i])
	return lista

def addUser(id_utente, username, nome):
	start_position = [11.732221,45.767466]
	cur.execute("insert into utenti (id_utente, username, nome, posizione) values ((%(id_utente)s), (%(username)s), (%(nome)s), (%(posizione)s))", {'id_utente':id_utente, 'username':username, 'nome':nome, 'posizione':start_position})
	conn.commit()

def changeUsername(id_utente, username):
	cur.execute("update utenti set username = (%(username)s) where id_utente = (%(id_utente)s)", {'username':username, 'id_utente':id_utente})
	conn.commit()

def changeName(id_utente, nome):
	cur.execute("update utenti set nome = (%(nome)s) where id_utente = (%(id_utente)s)", {'nome':nome, 'id_utente':id_utente})
	conn.commit()

def checkUser(bot, update, id_utente, username):
	command = update.message.text.split()
	chat_id = update.message.chat_id
	length = len(command)
	if length == 1:
		if str(update.message.reply_to_message) == "None":
			bot.sendMessage(chat_id = chat_id, text = "Aggiungi l'username o rispondi ad un messaggio")
			return 0, "None"
		else:
			id_utente = update.message.reply_to_message.from_user.id
			username = update.message.reply_to_message.from_user.username
			if not userPresence(id_utente, chat_id):
				bot.sendMessage(chat_id = chat_id, text = "Utente non presente nel database")
				return 0, "None"
	else:
		username = command[1]
		if username[0] == "@":
			username = username[1:]
		id_utente = findID(str(username))
		if id_utente == 0:
			try:	
				nickname = username
				id_utente = findIDfromNick(nickname)
				if id_utente == 0:
					id_utente = int(username)
					if idPresence(id_utente):
						return id_utente, "None"
					username = findUsername(id_utente)
					if username == "None":
						bot.sendMessage(chat_id = chat_id, text = "Username non riconosciuto")
						return 0, "None"
				#else:
				#	bot.sendMessage(chat_id = chat_id, text = "Riconosciuto tramite ID l'utente: @" + username)
			except:
				bot.sendMessage(chat_id = chat_id, text = "Username non riconosciuto")
				return 0, "None"
	return id_utente, username

def distanza(posizione, palestra):
	x = (posizione[0]-palestra.longitudine)*77.4
	y = (posizione[1]-palestra.latitudine)*111.3
	dist = x*x+y*y
	dist = pow(dist,0.5)
	return dist

def findID(username):
	cur.execute("select * from utenti where lower(username) = lower(%(username)s)", {'username':username})
	found = cur.fetchall()
	if len(found) == 1:
		return found[0][0]
	else:
		return 0

def findIDfromNick(nickname):
	cur.execute("select * from utenti where lower(nickname) = lower(%(nickname)s)", {'nickname':nickname})
	found = cur.fetchall()
	if len(found) == 1:
		return found[0][0]
	else:
		return 0

def findUsername(id_utente):
	utente = getUtente(id_utente)
	return utente.username

def getpalestra(id_palestra):
	cur.execute("select * from palestre where id_palestra = (%(id_palestra)s)", {'id_palestra':id_palestra})
	found = cur.fetchall()
	palestra = Raid()
	if len(found) == 0:
		palestra.id_palestra = -1
		return palestra
	palestra.id_palestra = found[0][0]
	palestra.nome = found[0][1]
	palestra.longitudine = found[0][2]
	palestra.latitudine = found[0][3]
	return palestra

def getraid(id_raid):
	cur.execute("select * from raid where id_raid = (%(id_raid)s)", {'id_raid':id_raid})
	found = cur.fetchall()
	raid = Raid()
	if len(found) == 0:
		raid.id_raid = -1
	raid.id_raid = found[0][0]
	raid.id_creatore = found[0][1]
	raid.presenti = found[0][2]
	raid.invitati = found[0][3]
	raid.fly = found[0][4]
	raid.passex = found[0][5]
	raid.stato = found[0][6]
	raid.informazioni = found[0][7]
	raid.livello = found[0][8]
	raid.pokemon = found[0][9]
	raid.id_palestra = found[0][10]
	raid.ora_termine = found[0][11]
	raid.ora_confermata = found[0][12]
	raid.numero_presenze = found[0][13]
	raid.numero_invitati = found[0][14]
	raid.numero_fly = found[0][15]
	raid.ora_inizio = found[0][16]
	raid.rimossi = found[0][17]
	return raid

def gettarget(target):
	try:
		id_utente = int(target)
		return id_utente
	except:
		target = str(target)
		if target[0] == "@":
			target = target[1:]
		id_utente = findID(target)
		if id_utente == 0:
			id_utente = findIDfromNick(target)
		return id_utente

def getUtente(target):
	utente = Utente()
	try:
		id_utente = int(target)
	except:
		id_utente = findID(str(target))
	cur.execute("select * from utenti where id_utente = (%(id_utente)s)", {'id_utente':id_utente})
	found = cur.fetchone()
	if str(found) != "None":
		utente = getUserFromLine(found)
	return utente

def getUserFromLine(linea):
	utente = Utente()
	utente.id_utente = int(linea[0])
	utente.username = linea[1]
	utente.nickname = linea[2]
	utente.livello = int(linea[3])
	utente.team = linea[4]
	utente.stato = linea[5]
	utente.legit = bool(linea[6])
	utente.multi = linea[7]
	utente.screen = linea[8]
	utente.posizione = linea[9]
	utente.codice_amico = linea[10]
	utente.nome = linea[11]
	if utente.team == "giallo":
		utente.emoji = " 🟡"
	elif utente.team == "rosso":
		utente.emoji = " 🔴"
	elif utente.team == "blu":
		utente.emoji = " 🔵"
	else:
		utente.emoji = " 🥐"
	return utente

def idPresence(id_utente):
	cur.execute("select * from utenti where id_utente = (%(id_utente)s)", {'id_utente':int(id_utente)})
	found = cur.fetchall()
	if len(found) == 1:
		return True
	return False

def inputSanification(text):
	secure = True
	for i in range(0, len(parolebandite)):
		if parolebandite[i] in str.lower(text):
			secure = False
	return secure

def legitList(legit):
	cur.execute("select * from utenti where legit = (%(legit)s)", {'legit':legit})
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found)):
		lista.append(getUserFromLine(found[i]))
	return lista

def listaPalestre(posizione = [0,0]):
	cur.execute("select * from palestre order by nome asc")
	found = cur.fetchall()
	palestre = []
	for i in range(0, len(found)):
		palestre.append(getpalestra(found[i][0]))
	if posizione == [0,0]:
		return palestre

def missingList():
	#cur.execute("select * from utenti where screen = 'Nessuno' and stato = 'in attesa'")
	cur.execute("select * from utenti where (nickname = 'None' or livello == 1) and stato != 'in attesa'")
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found)):
		lista.append(getUserFromLine(found[i]))
	return lista

def newpalestraid():
	cur.execute("select id_palestra from palestre order by id_palestra DESC limit 2")
	found = cur.fetchall()
	if len(found) == 0:
		return 0
	return (int(found[0][0])+1)

def newraidid():
	cur.execute("select id_raid from raid order by id_raid DESC limit 2")
	found = cur.fetchall()
	if len(found) == 0:
		return 0
	return (int(found[0][0])+1)

def notifyme(chat_id):
	cur.execute("select notifiche from gruppi where chat_id = (%(chat_id)s)", {'chat_id':str(chat_id)})
	found = cur.fetchone()
	return int(found[0])

def oraInizio(ora_termine):
	ora_inizio = [0,0]
	ora_inizio[0] = ora_termine[0]
	ora_inizio[1] = ora_termine[1]-45
	if ora_inizio[1] < 0:
		ora_inizio[1] += 60
		ora_inizio[0] -= 1
		if ora_inizio[0] < 0:
			ora_inizio[0] += 24
	return ora_inizio

def orario(data):
	text = ""
	if data[0] < 10:
		text += "0"
	text += str(data[0]) + ":" 
	if data[1] < 10:
		text += "0"
	text += str(data[1])
	return text

def oraTermine(ora_inizio):
	ora_termine = [0,0]
	ora_termine[0] = ora_inizio[0]
	ora_termine[1] = ora_inizio[1]+45
	if ora_termine[1] > 60:
		ora_termine[1] -= 60
		ora_termine[0] += 1
		if ora_termine[0] > 23:
			ora_termine[0] -= 24
	return ora_termine

def setBan(id_utente, chat_id, ban):
	setStato(id_utente, chat_id, "bannato")
	setWarn(id_utente, chat_id, 0)
	contaBan(id_utente, chat_id, ban)

def setStato(id_utente, stato):
	cur.execute("update utenti set stato = (%(stato)s) where id_utente = (%(id_utente)s)", {'stato':stato, 'id_utente':id_utente})
	conn.commit()

def setUnban(id_utente, chat_id):
	setStato(id_utente, chat_id, "presente")

def teamList(team):
	cur.execute("select * from utenti where team = (%(team)s) order by livello desc", {'team':team})
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found)):
		lista.append(getUserFromLine(found[i]))
	return lista

def updateLocation(id_utente, location):
	cur.execute("update utenti set posizione = (%(loc)s) where id_utente = (%(id_utente)s)", {'id_utente':id_utente, 'loc':[location.longitude, location.latitude]})
	conn.commit()

def userPresence(id_utente):
	cur.execute("select * from utenti where id_utente = (%(id_utente)s)", {'id_utente':id_utente})
	found = cur.fetchall()
	if len(found) >= 1:
		return True
	else:
		return False

def verifyList():
	cur.execute("select * from utenti where stato = 'in attesa'")
	#cur.execute("select * from utenti where (screen != 'Nessuno' or (nickname != 'None' and livello != 1)) and stato = 'in attesa'")
	found = cur.fetchall()
	lista = []
	for i in range(0, len(found)):
		lista.append(getUserFromLine(found[i]))
	return lista
