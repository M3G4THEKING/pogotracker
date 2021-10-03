import telegram, string
import functions, authorized, mcomm, utility, admin, button

idb = open("botid.txt", "r")
api = idb.read().split()

bot = telegram.Bot(token=api[0])
print(bot.getMe())

from telegram.ext import CommandHandler, MessageHandler, InlineQueryHandler, ChosenInlineResultHandler, Filters
from telegram.ext import Updater
updater = Updater(token=api[0])
dispatcher = updater.dispatcher

from telegram.ext import CallbackQueryHandler
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) 

bot.sendMessage(chat_id = 119444006, text ="[N] Bot online!")

from functions import chat_dedicata

def start(bot, update):
	id_utente = update.message.from_user.id
	chat_id = update.message.chat_id
	command = update.message.text.split()
	print(command)
	if len(command) > 1:
		functions.addtoraid(bot, update)
		return
	if not authorized.banned(id_utente):
		tosendtext = ""
		if not utility.userPresence(id_utente):
			#try:
				#stato = bot.getChatMember(chat_id = int(chat_dedicata), user_id = id_utente).status
				#if stato != "left" and stato != "kicked":
			tosendtext = "Per iniziare, imposta in privato livello, nickname in gioco e squadra. Per sapere come funzionano i comandi, inviami !guida o /help\nSe hai dubbi chiedi agli admin del gruppo, dopo che avrai inviato tutto questo il tuo account verrà verificato e saremo pronti per iniziare!"
			username = str(update.message.from_user.username)
			if username == "None":
				username = "Nessuno"
			utility.addUser(id_utente, username, update.message.from_user.first_name)
				#else:
				#	tosendtext = "Entra nella chat LINK NON FORNITO, poi torna qui per potermi riavviare con /start\nDopo averlo fatto potrai procedere con la registrazione dell'account!"
			#except:
			#	tosendtext = "Entra nella chat LINK NON FORNITO, poi torna qui per potermi riavviare con /start\nDopo averlo fatto potrai procedere con la registrazione dell'account!"
		bot.sendMessage(chat_id=chat_id, text="Benvenuta/o " + update.message.from_user.first_name+"!\n"+tosendtext) 
	
#help
def Help(bot, update):
	help(bot, update)

def help(bot, update):
	chat_id = update.message.chat_id
	if chat_id < 0:
		return
	id_utente = update.message.from_user.id
	utente = utility.getUtente(id_utente)

	if not authorized.banned(id_utente):
		testo = "<b>Benvenuto nel bot per raid!</b>:\n\n/info : Visualizza il tuo profilo (o di altri se specifichi il nick)\n\n<b>Dati personali</b>\n/codice_amico CODICE : sarà visibile nelle tue informazioni\n/nickname TUONICK : scrivi il tuo nickname in gioco\n/livello TUOLIVELLO : scrivi il tuo livello giocatore\n/team BLU : può essere giallo, rosso o blu\n\n<b>RAID</b>\n/gym : così puoi vedere le palestre più vicine a te, se mi mandi una posizione userò quella come riferimento!\n/gym NOME PALESTRA : il bot ti invierà la posizione della palestra (funziona anche con /gym #Numero_palestra, il numero si vede nella lista delle palestre)"
		testo += "\n\n<b>Pulsanti raid</b>\n'Presente' ti iscrive al raid, se premuto più volte permette di segnare che hai altri account con te\n'Remoto' come per il precedente, ma ti segna sotto fly\n'Invitato' come i precedenti, segni che ci sei tramite invito\n'Toglimi' rimuove la tua presenza"
		#testo = "<b>Comandi disponibili</b>:\n/info : Visualizza il tuo profilo\n\nAttenzione, i seguenti comandi vanno mandati rispondendo ad un proprio messaggio precedentemente inviato con scritta solo l'informazione da inviare al bot (e SOLO nickname, livello e screen sono obbligatori):\n\n/nickname : scrivi il tuo nickname in gioco\n/livello: scrivi il tuo livello giocatore\n/team : può essere giallo, rosso o blu\n/multi : se hai altri account, scrivi la lista dei nickname in un messaggio\n/legit : cambia da legit a fly e viceversa\n/screen : manda una foto del tuo profilo, poi manda questo comando in risposta a quella foto. Questo dirà agli admin che hai completato l'inserimento delle informazioni e controlleranno il tuo profilo. Attenzione, dopo la verifica potrai cambiare solo il livello e lo screen, quindi non mettere informazioni errate."
	
		if authorized.admin(id_utente):
			testo += "\n\n<b>Comandi admin</b>:\n/info username/nickname : Visualizza il profilo di qualcuno e lo screen del profilo (se lo ha mandato)\n/verifica username/nickname : Confermi la veridicità dei dati forniti.\n/ban username/nickname : il giocatore viene segnato come non affidabile e sarà visibile dallo stato 'Bannato'\n/giallo, /rosso, /blu : manda una lista degli username di telegram e nickname in gioco delle relative squadre\n/listaraid Livello Pokemon1 Pokemon2 Pokemon3 ecc: quando cambiano i boss raid, potete usare questo comando per cambiarli. Es: /listaraid 4 Tyranitar Machamp\n/palestra : crea una nuova palestra, per farlo devi prima mandare le coordinate nel formato latitudine,longitudine, usando punti per i decimali, e poi quotando il messaggio con le coordinate e mandando /palestra Nome Esatto Palestra\n/comando nome : crei un nuovo comando, richiamabile con !nomecomando, che può essere un messaggio o un'immagine a cui rispondi; la lista è visibile con /comandi\n/eliminapalestra id : cancelli una palestra registrata\n\n<b>Creare un raid</b>\n/raid 'NOME PALESTRA'/#Numero_palestra:Pokemon:ora.minuti : apparirà la creazione del raid, coi pulsanti scegli il livello del raid e se confermarlo; il nome palestra (o numero per comodità) e il Pokemon sono opzionali\n<b>Inline</b>\nUsando il comando inline e scrivendo l'ID del raid, si potrà inoltrare il raid in altre chat"
			#testo += "\n\n<b>Comandi admin</b>:\n/info username/nickname : Visualizza il profilo di qualcuno e lo screen del profilo (se lo ha mandato)\n/verifica username/nickname : Confermi la veridicità dei dati forniti, il giocatore non potrà più cambiare da legit a fly e viceversa, il nickname ed il team.\n/ban username/nickname : il giocatore viene segnato come non affidabile e sarà visibile dallo stato 'Bannato'\n/giallo, /rosso, /blu : manda una lista degli username di telegram e nickname in gioco delle relative squadre\n/fly : come per il precedente comando\n/mancanti : manda la lista dei giocatori registrati ma con informazioni incomplete"
	
			if authorized.owner(id_utente):
				testo += "\n\n/id : manda l'id della chat"
			
		bot.sendMessage(chat_id=update.message.chat_id, text = testo, parse_mode = "HTML")

