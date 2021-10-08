from json import dumps
from psycopg2 import connect
from Raid import Raid
from User import User

conn = None

def createConnection(infos: str):
	global conn
	conn = connect(infos)

def getCursor():
	return conn.cursor()

def getConnection():
	return conn

def addGym(Nome: str, Posizione: dict):
	cur = getCursor()
	cur.execute('INSERT INTO "Gyms" ("Nome", "Longitudine", "Latitudine") VALUES (%s, %s, %s) RETURNING "IDPalestra"', (Nome, Posizione[0], Posizione[1]))
	return cur.fetchone()[0]

def addRaid(IDCreatore: int, Partecipanti: dict, Pokemon: str, IDPalestra: int, OraInizio: dict, OraFine: dict):
	cur = getCursor()
	cur.execute('INSERT INTO "Raids" ("IDCreatore", "Partecipanti", "Pokemon", "IDPalestra", "OraInizio", "OraFine") VALUES (%s, %s, %s, %s, %s, %s) RETURNING "IDRaid"', (IDCreatore, dumps(Partecipanti), Pokemon, IDPalestra, OraInizio, OraFine))
	return cur.fetchone()[0]

def addUser(IDUtente: int, Username: str, Nome: str):
	cur = getCursor()
	cur.execute('INSERT INTO "Users" ("IDUtente", "Username", "Nome") VALUES (%s, %s, %s)', (IDUtente, Username, Nome))
	conn.commit()

def deleteGym(IDPalestra: int):
	cur = getCursor()
	cur.execute('DELETE FROM "Gyms" WHERE "IDPalestra" = %s', (IDPalestra, ))
	conn.commit()

def findGym(filters: dict = []):
	cur = getCursor()
	if len(filters) == 1 and filters[0].replace("%","").isdigit():
		cur.execute('SELECT * FROM "Gyms" WHERE "IDPalestra" = %s', (int(filters[0].replace("%","")), ))
	else:
		cur.execute('SELECT * FROM "Gyms" WHERE lower("Nome") LIKE ALL (%s)', (filters, ))
	return cur.fetchall()

def getAuth(ID: int = None, Username: str = None):
	cur = getCursor()
	res = None
	if ID:
		cur.execute('SELECT "Autorizzazione" FROM "Users" WHERE "IDUtente" = %s', (str(ID), ))
		res = cur.fetchone()
	if Username:
		cur.execute('SELECT "Autorizzazione" FROM "Users" WHERE lower("Username") = %s or lower("Nickname") = %s', (Username.lower() if Username[0] != "@" else Username[1:].lower(), ))
		res = cur.fetchone()
	return int(res[0]) if res else 0

def getCodesList(team: str = None):
	cur = getCursor()
	if team:
		cur.execute('SELECT "Nome", "CodiceAmico", "Nickname", "Username" from "Users" where "CodiceAmico" IS NOT NULL AND "Team" = %s', (team, ))
	else:
		cur.execute('SELECT "Nome", "CodiceAmico", "Nickname", "Username" from "Users" where "CodiceAmico" IS NOT NULL')
	return cur.fetchall()

def getGym(IDPalestra: int):
	cur = getCursor()
	cur.execute('SELECT * FROM "Gyms" WHERE "IDPalestra" = %s', (str(IDPalestra), ))
	return cur.fetchone()

def getRaid(ID: int = None):
	cur = getCursor()
	cur.execute('SELECT * FROM "Raids" WHERE "IDRaid" = %s', (ID, ))
	res = cur.fetchone()
	return Raid(res) if res else None

def getUsersListByAuth(permLevel: int = 1):
	cur = getCursor()
	cur.execute('SELECT * FROM "Users" WHERE "Autorizzazione" = %s ORDER BY "Nome"', (permLevel, ))
	return cur.fetchall()

def getUser(ID: int = None, Username: str = None):
	cur = getCursor()
	res = None
	if ID:
		cur.execute('SELECT * FROM "Users" WHERE "IDUtente" = %s', (str(ID), ))
		res = cur.fetchone()
	if Username:
		cur.execute('SELECT * FROM "Users" WHERE lower("Username") = %s or lower("Nickname") = %s', (Username.lower() if Username[0] != "@" else Username[1:].lower(), Username.lower() if Username[0] != "@" else Username[1:].lower()))
		res = cur.fetchone()
	return User(res) if res else None