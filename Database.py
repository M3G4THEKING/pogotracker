from psycopg2 import connect
from .Constructors.User import User

conn = None

def createConnection(infos: str):
	global conn
	conn = connect(infos)

def getCursor():
	return conn.cursor()

def getConnection():
	return conn

def addUser(IDUtente: int, Username: str, Nome: str):
	cur = getCursor()
	cur.execute('INSERT INTO "utenti" (id_utente, username, nome) VALUES (%s, %s, %s)', (IDUtente, Username, Nome))
	conn.commit()

def getAuth(ID: int = None, Username: str = None):
	cur = getCursor()
	res = None
	if ID:
		cur.execute('SELECT "autorizzazione" FROM "utenti" WHERE "id_utente" = %s', (str(ID), ))
		res = cur.fetchone()
	if Username:
		cur.execute('SELECT "autorizzazione" FROM "utenti" WHERE "username" = %s or "nickname" = %s', (Username if Username[0] != "@" else Username[1:], ))
		res = cur.fetchone()
	return res[0] if res else 0

def getCodesList(team: str = None):
	cur = getCursor()
	if team:
		cur.execute('select "nome", "codice_amico", "nickname", "username" from "utenti" where "codice_amico" IS NOT NULL AND "team" = %s', (team, ))
	else:
		cur.execute('select "nome", "codice_amico", "nickname", "username" from "utenti" where "codice_amico" IS NOT NULL')
	return cur.fetchall()

def getUsersListByAuth(permLevel: int = 1):
	cur = getCursor()
	cur.execute('SELECT * FROM "utenti" WHERE "autorizzazione" = %s ORDER BY "nome"', (permLevel, ))
	return cur.fetchall()

def getUtente(ID: int = None, Username: str = None):
	cur = getCursor()
	res = None
	if ID:
		cur.execute('SELECT * FROM "utenti" WHERE "id_utente" = %s', (str(ID), ))
		res = cur.fetchone()
	if Username:
		cur.execute('SELECT * FROM "utenti" WHERE lower("username") = %s or lower("nickname") = %s', (Username.lower() if Username[0] != "@" else Username[1:].lower(), ))
		res = cur.fetchone()
	return User(res) if res else None