#HANDLER
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

#functions.py
nickname_handler = CommandHandler('nickname', functions.nickname)
dispatcher.add_handler(nickname_handler)
livello_handler = CommandHandler('livello', functions.livello)
dispatcher.add_handler(livello_handler)
codice_amico_handler = CommandHandler('codice_amico', functions.codice_amico)
dispatcher.add_handler(codice_amico_handler)
team_handler = CommandHandler('team', functions.team)
dispatcher.add_handler(team_handler)
#legit_handler = CommandHandler('legit', functions.legit)
#dispatcher.add_handler(legit_handler)
multi_handler = CommandHandler('multi', functions.multi)
dispatcher.add_handler(multi_handler)
screen_handler = CommandHandler('screen', functions.screen)
dispatcher.add_handler(screen_handler)
info_handler = CommandHandler('info', functions.info)
dispatcher.add_handler(info_handler)
raid_handler = CommandHandler('raid', functions.raid)
dispatcher.add_handler(raid_handler)
gym_handler = CommandHandler('gym', functions.gym)
dispatcher.add_handler(gym_handler)
comandi_handler = CommandHandler('comandi', functions.comandi)
dispatcher.add_handler(comandi_handler)
#user_handler = CommandHandler('user', functions.user)
#dispatcher.add_handler(user_handler)
#database_handler = CommandHandler('database', functions.database)
#dispatcher.add_handler(database_handler)

#mcomm.py
id_handler = CommandHandler('id', mcomm.id)
dispatcher.add_handler(id_handler)
comando_handler = CommandHandler('comando', mcomm.comando)
dispatcher.add_handler(comando_handler)

#admin.py
admin_handler = CommandHandler('admin', admin.admin)
dispatcher.add_handler(admin_handler)
giallo_handler = CommandHandler('giallo', admin.giallo)
dispatcher.add_handler(giallo_handler)
rosso_handler = CommandHandler('rosso', admin.rosso)
dispatcher.add_handler(rosso_handler)
blu_handler = CommandHandler('blu', admin.blu)
dispatcher.add_handler(blu_handler)
#Legit_handler = CommandHandler('Legit', admin.Legit)
#dispatcher.add_handler(Legit_handler)
#fly_handler = CommandHandler('fly', admin.fly)
#dispatcher.add_handler(fly_handler)
mancanti_handler = CommandHandler('mancanti', admin.mancanti)
dispatcher.add_handler(mancanti_handler)
verifica_handler = CommandHandler('verifica', admin.verifica)
dispatcher.add_handler(verifica_handler)
ban_handler = CommandHandler('ban', admin.ban)
dispatcher.add_handler(ban_handler)
palestra_handler = CommandHandler('palestra', admin.palestra)
dispatcher.add_handler(palestra_handler)
listaraid_handler = CommandHandler('listaraid', admin.listaraid)
dispatcher.add_handler(listaraid_handler)
eliminapalestra_handler = CommandHandler('eliminapalestra', admin.eliminapalestra)
dispatcher.add_handler(eliminapalestra_handler)

#button
dispatcher.add_handler(CallbackQueryHandler(button.button))

inlineraid_handler = InlineQueryHandler(functions.inlineraid)
dispatcher.add_handler(inlineraid_handler)

#Poiche' questo handler filtra tutto, deve essere l'ultimo o sorpassa gli altri handler
getuser_handler = MessageHandler(Filters.all, functions.getuser)
dispatcher.add_handler(getuser_handler)

updater.start_polling()
