import Database

class User:
	def __init__(self, data) -> None:
		self.IDUtente = data[0]
		self.Username = data[1]
		self.Nickname = data[2]
		self.Livello = int(data[3]) if data[3] else None
		self.Team = data[4]
		self.Autorizzazione = int(data[5])
		self.Screen = data[6]
		self.Posizione = [data[7], data[8]]
		self.CodiceAmico = data[9]
		self.Nome = data[10]

	def setAuthorization(self, Autorizzazione: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Autorizzazione" = %s WHERE "IDUtente" = %s', (Autorizzazione, self.IDUtente))
		Database.getConnection().commit()

	def setFriendCode(self, Codice: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "CodiceAmico" = %s WHERE "IDUtente" = %s', (Codice, self.IDUtente))
		Database.getConnection().commit()

	def setLevel(self, Livello: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Livello" = %s WHERE "IDUtente" = %s', (Livello, self.IDUtente))
		Database.getConnection().commit()

	def setLocation(self, Location):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Longitudine" = %s, "Latitudine" = %s WHERE "IDUtente" = %s', (Location.longitude, Location.latitude, self.IDUtente))
		Database.getConnection().commit()

	def setName(self, Name: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Nome" = %s WHERE "IDUtente" = %s', (Name, self.IDUtente))
		Database.getConnection().commit()

	def setNickname(self, Nickname: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Nickname" = %s WHERE "IDUtente" = %s', (Nickname, self.IDUtente))
		Database.getConnection().commit()

	def setScreen(self, Screen: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Screen" = %s WHERE "IDUtente" = %s', (str(Screen), self.IDUtente))
		Database.getConnection().commit()

	def setTeam(self, Team: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Team" = %s WHERE "IDUtente" = %s', (Team, self.IDUtente))
		Database.getConnection().commit()

	def setUsername(self, Username: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "Users" SET "Username" = %s WHERE "IDUtente" = %s', (Username, self.IDUtente))
		Database.getConnection().commit()