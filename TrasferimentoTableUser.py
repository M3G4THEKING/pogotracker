from Functions import sanification
from JSONParser import loadDatabaseConfig
from psycopg2 import connect

global conn
conn = connect(loadDatabaseConfig("Connect.json"))

cur = conn.cursor()
cur.execute("select * from utenti")
res = cur.fetchall()

for ute in res:
	nick = sanification(ute[2], True)[:16] if ute[2] != "None" else None
	liv = None if ute[3] == 1 else ute[3]
	team = None if ute[4] == "Nessuno" else ute[4]
	aut = -1 if ute[5] == "bannato" else (1 if ute[5] == "in attesa" else (2 if ute[5] == "verificato" else (3 if ute[0] != 119444006 else 4)))
	scre = None if ute[8] == "Nessuno" else ute[8]
	pos = None if int(ute[9][0]) == 0 and int(ute[9][1]) == 0 else ute[9]
	pos = None if ute[9][0] > 11.7321 and ute[9][0] < 11.7323 else pos
	codic = None if ute[10] == "None" else ute[10]
	nome = None if ute[11] == "Nessuno" else sanification(ute[11])[:64]
	cur.execute("insert into Users values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ute[0], ute[1], nick, liv, team, aut, scre, pos[0] if pos else None, pos[1] if pos else None, codic, nome))

conn.commit()