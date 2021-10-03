from json import dumps
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

def getUtente(ID: int = None, Username: str = None):
	cur = getCursor()
	res = None
	if ID:
		cur.execute('SELECT * FROM "utenti" WHERE "id_utente" = %s', (str(ID), ))
		res = cur.fetchone()
	if Username:
		cur.execute('SELECT * FROM "utenti" WHERE "username" = %s or "nickname" = %s', (Username if Username[0] != "@" else Username[1:], ))
		res = cur.fetchone()
	return User(res) if res else None