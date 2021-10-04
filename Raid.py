import Database
from json import dumps

class Raid:
	def __init__(self, data) -> None:
		self.IDRaid = data[0]
		self.IDCreatore = data[1]
		self.Partecipanti = data[2]
		self.PassEX = data[3]
		self.Stato = data[4]
		self.Livello = data[5]
		self.Pokemon = data[6]
		self.IDPalestra = data[7]
		self.OraInizio = data[8]
		self.OraFine = data[9]
		self.OraConfermata = data[10]

	def setLivello(self, Livello: bool):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "Livello" = %s WHERE "IDRaid" = %s', (Livello, self.IDRaid))
		Database.getConnection().commit()

	def setOraConfermata(self, OraConfermata: bool):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "OraConfermata" = %s WHERE "IDRaid" = %s', (OraConfermata, self.IDRaid))
		Database.getConnection().commit()

	def setPartecipanti(self, Partecipanti: dict):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "Partecipanti" = %s WHERE "IDRaid" = %s', (dumps(Partecipanti), self.IDRaid))
		Database.getConnection().commit()

	def setPassEX(self, PassEX: bool):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "PassEX" = %s WHERE "IDRaid" = %s', (PassEX, self.IDRaid))
		Database.getConnection().commit()

	def setPokemon(self, Pokemon: bool):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "Pokemon" = %s WHERE "IDRaid" = %s', (Pokemon, self.IDRaid))
		Database.getConnection().commit()

	def setStato(self, Stato: bool):
		cur = Database.getCursor()
		cur.execute('UPDATE "Raids" SET "Stato" = %s WHERE "IDRaid" = %s', (Stato, self.IDRaid))
		Database.getConnection().commit()