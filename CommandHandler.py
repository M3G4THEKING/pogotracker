
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, Filters, InlineQueryHandler, MessageHandler

from Admin import admin, ban, eliminapalestra, listaraid, palestra, unban, verifica
from ButtonHandler import ButtonHandler
from Functions import codice_amico, gym, info, livello, nickname, raid, readChat, start, team
from InlineButton import InlineRaid

def loadCommands(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(CommandHandler("admin", admin))
	dispatcher.add_handler(CommandHandler("ban", ban))
	dispatcher.add_handler(CommandHandler("codice_amico", codice_amico))
	dispatcher.add_handler(CommandHandler("eliminapalestra", eliminapalestra))
	dispatcher.add_handler(CommandHandler("gym", gym))
	dispatcher.add_handler(CommandHandler("info", info))
	dispatcher.add_handler(CommandHandler("listaraid", listaraid))
	dispatcher.add_handler(CommandHandler("livello", livello))
	dispatcher.add_handler(CommandHandler("nickname", nickname))
	dispatcher.add_handler(CommandHandler("palestra", palestra))
	dispatcher.add_handler(CommandHandler("raid", raid))
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("team", team))
	dispatcher.add_handler(CommandHandler("unban", unban))
	dispatcher.add_handler(CommandHandler("verifica", verifica))

def loadCallbackQueries(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(CallbackQueryHandler(ButtonHandler))

def loadInlineQueries(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(InlineQueryHandler(InlineRaid))

def loadMessageHandler(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(MessageHandler(Filters.all, readChat))