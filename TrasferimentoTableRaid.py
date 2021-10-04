from json import dumps

from psycopg2 import connect
from JSONParser import loadDatabaseConfig

global conn
conn = connect(loadDatabaseConfig("Connect.json"))

cur = conn.cursor()
cur.execute("select * from raid order by id_raid desc")
res = cur.fetchall()

for raid in res:
	Part = {"presenti":{},"invitati":{},"fly":{},"rimossi":{}}
	for pers in raid[2]:
		Part["presenti"][str(pers)] = raid[13][len(Part["presenti"])]
	for pers in raid[3]:
		Part["invitati"][str(pers)] = raid[14][len(Part["invitati"])]
	for pers in raid[4]:
		Part["fly"][str(pers)] = raid[15][len(Part["fly"])]
	for pers in raid[17]:
		Part["rimossi"][str(pers)] = True
	liv = None if not raid[8] else raid[8]
	pok = None if raid[9] == "Nessuno" else raid[9][:64]
	idp = None if not raid[10] else raid[10]
	orai = [int(raid[11][0]), int(raid[16][1])]
	orat = [int(raid[11][0]), int(raid[11][1])]
	cur.execute("insert into Raids values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (raid[0], raid[1], dumps(Part), raid[5], raid[6], liv, pok, idp, orai, orat, raid[12]))

conn.commit()