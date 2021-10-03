from .. import Database
from ..JSONParser import getPermessi

class User:
	def __init__(self, data) -> None:
		self.IDUtente = data[0]
		self.Username = data[1]
		self.Nickname = data[2]
		self.Livello = data[3]
		self.Team = data[4]
		self.Autorizzazione = data[5]
		self.Legit = data[6]
		self.Multi = data[7]
		self.Screen = data[8]
		self.Posizione = data[9]
		self.CodiceAmico = data[10]
		self.Nome = data[11]

	def setLevel(self, Livello: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "livello" = %s WHERE "id_utente" = %s', (Livello, self.ID))
		Database.getConnection().commit()

	def setFriendCode(self, Codice: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "codice_amico" = %s WHERE "id_utente" = %s', (Codice, self.ID))
		Database.getConnection().commit()

	def setName(self, Name: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "nome" = %s WHERE "id_utente" = %s', (Name, self.ID))
		Database.getConnection().commit()

	def setNickname(self, Nickname: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "nickname" = %s WHERE "id_utente" = %s', (Nickname, self.ID))
		Database.getConnection().commit()

	def setScreen(self, Screen: int):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "screen" = %s WHERE "id_utente" = %s', (Screen, self.ID))
		Database.getConnection().commit()

	def setTeam(self, Team: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "team" = %s WHERE "id_utente" = %s', (Team, self.ID))
		Database.getConnection().commit()

	def setUsername(self, Username: str):
		cur = Database.getCursor()
		cur.execute('UPDATE "utenti" SET "username" = %s WHERE "id_utente" = %s', (Username, self.ID))
		Database.getConnection().commit()