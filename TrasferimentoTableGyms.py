from JSONParser import loadDatabaseConfig
from psycopg2 import connect

global conn
conn = connect(loadDatabaseConfig("Connect.json"))

cur = conn.cursor()
cur.execute("select * from palestre order by id_palestra asc")
res = cur.fetchall()

for pal in res:
	nome = pal[1][:50]
	cur.execute('insert into "Gyms" ("Nome", "Longitudine", "Latitudine") values (%s, %s, %s)', (nome, pal[2], pal[3]))

conn.commit()