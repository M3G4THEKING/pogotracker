#mcomm
#File per comandi più avanzati, per l'owner
import authorized, utility
from utility import cur,conn
import string

from telegram.ext import CommandHandler


def id(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	bot.sendMessage(chat_id = update.message.from_user.id, text = "ID chat: " + str(update.message.chat_id))
	if str(update.message.reply_to_message) != "None":
		bot.sendMessage(chat_id = 119444006, text = "Utente: " + update.message.reply_to_message.from_user.username + " (" + str(update.message.reply_to_message.from_user.id) + ")")

def comando(bot, update):
	if not authorized.admin(update.message.from_user.id):
		return
	reply = update.message.reply_to_message
	command = update.message.text.split()
	if len(command) == 1:
		tosendtext = "/comando nome"
	elif str(reply) == "None":
		tosendtext = "Quota un messaggio/immagine"
	else:
		nuovocomando = command[1].lower()
		cur.execute("select * from comandi where nome = (%(nome)s)", {'nome':nuovocomando})
		found = cur.fetchall()
		if len(found) == 1:
			nuovo = False
		else:
			nuovo = True
		try:
			screen = reply.photo[-1].file_id
			testo = screen 
			immagine = True
		except:
			testo = reply.text
			immagine = False
		if nuovo:
			cur.execute("insert into comandi values ( (%(nome)s), (%(testo)s), (%(immagine)s) )", {'nome':nuovocomando, 'testo':testo, 'immagine':immagine})
		else:
			cur.execute("update comandi set testo = (%(testo)s), immagine = (%(immagine)s)  where nome = (%(nome)s)", {'nome':nuovocomando, 'testo':testo, 'immagine':immagine})
		conn.commit()
		tosendtext = "Comando impostato con successo!"
	bot.sendMessage(chat_id = update.message.chat_id, text = tosendtext)
