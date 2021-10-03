from Database import getUtente

def permLevel(IDUtente):
	utente = getUtente(IDUtente)
	return utente.PermLevel if utente else 0